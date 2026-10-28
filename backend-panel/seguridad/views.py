from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Usuario
from core.models import EntidadMiembro, EntidadMiembroRol, EntidadVerificable, Permiso, Recurso, Rol, RolPermiso, UsuarioRol
from .autorizacion import exigir, puede, tiene_base, usuario_activo
from .models import AsignacionRecurso, EventoSeguridad, ResponsableEntidad, TransferenciaResponsabilidad
from .objetos import MODELOS, contexto
from .politicas import POLITICAS, ROLES, SEGURIDAD
from .serializers import (
    ComprobacionEntrada, FondoEntrada, MiembroEntrada, MotivoEntrada, PermisoSerializer,
    PermisosRolEntrada, PrincipalEntrada, RecursoSerializer, ResolucionTransferenciaEntrada,
    RolEntidadEntrada, RolGlobalEntrada, RolSerializer, TransferenciaEntrada, UsuarioSerializer,
)
from . import servicios


class ErroresControlados:
    def handle_exception(self, exc):
        if isinstance(exc, ObjectDoesNotExist):
            return Response({"detalle": "Registro no disponible en este ámbito"}, status=404)
        if isinstance(exc, IntegrityError):
            return Response({"detalle": "Conflicto con un registro existente"}, status=409)
        return super().handle_exception(exc)


def entrada(clase, request):
    serializador = clase(data=request.data)
    serializador.is_valid(raise_exception=True)
    return serializador.validated_data


class Paginacion(PageNumberPagination):
    page_size = 25
    page_size_query_param = "limite"
    max_page_size = 100


