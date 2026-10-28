"""Recorridos de negocio con acciones explícitas y autorización por registro."""
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound

from accounts.models import Usuario
from animals.models import Mascota, CustodiaMascota, HistorialMedico
from core.models import EntidadVerificable, EntidadMiembro, ValorMaestro
from .autorizacion import usuario_activo, principal_de, puede, exigir
from .servicios import auditar, motivo_obligatorio
from .models import (AccesoExcepcional, DelegacionCuenta, PropuestaCuenta, DocumentoPrivado,
    EnmiendaClinica, RevisionSoporte, CorreccionReporte, PublicacionReporte,
    RespuestasAdopcion, Anuncio, VersionAnuncio, ReclamacionMascota)


def activo(actor):
    if not usuario_activo(actor):
        raise PermissionDenied("Cuenta inactiva")


def valor(tipo, nombre):
    return ValorMaestro.objects.get(tipo__nombre=tipo, nombre=nombre)


def obtener(modelo, pk, bloquear=False):
    qs = modelo.objects.select_for_update() if bloquear else modelo.objects
    obj = qs.filter(pk=pk).first()
    if obj is None:
        raise NotFound("Registro no disponible")
    return obj


def solo_campos(datos, permitidos, requeridos=()):
    if not isinstance(datos, dict) or set(datos) - set(permitidos) or set(requeridos) - set(datos):
        raise ValidationError("Campos no permitidos o incompletos")
    return datos


def entidad_verificada(pk):
    if not EntidadVerificable.objects.filter(pk=pk, estado_verificacion__tipo__nombre="estado_verificacion",
                                           estado_verificacion__nombre="Verificada").exists():
        raise ValidationError("La entidad no está verificada")


def principal(actor, entidad_id):
    activo(actor)
    if not principal_de(actor, entidad_id):
        raise PermissionDenied("Solo el responsable principal vigente")


def custodio(mascota):
    ids = list(CustodiaMascota.objects.filter(mascota=mascota, fecha_fin__isnull=True)
               .values_list("fundacion_id", flat=True)[:2])
    if len(ids) > 1 or (ids and mascota.dueno_id):
        raise ValidationError("La ficha presenta un conflicto de custodia")
    return ids[0] if ids else None


def dueno(actor, mascota):
    activo(actor)
    return mascota.dueno_id == actor.pk and custodio(mascota) is None


def objeto_privado(recurso, pk):
    from adoption.models import SolicitudAdopcion
    from commerce.models import PedidoIniciado
    from rescue.models import Apadrinamiento
    from core.models import SolicitudValidacion
    modelos = {"historial": HistorialMedico, "soporte": DocumentoPrivado,
        "adopcion": SolicitudAdopcion, "aporte": Apadrinamiento,
        "pedido": PedidoIniciado, "verificacion": SolicitudValidacion,
        "expediente": Mascota, "reclamacion": ReclamacionMascota}
    if recurso not in modelos:
        raise ValidationError("Recurso privado no admitido")
    return obtener(modelos[recurso], pk)


def autoridad(actor, recurso, pk):
    """Autoridad sobre el dato; administración técnica no es suficiente."""
    if not usuario_activo(actor):
        return False
    obj = objeto_privado(recurso, pk)
    if recurso == "soporte":
        return autoridad(actor, obj.recurso, obj.objeto_id)
    if recurso == "historial":
        return autoridad(actor, "expediente", obj.mascota_id)
    if recurso == "expediente":
        entidad_id = custodio(obj)
        return principal_de(actor, entidad_id) if entidad_id else obj.dueno_id == actor.pk
    if recurso in ("verificacion", "reclamacion"):
        return (obj.usuario_solicitante_id if recurso == "verificacion" else obj.reclamante_id) == actor.pk
    from .objetos import contexto
    ctx = contexto(recurso, pk)
    return ctx.propietario_id == actor.pk or (ctx.entidad_id and principal_de(actor, ctx.entidad_id))


