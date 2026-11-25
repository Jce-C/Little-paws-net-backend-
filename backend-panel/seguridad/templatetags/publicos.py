import base64,mimetypes,re
from functools import lru_cache
from pathlib import Path
from django import template
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe
register=template.Library()
@register.simple_tag(takes_context=True)
def catalogo_integrado(context):
    # Public login keeps a single request; translate interactive labels inline.
    from django.views.i18n import JavaScriptCatalog
    response=JavaScriptCatalog.as_view(packages=['seguridad'])(context['request'])
    return mark_safe(response.content.decode('utf-8').replace('</script','<\\/script'))
PERMITIDOS={'seguridad/tokens.css','seguridad/preferencias.css','seguridad/tema.css','seguridad/preferencias.js','acceso/login.css','acceso/login.js','acceso/logo.svg','seguridad/icons.svg','seguridad/favicon.svg','seguridad/fonts/LeckerliOne.woff2','seguridad/fonts/JetBrainsMono.woff2','acceso/login-fondo.webp'}
PERMITIDOS.update({'seguridad/avisos.css','seguridad/avisos.js','seguridad/materiales.css'})
@lru_cache(maxsize=32)
def leer(nombre):
    if nombre not in PERMITIDOS:raise ValueError('Recurso público no permitido')
    path=finders.find(nombre)
    if not path:raise ValueError('Recurso público inexistente')
    return Path(path).read_bytes()
@register.simple_tag
def dato_publico(nombre):
    mime=mimetypes.guess_type(nombre)[0] or 'application/octet-stream'
    return 'data:'+mime+';base64,'+base64.b64encode(leer(nombre)).decode()
@register.simple_tag
def inline_publico(nombre):
    contenido=leer(nombre).decode('utf-8')
    if nombre=='seguridad/tokens.css':contenido=re.sub(r'@font-face\s*\{[^}]+\}','',contenido)
    return mark_safe(contenido)
@register.simple_tag
def simbolos_publicos():
    contenido=leer('seguridad/icons.svg').decode('utf-8')
    contenido=re.sub(r'<svg\b[^>]*>','<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">',contenido,count=1)
    return mark_safe(contenido)
