"""API del negocio para el panel y el cliente móvil; nunca concede por mostrar botones."""
from django.db import transaction
from django.http import FileResponse
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .views import VistaSegura, entrada
from . import flujos as f, flujos_serializers as s, documentos
from . import models as m
from .autorizacion import exigir, puede, principal_de
from .servicios import auditar


class Privada(VistaSegura):
    def finalize_response(self, request, response, *args, **kwargs):
        respuesta = super().finalize_response(request, response, *args, **kwargs)
        respuesta["Cache-Control"] = "no-store"
        respuesta["X-Content-Type-Options"] = "nosniff"
        return respuesta


def resultado(obj):
    return Response({"id": obj.pk, "estado": getattr(obj, "estado", "GUARDADO")})


class DelegarCuentaView(Privada):
    def post(self, request, entidad_id):
        return resultado(f.delegar_cuenta(request.user, entidad_id, **entrada(s.DelegacionEntrada, request)))


class CuentasView(Privada):
    def get(self, request, entidad_id):
        if not (principal_de(request.user, entidad_id) and puede(request.user, "cuenta.aprobar", entidad_id=entidad_id)) and not f.delegado(request.user, entidad_id):
            raise PermissionDenied("Solo principal o persona delegada de esta entidad")
        return Response(list(m.PropuestaCuenta.objects.filter(entidad_id=entidad_id).order_by("-pk")
            .values("id", "estado", "banco", "tipo", "titular", "ultimos4", "preparador_id", "creada")[:100]))

    def post(self, request, entidad_id):
        return resultado(f.proponer_cuenta(request.user, entidad_id, entrada(s.CuentaEntrada, request)))


class CuentaRevisionView(Privada):
    def get(self, request, pk):
        from core.crypto import descifrar
        obj = f.obtener(m.PropuestaCuenta, pk)
        if not (principal_de(request.user, obj.entidad_id) and puede(request.user, "cuenta.aprobar", entidad_id=obj.entidad_id)) and not (obj.preparador_id == request.user.pk and f.delegado(request.user, obj.entidad_id)):
            raise PermissionDenied("Propuesta no disponible")
        return Response({"id": obj.pk, "estado": obj.estado, "numero": descifrar(obj.numero_cifrado),
            "banco": obj.banco, "tipo": obj.tipo, "titular": obj.titular})

    def post(self, request, pk):
        return resultado(f.resolver_cuenta(request.user, pk, **entrada(s.Decision, request)))


class ExcepcionesView(Privada):
    def post(self, request):
        d = entrada(s.ExcepcionEntrada, request)
        return resultado(f.solicitar_excepcion(request.user, d["recurso"], d["objeto_id"], d["motivo"]))

    def get(self, request):
        resultado = []
        for obj in m.AccesoExcepcional.objects.order_by("-pk")[:500]:
            if obj.solicitante_id == request.user.pk or f.autoridad(request.user, obj.recurso, obj.objeto_id):
                resultado.append({"id": obj.pk, "recurso": obj.recurso, "objeto_id": obj.objeto_id,
                    "estado": obj.estado, "solicitante_id": obj.solicitante_id, "motivo": obj.motivo,
                    "expira": obj.expira, "revocada": obj.revocada})
        return Response(resultado)


class ExcepcionResolverView(Privada):
    def post(self, request, pk):
        return resultado(f.resolver_excepcion(request.user, pk, **entrada(s.DecisionExcepcion, request)))


class ExcepcionRevocarView(Privada):
    def post(self, request, pk):
        from .serializers import MotivoEntrada
        return resultado(f.revocar_excepcion(request.user, pk, **entrada(MotivoEntrada, request)))


class DocumentoCargarView(Privada):
    def post(self, request, recurso, pk):
        if set(request.data) != {"archivo"}:
            raise ValidationError("Se requiere únicamente el archivo")
        obj = documentos.cargar(request.user, recurso, pk, request.FILES.get("archivo"))
        return Response({"id": obj.pk, "mime": obj.mime, "tamano": obj.tamano,
            "etiqueta": "Aportado por el dueño · No verificado" if recurso == "expediente" else "Documento privado"}, status=201)


