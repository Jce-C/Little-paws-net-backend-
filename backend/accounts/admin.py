"""Alta segura de usuarios y consulta de cuentas en el panel interno."""

from django import forms
from django.contrib import admin
from django.contrib.auth.password_validation import validate_password

from core.admin_base import SoloLecturaAdmin

from .models import Usuario


class CrearUsuarioAdminForm(forms.ModelForm):
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ("email", "nombre", "telefono")

    def clean(self):
        datos = super().clean()
        clave = datos.get("password1")
        if clave and clave != datos.get("password2"):
            self.add_error("password2", "Las contraseñas no coinciden.")
        if clave:
            candidato = Usuario(email=datos.get("email", ""), nombre=datos.get("nombre", ""))
            try:
                validate_password(clave, candidato)
            except forms.ValidationError as exc:
                self.add_error("password1", exc)
        return datos

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = Usuario.objects.normalize_email(usuario.email).strip()
        usuario.set_password(self.cleaned_data["password1"])
        if commit:
            usuario.save()
        return usuario


@admin.register(Usuario)
class UsuarioAdmin(SoloLecturaAdmin):
    list_display = ("id_usuario", "email", "nombre", "is_active", "is_staff", "is_superuser")
    search_fields = ("email", "nombre")
    list_filter = ("is_active", "is_staff", "is_superuser")
    ordering = ("email",)

    def has_add_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs["form"] = CrearUsuarioAdminForm
        return super().get_form(request, obj, **kwargs)

    def get_fields(self, request, obj=None):
        if obj is None:
            return ("email", "nombre", "telefono", "password1", "password2")
        return ("id_usuario", "email", "nombre", "telefono", "is_active", "is_staff", "is_superuser", "fecha_registro")

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()
        return self.get_fields(request, obj)
