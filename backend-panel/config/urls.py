from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.views.generic import RedirectView


def health(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("", RedirectView.as_view(pattern_name="panel:login", permanent=False)),
    path("panel/", include("seguridad.web.urls")),
    path("admin/", admin.site.urls),
    path("api/health/", health, name="health"),
    path("api/auth/", include("accounts.urls")),
    path("api/seguridad/", include("seguridad.urls")),
    path("api/", include("rescue.urls")),
    path("api/", include("animals.urls")),
    path("api/", include("adoption.urls")),
    path("api/", include("funds.urls")),
    path("api/", include("commerce.urls")),
    path("api/", include("core.urls")),
]