class DocumentoDescargarView(Privada):
    def get(self, request, pk):
        f.exigir_lectura(request.user, "soporte", pk)
        obj = f.obtener(m.DocumentoPrivado, pk)
        path = documentos.ruta(obj)
        if not path.is_file():
            raise NotFound("Contenido de archivo no disponible")
        auditar(request.user, "documento.descargar", "soporte", pk)
        respuesta = FileResponse(path.open("rb"), as_attachment=True,
            filename=f"documento-{pk}{path.suffix}", content_type=obj.mime)
        respuesta["Content-Security-Policy"] = "sandbox; default-src 'none'"
        return respuesta


def documentos_de(recurso, pk):
    registros = list(m.DocumentoPrivado.objects.filter(recurso=recurso, objeto_id=pk)
        .values("id", "mime", "tamano", "creada", "propietario_id"))
    if recurso == "expediente":
        for doc in registros:
            doc["etiqueta"] = "Aportado por el dueño · No verificado automáticamente"
    return registros


class RegistroPrivadoView(Privada):
    def get(self, request, recurso, pk):
        f.exigir_lectura(request.user, recurso, pk)
        obj = f.objeto_privado(recurso, pk)
        data = {"id": pk, "recurso": recurso}
        if recurso == "historial":
            data.update(detalle=obj.detalle, mascota_id=obj.mascota_id, autor_id=obj.usuario_registrador_id,
                fecha=obj.fecha_atencion, enmiendas=list(m.EnmiendaClinica.objects.filter(original=obj)
                .values("id", "autor_id", "detalle", "motivo", "creada")))
        elif recurso == "expediente":
            data.update(nombre=obj.nombre,
                historiales=list(obj.historialmedico_set.values_list("pk", flat=True)),
                documentos=documentos_de(recurso, pk),
                revisiones=list(m.RevisionSoporte.objects.filter(documento__recurso="expediente", documento__objeto_id=pk)
                    .values("id", "documento_id", "profesional_id", "resultado", "observacion", "creada")))
        elif recurso == "adopcion":
            fila = m.RespuestasAdopcion.objects.filter(solicitud=obj).first()
            data.update(estado=obj.estado_adopcion.nombre, mascota_id=obj.mascota_id,
                respuestas=fila.respuestas if fila else {},
                versiones=list(m.VersionRespuestas.objects.filter(solicitud=obj)
                    .values("id", "anteriores", "nuevas", "creada")),
                documentos=documentos_de(recurso, pk))
            # Observaciones internas de resolución no son campos editables por el ciudadano.
            data["observaciones"] = obj.observaciones
        elif recurso == "aporte":
            from core.crypto import descifrar
            data.update(estado=obj.estado_apadrinamiento.nombre, monto=str(obj.monto_comprometido),
                documentos=documentos_de(recurso, pk), declaraciones=[{"id": x.pk,
                    "monto": str(x.monto_declarado), "referencia": descifrar(x.referencia_cifrada) if x.referencia_cifrada else ""}
                    for x in obj.declaraciontransferencia_set.all()],
                confirmaciones=list(obj.confirmacionaporte_set.values("monto_confirmado", "fecha_confirmacion", "usuario_confirmador_id")))
        elif recurso == "pedido":
            data.update(estado=obj.estado_pedido.nombre, tienda_id=obj.tienda_id,
                lineas=list(obj.detallepedido_set.values("producto_id", "cantidad", "precio_referencia")))
        elif recurso == "verificacion":
            data.update(estado=obj.estado_solicitud.nombre, entidad_id=obj.entidad_id,
                observacion=obj.observacion, documentos=documentos_de(recurso, pk))
        elif recurso == "soporte":
            data.update(mime=obj.mime, tamano=obj.tamano, creada=obj.creada)
        elif recurso == "reclamacion":
            data.update(estado=obj.estado, motivo=obj.motivo, documentos=documentos_de(recurso, pk))
            if obj.revisor_id == request.user.pk:
                data.update(mascota_id=obj.mascota_id, dueno_actual_id=obj.mascota.dueno_id,
                            reclamante_id=obj.reclamante_id, dueno_revisado_id=obj.dueno_revisado_id)
        auditar(request.user, "registro.consultar", recurso, pk)
        return Response(data)


class EnmiendaView(Privada):
    def post(self, request, pk):
        return resultado(f.enmendar(request.user, pk, **entrada(s.EnmiendaEntrada, request)))


class SoporteRevisionView(Privada):
    def post(self, request, pk):
        return resultado(f.revisar_soporte(request.user, pk, **entrada(s.SoporteEntrada, request)))


class AdopcionRespuestasView(Privada):
    def post(self, request, pk):
        return resultado(f.cambiar_adopcion(request.user, pk, **entrada(s.RespuestasEntrada, request)))


