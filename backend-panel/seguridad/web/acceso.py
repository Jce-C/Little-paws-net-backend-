"""Sesión web, captcha consumible y límites compartidos entre procesos mediante MySQL."""
import secrets
import time
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import logout
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import constant_time_compare, salted_hmac

from seguridad.models import DesafioWeb, LimiteWeb


def huella(valor):
    return salted_hmac("little-paws-web", str(valor), algorithm="sha256").hexdigest()


@transaction.atomic
def limitar(tipo, valor, maximo, segundos=900):
    clave = huella(f"{tipo}:{valor}")
    ventana = int(time.time()) // segundos
    fila, _ = LimiteWeb.objects.get_or_create(clave=clave, defaults={"ventana": ventana})
    fila = LimiteWeb.objects.select_for_update().get(pk=clave)
    if fila.ventana != ventana:
        fila.ventana, fila.cantidad = ventana, 0
    fila.cantidad += 1
    fila.save(update_fields=["ventana", "cantidad"])
    return fila.cantidad <= maximo


def emitir(request):
    if request.session.session_key is None:
        request.session.create()
    a, b = secrets.randbelow(9) + 1, secrets.randbelow(9) + 1
    token = uuid.uuid4()
    DesafioWeb.objects.create(token=token, sesion_hash=huella(request.session.session_key),
        respuesta_hash=huella(f"{token}:{a+b}"), expira=timezone.now()+timedelta(minutes=5))
    # Mantener acotados los desafíos expirados; no guardar la IP ni el correo en claro.
    vencidos = list(DesafioWeb.objects.filter(expira__lt=timezone.now()).values_list("pk", flat=True)[:100])
    DesafioWeb.objects.filter(pk__in=vencidos).delete()
    return {"token": str(token), "suma": f"{a} + {b}"}


@transaction.atomic
def consumir(request, token, respuesta):
    try:
        token = uuid.UUID(str(token))
    except (ValueError, TypeError, AttributeError):
        return False
    obj = DesafioWeb.objects.select_for_update().filter(pk=token).first()
    if obj is None:
        return False
    valido = not obj.consumido and obj.expira > timezone.now() and constant_time_compare(
        obj.sesion_hash, huella(request.session.session_key)) and constant_time_compare(
        obj.respuesta_hash, huella(f"{token}:{str(respuesta).strip()}"))
    # Solo la sesión propietaria puede consumirlo; los errores también exigen otra suma.
    if constant_time_compare(obj.sesion_hash, huella(request.session.session_key)):
        obj.consumido = True
        obj.save(update_fields=["consumido"])
    return bool(valido)


class SesionWebMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        inicio = request.session.get("lpn_web_inicio")
        if inicio is not None and (not isinstance(inicio, (float, int)) or time.time()-inicio > settings.LPN_WEB_SESSION_SECONDS):
            logout(request)
        respuesta = self.get_response(request)
        if request.path.startswith(("/panel/", "/api/seguridad/")):
            respuesta["Cache-Control"] = "no-store"
            respuesta["Referrer-Policy"] = "same-origin"
        return respuesta