def excepcion(actor, recurso, pk):
    ahora = timezone.now()
    for permiso in AccesoExcepcional.objects.filter(solicitante_id=actor.pk, recurso=recurso, objeto_id=pk,
            estado="APROBADA", revocada__isnull=True, expira__gt=ahora).select_related("aprobador"):
        if permiso.aprobador_id != actor.pk and autoridad(permiso.aprobador, recurso, pk):
            return True
    return False


def leer(actor, recurso, pk, *, excepcional=True):
    activo(actor)
    obj = objeto_privado(recurso, pk)
    permitido = False
    if recurso == "expediente":
        permitido = dueno(actor, obj) or puede(actor, "expediente.escribir", objeto_id=pk)
    elif recurso == "historial":
        permitido = leer(actor, "expediente", obj.mascota_id, excepcional=False)
    elif recurso == "soporte":
        permitido = leer(actor, obj.recurso, obj.objeto_id, excepcional=False)
    elif recurso == "reclamacion":
        permitido = obj.reclamante_id == actor.pk or puede(actor, "reclamacion.resolver", objeto_id=pk)
    else:
        campo = {"adopcion": "usuario_adoptante_id", "aporte": "usuario_padrino_id",
                 "pedido": "usuario_cliente_id", "verificacion": "usuario_solicitante_id"}[recurso]
        permitido = getattr(obj, campo) == actor.pk or puede(actor, f"{recurso}.ver", objeto_id=pk)
    return bool(permitido or (excepcional and recurso != "expediente" and excepcion(actor, recurso, pk)))


def exigir_lectura(actor, recurso, pk):
    if not leer(actor, recurso, pk):
        raise PermissionDenied("No tienes acceso a este registro")


@transaction.atomic
def delegar_cuenta(actor, entidad_id, miembro_id, revocar=False):
    obtener(EntidadVerificable, entidad_id, True)
    principal(actor, entidad_id)
    exigir(actor, "cuenta.delegar", entidad_id=entidad_id)
    m = obtener(EntidadMiembro, miembro_id, True)
    if m.entidad_id != entidad_id or m.fecha_salida or not usuario_activo(m.usuario_id):
        raise ValidationError("Miembro no vigente en esta entidad")
    if not revocar and principal_de(m.usuario_id, entidad_id):
        raise ValidationError("La preparación y aprobación requieren personas diferentes")
    obj, _ = DelegacionCuenta.objects.update_or_create(miembro=m, defaults={"entidad_id": entidad_id,
        "otorgante": actor, "revocada": timezone.now() if revocar else None})
    auditar(actor, "cuenta.delegacion", "entidades", entidad_id, entidad_id, revocada=revocar, miembro_id=m.pk)
    return obj


def delegado(actor, entidad_id):
    return puede(actor, "cuenta.preparar", entidad_id=entidad_id)


@transaction.atomic
def proponer_cuenta(actor, entidad_id, datos):
    from core.crypto import cifrar
    from rescue.models import CuentaFundacion
    obtener(EntidadVerificable, entidad_id, True)
    from core.models import Fundacion
    obtener(Fundacion, entidad_id)
    entidad_verificada(entidad_id)
    if not delegado(actor, entidad_id) or principal_de(actor, entidad_id):
        raise PermissionDenied("Solo una persona delegada distinta del principal prepara cambios")
    solo_campos(datos, ("numero", "banco", "tipo", "titular"), ("numero", "banco", "tipo", "titular"))
    limites = {"numero": 40, "banco": 120, "tipo": 60, "titular": 150}
    if any(not isinstance(datos[c], str) or not datos[c].strip() or len(datos[c]) > n for c, n in limites.items()):
        raise ValidationError("Datos de cuenta inválidos")
    if len(datos["numero"]) < 4 or not datos["numero"].isascii() or not datos["numero"].isdigit():
        raise ValidationError("Número de cuenta inválido")
    base = CuentaFundacion.objects.filter(fundacion_id=entidad_id, activa=True).order_by("-pk").first()
    p = PropuestaCuenta.objects.create(entidad_id=entidad_id, preparador=actor,
        numero_cifrado=cifrar(datos["numero"]), ultimos4=datos["numero"][-4:], banco=datos["banco"],
        tipo=datos["tipo"], titular=datos["titular"], cuenta_base_id=base.pk if base else None)
    auditar(actor, "cuenta.proponer", "cuentas", p.pk, entidad_id)
    return p


