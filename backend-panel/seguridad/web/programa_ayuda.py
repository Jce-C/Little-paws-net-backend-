from django import forms
from django.utils.translation import gettext_lazy as _
from django.forms import formset_factory
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from rest_framework.exceptions import APIException
from core.help_programs import autorizada, datos, guardar
from core.models import ProgramaAyuda
from seguridad.i18n import texto_error
from .views import protegido


class EstadoForm(forms.Form):
    version = forms.CharField(widget=forms.HiddenInput)
    publicada = forms.BooleanField(required=False, label=_('Publicar actividades y canales'))
    confirmar_publicacion = forms.BooleanField(required=False, label=_('Confirmo que la organización autoriza publicar esta información y que los canales le pertenecen.'))


class ActividadForm(forms.Form):
    titulo = forms.CharField(max_length=100, label=_('Actividad'))
    descripcion = forms.CharField(max_length=500, label=_('Qué hará la persona voluntaria'), widget=forms.Textarea(attrs={'rows': 2}))
    horario = forms.CharField(max_length=160, label=_('Horario o disponibilidad por acordar'))
    requisitos = forms.CharField(max_length=300, label=_('Requisitos y acompañamiento'), widget=forms.Textarea(attrs={'rows': 2}))


class CanalForm(forms.Form):
    titulo = forms.CharField(max_length=100, label=_('Nombre del canal'))
    descripcion = forms.CharField(max_length=300, label=_('Para qué sirve y cómo confirmar el aporte'), widget=forms.Textarea(attrs={'rows': 2}))
    url = forms.URLField(max_length=300, label=_('Enlace oficial HTTPS'), assume_scheme='https', widget=forms.URLInput(attrs={'autocomplete': 'url', 'autocapitalize': 'none', 'spellcheck': 'false'}))


@protegido
@csrf_protect
@require_http_methods(['GET', 'POST'])
def programa(request, fundacion_id):
    foundation = autorizada(request.user, fundacion_id)
    saved = datos(ProgramaAyuda.objects.filter(fundacion=foundation).first())
    posted = request.POST if request.method == 'POST' else None
    state = EstadoForm(posted, initial=saved)
    activities = formset_factory(ActividadForm, extra=8-len(saved['actividades']), max_num=8, absolute_max=8, validate_max=True, can_delete=True)(posted, prefix='actividades', initial=saved['actividades'] if posted is None else None)
    channels = formset_factory(CanalForm, extra=4-len(saved['canales']), max_num=4, absolute_max=4, validate_max=True, can_delete=True)(posted, prefix='canales', initial=saved['canales'] if posted is None else None)
    status = 200
    if request.method == 'POST':
        valid = [state.is_valid(), activities.is_valid(), channels.is_valid()]
        if all(valid):
            values = dict(state.cleaned_data)
            for key, forms_list in [('actividades', activities), ('canales', channels)]:
                values[key] = [{k: v for k, v in form.cleaned_data.items() if k != 'DELETE'} for form in forms_list if form.cleaned_data and not form.cleaned_data.get('DELETE')]
            try:
                guardar(request.user, foundation.pk, values)
                messages.success(request, _('Convocatoria publicada.') if values['publicada'] else _('Convocatoria guardada sin publicar.'))
                return redirect('panel:programa_ayuda', fundacion_id=foundation.pk)
            except APIException as exc:
                if exc.status_code in (401, 403):
                    raise
                state.add_error(None, texto_error(exc.detail))
                status = exc.status_code
        else:
            status = 400
    return render(request, 'seguridad/web/programa_ayuda.html', {
        **request.panel, 'fundacion_ayuda': foundation, 'estado_programa': state,
        'grupos_programa': [(_('Actividades de voluntariado'), activities), (_('Canales oficiales de aporte'), channels)],
        'volver_programa': reverse('panel:area', args=['organizaciones']),
        'actual': next((m for m in request.panel['modulos'] if m['codigo'] == 'organizaciones'), None),
    }, status=status)
