"""Pantallas y formularios reales sobre los contratos existentes del negocio."""
from django import forms
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render,redirect
from django.contrib import messages
from django.urls import resolve,reverse
from django.utils.module_loading import import_string
from django.views.decorators.http import require_http_methods
from django.http import Http404
from rest_framework import serializers as drf
from rest_framework.exceptions import APIException,ValidationError,PermissionDenied
from rest_framework.test import APIRequestFactory,force_authenticate
from core.models import EntidadVerificable,ValorMaestro,Ciudad,Fundacion,UsuarioRol
from animals.models import Mascota,Raza,Especie
from seguridad.autorizacion import motor,puede,es_superusuario
from seguridad.servicios import auditar
from seguridad.consultas_negocio import mascotas_visibles
from seguridad import flujos
from .views import protegido
from .procesos import OPERACIONES
from seguridad.i18n import traducir_formulario,texto_error
from django.utils.translation import gettext as _t

AREAS={'organizaciones':'Organizaciones y equipos','mascotas':'Mascotas','reportes':'Reportes de rescate',
 'rescates':'Casos de rescate','adopciones':'Adopciones y seguimiento','aportes':'Aportes',
 'fondos':'Fondos externos','catalogo':'Catálogo y existencias','pedidos':'Pedidos',
 'expedientes':'Atención veterinaria','publicidad':'Anuncios','revision-publicidad':'Revisión de anuncios',
 'verificaciones':'Verificaciones','reclamaciones':'Reclamaciones de titularidad'}
PRIVADOS={'adopciones':'adopcion','aportes':'aporte','pedidos':'pedido','verificaciones':'verificacion','expedientes':'expediente','reclamaciones':'reclamacion'}
ETIQUETAS={'pk':'Identificador','id':'Identificador','id_mascota':'Mascota','mascota_id':'Mascota','raza_id':'Raza','barrio':'Barrio o sector','direccion':'Dirección exacta','indicaciones':'Indicaciones adicionales (opcional)','confirmar':'Confirmo que la ficha ha sido revisada','disponible':'Disponible para adopción',
 'id_fundacion':'Fundación','entidad_id':'Organización','ciudad_id':'Ciudad','id_fondo_externo':'Fondo externo','id_reporte':'Reporte',
 'usuario_id':'Persona','miembro_id':'Integrante','sucesor_id':'Nuevo responsable','id_veterinario':'Veterinario',
 'id_tienda':'Tienda','tipo_fondo_id':'Tipo de fondo','categoria_id':'Categoría','tipo_id':'Tipo de producto',
 'mantener_secundario':'Mantener al responsable anterior como secundario','dueno_actual_id':'Dueño actual revisado','nuevo_dueno_id':'Nuevo dueño',
 'registro':'Registro sobre el que se realizará la acción','aprobar':'Decisión','detalle':'Descripción de la atención o seguimiento',
 'token':'Código QR de acceso','numero':'Número de cuenta receptora','revocar':'Retirar esta asignación','recuperar':'Recuperación administrativa de responsabilidad'}


def filas(request,area):
    if not hasattr(request,'_filas_negocio'):request._filas_negocio={}
    if area not in request._filas_negocio:request._filas_negocio[area]=_filas(request,area)
    return request._filas_negocio[area]


