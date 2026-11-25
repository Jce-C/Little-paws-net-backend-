from django import forms
from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from rest_framework.exceptions import APIException
from accounts.models import Usuario
from core.models import Rol,UsuarioRol
from seguridad.autorizacion import exigir,motor
from seguridad.serializers import UsuarioSerializer
from seguridad.servicios import auditar,guardar_estado_usuario
from .views import protegido
from seguridad.i18n import traducir_formulario,texto_error
from django.utils.translation import gettext as _t


class UsuarioForm(forms.Form):
    nombre=forms.CharField(max_length=150,label='Nombre completo')
    email=forms.EmailField(label='Correo electrónico')
    telefono=forms.CharField(max_length=20,label='Teléfono',required=False)
    is_active=forms.BooleanField(label='Cuenta activa',required=False,initial=True)
    password=forms.CharField(max_length=255,label='Contraseña inicial',required=False,widget=forms.PasswordInput(attrs={'autocomplete':'new-password'}))


@protegido
@require_http_methods(['GET','POST'])
def usuarios(request):
    exigir(request.user,'usuarios.ver')
    elegido=Usuario.objects.filter(pk=request.GET.get('editar')).first() if request.GET.get('editar','').isdigit() else None
    nuevo=request.GET.get('nuevo')=='1'
    form=None
    if elegido or nuevo:
        exigir(request.user,'usuarios.crear' if nuevo else 'usuarios.editar')
        inicial={k:getattr(elegido,k) for k in ('nombre','email','telefono','is_active')} if elegido else {}
        form=traducir_formulario(UsuarioForm(request.POST if request.method=='POST' else None,initial=inicial))
        if elegido:form.fields.pop('password')
        else:form.fields['password'].required=True
        if request.method=='POST' and form.is_valid():
            datos=form.cleaned_data
            s=UsuarioSerializer(elegido,data=datos,partial=bool(elegido))
            try:
                s.is_valid(raise_exception=True)
                from django.db import transaction
                with transaction.atomic():
                    if elegido:
                        guardar_estado_usuario(request.user,elegido,s.validated_data)
                    else:
                        persona=s.save(debe_cambiar_clave=True)
                        UsuarioRol.objects.get_or_create(usuario=persona,rol=Rol.objects.get(codigo='CIUDADANO',activo=True))
                        auditar(request.user,'usuario.crear','usuarios',persona.pk,motivo='Alta con contraseña temporal y rol ciudadano')
                messages.success(request,_t('Cuenta guardada. Las nuevas cuentas deben cambiar la contraseña inicial.'))
                return redirect('panel:usuarios')
            except APIException as exc:
                from seguridad.auditoria_contexto import registrar_fallo
                registrar_fallo(request,exc.status_code,'usuarios.guardar',getattr(elegido,'pk',None))
                form.add_error(None,texto_error(exc.detail))
    elif request.method=='POST':
        exigir(request.user,'usuarios.editar')
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied('Selecciona la cuenta que deseas editar.')
    q=request.GET.get('q','')[:100]
    filtro=Q(nombre__icontains=q)|Q(email__icontains=q)
    if q.isdigit():filtro|=Q(pk=int(q))
    qs=Usuario.objects.prefetch_related('usuariorol_set__rol','entidadmiembro_set__entidad','entidadmiembro_set__entidadmiembrorol_set__rol','entidadmiembro_set__responsableentidad_set').filter(filtro).order_by('nombre')
    page=Paginator(qs,25).get_page(request.GET.get('pagina'))
    actual=next((m for m in request.panel['modulos'] if m['codigo']=='usuarios'),None)
    return render(request,'seguridad/web/usuarios.html',{**request.panel,'actual':actual,'form_usuario':form,'elegido':elegido,'personas':UsuarioSerializer(page,many=True).data,'paginacion':page,'puede_eliminar':motor(request.user).base('usuarios.eliminar'),'puede_desactivar':motor(request.user).base('usuarios.desactivar'),'puede_restaurar':motor(request.user).base('usuarios.restaurar'),'puede_baja':any(motor(request.user).base('usuarios.'+a) for a in ('eliminar','desactivar','restaurar')),'puede_crear':motor(request.user).base('usuarios.crear'),'puede_editar':motor(request.user).base('usuarios.editar'),'puede_roles':motor(request.user).base('roles.asignar')})
