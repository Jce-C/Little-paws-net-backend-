import os
from datetime import timedelta
from decimal import Decimal
from tempfile import TemporaryDirectory
from unittest.mock import patch

from cryptography.fernet import Fernet
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from animals.models import Mascota, Raza, Especie, HistorialMedico, AutorizacionExpediente, CodigoQRExpediente
from adoption.models import SolicitudAdopcion
from core.models import Ciudad, Fundacion, Tienda, Veterinario, UsuarioRol, Rol, SolicitudValidacion
from rescue.models import CuentaFundacion, Reporte, CasoRescate
from commerce.models import Producto, PedidoIniciado, DetallePedido
from . import flujos as f, models as m, documentos
from .tests import BaseRBAC, cuenta, entidad, valor, miembro_con_rol
from .servicios import tomar, devolver, gestionar_miembro


class FlujosTests(BaseRBAC):
    def setUp(self):
        self.temporal = TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        ajuste = override_settings(LPN_PRIVATE_ROOT=self.temporal.name)
        ajuste.enable()
        self.addCleanup(ajuste.disable)
        cipher = patch.dict(os.environ, {"LPN_DATA_KEY": Fernet.generate_key().decode()})
        cipher.start()
        self.addCleanup(cipher.stop)
        self.ciudad = Ciudad.objects.create(nombre="Pruebas", departamento="Pruebas")
        self.fundacion = Fundacion.objects.create(entidad=self.entidad, nit="PRUEBAS-01", ciudad=self.ciudad)
        self.raza = Raza.objects.create(especie=Especie.objects.create(nombre="Canino de prueba"), nombre="Mestizo")
        self.pet = Mascota.objects.create(dueno=self.ciudadano, raza=self.raza,
            estado_mascota=valor("estado_mascota", "Con dueño"), nombre="Mascota de prueba")
        self.mod = cuenta("moderador_flujos")
        UsuarioRol.objects.create(usuario=self.mod, rol=Rol.objects.get(codigo="MODERADOR"))

    def pdf(self):
        return SimpleUploadedFile("prueba.pdf", b"%PDF-1.4\nDocumento sintetico", content_type="application/pdf")

    def delegar(self):
        return f.delegar_cuenta(self.ana, self.entidad.pk, self.carlos_m.pk)

    def propuesta(self, numero="000123456789"):
        return f.proponer_cuenta(self.carlos, self.entidad.pk,
            {"numero": numero, "banco": "Banco sintético", "tipo": "Ahorros", "titular": "Fundación sintética"})

    def vet(self):
        organizacion = entidad("Profesional sintético")
        profesional = cuenta("veterinario_flujos")
        miembro_con_rol(profesional, organizacion, "VETERINARIO")
        veterinario = Veterinario.objects.create(entidad=organizacion,
            usuario_profesional=profesional, registro_profesional="PRUEBA-VET-01")
        AutorizacionExpediente.objects.create(mascota=self.pet, veterinario=veterinario,
            usuario_otorgante=self.ciudadano, fecha_expiracion=timezone.now()+timedelta(hours=4))
        return profesional, veterinario

    def reclamacion(self):
        obj = m.ReclamacionMascota.objects.create(mascota=self.pet, reclamante=self.otro, motivo="Soporte de prueba")
        documentos.cargar(self.otro, "reclamacion", obj.pk, self.pdf())
        f.tomar_reclamacion(self.mod, obj.pk)
        return obj

    def test_cuenta_preparar_no_publica_y_aprobacion_conserva_historico(self):
        self.delegar()
        primera = self.propuesta()
        self.assertFalse(CuentaFundacion.objects.exists())
        f.resolver_cuenta(self.ana, primera.pk, True, "Revisión sintética")
        vieja = CuentaFundacion.objects.get()
        nueva = self.propuesta("999988887777")
        f.resolver_cuenta(self.ana, nueva.pk, True, "Cambio autorizado")
        vieja.refresh_from_db()
        self.assertFalse(vieja.activa)
        self.assertEqual(CuentaFundacion.objects.filter(activa=True).count(), 1)
        self.assertEqual(CuentaFundacion.objects.count(), 2)
        self.assertNotIn(b"999988887777", bytes(m.PropuestaCuenta.objects.get(pk=nueva.pk).numero_cifrado))

    def test_secundario_no_delega_cuentas_y_principal_no_prepara(self):
        with self.assertRaises(PermissionDenied):
            f.delegar_cuenta(self.carlos, self.entidad.pk, self.ana_m.pk)
        self.delegar()
        with self.assertRaises(PermissionDenied):
            f.proponer_cuenta(self.ana, self.entidad.pk, {})

    def test_delegado_no_aprueba_y_revocacion_invalida_propuesta(self):
        self.delegar()
        obj = self.propuesta()
        with self.assertRaises(PermissionDenied):
            f.resolver_cuenta(self.carlos, obj.pk, True, "No válido")
        f.delegar_cuenta(self.ana, self.entidad.pk, self.carlos_m.pk, revocar=True)
        with self.assertRaises(ValidationError):
            f.resolver_cuenta(self.ana, obj.pk, True, "Delegación retirada")
        self.assertFalse(CuentaFundacion.objects.exists())

    def test_propuesta_obsoleta_no_pisa_cuenta_aprobada(self):
        self.delegar()
        a, b = self.propuesta(), self.propuesta("777788889999")
        f.resolver_cuenta(self.ana, a.pk, True, "Primera revisión")
        with self.assertRaises(ValidationError):
            f.resolver_cuenta(self.ana, b.pk, True, "Propuesta desactualizada")

    def test_api_cuentas_rechaza_campos_de_aprobacion_y_oculta_numero_en_lista(self):
        self.delegar()
        p = self.propuesta()
        base = f"/api/seguridad/operaciones/entidades/{self.entidad.pk}/propuestas-cuenta/"
        listado = self.cliente(self.ana).get(base)
        self.assertNotIn("numero_cifrado", str(listado.data))
        self.assertNotIn("000123456789", str(listado.data))
        self.assertEqual(self.cliente(self.admin).get(f"/api/seguridad/operaciones/propuestas-cuenta/{p.pk}/").status_code, 403)
        self.assertEqual(self.cliente(self.carlos).post(base, {"estado": "APROBADA"}, format="json").status_code, 400)

    def test_archivo_privado_no_entrega_ruta_y_bloquea_otro_usuario(self):
        obj = documentos.cargar(self.ciudadano, "expediente", self.pet.pk, self.pdf())
        ruta = f"/api/seguridad/operaciones/documentos/{obj.pk}/descargar/"
        self.assertEqual(self.cliente(self.admin).get(ruta).status_code, 403)
        respuesta = self.cliente(self.ciudadano).get(ruta)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta["Cache-Control"], "no-store")
        self.assertIn("attachment", respuesta["Content-Disposition"])
        self.assertTrue(b"".join(respuesta.streaming_content).startswith(b"%PDF-"))
        self.assertTrue(documentos.ruta(obj).is_file())

    def test_archivo_no_se_adjunta_a_mascota_ajena_ni_acepta_html(self):
        with self.assertRaises(PermissionDenied):
            documentos.cargar(self.otro, "expediente", self.pet.pk, self.pdf())
        with self.assertRaises(ValidationError):
            documentos.cargar(self.ciudadano, "expediente", self.pet.pk,
                SimpleUploadedFile("falso.pdf", b"<script>alert(1)</script>"))
        self.assertFalse(m.DocumentoPrivado.objects.exists())

    def test_excepcion_archivo_es_solo_registro_seleccionado_y_no_autoaprobable(self):
        a = documentos.cargar(self.ciudadano, "expediente", self.pet.pk, self.pdf())
        b = documentos.cargar(self.ciudadano, "expediente", self.pet.pk, self.pdf())
        permiso = f.solicitar_excepcion(self.otro, "soporte", a.pk, "Consulta específica")
        with self.assertRaises(PermissionDenied):
            f.resolver_excepcion(self.otro, permiso.pk, True, 1, "No válido")
        with self.assertRaises(PermissionDenied):
            f.resolver_excepcion(self.admin, permiso.pk, True, 1, "No es autoridad médica")
        f.resolver_excepcion(self.ciudadano, permiso.pk, True, 1, "Solo este soporte")
        self.assertTrue(f.leer(self.otro, "soporte", a.pk))
        self.assertFalse(f.leer(self.otro, "soporte", b.pk))
        self.assertFalse(f.leer(self.otro, "expediente", self.pet.pk))
        with self.assertRaises(PermissionDenied):
            documentos.cargar(self.otro, "expediente", self.pet.pk, self.pdf())

    def test_excepcion_maximo_24_horas_vencimiento_y_revocacion(self):
        doc = documentos.cargar(self.ciudadano, "expediente", self.pet.pk, self.pdf())
        obj = f.solicitar_excepcion(self.otro, "soporte", doc.pk, "Acceso temporal")
        with self.assertRaises(ValidationError):
            f.resolver_excepcion(self.ciudadano, obj.pk, True, 25, "Duración inválida")
        f.resolver_excepcion(self.ciudadano, obj.pk, True, 24, "Autorizado")
        self.assertTrue(f.leer(self.otro, "soporte", doc.pk))
        m.AccesoExcepcional.objects.filter(pk=obj.pk).update(expira=timezone.now()-timedelta(seconds=1))
        self.assertFalse(f.leer(self.otro, "soporte", doc.pk))
        otro = f.solicitar_excepcion(self.otro, "soporte", doc.pk, "Nueva solicitud explícita")
        f.resolver_excepcion(self.ciudadano, otro.pk, True, 1, "Autorización nueva")
        f.revocar_excepcion(self.ciudadano, otro.pk, "Revocación anticipada")
        self.assertFalse(f.leer(self.otro, "soporte", doc.pk))

    def test_enmienda_conserva_original_y_no_permite_otro_autor(self):
        profesional, veterinario = self.vet()
        original = HistorialMedico.objects.create(mascota=self.pet, veterinario=veterinario,
            usuario_registrador=profesional, detalle="Texto original", fecha_atencion=timezone.now())
        obj = f.enmendar(profesional, original.pk, "Corrección vinculada", "Error de transcripción")
        original.refresh_from_db()
        self.assertEqual(original.detalle, "Texto original")
        self.assertEqual(obj.original_id, original.pk)
        with self.assertRaises(PermissionDenied):
            f.enmendar(self.ciudadano, original.pk, "No válido", "No es profesional")
        AutorizacionExpediente.objects.filter(veterinario=veterinario).update(fecha_revocacion=timezone.now())
        with self.assertRaises(PermissionDenied):
            f.enmendar(profesional, original.pk, "Sin autorización", "Acceso revocado")

    def test_soporte_del_dueno_no_se_valida_solo_y_revision_no_lo_sobrescribe(self):
        doc = documentos.cargar(self.ciudadano, "expediente", self.pet.pk, self.pdf())
        self.assertFalse(m.RevisionSoporte.objects.exists())
        profesional, _ = self.vet()
        f.revisar_soporte(profesional, doc.pk, "ACLARACIONES", "Falta información")
        f.revisar_soporte(profesional, doc.pk, "VALIDADO", "Información contrastada")
        self.assertEqual(m.RevisionSoporte.objects.count(), 2)
        self.assertTrue(documentos.ruta(doc).is_file())

    def test_verificacion_asignada_correcciones_y_reenvio_no_verifica_automaticamente(self):
        solicitud = SolicitudValidacion.objects.create(entidad=self.entidad, usuario_solicitante=self.ana,
            estado_solicitud=valor("estado_solicitud_validacion", "Pendiente"))
        documentos.cargar(self.ana, "verificacion", solicitud.pk, self.pdf())
        with self.assertRaises(PermissionDenied):
            f.resolver_verificacion(self.mod, solicitud.pk, "aprobar", "Sin asignación")
        tomar(self.mod, "verificacion", solicitud.pk)
        f.resolver_verificacion(self.mod, solicitud.pk, "correcciones", "Documento ilegible")
        f.resolver_verificacion(self.ana, solicitud.pk, "reenviar", "Nueva evidencia")
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado_solicitud.nombre, "Pendiente")
        f.resolver_verificacion(self.mod, solicitud.pk, "aprobar", "Documentación contrastada")
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado_solicitud.nombre, "Aprobada")

    def test_anuncio_nueva_version_no_sustituye_aprobada_hasta_revision(self):
        miembro_con_rol(self.carlos, self.entidad, "GESTOR_PUBLICIDAD")
        datos = {"titulo": "Versión uno", "texto": "Texto de prueba", "url": "https://example.invalid/",
            "inicio": timezone.now()-timedelta(hours=1), "fin": timezone.now()+timedelta(days=1)}
        a = f.nueva_version_anuncio(self.carlos, self.entidad.pk, datos)
        from .flujos_views import publicidad_publica
        self.assertEqual(publicidad_publica(), [])
        f.revisar_anuncio(self.mod, a.pk, "aprobar", "Versión aprobada")
        b = f.nueva_version_anuncio(self.carlos, self.entidad.pk, {**datos, "titulo": "Versión dos"}, a.anuncio_id)
        self.assertEqual(publicidad_publica()[0]["titulo"], "Versión uno")
        f.revisar_anuncio(self.mod, b.pk, "aprobar", "Segunda versión aprobada")
        self.assertEqual(publicidad_publica()[0]["titulo"], "Versión dos")
        f.revisar_anuncio(self.mod, b.pk, "ocultar", "Moderación con motivo")
        self.assertEqual(publicidad_publica(), [])

    def test_reclamacion_dos_pasos_no_abre_clinica_y_cambio_revoca_qr_y_autorizaciones(self):
        self.vet()
        CodigoQRExpediente.objects.create(mascota=self.pet, codigo_hash="hash-sintetico",
            fecha_expiracion=timezone.now()+timedelta(hours=1), usuario_creador=self.ciudadano)
        obj = self.reclamacion()
        self.assertFalse(f.leer(self.mod, "expediente", self.pet.pk))
        f.resolver_reclamacion(self.mod, obj.pk, True, "Reclamación contrastada")
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.dueno_id, self.ciudadano.pk)
        self.assertFalse(f.leer(self.otro, "expediente", self.pet.pk))
        f.ejecutar_titularidad(self.mod, obj.pk, self.ciudadano.pk, self.otro.pk, "Aplicación explícita revisada")
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.dueno_id, self.otro.pk)
        self.assertFalse(AutorizacionExpediente.objects.filter(fecha_revocacion__isnull=True).exists())
        self.assertFalse(CodigoQRExpediente.objects.filter(fecha_revocacion__isnull=True).exists())
        self.assertEqual(m.HistorialTitularidad.objects.count(), 1)

    def test_reclamacion_sin_resolver_no_cambia_y_decision_obsoleta_no_se_ejecuta(self):
        obj = self.reclamacion()
        with self.assertRaises(PermissionDenied):
            f.ejecutar_titularidad(self.mod, obj.pk, self.ciudadano.pk, self.otro.pk, "No resuelta")
        f.resolver_reclamacion(self.mod, obj.pk, True, "Resultado favorable")
        Mascota.objects.filter(pk=self.pet.pk).update(dueno=self.ana)
        with self.assertRaises(ValidationError):
            f.ejecutar_titularidad(self.mod, obj.pk, self.ana.pk, self.otro.pk, "Dato desactualizado")

    def test_reclamar_no_permite_tomar_si_es_dueno_y_rol_revocado_cierra_revisor(self):
        obj = self.reclamacion()
        UsuarioRol.objects.filter(usuario=self.mod).update(fecha_revocacion=timezone.now())
        self.assertFalse(f.leer(self.mod, "reclamacion", obj.pk))
        with self.assertRaises(PermissionDenied):
            f.resolver_reclamacion(self.mod, obj.pk, False, "Rol revocado")

    def test_crear_mascota_solo_declara_nueva_ficha_y_no_acepta_dueno_o_id(self):
        ruta = "/api/seguridad/operaciones/mascotas-propias/"
        cliente = self.cliente(self.ciudadano)
        self.assertEqual(cliente.post(ruta, {"nombre": "Otra", "raza_id": self.raza.pk, "dueno_id": self.otro.pk}, format="json").status_code, 400)
        r = cliente.post(ruta, {"nombre": "Otra", "raza_id": self.raza.pk}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Mascota.objects.get(pk=r.data["id"]).dueno_id, self.ciudadano.pk)

    def test_producto_precio_nuevo_no_cambia_precio_historico_de_pedido(self):
        tienda = Tienda.objects.create(entidad=self.entidad, ciudad=self.ciudad, direccion="Sintética")
        miembro_con_rol(self.carlos, self.entidad, "GESTOR_CATALOGO")
        producto = Producto.objects.create(tienda=tienda, nombre="Prueba", precio=Decimal("10"),
            categoria_producto=valor("categoria_producto", "Alimentos"), tipo_producto=valor("tipo_producto", "Alimento seco"),
            estado_producto=valor("estado_producto", "Disponible"))
        pedido = PedidoIniciado.objects.create(tienda=tienda, usuario_cliente=self.ciudadano,
            estado_pedido=valor("estado_pedido", "Iniciado"))
        detalle = DetallePedido.objects.create(pedido=pedido, tienda=tienda, producto=producto, cantidad=1, precio_referencia=Decimal("10"))
        r = self.cliente(self.carlos).patch(f"/api/seguridad/operaciones/productos/{producto.pk}/", {"precio": "25.00"}, format="json")
        self.assertEqual(r.status_code, 200)
        detalle.refresh_from_db()
        self.assertEqual(detalle.precio_referencia, Decimal("10"))
        self.assertEqual(m.CambioProducto.objects.count(), 1)
        self.assertFalse(f.leer(self.carlos, "pedido", pedido.pk))

    def test_pedido_gestionado_requiere_toma_y_no_ejecuta_cobros(self):
        tienda = Tienda.objects.create(entidad=self.entidad, ciudad=self.ciudad, direccion="Sintética")
        miembro_con_rol(self.carlos, self.entidad, "GESTOR_PEDIDOS")
        pedido = PedidoIniciado.objects.create(tienda=tienda, usuario_cliente=self.ciudadano,
            estado_pedido=valor("estado_pedido", "Iniciado"))
        with self.assertRaises(PermissionDenied):
            f.actualizar_pedido(self.carlos, pedido.pk, "Contactado", "Sin asignación")
        tomar(self.carlos, "pedido", pedido.pk)
        f.actualizar_pedido(self.carlos, pedido.pk, "Contactado", "Contacto informativo")
        devolver(self.carlos, "pedido", pedido.pk, "Cambio de turno")
        self.assertFalse(f.leer(self.carlos, "pedido", pedido.pk))

    def test_reporte_oculto_correccion_aprobada_no_republica(self):
        reporte = Reporte.objects.create(usuario_reportante=self.ciudadano,
            estado_reporte=valor("estado_reporte", "En atención"),
            tipo_reporte=valor("tipo_reporte", "Rescate"), descripcion="Original")
        CasoRescate.objects.create(reporte=reporte, fundacion=self.fundacion,
            estado_caso=valor("estado_caso", "En atención"), usuario_ultimo_cambio=self.carlos)
        miembro_con_rol(self.carlos, self.entidad, "GESTOR_RESCATES")
        f.moderar_reporte(self.mod, reporte.pk, "ocultar", "Contenido pendiente de corrección")
        obj = f.proponer_correccion(self.ciudadano, reporte.pk, {"descripcion": "Corregido"}, "Corrección propia")
        f.resolver_correccion(self.carlos, obj.pk, True, "Corrección operativa aceptada")
        self.assertTrue(m.PublicacionReporte.objects.get(reporte=reporte).oculta)
        f.moderar_reporte(self.ciudadano, reporte.pk, "solicitar_revision", "Contenido corregido")
        f.moderar_reporte(self.mod, reporte.pk, "republicar", "Republicación aprobada")
        self.assertFalse(m.PublicacionReporte.objects.get(reporte=reporte).oculta)

    def test_baja_y_reingreso_no_reactivan_delegacion_bancaria(self):
        self.delegar()
        gestionar_miembro(self.ana, self.entidad.pk, self.carlos.pk, retirar=True)
        gestionar_miembro(self.ana, self.entidad.pk, self.carlos.pk)
        self.assertFalse(f.delegado(self.carlos, self.entidad.pk))

    def test_principal_autoriza_veterinario_en_custodia_sin_leer_historial(self):
        from animals.models import CustodiaMascota
        from animals.services import autorizar_veterinario
        profesional, veterinario = self.vet()
        self.pet.dueno = None
        self.pet.save(update_fields=["dueno"])
        CustodiaMascota.objects.create(mascota=self.pet, fundacion=self.fundacion,
            fecha_inicio=timezone.now(), usuario_registrador=self.ana)
        autorizacion = autorizar_veterinario(mascota_id=self.pet.pk, veterinario_id=veterinario.pk,
            usuario_otorgante_id=self.ana.pk)
        self.assertEqual(autorizacion.usuario_otorgante_id, self.ana.pk)
        self.assertFalse(f.leer(self.ana, "expediente", self.pet.pk))

    def test_reporte_pendiente_solo_propietario_edita_y_cierra(self):
        reporte = Reporte.objects.create(usuario_reportante=self.ciudadano,
            estado_reporte=valor("estado_reporte", "Pendiente"),
            tipo_reporte=valor("tipo_reporte", "Rescate"), descripcion="Original")
        with self.assertRaises(PermissionDenied):
            f.editar_reporte_pendiente(self.otro, reporte.pk, {"descripcion": "Ajeno"})
        f.editar_reporte_pendiente(self.ciudadano, reporte.pk, {"descripcion": "Corregido"})
        f.editar_reporte_pendiente(self.ciudadano, reporte.pk, {}, cerrar=True)
        reporte.refresh_from_db()
        self.assertEqual(reporte.descripcion, "Corregido")
        self.assertEqual(reporte.estado_reporte.nombre, "Cerrado")

    def test_api_privada_no_acepta_conceder_excepcion_a_otro_usuario(self):
        obj = documentos.cargar(self.ciudadano, "expediente", self.pet.pk, self.pdf())
        ruta = "/api/seguridad/operaciones/excepciones/"
        respuesta = self.cliente(self.otro).post(ruta, {"recurso": "soporte", "objeto_id": obj.pk,
            "motivo": "Consulta", "solicitante_id": self.admin.pk, "estado": "APROBADA"}, format="json")
        self.assertEqual(respuesta.status_code, 400)
        self.assertFalse(m.AccesoExcepcional.objects.exists())


