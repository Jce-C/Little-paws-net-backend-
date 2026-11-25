from django.db import transaction
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .views import VistaSegura
from .autorizacion import exigir
from .serializers import EntradaEstricta
from .servicios import auditar
from core.models import EntidadVerificable,Fundacion,Tienda,Clinica,Ciudad,ValorMaestro,CapacidadFundacion


class OrganizacionEntrada(EntradaEstricta,serializers.Serializer):
    nombre=serializers.CharField(max_length=150)
    tipo=serializers.ChoiceField(choices=['fundacion','tienda','clinica','veterinario'])
    ciudad_id=serializers.PrimaryKeyRelatedField(queryset=Ciudad.objects.filter(activo=True))
    nit=serializers.CharField(max_length=30,required=False,allow_blank=True)
    direccion=serializers.CharField(max_length=255,required=False,allow_blank=True)
    whatsapp=serializers.CharField(max_length=20,required=False,allow_blank=True)
    descripcion=serializers.CharField(max_length=5000,required=False,allow_blank=True)
    cupos_totales=serializers.IntegerField(min_value=0,max_value=65535,required=False,default=0)
    registro_profesional=serializers.CharField(max_length=80,required=False,allow_blank=True)
    usuario_profesional_id=serializers.IntegerField(min_value=1,required=False)
    clinica_id=serializers.PrimaryKeyRelatedField(queryset=Clinica.objects.all(),required=False,allow_null=True)
    especialidad=serializers.CharField(max_length=120,required=False,allow_blank=True)


class OrganizacionesView(VistaSegura):
    def get(self,request):
        exigir(request.user,'entidades.ver')
        return Response(list(EntidadVerificable.objects.values('pk','nombre','estado_verificacion__nombre').order_by('nombre')[:100]))

    @transaction.atomic
    def post(self,request):
        exigir(request.user,'entidades.crear')
        s=OrganizacionEntrada(data=request.data);s.is_valid(raise_exception=True);d=s.validated_data
        if d['tipo']=='fundacion' and not d.get('nit'):
            raise ValidationError('La fundación requiere NIT.')
        if d['tipo']=='veterinario' and (not d.get('registro_profesional') or not d.get('usuario_profesional_id')):
            raise ValidationError('El profesional requiere cuenta individual y registro profesional.')
        e=EntidadVerificable.objects.create(nombre=d['nombre'],estado_verificacion=ValorMaestro.objects.get(tipo__nombre='estado_verificacion',nombre='Pendiente'))
        if d['tipo']=='fundacion':
            f=Fundacion(entidad=e,ciudad=d['ciudad_id'],nit=d['nit'],descripcion=d.get('descripcion',''));f.save()
            CapacidadFundacion.objects.create(fundacion=f,cupos_totales=d['cupos_totales'],usuario_actualizador=request.user)
        elif d['tipo']=='tienda':
            Tienda.objects.create(entidad=e,ciudad=d['ciudad_id'],direccion=d.get('direccion',''),whatsapp=d.get('whatsapp',''))
        elif d['tipo']=='clinica':
            Clinica.objects.create(entidad=e,ciudad=d['ciudad_id'],direccion=d.get('direccion',''))
        else:
            from core.models import Veterinario
            from accounts.models import Usuario
            if not Usuario.objects.filter(pk=d['usuario_profesional_id'],is_active=True).exists():raise ValidationError('Cuenta profesional no disponible.')
            Veterinario.objects.create(entidad=e,usuario_profesional_id=d['usuario_profesional_id'],registro_profesional=d['registro_profesional'],clinica=d.get('clinica_id'),especialidad=d.get('especialidad',''))
        auditar(request.user,'entidad.crear','entidades',e.pk,e.pk,nuevo={'nombre':e.nombre,'tipo':d['tipo'],'estado':'Pendiente'})
        return Response({'id':e.pk,'estado':'Pendiente'},status=201)


class EditarOrganizacionEntrada(EntradaEstricta,serializers.Serializer):
    nombre=serializers.CharField(max_length=150,required=False)
    descripcion=serializers.CharField(max_length=5000,required=False,allow_blank=True)
    direccion=serializers.CharField(max_length=255,required=False,allow_blank=True)
    whatsapp=serializers.CharField(max_length=20,required=False,allow_blank=True)
    cupos_totales=serializers.IntegerField(min_value=0,max_value=65535,required=False)


