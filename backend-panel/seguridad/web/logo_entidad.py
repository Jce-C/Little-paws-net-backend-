"""La web y la API comparten autorización, normalización y auditoría."""
from django import forms
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import Http404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException, Throttled
from core import public_logos as photos
from core.models import LogoPublicoEntidad
from core.logo_views import LogoEntidadThrottle
from seguridad.i18n import traducir_formulario, texto_error
from .views import protegido


class PublicarForm(forms.Form):
    archivo = forms.FileField(label=_("Logo (obligatorio)"), widget=forms.FileInput(attrs={
        "accept": "image/jpeg,image/png,image/webp", "aria-describedby": "logo-ayuda"}))
    confirmar_publicacion = forms.BooleanField(label=_("Tengo autorización para publicar el logo de esta organización."))


class RetirarForm(forms.Form):
    confirmar_retirada = forms.BooleanField(label=_("Confirmo que quiero retirar el logo del directorio público."))


@protegido
@csrf_protect
@require_http_methods(['GET', 'POST'])
def logo_publico(request, entidad_id):
    entity = photos.autorizado(request.user, entidad_id)
    mode = request.GET.get('modo', 'publicar')
    if mode not in {'publicar', 'retirar'}:
        raise Http404
    photo = LogoPublicoEntidad.objects.filter(entidad=entity).first()
    form_class = RetirarForm if mode == 'retirar' else PublicarForm
    form = form_class(request.POST if request.method == 'POST' else None,
                      request.FILES if request.method == 'POST' else None)
    status = 200
    if request.method == 'POST':
        if not form.is_valid():
            status = 400
        else:
            try:
                if mode == 'retirar':
                    photos.retirar(request.user, entity.pk)
                    messages.success(request, _('Logo retirado del directorio público.'))
                else:
                    limiter = LogoEntidadThrottle()
                    if not limiter.allow_request(request, None):
                        raise Throttled(wait=limiter.wait())
                    photos.publicar(request.user, entity.pk, form.cleaned_data['archivo'], form.cleaned_data['confirmar_publicacion'])
                    messages.success(request, _('Logo publicado. Ya está disponible en el directorio y la app.'))
                return redirect('panel:logo_entidad', entidad_id=entity.pk)
            except APIException as exc:
                if exc.status_code in (401, 403):
                    raise
                form.add_error(None, texto_error(exc.detail))
                status = exc.status_code
    visible = photos.disponibles().filter(pk=entity.pk).exists()
    context = {**request.panel, 'actual': next((m for m in request.panel['modulos'] if m['codigo'] == 'organizaciones'), None),
               'entidad_logo': entity, 'modo_logo': mode, 'tiene_publicacion': bool(photo and photo.publicada),
               'logo_actual': photos.descriptor(entity) if visible else None,
               'puede_publicar_logo': visible, 'form_logo': traducir_formulario(form),
               'volver_logos': reverse('panel:area', args=['organizaciones'])}
    return render(request, 'seguridad/web/logo_entidad.html', context, status=status)