class AdopcionRetirarView(Privada):
    def post(self, request, pk):
        if not entrada(s.RetirarEntrada, request)["confirmar"]:
            raise ValidationError("Confirma la retirada")
        return resultado(f.cambiar_adopcion(request.user, pk, retirar=True))


class CorreccionCrearView(Privada):
    def post(self, request, pk):
        return resultado(f.proponer_correccion(request.user, pk, **entrada(s.CorreccionEntrada, request)))

    def get(self, request, pk):
        from rescue.models import Reporte, CasoRescate
        reporte = f.obtener(Reporte, pk)
        caso = CasoRescate.objects.filter(reporte=reporte).first()
        if reporte.usuario_reportante_id != request.user.pk and not (caso and puede(request.user, "caso.ver", entidad_id=caso.fundacion_id)):
            raise PermissionDenied("Reporte no disponible")
        return Response(list(m.CorreccionReporte.objects.filter(reporte=reporte).values(
            "id", "estado", "propuesta", "base", "motivo", "creada")))


class ReportePropioView(Privada):
    def patch(self, request, pk):
        d = entrada(s.CorreccionEntrada, request)
        return resultado(f.editar_reporte_pendiente(request.user, pk, d["propuesta"]))

    def post(self, request, pk):
        if not entrada(s.RetirarEntrada, request)["confirmar"]:
            raise ValidationError("Confirma el cierre")
        return resultado(f.editar_reporte_pendiente(request.user, pk, {}, cerrar=True))


class CorreccionResolverView(Privada):
    def post(self, request, pk):
        return resultado(f.resolver_correccion(request.user, pk, **entrada(s.Decision, request)))


class ReporteModeracionView(Privada):
    def post(self, request, pk):
        return resultado(f.moderar_reporte(request.user, pk, **entrada(s.Accion, request)))


class VerificacionResolverView(Privada):
    def post(self, request, pk):
        return resultado(f.resolver_verificacion(request.user, pk, **entrada(s.Accion, request)))


class VerificacionCrearView(Privada):
    @transaction.atomic
    def post(self, request, entidad_id):
        from core.models import SolicitudValidacion, EntidadVerificable
        if request.data:
            raise ValidationError("Esta acción no admite datos de estado o solicitante")
        f.obtener(EntidadVerificable, entidad_id, True)
        f.principal(request.user, entidad_id)
        if SolicitudValidacion.objects.filter(entidad_id=entidad_id, fecha_resolucion__isnull=True).exists():
            raise ValidationError("Ya hay una solicitud abierta")
        obj = SolicitudValidacion.objects.create(entidad_id=entidad_id, usuario_solicitante=request.user,
            estado_solicitud=f.valor("estado_solicitud_validacion", "Pendiente"))
        auditar(request.user, "verificacion.crear", "verificacion", obj.pk, entidad_id)
        return resultado(obj)


class AnunciosView(Privada):
    def get(self, request, entidad_id):
        exigir(request.user, "publicidad.gestionar", entidad_id=entidad_id)
        return Response(list(m.VersionAnuncio.objects.filter(anuncio__entidad_id=entidad_id).order_by("-pk")
            .values("id", "anuncio_id", "estado", "titulo", "texto", "url", "inicio", "fin")[:100]))

    def post(self, request, entidad_id):
        return resultado(f.nueva_version_anuncio(request.user, entidad_id, entrada(s.VersionEntrada, request)))


class AnuncioVersionView(Privada):
    def post(self, request, pk):
        anuncio = f.obtener(m.Anuncio, pk)
        return resultado(f.nueva_version_anuncio(request.user, anuncio.entidad_id,
            entrada(s.VersionEntrada, request), anuncio_id=pk))


class AnuncioRevisionView(Privada):
    def post(self, request, pk):
        return resultado(f.revisar_anuncio(request.user, pk, **entrada(s.Accion, request)))


class ColaPublicidadView(Privada):
    def get(self, request):
        exigir(request.user, "publicidad.revisar")
        return Response(list(m.VersionAnuncio.objects.filter(estado="PENDIENTE").exclude(autor=request.user)
            .values("id", "anuncio_id", "titulo", "texto", "url", "inicio", "fin")[:100]))


