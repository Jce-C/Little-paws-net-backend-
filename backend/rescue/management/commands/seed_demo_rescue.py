"""Carga ficticia e idempotente del proceso asignado a José Carlos."""

import secrets
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone

from accounts.models import Usuario
from animals.models import (
    AutorizacionExpediente, CustodiaMascota, HistorialMedico, Mascota, Raza,
)
from animals.services import (
    autorizar_veterinario, regenerar_qr, registrar_atencion, registrar_custodia,
)
from core.models import (
    CapacidadFundacion, Ciudad, EntidadMiembro, EntidadMiembroRol,
    EntidadVerificable, Fundacion, FundacionZona, Rol, ValorMaestro, Veterinario, Zona,
)
from rescue.models import (
    Apadrinamiento, CasoRescate, ConfirmacionAporte, HistorialEstadoApadrinamiento,
    HistorialEstadoCaso, HistorialEstadoReporte, Reporte, ReporteUbicacion, ZonaGeografica,
)
from rescue.services import aceptar_reporte
from rescue.sponsorship import confirmar_aporte, crear_compromiso


def _usuario(correo, nombre):
    usuario = Usuario.objects.filter(email=correo).first()
    return usuario or Usuario.objects.create_user(
        email=correo, nombre=nombre, password=secrets.token_urlsafe(24),
    )