def _filas(request,area):
    from adoption.models import SolicitudAdopcion
    from rescue.models import Reporte,CasoRescate,Apadrinamiento
    from funds.models import FondoExterno
    from commerce.models import Producto,PedidoIniciado
    from core.models import SolicitudValidacion
    from seguridad.models import Anuncio,VersionAnuncio,ReclamacionMascota
    m=motor(request.user);entidad=request.panel['entidad_id'];super_=bool(m.usuario.is_superuser)
    datos=[]
    if area=='organizaciones':
        qs=EntidadVerificable.objects.all() if m.base('entidades.ver') else EntidadVerificable.objects.filter(pk__in=m.miembros)
        fundaciones=set(Fundacion.objects.values_list('pk',flat=True))
        return [{'id':e.pk,'nombre':e.nombre,'puede_perfil_publico':m.base('entidades.editar'),'puede_programa_ayuda':m.base('ayudas.gestionar',e.pk) and e.pk in fundaciones,'estado':'Desactivado' if e.pk in m.bajas_entidad else e.estado_verificacion.nombre,'detalle':m.base('entidades.ver') or m.base('miembros.ver',e.pk)} for e in qs.select_related('estado_verificacion')[:100]]
    if area=='mascotas':
        from seguridad.consultas_negocio import mascotas_visibles
        qs=mascotas_visibles(request.user,entidad)
        vista=request.GET.get('vista','adopcion')
        from adoption.consultas import disponibles_adopcion
        if vista=='propias':qs=qs.filter(dueno=request.user)
        elif vista!='gestion':qs=qs.filter(pk__in=disponibles_adopcion().values('pk'))
        registros=[]
        for p in qs.select_related('estado_mascota').prefetch_related('custodiamascota_set')[:100]:
            custodias=[c for c in p.custodiamascota_set.all() if c.fecha_fin is None]
            conflicto=len(custodias)>1 or bool(custodias and p.dueno_id)
            autorizar=not conflicto and (super_ or (not custodias and p.dueno_id==request.user.pk) or (len(custodias)==1 and m.base('expediente.autorizar',custodias[0].fundacion_id)))
            registros.append({'id':p.pk,'nombre':p.nombre,'estado':p.estado_mascota.nombre,'detalle':True,'autorizar':autorizar,'gestion_adopcion':not conflicto and not p.dueno_id and len(custodias)==1 and m.base('mascotas.publicar_adopcion',custodias[0].fundacion_id)})
        return registros
    if area=='reportes':
        qs=Reporte.objects.all() if super_ or m.base('reportes.ver') or m.base('reporte.moderar') else Reporte.objects.filter(Q(usuario_reportante=request.user)|Q(casorescate__fundacion_id=entidad))
        return [{'id':r.pk,'nombre':r.tipo_reporte.nombre+' · '+r.descripcion[:100],'estado':r.estado_reporte.nombre,'detalle':True} for r in qs.select_related('estado_reporte','tipo_reporte')[:100]]
    if area=='rescates':
        qs=CasoRescate.objects.all() if super_ else CasoRescate.objects.filter(fundacion_id=entidad)
        if not m.base('caso.ver',entidad):return []
        return [{'id':c.pk,'nombre':f'Rescate #{c.pk}','estado':c.estado_caso.nombre,'detalle':False,'mascota_registrada':bool(c.reporte.mascota_id)} for c in qs.select_related('estado_caso','reporte')[:100]]
    if area=='fondos':
        qs=FondoExterno.objects.filter(estado_fondo__nombre='Activo')
        return [{'id':f.pk,'nombre':f.nombre,'estado':'Activo · registro informativo','detalle':False} for f in qs[:100]]
    if area=='catalogo':
        from commerce.consultas import productos_vigentes
        qs=productos_vigentes()
        qs=qs if super_ else qs.filter(tienda_id=entidad) if m.base('producto.gestionar',entidad) else qs.filter(estado_producto__nombre='Disponible',tienda__entidad__estado_verificacion__nombre='Verificada')
        return [{'id':p.pk,'nombre':p.nombre,'estado':f'{p.existencias} unidades · {p.precio}','detalle':False,'puede_foto_producto':m.base('producto.gestionar',p.tienda_id),'puede_eliminar_producto':m.base('producto.eliminar',p.tienda_id)} for p in qs[:100]]
    if area in ('publicidad','revision-publicidad'):
        qs=VersionAnuncio.objects.all() if m.base('publicidad.revisar') else VersionAnuncio.objects.filter(anuncio__entidad_id=entidad)
        if not m.base('publicidad.revisar') and not m.base('publicidad.gestionar',entidad):return []
        return [{'id':v.pk if area=='revision-publicidad' else v.anuncio_id,'nombre':v.titulo,'estado':v.estado,'detalle':False} for v in qs.order_by('-pk')[:100]]
    modelos={'adopciones':SolicitudAdopcion,'aportes':Apadrinamiento,'pedidos':PedidoIniciado,'verificaciones':SolicitudValidacion,'reclamaciones':ReclamacionMascota,'expedientes':Mascota}
    modelo=modelos[area];recurso=PRIVADOS[area]
    from seguridad.models import AsignacionRecurso
    asignados=AsignacionRecurso.objects.filter(usuario=request.user,recurso__codigo=recurso,fecha_revocacion__isnull=True).values_list('objeto_id',flat=True)
    qs=modelo.objects.all()
    if not super_:
        if area=='adopciones':
            filtro=Q(usuario_adoptante=request.user)|Q(pk__in=asignados)
            if m.base('adopcion.tomar',entidad):filtro|=Q(mascota__custodiamascota__fundacion_id=entidad,mascota__custodiamascota__fecha_fin__isnull=True)
        elif area=='aportes':
            filtro=Q(usuario_padrino=request.user)|Q(pk__in=asignados)
            if m.base('aporte.tomar',entidad):filtro|=Q(reporte__casorescate__fundacion_id=entidad)
        elif area=='pedidos':
            filtro=Q(usuario_cliente=request.user)|Q(pk__in=asignados)
            if m.base('pedido.tomar',entidad):filtro|=Q(tienda_id=entidad)
        elif area=='verificaciones':filtro=Q() if m.base('verificacion.tomar') else Q(usuario_solicitante=request.user)|Q(pk__in=asignados)
        elif area=='reclamaciones':filtro=Q(reclamante=request.user)|Q(revisor=request.user)|(Q(revisor__isnull=True,estado='PENDIENTE') if m.base('reclamacion.tomar') else Q(pk__in=[]))
        else:filtro=Q(dueno=request.user)|Q(autorizacionexpediente__veterinario__usuario_profesional=request.user,autorizacionexpediente__fecha_revocacion__isnull=True)
        qs=qs.filter(filtro).distinct()
    for obj in qs.order_by('-pk')[:100]:
        leer=flujos.leer(request.user,recurso,obj.pk)
        tomar=False
        if not leer and recurso in ('adopcion','aporte','pedido','verificacion') and m.base(recurso+'.tomar',entidad):
            from seguridad.objetos import contexto
            c=contexto(recurso,obj.pk)
            tomar=c.disponible and (recurso=='verificacion' or c.entidad_id==entidad)
        if not leer and recurso=='reclamacion' and m.base('reclamacion.tomar'):
            tomar=obj.revisor_id is None and obj.estado=='PENDIENTE'
        if not leer and not tomar:continue
        estado=getattr(obj,'estado',None) or getattr(getattr(obj,'estado_adopcion',None),'nombre',None) or getattr(getattr(obj,'estado_pedido',None),'nombre',None) or getattr(getattr(obj,'estado_solicitud',None),'nombre',None) or getattr(getattr(obj,'estado_apadrinamiento',None),'nombre',None) or getattr(getattr(obj,'estado_mascota',None),'nombre',None) or 'Disponible'
        nombre=getattr(obj,'nombre',None) or f'{AREAS[area]} #{obj.pk}'
        datos.append({'id':obj.pk,'nombre':nombre,'estado':estado,'detalle':leer,'tomar':tomar,'propio':getattr(obj,{'adopciones':'usuario_adoptante_id','aportes':'usuario_padrino_id','pedidos':'usuario_cliente_id','verificaciones':'usuario_solicitante_id','expedientes':'dueno_id','reclamaciones':'reclamante_id'}[area],None)==request.user.pk})
    return datos


