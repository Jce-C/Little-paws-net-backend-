from io import BytesIO
from tempfile import TemporaryDirectory
from unittest.mock import patch
from PIL import Image
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APIClient
from seguridad.tests import BaseRBAC
from core.models import FotoPublicaPerfil, PublicacionComunidad, ComentarioComunidad
from . import public_avatars as photos


def image():
    stream = BytesIO()
    exif = Image.Exif()
    exif[270] = 'Private EXIF QA'
    Image.new('RGB', (1000, 500), 'green').save(stream, 'JPEG', exif=exif)
    return SimpleUploadedFile('private-filename.jpg', stream.getvalue(), 'image/jpeg')


class PublicAvatarTests(BaseRBAC):
    path = '/api/auth/foto-publica/'

    def setUp(self):
        cache.clear()
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        config = override_settings(LPN_PRIVATE_ROOT=temp.name)
        config.enable()
        self.addCleanup(config.disable)

    def publish(self, actor=None, **extra):
        return self.cliente(actor or self.ciudadano).post(self.path, {
            'archivo': image(), 'confirmar_publicacion': 'true', **extra,
        }, format='multipart')

    def test_owned_publication_and_normalized_private_metadata(self):
        response = self.publish()
        self.assertEqual(response.status_code, 201, response.data)
        value = response.data['foto_publica']
        self.assertEqual(set(value), {'url', 'ancho', 'alto', 'bytes'})
        self.assertEqual(value['ancho'], 256)
        self.assertLessEqual(value['bytes'], 64 * 1024)
        public = APIClient().get(value['url'])
        self.assertEqual(public.status_code, 200)
        self.assertEqual(public['Cache-Control'], 'no-store')
        self.assertEqual(public['Content-Type'], 'image/webp')
        self.assertEqual(public['X-Content-Type-Options'], 'nosniff')
        with Image.open(BytesIO(public.content)) as decoded:
            self.assertEqual(dict(decoded.getexif()), {})
        self.assertNotIn(b'Private EXIF', public.content)
        self.assertEqual(FotoPublicaPerfil.objects.get().usuario, self.ciudadano)

    def test_requires_login_and_explicit_consent(self):
        self.assertEqual(APIClient().get(self.path).status_code, 401)
        self.assertEqual(APIClient().post(self.path).status_code, 401)
        self.assertEqual(self.publish(confirmar_publicacion='false').status_code, 400)
        self.assertFalse(FotoPublicaPerfil.objects.exists())

    def test_admin_cannot_target_another_account(self):
        self.assertEqual(self.publish(self.admin, usuario=self.otro.pk).status_code, 400)
        self.assertEqual(self.publish(self.admin).status_code, 201)
        self.assertEqual(FotoPublicaPerfil.objects.get().usuario, self.admin)
        self.assertEqual(self.cliente(self.otro).get(self.path).data['foto_publica'], None)

    def test_replacement_invalidates_previous_url_and_deletes_old_file(self):
        old_url = self.publish().data['foto_publica']['url']
        old_file = photos.ruta(FotoPublicaPerfil.objects.get().clave)
        with self.captureOnCommitCallbacks(execute=True):
            new_url = self.publish().data['foto_publica']['url']
        self.assertNotEqual(new_url, old_url)
        self.assertEqual(APIClient().get(old_url).status_code, 404)
        self.assertFalse(old_file.exists())

    def test_withdrawal_is_owned_and_stops_public_serving(self):
        url = self.publish().data['foto_publica']['url']
        self.assertEqual(self.cliente(self.otro).delete(self.path).status_code, 404)
        with self.captureOnCommitCallbacks(execute=True):
            self.assertEqual(self.cliente(self.ciudadano).delete(self.path).status_code, 204)
        self.assertEqual(APIClient().get(url).status_code, 404)
        self.assertEqual(self.cliente(self.ciudadano).delete(self.path).status_code, 204)

    def test_inactive_account_does_not_expose_photo(self):
        url = self.publish().data['foto_publica']['url']
        self.ciudadano.is_active = False
        self.ciudadano.save(update_fields=['is_active'])
        self.assertEqual(APIClient().get(url).status_code, 404)

    def test_deactivation_during_processing_prevents_publication(self):
        real = photos.normalizar
        def deactivate(file, **kwargs):
            self.ciudadano.is_active = False
            self.ciudadano.save(update_fields=['is_active'])
            return real(file, **kwargs)
        with patch('core.public_avatars.normalizar', side_effect=deactivate):
            self.assertEqual(self.publish().status_code, 404)
        self.assertFalse(FotoPublicaPerfil.objects.exists())

    def test_public_feed_and_comments_include_optional_photo_without_n_plus_one(self):
        url = self.publish().data['foto_publica']['url']
        post = PublicacionComunidad.objects.create(autor=self.ciudadano, contenido='QA')
        ComentarioComunidad.objects.create(autor=self.ciudadano, publicacion=post, contenido='QA')
        with self.assertNumQueries(1):
            data = APIClient().get('/api/comunidad/publicaciones/').data
        self.assertEqual(data['results'][0]['foto_autor']['url'], url)
        self.assertNotIn('email', str(data))
        self.assertNotIn('usuario_id', str(data))
        comment = APIClient().get(f'/api/comunidad/publicaciones/{post.pk}/comentarios/').data
        self.assertEqual(comment['results'][0]['foto_autor']['url'], url)
        self.cliente(self.ciudadano).delete(self.path)
        self.assertIsNone(APIClient().get('/api/comunidad/publicaciones/').data['results'][0]['foto_autor'])

    def test_invalid_file_and_storage_failure_leave_no_record(self):
        file = SimpleUploadedFile('bad.svg', b'<svg/>', 'image/svg+xml')
        self.assertEqual(self.publish(archivo=file).status_code, 400)
        with patch('core.public_avatars.Path.mkdir', side_effect=OSError('unavailable')):
            self.assertEqual(self.publish().status_code, 503)
        self.assertFalse(FotoPublicaPerfil.objects.exists())
