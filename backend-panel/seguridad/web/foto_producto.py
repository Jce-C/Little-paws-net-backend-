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
from commerce import public_photos as photos
from commerce.models import FotoPublicaProducto
from commerce.photo_views import FotoProductoThrottle
from seguridad.i18n import traducir_formulario, texto_error
from .views import protegido


class PublicarForm(forms.Form):
    archivo = forms.FileField(label=_("Fotografía (obligatoria)"), widget=forms.FileInput(attrs={
        "accept": "image/jpeg,image/png,image/webp", "aria-describedby": "foto-ayuda"}))
    confirmar_publicacion = forms.BooleanField(label=_("Tengo autorización para publicar esta fotografía y he revisado que no exponga datos personales."))


class RetirarForm(forms.Form):
    confirmar_retirada = forms.BooleanField(label=_("Confirmo que quiero retirar la fotografía del catálogo público."))


@protegido
@csrf_protect
@require_http_methods(['GET', 'POST'])
def fotografia(request, producto_id):
    product = photos.autorizado(request.user, producto_id)
    mode = request.GET.get('modo', 'publicar')
    if mode not in {'publicar', 'retirar'}:
        raise Http404
    photo = FotoPublicaProducto.objects.filter(producto=product).first()
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
                    photos.retirar(request.user, product.pk)
                    messages.success(request, _('Fotografía retirada del catálogo público.'))
                else:
                    limiter = FotoProductoThrottle()
                    if not limiter.allow_request(request, None):
                        raise Throttled(wait=limiter.wait())
                    photos.publicar(request.user, product.pk, form.cleaned_data['archivo'], form.cleaned_data['confirmar_publicacion'])
                    messages.success(request, _('Fotografía publicada. Ya está disponible en el catálogo y la app.'))
                return redirect('panel:foto_producto', producto_id=product.pk)
            except APIException as exc:
                if exc.status_code in (401, 403):
                    raise
                form.add_error(None, texto_error(exc.detail))
                status = exc.status_code
    visible = photos.disponibles().filter(pk=product.pk).exists()
    context = {**request.panel, 'actual': next((m for m in request.panel['modulos'] if m['codigo'] == 'catalogo'), None),
               'producto_foto': product, 'modo_foto': mode, 'tiene_publicacion': bool(photo and photo.publicada),
               'foto_actual': photos.descriptor(product) if visible else None,
               'puede_publicar_foto': visible, 'form_foto': traducir_formulario(form),
               'volver_fotos': reverse('panel:area', args=['catalogo'])}
    return render(request, 'seguridad/web/foto_producto.html', context, status=status)