def opciones_fk(request,nombre,field):
    from accounts.models import Usuario
    from core.models import EntidadMiembro, Veterinario
    from funds.models import FondoExterno
    from commerce.models import Producto
    from rescue.models import Reporte
    m=motor(request.user);entidad=request.panel['entidad_id']
    qs=None
    if nombre in ('usuario_id','usuario_profesional_id','nuevo_dueno_id','dueno_actual_id'):
        qs=Usuario.objects.all() if m.base('usuarios.ver') else Usuario.objects.filter(Q(pk=request.user.pk)|Q(entidadmiembro__entidad_id=entidad)).distinct()
    elif nombre in ('id_mascota','mascota_id','mascota'):
        from adoption.consultas import disponibles_adopcion
        qs=disponibles_adopcion() if request.GET.get('accion')=='solicitar-adopcion' else mascotas_visibles(request.user,entidad)
    elif nombre=='especie_id':qs=Especie.objects.filter(activo=True).order_by('nombre')
    elif nombre=='raza_id':qs=Raza.objects.filter(activo=True,especie__activo=True).select_related('especie').order_by('especie__nombre','nombre')
    elif nombre=='rol_id':
        from core.models import Rol
        qs=Rol.objects.filter(activo=True,ambito='ENTIDAD',delegable=True).exclude(codigo='RESPONSABLE_PRINCIPAL')
    elif nombre=='id_tienda':
        from core.models import Tienda
        qs=Tienda.objects.filter(entidad__estado_verificacion__nombre='Verificada').select_related('entidad')
    elif nombre in ('id_fundacion','entidad_id'):
        qs=EntidadVerificable.objects.all() if m.base('entidades.ver') or m.usuario.is_superuser else EntidadVerificable.objects.filter(pk__in=m.miembros)
    elif nombre=='ciudad_id':qs=Ciudad.objects.filter(activo=True).order_by('departamento','nombre')
    elif nombre=='clinica_id':
        from core.models import Clinica
        qs=Clinica.objects.all()
    elif nombre=='id_fondo_externo':qs=FondoExterno.objects.filter(estado_fondo__nombre='Activo')
    elif nombre=='miembro_id' or nombre=='sucesor_id':qs=EntidadMiembro.objects.filter(entidad_id=entidad,fecha_salida__isnull=True).select_related('usuario')
    elif nombre=='id_veterinario':qs=Veterinario.objects.filter(entidad__estado_verificacion__nombre='Verificada').select_related('usuario_profesional')
    elif nombre in ('tipo_reporte','tipo_fondo_id','categoria_id','tipo_id'):
        tipo={'tipo_reporte':'tipo_reporte','tipo_fondo_id':'tipo_fondo','categoria_id':'categoria_producto','tipo_id':'tipo_producto'}[nombre]
        qs=ValorMaestro.objects.filter(tipo__nombre=tipo)
    elif nombre=='id_reporte':qs=Reporte.objects.filter(casorescate__isnull=False).exclude(publicacionreporte__oculta=True)
    if qs is None and isinstance(field,drf.PrimaryKeyRelatedField):qs=field.queryset
    if qs is None:return None
    if nombre=='especie_id':return [(o.pk,o.nombre) for o in Especie.objects.filter(activo=True).order_by('nombre')]
    if nombre=='ciudad_id':return [(o.pk,o.nombre+' · '+o.departamento) for o in qs]
    if nombre=='raza_id':return [(o.pk,o.especie.nombre+' · '+o.nombre) for o in qs]
    return [(o.pk,f'#{o.pk} · '+str(getattr(o,'nombre',None) or getattr(getattr(o,'entidad',None),'nombre',None) or getattr(getattr(o,'usuario',None),'nombre',None) or getattr(getattr(o,'usuario_profesional',None),'nombre',None) or getattr(o,'descripcion',None) or str(o))[:100]) for o in qs[:200]]


