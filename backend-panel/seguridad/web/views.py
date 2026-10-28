import time
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods, require_POST
from rest_framework.exceptions import PermissionDenied

from seguridad.autorizacion import usuario_activo, puede, tiene_base
from seguridad.servicios import auditar
from .acceso import emitir, consumir, limitar
from .contexto import construir
from .forms import LoginForm


def retorno_seguro(request, destino):
    return destino if destino and destino.startswith("/panel/") and url_has_allowed_host_and_scheme(
        destino, {request.get_host()}, require_https=request.is_secure()) and not destino.startswith("//") else reverse("panel:inicio")


@never_cache
@sensitive_post_parameters("password", "captcha")
@csrf_protect
@require_http_methods(["GET", "POST"])
def iniciar(request):
    if request.user.is_authenticated and usuario_activo(request.user):
        return redirect("panel:inicio")
    ip = request.META.get("REMOTE_ADDR", "sin-ip")
    destino = request.POST.get("next", request.GET.get("next", ""))[:2048]
    error, estado, correo = "", 200, ""
    if request.method == "POST":
        correo = request.POST.get("email", "")[:254].strip().casefold()
        ip_ok = limitar("login-ip", ip, 25)
        cuenta_ok = limitar("login-cuenta", correo, 8)
        captcha_ok = consumir(request, request.POST.get("captcha_token"), request.POST.get("captcha", ""))
        if not ip_ok or not cuenta_ok:
            return limite(request)
        form = LoginForm(request.POST)
        if form.is_valid() and captcha_ok:
            usuario = authenticate(request, username=form.cleaned_data["email"], password=form.cleaned_data["password"])
            if usuario is not None and usuario_activo(usuario):
                login(request, usuario)
                request.session["lpn_web_inicio"] = time.time()
                request.session.set_expiry(settings.LPN_WEB_SESSION_SECONDS)
                auditar(usuario, "sesion.web_iniciar", "sesion")
                return HttpResponseRedirect(retorno_seguro(request, destino))
        error = "No pudimos iniciar sesión. Revisa tu correo, contraseña y la nueva suma."
        estado = 400
    if not limitar("captcha-ip", ip, 60):
        return limite(request)
    desafio = emitir(request)
    form = LoginForm(initial={"email": correo, "captcha_token": desafio["token"]})
    return render(request, "seguridad/web/login.html", {"form": form, "desafio": desafio,
        "error": error, "next": retorno_seguro(request, destino)}, status=estado)


def limite(request):
    respuesta = render(request, "seguridad/web/error.html", {"titulo": "Hagamos una pausa",
        "detalle": "Se alcanzó el límite de intentos. Intenta nuevamente en 15 minutos.", "codigo": "429"}, status=429)
    respuesta["Retry-After"] = "900"
    return respuesta


def protegido(vista):
    @wraps(vista)
    @never_cache
    def envolver(request, *args, **kwargs):
        if not request.user.is_authenticated or not usuario_activo(request.user):
            if request.user.is_authenticated:
                logout(request)
            from urllib.parse import urlencode
            return redirect(reverse("panel:login") + "?" + urlencode({"next": request.path}))
        contexto = construir(request)
        if not contexto["puede_panel"]:
            return render(request, "seguridad/web/sin_acceso.html", contexto, status=403)
        request.panel = contexto
        try:
            return vista(request, *args, **kwargs)
        except PermissionDenied:
            return render(request, "seguridad/web/error.html", {"titulo": "Este módulo no está disponible",
                "detalle": "Tu cuenta no tiene permiso en este ámbito. Puedes volver al inicio para ver tus accesos actuales.", "codigo": "403"}, status=403)
    return envolver


@protegido
@require_http_methods(["GET"])
def inicio(request):
    return render(request, "seguridad/web/inicio.html", request.panel)


@csrf_protect
@require_POST
def salir(request):
    if request.user.is_authenticated:
        auditar(request.user, "sesion.web_cerrar", "sesion")
    logout(request)
    return redirect("panel:login")


