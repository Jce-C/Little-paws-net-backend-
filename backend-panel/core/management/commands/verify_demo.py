"""Prueba de humo HTTP/negocio sobre la demo, siempre con rollback."""

import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from rest_framework.test import APIClient

from animals.models import Mascota
from commerce.models import Producto
from core.models import Fundacion, ValorMaestro, Veterinario
from funds.models import FondoExterno
from rescue.models import Reporte


class Command(BaseCommand):
    help = "Verifica flujos de la API sin conservar los registros de prueba"

    def handle(self, *args, **options):
        clave = os.getenv("LPN_DEMO_PASSWORD")
        if not clave:
            raise CommandError("Configure LPN_DEMO_PASSWORD para probar las cuentas demo")
        cliente = APIClient(HTTP_HOST="localhost")
        pruebas = 0
        reportes_antes = Reporte.objects.count()

        def comprobar(respuesta, esperado, etiqueta):
            nonlocal pruebas
            if respuesta.status_code != esperado:
                raise CommandError(f"{etiqueta}: HTTP {respuesta.status_code}; {respuesta.data}")
            pruebas += 1
            return respuesta.data

        def entrar(numero):
            respuesta = cliente.post(
                "/api/auth/token/",
                {"email": f"demo{numero:02d}@example.invalid", "password": clave},
                format="json",
            )
            datos = comprobar(respuesta, 200, f"login demo{numero:02d}")
            cliente.credentials(HTTP_AUTHORIZATION="Bearer " + datos["access"])

        with transaction.atomic():
            comprobar(cliente.post(
                "/api/auth/registro/",
                {"email": "nuevo-demo@example.invalid", "nombre": "Cuenta de prueba reversible",
                 "password": "CuentaNuevaDemo-2026!"}, format="json",
            ), 201, "registrar usuario con contraseña validada")
            tipo = ValorMaestro.objects.get(tipo__nombre="tipo_reporte", nombre="Rescate")
            anonimo = comprobar(cliente.post(
                "/api/reportes/",
                {"tipo_reporte": tipo.pk, "descripcion": "Reporte anónimo reversible",
                 "latitud": "4.600000", "longitud": "-74.080000"}, format="json",
            ), 201, "crear reporte anónimo")
            ruta_anonima = f"/api/reportes/{anonimo['id_reporte']}/gestion-anonima/"
            comprobar(cliente.post(
                ruta_anonima, {"codigo_gestion": "clave-incorrecta", "cerrar": True}, format="json",
            ), 403, "rechazar clave anónima inválida")
            comprobar(cliente.post(
                ruta_anonima,
                {"codigo_gestion": anonimo["codigo_gestion"], "descripcion": "Reporte anónimo corregido"},
                format="json",
            ), 200, "editar reporte anónimo pendiente")
            comprobar(cliente.post(
                ruta_anonima, {"codigo_gestion": anonimo["codigo_gestion"], "cerrar": True},
                format="json",
            ), 200, "cerrar reporte anónimo")
            comprobar(cliente.post(
                ruta_anonima,
                {"codigo_gestion": anonimo["codigo_gestion"], "descripcion": "No debe cambiar"},
                format="json",
            ), 409, "impedir cambios tras el cierre")
            entrar(20)
            nuevo = comprobar(cliente.post(
                "/api/reportes/",
                {
                    "tipo_reporte": tipo.pk,
                    "descripcion": "Verificación reversible de API",
                    "latitud": "4.600000", "longitud": "-74.080000",
                }, format="json",
            ), 201, "crear reporte")
            reporte_id = nuevo["id_reporte"]
            fundacion = Fundacion.objects.get(entidad__nombre="Fundación demo 1")
            comprobar(cliente.post(
                f"/api/reportes/{reporte_id}/aceptar/",
                {"id_fundacion": fundacion.pk}, format="json",
            ), 403, "rechazar aceptación no autorizada")

            entrar(1)
            comprobar(cliente.post(
                f"/api/reportes/{reporte_id}/aceptar/",
                {"id_fundacion": fundacion.pk}, format="json",
            ), 201, "aceptar con permiso y cobertura")
            mascota = Mascota.objects.get(nombre="Mascota demo 01")
            vet = Veterinario.objects.get(registro_profesional="DEMO-VET-0001")
            comprobar(cliente.post(
                f"/api/mascotas/{mascota.pk}/autorizaciones/",
                {"id_veterinario": vet.pk}, format="json",
            ), 201, "autorizar veterinario")
            qr = comprobar(cliente.post(
                f"/api/mascotas/{mascota.pk}/qr/", {}, format="json",
            ), 201, "crear QR revocable")
            entrar(5)
            comprobar(cliente.post(
                f"/api/qr/{qr['codigo']}/atenciones/",
                {"detalle": "Prueba reversible", "fecha_atencion": timezone.now().isoformat()},
                format="json",
            ), 201, "escritura médica autorizada")

            entrar(20)
            disponible = Mascota.objects.get(nombre="Mascota demo 11")
            solicitud = comprobar(cliente.post(
                "/api/adopcion/solicitudes/", {"id_mascota": disponible.pk}, format="json",
            ), 201, "solicitar adopción")
            entrar(1)
            comprobar(cliente.post(
                f"/api/seguridad/asignaciones/adopcion/{solicitud['id_solicitud_adopcion']}/tomar/",
                {}, format="json",
            ), 200, "asignar revisión de adopción")
            comprobar(cliente.post(
                f"/api/adopcion/solicitudes/{solicitud['id_solicitud_adopcion']}/resolver/",
                {"id_fundacion": fundacion.pk, "aprobar": True}, format="json",
            ), 200, "aprobar adopción y cerrar otras")

            entrar(20)
            producto = Producto.objects.get(nombre="Producto demo 01")
            pedido = comprobar(cliente.post(
                "/api/pedidos/",
                {"id_tienda": producto.tienda_id,
                 "lineas": [{"id_producto": producto.pk, "cantidad": 2}]}, format="json",
            ), 201, "iniciar pedido")
            comprobar(cliente.get(
                f"/api/pedidos/{pedido['id_pedido']}/"
            ), 200, "consultar total referencial")
            fondo = FondoExterno.objects.get(nombre="Fondo externo demo")
            comprobar(cliente.post(
                "/api/fondos/donaciones/",
                {"id_fondo_externo": fondo.pk, "monto_comprometido": "25000.00"}, format="json",
            ), 201, "compromiso con fondo externo")
            compromiso = comprobar(cliente.post(
                "/api/apadrinamientos/",
                {"id_reporte": Reporte.objects.get(descripcion="Reporte sintético de rescate 01").pk,
                 "monto_comprometido": "50000.00"}, format="json",
            ), 201, "compromiso de apadrinamiento")
            cuenta = comprobar(cliente.get(
                f"/api/apadrinamientos/{compromiso['id_apadrinamiento']}/cuenta/"
            ), 200, "revelar cuenta solo al padrino")
            if cuenta["numero_cuenta"] != "000123456789":
                raise CommandError("La cuenta demo no se descifró correctamente")
            comprobar(cliente.post(
                f"/api/apadrinamientos/{compromiso['id_apadrinamiento']}/declaraciones/",
                {
                    "monto_declarado": "25000.00",
                    "referencia": "DEMO-SIN-TRANSFERENCIA",
                    "fecha_transferencia_declarada": timezone.now().isoformat(),
                }, format="json",
            ), 201, "declaración no confirmatoria del padrino")
            entrar(1)
            comprobar(cliente.post(
                f"/api/seguridad/asignaciones/aporte/{compromiso['id_apadrinamiento']}/tomar/",
                {}, format="json",
            ), 200, "asignar revisión de aporte")
            comprobar(cliente.post(
                f"/api/apadrinamientos/{compromiso['id_apadrinamiento']}/confirmaciones/",
                {"monto_confirmado": "25000.00"}, format="json",
            ), 201, "confirmación exclusiva de fundación")
            transaction.set_rollback(True)

        if Reporte.objects.count() != reportes_antes:
            raise CommandError("La prueba dejó datos persistidos")
        self.stdout.write(self.style.SUCCESS(f"Verificación correcta: {pruebas} pasos; cambios revertidos"))
