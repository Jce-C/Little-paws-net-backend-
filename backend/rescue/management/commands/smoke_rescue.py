"""Prueba real de cobertura y transición; revierte las filas creadas."""

from uuid import uuid4

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from accounts.models import Usuario
from core.models import (
    CapacidadFundacion, Ciudad, EntidadMiembro, EntidadMiembroRol,
    EntidadVerificable, Fundacion, FundacionZona, Rol, ValorMaestro, Zona,
)
from rescue.models import HistorialEstadoCaso, Reporte, ReporteUbicacion, ZonaGeografica
from rescue.services import aceptar_reporte, cerrar_caso, fundacion_cubre_reporte


class _FinPrueba(Exception):
    pass


class Command(BaseCommand):
    help = "Verifica cobertura espacial, aceptación, historial y cupos sin conservar registros"

    def handle(self, *args, **options):
        if connection.vendor != "mysql":
            raise CommandError("Esta prueba requiere MySQL")
        if connection.settings_dict["NAME"] != "little_paws_net_equipo":
            raise CommandError("Esta prueba solo puede ejecutarse en little_paws_net_equipo")
        sufijo = uuid4().hex[:12]
        try:
            with transaction.atomic():
                gestor = Usuario.objects.create_user(
                    email=f"smoke-{sufijo}@example.invalid", password=uuid4().hex,
                    nombre="Prueba de rescate",
                )
                ciudad = Ciudad.objects.create(nombre=f"Ciudad-{sufijo}", departamento="Prueba")
                zona = Zona.objects.create(ciudad=ciudad, nombre="Centro")
                ZonaGeografica.objects.create(
                    zona=zona,
                    poligono_wkt=(
                        "MULTIPOLYGON(((-74.09 4.60,-74.07 4.60,-74.07 4.62,"
                        "-74.09 4.62,-74.09 4.60)))"
                    ),
                )
                verificada = ValorMaestro.objects.get(tipo__nombre="estado_verificacion", nombre="Verificada")
                entidad = EntidadVerificable.objects.create(
                    nombre=f"Fundación-{sufijo}", estado_verificacion=verificada,
                )
                fundacion = Fundacion.objects.create(entidad=entidad, ciudad=ciudad, nit=f"TEST-{sufijo}")
                FundacionZona.objects.create(fundacion=fundacion, zona=zona)
                capacidad = CapacidadFundacion.objects.create(
                    fundacion=fundacion, cupos_totales=1, usuario_actualizador=gestor,
                )
                miembro = EntidadMiembro.objects.create(entidad=entidad, usuario=gestor)
                EntidadMiembroRol.objects.create(
                    miembro=miembro, rol=Rol.objects.get(codigo="GESTOR_FUNDACION"),
                )
                reporte = Reporte.objects.create(
                    usuario_reportante=gestor,
                    estado_reporte=ValorMaestro.objects.get(tipo__nombre="estado_reporte", nombre="Pendiente"),
                    tipo_reporte=ValorMaestro.objects.get(tipo__nombre="tipo_reporte", nombre="Rescate"),
                    descripcion="Prueba temporal de cobertura",
                )
                ReporteUbicacion.objects.create(
                    reporte=reporte, latitud="4.609710", longitud="-74.081750",
                )
                if not fundacion_cubre_reporte(fundacion.pk, reporte.pk):
                    raise CommandError("La cobertura espacial no reconoció el punto interior")
                caso = aceptar_reporte(
                    reporte_id=reporte.pk, fundacion_id=fundacion.pk,
                    usuario_actor_id=gestor.pk,
                )
                capacidad.refresh_from_db()
                if capacidad.cupos_ocupados != 1:
                    raise CommandError("La aceptación no ocupó un cupo")
                cerrar_caso(caso_id=caso.pk, usuario_actor_id=gestor.pk, nuevo_estado="Cerrado")
                capacidad.refresh_from_db()
                if capacidad.cupos_ocupados != 0:
                    raise CommandError("El cierre no liberó el cupo")
                if HistorialEstadoCaso.objects.filter(caso=caso).count() != 2:
                    raise CommandError("Falta la trazabilidad del caso")
                raise _FinPrueba
        except _FinPrueba:
            self.stdout.write(self.style.SUCCESS("Rescate MySQL: cobertura, autorización, cupos e historial OK; filas revertidas"))
