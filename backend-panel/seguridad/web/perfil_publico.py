from django import forms
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from rest_framework.exceptions import APIException
from core.public_profiles import autorizado, guardar, datos
from core.models import PerfilPublicoEntidad
from seguridad.i18n import traducir_formulario, texto_error
from .views import protegido


class PerfilForm(forms.Form):
    descripcion = forms.CharField(required=False, max_length=2000, label=_('Descripción pública'), help_text=_('Obligatoria al publicar; máximo 2000 caracteres.'), widget=forms.Textarea(attrs={'rows': 4}))
    servicios = forms.CharField(required=False, max_length=1000, label=_('Servicios que ofrece'), widget=forms.Textarea(attrs={'rows': 3}))
    telefono = forms.CharField(required=False, max_length=32, label=_('Teléfono público'), widget=forms.TextInput(attrs={'type': 'tel', 'autocomplete': 'tel'}))
    correo = forms.EmailField(required=False, label=_('Correo público'), widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    sitio_web = forms.URLField(required=False, max_length=200, label=_('Sitio web público'), help_text=_('Solo HTTPS. No se consulta ni descarga el contenido del enlace.'), widget=forms.URLInput(attrs={'autocomplete': 'url', 'spellcheck': 'false', 'autocapitalize': 'none'}))
    publicada = forms.BooleanField(required=False, label=_('Mostrar esta ficha en el directorio público'))
    confirmar_publicacion = forms.BooleanField(required=False, label=_('Tengo autorización para publicar estos textos y datos de contacto.'))


@protegido
@csrf_protect
@require_http_methods(['GET', 'POST'])
def perfil_publico(request, entidad_id):
    entity = autorizado(request.user, entidad_id)
    profile = PerfilPublicoEntidad.objects.filter(entidad=entity).first()
    form = PerfilForm(request.POST if request.method == 'POST' else None, initial=datos(profile) if profile else None)
    status = 200
    if request.method == 'POST':
        if form.is_valid():
            try:
                profile = guardar(request.user, entity.pk, form.cleaned_data)
                messages.success(request, _('Ficha pública actualizada.') if profile.publicada else _('Ficha guardada sin publicar.'))
                return redirect('panel:perfil_publico', entidad_id=entity.pk)
            except APIException as exc:
                if exc.status_code in (401, 403):
                    raise
                form.add_error(None, texto_error(exc.detail))
                status = exc.status_code
        else:
            status = 400
    form = traducir_formulario(form)
    context = {**request.panel, 'entidad_perfil': entity, 'perfil_guardado': profile, 'form_perfil': form,
               'actual': next((m for m in request.panel['modulos'] if m['codigo'] == 'organizaciones'), None),
               'volver_perfil': reverse('panel:area', args=['organizaciones']),
               'grupos_perfil': [(_('Sobre la organización'), [form['descripcion'], form['servicios']]),
                                  (_('Contacto autorizado'), [form['telefono'], form['correo'], form['sitio_web']])]}
    return render(request, 'seguridad/web/perfil_publico.html', context, status=status)
