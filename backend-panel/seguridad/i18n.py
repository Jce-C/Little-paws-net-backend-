"""Translate error messages at the HTTP boundary; domain codes and data stay stable."""
from django.utils.translation import gettext
from rest_framework.exceptions import ErrorDetail
from rest_framework.views import exception_handler as drf_exception_handler


def traducir_error(valor):
    if isinstance(valor, dict):
        return {clave: traducir_error(dato) for clave, dato in valor.items()}
    if isinstance(valor, list):
        return [traducir_error(dato) for dato in valor]
    if isinstance(valor, ErrorDetail):
        return ErrorDetail(gettext(str(valor)), code=valor.code)
    if isinstance(valor, str):
        return gettext(valor)
    return valor


def traducir_formulario(form):
    """Localize labels and choice captions, never submitted values or IDs."""
    for field in form.fields.values():
        if field.label:
            field.label = gettext(str(field.label))
        if field.help_text:
            field.help_text = gettext(str(field.help_text))
        if hasattr(field, 'choices'):
            field.choices = [(key, gettext(str(label))) for key, label in field.choices]
    if hasattr(form, 'lineas_formset'):
        for line in form.lineas_formset:
            traducir_formulario(line)
    return form


def texto_error(value):
    """Readable form errors; keep the API's structured error payload intact."""
    if isinstance(value, dict):
        return ' '.join(
            ('' if key in ('detail', 'detalle', 'non_field_errors') else gettext(str(key).replace('_', ' ').capitalize()) + ': ')
            + texto_error(message) for key, message in value.items()
        )
    if isinstance(value, (list, tuple)):
        return ' '.join(texto_error(message) for message in value)
    return gettext(str(value))


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is not None:
        response.data = traducir_error(response.data)
    return response
