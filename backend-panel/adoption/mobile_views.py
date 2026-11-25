"""Ficha pública de adopción: solo datos de mascotas disponibles y sin expediente."""
from django.shortcuts import get_object_or_404
from django.db.models import Value, OuterRef, Subquery
from django.db.models.functions import Coalesce, NullIf
from rest_framework import serializers
from django.utils import timezone
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from animals.models import CustodiaMascota
from animals.public_photos import foto_descriptor, galeria_descriptor
from animals.public_presentation import descriptor as presentacion_descriptor
from .consultas import disponibles_adopcion


class MascotaFichaPublicaView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, mascota_id):
        mascota = get_object_or_404(
            disponibles_adopcion().select_related("especie", "raza__especie", "tamano", "sexo", "foto_publica", "presentacion_publica"),
            pk=mascota_id,
        )
        custodia = get_object_or_404(
            CustodiaMascota.objects.select_related("fundacion__entidad", "fundacion__ciudad"),
            mascota=mascota, fecha_fin__isnull=True,
        )
        today = timezone.localdate()
        born = mascota.fecha_nacimiento
        months = None
        if born is not None and born <= today:
            months = (today.year - born.year) * 12 + today.month - born.month - (today.day < born.day)
            months = max(0, months)
        response = Response({
            "foto": foto_descriptor(mascota, custodia.fundacion_id),
            "presentacion": presentacion_descriptor(mascota, custodia.fundacion_id),
            "fotos": galeria_descriptor(mascota, custodia.fundacion_id),
            "id_mascota": mascota.pk,
            "nombre": mascota.nombre,
            "especie": mascota.especie_nombre,
            "raza": mascota.raza_nombre,
            "edad_meses": months,
            "edad_estimada": mascota.es_estimada,
            "tamano": mascota.tamano.nombre if mascota.tamano else None,
            "sexo": mascota.sexo.nombre if mascota.sexo else None,
            "estado": "En adopción",
            "organizacion": custodia.fundacion.entidad.nombre,
            "ciudad": custodia.fundacion.ciudad.nombre,
            "custodia_desde": custodia.fecha_inicio,
        })
        response["Cache-Control"] = "no-store"
        return response


class CatalogoCursorPagination(CursorPagination):
    """Límite fijo y posición estable, sin COUNT global ni orden editable."""

    page_size = 24
    ordering = "id_mascota"
    page_size_query_param = None


class CatalogoMovilView(APIView):
    """Catálogo por páginas; conserva la lista anterior para clientes existentes."""

    permission_classes = [AllowAny]

    def get(self, request):
        queryset = disponibles_adopcion().select_related("especie", "raza__especie", "foto_publica", "sexo", "tamano", "presentacion_publica").annotate(
            fundacion_foto=Subquery(CustodiaMascota.objects.filter(mascota_id=OuterRef("pk"), fecha_fin__isnull=True).values("fundacion_id")[:1]),
        )
        queryset = queryset.annotate(especie_publica=Coalesce(
            "especie__nombre", "raza__especie__nombre",
            NullIf("descripcion_especie", Value("")), Value("No identificada"),
        ))
        species = list(queryset.values_list("especie_publica", flat=True).order_by("especie_publica").distinct())
        selected = serializers.CharField(max_length=150, allow_blank=True).run_validation(request.query_params.get("especie", ""))
        if selected:
            queryset = queryset.filter(especie_publica=selected)
        paginator = CatalogoCursorPagination()
        mascotas = paginator.paginate_queryset(queryset, request, view=self)
        today = timezone.localdate()
        response = paginator.get_paginated_response([
            {
                "id_mascota": mascota.pk,
                "foto": foto_descriptor(mascota, mascota.fundacion_foto),
                "presentacion": presentacion_descriptor(mascota, mascota.fundacion_foto),
                "nombre": mascota.nombre,
                "especie": mascota.especie_nombre,
                "raza": mascota.raza_nombre,
                "sexo": mascota.sexo.nombre if mascota.sexo else None,
                "tamano": mascota.tamano.nombre if mascota.tamano else None,
                "estado": "En adopción",
                "edad_meses": max(0, (today.year - mascota.fecha_nacimiento.year) * 12 + today.month - mascota.fecha_nacimiento.month - (today.day < mascota.fecha_nacimiento.day)) if mascota.fecha_nacimiento and mascota.fecha_nacimiento <= today else None,
            }
            for mascota in mascotas
        ])
        response.data["species"] = species
        response["Cache-Control"] = "no-store"
        response["X-Content-Type-Options"] = "nosniff"
        return response
