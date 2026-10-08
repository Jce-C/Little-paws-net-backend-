"""API de consulta de catálogos; no permite modificarlos."""

from rest_framework import generics, permissions

from .models import TipoMaestro
from .serializers import TipoMaestroSerializer


class CatalogosView(generics.ListAPIView):
    serializer_class = TipoMaestroSerializer
    permission_classes = [permissions.AllowAny]
    queryset = TipoMaestro.objects.filter(activo=True).prefetch_related("valormaestro_set").order_by("nombre")