class AdopcionCambiosTests(BaseRBAC):
    def setUp(self):
        raza = Raza.objects.create(especie=Especie.objects.create(nombre="Prueba"), nombre="Prueba")
        self.pet = Mascota.objects.create(raza=raza, estado_mascota=valor("estado_mascota", "En adopción"))
        self.solicitud = SolicitudAdopcion.objects.create(mascota=self.pet, usuario_adoptante=self.ciudadano,
            estado_adopcion=valor("estado_adopcion", "Pendiente"))

    def test_respuestas_conservan_historial_y_no_modifican_decision(self):
        f.cambiar_adopcion(self.ciudadano, self.solicitud.pk, respuestas={"vivienda": "Casa"})
        f.cambiar_adopcion(self.ciudadano, self.solicitud.pk, respuestas={"vivienda": "Apartamento"})
        self.assertEqual(m.VersionRespuestas.objects.count(), 2)
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado_adopcion.nombre, "Pendiente")
        with self.assertRaises(PermissionDenied):
            f.cambiar_adopcion(self.otro, self.solicitud.pk, respuestas={"vivienda": "Ajena"})

    def test_retirada_impide_resolucion_y_conserva_registro(self):
        from adoption.services import resolver_solicitud, AdopcionError
        f.cambiar_adopcion(self.ciudadano, self.solicitud.pk, retirar=True)
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado_adopcion.nombre, "Retirada")
        with self.assertRaises(AdopcionError):
            resolver_solicitud(solicitud_id=self.solicitud.pk, fundacion_id=self.entidad.pk,
                usuario_actor_id=self.carlos.pk, aprobar=True)
        self.assertTrue(SolicitudAdopcion.objects.filter(pk=self.solicitud.pk).exists())


