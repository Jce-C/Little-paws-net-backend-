"""Pruebas del esquema comercial y sus catálogos iniciales."""

from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import Usuario
from core.models import (
    Ciudad, EntidadMiembro, EntidadMiembroRol, EntidadVerificable,
    Permiso, Rol, RolPermiso, Tienda, ValorMaestro,
)

from .models import DetallePedido, PedidoIniciado, Producto


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
