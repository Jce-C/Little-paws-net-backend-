from rest_framework import serializers
from rest_framework.response import Response
from .views import VistaSegura
from .serializers import EntradaEstricta
from .asignaciones import guardar_roles,firma_persona
from .autorizacion import exigir,motor
from .administracion_segura import administrador_total
from django.shortcuts import get_object_or_404
from core.models import EntidadVerificable,UsuarioRol,EntidadMiembroRol
from accounts.models import Usuario

class RolesPersonaEntrada(EntradaEstricta,serializers.Serializer):
    roles=serializers.ListField(child=serializers.IntegerField(min_value=1),max_length=1000,allow_empty=True)
    entidad=serializers.IntegerField(min_value=1,required=False,allow_null=True)
    version=serializers.CharField(max_length=64)
    motivo=serializers.CharField(max_length=500)
    incorporar=serializers.BooleanField(default=False)
    activar_inactivos=serializers.BooleanField(default=False)

class RolesPersonaView(VistaSegura):
    def get(self,request,usuario_id):
        exigir(request.user,'roles.asignar');usuario=get_object_or_404(Usuario,pk=usuario_id)
        raw=request.query_params.get('entidad');entidad=serializers.IntegerField(min_value=1).run_validation(raw) if raw else None
        if entidad:
            ma=motor(request.user);get_object_or_404(EntidadVerificable.objects.exclude(pk__in=ma.bajas_entidad),pk=entidad)
            if not administrador_total(request.user) and not(ma.base('miembros.roles',entidad) or ma.base('miembros.gestionar',entidad)):exigir(request.user,'miembros.roles',entidad_id=entidad)
        roles=list(EntidadMiembroRol.objects.filter(miembro__usuario=usuario,miembro__entidad_id=entidad,miembro__fecha_salida__isnull=True,fecha_revocacion__isnull=True).values_list('rol_id',flat=True)) if entidad else list(UsuarioRol.objects.filter(usuario=usuario,fecha_revocacion__isnull=True).values_list('rol_id',flat=True))
        return Response({'usuario':usuario.pk,'entidad':entidad,'roles':roles,'version':firma_persona(usuario,entidad,'usuarios')})
    def put(self,request,usuario_id):
        s=RolesPersonaEntrada(data=request.data);s.is_valid(raise_exception=True)
        return Response(guardar_roles(request.user,usuario_id,**s.validated_data))
    def patch(self,request,usuario_id):return self.put(request,usuario_id)