def formulario(request,op,datos=None):
    campos={};carrito=False
    iniciales={}
    registro=request.GET.get('registro','')
    permitidos_edicion=mascotas_visibles(request.user,request.panel['entidad_id']).filter(pk=int(registro)).exists() if op.area=='mascotas' and registro.isdigit() else any(str(r['id'])==registro for r in filas(request,op.area))
    if op.metodo=='patch' and registro.isdigit() and permitidos_edicion:
        modelos={'organizaciones':'core.models.EntidadVerificable','mascotas':'animals.models.Mascota','fondos':'funds.models.FondoExterno','catalogo':'commerce.models.Producto'}
        obj=import_string(modelos[op.area]).objects.filter(pk=int(registro)).first() if op.area in modelos else None
        if obj:
            for f in obj._meta.concrete_fields:
                iniciales[f.attname]=getattr(obj,f.attname)
            if op.area=='catalogo':iniciales['disponible']=obj.estado_producto.nombre=='Disponible'
            if op.area=='organizaciones':
                for ruta in ('fundacion','tienda','clinica'):
                    relacionado=getattr(obj,ruta,None)
                    if relacionado:
                        for f in relacionado._meta.concrete_fields:iniciales[f.attname]=getattr(relacionado,f.attname)
                capacidad=__import__('core.models',fromlist=['CapacidadFundacion']).CapacidadFundacion.objects.filter(fundacion_id=obj.pk).first()
                if capacidad:iniciales['cupos_totales']=capacidad.cupos_totales
    if op.registro:
        especiales={'resolver-transferencia':('seguridad.models.TransferenciaResponsabilidad','entidad_id'), 'aprobar-cuenta':('seguridad.models.PropuestaCuenta','entidad_id'), 'resolver-correccion':('seguridad.models.CorreccionReporte','reporte__casorescate__fundacion_id'), 'enmendar-atencion':('animals.models.HistorialMedico','mascota__custodiamascota__fundacion_id'), 'revocar-autorizacion':('animals.models.AutorizacionExpediente','mascota__custodiamascota__fundacion_id')}
        key=next((k for k,o in OPERACIONES.items() if o is op),'')
        especial=key.removesuffix('-mascota')
        if especial in especiales:
            modelo,filtro=especiales[especial];qs=import_string(modelo).objects.all()
            if not es_superusuario(request.user):
                if especial=='resolver-transferencia':qs=qs.filter(Q(saliente__usuario=request.user)|Q(sucesor__usuario=request.user))
                elif especial=='revocar-autorizacion':qs=qs.filter(Q(mascota__dueno=request.user)|Q(mascota__custodiamascota__fundacion_id=request.panel['entidad_id'],mascota__custodiamascota__fecha_fin__isnull=True)).distinct()
                else:qs=qs.filter(**{filtro:request.panel['entidad_id']})
            if especial=='resolver-transferencia':
                qs=qs.filter(estado='PENDIENTE')
                if request.panel['entidad_id']:qs=qs.filter(entidad_id=request.panel['entidad_id'])
                qs=qs.select_related('entidad','saliente__usuario','sucesor__usuario')
                opciones=[(o.pk,f'{o.entidad.nombre} · {o.saliente.usuario.nombre} → {o.sucesor.usuario.nombre} · Pendiente') for o in qs[:100]]
            else:opciones=[(o.pk,'Registro #'+str(o.pk)) for o in qs[:100]]
        elif op.area=='mascotas':opciones=[(o.pk,f'#{o.pk} · {o.nombre}') for o in mascotas_visibles(request.user,request.panel['entidad_id'])[:200]]
        else:opciones=[(o['id'],f"#{o['id']} · {o['nombre']}") for o in filas(request,op.area)]
        campos['registro']=forms.TypedChoiceField(choices=[('','Selecciona el registro')]+opciones,coerce=int,label=ETIQUETAS['registro'],initial=request.GET.get('registro'))
    if '{token}' in op.url:campos['token']=forms.CharField(max_length=100,label='Código de acceso QR',widget=forms.PasswordInput(render_value=False))
    if op.serializer:
        ser=import_string(op.serializer)()
        for nombre,f in ser.fields.items():
            if op.area=='reportes' and nombre in ('latitud','longitud'):continue
            label=ETIQUETAS.get(nombre,nombre.replace('_',' ').capitalize());required=f.required and not f.allow_null and op.metodo!='patch'
            inicial=None if f.default is drf.empty else f.default
            choices=opciones_fk(request,nombre,f)
            if nombre=='lineas':
                carrito=True
            elif nombre=='accion':
                valores=['aprobar','rechazar','correcciones','reenviar'] if op.area=='verificaciones' else ['ocultar','republicar','solicitar_revision'] if op.area=='reportes' else ['aprobar','rechazar','ocultar']
                campos[nombre]=forms.ChoiceField(label='Acción',choices=[(x,x.replace('_',' ').capitalize()) for x in valores])
            elif nombre=='estado':
                valores=['Cerrado','Cancelado'] if op.area=='rescates' else ['Contactado','Cancelado']
                campos[nombre]=forms.ChoiceField(label='Nuevo estado',choices=[(x,x) for x in valores])
            elif isinstance(f,drf.FileField):campos[nombre]=forms.FileField(label=label)
            elif isinstance(f,drf.DictField):
                claves=['hogar','experiencia','compromiso'] if nombre=='respuestas' else ['descripcion','contacto_reportante']
                for k in claves:campos[nombre+'__'+k]=forms.CharField(required=nombre=='respuestas',max_length=2000,label=k.replace('_',' ').capitalize(),widget=forms.Textarea(attrs={'rows':3}))
            elif choices is not None:
                campos[nombre]=forms.TypedChoiceField(choices=[('','Selecciona una opción')]+choices,coerce=int,required=required,empty_value=None,label=label)
            elif isinstance(f,drf.ChoiceField):campos[nombre]=forms.ChoiceField(choices=list(f.choices.items()),required=required,label=label)
            elif isinstance(f,drf.BooleanField):
                if nombre=='aprobar':campos[nombre]=forms.TypedChoiceField(choices=[('','Elige la decisión'),('true','Aprobar'),('false','Rechazar')],coerce=lambda x:x=='true',label='Decisión')
                else:campos[nombre]=forms.BooleanField(required=nombre=='confirmar',label=label,initial=inicial)
            elif isinstance(f,drf.DateTimeField):campos[nombre]=forms.DateTimeField(required=required,label=label,widget=forms.DateTimeInput(attrs={'type':'datetime-local'}))
            elif isinstance(f,drf.DateField):campos[nombre]=forms.DateField(required=required,label=label,widget=forms.DateInput(attrs={'type':'date'}))
            elif isinstance(f,drf.DecimalField):campos[nombre]=forms.DecimalField(required=required,label=label,min_value=f.min_value,max_value=f.max_value,max_digits=f.max_digits,decimal_places=f.decimal_places)
            elif isinstance(f,drf.IntegerField):campos[nombre]=forms.IntegerField(required=required,label=label,min_value=f.min_value,max_value=f.max_value,initial=inicial)
            else:
                multiline=nombre in ('detalle','descripcion','motivo','observaciones','texto')
                campos[nombre]=forms.CharField(required=required,label=label,max_length=getattr(f,'max_length',None),initial=inicial,widget=forms.Textarea(attrs={'rows':3}) if multiline else forms.TextInput())
    if op.area=='organizaciones' and ('{entidad}' in op.url or 'transferencias/{pk}' in op.url):
        from .contextos_negocio import organizaciones_para
        ctx=forms.TypedChoiceField(choices=[('','Selecciona la organización')]+[(e.pk,e.nombre) for e in organizaciones_para(request.user,op)],coerce=int,label='Organización del proceso',initial=request.panel['entidad_id'])
        ctx.widget.attrs.update({'data-operation-context':'','data-ui-filter':''})
        campos={'organizacion':ctx,**campos}
    form=type('FormularioOperacion',(forms.Form,),campos)(datos,files=request.FILES if request.method=='POST' else None,initial=iniciales)
    for name,field in form.fields.items():
        if isinstance(field,forms.TypedChoiceField) and name not in ('organizacion','accion','estado'):
            field.widget.attrs['data-searchable-select']=''
        if name=='raza_id':
            import json
            field.widget.attrs['data-species-map']=json.dumps(dict(Raza.objects.values_list('pk','especie_id')))
            field.help_text='Opcional. Elige primero la especie; puedes dejar la raza sin determinar.'
        if name=='especie_id':field.label='Especie';field.help_text='Si no aparece, deja esta opción vacía y describe el animal debajo.'
        if name=='descripcion_especie':field.label='Otra especie o animal no identificado';field.help_text='Por ejemplo: ave pequeña de plumaje amarillo. No necesitas inventar una raza.'
        if name=='tipo_reporte':field.label='¿Qué situación quieres reportar?';field.help_text='Rescate: necesita atención o está en riesgo. Mascota perdida: estás buscando a tu animal. Animal encontrado: lo viste o lo tienes a salvo y buscas a su familia. Abandono o maltrato: describe los hechos observados.'
        if name=='mascota' and op.area=='reportes':field.label='Mascota registrada (opcional)';field.help_text='Si no conoces una ficha, deja este campo vacío y describe el animal.'
        if name=='ciudad_id':field.help_text='Escribe la ciudad y selecciona la coincidencia con su departamento.'
    if carrito:
        from commerce.models import Producto
        from django.forms import formset_factory
        opciones=[(p.pk,f'{p.nombre} · {p.precio}') for p in Producto.objects.filter(estado_producto__nombre='Disponible',tienda__entidad__estado_verificacion__nombre='Verificada')[:200]]
        Linea=type('LineaPedido',(forms.Form,),{'id_producto':forms.TypedChoiceField(choices=opciones,coerce=int,label='Producto'),'cantidad':forms.IntegerField(min_value=1,initial=1,label='Cantidad')})
        form.lineas_formset=formset_factory(Linea,extra=1,can_delete=True,max_num=50,validate_max=True,min_num=1,validate_min=True)(datos,prefix='lineas')
    form.bloqueos=[{'campo':field.label,'nombre':name} for name,field in form.fields.items() if field.required and isinstance(field,forms.TypedChoiceField) and not any(str(value) for value,label in field.choices)]
    return traducir_formulario(form)


