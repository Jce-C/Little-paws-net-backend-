from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.utils.translation import get_language


def health(request):
    return JsonResponse({"status": "ok"})


def idiomas(request):
    idioma = get_language().split("-")[0]
    return JsonResponse({
        "idioma_actual": idioma,
        "idioma_predeterminado": "es",
        "idiomas_disponibles": ["es", "en"],
        "mensaje": "Idiomas disponibles" if idioma == "es" else "Available languages",
    })


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health, name="health"),
    path("api/idiomas/", idiomas, name="idiomas"),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("core.urls")),
    path("api/", include("rescue.urls")),
    path("api/", include("animals.urls")),
    path("api/", include("adoptions.urls")),
    path("api/", include("funds.urls")),
    path("api/", include("commerce.urls")),
]
