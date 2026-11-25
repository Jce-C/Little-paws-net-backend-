"""Datos sintéticos e idempotentes para una instalación de demostración.

No usar contra una base de producción. Todos los correos terminan en el dominio
reservado example.invalid y la contraseña procede de una variable local.
"""

import os
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from accounts.models import Usuario
from adoption.models import SolicitudAdopcion
from animals.models import CustodiaMascota, Especie, HistorialMedico, Mascota, Raza
from animals.services import autorizar_veterinario, regenerar_qr, registrar_atencion
from commerce.models import (
    AlianzaVeterinaria, DetallePedido, EspacioPublicitario, PedidoIniciado,
    Producto, ReporteModerado, TarifaPublicacion,
)
from core.crypto import cifrar
from core.models import (
    Anunciante, ArchivoDigital, CapacidadFundacion, Ciudad, Clinica,
    DocumentoValidacion, EntidadMiembro, EntidadMiembroRol,
    EntidadVerificable, Fundacion, FundacionZona, Notificacion, Permiso, Rol, RolPermiso,
    SolicitudValidacion, Tienda, UsuarioRol, ValorMaestro, Veterinario, Zona,
)
from funds.models import (
    DistribucionReportadaFondo, DonacionGeneral, FondoExterno, SolicitudEmergencia,
)
from geography.models import ReporteUbicacion, ZonaGeografica
from rescue.models import (
    Apadrinamiento, CasoRescate, ConfirmacionAporte, CuentaFundacion,
    DeclaracionTransferencia, Reporte,
)
from rescue.services import aceptar_reporte
from rescue.sponsorship import confirmar_aporte
from seguridad.autorizacion import puede
from seguridad.models import AsignacionFondo
from seguridad.servicios import tomar


def valor(tipo, nombre):
    return ValorMaestro.objects.get(tipo__nombre=tipo, nombre=nombre)


