"""Citizen-owned pets are private records, never adoption listings."""
import base64, calendar
from datetime import date
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.response import Response
from seguridad.flujos_views import Privada
from seguridad.autorizacion import exigir
from seguridad.servicios import auditar
from core.models import ValorMaestro
from core.public_images import normalizar
from .models import Mascota, PerfilMascotaPersonal, Especie, Raza

class PersonalEntrada(serializers.Serializer):
    def to_internal_value(self, data):
        if hasattr(data, 'keys') and (set(data.keys()) - set(self.fields)):
            raise serializers.ValidationError({'non_field_errors': ['Hay campos no permitidos en el registro.']})
        return super().to_internal_value(data)

    nombre = serializers.CharField(max_length=120)
    especie = serializers.CharField(max_length=100)
    raza = serializers.CharField(max_length=120, required=False, allow_blank=True)
    edad_meses = serializers.IntegerField(min_value=0, max_value=600, required=False)
    sexo = serializers.CharField(max_length=60, required=False, allow_blank=True)
    tamano = serializers.CharField(max_length=60, required=False, allow_blank=True)
    color = serializers.CharField(max_length=100, required=False, allow_blank=True)
    descripcion = serializers.CharField(max_length=2000, required=False, allow_blank=True)
    archivo = serializers.ImageField(required=False, write_only=True)

def personal_descriptor(pet, include_photo=True):
    profile = getattr(pet, 'perfil_personal', None)
    return None if profile is None else {'raza':profile.raza_texto, 'sexo':profile.sexo_texto, 'tamano':profile.tamano_texto, 'color':profile.color, 'descripcion':profile.descripcion,
      'foto_miniatura': None if not include_photo or not profile.foto else {'tipo':'image/webp','ancho':profile.ancho,'alto':profile.alto,'datos':base64.b64encode(bytes(profile.foto)).decode('ascii')}}

class MascotaPersonalCrearView(Privada):
    def post(self, request):
        import hashlib
        from core.operation_receipts import crear_una_vez
        exigir(request.user, 'mascotas.participar')
        serializer = PersonalEntrada(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        photo = normalizar(data['archivo'], max_side=160, max_output=16*1024) if data.get('archivo') else (b'', 0, 0)
        payload = {key:value for key,value in data.items() if key != 'archivo'}
        payload['foto_sha256'] = hashlib.sha256(photo[0]).hexdigest()
        return crear_una_vez(request, 'mascota-personal', payload, lambda:self._create(request, data, photo))

    def _create(self, request, data, photo):
        species=Especie.objects.filter(nombre__iexact=data['especie'],activo=True).first()
        breed=Raza.objects.filter(nombre__iexact=data.get('raza',''), especie=species, activo=True).first() if species else None
        today=timezone.localdate(); months=data.get('edad_meses'); born=None
        if months is not None:
            year,month=divmod(today.year*12+today.month-1-months,12);month+=1
            born=date(year,month,min(today.day,calendar.monthrange(year,month)[1]))
        state=get_object_or_404(ValorMaestro,tipo__nombre='estado_mascota',nombre='Con dueño')
        pet=Mascota.objects.create(dueno=request.user,nombre=data['nombre'],especie=species,descripcion_especie=data['especie'] if not species else '',raza=breed,estado_mascota=state,fecha_nacimiento=born,es_estimada=born is not None)
        PerfilMascotaPersonal.objects.create(mascota=pet,raza_texto=data.get('raza',''),sexo_texto=data.get('sexo',''),tamano_texto=data.get('tamano',''),color=data.get('color',''),descripcion=data.get('descripcion',''),foto=photo[0],ancho=photo[1],alto=photo[2])
        auditar(request.user,'mascotas.participar','mascotas',pet.pk,operacion='registrar-mascota-personal',nuevo={'nombre':pet.nombre,'origen':'personal'})
        response=Response({'id_mascota':pet.pk,'nombre':pet.nombre},status=201);response['Cache-Control']='no-store';return response

class MascotaPersonalDetalleView(Privada):
    def get(self,request,mascota_id):
        exigir(request.user,'mascotas.participar')
        pet=get_object_or_404(Mascota.objects.select_related('perfil_personal', 'especie'),pk=mascota_id,dueno=request.user)
        values=personal_descriptor(pet)
        if values is None:raise serializers.ValidationError('Esta mascota no fue registrada como mascota personal.')
        values.update(id_mascota=pet.pk,nombre=pet.nombre,especie=pet.especie_nombre,fecha_nacimiento=pet.fecha_nacimiento)
        response=Response(values);response['Cache-Control']='no-store';return response