class CatalogoViewSet(ErroresControlados, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = Paginacion
    http_method_names = ["get", "post", "patch", "head", "options"]
    filter_backends = [SearchFilter]
    recurso = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        accion = {"list": "ver", "retrieve": "ver", "create": "crear", "partial_update": "editar", "permisos": "editar"}.get(self.action, "ver")
        if self.action == "permisos" and request.method == "GET":
            accion = "ver"
        exigir(request.user, f"{self.recurso}.{accion}")

    @transaction.atomic
    def perform_create(self, serializer):
        servicios.bloqueo_seguridad()
        exigir(self.request.user, f"{self.recurso}.crear")
        objeto = serializer.save()
        servicios.auditar(self.request.user, f"{self.recurso}.crear", self.recurso, objeto.pk)

    @transaction.atomic
    def perform_update(self, serializer):
        servicios.bloqueo_seguridad()
        exigir(self.request.user, f"{self.recurso}.editar")
        objeto = serializer.save()
        servicios.auditar(self.request.user, f"{self.recurso}.editar", self.recurso, objeto.pk,
                          campos=sorted(serializer.validated_data))


class UsuariosViewSet(CatalogoViewSet):
    recurso = "usuarios"
    queryset = Usuario.objects.order_by("id_usuario")
    serializer_class = UsuarioSerializer
    search_fields = ["nombre", "email"]

    @transaction.atomic
    def perform_create(self, serializer):
        servicios.bloqueo_seguridad()
        exigir(self.request.user, "usuarios.crear")
        usuario = serializer.save()
        UsuarioRol.objects.get_or_create(usuario=usuario, rol=Rol.objects.get(codigo="CIUDADANO"))
        servicios.auditar(self.request.user, "usuario.crear", "usuarios", usuario.pk)

    def perform_update(self, serializer):
        serializer.instance = servicios.guardar_estado_usuario(self.request.user, serializer.instance, serializer.validated_data)


class RecursosViewSet(CatalogoViewSet):
    recurso = "recursos"
    queryset = Recurso.objects.order_by("codigo")
    serializer_class = RecursoSerializer
    search_fields = ["codigo", "nombre"]


class PermisosViewSet(CatalogoViewSet):
    recurso = "permisos"
    queryset = Permiso.objects.select_related("recurso").order_by("codigo")
    serializer_class = PermisoSerializer
    search_fields = ["codigo", "descripcion"]

    @transaction.atomic
    def perform_update(self, serializer):
        super().perform_update(serializer)
        permiso = serializer.instance
        if not permiso.activo:
            usuarios = set(UsuarioRol.objects.filter(rol__rolpermiso__permiso=permiso).values_list("usuario_id", flat=True))
            usuarios.update(EntidadMiembroRol.objects.filter(rol__rolpermiso__permiso=permiso).values_list("miembro__usuario_id", flat=True))
            for usuario_id in usuarios:
                servicios.limpiar_asignaciones(usuario_id)


class RolesViewSet(CatalogoViewSet):
    recurso = "roles"
    queryset = Rol.objects.order_by("nombre")
    serializer_class = RolSerializer
    search_fields = ["codigo", "nombre"]

    @transaction.atomic
    def perform_update(self, serializer):
        servicios.bloqueo_seguridad()
        super().perform_update(serializer)
        self._limpiar(serializer.instance)

    def _limpiar(self, rol):
        ids = set(UsuarioRol.objects.filter(rol=rol).values_list("usuario_id", flat=True))
        ids.update(EntidadMiembroRol.objects.filter(rol=rol).values_list("miembro__usuario_id", flat=True))
        for pk in ids:
            servicios.limpiar_asignaciones(pk)

    @action(detail=True, methods=["get", "post"])
    def permisos(self, request, pk=None):
        rol = self.get_object()
        if request.method == "GET":
            exigir(request.user, "roles.ver")
            return Response(PermisoSerializer(Permiso.objects.filter(rolpermiso__rol=rol).order_by("codigo"), many=True).data)
        ids = entrada(PermisosRolEntrada, request)["permisos"]
        permisos = list(Permiso.objects.filter(pk__in=ids))
        codigos = {p.codigo for p in permisos}
        if any(p.codigo not in POLITICAS for p in permisos):
            raise ValidationError("El servidor no reconoce alguna de las acciones")
        if rol.sistema and (rol.codigo not in ROLES or not codigos.issubset(set(ROLES[rol.codigo][3]))):
            raise ValidationError("No se pueden ampliar las responsabilidades del rol del sistema")
        if rol.codigo in ("ADMIN_SEGURIDAD", "RESPONSABLE_PRINCIPAL", "RESPONSABLE_SECUNDARIO") and codigos != set(ROLES[rol.codigo][3]):
            raise ValidationError("Los permisos estructurales del rol deben conservarse")
        if rol.ambito == "ENTIDAD" and any(p.alcance == "GLOBAL" or p.recurso.codigo in ("verificacion", "reclamacion") for p in permisos):
            raise ValidationError("Un rol de entidad no puede recibir permisos globales")
        if rol.ambito == "GLOBAL":
            seguridad = codigos.intersection(SEGURIDAD)
            moderacion = {c for c in codigos if c.startswith(("verificacion.", "entidad.", "publicidad.", "reporte.", "reclamacion."))}
            if seguridad and moderacion:
                raise ValidationError("Seguridad y moderación deben permanecer en roles separados")
            if any(p.alcance not in ("GLOBAL", "ASIGNADO") or (p.alcance == "ASIGNADO" and p.recurso.codigo not in ("verificacion", "reclamacion")) for p in permisos):
                raise ValidationError("El permiso requiere un rol y contexto de entidad")
        with transaction.atomic():
            servicios.bloqueo_seguridad()
            exigir(request.user, "roles.editar")
            Rol.objects.select_for_update().get(pk=rol.pk)
            RolPermiso.objects.filter(rol=rol).exclude(permiso_id__in=ids).delete()
            for permiso in permisos:
                RolPermiso.objects.get_or_create(rol=rol, permiso=permiso)
            self._limpiar(rol)
            servicios.auditar(request.user, "rol.permisos", "roles", rol.pk, permisos=sorted(codigos))
        return Response({"guardado": True, "permisos": sorted(codigos)})


class VistaSegura(ErroresControlados, APIView):
    permission_classes = [IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if not usuario_activo(request.user):
            raise PermissionDenied("Cuenta inactiva")


class EfectivosView(VistaSegura):
    def get(self, request):
        globales = list(UsuarioRol.objects.filter(usuario=request.user, fecha_revocacion__isnull=True,
            rol__activo=True, rol__ambito="GLOBAL").values_list("rol__codigo", flat=True))
        miembros = EntidadMiembro.objects.filter(usuario=request.user, fecha_salida__isnull=True).select_related("entidad")
        entidades = []
        for miembro in miembros:
            roles = list(EntidadMiembroRol.objects.filter(miembro=miembro, fecha_revocacion__isnull=True,
                rol__activo=True, rol__ambito="ENTIDAD").exclude(rol__codigo="RESPONSABLE_PRINCIPAL").values_list("rol__codigo", flat=True))
            if ResponsableEntidad.objects.filter(entidad=miembro.entidad, principal=miembro).exists():
                roles.append("RESPONSABLE_PRINCIPAL")
            entidades.append({"id": miembro.entidad_id, "nombre": miembro.entidad.nombre, "roles": roles,
                "prepara_cuentas": puede(request.user, "cuenta.preparar", entidad_id=miembro.entidad_id),
                "permisos": [{"codigo": c, "alcance": politica[2]} for c, politica in POLITICAS.items()
                             if politica[2] != "GLOBAL" and politica[0] not in ("verificacion", "reclamacion")
                             and tiene_base(request.user, c, entidad_id=miembro.entidad_id)]})
        return Response({"usuario": {"id": request.user.pk, "nombre": request.user.nombre},
            "roles_globales": globales, "entidades": entidades,
            "permisos_globales": [{"codigo": c, "alcance": p[2]} for c, p in POLITICAS.items()
                                 if (p[2] == "GLOBAL" or p[0] in ("verificacion", "reclamacion")) and tiene_base(request.user, c)],
            "nota": "ASIGNADO y AUTORIZADO requieren comprobar también el registro concreto"})


class ComprobarView(VistaSegura):
    def post(self, request):
        datos = entrada(ComprobacionEntrada, request)
        codigo = datos.pop("permiso")
        return Response({"permitido": puede(request.user, codigo, **datos)})


class RolGlobalView(VistaSegura):
    def post(self, request, usuario_id):
        datos = entrada(RolGlobalEntrada, request)
        asignacion = servicios.asignar_global(request.user, usuario_id, **datos)
        return Response({"id": asignacion.pk, "revocado": asignacion.fecha_revocacion is not None})


class EntidadesView(VistaSegura):
    def get(self, request):
        exigir(request.user, "entidades.ver")
        return Response(list(EntidadVerificable.objects.order_by("pk").values("id_entidad_verificable", "nombre")[:200]))


class MiembrosView(VistaSegura):
    def get(self, request, entidad_id):
        exigir(request.user, "miembros.ver", entidad_id=entidad_id)
        return Response([{"id": m.pk, "usuario_id": m.usuario_id, "nombre": m.usuario.nombre,
            "activo": m.fecha_salida is None, "roles": list(EntidadMiembroRol.objects.filter(miembro=m,
                fecha_revocacion__isnull=True, rol__activo=True).values_list("rol__codigo", flat=True)),
            "principal": ResponsableEntidad.objects.filter(entidad_id=entidad_id, principal=m).exists()}
            for m in EntidadMiembro.objects.filter(entidad_id=entidad_id).select_related("usuario").order_by("pk")[:200]])

    def post(self, request, entidad_id):
        miembro = servicios.gestionar_miembro(request.user, entidad_id, **entrada(MiembroEntrada, request))
        return Response({"id": miembro.pk, "retirado": miembro.fecha_salida is not None})


class RolEntidadView(VistaSegura):
    def post(self, request, entidad_id):
        asignacion = servicios.asignar_entidad(request.user, entidad_id, **entrada(RolEntidadEntrada, request))
        return Response({"id": asignacion.pk, "revocado": asignacion.fecha_revocacion is not None})


class PrincipalView(VistaSegura):
    def post(self, request, entidad_id):
        registro = servicios.designar_principal(request.user, entidad_id, **entrada(PrincipalEntrada, request))
        return Response({"entidad_id": entidad_id, "principal_id": registro.principal_id})


class TransferirView(VistaSegura):
    def get(self, request, entidad_id):
        # Incluye participantes aunque ya hayan dejado el cargo; no datos privados del negocio.
        qs = TransferenciaResponsabilidad.objects.filter(entidad_id=entidad_id).filter(
            Q(saliente__usuario=request.user) | Q(sucesor__usuario=request.user))
        return Response(list(qs.order_by("-pk").values("id", "saliente_id", "sucesor_id", "estado", "mantener_secundario", "creada", "resuelta")[:100]))

    def post(self, request, entidad_id):
        transferencia = servicios.iniciar_transferencia(request.user, entidad_id, **entrada(TransferenciaEntrada, request))
        return Response({"id": transferencia.pk, "estado": transferencia.estado}, status=201)


class ResolverTransferenciaView(VistaSegura):
    def post(self, request, transferencia_id):
        resultado = servicios.resolver_transferencia(request.user, transferencia_id,
            **entrada(ResolucionTransferenciaEntrada, request))
        return Response({"id": resultado.pk, "estado": resultado.estado})


class ColaView(VistaSegura):
    def get(self, request, recurso):
        from django.apps import apps
        if recurso not in MODELOS or recurso == "fondo":
            raise ValidationError("Recurso sin cola de revisión")
        entidad_id = request.query_params.get("entidad_id")
        try:
            entidad_id = int(entidad_id) if entidad_id else None
        except (ValueError, TypeError):
            raise ValidationError("Entidad inválida")
        exigir(request.user, f"{recurso}.tomar", entidad_id=entidad_id)
        modelo = apps.get_model(*MODELOS[recurso])
        qs = modelo.objects.all()
        if recurso == "adopcion":
            qs = qs.filter(mascota__custodiamascota__fundacion_id=entidad_id,
                mascota__custodiamascota__fecha_fin__isnull=True).exclude(usuario_adoptante=request.user)
        elif recurso == "aporte":
            qs = qs.filter(reporte__casorescate__fundacion_id=entidad_id)
        elif recurso == "pedido":
            qs = qs.filter(tienda_id=entidad_id)
        else:
            qs = qs.exclude(usuario_solicitante=request.user)
        ocupados = AsignacionRecurso.objects.filter(recurso__codigo=recurso,
            fecha_revocacion__isnull=True).values_list("objeto_id", flat=True)
        qs = qs.exclude(pk__in=ocupados).order_by("pk").distinct()
        # Solo identificadores de trabajo: nunca respuestas, contactos, importes o archivos.
        resultado = []
        for pk in qs.values_list("pk", flat=True)[:200]:
            ctx = contexto(recurso, pk)
            if ctx.disponible and (recurso == "verificacion" or ctx.entidad_id == entidad_id):
                resultado.append({"id": pk, "recurso": recurso})
        return Response(resultado)


class TomarView(VistaSegura):
    def post(self, request, recurso, objeto_id):
        if request.data:
            raise ValidationError("Esta operación no acepta entidad o usuario del cliente")
        asignacion = servicios.tomar(request.user, recurso, objeto_id)
        return Response({"id": asignacion.pk, "objeto_id": objeto_id, "asignado": True})


class DevolverView(VistaSegura):
    def post(self, request, recurso, objeto_id):
        servicios.devolver(request.user, recurso, objeto_id, **entrada(MotivoEntrada, request))
        return Response({"devuelto": True})


class AsignarFondoView(VistaSegura):
    def post(self, request, fondo_id):
        asignacion = servicios.asignar_fondo(request.user, fondo_id, **entrada(FondoEntrada, request))
        return Response({"id": asignacion.pk, "revocado": asignacion.fecha_revocacion is not None})


class AuditoriaView(VistaSegura):
    def get(self, request):
        exigir(request.user, "auditoria.ver")
        qs = EventoSeguridad.objects.order_by("-pk")
        paginador = Paginacion()
        pagina = paginador.paginate_queryset(qs, request)
        return paginador.get_paginated_response([{"id": e.pk, "actor_id": e.actor_id,
            "accion": e.accion, "recurso": e.recurso, "objeto_id": e.objeto_id,
            "entidad_id": e.entidad_id, "fecha": e.fecha, "motivo": e.motivo, "datos": e.datos} for e in pagina])
