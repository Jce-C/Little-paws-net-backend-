from rest_framework import serializers
from rest_framework.response import Response
from .views import VistaSegura
from .serializers import EntradaEstricta
from .administracion_segura import preparar_confirmacion,ejecutar_baja

class ConfirmacionEntrada(EntradaEstricta,serializers.Serializer):
    accion=serializers.ChoiceField(choices=['desactivar','eliminar','restaurar','fisica'])
    motivo=serializers.CharField(max_length=500,allow_blank=True,required=False,default="")
    confirmacion=serializers.CharField(max_length=2000)
    nombre=serializers.CharField(max_length=254,required=False,allow_blank=True,default="")
    acepto=serializers.BooleanField()

class BajaView(VistaSegura):
    def get(self,request,tipo,pk):
        d=preparar_confirmacion(request.user,tipo,pk);obj=d.pop('objeto');d['nombre']=obj.nombre;d['id']=obj.pk
        return Response(d)
    def post(self,request,tipo,pk):
        s=ConfirmacionEntrada(data=request.data);s.is_valid(raise_exception=True)
        return Response(ejecutar_baja(request.user,tipo,pk,**s.validated_data))