class ReclamacionesView(Privada):
    def get(self, request):
        if puede(request.user, "reclamacion.tomar"):
            qs = m.ReclamacionMascota.objects.filter(estado="PENDIENTE", revisor__isnull=True).exclude(reclamante=request.user).exclude(mascota__dueno=request.user)
        else:
            qs = m.ReclamacionMascota.objects.filter(reclamante=request.user)
        return Response(list(qs.values("id", "estado")[:100]))

    @transaction.atomic
    def post(self, request):
        from animals.models import Mascota
        d = entrada(s.ReclamarEntrada, request)
        mascota = f.obtener(Mascota, d["mascota_id"], True)
        if m.ReclamacionMascota.objects.filter(mascota=mascota, reclamante=request.user,
                estado__in=["PENDIENTE", "FAVORABLE"]).exists():
            raise ValidationError("Ya tienes una reclamación abierta")
        obj = m.ReclamacionMascota.objects.create(mascota=mascota, reclamante=request.user, motivo=d["motivo"])
        auditar(request.user, "reclamacion.crear", "reclamacion", obj.pk)
        return resultado(obj)


class ReclamacionTomarView(Privada):
    def post(self, request, pk):
        if request.data:
            raise ValidationError("La toma no admite elegir revisor")
        return resultado(f.tomar_reclamacion(request.user, pk))


class ReclamacionResolverView(Privada):
    def post(self, request, pk):
        return resultado(f.resolver_reclamacion(request.user, pk, **entrada(s.Decision, request)))


class TitularidadView(Privada):
    def post(self, request, pk):
        return resultado(f.ejecutar_titularidad(request.user, pk, **entrada(s.TitularidadEntrada, request)))


class PedidoEstadoView(Privada):
    def post(self, request, pk):
        return resultado(f.actualizar_pedido(request.user, pk, **entrada(s.EstadoEntrada, request)))


class CasoEstadoView(Privada):
    def post(self, request, pk):
        return resultado(f.actualizar_caso(request.user, pk, **entrada(s.EstadoEntrada, request)))


class AutorizacionRevocarView(Privada):
    @transaction.atomic
    def post(self, request, pk):
        from animals.models import AutorizacionExpediente
        from animals.services import _custodio_puede
        from .serializers import MotivoEntrada
        obj = f.obtener(AutorizacionExpediente, pk, True)
        d = entrada(MotivoEntrada, request)
        if not _custodio_puede(obj.mascota, request.user.pk):
            raise PermissionDenied("Solo el titular o custodio competente puede revocar")
        obj.fecha_revocacion = timezone.now()
        obj.save(update_fields=["fecha_revocacion"])
        auditar(request.user, "expediente.autorizacion_revocar", "expediente", obj.mascota_id, motivo=d["motivo"])
        return resultado(obj)


class PublicidadAnteriorOcultarView(Privada):
    @transaction.atomic
    def post(self, request, pk):
        from commerce.models import EspacioPublicitario
        from .serializers import MotivoEntrada
        exigir(request.user, "publicidad.revisar")
        obj = f.obtener(EspacioPublicitario, pk, True)
        motivo = entrada(MotivoEntrada, request)["motivo"]
        anterior = obj.estado_publicidad.nombre
        obj.estado_publicidad = f.valor("estado_publicidad", "Rechazada")
        obj.usuario_revisor = request.user
        obj.fecha_decision = timezone.now()
        obj.save(update_fields=["estado_publicidad", "usuario_revisor", "fecha_decision"])
        auditar(request.user, "publicidad.anterior_ocultar", "publicidad", pk,
            obj.anunciante_id, motivo, anterior=anterior)
        return resultado(obj)


class MascotaCrearView(Privada):
    @transaction.atomic
    def post(self, request):
        from animals.models import Mascota, Raza
        datos = entrada(s.MascotaEntrada, request)
        f.obtener(Raza, datos["raza_id"])
        fecha = datos.get("fecha_nacimiento")
        if fecha and fecha > timezone.localdate():
            raise ValidationError("La fecha de nacimiento no puede estar en el futuro")
        obj = Mascota.objects.create(dueno=request.user, estado_mascota=f.valor("estado_mascota", "Con dueño"), **datos)
        auditar(request.user, "mascota.declarar", "expediente", obj.pk)
        return Response({"id": obj.pk, "propiedad": "DECLARADA_NO_VERIFICADA"}, status=201)


