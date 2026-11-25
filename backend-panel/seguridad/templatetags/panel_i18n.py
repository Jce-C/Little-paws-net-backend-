"""Translate presentation labels without modifying stored names, codes or permissions."""
from django import template
from django.forms.utils import ErrorList
from django.utils.translation import gettext

register = template.Library()

@register.filter
def ui(value):
    return gettext(str(value)) if value is not None else ''

@register.filter
def ui_errors(value):
    return ErrorList([gettext(str(error)) for error in value])

@register.filter
def rol_ui(value):
    role, separator, organization = str(value).partition(' · ')
    return gettext(role) + separator + organization

@register.filter
def ui_lista(values):
    return [rol_ui(value) for value in values]
