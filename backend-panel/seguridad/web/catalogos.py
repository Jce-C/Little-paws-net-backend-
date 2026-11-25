from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from rest_framework.exceptions import APIException
from seguridad import catalogos as c
from seguridad.autorizacion import exigir,tiene_base
from seguridad.i18n import texto_error
from .views import protegido
from seguridad.i18n import traducir_formulario
from django.utils.translation import gettext as _

@protegido
@require_http_methods(['GET','POST'])
def catalogos(request):
    exigir(request.user,'catalogos.ver');tipo=request.GET.get('tipo','ciudades')
    if tipo not in c.MODELOS:tipo='ciudades'
    obj=get_object_or_404(c.MODELOS[tipo],pk=request.GET['editar']) if request.GET.get('editar','').isdigit() else None
    form=None;error=''
    if obj or request.GET.get('nuevo') or request.method=='POST':
        exigir(request.user,'catalogos.editar' if obj else 'catalogos.crear')
        if request.method=='POST':
            try:
                c.guardar(request.user,tipo,request.POST,obj.pk if obj else None,request.POST.get('version'))
                messages.success(request,_('Catálogo actualizado.'));return redirect(reverse('panel:catalogos')+'?tipo='+tipo)
            except APIException as exc:
                from seguridad.auditoria_contexto import registrar_fallo
                registrar_fallo(request,exc.status_code,'catalogos',obj.pk if obj else None)
                error=texto_error(exc.detail)
        form=traducir_formulario(c.formulario(tipo,request.POST if request.method=='POST' else None,obj))
    qs=c.MODELOS[tipo].objects.order_by('nombre');q=request.GET.get('q','')[:100]
    if tipo=='razas':qs=qs.select_related('especie')
    if q:qs=qs.filter(Q(nombre__icontains=q)|Q(departamento__icontains=q)) if tipo=='ciudades' else qs.filter(nombre__icontains=q)
    page=Paginator(qs,25).get_page(request.GET.get('pagina'))
    return render(request,'seguridad/web/catalogos.html',{**request.panel,'actual':next((x for x in request.panel['modulos'] if x['codigo']=='catalogos'),None),'tipo_catalogo':tipo,'tipos_catalogo':[('ciudades',_('Ciudades')),('especies',_('Especies')),('razas',_('Razas'))],'registros_catalogo':page,'form_catalogo':form,'objeto_catalogo':obj,'version_catalogo':c.version(obj) if obj else '', 'error_admin':error,'puede_crear':tiene_base(request.user,'catalogos.crear'),'puede_editar':tiene_base(request.user,'catalogos.editar')})
