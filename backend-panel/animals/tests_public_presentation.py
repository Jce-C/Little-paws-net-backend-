from django.test import Client
from django.utils import timezone
from rest_framework.test import APIClient
from core.models import Ciudad, Fundacion, EntidadMiembroRol
from seguridad.tests import BaseRBAC, miembro_con_rol, valor
from seguridad.models import EventoSeguridad
from .models import Mascota, CustodiaMascota, PresentacionPublicaMascota


class PresentacionPublicaTests(BaseRBAC):
    def setUp(self):
        city, _ = Ciudad.objects.get_or_create(nombre='Riohacha', departamento='La Guajira')
        self.foundation = Fundacion.objects.create(entidad=self.entidad, ciudad=city, nit='QA-EDITORIAL')
        self.other = Fundacion.objects.create(entidad=self.ajena, ciudad=city, nit='QA-EDITORIAL-OTRA')
        self.pet = Mascota.objects.create(nombre='Mascota sintética', descripcion_especie='Perro', estado_mascota=valor('estado_mascota', 'En adopción'))
        self.custody = CustodiaMascota.objects.create(mascota=self.pet, fundacion=self.foundation, usuario_registrador=self.ana, fecha_inicio=timezone.now())
        miembro_con_rol(self.ana, self.entidad, 'GESTOR_ADOPCIONES')
        miembro_con_rol(self.otro, self.ajena, 'GESTOR_ADOPCIONES')
        self.url = f'/api/mascotas/{self.pet.pk}/presentacion-publica/'
        self.public = f'/api/adopcion/mascotas/{self.pet.pk}/'
        self.values = {'descripcion': 'Es tranquila y disfruta paseos cortos.', 'cuidados': 'Alimentación autorizada según orientación de la fundación.',
                       'espacio': 'Un hogar con zona segura de descanso.', 'publicada': True, 'confirmar_publicacion': True}

    def save(self, actor=None, **values):
        return self.cliente(actor or self.ana).put(self.url, {**self.values, **values}, format='json')

    def test_publicacion_whitelist_y_catalogo_compatibles(self):
        self.assertEqual(self.save().status_code, 200)
        response = APIClient().get(self.public)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['presentacion'], {key: self.values[key] for key in ('descripcion', 'cuidados', 'espacio')})
        self.assertEqual(response['Cache-Control'], 'no-store')
        catalog = APIClient().get('/api/adopcion/catalogo/')
        self.assertEqual(catalog.data['results'][0]['presentacion']['descripcion'], self.values['descripcion'])
        self.assertNotIn('editor', str(response.data['presentacion']))
        self.assertTrue(EventoSeguridad.objects.filter(accion='mascotas.presentacion_publica').exists())

    def test_borrador_retirada_y_ausencia_de_cuidados_no_inventa_datos(self):
        self.assertIsNone(APIClient().get(self.public).data['presentacion'])
        self.assertEqual(self.save(publicada=False, confirmar_publicacion=False).status_code, 200)
        self.assertIsNone(APIClient().get(self.public).data['presentacion'])
        self.assertEqual(self.save(cuidados='', espacio='').status_code, 200)
        self.assertEqual(APIClient().get(self.public).data['presentacion']['cuidados'], '')
        self.assertEqual(self.save(publicada=False, confirmar_publicacion=False).status_code, 200)
        self.assertIsNone(APIClient().get(self.public).data['presentacion'])

    def test_autorizacion_por_fundacion_y_revocacion(self):
        self.assertEqual(APIClient().put(self.url, self.values, format='json').status_code, 401)
        for actor in (self.ciudadano, self.otro):
            self.assertEqual(self.save(actor).status_code, 403)
            self.assertEqual(self.cliente(actor).get(self.url).status_code, 403)
        self.assertEqual(self.save().status_code, 200)
        EntidadMiembroRol.objects.filter(miembro__usuario=self.ana, rol__codigo='GESTOR_ADOPCIONES').update(fecha_revocacion=timezone.now())
        self.assertEqual(self.save().status_code, 403)

    def test_confirmacion_descripcion_limites_y_campos_privados(self):
        for change in ({'confirmar_publicacion': False}, {'descripcion': ''}, {'descripcion': 'x' * 1001},
                       {'cuidados': 'x' * 2001}, {'espacio': 'x' * 601}, {'expediente': 'No aceptar'}, {'editor_id': self.otro.pk}):
            with self.subTest(keys=list(change)):
                self.assertEqual(self.save(**change).status_code, 400)
        self.assertFalse(PresentacionPublicaMascota.objects.exists())
        from django.utils.translation import override
        from .public_presentation import PresentacionEntrada
        with override('en'):
            serializer = PresentacionEntrada(data={**self.values, 'confirmar_publicacion': False})
            self.assertFalse(serializer.is_valid())
            self.assertIn('Confirm this text', str(serializer.errors))

    def test_cambio_de_custodia_no_revela_textos_ni_borrador_anterior(self):
        self.assertEqual(self.save(publicada=False, confirmar_publicacion=False).status_code, 200)
        self.custody.fecha_fin = timezone.now()
        self.custody.save(update_fields=['fecha_fin'])
        CustodiaMascota.objects.create(mascota=self.pet, fundacion=self.other, usuario_registrador=self.otro, fecha_inicio=timezone.now())
        self.assertIsNone(APIClient().get(self.public).data['presentacion'])
        self.assertEqual(self.cliente(self.otro).get(self.url).data['descripcion'], '')
        self.assertEqual(self.save(self.otro, descripcion='Presentación nueva y autorizada').status_code, 200)
        event = EventoSeguridad.objects.filter(accion='mascotas.presentacion_publica').first()
        self.assertEqual(event.datos['anterior'], {})
        self.assertEqual(APIClient().get(self.public).data['presentacion']['descripcion'], 'Presentación nueva y autorizada')

    def test_no_publica_ni_devuelve_ficha_si_no_esta_disponible(self):
        self.pet.dueno = self.ciudadano
        self.pet.save(update_fields=['dueno'])
        self.assertEqual(self.save().status_code, 400)
        self.assertEqual(APIClient().get(self.public).status_code, 404)

    def test_catalogo_no_hace_una_consulta_por_cada_presentacion(self):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext
        self.assertEqual(self.save().status_code, 200)
        with CaptureQueriesContext(connection) as first:
            APIClient().get('/api/adopcion/catalogo/')
        pet = Mascota.objects.create(nombre='Segunda sintética', descripcion_especie='Perro', estado_mascota=self.pet.estado_mascota)
        CustodiaMascota.objects.create(mascota=pet, fundacion=self.foundation, usuario_registrador=self.ana, fecha_inicio=timezone.now())
        PresentacionPublicaMascota.objects.create(mascota=pet, fundacion=self.foundation, editor=self.ana, descripcion='Otra presentación autorizada', publicada=True)
        with CaptureQueriesContext(connection) as second:
            response = APIClient().get('/api/adopcion/catalogo/')
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(len(first), len(second))

    def test_panel_csrf_edicion_cancelar_y_permiso(self):
        url = f'/panel/mascotas/{self.pet.pk}/presentacion/'
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.ana)
        self.assertEqual(client.post(url, self.values).status_code, 403)
        self.assertContains(client.get(url), 'Guardar presentación')
        self.assertContains(client.get(url), 'Cancelar')
        csrf = client.cookies['csrftoken'].value
        self.assertEqual(client.post(url, {**self.values, 'csrfmiddlewaretoken': csrf}).status_code, 302)
        self.assertEqual(client.post(url, {**self.values, 'publicada': False, 'confirmar_publicacion': False, 'csrfmiddlewaretoken': csrf}).status_code, 302)
        self.assertIsNone(APIClient().get(self.public).data['presentacion'])
        client.force_login(self.otro)
        self.assertEqual(client.get(url).status_code, 403)
