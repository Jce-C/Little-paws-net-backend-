from io import BytesIO
from tempfile import TemporaryDirectory
from unittest.mock import patch
from PIL import Image
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings
from rest_framework.test import APIClient
from seguridad.tests import BaseRBAC, valor
from seguridad.models import BajaAdministrativa, EventoSeguridad
from seguridad.autorizacion import invalidar
from core.models import Ciudad, Fundacion, Tienda, LogoPublicoEntidad, Rol, Permiso, RolPermiso
from . import public_logos as logos


def upload():
    stream = BytesIO()
    exif = Image.Exif()
    exif[270] = 'Dato privado de prueba'
    Image.new('RGB', (1800, 900), 'green').save(stream, 'JPEG', exif=exif)
    return SimpleUploadedFile('marca-original.jpg', stream.getvalue(), 'image/jpeg')


class PublicLogoTests(BaseRBAC):
    def setUp(self):
        cache.clear()
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.settings_override = override_settings(LPN_PRIVATE_ROOT=self.temp.name)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        city = Ciudad.objects.create(nombre='Ciudad logo QA', departamento='QA')
        self.foundation = Fundacion.objects.create(entidad=self.entidad, ciudad=city, nit='QA-LOGO')
        self.store = Tienda.objects.create(entidad=self.ajena, ciudad=city, direccion='Dirección QA', whatsapp='Contacto interno QA')
        self.manage = f'/api/red/organizaciones/{self.entidad.pk}/logo-publico/'
        self.public = f'/api/red/organizaciones/{self.entidad.pk}/logo/'

    def publish(self, actor=None, **values):
        return self.cliente(actor or self.admin).post(self.manage, {
            'archivo': upload(), 'confirmar_publicacion': 'true', **values,
        }, format='multipart')

    def listing(self):
        return APIClient().get('/api/red/organizaciones/')

    def test_publication_is_small_webp_without_metadata_and_directory_has_no_n_plus_one(self):
        response = self.publish()
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(set(response.data['logo']), {'url', 'ancho', 'alto', 'bytes'})
        self.assertLessEqual(response.data['logo']['bytes'], 96 * 1024)
        response = APIClient().get(self.public)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Cache-Control'], 'no-store')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['Content-Type'], 'image/webp')
        with Image.open(BytesIO(response.content)) as image:
            self.assertEqual(image.size, (512, 256))
            self.assertEqual(dict(image.getexif()), {})
        self.assertNotIn(b'Dato privado', response.content)
        with self.assertNumQueries(3):
            listing = self.listing()
        row = next(row for row in listing.data if row['id'] == self.entidad.pk)
        self.assertEqual(row['logo']['ancho'], 512)
        self.assertNotIn('clave', str(row['logo']))
        self.assertNotIn('publicador', str(row['logo']))
        event = EventoSeguridad.objects.get(accion='entidad.logo_publicar')
        from seguridad.web.presentacion_eventos import descripcion_reciente, informacion_evento
        self.assertIn('logo', descripcion_reciente(event))
        self.assertIn('512', informacion_evento(event))
        self.assertNotIn('clave', str(event.datos))

    def test_anonymous_and_roles_without_permission_cannot_publish(self):
        self.assertEqual(APIClient().post(self.manage).status_code, 401)
        self.assertEqual(self.publish(self.ciudadano).status_code, 403)
        self.assertEqual(self.publish(confirmar_publicacion='false').status_code, 400)
        self.assertFalse(LogoPublicoEntidad.objects.exists())

    def test_permission_can_be_granted_to_citizen_and_revoked(self):
        assignment = RolPermiso.objects.create(rol=Rol.objects.get(codigo='CIUDADANO'), permiso=Permiso.objects.get(codigo='entidades.editar'))
        invalidar()
        self.assertEqual(self.publish(self.ciudadano).status_code, 201)
        assignment.delete()
        invalidar()
        self.assertEqual(self.publish(self.ciudadano).status_code, 403)
        self.assertEqual(self.cliente(self.ciudadano).delete(self.manage).status_code, 403)

    def test_revocation_during_normalization_prevents_file_and_database_write(self):
        real = logos.normalizar
        def revoke(file, **kwargs):
            RolPermiso.objects.filter(rol__codigo='ADMIN_SEGURIDAD', permiso__codigo='entidades.editar').delete()
            return real(file, **kwargs)
        with patch('core.public_logos.normalizar', side_effect=revoke):
            self.assertEqual(self.publish().status_code, 403)
        self.assertFalse(LogoPublicoEntidad.objects.exists())
        self.assertFalse(logos.raiz().exists())

    def test_replacement_changes_version_and_removes_obsolete_copy(self):
        first = self.publish().data['logo']['url']
        old = logos.ruta(LogoPublicoEntidad.objects.get().clave)
        with self.captureOnCommitCallbacks(execute=True):
            second = self.publish()
        self.assertEqual(second.status_code, 201)
        self.assertNotEqual(first, second.data['logo']['url'])
        self.assertFalse(old.exists())
        self.assertEqual(LogoPublicoEntidad.objects.count(), 1)

    def test_withdrawal_stops_serving_and_is_idempotent(self):
        self.assertEqual(self.publish().status_code, 201)
        path = logos.ruta(LogoPublicoEntidad.objects.get().clave)
        with self.captureOnCommitCallbacks(execute=True):
            self.assertEqual(self.cliente(self.admin).delete(self.manage).status_code, 204)
        self.assertFalse(path.exists())
        response = APIClient().get(self.public)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response['Cache-Control'], 'no-store')
        self.assertIsNone(next(row for row in self.listing().data if row['id'] == self.entidad.pk)['logo'])
        self.assertEqual(self.cliente(self.admin).delete(self.manage).status_code, 204)
        self.assertEqual(EventoSeguridad.objects.filter(accion='entidad.logo_retirar').count(), 1)

    def test_unverified_or_deactivated_organization_never_serves_its_logo(self):
        self.assertEqual(self.publish().status_code, 201)
        self.entidad.estado_verificacion = valor('estado_verificacion', 'Pendiente')
        self.entidad.save(update_fields=['estado_verificacion'])
        self.assertEqual(APIClient().get(self.public).status_code, 404)
        self.assertEqual(self.publish().status_code, 400)
        self.entidad.estado_verificacion = valor('estado_verificacion', 'Verificada')
        self.entidad.save(update_fields=['estado_verificacion'])
        BajaAdministrativa.objects.create(tipo='entidades', objeto_id=self.entidad.pk, activo=False, autor=self.admin, motivo='QA')
        self.assertEqual(APIClient().get(self.public).status_code, 404)
        self.assertFalse(any(row['id'] == self.entidad.pk for row in self.listing().data))

    def test_fake_svg_and_traversal_are_rejected(self):
        self.assertEqual(self.publish(archivo=SimpleUploadedFile('x.png', b'<svg/>', 'image/png')).status_code, 400)
        self.assertEqual(self.publish(publicador_id=str(self.otro.pk)).status_code, 400)
        from rest_framework.exceptions import ValidationError
        for key in ('../marca.webp', '/tmp/marca.webp', 'marca.svg'):
            with self.assertRaises(ValidationError):
                logos.ruta(key)

    def test_storage_failure_does_not_create_a_publication(self):
        with patch('core.public_logos.raiz', side_effect=OSError('synthetic')):
            self.assertEqual(self.publish().status_code, 503)
        self.assertFalse(LogoPublicoEntidad.objects.exists())

    def test_panel_post_has_csrf_and_same_publication_withdrawal_policy(self):
        path = f'/panel/organizaciones/{self.entidad.pk}/logo/'
        web = Client(enforce_csrf_checks=True)
        web.force_login(self.admin)
        self.assertEqual(web.post(path, {'archivo': upload(), 'confirmar_publicacion': True}).status_code, 403)
        self.assertEqual(web.get(path).status_code, 200)
        self.assertContains(web.get('/panel/areas/organizaciones/'), path)
        token = web.cookies['csrftoken'].value
        self.assertEqual(web.post(path, {'archivo': upload(), 'confirmar_publicacion': True, 'csrfmiddlewaretoken': token}).status_code, 302)
        self.assertContains(web.get(path), 'width="128" height="128"')
        self.assertEqual(web.post(path + '?modo=retirar', {'confirmar_retirada': True, 'csrfmiddlewaretoken': token}).status_code, 302)
        self.assertEqual(APIClient().get(self.public).status_code, 404)
        web.force_login(self.ciudadano)
        self.assertEqual(web.get(path).status_code, 403)
