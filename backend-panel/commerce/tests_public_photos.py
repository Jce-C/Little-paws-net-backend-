from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from PIL import Image
from django.test import override_settings, Client
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from seguridad.tests import BaseRBAC, miembro_con_rol, valor
from seguridad.models import BajaAdministrativa, EventoSeguridad
from core.models import Ciudad, Tienda, EntidadMiembroRol
from .models import Producto, FotoPublicaProducto
from . import public_photos as photos


def upload():
    stream = BytesIO()
    exif = Image.Exif()
    exif[270] = 'Dato privado de prueba'
    Image.new('RGB', (1800, 900), 'green').save(stream, 'JPEG', exif=exif)
    return SimpleUploadedFile('original.jpg', stream.getvalue(), 'image/jpeg')


class FotosProductoTests(BaseRBAC):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        override = override_settings(LPN_PRIVATE_ROOT=Path(temp.name))
        override.enable()
        self.addCleanup(override.disable)
        city, _ = Ciudad.objects.get_or_create(nombre='Riohacha', departamento='La Guajira')
        self.store = Tienda.objects.create(entidad=self.entidad, ciudad=city, direccion='Dirección sintética')
        self.other = Tienda.objects.create(entidad=self.ajena, ciudad=city, direccion='Otra dirección sintética')
        miembro_con_rol(self.carlos, self.entidad, 'GESTOR_CATALOGO')
        miembro_con_rol(self.otro, self.ajena, 'GESTOR_CATALOGO')
        self.product = Producto.objects.create(tienda=self.store, nombre='Producto sintético', precio='10000', existencias=2,
            categoria_producto=valor('categoria_producto', 'Alimentos'), tipo_producto=valor('tipo_producto', 'Alimento seco'),
            estado_producto=valor('estado_producto', 'Disponible'))
        self.manage = f'/api/catalogo/productos/{self.product.pk}/foto-publica/'
        self.public = f'/api/catalogo/productos/{self.product.pk}/foto/'

    def publish(self, actor=None, **values):
        return self.cliente(actor or self.carlos).post(self.manage, {'archivo': upload(), 'confirmar_publicacion': 'true', **values}, format='multipart')

    def test_normaliza_publica_sin_metadatos_y_catalogo_sin_n_mas_uno(self):
        self.assertEqual(self.publish().status_code, 201)
        response = APIClient().get(self.public)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Cache-Control'], 'no-store')
        self.assertEqual(response['Content-Type'], 'image/webp')
        with Image.open(BytesIO(response.content)) as image:
            self.assertEqual(image.size, (1280, 640))
            self.assertEqual(dict(image.getexif()), {})
        self.assertNotIn(b'Dato privado', response.content)
        with self.assertNumQueries(1):
            catalog = APIClient().get('/api/catalogo/productos/')
        self.assertEqual(catalog.data[0]['foto']['ancho'], 1280)
        self.assertNotIn('clave', catalog.data[0]['foto'])
        self.assertTrue(EventoSeguridad.objects.filter(accion='producto.foto_publicar').exists())
        from seguridad.web.presentacion_eventos import descripcion_reciente, informacion_evento
        event = EventoSeguridad.objects.get(accion='producto.foto_publicar')
        self.assertIn('producto', descripcion_reciente(event))
        self.assertIn('1280', informacion_evento(event))

    def test_solo_gestor_de_la_tienda_con_confirmacion(self):
        self.assertEqual(APIClient().post(self.manage).status_code, 401)
        for actor in (self.ciudadano, self.otro):
            self.assertEqual(self.publish(actor).status_code, 403)
        self.assertEqual(self.publish(confirmar_publicacion='false').status_code, 400)
        self.assertFalse(FotoPublicaProducto.objects.exists())

    def test_revocacion_incluso_durante_normalizacion(self):
        real = photos.normalizar
        def revoke(file):
            EntidadMiembroRol.objects.filter(miembro__usuario=self.carlos).update(fecha_revocacion=timezone.now())
            return real(file)
        with patch('commerce.public_photos.normalizar', side_effect=revoke):
            self.assertEqual(self.publish().status_code, 403)
        self.assertFalse(FotoPublicaProducto.objects.exists())

    def test_rechaza_imagen_falsa_y_ruta_fuera_de_almacen(self):
        self.assertEqual(self.publish(archivo=SimpleUploadedFile('x.jpg', b'<svg/>', 'image/jpeg')).status_code, 400)
        from rest_framework.exceptions import ValidationError
        for key in ('../archivo.webp', '/tmp/a.webp', 'imagen.jpg'):
            with self.assertRaises(ValidationError):
                photos.ruta(key)

    def test_retirada_borra_y_no_se_puede_seguir_consultando(self):
        self.assertEqual(self.publish().status_code, 201)
        path = photos.ruta(FotoPublicaProducto.objects.get().clave)
        with self.captureOnCommitCallbacks(execute=True):
            self.assertEqual(self.cliente(self.carlos).delete(self.manage).status_code, 204)
        self.assertFalse(path.exists())
        response = APIClient().get(self.public)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response['Cache-Control'], 'no-store')
        self.assertIsNone(APIClient().get('/api/catalogo/productos/').data[0]['foto'])

    def test_oculta_por_estado_baja_verificacion_y_cambio_de_tienda(self):
        self.assertEqual(self.publish().status_code, 201)
        self.product.tienda = self.other
        self.product.save(update_fields=['tienda'])
        self.assertEqual(APIClient().get(self.public).status_code, 404)
        self.assertIsNone(APIClient().get('/api/catalogo/productos/').data[0]['foto'])
        self.product.tienda = self.store
        self.product.save(update_fields=['tienda'])
        BajaAdministrativa.objects.create(tipo='productos', objeto_id=self.product.pk, activo=False, eliminado=False, autor=self.admin, motivo='Prueba sintética')
        self.assertEqual(APIClient().get(self.public).status_code, 404)
        self.assertEqual(APIClient().get('/api/catalogo/productos/').data, [])

    def test_panel_publica_y_retirada_con_misma_autorizacion(self):
        client = Client()
        client.force_login(self.carlos)
        url = f'/panel/productos/{self.product.pk}/fotografia/'
        self.assertEqual(client.get(url).status_code, 200)
        self.assertEqual(client.post(url, {'archivo': upload(), 'confirmar_publicacion': True}).status_code, 302)
        self.assertContains(client.get(url), 'Publicación actual')
        self.assertEqual(client.post(url + '?modo=retirar', {'confirmar_retirada': True}).status_code, 302)
        client.force_login(self.otro)
        self.assertEqual(client.get(url).status_code, 403)

    def test_almacen_inaccesible_no_crea_publicacion(self):
        with patch('commerce.public_photos.raiz', side_effect=OSError('synthetic')):
            self.assertEqual(self.publish().status_code, 503)
        self.assertFalse(FotoPublicaProducto.objects.exists())

    def test_disponibilidad_y_verificacion_se_revisan_en_cada_get(self):
        self.assertEqual(self.publish().status_code, 201)
        previous = self.product.estado_producto
        from core.models import ValorMaestro
        self.product.estado_producto = ValorMaestro.objects.filter(tipo__nombre='estado_producto').exclude(pk=previous.pk).first()
        self.product.save(update_fields=['estado_producto'])
        self.assertEqual(APIClient().get(self.public).status_code, 404)
        self.assertEqual(self.publish().status_code, 400)
        self.product.estado_producto = previous
        self.product.save(update_fields=['estado_producto'])
        self.entidad.estado_verificacion = ValorMaestro.objects.filter(tipo__nombre='estado_verificacion').exclude(nombre='Verificada').first()
        self.entidad.save(update_fields=['estado_verificacion'])
        self.assertEqual(APIClient().get(self.public).status_code, 404)
        self.assertEqual(self.publish().status_code, 400)

    def test_panel_exige_csrf_y_muestra_enlace_solo_con_permiso(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.carlos)
        url = f'/panel/productos/{self.product.pk}/fotografia/'
        self.assertEqual(client.post(url, {'archivo': upload(), 'confirmar_publicacion': True}).status_code, 403)
        self.assertFalse(FotoPublicaProducto.objects.exists())
        self.assertContains(client.get(f'/panel/areas/catalogo/?entidad={self.entidad.pk}'), url)
