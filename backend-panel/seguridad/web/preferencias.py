"""Preferencias visuales locales: no modifican cuentas, permisos ni datos."""
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST


OPCIONES = {
    "texto": ("normal", "large", "largest"),
    "contraste": ("normal", "strong"),
    "movimiento": ("system", "reduce"),
}


def contexto_preferencias(request):
    return {"vista": {campo: request.COOKIES.get("lpn_" + campo, valores[0])
                     if request.COOKIES.get("lpn_" + campo, valores[0]) in valores else valores[0]
                     for campo, valores in OPCIONES.items()}}


@never_cache
@csrf_protect
@require_POST
def guardar(request):
    destino = request.POST.get("next", "")[:2048]
    if not url_has_allowed_host_and_scheme(destino, {request.get_host()}, require_https=request.is_secure()):
        destino = reverse("panel:login")
    if not destino.startswith("/panel/"):
        destino = reverse("panel:login")
    respuesta = HttpResponseRedirect(destino)
    for campo, valores in OPCIONES.items():
        valor = request.POST.get(campo, valores[0]) if request.POST.get("restablecer") != "1" else valores[0]
        valor = valor if valor in valores else valores[0]
        respuesta.set_cookie("lpn_" + campo, valor, max_age=31536000,
                            secure=settings.SESSION_COOKIE_SECURE, httponly=True, samesite="Lax")
    return respuesta