class OrganizacionDetalleView(VistaSegura):
    @transaction.atomic
    def patch(self,request,pk):
        exigir(request.user,'entidades.editar')
        e=EntidadVerificable.objects.select_for_update().get(pk=pk)
        from .models import BajaAdministrativa
        if BajaAdministrativa.objects.filter(tipo='entidades',objeto_id=pk,activo=False).exists():raise ValidationError('Restaura la entidad antes de modificarla.')
        s=EditarOrganizacionEntrada(data=request.data);s.is_valid(raise_exception=True);d=s.validated_data
        anterior={'nombre':e.nombre}
        if 'nombre' in d:e.nombre=d['nombre'];e.save(update_fields=['nombre'])
        if 'cupos_totales' in d:
            capacidad=CapacidadFundacion.objects.select_for_update().get(fundacion_id=pk)
            if d['cupos_totales']<capacidad.cupos_ocupados:raise ValidationError('No puede haber menos cupos que los ocupados.')
            anterior['cupos_totales']=capacidad.cupos_totales;capacidad.cupos_totales=d['cupos_totales'];capacidad.usuario_actualizador=request.user;capacidad.save()
        for model,campos in ((Fundacion,['descripcion']),(Tienda,['direccion','whatsapp']),(Clinica,['direccion'])):
            obj=model.objects.filter(pk=pk).first()
            if obj:
                for c in campos:
                    if c in d:anterior[c]=getattr(obj,c);setattr(obj,c,d[c])
                obj.save()
        auditar(request.user,'entidad.editar','entidades',pk,pk,anterior=anterior,nuevo=d)
        return Response({'guardado':True})


class SeguimientoEntrada(EntradaEstricta,serializers.Serializer):
    detalle=serializers.CharField(max_length=12000)


class SeguimientoView(VistaSegura):
    def get(self,request,pk):
        from .flujos import exigir_lectura
        exigir_lectura(request.user,'adopcion',pk)
        from .models import SeguimientoAdopcion
        return Response(list(SeguimientoAdopcion.objects.filter(solicitud_id=pk).values('id','detalle','fecha','actor__nombre')))

    @transaction.atomic
    def post(self,request,pk):
        from adoption.models import SolicitudAdopcion
        from .models import SeguimientoAdopcion
        exigir(request.user,'adopcion.seguimiento',objeto_id=pk)
        solicitud=SolicitudAdopcion.objects.select_for_update().get(pk=pk)
        if solicitud.estado_adopcion.nombre!='Aprobada':raise ValidationError('El seguimiento requiere una adopción aprobada.')
        s=SeguimientoEntrada(data=request.data);s.is_valid(raise_exception=True)
        obj=SeguimientoAdopcion.objects.create(solicitud=solicitud,actor=request.user,detalle=s.validated_data['detalle'])
        auditar(request.user,'adopcion.seguimiento','adopcion',pk,motivo='Seguimiento posterior a adopción',seguimiento_id=obj.pk)
        return Response({'id':obj.pk},status=201)


class FondoEntrada(EntradaEstricta,serializers.Serializer):
    nombre=serializers.CharField(max_length=150)
    entidad_administradora=serializers.CharField(max_length=150)
    entidad_id=serializers.PrimaryKeyRelatedField(queryset=EntidadVerificable.objects.all())
    tipo_fondo_id=serializers.PrimaryKeyRelatedField(queryset=ValorMaestro.objects.filter(tipo__nombre='tipo_fondo'))


