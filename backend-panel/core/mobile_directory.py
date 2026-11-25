"""Public directory: verified organizations, never members or private contacts."""
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Clinica, Fundacion, Tienda
from seguridad.models import BajaAdministrativa
from .public_profiles import descriptor
from .public_logos import descriptor as logo_publico
from .help_programs import descriptor as programa_publico


class OrganizacionesPublicasView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        inactive = BajaAdministrativa.objects.filter(tipo="entidades", activo=False).values("objeto_id")
        rows = []
        for model, kind in ((Fundacion, "Fundación"), (Clinica, "Veterinaria"), (Tienda, "Tienda")):
            queryset = model.objects.select_related("entidad__perfil_publico", "entidad__logo_publico", "ciudad", *(("programa_ayuda",) if model is Fundacion else ())).filter(
                entidad__estado_verificacion__nombre="Verificada",
            ).exclude(pk__in=inactive).order_by("pk")[:100]
            rows.extend({
                "id": item.pk, "nombre": item.entidad.nombre, "tipo": kind,
                "ciudad": item.ciudad.nombre,
                "descripcion": getattr(item, "descripcion", "")[:1000],
                "direccion": getattr(item, "direccion", ""),
                "acepta_voluntarios": getattr(item, "acepta_voluntarios", False),
                "necesidades_ayuda": getattr(item, "necesidades_ayuda", "")[:1000],
                "perfil_publico": descriptor(item.entidad),
                "logo": logo_publico(item.entidad),
                "programa_ayuda": programa_publico(item) if kind == "Fundación" else None,
            } for item in queryset)
        response = Response(sorted(rows, key=lambda row: (row["nombre"].casefold(), row["id"])))
        response["Cache-Control"] = "no-store"
        return response