from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from django.db import close_old_connections
from django.test import TransactionTestCase
from .tests import catalogos


class FlujosConcurrenciaTests(TransactionTestCase):
    def setUp(self):
        catalogos()

    def test_retirar_y_aprobar_en_paralelo_solo_permite_una_transicion(self):
        from animals.models import CustodiaMascota
        from adoption.services import resolver_solicitud, AdopcionError
        adoptante, gestor = cuenta("adoptante_race"), cuenta("gestor_race")
        organizacion = entidad("Fundación concurrencia")
        ciudad = Ciudad.objects.create(nombre="Concurrencia", departamento="Pruebas")
        fundacion = Fundacion.objects.create(entidad=organizacion, ciudad=ciudad, nit="RACE-01")
        miembro_con_rol(gestor, organizacion, "GESTOR_ADOPCIONES")
        raza = Raza.objects.create(especie=Especie.objects.create(nombre="Concurrencia"), nombre="Prueba")
        mascota = Mascota.objects.create(raza=raza, estado_mascota=valor("estado_mascota", "En adopción"))
        CustodiaMascota.objects.create(mascota=mascota, fundacion=fundacion, fecha_inicio=timezone.now(), usuario_registrador=gestor)
        solicitud = SolicitudAdopcion.objects.create(mascota=mascota, usuario_adoptante=adoptante,
            estado_adopcion=valor("estado_adopcion", "Pendiente"))
        tomar(gestor, "adopcion", solicitud.pk)
        barrera = Barrier(2)

        def intentar(operacion):
            close_old_connections()
            barrera.wait(timeout=10)
            try:
                if operacion == "retirar":
                    f.cambiar_adopcion(adoptante, solicitud.pk, retirar=True)
                    return "Retirada"
                resolver_solicitud(solicitud_id=solicitud.pk, fundacion_id=fundacion.pk,
                    usuario_actor_id=gestor.pk, aprobar=True)
                return "Aprobada"
            except (ValidationError, AdopcionError):
                return "Bloqueada"
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            resultados = list(pool.map(intentar, ["retirar", "aprobar"]))
        self.assertEqual(resultados.count("Bloqueada"), 1)
        solicitud.refresh_from_db()
        mascota.refresh_from_db()
        self.assertIn(solicitud.estado_adopcion.nombre, resultados)
        self.assertEqual(mascota.dueno_id, adoptante.pk if solicitud.estado_adopcion.nombre == "Aprobada" else None)

    def test_dos_moderadores_no_toman_la_misma_reclamacion(self):
        reclamante = cuenta("claim_race")
        raza = Raza.objects.create(especie=Especie.objects.create(nombre="Claim"), nombre="Prueba")
        mascota = Mascota.objects.create(raza=raza, estado_mascota=valor("estado_mascota", "Con dueño"))
        obj = m.ReclamacionMascota.objects.create(mascota=mascota, reclamante=reclamante, motivo="Prueba sintética")
        usuarios = [cuenta("moderador_race_1"), cuenta("moderador_race_2")]
        for usuario in usuarios:
            UsuarioRol.objects.create(usuario=usuario, rol=Rol.objects.get(codigo="MODERADOR"))
        barrera = Barrier(2)

        def intentar(usuario):
            close_old_connections()
            barrera.wait(timeout=10)
            try:
                f.tomar_reclamacion(usuario, obj.pk)
                return "Tomada"
            except ValidationError:
                return "Ocupada"
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            resultados = list(pool.map(intentar, usuarios))
        self.assertCountEqual(resultados, ["Tomada", "Ocupada"])
