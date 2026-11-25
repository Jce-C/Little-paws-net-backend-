from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog
from django.views.decorators.cache import never_cache
from seguridad.web.views import bienvenida


def health(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("jsi18n/", never_cache(JavaScriptCatalog.as_view(packages=["seguridad"])), name="javascript-catalog"),
    path("", bienvenida, name="landing"),
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
