"""Pruebas del esquema comercial y sus catálogos iniciales."""

from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import Usuario
from core.models import (
    Anunciante, ArchivoDigital, Ciudad, EntidadMiembro, EntidadMiembroRol,
    EntidadVerificable, Notificacion, Permiso, Rol, RolPermiso,
    Tienda, UsuarioRol, ValorMaestro,
)

from .models import DetallePedido, EspacioPublicitario, PedidoIniciado, Producto, TarifaPublicacion


class ComercioModelosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        verificada = ValorMaestro.objects.get(tipo__nombre="estado_verificacion", nombre="Verificada")
        ciudad = Ciudad.objects.create(nombre="Ciudad Comercio", departamento="Pruebas")
        entidad = EntidadVerificable.objects.create(nombre="Tienda Comercio", estado_verificacion=verificada)
        cls.tienda = Tienda.objects.create(entidad=entidad, ciudad=ciudad, direccion="Calle de prueba")
        cls.cliente = Usuario.objects.create_user(
            email="cliente-comercio@example.invalid", password="clave", nombre="Cliente",
        )
        cls.producto = Producto.objects.create(
            tienda=cls.tienda,
            categoria_producto=ValorMaestro.objects.get(tipo__nombre="categoria_producto", nombre="Alimentos"),
            tipo_producto=ValorMaestro.objects.get(tipo__nombre="tipo_producto", nombre="Alimento seco"),
            nombre="Alimento de prueba", precio=Decimal("15000.00"), existencias=5,
            estado_producto=ValorMaestro.objects.get(tipo__nombre="estado_producto", nombre="Disponible"),
        )

    def test_catalogos_y_permisos_comerciales(self):
        self.assertTrue(Rol.objects.filter(codigo="GESTOR_TIENDA", ambito="ENTIDAD").exists())
        self.assertTrue(Rol.objects.filter(codigo="GESTOR_ANUNCIANTE", ambito="ENTIDAD").exists())
        permiso = Permiso.objects.get(codigo="producto.gestionar")
        self.assertTrue(RolPermiso.objects.filter(rol__codigo="GESTOR_TIENDA", permiso=permiso).exists())
        self.assertEqual(
            set(ValorMaestro.objects.filter(tipo__nombre="estado_pedido").values_list("nombre", flat=True)),
            {"Iniciado", "Cancelado"},
        )

    def test_producto_exige_precio_positivo(self):
        self.producto.precio = Decimal("0.00")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.producto.save(update_fields=["precio"])

    def test_detalle_usa_clave_compuesta_y_cantidad_positiva(self):
        pedido = PedidoIniciado.objects.create(
            tienda=self.tienda, usuario_cliente=self.cliente,
            estado_pedido=ValorMaestro.objects.get(tipo__nombre="estado_pedido", nombre="Iniciado"),
        )
        detalle = DetallePedido.objects.create(
            pedido=pedido, producto=self.producto, cantidad=2, precio_referencia=self.producto.precio,
        )
        self.assertEqual(detalle.pk, (pedido.pk, self.producto.pk))
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DetallePedido.objects.create(
                    pedido=pedido, producto=self.producto, cantidad=1, precio_referencia=self.producto.precio,
                )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                detalle.cantidad = 0
                detalle.save(update_fields=["cantidad"])


class ProductoAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        verificada = ValorMaestro.objects.get(tipo__nombre="estado_verificacion", nombre="Verificada")
        ciudad = Ciudad.objects.create(nombre="Ciudad API Comercio", departamento="Pruebas")
        entidad = EntidadVerificable.objects.create(nombre="Tienda API", estado_verificacion=verificada)
        cls.tienda = Tienda.objects.create(entidad=entidad, ciudad=ciudad, direccion="Calle 1")
        otra_entidad = EntidadVerificable.objects.create(nombre="Tienda Ajena", estado_verificacion=verificada)
        cls.otra_tienda = Tienda.objects.create(entidad=otra_entidad, ciudad=ciudad, direccion="Calle 2")
        cls.gestor = Usuario.objects.create_user(email="gestor-tienda@example.invalid", password="clave", nombre="Gestor")
        cls.ajeno = Usuario.objects.create_user(email="ajeno-tienda@example.invalid", password="clave", nombre="Ajeno")
        rol = Rol.objects.get(codigo="GESTOR_TIENDA")
        EntidadMiembroRol.objects.create(
            miembro=EntidadMiembro.objects.create(entidad=entidad, usuario=cls.gestor), rol=rol,
        )
        EntidadMiembroRol.objects.create(
            miembro=EntidadMiembro.objects.create(entidad=otra_entidad, usuario=cls.ajeno), rol=rol,
        )
        cls.categoria = ValorMaestro.objects.get(tipo__nombre="categoria_producto", nombre="Alimentos")
        cls.tipo = ValorMaestro.objects.get(tipo__nombre="tipo_producto", nombre="Alimento seco")

    def setUp(self):
        self.api = APIClient()

    def _datos(self, *, tienda=None):
        return {
            "id_tienda": (tienda or self.tienda).pk,
            "id_categoria_producto": self.categoria.pk,
            "id_tipo_producto": self.tipo.pk,
            "nombre": "Alimento de prueba", "precio": "20000.00", "existencias": 4,
        }

    def test_gestor_crea_producto_y_catalogo_es_publico(self):
        ruta = reverse("producto_listar_crear")
        self.assertEqual(self.api.get(ruta).data, [])
        self.assertEqual(self.api.post(ruta, self._datos(), format="json").status_code, 401)
        self.api.force_authenticate(user=self.gestor)
        creada = self.api.post(ruta, self._datos(), format="json")
        self.assertEqual(creada.status_code, 201, creada.data)
        self.assertEqual(creada.data["id_tienda"], self.tienda.pk)
        self.api.force_authenticate(user=None)
        listado = self.api.get(ruta)
        self.assertEqual(listado.status_code, 200)
        self.assertEqual(len(listado.data), 1)
        self.assertEqual(self.api.get(reverse("producto_detalle", args=[creada.data["id_producto"]])).status_code, 200)

    def test_otra_tienda_no_puede_crear_ni_modificar_producto(self):
        self.api.force_authenticate(user=self.gestor)
        self.assertEqual(self.api.post(
            reverse("producto_listar_crear"), self._datos(tienda=self.otra_tienda), format="json",
        ).status_code, 403)
        creada = self.api.post(reverse("producto_listar_crear"), self._datos(), format="json")
        self.assertEqual(creada.status_code, 201, creada.data)
        self.api.force_authenticate(user=self.ajeno)
        self.assertEqual(self.api.patch(
            reverse("producto_detalle", args=[creada.data["id_producto"]]),
            {"precio": "10000.00"}, format="json",
        ).status_code, 403)
        self.assertEqual(Producto.objects.get(pk=creada.data["id_producto"]).precio, Decimal("20000.00"))

    def test_actualizar_estado_oculta_producto_y_no_cambia_tienda(self):
        self.api.force_authenticate(user=self.gestor)
        creada = self.api.post(reverse("producto_listar_crear"), self._datos(), format="json")
        self.assertEqual(creada.status_code, 201, creada.data)
        ruta = reverse("producto_detalle", args=[creada.data["id_producto"]])
        inactivo = ValorMaestro.objects.get(tipo__nombre="estado_producto", nombre="Inactivo")
        modificada = self.api.patch(ruta, {"id_estado_producto": inactivo.pk}, format="json")
        self.assertEqual(modificada.status_code, 200, modificada.data)
        self.assertEqual(self.api.get(ruta).status_code, 404)
        self.assertEqual(self.api.get(reverse("producto_listar_crear")).data, [])
        rechazada = self.api.patch(ruta, {"id_tienda": self.otra_tienda.pk}, format="json")
        self.assertEqual(rechazada.status_code, 400)
        self.assertEqual(Producto.objects.get(pk=creada.data["id_producto"]).tienda_id, self.tienda.pk)

    def test_categorias_y_precios_invalidos_se_rechazan(self):
        self.api.force_authenticate(user=self.gestor)
        datos = self._datos()
        datos["id_categoria_producto"] = ValorMaestro.objects.get(
            tipo__nombre="estado_pedido", nombre="Iniciado",
        ).pk
        self.assertEqual(self.api.post(reverse("producto_listar_crear"), datos, format="json").status_code, 400)
        datos = self._datos()
        datos["precio"] = "0.00"
        self.assertEqual(self.api.post(reverse("producto_listar_crear"), datos, format="json").status_code, 400)
        self.assertFalse(Producto.objects.exists())

    def test_nombre_y_descripcion_del_producto_se_localizan(self):
        self.api.force_authenticate(user=self.gestor)
        datos = self._datos()
        datos.update({
            "nombre_en": "Test food", "descripcion": "Alimento para perro",
            "descripcion_en": "Dog food",
        })
        creada = self.api.post(reverse("producto_listar_crear"), datos, format="json")
        self.assertEqual(creada.status_code, 201, creada.data)
        self.assertEqual(creada.data["nombre"], "Alimento de prueba")
        self.api.force_authenticate(user=None)
        ingles = self.api.get(reverse("producto_listar_crear"), HTTP_ACCEPT_LANGUAGE="en")
        self.assertEqual(ingles.data[0]["nombre"], "Test food")
        self.assertEqual(ingles.data[0]["descripcion"], "Dog food")
        self.assertEqual(ingles.data[0]["categoria"], "Food")
        self.assertEqual(ingles.data[0]["tipo"], "Dry food")
        self.assertEqual(ingles.data[0]["estado"], "Available")
        self.assertEqual(ingles["Content-Language"], "en")
        self.assertNotIn("nombre_en", ingles.data[0])
        self.api.force_authenticate(user=self.gestor)
        ruta = reverse("producto_detalle", args=[creada.data["id_producto"]])
        self.assertEqual(self.api.patch(ruta, {"nombre_en": "Updated food"}, format="json").status_code, 200)
        self.api.force_authenticate(user=None)
        actualizado = self.api.get(ruta, HTTP_ACCEPT_LANGUAGE="en")
        self.assertEqual(actualizado.data["nombre"], "Updated food")

    def test_productos_sin_traduccion_mantienen_texto_original(self):
        self.api.force_authenticate(user=self.gestor)
        creada = self.api.post(reverse("producto_listar_crear"), self._datos(), format="json")
        self.assertEqual(creada.status_code, 201, creada.data)
        self.api.force_authenticate(user=None)
        ingles = self.api.get(reverse("producto_listar_crear"), HTTP_ACCEPT_LANGUAGE="en")
        self.assertEqual(ingles.data[0]["nombre"], "Alimento de prueba")

    def test_error_de_permiso_se_traduce_sin_cambiar_regla(self):
        self.api.force_authenticate(user=self.ajeno)
        respuesta = self.api.post(
            reverse("producto_listar_crear"), self._datos(),
            format="json", HTTP_ACCEPT_LANGUAGE="en",
        )
        self.assertEqual(respuesta.status_code, 403)
        self.assertEqual(respuesta.data["detalle"], "You cannot manage this store's products")


class PedidoAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        verificada = ValorMaestro.objects.get(tipo__nombre="estado_verificacion", nombre="Verificada")
        ciudad = Ciudad.objects.create(nombre="Ciudad Pedidos", departamento="Pruebas")
        entidad = EntidadVerificable.objects.create(nombre="Tienda Pedidos", estado_verificacion=verificada)
        cls.tienda = Tienda.objects.create(entidad=entidad, ciudad=ciudad, direccion="Calle 1")
        otra_entidad = EntidadVerificable.objects.create(nombre="Otra Tienda Pedidos", estado_verificacion=verificada)
        cls.otra_tienda = Tienda.objects.create(entidad=otra_entidad, ciudad=ciudad, direccion="Calle 2")
        cls.cliente = Usuario.objects.create_user(email="cliente-pedido@example.invalid", password="clave", nombre="Cliente")
        cls.otro = Usuario.objects.create_user(email="otro-pedido@example.invalid", password="clave", nombre="Otro")
        cls.gestor = Usuario.objects.create_user(email="gestor-pedido@example.invalid", password="clave", nombre="Gestor")
        cls.admin = Usuario.objects.create_user(email="admin-pedido@example.invalid", password="clave", nombre="Admin")
        UsuarioRol.objects.create(usuario=cls.admin, rol=Rol.objects.get(codigo="ADMIN_PLATAFORMA"))
        EntidadMiembroRol.objects.create(
            miembro=EntidadMiembro.objects.create(entidad=entidad, usuario=cls.gestor),
            rol=Rol.objects.get(codigo="GESTOR_TIENDA"),
        )
        categoria = ValorMaestro.objects.get(tipo__nombre="categoria_producto", nombre="Alimentos")
        tipo = ValorMaestro.objects.get(tipo__nombre="tipo_producto", nombre="Alimento seco")
        disponible = ValorMaestro.objects.get(tipo__nombre="estado_producto", nombre="Disponible")
        cls.producto1 = Producto.objects.create(
            tienda=cls.tienda, categoria_producto=categoria, tipo_producto=tipo,
            nombre="Producto uno", precio=Decimal("10000.00"), existencias=5,
            estado_producto=disponible,
        )
        cls.producto2 = Producto.objects.create(
            tienda=cls.tienda, categoria_producto=categoria, tipo_producto=tipo,
            nombre="Producto dos", precio=Decimal("2500.00"), existencias=3,
            estado_producto=disponible,
        )
        cls.producto_ajeno = Producto.objects.create(
            tienda=cls.otra_tienda, categoria_producto=categoria, tipo_producto=tipo,
            nombre="Producto ajeno", precio=Decimal("3000.00"), existencias=10,
            estado_producto=disponible,
        )

    def setUp(self):
        self.api = APIClient()

    def _datos(self):
        return {"id_tienda": self.tienda.pk, "productos": [
            {"id_producto": self.producto1.pk, "cantidad": 2},
            {"id_producto": self.producto2.pk, "cantidad": 1},
        ]}

    def _crear(self):
        self.api.force_authenticate(user=self.cliente)
        respuesta = self.api.post(reverse("pedido_listar_crear"), self._datos(), format="json")
        self.assertEqual(respuesta.status_code, 201, respuesta.data)
        return respuesta

    def test_crea_pedido_atomico_con_precios_y_notificacion_interna(self):
        respuesta = self._crear()
        self.assertEqual(respuesta.data["estado"], "Iniciado")
        self.assertEqual(respuesta.data["total_referencial"], "22500.00")
        self.assertIn("no confirma pago", respuesta.data["aviso"])
        pedido = PedidoIniciado.objects.get(pk=respuesta.data["id_pedido"])
        self.assertEqual(pedido.detallepedido_set.count(), 2)
        self.assertEqual(Notificacion.objects.filter(usuario=self.cliente).count(), 1)
        self.producto1.refresh_from_db()
        self.assertEqual(self.producto1.existencias, 5)
        self.producto1.precio = Decimal("13000.00")
        self.producto1.save(update_fields=["precio"])
        detalle = self.api.get(reverse("pedido_detalle", args=[pedido.pk]))
        self.assertEqual(detalle.data["total_referencial"], "22500.00")

    def test_respuesta_de_pedido_en_ingles(self):
        pedido_id = self._crear().data["id_pedido"]
        respuesta = self.api.get(
            reverse("pedido_detalle", args=[pedido_id]), HTTP_ACCEPT_LANGUAGE="en",
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["estado"], "Started")
        self.assertIn("payment is not confirmed", respuesta.data["aviso"])

    def test_rechaza_producto_de_otra_tienda_sin_dejar_registros(self):
        self.api.force_authenticate(user=self.cliente)
        datos = self._datos()
        datos["productos"][1]["id_producto"] = self.producto_ajeno.pk
        respuesta = self.api.post(reverse("pedido_listar_crear"), datos, format="json")
        self.assertEqual(respuesta.status_code, 400, respuesta.data)
        self.assertFalse(PedidoIniciado.objects.exists())
        self.assertFalse(DetallePedido.objects.exists())
        self.assertFalse(Notificacion.objects.exists())

    def test_rechaza_duplicados_y_cantidad_sin_existencias(self):
        self.api.force_authenticate(user=self.cliente)
        datos = self._datos()
        datos["productos"][1]["id_producto"] = self.producto1.pk
        self.assertEqual(self.api.post(reverse("pedido_listar_crear"), datos, format="json").status_code, 400)
        datos = self._datos()
        datos["productos"][0]["cantidad"] = 6
        self.assertEqual(self.api.post(reverse("pedido_listar_crear"), datos, format="json").status_code, 400)
        self.assertFalse(PedidoIniciado.objects.exists())

    def test_no_acepta_precio_enviado_por_cliente(self):
        self.api.force_authenticate(user=self.cliente)
        datos = self._datos()
        datos["productos"][0]["precio_referencia"] = "0.01"
        respuesta = self.api.post(reverse("pedido_listar_crear"), datos, format="json")
        self.assertEqual(respuesta.status_code, 400, respuesta.data)
        self.assertFalse(PedidoIniciado.objects.exists())

    def test_solo_cliente_gestor_de_tienda_y_admin_ven_pedido(self):
        pedido_id = self._crear().data["id_pedido"]
        ruta = reverse("pedido_detalle", args=[pedido_id])
        self.api.force_authenticate(user=self.otro)
        self.assertEqual(self.api.get(ruta).status_code, 404)
        self.assertEqual(self.api.get(reverse("pedido_listar_crear")).data, [])
        self.api.force_authenticate(user=self.gestor)
        self.assertEqual(self.api.get(ruta).status_code, 200)
        self.api.force_authenticate(user=self.admin)
        self.assertEqual(self.api.get(ruta).status_code, 200)

    def test_requiere_autenticacion(self):
        self.assertEqual(self.api.post(reverse("pedido_listar_crear"), self._datos(), format="json").status_code, 401)
        self.assertEqual(self.api.get(reverse("pedido_listar_crear")).status_code, 401)


class PublicidadAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        verificada = ValorMaestro.objects.get(tipo__nombre="estado_verificacion", nombre="Verificada")
        entidad = EntidadVerificable.objects.create(nombre="Anunciante Pruebas", estado_verificacion=verificada)
        cls.anunciante = Anunciante.objects.create(entidad=entidad, nit_documento="NIT-ADS-1")
        otra_entidad = EntidadVerificable.objects.create(nombre="Anunciante Ajeno", estado_verificacion=verificada)
        cls.otro_anunciante = Anunciante.objects.create(entidad=otra_entidad, nit_documento="NIT-ADS-2")
        cls.gestor = Usuario.objects.create_user(email="gestor-ads@example.invalid", password="clave", nombre="Gestor")
        cls.ajeno = Usuario.objects.create_user(email="ajeno-ads@example.invalid", password="clave", nombre="Ajeno")
        EntidadMiembroRol.objects.create(
            miembro=EntidadMiembro.objects.create(entidad=entidad, usuario=cls.gestor),
            rol=Rol.objects.get(codigo="GESTOR_ANUNCIANTE"),
        )
        EntidadMiembroRol.objects.create(
            miembro=EntidadMiembro.objects.create(entidad=otra_entidad, usuario=cls.ajeno),
            rol=Rol.objects.get(codigo="GESTOR_ANUNCIANTE"),
        )
        cls.archivo = ArchivoDigital.objects.create(
            storage_key="pruebas/banner.png", url_archivo="https://cdn.example.com/banner.png",
            mime_type="image/png", tamano_bytes=1024, visibilidad="PUBLICO", usuario_cargador=cls.gestor,
        )
        cls.tipo = ValorMaestro.objects.get(tipo__nombre="tipo_publicidad", nombre="Banner")

    def setUp(self):
        self.api = APIClient()

    def _datos(self, *, futuro=False):
        inicio = timezone.now() + timezone.timedelta(days=1) if futuro else timezone.now() - timezone.timedelta(minutes=1)
        return {
            "id_anunciante": self.anunciante.pk,
            "id_tipo_publicidad": self.tipo.pk,
            "fecha_inicio": inicio.isoformat(),
            "fecha_fin": (inicio + timezone.timedelta(days=7)).isoformat(),
            "url_destino": "https://example.com/adopcion",
            "id_archivo": self.archivo.pk,
        }

    def test_gestor_publica_y_catalogo_es_publico(self):
        ruta = reverse("publicidad_listar_crear")
        self.assertEqual(self.api.get(ruta).data, [])
        self.assertEqual(self.api.post(ruta, self._datos(), format="json").status_code, 401)
        self.api.force_authenticate(user=self.gestor)
        creada = self.api.post(ruta, self._datos(), format="json")
        self.assertEqual(creada.status_code, 201, creada.data)
        self.assertEqual(creada.data["url_archivo"], "https://cdn.example.com/banner.png")
        self.assertNotIn("storage_key", creada.data)
        self.api.force_authenticate(user=None)
        self.assertEqual(len(self.api.get(ruta).data), 1)
        self.assertEqual(self.api.get(reverse("publicidad_detalle", args=[creada.data["id_espacio"]])).status_code, 200)

    def test_aviso_publicitario_en_ingles(self):
        self.api.force_authenticate(user=self.gestor)
        creada = self.api.post(reverse("publicidad_listar_crear"), self._datos(), format="json")
        self.assertEqual(creada.status_code, 201, creada.data)
        respuesta = self.api.get(reverse("publicidad_listar_crear"), HTTP_ACCEPT_LANGUAGE="en")
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("does not process", respuesta.data[0]["aviso"])

    def test_anuncio_futuro_es_visible_solo_para_su_gestor(self):
        self.api.force_authenticate(user=self.gestor)
        creada = self.api.post(reverse("publicidad_listar_crear"), self._datos(futuro=True), format="json")
        self.assertEqual(creada.status_code, 201, creada.data)
        ruta = reverse("publicidad_detalle", args=[creada.data["id_espacio"]])
        self.api.force_authenticate(user=None)
        self.assertEqual(self.api.get(reverse("publicidad_listar_crear")).data, [])
        self.assertEqual(self.api.get(ruta).status_code, 404)
        self.api.force_authenticate(user=self.ajeno)
        self.assertEqual(self.api.get(ruta).status_code, 404)
        self.api.force_authenticate(user=self.gestor)
        self.assertEqual(self.api.get(ruta).status_code, 200)

    def test_otra_entidad_y_archivo_privado_son_rechazados(self):
        self.api.force_authenticate(user=self.gestor)
        datos = self._datos()
        datos["id_anunciante"] = self.otro_anunciante.pk
        self.assertEqual(self.api.post(reverse("publicidad_listar_crear"), datos, format="json").status_code, 403)
        archivo_privado = ArchivoDigital.objects.create(
            storage_key="pruebas/banner-privado.png", url_archivo="https://cdn.example.com/privado.png",
            mime_type="image/png", tamano_bytes=1024, visibilidad="PRIVADO", usuario_cargador=self.gestor,
        )
        datos = self._datos()
        datos["id_archivo"] = archivo_privado.pk
        self.assertEqual(self.api.post(reverse("publicidad_listar_crear"), datos, format="json").status_code, 400)
        self.assertFalse(EspacioPublicitario.objects.exists())

    def test_rechaza_url_interna_y_fecha_invalida(self):
        self.api.force_authenticate(user=self.gestor)
        datos = self._datos()
        datos["url_destino"] = "https://127.0.0.1/admin"
        self.assertEqual(self.api.post(reverse("publicidad_listar_crear"), datos, format="json").status_code, 400)
        datos = self._datos()
        datos["fecha_fin"] = datos["fecha_inicio"]
        self.assertEqual(self.api.post(reverse("publicidad_listar_crear"), datos, format="json").status_code, 400)
        self.assertFalse(EspacioPublicitario.objects.exists())


class TarifaPublicacionAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        verificada = ValorMaestro.objects.get(tipo__nombre="estado_verificacion", nombre="Verificada")
        ciudad = Ciudad.objects.create(nombre="Ciudad Tarifas", departamento="Pruebas")
        entidad = EntidadVerificable.objects.create(nombre="Tienda Tarifas", estado_verificacion=verificada)
        cls.tienda = Tienda.objects.create(entidad=entidad, ciudad=ciudad, direccion="Calle Tarifas")
        cls.admin = Usuario.objects.create_user(email="admin-tarifas@example.invalid", password="clave", nombre="Admin")
        cls.gestor = Usuario.objects.create_user(email="gestor-tarifas@example.invalid", password="clave", nombre="Gestor")
        cls.cliente = Usuario.objects.create_user(email="cliente-tarifas@example.invalid", password="clave", nombre="Cliente")
        UsuarioRol.objects.create(usuario=cls.admin, rol=Rol.objects.get(codigo="ADMIN_PLATAFORMA"))
        EntidadMiembroRol.objects.create(
            miembro=EntidadMiembro.objects.create(entidad=entidad, usuario=cls.gestor),
            rol=Rol.objects.get(codigo="GESTOR_TIENDA"),
        )
        cls.tipo = ValorMaestro.objects.get(tipo__nombre="tipo_tarifa", nombre="Mensual")

    def setUp(self):
        self.api = APIClient()

    def _datos(self, *, dias_inicio=-1, dias_fin=7):
        hoy = timezone.localdate()
        return {
            "id_tienda": self.tienda.pk,
            "id_tipo_tarifa": self.tipo.pk,
            "monto": "35000.00",
            "fecha_inicio": (hoy + timezone.timedelta(days=dias_inicio)).isoformat(),
            "fecha_fin": (hoy + timezone.timedelta(days=dias_fin)).isoformat(),
            "concepto": "Publicación mensual de la tienda",
        }

    def test_admin_crea_tarifa_vigente_y_consulta_publica(self):
        ruta = reverse("tarifa_listar_crear")
        self.assertEqual(self.api.get(ruta).data, [])
        self.api.force_authenticate(user=self.admin)
        creada = self.api.post(ruta, self._datos(), format="json")
        self.assertEqual(creada.status_code, 201, creada.data)
        self.assertEqual(creada.data["monto"], "35000.00")
        self.assertIn("no acredita cobro", creada.data["aviso"])
        self.api.force_authenticate(user=None)
        self.assertEqual(len(self.api.get(ruta).data), 1)
        self.assertEqual(self.api.get(reverse("tarifa_detalle", args=[creada.data["id_tarifa"]])).status_code, 200)

    def test_solo_admin_puede_crear_tarifas(self):
        ruta = reverse("tarifa_listar_crear")
        self.assertEqual(self.api.post(ruta, self._datos(), format="json").status_code, 401)
        for usuario in (self.gestor, self.cliente):
            self.api.force_authenticate(user=usuario)
            self.assertEqual(self.api.post(ruta, self._datos(), format="json").status_code, 403)
        self.assertFalse(TarifaPublicacion.objects.exists())

    def test_tarifa_futura_solo_es_visible_para_admin(self):
        self.api.force_authenticate(user=self.admin)
        creada = self.api.post(reverse("tarifa_listar_crear"), self._datos(dias_inicio=1), format="json")
        self.assertEqual(creada.status_code, 201, creada.data)
        detalle = reverse("tarifa_detalle", args=[creada.data["id_tarifa"]])
        self.api.force_authenticate(user=None)
        self.assertEqual(self.api.get(reverse("tarifa_listar_crear")).data, [])
        self.assertEqual(self.api.get(detalle).status_code, 404)
        self.api.force_authenticate(user=self.gestor)
        self.assertEqual(self.api.get(detalle).status_code, 404)
        self.api.force_authenticate(user=self.admin)
        self.assertEqual(self.api.get(detalle).status_code, 200)

    def test_rechaza_solapamiento_y_datos_invalidos(self):
        ruta = reverse("tarifa_listar_crear")
        self.api.force_authenticate(user=self.admin)
        self.assertEqual(self.api.post(ruta, self._datos(), format="json").status_code, 201)
        self.assertEqual(self.api.post(ruta, self._datos(dias_inicio=7, dias_fin=14), format="json").status_code, 400)
        datos = self._datos(dias_inicio=8, dias_fin=7)
        self.assertEqual(self.api.post(ruta, datos, format="json").status_code, 400)
        datos = self._datos(dias_inicio=8, dias_fin=14)
        datos["monto"] = "-1.00"
        self.assertEqual(self.api.post(ruta, datos, format="json").status_code, 400)
        datos = self._datos(dias_inicio=8, dias_fin=14)
        datos["id_tipo_tarifa"] = ValorMaestro.objects.get(
            tipo__nombre="estado_pedido", nombre="Iniciado",
        ).pk
        self.assertEqual(self.api.post(ruta, datos, format="json").status_code, 400)
        self.assertEqual(TarifaPublicacion.objects.count(), 1)

    def test_concepto_de_tarifa_se_localiza(self):
        self.api.force_authenticate(user=self.admin)
        datos = self._datos()
        datos["concepto_en"] = "Monthly store listing"
        creada = self.api.post(reverse("tarifa_listar_crear"), datos, format="json")
        self.assertEqual(creada.status_code, 201, creada.data)
        self.api.force_authenticate(user=None)
        ingles = self.api.get(reverse("tarifa_listar_crear"), HTTP_ACCEPT_LANGUAGE="en")
        self.assertEqual(ingles.data[0]["concepto"], "Monthly store listing")
        self.assertEqual(ingles.data[0]["tipo_tarifa"], "Monthly")
        self.assertIn("does not confirm", ingles.data[0]["aviso"])
