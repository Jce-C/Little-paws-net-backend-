"""Reglas de negocio del fondo externo, sin procesamiento de pagos."""

from django.db import IntegrityError, transaction
from django.utils import timezone

from core.crypto import cifrar
from core.models import ValorMaestro

from .models import DistribucionReportadaFondo, DonacionGeneral, FondoExterno, HistorialEstadoDonacion
from .permissions import administrador_puede, gestor_fundacion_puede


class FondoError(ValueError):
    pass


class FondoPermisoError(FondoError):
    pass


class FondoNoEncontradoError(FondoError):
    pass


class FondoTransicionError(FondoError):
    pass


@transaction.atomic
def crear_fondo_externo(*, usuario_actor, nombre, instrucciones_transferencia):
    if not administrador_puede(usuario_actor, "fondo.gestionar"):
        raise FondoPermisoError("No tiene permiso para configurar fondos")
    nombre = nombre.strip()
    instrucciones_transferencia = instrucciones_transferencia.strip()
    if not nombre or not instrucciones_transferencia:
        raise FondoError("Nombre e instrucciones son obligatorios")
    if FondoExterno.objects.filter(nombre__iexact=nombre).exists():
        raise FondoError("Ya existe un fondo con ese nombre")
    try:
        return FondoExterno.objects.create(
            nombre=nombre,
            datos_transferencia_cifrados=cifrar(instrucciones_transferencia),
        )
    except IntegrityError as exc:
        raise FondoError("Ya existe un fondo con ese nombre") from exc


@transaction.atomic
def crear_compromiso_donacion(*, usuario_donante, fondo_externo, monto_comprometido):
    if not usuario_donante.is_active:
        raise FondoPermisoError("La cuenta del donante no está activa")
    if monto_comprometido <= 0:
        raise FondoError("El monto comprometido debe ser positivo")
    estado = ValorMaestro.objects.get(tipo__nombre="estado_donacion", nombre="Comprometida")
    donacion = DonacionGeneral.objects.create(
        fondo_externo=fondo_externo,
        usuario_donante=usuario_donante,
        estado_donacion=estado,
        monto_comprometido=monto_comprometido,
    )
    HistorialEstadoDonacion.objects.create(
        donacion=donacion,
        estado_nuevo=estado,
        usuario_actor=usuario_donante,
        observacion="Registro del compromiso; no confirma recepción de dinero",
    )
    return donacion


@transaction.atomic
def resolver_compromiso_donacion(*, donacion_id, usuario_actor, estado, observacion, referencia_externa=""):
    if not administrador_puede(usuario_actor, "donacion.confirmar"):
        raise FondoPermisoError("No tiene permiso para resolver donaciones")
    if estado not in ("Confirmada", "Rechazada"):
        raise FondoError("La decisión debe ser Confirmada o Rechazada")
    observacion = observacion.strip()
    referencia_externa = referencia_externa.strip()
    if not observacion:
        raise FondoError("La resolución requiere una observación")
    if estado == "Confirmada" and not referencia_externa:
        raise FondoError("La confirmación requiere una referencia externa verificable")
    try:
        donacion = DonacionGeneral.objects.select_for_update().select_related(
            "estado_donacion__tipo",
        ).get(pk=donacion_id)
    except DonacionGeneral.DoesNotExist as exc:
        raise FondoNoEncontradoError("Donación inexistente") from exc
    if donacion.usuario_donante_id == usuario_actor.pk:
        raise FondoPermisoError("No puede resolver su propio compromiso")
    anterior = donacion.estado_donacion
    if anterior.tipo.nombre != "estado_donacion" or anterior.nombre != "Comprometida":
        raise FondoTransicionError("Solo se puede resolver una donación comprometida")
    nuevo_estado = ValorMaestro.objects.get(tipo__nombre="estado_donacion", nombre=estado)
    donacion.estado_donacion = nuevo_estado
    donacion.save(update_fields=["estado_donacion"])
    detalle = observacion
    if estado == "Confirmada":
        detalle = f"{observacion} | Referencia externa: {referencia_externa}"
    HistorialEstadoDonacion.objects.create(
        donacion=donacion,
        estado_anterior=anterior,
        estado_nuevo=nuevo_estado,
        usuario_actor=usuario_actor,
        observacion=detalle,
    )
    return donacion


@transaction.atomic
def reportar_distribucion(*, usuario_actor, fondo_externo, fundacion, monto_reportado,
                         fecha_distribucion, criterio, archivo_evidencia):
    if not administrador_puede(usuario_actor, "distribucion.reportar"):
        raise FondoPermisoError("No tiene permiso para reportar distribuciones")
    if fundacion.entidad.estado_verificacion.tipo.nombre != "estado_verificacion" or (
        fundacion.entidad.estado_verificacion.nombre != "Verificada"
    ):
        raise FondoError("La fundación destinataria debe estar verificada")
    if monto_reportado <= 0 or fecha_distribucion > timezone.now():
        raise FondoError("El monto debe ser positivo y la fecha no puede ser futura")
    if not criterio.strip():
        raise FondoError("El criterio es obligatorio")
    if archivo_evidencia.visibilidad != "PRIVADO" or archivo_evidencia.usuario_cargador_id != usuario_actor.pk:
        raise FondoError("La evidencia debe ser privada y pertenecer al usuario reportador")
    estado = ValorMaestro.objects.get(tipo__nombre="estado_distribucion", nombre="Reportada")
    return DistribucionReportadaFondo.objects.create(
        fondo_externo=fondo_externo, fundacion=fundacion, monto_reportado=monto_reportado,
        fecha_distribucion=fecha_distribucion, criterio=criterio.strip(),
        archivo_evidencia=archivo_evidencia, usuario_reportador=usuario_actor,
        estado_distribucion=estado,
    )


@transaction.atomic
def confirmar_distribucion(*, distribucion_id, usuario_actor, observacion_confirmacion):
    try:
        distribucion = DistribucionReportadaFondo.objects.select_for_update().select_related(
            "estado_distribucion__tipo",
        ).get(pk=distribucion_id)
    except DistribucionReportadaFondo.DoesNotExist as exc:
        raise FondoNoEncontradoError("Distribución inexistente") from exc
    if not gestor_fundacion_puede(usuario_actor, distribucion.fundacion_id, "distribucion.confirmar"):
        raise FondoPermisoError("No es gestor autorizado de la fundación destinataria")
    if distribucion.usuario_reportador_id == usuario_actor.pk:
        raise FondoPermisoError("El reportador no puede confirmar su propio registro")
    if distribucion.estado_distribucion.tipo.nombre != "estado_distribucion" or (
        distribucion.estado_distribucion.nombre != "Reportada"
    ):
        raise FondoTransicionError("Solo se puede confirmar una distribución reportada")
    observacion_confirmacion = observacion_confirmacion.strip()
    if not observacion_confirmacion:
        raise FondoError("La confirmación requiere una observación")
    distribucion.estado_distribucion = ValorMaestro.objects.get(
        tipo__nombre="estado_distribucion", nombre="Confirmada",
    )
    distribucion.usuario_confirmador = usuario_actor
    distribucion.fecha_confirmacion = timezone.now()
    distribucion.observacion_confirmacion = observacion_confirmacion
    distribucion.save(update_fields=[
        "estado_distribucion", "usuario_confirmador", "fecha_confirmacion", "observacion_confirmacion",
    ])
    return distribucion
