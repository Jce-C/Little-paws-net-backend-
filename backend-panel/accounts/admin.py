from django import forms
from django.contrib import admin
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Usuario


def validar_identidad_tecnica(pk,datos):
    if not pk:return
    current=Usuario.objects.get(pk=pk)
    if current.is_superuser and datos.get('is_superuser') is False and not Usuario.objects.filter(is_superuser=True,is_active=True).exclude(pk=pk).exists():
        raise ValidationError(_('No se puede retirar el último superusuario técnico activo.'))
    if current.is_active and datos.get('is_active') is False:
        if current.is_superuser:raise ValidationError(_('Esta cuenta técnica está protegida contra desactivación.'))
        from seguridad.models import ResponsableEntidad
        if ResponsableEntidad.objects.filter(principal__usuario=current,principal__fecha_salida__isnull=True).exists():raise ValidationError(_('Transfiere la responsabilidad principal antes de esta baja.'))
        from core.models import UsuarioRol
        if UsuarioRol.objects.filter(usuario=current,rol__codigo='ADMIN_SEGURIDAD',fecha_revocacion__isnull=True).exists():
            from seguridad.servicios import conservar_administrador
            from rest_framework.exceptions import ValidationError as ErrorAPI
            from seguridad.i18n import texto_error
            try:conservar_administrador(current.pk)
            except ErrorAPI as exc:raise ValidationError(texto_error(exc.detail))
    if not current.is_active and datos.get('is_active') is True:
        from seguridad.models import BajaAdministrativa
        if BajaAdministrativa.objects.filter(tipo='usuarios',objeto_id=pk,activo=False).exists():raise ValidationError(_('Utiliza la restauración confirmada del panel.'))


class CuentaForm(forms.ModelForm):
    password_nueva=forms.CharField(label='Nueva contraseña',required=False,widget=forms.PasswordInput(attrs={'autocomplete':'new-password'}))
    password_confirmar=forms.CharField(label='Repetir contraseña',required=False,widget=forms.PasswordInput(attrs={'autocomplete':'new-password'}))

    class Meta:
        model=Usuario
        fields=['nombre','email','telefono','is_active','is_staff','is_superuser','debe_cambiar_clave']

    def clean(self):
        datos=super().clean()
        try:validar_identidad_tecnica(self.instance.pk,datos)
        except ValidationError:
            from seguridad.auditoria_contexto import actual,registrar_fallo
            ctx=actual.get()
            if ctx:registrar_fallo(ctx['request'],403,'django_admin.validar',self.instance.pk)
            raise
        clave=datos.get('password_nueva')
        if not self.instance.pk and not clave:
            raise ValidationError('Escribe una contraseña inicial.')
        if clave:
            if clave!=datos.get('password_confirmar'):
                raise ValidationError('Las contraseñas no coinciden.')
            candidato=Usuario(nombre=datos.get('nombre',''),email=datos.get('email',''))
            validate_password(clave,candidato)
        return datos


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    form=CuentaForm
    list_display=['nombre','email','is_active','is_staff','is_superuser']
    search_fields=['nombre','email']
    list_filter=['is_active','is_staff','is_superuser']
    readonly_fields=['fecha_registro','last_login']

    def has_add_permission(self,request):
        return request.user.is_active and request.user.is_superuser

    def has_change_permission(self,request,obj=None):
        return request.user.is_active and request.user.is_superuser

    def has_delete_permission(self,request,obj=None):
        return False

    @transaction.atomic
    def save_model(self,request,obj,form,change):
        from seguridad.servicios import auditar,guardar_estado_usuario
        from seguridad.servicios import bloqueo_seguridad
        bloqueo_seguridad()
        from django.core.exceptions import PermissionDenied
        current_actor=Usuario.objects.get(pk=request.user.pk)
        if not current_actor.is_active or not current_actor.is_superuser:raise PermissionDenied(_('La autorización técnica cambió; vuelve a iniciar sesión.'))
        try:validar_identidad_tecnica(obj.pk if change else None,form.cleaned_data)
        except ValidationError:raise PermissionDenied(_('La cuenta cambió mientras se editaba. Revisa de nuevo sus protecciones.'))
        if change and 'is_active' in form.changed_data:
            guardar_estado_usuario(request.user,obj,{'is_active':obj.is_active})
        if form.cleaned_data.get('password_nueva'):
            obj.set_password(form.cleaned_data['password_nueva'])
        obj.save()
        if not change:
            from core.models import Rol,UsuarioRol
            UsuarioRol.objects.get_or_create(usuario=obj,rol=Rol.objects.get(codigo='CIUDADANO'))
        auditar(request.user,'django_admin.usuario','usuarios',obj.pk,
            motivo='Administración técnica de la cuenta',campos=[c for c in form.changed_data if not c.startswith('password')])