@transaction.atomic
def resolver_cuenta(actor, pk, aprobar, motivo):
    from rescue.models import CuentaFundacion
    entidad_id = obtener(PropuestaCuenta, pk).entidad_id
    obtener(EntidadVerificable, entidad_id, True)
    p = obtener(PropuestaCuenta, pk, True)
    principal(actor, entidad_id)
    exigir(actor, "cuenta.aprobar", entidad_id=entidad_id)
    motivo = motivo_obligatorio(motivo)
    if p.estado != "PENDIENTE" or p.preparador_id == actor.pk:
        raise ValidationError("Propuesta resuelta o autoaprobación no permitida")
    if aprobar:
        entidad_verificada(entidad_id)
        if not delegado(p.preparador, entidad_id):
            raise ValidationError("La delegación del preparador ya no está vigente")
        vigente = CuentaFundacion.objects.filter(fundacion_id=entidad_id, activa=True).order_by("-pk").first()
        if (vigente.pk if vigente else None) != p.cuenta_base_id:
            raise ValidationError("La cuenta cambió; prepara una propuesta actualizada")
        CuentaFundacion.objects.filter(fundacion_id=entidad_id, activa=True).update(activa=False)
        p.cuenta_publicada = CuentaFundacion.objects.create(fundacion_id=entidad_id,
            numero_cuenta_cifrado=p.numero_cifrado, numero_cuenta_ultimos4=p.ultimos4,
            banco=p.banco, tipo_cuenta=p.tipo, titular=p.titular)
    p.estado = "APROBADA" if aprobar else "RECHAZADA"
    p.save(update_fields=["estado", "cuenta_publicada"])
    auditar(actor, "cuenta.resolver", "cuentas", p.pk, entidad_id, motivo, estado=p.estado)
    return p


@transaction.atomic
def solicitar_excepcion(actor, recurso, pk, motivo):
    activo(actor)
    # Seleccionar un registro concreto, nunca un expediente completo o un filtro.
    if recurso not in ("historial", "soporte", "adopcion", "aporte", "pedido", "verificacion"):
        raise ValidationError("Selecciona un registro privado concreto")
    objeto_privado(recurso, pk)
    obj = AccesoExcepcional.objects.create(solicitante=actor, recurso=recurso, objeto_id=pk,
        motivo=motivo_obligatorio(motivo))
    auditar(actor, "excepcion.solicitar", recurso, pk)
    return obj


@transaction.atomic
def resolver_excepcion(actor, pk, aprobar, horas, motivo):
    obj = obtener(AccesoExcepcional, pk, True)
    activo(actor)
    if obj.solicitante_id == actor.pk or not autoridad(actor, obj.recurso, obj.objeto_id):
        raise PermissionDenied("Se requiere otra persona con autoridad sobre el dato")
    if obj.estado != "PENDIENTE" or not 1 <= horas <= 24:
        raise ValidationError("Solicitud resuelta o duración fuera de 1 a 24 horas")
    obj.estado = "APROBADA" if aprobar else "RECHAZADA"
    obj.aprobador = actor
    obj.aprobada = timezone.now()
    obj.expira = obj.aprobada + timedelta(hours=horas) if aprobar else None
    obj.save()
    auditar(actor, "excepcion.resolver", obj.recurso, obj.objeto_id, motivo=motivo_obligatorio(motivo),
            estado=obj.estado, horas=horas)
    return obj


