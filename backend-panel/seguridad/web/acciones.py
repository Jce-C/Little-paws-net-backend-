from django.shortcuts import render,redirect
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext as _
from rest_framework.exceptions import APIException,ValidationError
from core.models import Permiso
from seguridad.autorizacion import exigir,motor
from seguridad.politicas import POLITICAS
from seguridad.serializers import PermisoSerializer
from seguridad.servicios import auditar,bloqueo_seguridad
from seguridad.administracion_segura import delegables
from seguridad.presentacion import presentacion
from seguridad.i18n import texto_error
from .views import protegido

@protegido
@require_http_methods(['GET','POST'])
def acciones(request):
    m=motor(request.user)
    exigir(request.user,'permisos.editar' if m.base('permisos.editar') else 'permisos.crear')
    codigo=request.POST.get('codigo') or request.GET.get('codigo') or sorted(POLITICAS)[0]
    if codigo not in POLITICAS:raise ValidationError('La acción requiere una operación implementada en el servidor.')
    obj=Permiso.objects.filter(codigo=codigo).first();error=''
    if request.method=='POST':
        try:
            exigir(request.user,'permisos.editar' if obj else 'permisos.crear');delegables(request.user,[codigo])
            with transaction.atomic():
                bloqueo_seguridad()
                s=PermisoSerializer(obj,data={'codigo':codigo,'descripcion':request.POST.get('descripcion',''),'activo':request.POST.get('activo')=='1'},partial=bool(obj))
                s.is_valid(raise_exception=True);obj=s.save()
                auditar(request.user,'permisos.editar','permisos',obj.pk,nuevo={'codigo':codigo,'descripcion':obj.descripcion,'activo':obj.activo})
            messages.success(request,_('Acción implementada actualizada.'))
            return redirect(reverse('panel:seguridad')+'?tab=permisos')
        except APIException as exc:error=texto_error(exc.detail)
    disponibles={p.codigo:p for p in Permiso.objects.select_related('recurso').filter(codigo__in=POLITICAS)}
    opciones=[{'codigo':c,'nombre':presentacion(disponibles[c])['nombre'] if c in disponibles else c,'recurso':disponibles[c].recurso.nombre if c in disponibles else POLITICAS[c][0]} for c in sorted(POLITICAS)]
    return render(request,'seguridad/web/acciones.html',{**request.panel,'codigos_acciones':sorted(POLITICAS),'opciones_acciones':opciones,'accion_codigo':codigo,'accion_objeto':obj,'error_admin':error,'accion_contrato':POLITICAS[codigo]})
