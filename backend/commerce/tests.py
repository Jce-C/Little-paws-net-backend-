"""Pruebas del esquema comercial y sus catálogos iniciales."""

from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import TestCase

from accounts.models import Usuario
from core.models import Ciudad, EntidadVerificable, Permiso, Rol, RolPermiso, Tienda, ValorMaestro

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
