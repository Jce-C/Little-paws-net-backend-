from django import forms
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from rest_framework.exceptions import APIException
from animals.public_photos import custodia_autorizada
from animals.public_presentation import datos, guardar
from animals.models import PresentacionPublicaMascota
from seguridad.i18n import traducir_formulario, texto_error
from .views import protegido


class PresentacionForm(forms.Form):
    descripcion = forms.CharField(required=False, max_length=1000, label=_('Sobre esta mascota'), help_text=_('Obligatoria al publicar. Describe su personalidad y el hogar que busca.'), widget=forms.Textarea(attrs={'rows': 3}))
    cuidados = forms.CharField(required=False, max_length=2000, label=_('Cuidados que debe conocer quien adopta'), help_text=_('Solo información autorizada para el público. No copies el expediente clínico ni datos de personas.'), widget=forms.Textarea(attrs={'rows': 4}))
    espacio = forms.CharField(required=False, max_length=600, label=_('Espacio y entorno recomendados'), widget=forms.Textarea(attrs={'rows': 2}))
    publicada = forms.BooleanField(required=False, label=_('Publicar esta presentación en la ficha de adopción'))
    confirmar_publicacion = forms.BooleanField(required=False, label=_('Confirmo que estos textos están revisados y autorizados para publicación.'))


@protegido
@csrf_protect
@require_http_methods(['GET', 'POST'])
def presentacion(request, mascota_id):
    pet, custody = custodia_autorizada(request.user, mascota_id, bloquear=False)
    profile = PresentacionPublicaMascota.objects.filter(mascota=pet, fundacion=custody.fundacion).first()
    form = PresentacionForm(request.POST if request.method == 'POST' else None, initial=datos(profile) if profile else None)
    status = 200
    if request.method == 'POST':
        if form.is_valid():
            try:
                profile = guardar(request.user, pet.pk, form.cleaned_data)
                messages.success(request, _('Presentación publicada.') if profile.publicada else _('Presentación guardada sin publicar.'))
                return redirect('panel:presentacion_mascota', mascota_id=pet.pk)
            except APIException as exc:
                if exc.status_code in (401, 403):
                    raise
                form.add_error(None, texto_error(exc.detail))
                status = exc.status_code
        else:
            status = 400
    context = {**request.panel, 'mascota_presentacion': pet, 'perfil_presentacion': profile,
               'actual': next((m for m in request.panel['modulos'] if m['codigo'] == 'mascotas'), None),
               'form_presentacion': traducir_formulario(form),
               'volver_presentacion': reverse('panel:area', args=['mascotas']) + '?vista=gestion'}
    return render(request, 'seguridad/web/presentacion_mascota.html', context, status=status)
