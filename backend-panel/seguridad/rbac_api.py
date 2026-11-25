from django.utils import timezone
from rest_framework import serializers
from rest_framework.response import Response
from .views import VistaSegura
from .autorizacion import exigir
from .models import ExcepcionPermiso
from .serializers import EntradaEstricta


class EntradaExcepcion(EntradaEstricta,serializers.Serializer):
    permiso_id=serializers.IntegerField(min_value=1)
    efecto=serializers.ChoiceField(choices=['HEREDAR','PERMITIR','DENEGAR'])
    motivo=serializers.CharField(max_length=500)
    entidad_id=serializers.IntegerField(min_value=1,allow_null=True,required=False,default=None)
    expira=serializers.DateTimeField(allow_null=True,required=False,default=None)


class ExcepcionesPermisoView(VistaSegura):
    def get(self,request,usuario_id):
        if usuario_id!=request.user.pk:
            exigir(request.user,'roles.asignar')
        return Response(list(ExcepcionPermiso.objects.filter(usuario_id=usuario_id).values('id','permiso_id','permiso__codigo','efecto','entidad_id','expira','motivo','autor_id','actualizada')))

    def post(self,request,usuario_id):
        s=EntradaExcepcion(data=request.data);s.is_valid(raise_exception=True)
        from .excepciones import guardar
        guardar(request.user,usuario_id,**s.validated_data)
        return Response({'guardado':True})