def preparar(datos):
    cuerpo={};diccionarios={}
    for nombre,valor in datos.items():
        if nombre in ('registro','token','producto_pedido','cantidad_pedido','organizacion'):continue
        if '__' in nombre:
            grupo,clave=nombre.split('__',1)
            if valor:diccionarios.setdefault(grupo,{})[clave]=valor
        elif nombre in ('raza_id','especie_id'):cuerpo[nombre]=valor
        elif valor is not None and valor!='':cuerpo[nombre]=valor
    cuerpo.update(diccionarios)
    if datos.get('producto_pedido'):cuerpo['lineas']=[{'id_producto':int(datos['producto_pedido']),'cantidad':datos['cantidad_pedido']}]
    return cuerpo


def detalle_legible(data):
    if isinstance(data,dict) and {'id','mime','tamano'}.issubset(data):return [{'titulo':_t('Documento privado #')+str(data['id']),'href':f"/api/seguridad/operaciones/documentos/{data['id']}/descargar/",'texto':str(data['mime'])}]
    if isinstance(data,dict):return [{'titulo':ETIQUETAS.get(k,k.replace('_',' ').capitalize()),'hijos':detalle_legible(_t(v) if k in ('estado','tipo') and isinstance(v,str) else v)} for k,v in data.items() if not any(s in k for s in ('password','cifrado','hash'))]
    if isinstance(data,(list,tuple)):return [{'titulo':_t('Registro %(numero)s') % {'numero':i+1},'hijos':detalle_legible(v)} for i,v in enumerate(data)]
    return [{'texto':_t('Sí') if data is True else _t('No') if data is False else str(data) if data is not None else _t('Sin dato')}]


