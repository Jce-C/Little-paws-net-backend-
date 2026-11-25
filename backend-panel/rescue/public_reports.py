"""Lectura pública acotada; no incluye contactos ni claves de gestión."""
from django.db.models import Q
from rest_framework.exceptions import ValidationError

from seguridad.models import PublicacionReporte
from .models import Reporte


PUBLIC_FIELDS = (
    "id_reporte", "descripcion", "tipo_reporte__nombre", "estado_reporte__nombre",
)
PAGE_SIZE = 20


def visible_reports():
    hidden = PublicacionReporte.objects.filter(oculta=True).values("reporte_id")
    return Reporte.objects.exclude(pk__in=hidden).order_by("-pk")


def public_report_page(params):
    cursor = params.get("antes", "")
    query = params.get("buscar", "").strip()
    if len(query) > 100:
        raise ValidationError({"buscar": "Usa como máximo 100 caracteres."})
    # IDs enteros de base de datos; no se aceptan URLs ni expresiones del cliente.
    if cursor and (not cursor.isascii() or not cursor.isdecimal() or
                   len(cursor) > 19 or not 0 < int(cursor) <= 9223372036854775807):
        raise ValidationError({"antes": "El cursor debe ser un identificador positivo válido."})
    reports = visible_reports()
    if cursor:
        reports = reports.filter(pk__lt=int(cursor))
    if query:
        reports = reports.filter(
            Q(descripcion__icontains=query) |
            Q(tipo_reporte__nombre__icontains=query) |
            Q(estado_reporte__nombre__icontains=query)
        )
    from .photo_views import foto_descriptor
    reports = reports.select_related('ciudad', 'tipo_reporte', 'estado_reporte', 'foto_ciudadana', 'casorescate__estado_caso', 'casorescate__fundacion__entidad')
    objects = list(reports.defer('foto_ciudadana__contenido')[:PAGE_SIZE + 1])
    rows = []
    for report in objects:
        case = getattr(report, 'casorescate', None)
        rows.append({'id_reporte': report.pk, 'descripcion': report.descripcion,
          'tipo_reporte__nombre': report.tipo_reporte.nombre, 'estado_reporte__nombre': report.estado_reporte.nombre,
          'ciudad': report.ciudad.nombre if report.ciudad else '', 'foto': foto_descriptor(report),
          'caso': None if case is None else {'id_caso': case.pk, 'fundacion_id': case.fundacion_id, 'fundacion': case.fundacion.entidad.nombre, 'estado': case.estado_caso.nombre}})
    has_more = len(rows) > PAGE_SIZE
    rows = rows[:PAGE_SIZE]
    return {
        "results": rows,
        "next_cursor": str(rows[-1]["id_reporte"]) if has_more else None,
    }
