"""Recipient-specific encrypted bank instructions. This endpoint never moves money."""
import json
from cryptography.fernet import InvalidToken
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from core.crypto import cifrar, descifrar
from seguridad.autorizacion import exigir
from seguridad.servicios import auditar
from .models import FondoExterno

class BancoEntrada(serializers.Serializer):
    titular=serializers.CharField(max_length=150)
    banco=serializers.CharField(max_length=120)
    tipo_cuenta=serializers.CharField(max_length=60)
    numero_cuenta=serializers.RegexField(r'^[0-9 -]{4,40}$')
    identificacion_titular=serializers.CharField(max_length=50)
    confirmar=serializers.BooleanField()

class DatosAporteView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,fondo_id):
        exigir(request.user,'fondo.participar')
        fund=get_object_or_404(FondoExterno.objects.select_related('entidad'),pk=fondo_id,estado_fondo__nombre='Activo')
        if not fund.entidad_id or fund.entidad.estado_verificacion.nombre!='Verificada':raise ValidationError('La organización no tiene verificación vigente.')
        exigir(request.user,'fondo.participar',entidad_id=fund.entidad_id,objeto_id=fund.pk)
        if not fund.datos_transferencia_cifrados:raise ValidationError('Esta organización todavía no publicó instrucciones bancarias.')
        try:
            values=json.loads(descifrar(fund.datos_transferencia_cifrados))
            s=BancoEntrada(data={**values,'confirmar':True});s.is_valid(raise_exception=True)
        except (ImproperlyConfigured,ValueError,TypeError,InvalidToken):return Response({'detalle':'Las instrucciones bancarias no están disponibles.'},status=503)
        result={key:value for key,value in s.validated_data.items() if key!='confirmar'}
        result.update(organizacion=fund.entidad.nombre,organizacion_id=fund.entidad_id,prueba=False,nota='Transferencia externa. Little Paws Net no procesa ni confirma el pago.')
        auditar(request.user,'fondo.cuenta_consultar','fondos',fund.pk,fund.entidad_id)
        response=Response(result);response['Cache-Control']='no-store';return response
    @transaction.atomic
    def patch(self,request,fondo_id):
        fund=get_object_or_404(FondoExterno.objects.select_for_update().select_related('entidad'),pk=fondo_id)
        if not fund.entidad_id or fund.entidad.estado_verificacion.nombre!='Verificada':raise ValidationError('La organización no tiene verificación vigente.')
        exigir(request.user,'fondo.reportar_distribucion',entidad_id=fund.entidad_id,objeto_id=fund.pk)
        serializer=BancoEntrada(data=request.data);serializer.is_valid(raise_exception=True)
        values=dict(serializer.validated_data)
        if not values.pop('confirmar'):raise ValidationError('Confirma que la organización autoriza estas instrucciones.')
        try: fund.datos_transferencia_cifrados=cifrar(json.dumps(values,ensure_ascii=False))
        except ImproperlyConfigured:return Response({'detalle':'El cifrado debe configurarse antes de guardar cuentas.'},status=503)
        fund.save(update_fields=['datos_transferencia_cifrados'])
        auditar(request.user,'fondo.reportar_distribucion','fondos',fund.pk,fund.entidad_id,operacion='actualizar-instrucciones-bancarias')
        response=Response({'guardado':True});response['Cache-Control']='no-store';return response
