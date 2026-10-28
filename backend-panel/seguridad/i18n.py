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


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is not None:
        response.data = traducir_error(response.data)
    return response