class Command(BaseCommand):
    help = "Crea más de 100 registros sintéticos relacionados sin duplicarlos"

    @transaction.atomic
    def handle(self, *args, **options):
        clave = os.getenv("LPN_DEMO_PASSWORD")
        if not clave or len(clave) < 12:
            raise CommandError("Configure LPN_DEMO_PASSWORD (mínimo 12 caracteres) solo para la demo")
        if Usuario.objects.filter(email__in=[f"demo{i:02d}@example.invalid" for i in range(1, 21)], is_active=False).exists():
            raise CommandError("Existen cuentas demo desactivadas. No se reactivan: use una base de demostración aislada")

        usuarios = []
        for i in range(1, 21):
            email = f"demo{i:02d}@example.invalid"
            usuario = Usuario.objects.filter(email=email).first()
            if usuario is None:
                usuario = Usuario.objects.create_user(
                    email=email, password=clave, nombre=f"Usuario demo {i:02d}",
                    telefono=f"300555{i:04d}",
                )
            usuarios.append(usuario)
            UsuarioRol.objects.get_or_create(usuario=usuario, rol=Rol.objects.get(codigo="CIUDADANO"))

        ciudad, _ = Ciudad.objects.get_or_create(nombre="Bogotá", departamento="Bogotá D.C.")
        zona, _ = Zona.objects.get_or_create(ciudad=ciudad, nombre="Zona demo central")
        ZonaGeografica.objects.get_or_create(
            zona=zona,
            defaults={"poligono_wkt": "MULTIPOLYGON(((-75 4,-73 4,-73 5,-75 5,-75 4)))"},
        )
        verificada = valor("estado_verificacion", "Verificada")
        rol_fundacion = Rol.objects.get(codigo="GESTOR_RESCATES")
        apoyo_demo, _ = Rol.objects.get_or_create(codigo="APOYO_DEMO", defaults={
            "nombre": "Autorizaciones de la demo sintética", "ambito": "ENTIDAD"})
        RolPermiso.objects.get_or_create(rol=apoyo_demo, permiso=Permiso.objects.get(codigo="expediente.autorizar"))
        fundaciones = []
        for i in range(2):
            entidad, _ = EntidadVerificable.objects.get_or_create(
                nombre=f"Fundación demo {i + 1}", defaults={"estado_verificacion": verificada}
            )
            fundacion, _ = Fundacion.objects.get_or_create(
                entidad=entidad,
                defaults={"nit": f"90000000{i + 1}", "ciudad": ciudad, "descripcion": "Entidad de prueba"},
            )
            CapacidadFundacion.objects.get_or_create(
                fundacion=fundacion,
                defaults={"cupos_totales": 30, "cupos_ocupados": 0, "usuario_actualizador": usuarios[i]},
            )
            FundacionZona.objects.get_or_create(fundacion=fundacion, zona=zona, defaults={"activo": True})
            miembro, _ = EntidadMiembro.objects.get_or_create(entidad=entidad, usuario=usuarios[i])
            EntidadMiembroRol.objects.get_or_create(miembro=miembro, rol=rol_fundacion)
            for codigo_rol in ("GESTOR_ADOPCIONES", "GESTOR_APORTES"):
                EntidadMiembroRol.objects.get_or_create(miembro=miembro, rol=Rol.objects.get(codigo=codigo_rol))
            EntidadMiembroRol.objects.get_or_create(miembro=miembro, rol=apoyo_demo)
            fundaciones.append(fundacion)
        if not CuentaFundacion.objects.filter(fundacion=fundaciones[0]).exists():
            CuentaFundacion.objects.create(
                fundacion=fundaciones[0],
                numero_cuenta_cifrado=cifrar("000123456789"),
                numero_cuenta_ultimos4="6789",
                banco="Banco ficticio de demostración",
                tipo_cuenta="Ahorros",
                titular="Fundación demo 1 — CUENTA SIMULADA",
            )

        especie, _ = Especie.objects.get_or_create(nombre="Perro")
        raza, _ = Raza.objects.get_or_create(especie=especie, nombre="Mestizo")
        mascotas = []
        for i in range(15):
            estado = "En rescate" if i < 10 else "En adopción"
            mascota, _ = Mascota.objects.get_or_create(
                nombre=f"Mascota demo {i + 1:02d}",
                defaults={
                    "dueno": None, "raza": raza,
                    "estado_mascota": valor("estado_mascota", estado),
                },
            )
            if mascota.dueno_id is not None:
                mascota.dueno = None
                mascota.save(update_fields=["dueno"])
            mascotas.append(mascota)

        reportes = []
        for i in range(25):
            descripcion = f"Reporte sintético de rescate {i + 1:02d}"
            reporte, _ = Reporte.objects.get_or_create(
                descripcion=descripcion,
                defaults={
                    "usuario_reportante": usuarios[(i + 2) % 20],
                    "codigo_gestion_hash": "",
                    "estado_reporte": valor("estado_reporte", "Pendiente"),
                    "tipo_reporte": valor("tipo_reporte", "Rescate"),
                    "mascota": mascotas[i % 15],
                },
            )
            ReporteUbicacion.objects.get_or_create(
                reporte=reporte,
                defaults={
                    "latitud": Decimal("4.600000") + Decimal(i) / Decimal("10000"),
                    "longitud": Decimal("-74.080000") + Decimal(i) / Decimal("10000"),
                },
            )
            reportes.append(reporte)

        for i, reporte in enumerate(reportes[:10]):
            fundacion = fundaciones[i % 2]
            caso = CasoRescate.objects.filter(reporte=reporte).first()
            if caso is None:
                caso = aceptar_reporte(
                    reporte_id=reporte.pk,
                    fundacion_id=fundacion.pk,
                    usuario_actor_id=usuarios[i % 2].pk,
                )
            if not CustodiaMascota.objects.filter(mascota=mascotas[i], fecha_fin__isnull=True).exists():
                CustodiaMascota.objects.create(
                    mascota=mascotas[i], fundacion=fundacion, caso=caso,
                    fecha_inicio=timezone.now(), usuario_registrador=usuarios[i % 2],
                )

        for i in range(15):
            if i < 5 and not CustodiaMascota.objects.filter(
                mascota=mascotas[10 + i], fecha_fin__isnull=True
            ).exists():
                CustodiaMascota.objects.create(
                    mascota=mascotas[10 + i], fundacion=fundaciones[0],
                    fecha_inicio=timezone.now(), usuario_registrador=usuarios[0],
                )
            SolicitudAdopcion.objects.get_or_create(
                mascota=mascotas[10 + i % 5], usuario_adoptante=usuarios[(i + 4) % 20],
                defaults={"estado_adopcion": valor("estado_adopcion", "Pendiente")},
            )
            Apadrinamiento.objects.get_or_create(
                reporte=reportes[i % 10], usuario_padrino=usuarios[(i + 5) % 20],
                defaults={
                    "estado_apadrinamiento": valor("estado_apadrinamiento", "En espera"),
                    "monto_comprometido": Decimal("50000.00") + Decimal(i * 1000),
                },
            )
        primero = Apadrinamiento.objects.get(reporte=reportes[0], usuario_padrino=usuarios[5])
        if not DeclaracionTransferencia.objects.filter(apadrinamiento=primero).exists():
            DeclaracionTransferencia.objects.create(
                apadrinamiento=primero,
                monto_declarado=Decimal("25000.00"),
                referencia_cifrada=cifrar("DEMO-REFERENCIA-SIN-VALOR"),
                fecha_transferencia_declarada=timezone.now(),
            )
        if not ConfirmacionAporte.objects.filter(apadrinamiento=primero).exists():
            if not puede(usuarios[0], "aporte.confirmar", entidad_id=fundaciones[0].pk, objeto_id=primero.pk):
                tomar(usuarios[0], "aporte", primero.pk)
            confirmar_aporte(
                apadrinamiento_id=primero.pk,
                usuario_confirmador_id=usuarios[0].pk,
                monto=Decimal("25000.00"),
            )

        entidad_fondo, _ = EntidadVerificable.objects.get_or_create(
            nombre="Administradora fondo demo", defaults={"estado_verificacion": verificada}
        )
        fondo, _ = FondoExterno.objects.get_or_create(
            nombre="Fondo externo demo",
            defaults={
                "entidad": entidad_fondo, "entidad_administradora": "Administradora fondo demo",
                "tipo_fondo": valor("tipo_fondo", "Emergencias"),
                "estado_fondo": valor("estado_fondo", "Activo"),
            },
        )
        miembro_fondo, _ = EntidadMiembro.objects.get_or_create(
            entidad=entidad_fondo, usuario=usuarios[2]
        )
        EntidadMiembroRol.objects.get_or_create(
            miembro=miembro_fondo, rol=Rol.objects.get(codigo="GESTOR_FONDO")
        )
        AsignacionFondo.objects.get_or_create(fondo=fondo, usuario=usuarios[2])
        for i in range(12):
            DonacionGeneral.objects.get_or_create(
                fondo_externo=fondo, usuario_donante=usuarios[i],
                defaults={
                    "estado_donacion": valor("estado_donacion", "Comprometida"),
                    "monto_comprometido": Decimal("20000.00") + Decimal(i * 500),
                },
            )
        for i in range(4):
            DistribucionReportadaFondo.objects.get_or_create(
                fondo_externo=fondo, fundacion=fundaciones[i % 2],
                criterio=f"Distribución demo {i + 1}",
                defaults={
                    "estado_distribucion": valor("estado_distribucion", "Reportada"),
                    "monto_reportado": Decimal("100000.00") + Decimal(i * 5000),
                    "fecha_distribucion": timezone.now(),
                },
            )
        SolicitudEmergencia.objects.get_or_create(
            fundacion=fundaciones[0], fondo_externo=fondo,
            motivo="Solicitud sintética de alimento y atención veterinaria",
            defaults={
                "estado_emergencia": valor("estado_emergencia", "Pendiente"),
                "monto_solicitado": Decimal("150000.00"),
            },
        )

        entidad_tienda, _ = EntidadVerificable.objects.get_or_create(
            nombre="Tienda aliada demo", defaults={"estado_verificacion": verificada}
        )
        tienda, _ = Tienda.objects.get_or_create(
            entidad=entidad_tienda,
            defaults={"ciudad": ciudad, "direccion": "Calle demo 1", "whatsapp": "3005550000"},
        )
        miembro_tienda, _ = EntidadMiembro.objects.get_or_create(
            entidad=entidad_tienda, usuario=usuarios[3]
        )
        for codigo_rol in ("GESTOR_CATALOGO", "GESTOR_PEDIDOS"):
            EntidadMiembroRol.objects.get_or_create(miembro=miembro_tienda, rol=Rol.objects.get(codigo=codigo_rol))
        entidad_vet, _ = EntidadVerificable.objects.get_or_create(
            nombre="Veterinaria demo", defaults={"estado_verificacion": verificada}
        )
        Veterinario.objects.get_or_create(
            entidad=entidad_vet,
            defaults={
                "usuario_profesional": usuarios[4],
                "registro_profesional": "DEMO-VET-0001",
                "especialidad": "Medicina general",
            },
        )
        miembro_vet, _ = EntidadMiembro.objects.get_or_create(
            entidad=entidad_vet, usuario=usuarios[4]
        )
        EntidadMiembroRol.objects.get_or_create(
            miembro=miembro_vet, rol=Rol.objects.get(codigo="VETERINARIO")
        )
        vet = Veterinario.objects.get(entidad=entidad_vet)
        if not HistorialMedico.objects.filter(mascota=mascotas[0]).exists():
            autorizar_veterinario(
                mascota_id=mascotas[0].pk,
                veterinario_id=vet.pk,
                usuario_otorgante_id=usuarios[0].pk,
            )
            _, token = regenerar_qr(mascota_id=mascotas[0].pk, usuario_creador_id=usuarios[0].pk)
            registrar_atencion(
                token_qr=token, usuario_veterinario_id=usuarios[4].pk,
                detalle="Valoración clínica sintética; sin datos de un animal real.",
                fecha_atencion=timezone.now(),
            )

        archivo_validacion, _ = ArchivoDigital.objects.get_or_create(
            storage_key="demo_assets/validacion.txt",
            defaults={
                "mime_type": "text/plain", "tamano_bytes": 83,
                "visibilidad": ArchivoDigital.Visibilidad.PRIVADO,
                "usuario_cargador": usuarios[0],
            },
        )
        validacion, validacion_creada = SolicitudValidacion.objects.get_or_create(
            entidad=fundaciones[0].entidad,
            usuario_solicitante=usuarios[0],
            defaults={
                "usuario_validador": usuarios[5],
                "estado_solicitud": valor("estado_solicitud_validacion", "Pendiente"),
            },
        )
        if validacion_creada:
            validacion.estado_solicitud = valor("estado_solicitud_validacion", "Aprobada")
            validacion.fecha_resolucion = timezone.now()
            validacion.save(update_fields=["estado_solicitud", "fecha_resolucion"])
        DocumentoValidacion.objects.get_or_create(
            archivo=archivo_validacion,
            defaults={"solicitud": validacion, "usuario_cargador": usuarios[0]},
        )

        entidad_clinica, _ = EntidadVerificable.objects.get_or_create(
            nombre="Clínica veterinaria demo", defaults={"estado_verificacion": verificada}
        )
        clinica, _ = Clinica.objects.get_or_create(
            entidad=entidad_clinica,
            defaults={"ciudad": ciudad, "direccion": "Carrera demo 2"},
        )
        AlianzaVeterinaria.objects.get_or_create(
            clinica=clinica,
            descripcion="Alianza sintética de consulta básica",
            defaults={
                "nivel_alianza": valor("nivel_alianza", "Básica"),
                "estado_alianza": valor("estado_alianza", "Activa"),
                "tarifa": Decimal("0.00"),
                "fecha_inicio": timezone.localdate(),
                "fecha_fin": timezone.localdate() + timedelta(days=90),
            },
        )
        TarifaPublicacion.objects.get_or_create(
            tienda=tienda, concepto="Tarifa sintética de catálogo",
            defaults={
                "tipo_tarifa": valor("tipo_tarifa", "Publicación"),
                "monto": Decimal("0.00"),
                "fecha_inicio": timezone.localdate(),
                "fecha_fin": timezone.localdate() + timedelta(days=90),
            },
        )
        entidad_anunciante, _ = EntidadVerificable.objects.get_or_create(
            nombre="Anunciante demo", defaults={"estado_verificacion": verificada}
        )
        anunciante, _ = Anunciante.objects.get_or_create(
            entidad=entidad_anunciante,
            defaults={"nit_documento": "DEMO-ANUNCIANTE-1", "descripcion": "Solo prueba"},
        )
        archivo_banner, _ = ArchivoDigital.objects.get_or_create(
            storage_key="demo_assets/banner.svg",
            defaults={
                "mime_type": "image/svg+xml", "tamano_bytes": 231,
                "visibilidad": ArchivoDigital.Visibilidad.PUBLICO,
                "usuario_cargador": usuarios[5],
            },
        )
        EspacioPublicitario.objects.get_or_create(
            anunciante=anunciante, archivo=archivo_banner,
            defaults={
                "tipo_publicidad": valor("tipo_publicidad", "Banner"),
                "estado_publicidad": valor("estado_publicidad", "Aprobada"),
                "fecha_inicio": timezone.now(),
                "fecha_fin": timezone.now() + timedelta(days=30),
                "url_destino": "https://example.invalid/anuncio-demo",
                "usuario_revisor": usuarios[5], "fecha_decision": timezone.now(),
            },
        )
        ReporteModerado.objects.get_or_create(
            reporte=reportes[0], usuario_moderador=usuarios[5],
            defaults={"resultado_moderacion": valor("resultado_moderacion", "Aprobado")},
        )
        productos = []
        for i in range(15):
            producto, _ = Producto.objects.get_or_create(
                tienda=tienda, nombre=f"Producto demo {i + 1:02d}",
                defaults={
                    "categoria_producto": valor("categoria_producto", "Alimentos"),
                    "tipo_producto": valor("tipo_producto", "Alimento seco"),
                    "estado_producto": valor("estado_producto", "Disponible"),
                    "precio": Decimal("12000.00") + Decimal(i * 1000),
                    "existencias": 50,
                },
            )
            productos.append(producto)
        for i in range(8):
            pedido, _ = PedidoIniciado.objects.get_or_create(
                tienda=tienda, usuario_cliente=usuarios[(i + 10) % 20],
                defaults={"estado_pedido": valor("estado_pedido", "Iniciado")},
            )
            DetallePedido.objects.get_or_create(
                pedido=pedido, tienda=tienda, producto=productos[i],
                defaults={"cantidad": i % 3 + 1, "precio_referencia": productos[i].precio},
            )
        for i in range(10):
            Notificacion.objects.get_or_create(
                usuario=usuarios[i],
                tipo_notificacion=valor("tipo_notificacion", "Caso aceptado"),
                contenido=f"Notificación de demostración {i + 1:02d}",
            )

        conteos = {
            "usuarios": Usuario.objects.filter(email__endswith="@example.invalid").count(),
            "mascotas": Mascota.objects.filter(nombre__startswith="Mascota demo").count(),
            "reportes": Reporte.objects.filter(descripcion__startswith="Reporte sintético").count(),
            "casos": CasoRescate.objects.filter(reporte__descripcion__startswith="Reporte sintético").count(),
            "solicitudes_adopcion": SolicitudAdopcion.objects.filter(
                mascota__nombre__startswith="Mascota demo"
            ).count(),
            "apadrinamientos": Apadrinamiento.objects.filter(
                reporte__descripcion__startswith="Reporte sintético"
            ).count(),
            "donaciones": DonacionGeneral.objects.filter(fondo_externo=fondo).count(),
            "productos": Producto.objects.filter(tienda=tienda).count(),
            "pedidos": PedidoIniciado.objects.filter(tienda=tienda).count(),
        }
        total = sum(conteos.values())
        if total < 100:
            raise CommandError(f"Solo se obtuvieron {total} registros demo")
        self.stdout.write(self.style.SUCCESS(f"Datos demo listos: {total} registros principales"))
        for nombre, cantidad in conteos.items():
            self.stdout.write(f"  {nombre}: {cantidad}")