class FondosAdministrarView(VistaSegura):
    @transaction.atomic
    def post(self,request):
        from funds.models import FondoExterno
        exigir(request.user,'fondo.crear')
        s=FondoEntrada(data=request.data);s.is_valid(raise_exception=True);d=s.validated_data
        obj=FondoExterno.objects.create(nombre=d['nombre'],entidad_administradora=d['entidad_administradora'],entidad=d['entidad_id'],tipo_fondo=d['tipo_fondo_id'],estado_fondo=ValorMaestro.objects.get(tipo__nombre='estado_fondo',nombre='Activo'))
        auditar(request.user,'fondo.crear','fondo',obj.pk,obj.entidad_id,nuevo={'nombre':obj.nombre})
        return Response({'id':obj.pk,'transferencia_ejecutada':False},status=201)

    @transaction.atomic
    def patch(self,request,pk):
        from funds.models import FondoExterno
        exigir(request.user,'fondo.editar')
        s=FondoEntrada(data=request.data,partial=True);s.is_valid(raise_exception=True)
        obj=FondoExterno.objects.select_for_update().get(pk=pk)
        anteriores={'nombre':obj.nombre,'entidad_administradora':obj.entidad_administradora}
        for k,v in s.validated_data.items():
            setattr(obj,{'entidad_id':'entidad','tipo_fondo_id':'tipo_fondo'}.get(k,k),v)
        obj.save()
        auditar(request.user,'fondo.editar','fondo',pk,obj.entidad_id,anterior=anteriores,nuevo={'nombre':obj.nombre,'entidad_administradora':obj.entidad_administradora})
        return Response({'guardado':True})


class DocumentoEntrada(EntradaEstricta,serializers.Serializer):
    archivo=serializers.FileField()


class MascotaEditarEntrada(EntradaEstricta,serializers.Serializer):
    nombre=serializers.CharField(max_length=120,required=False)
    fecha_nacimiento=serializers.DateField(required=False,allow_null=True)
    especie_id=serializers.IntegerField(min_value=1,required=False,allow_null=True)
    raza_id=serializers.IntegerField(min_value=1,required=False,allow_null=True)
    descripcion_especie=serializers.CharField(max_length=150,required=False,allow_blank=True)


class MascotaAdministrarView(VistaSegura):
    @transaction.atomic
    def post(self,request):
        exigir(request.user,'mascotas.crear')
        # El alta administrativa declara una ficha propia; no inventa una transferencia.
        from .flujos_views import MascotaCrearView
        return MascotaCrearView.post(self,request)

    @transaction.atomic
    def patch(self,request,pk):
        from animals.models import Mascota,Raza
        exigir(request.user,'mascotas.editar')
        s=MascotaEditarEntrada(data=request.data);s.is_valid(raise_exception=True);d=s.validated_data
        from django.utils import timezone
        if d.get('fecha_nacimiento') and d['fecha_nacimiento']>timezone.localdate():raise ValidationError('La fecha debe estar en el pasado.')
        obj=Mascota.objects.select_for_update().get(pk=pk)
        from animals.identificacion import identificar
        d=identificar(d,obj)
        anteriores={k:getattr(obj,k) for k in d}
        for k,v in d.items():setattr(obj,k,v)
        obj.save()
        auditar(request.user,'mascota.editar','mascotas',pk,anterior={k:str(v) for k,v in anteriores.items()},nuevo={k:str(v) for k,v in d.items()})
        return Response({'guardado':True})


class CoberturaEntrada(EntradaEstricta,serializers.Serializer):
    ciudad_id=serializers.PrimaryKeyRelatedField(queryset=Ciudad.objects.filter(activo=True))
    activo=serializers.BooleanField(default=True)

class CoberturaView(VistaSegura):
    def get(self,request,pk):
        exigir(request.user,'caso.cobertura',entidad_id=pk)
        from geography.models import CoberturaCiudadFundacion
        return Response(list(CoberturaCiudadFundacion.objects.filter(fundacion_id=pk,activo=True).values('ciudad_id','ciudad__nombre')))
    @transaction.atomic
    def post(self,request,pk):
        exigir(request.user,'caso.cobertura',entidad_id=pk)
        from geography.models import CoberturaCiudadFundacion
        from .servicios import bloqueo_seguridad
        bloqueo_seguridad();exigir(request.user,'caso.cobertura',entidad_id=pk)
        if not Fundacion.objects.filter(pk=pk).exists():raise ValidationError('La cobertura corresponde a una fundación.')
        s=CoberturaEntrada(data=request.data);s.is_valid(raise_exception=True);d=s.validated_data
        obj= CoberturaCiudadFundacion.objects.filter(fundacion_id=pk,ciudad=d['ciudad_id']).first();antes=obj.activo if obj else False
        obj,_=CoberturaCiudadFundacion.objects.update_or_create(fundacion_id=pk,ciudad=d['ciudad_id'],defaults={'activo':d['activo']})
        auditar(request.user,'caso.cobertura','caso',obj.pk,pk,anterior=antes,nuevo={'ciudad_id':obj.ciudad_id,'activo':obj.activo})
        return Response({'guardado':True})