class Command(BaseCommand):
    help = "Carga datos DEMO ficticios de rescate, apadrinamiento y expediente"

    @transaction.atomic
    def handle(self, *args, **options):
        if connection.vendor != "mysql" or connection.settings_dict["NAME"] != "little_paws_net_equipo":
            raise CommandError("La carga DEMO solo se permite en little_paws_net_equipo sobre MySQL")
        gestor = _usuario("demo.jose.gestor@example.invalid", "Gestor demo")
        usuario_vet = _usuario("demo.jose.vet@example.invalid", "Veterinaria demo")
        ciudad, _ = Ciudad.objects.get_or_create(nombre="Ciudad DEMO", departamento="DEMO")
        zona, _ = Zona.objects.get_or_create(ciudad=ciudad, nombre="Zona rescate DEMO")
        ZonaGeografica.objects.get_or_create(
            zona=zona,
            defaults={"poligono_wkt": (
                "MULTIPOLYGON(((-74.09 4.60,-74.07 4.60,-74.07 4.62,"
                "-74.09 4.62,-74.09 4.60)))"
            )},
        )
        verificada = ValorMaestro.objects.get(tipo__nombre="estado_verificacion", nombre="Verificada")
        fundacion = Fundacion.objects.filter(nit="DEMO-JOSE-001").first()
        if fundacion is None:
            entidad = EntidadVerificable.objects.create(
                nombre="Fundación DEMO de rescate", estado_verificacion=verificada,
            )
            fundacion = Fundacion.objects.create(
                entidad=entidad, ciudad=ciudad, nit="DEMO-JOSE-001",
            )
        FundacionZona.objects.get_or_create(fundacion=fundacion, zona=zona)
        CapacidadFundacion.objects.get_or_create(
            fundacion=fundacion,
            defaults={"cupos_totales": 10, "usuario_actualizador": gestor},
        )
        miembro, _ = EntidadMiembro.objects.get_or_create(entidad=fundacion.entidad, usuario=gestor)
        EntidadMiembroRol.objects.get_or_create(
            miembro=miembro, rol=Rol.objects.get(codigo="GESTOR_FUNDACION"),
        )
        veterinario = Veterinario.objects.filter(registro_profesional="DEMO-MAT-001").first()
        if veterinario is None:
            entidad_vet = EntidadVerificable.objects.create(
                nombre="Veterinaria DEMO", estado_verificacion=verificada,
            )
            veterinario = Veterinario.objects.create(
                entidad=entidad_vet, usuario_profesional=usuario_vet,
                registro_profesional="DEMO-MAT-001",
            )
        raza = Raza.objects.get(especie__nombre="Canino", nombre="Mestizo")
        estado_mascota = ValorMaestro.objects.get(tipo__nombre="estado_mascota", nombre="En rescate")
        estado_reporte = ValorMaestro.objects.get(tipo__nombre="estado_reporte", nombre="Pendiente")
        tipo_reporte = ValorMaestro.objects.get(tipo__nombre="tipo_reporte", nombre="Rescate")

        for numero in range(1, 26):
            reportante = _usuario(
                f"demo.jose.ciudadano.{numero:03d}@example.invalid",
                f"Ciudadano DEMO {numero:03d}",
            )
            descripcion = f"DEMO-JOSE-{numero:03d}: animal hallado en zona de prueba"
            reporte = Reporte.objects.filter(usuario_reportante=reportante, descripcion=descripcion).first()
            if reporte is None:
                mascota = Mascota.objects.create(
                    dueno=reportante, raza=raza, estado_mascota=estado_mascota,
                    nombre=f"Mascota DEMO {numero:03d}",
                )
                reporte = Reporte.objects.create(
                    usuario_reportante=reportante, mascota=mascota,
                    tipo_reporte=tipo_reporte, estado_reporte=estado_reporte,
                    descripcion=descripcion,
                )
                ReporteUbicacion.objects.create(
                    reporte=reporte, latitud="4.609710", longitud="-74.081750",
                )
                HistorialEstadoReporte.objects.create(
                    reporte=reporte, estado_nuevo=estado_reporte,
                    usuario_actor=reportante, observacion="Creación de reporte DEMO",
                )
            if numero > 5:
                continue
            caso = CasoRescate.objects.filter(reporte=reporte).first()
            if caso is None:
                caso = aceptar_reporte(
                    reporte_id=reporte.pk, fundacion_id=fundacion.pk,
                    usuario_actor_id=gestor.pk,
                )
            if not Apadrinamiento.objects.filter(reporte=reporte, usuario_padrino=reportante).exists():
                apadrinamiento = crear_compromiso(
                    reporte_id=reporte.pk, usuario_padrino_id=reportante.pk,
                    monto=Decimal("100.00"),
                )
                confirmar_aporte(
                    apadrinamiento_id=apadrinamiento.pk, usuario_confirmador_id=gestor.pk,
                    monto=Decimal("40.00"),
                )
            if numero <= 2 and not CustodiaMascota.objects.filter(mascota=reporte.mascota, fecha_fin__isnull=True).exists():
                registrar_custodia(caso_id=caso.pk, usuario_id=gestor.pk)
            if numero <= 2 and not HistorialMedico.objects.filter(mascota=reporte.mascota).exists():
                if not AutorizacionExpediente.objects.filter(
                    mascota=reporte.mascota, veterinario=veterinario,
                ).exists():
                    autorizar_veterinario(
                        mascota_id=reporte.mascota_id, veterinario_id=veterinario.pk,
                        usuario_id=gestor.pk,
                    )
                _, token = regenerar_qr(mascota_id=reporte.mascota_id, usuario_id=gestor.pk)
                registrar_atencion(
                    mascota_id=reporte.mascota_id, usuario_id=usuario_vet.pk,
                    token=token, detalle="Revisión médica DEMO sin datos reales",
                    fecha_atencion=timezone.now(),
                )

        modelos = (
            Usuario, Mascota, Reporte, ReporteUbicacion, HistorialEstadoReporte,
            CasoRescate, HistorialEstadoCaso, Apadrinamiento, ConfirmacionAporte,
            HistorialEstadoApadrinamiento, CustodiaMascota, AutorizacionExpediente,
            HistorialMedico,
        )
        total = sum(modelo.objects.count() for modelo in modelos)
        if total < 100:
            raise CommandError(f"Carga incompleta: solo {total} registros en tablas del proceso")
        self.stdout.write(self.style.SUCCESS(
            f"DEMO José: {Reporte.objects.count()} reportes, "
            f"{CasoRescate.objects.count()} casos, {total} registros del proceso"
        ))