class ProductosView(Privada):
    def get(self, request, entidad_id):
        from commerce.models import Producto
        exigir(request.user, "producto.gestionar", entidad_id=entidad_id)
        return Response(list(Producto.objects.filter(tienda_id=entidad_id)
            .values("id_producto", "nombre", "precio", "existencias", "estado_producto_id")[:100]))

    @transaction.atomic
    def post(self, request, entidad_id):
        from commerce.models import Producto
        from core.models import Tienda
        exigir(request.user, "producto.gestionar", entidad_id=entidad_id)
        f.entidad_verificada(entidad_id)
        f.obtener(Tienda, entidad_id)
        d = entrada(s.ProductoEntrada, request)
        if not {"nombre", "precio", "categoria_id", "tipo_id"}.issubset(d):
            raise ValidationError("Faltan nombre, precio, categoría o tipo")
        obj = Producto(tienda_id=entidad_id)
        guardar_producto(obj, request.user, d)
        return resultado(obj)


def guardar_producto(obj, actor, d):
    from core.models import ValorMaestro
    previo = {k: str(getattr(obj, k)) for k in ("nombre", "precio", "existencias", "estado_producto_id")} if obj.pk else {}
    disponible = d.pop("disponible", obj.estado_producto.nombre == "Disponible" if obj.pk else True)
    for k, tipo, campo in (("categoria_id", "categoria_producto", "categoria_producto_id"), ("tipo_id", "tipo_producto", "tipo_producto_id")):
        if k in d:
            identificador = d.pop(k)
            if not ValorMaestro.objects.filter(pk=identificador, tipo__nombre=tipo).exists():
                raise ValidationError("Categoría o tipo no válido")
            setattr(obj, campo, identificador)
    for k, v in d.items():
        setattr(obj, k, v)
    obj.estado_producto = f.valor("estado_producto", "Disponible" if disponible else "Inactivo")
    obj.save()
    m.CambioProducto.objects.create(producto=obj, actor=actor, anteriores=previo,
        nuevos={k: str(getattr(obj, k)) for k in ("nombre", "precio", "existencias", "estado_producto_id")})
    auditar(actor, "producto.guardar", "producto", obj.pk, obj.tienda_id)


class ProductoEditarView(Privada):
    @transaction.atomic
    def patch(self, request, pk):
        from commerce.models import Producto
        obj = f.obtener(Producto, pk, True)
        exigir(request.user, "producto.gestionar", entidad_id=obj.tienda_id)
        f.entidad_verificada(obj.tienda_id)
        guardar_producto(obj, request.user, entrada(s.ProductoEntrada, request))
        return resultado(obj)


class MisRegistrosView(Privada):
    def get(self, request):
        from adoption.models import SolicitudAdopcion
        from core.models import SolicitudValidacion
        return Response({
            "adopciones": list(SolicitudAdopcion.objects.filter(usuario_adoptante=request.user).values("id_solicitud_adopcion", "estado_adopcion__nombre")[:100]),
            "verificaciones": list(SolicitudValidacion.objects.filter(usuario_solicitante=request.user).values("id_solicitud_validacion", "estado_solicitud__nombre")[:100]),
            "asignaciones": list(m.AsignacionRecurso.objects.filter(usuario=request.user).values("recurso__codigo", "objeto_id", "fecha_revocacion")[:100]),
            "reclamaciones_asignadas": list(m.ReclamacionMascota.objects.filter(revisor=request.user).values("id", "estado")[:100]),
        })


def publicidad_publica():
    ahora = timezone.now()
    salida = []
    for anuncio in m.Anuncio.objects.filter(oculto=False, entidad__estado_verificacion__nombre="Verificada").order_by("-pk")[:100]:
        # La última aprobada sustituye a la anterior; una pendiente no la sustituye.
        version = m.VersionAnuncio.objects.filter(anuncio=anuncio, estado="APROBADA", inicio__lte=ahora).order_by("-pk").first()
        if version and version.inicio <= ahora < version.fin:
            salida.append({"id_anuncio": anuncio.pk, "version_id": version.pk,
                "titulo": version.titulo, "texto": version.texto, "url_destino": version.url,
                "anunciante": anuncio.entidad.nombre})
    return salida


class ReportesPublicosView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from rescue.models import Reporte
        ocultos = m.PublicacionReporte.objects.filter(oculta=True).values_list("reporte_id", flat=True)
        return Response(list(Reporte.objects.exclude(pk__in=ocultos).order_by("-pk")
            .values("id_reporte", "descripcion", "tipo_reporte__nombre", "estado_reporte__nombre")[:100]))