@transaction.atomic
def revocar_excepcion(actor, pk, motivo):
    obj = obtener(AccesoExcepcional, pk, True)
    activo(actor)
    if actor.pk != obj.solicitante_id and not autoridad(actor, obj.recurso, obj.objeto_id):
        raise PermissionDenied("No tienes autoridad para revocar este acceso")
    obj.revocada = timezone.now()
    obj.save(update_fields=["revocada"])
    auditar(actor, "excepcion.revocar", obj.recurso, obj.objeto_id, motivo=motivo_obligatorio(motivo))
    return obj


@transaction.atomic
def enmendar(actor, pk, detalle, motivo):
    mascota_id = obtener(HistorialMedico, pk).mascota_id
    obtener(Mascota, mascota_id, True)
    original = obtener(HistorialMedico, pk, True)
    exigir(actor, "expediente.escribir", objeto_id=original.mascota_id)
    if original.usuario_registrador_id != actor.pk or original.veterinario_id is None:
        raise PermissionDenied("Solo el profesional autor puede enmendar su anotación")
    obj = EnmiendaClinica.objects.create(original=original, autor=actor, detalle=detalle,
        motivo=motivo_obligatorio(motivo))
    auditar(actor, "expediente.enmienda", "historial", pk, enmienda_id=obj.pk)
    return obj


@transaction.atomic
def revisar_soporte(actor, pk, resultado, observacion):
    previo = obtener(DocumentoPrivado, pk)
    if previo.recurso != "expediente":
        raise ValidationError("Este documento no es un soporte del dueño")
    obtener(Mascota, previo.objeto_id, True)
    doc = obtener(DocumentoPrivado, pk, True)
    if doc.recurso != "expediente" or resultado not in ("VALIDADO", "ACLARACIONES"):
        raise ValidationError("Soporte o resultado no admitido")
    exigir(actor, "expediente.escribir", objeto_id=doc.objeto_id)
    obj = RevisionSoporte.objects.create(documento=doc, profesional=actor, resultado=resultado,
        observacion=motivo_obligatorio(observacion))
    auditar(actor, "soporte.revisar", "soporte", pk, resultado=resultado)
    return obj


@transaction.atomic
def cambiar_adopcion(actor, pk, retirar=False, respuestas=None):
    from adoption.models import SolicitudAdopcion, HistorialEstadoAdopcion
    solicitud = obtener(SolicitudAdopcion, pk)
    obtener(Mascota, solicitud.mascota_id, True)
    solicitud = obtener(SolicitudAdopcion, pk, True)
    activo(actor)
    if solicitud.usuario_adoptante_id != actor.pk:
        raise PermissionDenied("Solo la persona solicitante")
    if solicitud.estado_adopcion.nombre != "Pendiente":
        raise ValidationError("La solicitud ya no está pendiente")
    if retirar:
        anterior = solicitud.estado_adopcion
        solicitud.estado_adopcion = valor("estado_adopcion", "Retirada")
        solicitud.fecha_resolucion = timezone.now()
        solicitud.save(update_fields=["estado_adopcion", "fecha_resolucion"])
        HistorialEstadoAdopcion.objects.create(solicitud=solicitud, estado_anterior=anterior,
            estado_nuevo=solicitud.estado_adopcion, usuario_actor=actor, observacion="Retirada por el solicitante")
        from .models import AsignacionRecurso
        AsignacionRecurso.objects.filter(recurso__codigo="adopcion", objeto_id=pk,
            fecha_revocacion__isnull=True).update(fecha_revocacion=timezone.now())
    else:
        if not isinstance(respuestas, dict) or len(str(respuestas)) > 12000 or any(
                not isinstance(k, str) or not isinstance(v, str) or len(k) > 100 or len(v) > 2000
                for k, v in respuestas.items()):
            raise ValidationError("Respuestas inválidas; no se aceptan campos internos")
        fila, _ = RespuestasAdopcion.objects.get_or_create(solicitud=solicitud)
        # Los valores clínicos/contactos no se copian a la auditoría administrativa.
        from .models import VersionRespuestas
        VersionRespuestas.objects.create(solicitud=solicitud, autor=actor,
            anteriores=fila.respuestas, nuevas=respuestas)
        fila.respuestas = respuestas
        fila.save(update_fields=["respuestas"])
    auditar(actor, "adopcion.retirar" if retirar else "adopcion.respuestas", "adopcion", pk)
    return solicitud


