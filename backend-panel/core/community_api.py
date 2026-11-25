"""Public conversations with configurable participation and server-side ownership."""
from django.db import transaction
from django.db.models import Count, Exists, OuterRef
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle
from core.models import PublicacionComunidad, ComentarioComunidad, ReaccionComunidad, InteresAyuda, Fundacion
from seguridad.autorizacion import exigir, puede
from seguridad.servicios import auditar
from seguridad.models import BajaAdministrativa
from core.models import Notificacion, ValorMaestro
from .public_avatars import descriptor as foto_publica


class EscrituraComunidadThrottle(UserRateThrottle):
    rate = "30/hour"
    scope = "community_write"


class LecturaComunidadThrottle(UserRateThrottle):
    rate = "60/min"
    scope = "community_read"


class Mensaje(serializers.Serializer):
    contenido = serializers.CharField(max_length=5000, allow_blank=False, trim_whitespace=True)


def pagina(request):
    return serializers.IntegerField(min_value=0, max_value=9223372036854775807).run_validation(request.query_params.get("antes", 0))


class SinCacheView(APIView):
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Cache-Control"] = "no-store"
        return response


class PublicacionesView(SinCacheView):
    def get_permissions(self):
        return [AllowAny()] if self.request.method in ("GET", "HEAD", "OPTIONS") else [IsAuthenticated()]

    def get_throttles(self):
        return [LecturaComunidadThrottle()] if self.request.method in ("GET", "HEAD") else [EscrituraComunidadThrottle()]

    def get(self, request):
        before = pagina(request)
        rows = PublicacionComunidad.objects.filter(oculta=False).select_related("autor", "autor__foto_comunidad").annotate(
            reacciones_total=Count("reacciones", distinct=True), comentarios_total=Count("comentarios", distinct=True),
        )
        if before:
            rows = rows.filter(pk__lt=before)
        uid = request.user.pk if request.user.is_authenticated else None
        rows = rows.annotate(reaccion_propia=Exists(ReaccionComunidad.objects.filter(publicacion_id=OuterRef("pk"), usuario_id=uid)))
        rows = list(rows.order_by("-pk")[:21])
        return Response({"results": [{"id": row.pk, "contenido": row.contenido,
            "autor": row.autor.nombre or "Miembro de la comunidad", "foto_autor": foto_publica(row.autor), "fecha": row.fecha,
            "propia": row.autor_id == uid, "reacciones": row.reacciones_total,
            "comentarios": row.comentarios_total, "reaccion_propia": row.reaccion_propia} for row in rows[:20]],
            "antes": rows[19].pk if len(rows) > 20 else None,
            "puede_publicar": bool(uid and puede(request.user, "comunidad.participar")),
            "puede_moderar": bool(uid and puede(request.user, "comunidad.moderar"))})

    @transaction.atomic
    def post(self, request):
        exigir(request.user, "comunidad.participar")
        data = Mensaje(data=request.data)
        data.is_valid(raise_exception=True)
        row = PublicacionComunidad.objects.create(autor=request.user, **data.validated_data)
        auditar(request.user, "comunidad.participar", "comunidad", row.pk, motivo="Publicación de un mensaje público")
        return Response({"id": row.pk}, status=201)


class ComentariosView(PublicacionesView):
    def get(self, request, publicacion_id):
        post = get_object_or_404(PublicacionComunidad, pk=publicacion_id, oculta=False)
        rows = post.comentarios.select_related("autor", "autor__foto_comunidad").order_by("pk")
        after = serializers.IntegerField(min_value=0, max_value=9223372036854775807).run_validation(request.query_params.get("despues", 0))
        rows = list(rows.filter(pk__gt=after)[:21])
        return Response({"results": [{"id": row.pk, "autor": row.autor.nombre or "Miembro de la comunidad", "foto_autor": foto_publica(row.autor), "contenido": row.contenido,
            "fecha": row.fecha, "respuesta_a": row.respuesta_a_id} for row in rows[:20]], "despues": rows[19].pk if len(rows) > 20 else None,
            "puede_publicar": request.user.is_authenticated and puede(request.user, "comunidad.participar")})

    @transaction.atomic
    def post(self, request, publicacion_id):
        exigir(request.user, "comunidad.participar")
        post = get_object_or_404(PublicacionComunidad.objects.select_for_update(), pk=publicacion_id, oculta=False)
        text = serializers.CharField(max_length=2000, allow_blank=False, trim_whitespace=True).run_validation(request.data.get("contenido"))
        parent = None
        if request.data.get("respuesta_a") is not None:
            pid = serializers.IntegerField(min_value=1).run_validation(request.data["respuesta_a"])
            parent = get_object_or_404(ComentarioComunidad, pk=pid, publicacion=post, respuesta_a__isnull=True)
        row = ComentarioComunidad.objects.create(publicacion=post, autor=request.user, contenido=text, respuesta_a=parent)
        auditar(request.user, "comunidad.participar", "comunidad", post.pk, motivo="Comentario público registrado", comentario_id=row.pk)
        return Response({"id": row.pk}, status=201)


