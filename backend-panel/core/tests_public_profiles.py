from django.test import Client
from django.utils import timezone
from rest_framework.test import APIClient
from seguridad.tests import BaseRBAC, valor
from seguridad.models import BajaAdministrativa, EventoSeguridad
from seguridad.autorizacion import invalidar
from core.models import Ciudad, Tienda, PerfilPublicoEntidad, RolPermiso, Rol, Permiso, UsuarioRol


class PublicProfileTests(BaseRBAC):
    def setUp(self):
        city, _ = Ciudad.objects.get_or_create(nombre='Riohacha', departamento='La Guajira')
        self.store = Tienda.objects.create(entidad=self.entidad, ciudad=city, direccion='Dirección comercial QA', whatsapp='3009991234')
        self.url = f'/api/red/organizaciones/{self.entidad.pk}/perfil/'
        self.payload = {'descripcion': 'Organización sintética de protección animal', 'servicios': 'Orientación para adopción',
                        'telefono': '+57 300 123 4567', 'correo': 'publico@example.invalid',
                        'sitio_web': 'https://example.invalid/servicios', 'publicada': True, 'confirmar_publicacion': True}

    def listing(self):
        return APIClient().get('/api/red/organizaciones/')

    def test_no_copia_contactos_internos_y_borrador_no_es_publico(self):
        self.assertIsNone(self.listing().data[0]['perfil_publico'])
        self.assertNotIn('3009991234', str(self.listing().data))
        self.assertEqual(self.cliente(self.admin).put(self.url, {**self.payload, 'publicada': False, 'confirmar_publicacion': False}, format='json').status_code, 200)
        self.assertIsNone(self.listing().data[0]['perfil_publico'])
        self.assertEqual(self.cliente(self.ciudadano).get(self.url).status_code, 403)

    def test_publica_con_consentimiento_y_retirada_inmediata(self):
        self.assertEqual(self.cliente(self.admin).put(self.url, self.payload, format='json').status_code, 200)
        row = self.listing().data[0]['perfil_publico']
        self.assertEqual(row['telefono'], self.payload['telefono'])
        self.assertNotIn('editor', row)
        self.assertNotIn('confirmar_publicacion', row)
        self.assertEqual(self.cliente(self.admin).put(self.url, {**self.payload, 'publicada': False, 'confirmar_publicacion': False}, format='json').status_code, 200)
        self.assertIsNone(self.listing().data[0]['perfil_publico'])
        self.assertEqual(EventoSeguridad.objects.filter(accion='entidad.perfil_publico').count(), 2)
        self.assertEqual(self.listing()['Cache-Control'], 'no-store')

    def test_rechaza_sin_consentimiento_sin_descripcion_y_sitios_inseguros(self):
        client = self.cliente(self.admin)
        for change in ({'confirmar_publicacion': False}, {'descripcion': ''}, {'sitio_web': 'javascript:alert(1)'},
                       {'sitio_web': 'http://example.invalid/'}, {'sitio_web': 'https://user:password@example.invalid/'},
                       {'telefono': '<script>123</script>'}, {'correo': 'invalido'}, {'editor_id': self.ciudadano.pk}):
            with self.subTest(change=change):
                self.assertEqual(client.put(self.url, {**self.payload, **change}, format='json').status_code, 400)
        self.assertFalse(PerfilPublicoEntidad.objects.exists())

    def test_anonimo_no_modifica_y_permiso_configurable_se_revoca(self):
        self.assertEqual(APIClient().put(self.url, self.payload, format='json').status_code, 401)
        client = self.cliente(self.ciudadano)
        self.assertEqual(client.put(self.url, self.payload, format='json').status_code, 403)
        role = Rol.objects.get(codigo='CIUDADANO')
        assignment = RolPermiso.objects.create(rol=role, permiso=Permiso.objects.get(codigo='entidades.editar'))
        invalidar()
        self.assertEqual(client.put(self.url, self.payload, format='json').status_code, 200)
        assignment.delete()
        invalidar()
        self.assertEqual(client.put(self.url, self.payload, format='json').status_code, 403)

    def test_verificacion_y_baja_se_aplican_al_directorio(self):
        client = self.cliente(self.admin)
        self.assertEqual(client.put(self.url, self.payload, format='json').status_code, 200)
        self.entidad.estado_verificacion = valor('estado_verificacion', 'Pendiente')
        self.entidad.save(update_fields=['estado_verificacion'])
        self.assertEqual(self.listing().data, [])
        self.assertEqual(client.put(self.url, self.payload, format='json').status_code, 400)
        self.entidad.estado_verificacion = valor('estado_verificacion', 'Verificada')
        self.entidad.save(update_fields=['estado_verificacion'])
        BajaAdministrativa.objects.create(tipo='entidades', objeto_id=self.entidad.pk, activo=False, autor=self.admin, motivo='QA')
        self.assertEqual(self.listing().data, [])
        self.assertEqual(client.put(self.url, {**self.payload, 'publicada': False}, format='json').status_code, 400)

    def test_directorio_no_genera_consulta_por_cada_perfil(self):
        self.assertEqual(self.cliente(self.admin).put(self.url, self.payload, format='json').status_code, 200)
        with self.assertNumQueries(3):
            response = self.listing()
        self.assertEqual(response.status_code, 200)

    def test_panel_csrf_edicion_y_retirada(self):
        url = f'/panel/organizaciones/{self.entidad.pk}/perfil-publico/'
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin)
        self.assertEqual(client.post(url, self.payload).status_code, 403)
        page = client.get(url)
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'Ficha pública de la organización')
        self.assertContains(client.get('/panel/areas/organizaciones/'), url)
        token = client.cookies['csrftoken'].value
        self.assertEqual(client.post(url, {**self.payload, 'csrfmiddlewaretoken': token}).status_code, 302)
        self.assertIsNotNone(self.listing().data[0]['perfil_publico'])
        self.assertEqual(client.post(url, {**self.payload, 'publicada': False, 'confirmar_publicacion': False, 'csrfmiddlewaretoken': token}).status_code, 302)
        self.assertIsNone(self.listing().data[0]['perfil_publico'])
        client.force_login(self.ciudadano)
        self.assertEqual(client.get(url).status_code, 403)

    def test_auditoria_legible_y_tolerante_a_registros_incompletos(self):
        from types import SimpleNamespace
        from seguridad.web.presentacion_eventos import descripcion_reciente
        for before, after, text in (({}, {'publicada': True}, 'Publicó'),
                                    ({'publicada': True}, {'publicada': True}, 'Actualizó'),
                                    ({'publicada': True}, {'publicada': False}, 'Retiró'),
                                    (None, None, 'borrador')):
            event = SimpleNamespace(accion='entidad.perfil_publico', datos={'anterior': before, 'nuevo': after})
            self.assertIn(text, descripcion_reciente(event))