@transaction.atomic
def proponer_correccion(actor, pk, propuesta, motivo):
    from rescue.models import Reporte, CasoRescate
    r = obtener(Reporte, pk, True)
    activo(actor)
    if r.usuario_reportante_id != actor.pk:
        raise PermissionDenied("Solo el reportante registrado")
    if not CasoRescate.objects.filter(reporte=r).exists():
        raise ValidationError("Este recorrido corresponde a reportes aceptados")
    solo_campos(propuesta, ("descripcion", "contacto_reportante"))
    if not propuesta or any(not isinstance(v, str) or len(v) > (5000 if k == "descripcion" else 150)
                           for k, v in propuesta.items()):
        raise ValidationError("Corrección inválida")
    obj = CorreccionReporte.objects.create(reporte=r, solicitante=actor, propuesta=propuesta,
        base={k: getattr(r, k) for k in propuesta}, motivo=motivo_obligatorio(motivo))
    auditar(actor, "reporte.correccion_solicitar", "reporte", pk)
    return obj


@transaction.atomic
def resolver_correccion(actor, pk, aprobar, motivo):
    from rescue.models import Reporte, CasoRescate
    c = obtener(CorreccionReporte, pk)
    r = obtener(Reporte, c.reporte_id, True)
    c = obtener(CorreccionReporte, pk, True)
    caso = CasoRescate.objects.get(reporte=r)
    exigir(actor, "caso.cambiar_estado", entidad_id=caso.fundacion_id)
    if c.estado != "PENDIENTE":
        raise ValidationError("La corrección ya fue resuelta")
    if aprobar:
        if any(getattr(r, k) != v for k, v in c.base.items()):
            raise ValidationError("El reporte cambió; prepara una nueva corrección")
        for k, v in c.propuesta.items():
            setattr(r, k, v)
        r.save(update_fields=[*c.propuesta, "fecha_actualizacion"])
    c.estado = "APROBADA" if aprobar else "RECHAZADA"
    c.save(update_fields=["estado"])
    auditar(actor, "reporte.correccion_resolver", "reporte", r.pk, caso.fundacion_id,
            motivo_obligatorio(motivo), correccion_id=c.pk, estado=c.estado)
    return c


@transaction.atomic
def moderar_reporte(actor, pk, accion, motivo):
    from rescue.models import Reporte
    r = obtener(Reporte, pk, True)
    obj, _ = PublicacionReporte.objects.get_or_create(reporte=r)
    if accion == "solicitar_revision":
        activo(actor)
        if r.usuario_reportante_id != actor.pk or not obj.oculta:
            raise PermissionDenied("Solo el autor de un reporte oculto")
        obj.revision_pendiente = True
    else:
        exigir(actor, "reporte.moderar")
        if accion == "republicar":
            if not obj.revision_pendiente:
                raise ValidationError("El autor debe solicitar revisión")
            obj.oculta = False
        elif accion == "ocultar":
            obj.oculta = True
        else:
            raise ValidationError("Acción inválida")
        obj.revision_pendiente = False
    obj.save()
    auditar(actor, f"reporte.{accion}", "reporte", pk, motivo=motivo_obligatorio(motivo))
    return obj


