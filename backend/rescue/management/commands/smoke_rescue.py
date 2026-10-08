"""Prueba real de cobertura y transición; revierte las filas creadas."""

from uuid import uuid4
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone

from accounts.models import Usuario
from animals.models import HistorialMedico, Raza
from animals.services import (
    autorizar_veterinario, regenerar_qr, registrar_atencion,
    registrar_custodia, registrar_mascota_caso,
)
from core.models import (
    CapacidadFundacion, Ciudad, EntidadMiembro, EntidadMiembroRol,
    EntidadVerificable, Fundacion, FundacionZona, Rol, ValorMaestro, Veterinario, Zona,
)
from rescue.models import (
    ConfirmacionAporte, HistorialEstadoCaso, Reporte, ReporteUbicacion, ZonaGeografica,
)
from rescue.services import aceptar_reporte, cerrar_caso, fundacion_cubre_reporte
from rescue.sponsorship import confirmar_aporte, crear_compromiso


class _FinPrueba(Exception):
    pass


class Command(BaseCommand):
    help = "Verifica rescate, apadrinamiento y expediente en MySQL sin conservar filas"

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
                padrino = Usuario.objects.create_user(
                    email=f"padrino-{sufijo}@example.invalid", password=uuid4().hex,
                    nombre="Padrino de prueba",
                )
                usuario_vet = Usuario.objects.create_user(
                    email=f"vet-{sufijo}@example.invalid", password=uuid4().hex,
                    nombre="Veterinario de prueba",
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
                mascota = registrar_mascota_caso(
                    caso_id=caso.pk, usuario_id=gestor.pk,
                    datos={"raza": Raza.objects.get(especie__nombre="Canino", nombre="Mestizo"),
                           "nombre": "Mascota temporal"},
                )
                registrar_custodia(caso_id=caso.pk, usuario_id=gestor.pk)
                entidad_vet = EntidadVerificable.objects.create(
                    nombre=f"Veterinario-{sufijo}", estado_verificacion=verificada,
                )
                veterinario = Veterinario.objects.create(
                    entidad=entidad_vet, usuario_profesional=usuario_vet,
                    registro_profesional=f"MAT-{sufijo}",
                )
                autorizar_veterinario(
                    mascota_id=mascota.pk, veterinario_id=veterinario.pk, usuario_id=gestor.pk,
                )
                _, codigo_qr = regenerar_qr(mascota_id=mascota.pk, usuario_id=gestor.pk)
                registrar_atencion(
                    mascota_id=mascota.pk, usuario_id=usuario_vet.pk,
                    token=codigo_qr, detalle="Control médico de prueba",
                    fecha_atencion=timezone.now(),
                )
                if HistorialMedico.objects.filter(mascota=mascota).count() != 1:
                    raise CommandError("No se creó la anotación médica")
                compromiso = crear_compromiso(
                    reporte_id=reporte.pk, usuario_padrino_id=padrino.pk,
                    monto=Decimal("100.00"),
                )
                confirmar_aporte(
                    apadrinamiento_id=compromiso.pk, usuario_confirmador_id=gestor.pk,
                    monto=Decimal("40.00"),
                )
                if ConfirmacionAporte.objects.filter(apadrinamiento=compromiso).count() != 1:
                    raise CommandError("No se confirmó el aporte")
                cerrar_caso(caso_id=caso.pk, usuario_actor_id=gestor.pk, nuevo_estado="Cerrado")
                capacidad.refresh_from_db()
                if capacidad.cupos_ocupados != 0:
                    raise CommandError("El cierre no liberó el cupo")
                if HistorialEstadoCaso.objects.filter(caso=caso).count() != 2:
                    raise CommandError("Falta la trazabilidad del caso")
                raise _FinPrueba
        except _FinPrueba:
            self.stdout.write(self.style.SUCCESS(
                "MySQL: rescate, apadrinamiento y expediente OK; filas de prueba revertidas"
            ))