class MascotaRescateView(VistaSegura):
    @transaction.atomic
    def post(self,request,pk):
        from rescue.models import CasoRescate,Reporte
        from animals.models import Mascota,CustodiaMascota
        from django.utils import timezone
        from .servicios import bloqueo_seguridad
        from .flujos_serializers import MascotaEntrada
        bloqueo_seguridad()
        from django.shortcuts import get_object_or_404
        caso=get_object_or_404(CasoRescate.objects.select_for_update().select_related('fundacion__entidad','estado_caso'),pk=pk)
        exigir(request.user,'caso.registrar_mascota',entidad_id=caso.fundacion_id)
        if caso.fundacion.entidad.estado_verificacion.nombre!='Verificada':raise ValidationError('La fundación debe estar verificada.')
        if caso.fecha_cierre or caso.estado_caso.nombre in ('Cerrado','Cancelado'):raise ValidationError('El caso está cerrado.')
        reporte=Reporte.objects.select_for_update().get(pk=caso.reporte_id)
        if reporte.mascota_id:raise ValidationError('El reporte ya tiene una mascota. No se cambia su titularidad desde este formulario.')
        s=MascotaEntrada(data=request.data);s.is_valid(raise_exception=True)
        if s.validated_data.get('fecha_nacimiento') and s.validated_data['fecha_nacimiento']>timezone.localdate():raise ValidationError('La fecha de nacimiento no puede estar en el futuro')
        pet=Mascota.objects.create(**s.validated_data,estado_mascota=ValorMaestro.objects.get(tipo__nombre='estado_mascota',nombre='En rescate'))
        CustodiaMascota.objects.create(mascota=pet,fundacion=caso.fundacion,caso=caso,fecha_inicio=timezone.now(),usuario_registrador=request.user)
        reporte.mascota=pet;reporte.save(update_fields=['mascota','fecha_actualizacion'])
        auditar(request.user,'caso.registrar_mascota','mascotas',pet.pk,caso.fundacion_id,nuevo={'caso_id':caso.pk,'reporte_id':reporte.pk,'estado':'En rescate'})
        return Response({'id':pet.pk},status=201)

class PublicarAdopcionEntrada(EntradaEstricta,serializers.Serializer):
    confirmar=serializers.BooleanField()
    disponible=serializers.BooleanField(default=True)

class PublicarAdopcionView(VistaSegura):
    @transaction.atomic
    def post(self,request,pk):
        from animals.models import Mascota,CustodiaMascota
        from django.utils import timezone
        from .servicios import bloqueo_seguridad
        from django.shortcuts import get_object_or_404
        bloqueo_seguridad();pet=get_object_or_404(Mascota.objects.select_for_update(),pk=pk)
        custodias=list(CustodiaMascota.objects.select_for_update().filter(mascota=pet,fecha_fin__isnull=True).select_related('fundacion__entidad'))
        if pet.dueno_id or len(custodias)!=1:raise ValidationError('Se requiere una custodia única vigente y una mascota sin titular particular.')
        custodia=custodias[0];exigir(request.user,'mascotas.publicar_adopcion',entidad_id=custodia.fundacion_id)
        if custodia.fundacion.entidad.estado_verificacion.nombre!='Verificada':raise ValidationError('La fundación debe estar verificada.')
        s=PublicarAdopcionEntrada(data=request.data);s.is_valid(raise_exception=True)
        if not s.validated_data['confirmar']:raise ValidationError('Confirma que la ficha está revisada para actualizar su disponibilidad.')
        if pet.estado_mascota.nombre=='Adoptada':raise ValidationError('La mascota ya está adoptada.')
        antes=pet.estado_mascota.nombre
        pet.estado_mascota=ValorMaestro.objects.get(tipo__nombre='estado_mascota',nombre='En adopción' if s.validated_data['disponible'] else 'En recuperación');pet.save(update_fields=['estado_mascota'])
        auditar(request.user,'mascotas.publicar_adopcion','mascotas',pet.pk,custodia.fundacion_id,anterior=antes,nuevo=pet.estado_mascota.nombre)
        return Response({'guardado':True})