@transaction.atomic
def resolver_verificacion(actor, pk, accion, motivo):
    from core.models import SolicitudValidacion
    solicitud = obtener(SolicitudValidacion, pk, True)
    motivo = motivo_obligatorio(motivo)
    if accion == "reenviar":
        activo(actor)
        if solicitud.usuario_solicitante_id != actor.pk or solicitud.estado_solicitud.nombre != "Correcciones":
            raise PermissionDenied("Solo el solicitante puede reenviar una solicitud en corrección")
        solicitud.estado_solicitud = valor("estado_solicitud_validacion", "Pendiente")
    else:
        exigir(actor, "entidad.validar", objeto_id=pk)
        if solicitud.usuario_solicitante_id == actor.pk or solicitud.estado_solicitud.nombre != "Pendiente":
            raise ValidationError("Estado o revisor no permitido")
        estados = {"aprobar": "Aprobada", "rechazar": "Rechazada", "correcciones": "Correcciones"}
        if accion not in estados:
            raise ValidationError("Acción inválida")
        if accion == "aprobar" and not DocumentoPrivado.objects.filter(recurso="verificacion", objeto_id=pk).exists():
            raise ValidationError("Se requieren documentos privados de verificación")
        solicitud.estado_solicitud = valor("estado_solicitud_validacion", estados[accion])
        solicitud.usuario_validador = actor
        solicitud.observacion = motivo
        if accion in ("aprobar", "rechazar"):
            solicitud.fecha_resolucion = timezone.now()
            entidad = obtener(EntidadVerificable, solicitud.entidad_id, True)
            entidad.estado_verificacion = valor("estado_verificacion", "Verificada" if accion == "aprobar" else "Rechazada")
            entidad.save(update_fields=["estado_verificacion"])
    solicitud.save()
    auditar(actor, f"verificacion.{accion}", "verificacion", pk, solicitud.entidad_id, motivo)
    return solicitud


@transaction.atomic
def nueva_version_anuncio(actor, entidad_id, datos, anuncio_id=None):
    exigir(actor, "publicidad.gestionar", entidad_id=entidad_id)
    entidad_verificada(entidad_id)
    if anuncio_id is None:
        anuncio = Anuncio.objects.create(entidad_id=entidad_id)
    else:
        anuncio = obtener(Anuncio, anuncio_id, True)
        if anuncio.entidad_id != entidad_id:
            raise PermissionDenied("Anuncio de otra entidad")
    obj = VersionAnuncio.objects.create(anuncio=anuncio, autor=actor, **datos)
    auditar(actor, "publicidad.enviar_revision", "publicidad", anuncio.pk, entidad_id, version_id=obj.pk)
    return obj


@transaction.atomic
def revisar_anuncio(actor, pk, accion, motivo):
    version = obtener(VersionAnuncio, pk)
    anuncio = obtener(Anuncio, version.anuncio_id, True)
    version = obtener(VersionAnuncio, pk, True)
    exigir(actor, "publicidad.revisar")
    if version.autor_id == actor.pk:
        raise PermissionDenied("No puedes revisar tu propia versión")
    if accion == "ocultar":
        anuncio.oculto = True
    elif accion in ("aprobar", "rechazar"):
        if version.estado != "PENDIENTE":
            raise ValidationError("La versión ya fue revisada")
        if VersionAnuncio.objects.filter(anuncio=anuncio, pk__gt=pk, estado="APROBADA").exists():
            raise ValidationError("Ya fue aprobada una versión posterior")
        version.estado = "APROBADA" if accion == "aprobar" else "RECHAZADA"
        version.save(update_fields=["estado"])
        if accion == "aprobar":
            anuncio.oculto = False
    else:
        raise ValidationError("Acción inválida")
    anuncio.save(update_fields=["oculto"])
    auditar(actor, f"publicidad.{accion}", "publicidad", anuncio.pk, anuncio.entidad_id,
            motivo_obligatorio(motivo), version_id=version.pk)
    return version