@csrf_protect
@protegido
@require_POST
def seleccionar(request):
    try:
        identificador = int(request.POST.get("entidad_id", ""))
    except ValueError:
        raise PermissionDenied()
    if identificador not in {e["id"] for e in request.panel["organizaciones"]}:
        raise PermissionDenied()
    request.session["lpn_entidad"] = identificador
    return redirect("panel:inicio")


@protegido
@require_http_methods(["GET"])
def modulo(request, codigo):
    m = next((m for m in request.panel["modulos"] if m["codigo"] == codigo), None)
    if m is None:
        raise PermissionDenied()
    entidad_id = request.panel["entidad_id"]
    endpoints = {
        "usuarios": "/api/seguridad/usuarios/", "roles": "/api/seguridad/roles/",
        "recursos": "/api/seguridad/recursos/", "permisos": "/api/seguridad/permisos/",
        "auditoria": "/api/seguridad/auditoria/", "equipo": f"/api/seguridad/entidades/{entidad_id}/miembros/",
        "cuentas": f"/api/seguridad/operaciones/entidades/{entidad_id}/propuestas-cuenta/",
        "publicidad": f"/api/seguridad/operaciones/entidades/{entidad_id}/anuncios/",
        "revision-publicidad": "/api/seguridad/operaciones/publicidad-pendiente/",
        "reclamaciones": "/api/seguridad/operaciones/reclamaciones/",
        "catalogo": f"/api/seguridad/operaciones/entidades/{entidad_id}/productos/",
    }
    recurso = {"verificaciones": "verificacion", "adopciones": "adopcion", "aportes": "aporte", "pedidos": "pedido"}.get(codigo)
    if recurso:
        endpoints[codigo] = f"/api/seguridad/colas/{recurso}/" + (f"?entidad_id={entidad_id}" if recurso != "verificacion" else "")
    datos = None
    if codigo == "rescates":
        from rescue.models import CasoRescate
        datos = list(CasoRescate.objects.filter(fundacion_id=entidad_id).order_by("-pk")
            .values("id_caso", "estado_caso__nombre", "fecha_aceptacion")[:100])
    elif codigo == "fondos":
        from seguridad.models import AsignacionFondo
        datos = [{"id_fondo": a.fondo_id, "nombre": a.fondo.nombre} for a in AsignacionFondo.objects.filter(
            usuario=request.user, fondo__entidad_id=entidad_id, fecha_revocacion__isnull=True).select_related("fondo")
            if puede(request.user, "fondo.ver", objeto_id=a.fondo_id)]
    elif codigo == "expedientes":
        from animals.models import AutorizacionExpediente
        from django.utils import timezone
        datos = [{"id_mascota": a.mascota_id, "nombre": a.mascota.nombre, "autorizacion_hasta": a.fecha_expiracion}
            for a in AutorizacionExpediente.objects.filter(veterinario__usuario_profesional=request.user,
                fecha_revocacion__isnull=True, fecha_expiracion__gt=timezone.now()).select_related("mascota")[:100]
            if puede(request.user, "expediente.escribir", objeto_id=a.mascota_id)]
    contexto = {**request.panel, "actual": m, "endpoint": endpoints.get(codigo, ""),
        "recurso_cola": recurso or "", "datos_iniciales": datos,
        "puede_crear": codigo in ("usuarios", "roles", "recursos") and puede(request.user, f"{codigo}.crear"),
        "puede_editar": codigo in ("usuarios", "roles", "recursos", "permisos") and puede(request.user, f"{codigo}.editar"),
        "puede_asignar_roles": codigo == "usuarios" and puede(request.user, "roles.asignar")}
    return render(request, "seguridad/web/modulo.html", contexto)


def csrf_error(request, reason=""):
    return render(request, "seguridad/web/error.html", {"titulo": "Tu formulario necesita actualizarse",
        "detalle": "Vuelve a abrir la página e intenta nuevamente. No se realizó la operación.", "codigo": "403"}, status=403)
