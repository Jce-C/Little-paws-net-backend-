from django.contrib import admin
from django.db import connection
from django.http import JsonResponse
from django.urls import include, path
from django.utils.translation import get_language


def health(request):
    return JsonResponse({"status": "ok"})


def inicio(request):
    return JsonResponse({
        "proyecto": "Little Paws Net",
        "descripcion": "API REST para rescate, adopcion, fondos y comercio aliado.",
        "documentacion": "https://github.com/Jce-C/Little-paws-net-backend-",
        "rutas_publicas": ["/api/health/", "/api/idiomas/", "/api/catalogos/", "/api/productos/", "/api/demo/resumen/"],
        "nota": "Los demas recursos requieren autenticacion. Esta API no incluye frontend.",
    })


def idiomas(request):
    idioma = request.GET.get("lang", "").lower()
    if idioma not in {"es", "en"}:
        idioma = get_language().split("-")[0]
    response = JsonResponse({
        "idioma_actual": idioma,
        "idioma_predeterminado": "es",
        "idiomas_disponibles": ["es", "en"],
        "mensaje": "Idiomas disponibles" if idioma == "es" else "Available languages",
    })
    response["Content-Language"] = idioma
    return response


def demo_resumen(request):
    if connection.settings_dict["NAME"] != "little_paws_net_demo":
        return JsonResponse({"detalle": "No disponible"}, status=404)

    from accounts.models import Usuario
    from animals.models import AutorizacionExpediente, CustodiaMascota, HistorialMedico, Mascota
    from rescue.models import (
        Apadrinamiento, CasoRescate, ConfirmacionAporte,
        HistorialEstadoApadrinamiento, HistorialEstadoCaso,
        HistorialEstadoReporte, Reporte, ReporteUbicacion,
    )

    modelos = (
        Usuario, Mascota, Reporte, ReporteUbicacion, HistorialEstadoReporte,
        CasoRescate, HistorialEstadoCaso, Apadrinamiento, ConfirmacionAporte,
        HistorialEstadoApadrinamiento, CustodiaMascota, AutorizacionExpediente,
        HistorialMedico,
    )
    return JsonResponse({
        "aviso": "Datos ficticios de demostracion; no contiene informacion personal real.",
        "usuarios": Usuario.objects.count(),
        "mascotas": Mascota.objects.count(),
        "reportes": Reporte.objects.count(),
        "casos_rescate": CasoRescate.objects.count(),
        "apadrinamientos": Apadrinamiento.objects.count(),
        "atenciones_medicas": HistorialMedico.objects.count(),
        "registros_del_proceso": sum(modelo.objects.count() for modelo in modelos),
    })


urlpatterns = [
    path("", inicio, name="inicio"),
    path("admin/", admin.site.urls),
    path("api/health/", health, name="health"),
    path("api/idiomas/", idiomas, name="idiomas"),
    path("api/demo/resumen/", demo_resumen, name="demo_resumen"),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("core.urls")),
    path("api/", include("rescue.urls")),
    path("api/", include("animals.urls")),
    path("api/", include("adoptions.urls")),
    path("api/", include("funds.urls")),
    path("api/", include("commerce.urls")),
]