@transaction.atomic
def tomar_reclamacion(actor, pk):
    exigir(actor, "reclamacion.tomar")
    obj = obtener(ReclamacionMascota, pk, True)
    if obj.reclamante_id == actor.pk or obj.mascota.dueno_id == actor.pk:
        raise PermissionDenied("Se requiere un revisor sin conflicto de titularidad")
    if obj.revisor_id or obj.estado != "PENDIENTE":
        raise ValidationError("La reclamación ya está asignada o resuelta")
    obj.revisor = actor
    obj.save(update_fields=["revisor"])
    auditar(actor, "reclamacion.tomar", "reclamacion", pk)
    return obj


@transaction.atomic
def resolver_reclamacion(actor, pk, aprobar, motivo):
    obj = obtener(ReclamacionMascota, pk, True)
    exigir(actor, "reclamacion.resolver", objeto_id=pk)
    if obj.revisor_id != actor.pk or obj.estado != "PENDIENTE":
        raise PermissionDenied("Solo el revisor asignado de una reclamación pendiente")
    if not DocumentoPrivado.objects.filter(recurso="reclamacion", objeto_id=pk).exists():
        raise ValidationError("Se requieren soportes de la reclamación")
    obj.estado = "FAVORABLE" if aprobar else "RECHAZADA"
    obj.dueno_revisado_id = obj.mascota.dueno_id
    obj.save(update_fields=["estado", "dueno_revisado_id"])
    auditar(actor, "reclamacion.resolver", "reclamacion", pk, motivo=motivo_obligatorio(motivo), estado=obj.estado)
    # La decisión no modifica dueño, autorizaciones clínicas ni códigos QR.
    return obj


@transaction.atomic
def ejecutar_titularidad(actor, pk, dueno_actual_id, nuevo_dueno_id, motivo):
    from animals.models import AutorizacionExpediente, CodigoQRExpediente
    from .models import HistorialTitularidad
    previo = obtener(ReclamacionMascota, pk)
    mascota = obtener(Mascota, previo.mascota_id, True)
    obj = obtener(ReclamacionMascota, pk, True)
    exigir(actor, "reclamacion.ejecutar", objeto_id=pk)
    if obj.revisor_id != actor.pk or obj.estado != "FAVORABLE":
        raise PermissionDenied("Se requiere decisión favorable del revisor asignado")
    if actor.pk in (obj.reclamante_id, mascota.dueno_id):
        raise PermissionDenied("El revisor no puede ser parte del conflicto")
    if custodio(mascota):
        raise ValidationError("La custodia de una fundación requiere su procedimiento de adopción o entrega")
    if mascota.dueno_id != dueno_actual_id or obj.dueno_revisado_id != dueno_actual_id:
        raise ValidationError("La titularidad cambió desde la revisión; requiere revisar de nuevo")
    if nuevo_dueno_id != obj.reclamante_id or nuevo_dueno_id == mascota.dueno_id:
        raise ValidationError("El destinatario debe coincidir con el reclamante revisado")
    if not usuario_activo(nuevo_dueno_id):
        raise ValidationError("La cuenta destinataria está inactiva")
    historia = HistorialTitularidad.objects.create(reclamacion=obj, anterior_id=mascota.dueno_id,
        nuevo_id=nuevo_dueno_id, actor=actor, motivo=motivo_obligatorio(motivo))
    mascota.dueno_id = nuevo_dueno_id
    mascota.save(update_fields=["dueno"])
    ahora = timezone.now()
    AutorizacionExpediente.objects.filter(mascota=mascota, fecha_revocacion__isnull=True).update(fecha_revocacion=ahora)
    CodigoQRExpediente.objects.filter(mascota=mascota, fecha_revocacion__isnull=True).update(fecha_revocacion=ahora)
    obj.estado = "EJECUTADA"
    obj.save(update_fields=["estado"])
    auditar(actor, "reclamacion.titularidad_ejecutar", "reclamacion", pk,
        anterior_id=historia.anterior_id, nuevo_id=nuevo_dueno_id)
    from core.models import Notificacion
    tipo, _ = ValorMaestro.objects.get_or_create(tipo=valor("tipo_notificacion", "Resultado de adopción").tipo,
                                                nombre="Cambio de titularidad")
    for destinatario in {historia.anterior_id, nuevo_dueno_id} - {None}:
        Notificacion.objects.create(usuario_id=destinatario, tipo_notificacion=tipo,
            contenido=f"Se registró el cambio de titularidad de la ficha {mascota.pk}, reclamación {pk}.")
    return historia


