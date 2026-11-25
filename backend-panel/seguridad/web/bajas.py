from django.shortcuts import render,redirect
from django.http import Http404
from django.contrib import messages
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext as _
from rest_framework.exceptions import APIException
from seguridad.administracion_segura import preparar_confirmacion,ejecutar_baja
from seguridad.i18n import texto_error
from .views import protegido

@protegido
@require_http_methods(['GET','POST'])
def baja(request,tipo,pk):
    error=''
    if request.method=='POST':
        try:
            ejecutar_baja(request.user,tipo,pk,request.POST.get('accion',''),motivo=request.POST.get('motivo',''),confirmacion=request.POST.get('confirmacion_token',''),nombre=request.POST.get('confirmar_nombre',''),acepto=request.POST.get('acepto')=='1')
            messages.success(request,_('Operación administrativa registrada. El historial se conserva.'))
            return redirect(reverse('panel:usuarios') if tipo=='usuarios' else reverse('panel:seguridad')+'?tab=roles' if tipo=='roles' else reverse('panel:area',args=['catalogo' if tipo=='productos' else 'organizaciones']))
        except APIException as exc:
            error=texto_error(exc.detail)
            from seguridad.auditoria_contexto import registrar_fallo
            registrar_fallo(request,exc.status_code,'baja',pk)
    try:data=preparar_confirmacion(request.user,tipo,pk)
    except ObjectDoesNotExist:raise Http404
    data['accion_inicial']=request.POST.get('accion',request.GET.get('accion','eliminar'))
    data['baja_simple']=data['accion_inicial'] in ('desactivar','restaurar')
    data['puede_desactivar']=any(a['codigo']=='desactivar' for a in data['operaciones_baja'])
    data['puede_restaurar']=any(a['codigo']=='restaurar' for a in data['operaciones_baja'])
    return render(request,'seguridad/web/baja.html',{**request.panel,**data,'error_admin':error})