class ReaccionView(SinCacheView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [EscrituraComunidadThrottle]

    @transaction.atomic
    def post(self, request, publicacion_id):
        exigir(request.user, "comunidad.participar")
        post = get_object_or_404(PublicacionComunidad.objects.select_for_update(), pk=publicacion_id, oculta=False)
        _, created = ReaccionComunidad.objects.get_or_create(publicacion=post, usuario=request.user)
        if created:
            auditar(request.user, "comunidad.participar", "comunidad", post.pk, motivo="Reacción pública registrada")
        return Response({"activa": True, "total": post.reacciones.count()})

    @transaction.atomic
    def delete(self, request, publicacion_id):
        exigir(request.user, "comunidad.participar")
        post = get_object_or_404(PublicacionComunidad.objects.select_for_update(), pk=publicacion_id, oculta=False)
        count, _ = ReaccionComunidad.objects.filter(publicacion=post, usuario=request.user).delete()
        if count:
            auditar(request.user, "comunidad.participar", "comunidad", post.pk, motivo="Reacción propia retirada")
        return Response({"activa": False, "total": post.reacciones.count()})


class RetirarPublicacionView(SinCacheView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, publicacion_id):
        post = get_object_or_404(PublicacionComunidad.objects.select_for_update(), pk=publicacion_id)
        own = post.autor_id == request.user.pk and puede(request.user, "comunidad.participar")
        exigir(request.user, "comunidad.participar" if own else "comunidad.moderar")
        reason = "Retirada por el autor" if own else serializers.CharField(min_length=5, max_length=500).run_validation(request.data.get("motivo"))
        post.oculta = True
        post.save(update_fields=["oculta"])
        auditar(request.user, "comunidad.participar" if own else "comunidad.moderar", "comunidad", post.pk, motivo=reason)
        return Response({"oculta": True})


class InteresesAyudaView(SinCacheView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [EscrituraComunidadThrottle]

    def get_throttles(self):
        return [LecturaComunidadThrottle()] if self.request.method == "GET" else [EscrituraComunidadThrottle()]

    def get(self, request):
        exigir(request.user, "ayudas.participar")
        rows = InteresAyuda.objects.filter(usuario=request.user).select_related("fundacion__entidad").order_by("-pk")[:100]
        return Response([{"id": row.pk, "organizacion": row.fundacion.entidad.nombre, "modalidad": row.modalidad, "mensaje": row.mensaje, "actividad": row.actividad, "fecha": row.fecha} for row in rows])

    @transaction.atomic
    def post(self, request):
        exigir(request.user, "ayudas.participar")
        fid = serializers.IntegerField(min_value=1).run_validation(request.data.get("fundacion_id"))
        mode = serializers.ChoiceField(choices=["voluntariado", "especie"]).run_validation(request.data.get("modalidad"))
        message = serializers.CharField(max_length=2000, allow_blank=False, trim_whitespace=True).run_validation(request.data.get("mensaje"))
        foundation = get_object_or_404(Fundacion.objects.select_for_update().filter(entidad__estado_verificacion__nombre="Verificada").exclude(
            pk__in=BajaAdministrativa.objects.filter(tipo="entidades", activo=False).values("objeto_id")), pk=fid)
        activity = serializers.CharField(max_length=100, allow_blank=True).run_validation(request.data.get("actividad", ""))
        if mode == "voluntariado" and not foundation.acepta_voluntarios:
            raise serializers.ValidationError("La organización no recibe voluntarios en este momento.")
        if activity:
            from .help_programs import descriptor as programa_publico
            program = programa_publico(foundation)
            if mode != "voluntariado" or not program or activity not in {row["titulo"] for row in program["actividades"]}:
                raise serializers.ValidationError("La actividad ya no está disponible. Actualiza la convocatoria antes de enviar.")
        row, created = InteresAyuda.objects.get_or_create(usuario=request.user, fundacion=foundation, modalidad=mode, defaults={"mensaje": message, "actividad": activity})
        if not created and (row.mensaje != message or row.actividad != activity):
            return Response({"detalle": "Ya registraste un interés en esta modalidad. Consulta Mis ofrecimientos antes de crear otro."}, status=409)
        if created:
            auditar(request.user, "ayudas.participar", "ayudas", row.pk, foundation.pk, motivo="Interés de ayuda registrado")
            from seguridad.models import ResponsableEntidad
            manager = ResponsableEntidad.objects.filter(entidad_id=foundation.pk).select_related("principal").first()
            kind = ValorMaestro.objects.filter(tipo__nombre="tipo_notificacion", nombre="Interés de ayuda").first()
            if manager and kind:
                Notificacion.objects.create(usuario_id=manager.principal.usuario_id, tipo_notificacion=kind,
                    contenido=f"Nuevo interés de {mode} para {foundation.entidad.nombre}. Consulta los ofrecimientos de tu organización.")
        return Response({"id": row.pk, "ya_registrado": not created, "aceptado": False}, status=201 if created else 200)


def perfil_ayuda(foundation):
    import hashlib, json
    data = {"id": foundation.pk, "nombre": foundation.entidad.nombre, "acepta_voluntarios": foundation.acepta_voluntarios, "necesidades_ayuda": foundation.necesidades_ayuda}
    data["version"] = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    return data


class MisOrganizacionesAyudaView(SinCacheView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rows = Fundacion.objects.select_related("entidad").order_by("pk")[:100]
        return Response([perfil_ayuda(row) for row in rows if puede(request.user, "ayudas.gestionar", entidad_id=row.pk)])


class OrganizacionAyudaView(SinCacheView):
    permission_classes = [IsAuthenticated]

    def get(self, request, fundacion_id):
        exigir(request.user, "ayudas.gestionar", entidad_id=fundacion_id)
        foundation = get_object_or_404(Fundacion.objects.select_related("entidad"), pk=fundacion_id)
        data = perfil_ayuda(foundation)
        offers = InteresAyuda.objects.filter(fundacion=foundation).select_related("usuario").order_by("-pk")[:50]
        data["ofrecimientos"] = [{"id": row.pk, "nombre": row.usuario.nombre, "modalidad": row.modalidad, "mensaje": row.mensaje, "actividad": row.actividad, "fecha": row.fecha} for row in offers]
        return Response(data)

    @transaction.atomic
    def patch(self, request, fundacion_id):
        exigir(request.user, "ayudas.gestionar", entidad_id=fundacion_id)
        foundation = get_object_or_404(Fundacion.objects.select_for_update().select_related("entidad"), pk=fundacion_id)
        old = perfil_ayuda(foundation)
        if request.data.get("version") != old["version"]:
            return Response({"detalle": "La convocatoria cambió. Actualiza antes de guardar."}, status=409)
        foundation.acepta_voluntarios = serializers.BooleanField().run_validation(request.data.get("acepta_voluntarios"))
        foundation.necesidades_ayuda = serializers.CharField(max_length=1000, allow_blank=True).run_validation(request.data.get("necesidades_ayuda"))
        foundation.save(update_fields=["acepta_voluntarios", "necesidades_ayuda"])
        new = perfil_ayuda(foundation)
        auditar(request.user, "ayudas.gestionar", "ayudas", foundation.pk, foundation.pk, motivo="Convocatoria de ayuda actualizada", anterior=old, nuevo=new)
        return Response(new)