@transaction.atomic
def actualizar_pedido(actor, pk, estado, motivo):
    from commerce.models import PedidoIniciado
    obj = obtener(PedidoIniciado, pk, True)
    exigir(actor, "pedido.gestionar", objeto_id=pk)
    transiciones = {"Iniciado": {"Contactado", "Cancelado"}, "Contactado": {"Cancelado"}}
    if estado not in transiciones.get(obj.estado_pedido.nombre, set()):
        raise ValidationError("Transición de pedido no permitida")
    anterior = obj.estado_pedido.nombre
    obj.estado_pedido = valor("estado_pedido", estado)
    obj.save(update_fields=["estado_pedido"])
    auditar(actor, "pedido.estado", "pedido", pk, obj.tienda_id,
        motivo_obligatorio(motivo), anterior=anterior, nuevo=estado)
    return obj


@transaction.atomic
def actualizar_caso(actor, pk, estado, motivo):
    from rescue.models import CasoRescate, HistorialEstadoCaso
    obj = obtener(CasoRescate, pk, True)
    exigir(actor, "caso.cambiar_estado", entidad_id=obj.fundacion_id)
    if obj.estado_caso.nombre != "En atención" or estado not in ("Cerrado", "Cancelado"):
        raise ValidationError("Solo un caso en atención admite cierre o cancelación")
    anterior = obj.estado_caso
    obj.estado_caso = valor("estado_caso", estado)
    obj.fecha_cierre = timezone.now()
    obj.usuario_ultimo_cambio = actor
    obj.save(update_fields=["estado_caso", "fecha_cierre", "usuario_ultimo_cambio"])
    HistorialEstadoCaso.objects.create(caso=obj, estado_anterior=anterior, estado_nuevo=obj.estado_caso,
        usuario_actor=actor, observacion=motivo_obligatorio(motivo))
    auditar(actor, "caso.estado", "caso", pk, obj.fundacion_id, motivo=motivo)
    return obj


@transaction.atomic
def editar_reporte_pendiente(actor, pk, cambios, cerrar=False):
    from rescue.models import Reporte, HistorialEstadoReporte
    obj = obtener(Reporte, pk, True)
    activo(actor)
    if obj.usuario_reportante_id != actor.pk:
        raise PermissionDenied("Solo el reportante registrado")
    if obj.estado_reporte.nombre != "Pendiente":
        raise ValidationError("Un reporte aceptado requiere una solicitud de corrección")
    solo_campos(cambios, ("descripcion", "contacto_reportante"))
    if any(not isinstance(v, str) or len(v) > (5000 if k == "descripcion" else 150) for k, v in cambios.items()):
        raise ValidationError("Campos de reporte inválidos")
    anteriores = {k: getattr(obj, k) for k in cambios}
    for k, v in cambios.items():
        setattr(obj, k, v)
    if cerrar:
        anterior = obj.estado_reporte
        obj.estado_reporte = valor("estado_reporte", "Cerrado")
        HistorialEstadoReporte.objects.create(reporte=obj, estado_anterior=anterior,
            estado_nuevo=obj.estado_reporte, usuario_actor=actor, observacion="Cierre por el reportante")
    obj.save()
    # Las versiones completas son privadas, igual que las correcciones de aceptados.
    CorreccionReporte.objects.create(reporte=obj, solicitante=actor, propuesta=cambios,
        base=anteriores, motivo="Edición del reportante antes de aceptación", estado="APROBADA")
    auditar(actor, "reporte.propio_cerrar" if cerrar else "reporte.propio_editar", "reporte", pk)
    return obj