@protegido
@require_http_methods(['GET','POST'])
def area(request,codigo):
    if codigo not in AREAS:raise PermissionDenied('Área no disponible')
    from .contextos_negocio import preparar_contexto,organizaciones_para
    preparar_contexto(request,codigo,OPERACIONES)
    m=motor(request.user);entidad=request.panel['entidad_id']
    publico=codigo=='fondos' and m.base('fondo.participar')
    if not publico and codigo not in [x['codigo'] for x in request.panel['modulos']]:
        if codigo!='organizaciones' or not (m.base('entidades.ver') or m.base('miembros.ver',entidad) or any(x['codigo'] in ('equipo','cuentas') for x in request.panel['modulos'])):
            raise PermissionDenied('Área no autorizada')
    operaciones=[(k,op) for k,op in OPERACIONES.items() if op.area==codigo and (not op.permiso or m.base(op.permiso,entidad) or (codigo=='organizaciones' and bool(organizaciones_para(request.user,op))))]
    seleccion=next(((k,op) for k,op in operaciones if k==request.GET.get('accion')),None)
    form=None;detalle=None
    if seleccion:
        key,op=seleccion;form=formulario(request,op,request.POST if request.method=='POST' else None)
        if request.method=='POST' and form.is_valid() and (not hasattr(form,'lineas_formset') or form.lineas_formset.is_valid()):
            try:
                if '{entidad}' in op.url and not entidad:raise ValidationError('Selecciona la organización del proceso.')
                url=op.url.format(pk=form.cleaned_data.get('registro'),entidad=entidad,token=form.cleaned_data.get('token',''))
                match=resolve(url)
                cuerpo=preparar(form.cleaned_data)
                if op.metodo=='patch':cuerpo={k:v for k,v in cuerpo.items() if k in request.POST or any(n.startswith(k+'__') for n in request.POST)}
                if hasattr(form,'lineas_formset'):cuerpo['lineas']=[{'id_producto':d['id_producto'],'cantidad':d['cantidad']} for d in form.lineas_formset.cleaned_data if d and not d.get('DELETE')]
                factory=APIRequestFactory()
                req=getattr(factory,op.metodo)('/api/operacion-panel/',cuerpo,format='multipart' if any(hasattr(v,'chunks') for v in cuerpo.values()) else 'json',HTTP_HOST=request.get_host())
                force_authenticate(req,user=request.user)
                from seguridad.auditoria_contexto import actual
                audit_ctx=actual.get();before_events=len(audit_ctx['eventos']) if audit_ctx else 0
                if audit_ctx:audit_ctx['operacion_panel']=key
                with transaction.atomic():
                    response=match.func(req,**match.kwargs)
                    if response.status_code>=400:
                        raise ValidationError(getattr(response,'data',{'detalle':'No se pudo completar la operación.'}))
                    if not audit_ctx or len(audit_ctx['eventos'])==before_events:auditar(request.user,'negocio.operacion',codigo,form.cleaned_data.get('registro'),entidad,motivo=op.nombre,operacion=key)
                if key.startswith('generar-qr'):
                    detalle=detalle_legible(response.data)
                else:
                    messages.success(request,_t('%(operacion)s: operación completada.') % {'operacion':_t(op.nombre)})
                    destino=reverse('panel:area',args=[codigo])
                    if codigo=='mascotas':destino+='?vista='+('propias' if key in ('declarar-mascota','crear-ficha') else request.GET.get('vista','gestion'))
                    return redirect(destino)
            except APIException as exc:
                from seguridad.auditoria_contexto import registrar_fallo
                registrar_fallo(request,exc.status_code,key,form.cleaned_data.get('registro'))
                if isinstance(exc.detail,dict):
                    for campo,errores in exc.detail.items():form.add_error(campo if campo in form.fields else None,texto_error(errores))
                else:form.add_error(None,texto_error(exc.detail))
    elif request.method=='POST':raise PermissionDenied('Selecciona una operación válida.')
    if request.GET.get('detalle') and (codigo in PRIVADOS or codigo in ('mascotas','organizaciones','reportes')):
        if not request.GET['detalle'].isdigit():raise Http404('Registro no válido')
        pk=int(request.GET['detalle'])
        if codigo=='reportes':
            from rescue.models import Reporte
            from geography.models import ReporteUbicacion
            if pk not in {fila['id'] for fila in filas(request,'reportes')}:raise PermissionDenied('Reporte no disponible')
            obj=Reporte.objects.select_related('ciudad','estado_reporte').get(pk=pk)
            location={'ciudad':obj.ciudad.nombre if obj.ciudad else None,'barrio':obj.barrio,'direccion':obj.direccion,'indicaciones':obj.indicaciones}
            coordinates=ReporteUbicacion.objects.filter(reporte=obj).values('latitud','longitud').first()
            if coordinates:location['coordenadas históricas']=coordinates
            detalle=detalle_legible({'situacion':obj.tipo_reporte.nombre,'descripcion':obj.descripcion,'estado':obj.estado_reporte.nombre,'ubicacion':location})
            auditar(request.user,'registro.consultar','reportes',pk)
        elif codigo=='organizaciones':
            if not m.base('entidades.ver') and not m.base('miembros.ver',pk):raise PermissionDenied('No puedes consultar esta organización.')
            e=EntidadVerificable.objects.select_related('estado_verificacion').filter(pk=pk).first()
            if not e:raise Http404('Organización no disponible')
            data={'nombre':e.nombre,'estado':e.estado_verificacion.nombre}
            for tipo in ('fundacion','tienda','clinica','veterinario'):
                obj=getattr(e,tipo,None)
                if obj:
                    data['tipo']=tipo
                    for campo in ('descripcion','direccion','whatsapp','especialidad'):
                        if hasattr(obj,campo):data[campo]=getattr(obj,campo)
                    if hasattr(obj,'ciudad'):data['ciudad']=obj.ciudad.nombre
            detalle=detalle_legible(data);auditar(request.user,'registro.consultar','entidades',pk)
        else:
            from seguridad.flujos_views import RegistroPrivadoView
            if codigo=='mascotas':
                from seguridad.consultas_negocio import mascotas_visibles
                if not mascotas_visibles(request.user,entidad).filter(pk=pk).exists():raise PermissionDenied('No puedes consultar esta ficha.')
                pet=Mascota.objects.select_related('raza__especie','estado_mascota').get(pk=pk)
                detalle=detalle_legible({'nombre':pet.nombre,'raza':pet.raza_nombre,'especie':pet.especie_nombre,'estado':pet.estado_mascota.nombre,'fecha_nacimiento':pet.fecha_nacimiento})
                if not flujos.leer(request.user,'expediente',pk):
                    auditar(request.user,'registro.consultar','mascotas',pk)
                else:
                    req=APIRequestFactory().get('/api/operacion-panel/',HTTP_HOST=request.get_host());force_authenticate(req,user=request.user)
                    response=RegistroPrivadoView.as_view()(req,recurso='expediente',pk=pk)
                    if response.status_code>=400:raise PermissionDenied('No puedes consultar el expediente.')
                    detalle+=detalle_legible(response.data)
            else:
                req=APIRequestFactory().get('/api/operacion-panel/',HTTP_HOST=request.get_host());force_authenticate(req,user=request.user)
                response=RegistroPrivadoView.as_view()(req,recurso=PRIVADOS[codigo],pk=pk)
                if response.status_code>=400:raise PermissionDenied('No puedes consultar este registro.')
                detalle=detalle_legible(response.data)
    datos=filas(request,codigo)
    especiales={'resolver-transferencia','aprobar-cuenta','resolver-correccion','enmendar-atencion','revocar-autorizacion','revocar-autorizacion-mascota'}
    solo_propios={'respuestas-adopcion','retirar-adopcion','declarar-aporte'}
    for registro in datos:
        acciones=[]
        for key,op in operaciones:
            if not op.registro or key in especiales:continue
            if key=='publicar-adopcion' and not registro.get('gestion_adopcion'):continue
            if key=='registrar-rescatada' and registro.get('mascota_registrada'):continue
            if key.endswith('-mascota') and not registro.get('autorizar'):continue
            if key in solo_propios and not registro.get('propio'):continue
            if key.startswith('tomar-') and not registro.get('tomar'):continue
            if key.startswith('adjuntar-') and not registro.get('detalle'):continue
            if op.permiso and not puede(request.user,op.permiso,entidad_id=entidad,objeto_id=registro['id']):continue
            if key=='resolver-adopcion' and registro['estado']!='Pendiente':continue
            if key=='resolver-reclamacion' and registro['estado']!='PENDIENTE':continue
            if key=='ejecutar-titularidad' and registro['estado']!='FAVORABLE':continue
            acciones.append((key,op))
        registro['acciones']=acciones
    cabecera=[(k,o) for k,o in operaciones if not o.registro or k in especiales]
    if codigo=='organizaciones':
        contextuales=[(k,o,{e.pk for e in organizaciones_para(request.user,o)}) for k,o in operaciones if k in ('designar-principal','transferir-principal','pedir-verificacion','resolver-transferencia')]
        for registro in datos:registro['acciones_contexto']=[(k,o) for k,o,ids in contextuales if registro['id'] in ids]
    if codigo=='mascotas' and request.GET.get('estado'):datos=[d for d in datos if d['estado']==request.GET['estado']]
    q=request.GET.get('q','')[:100].casefold()
    if q:datos=[d for d in datos if q in (str(d['id'])+' '+d['nombre']+' '+d['estado']+' '+_t(d['estado'])).casefold()]
    equipo=[]
    if codigo=='organizaciones' and entidad and m.base('miembros.ver',entidad):
        from core.models import EntidadMiembro
        from seguridad.models import ResponsableEntidad
        principal=ResponsableEntidad.objects.filter(entidad_id=entidad).values_list('principal_id',flat=True).first()
        for miembro in EntidadMiembro.objects.filter(entidad_id=entidad,fecha_salida__isnull=True).select_related('usuario').prefetch_related('entidadmiembrorol_set__rol'):
            cargos=[r.rol.nombre for r in miembro.entidadmiembrorol_set.all() if r.fecha_revocacion is None and r.rol.activo]
            if miembro.pk==principal:cargos.insert(0,'Responsable principal')
            equipo.append({'nombre':miembro.usuario.nombre,'email':miembro.usuario.email,'cargos':cargos,'id':miembro.pk})
    actual=next((x for x in request.panel['modulos'] if x['codigo']==codigo),None)
    if actual is None and codigo=='organizaciones':actual=next((x for x in request.panel['modulos'] if x['codigo'] in ('equipo','cuentas')),None)
    return render(request,'seguridad/web/negocio.html',{**request.panel,'actual':actual,'area_codigo':codigo,'area_nombre':actual['nombre'] if actual else AREAS[codigo],'area_descripcion':actual['descripcion'] if actual else '', 'puede_desactivar_entidad':codigo=='organizaciones' and m.base('entidades.desactivar'),'puede_restaurar_entidad':codigo=='organizaciones' and m.base('entidades.restaurar'),'puede_catalogos':m.base('catalogos.ver'),'puede_baja_entidad':codigo=='organizaciones' and any(m.base('entidades.'+a) for a in ('eliminar','desactivar','restaurar')),'equipo_area':equipo,'operaciones':cabecera,'operacion_elegida':seleccion[1] if seleccion else None,'form_operacion':form,'registros':datos,'detalle_negocio':detalle})
