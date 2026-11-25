from importlib import import_module
from django.apps import apps
from django.core.cache import cache
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient
from core.models import Ciudad, Fundacion, ProgramaAyuda, RolPermiso
from seguridad.models import EventoSeguridad
from seguridad.tests import BaseRBAC


class HelpProgramTests(BaseRBAC):
    def setUp(self):
        cache.clear()
        import_module('seguridad.migrations.0020_comunidad_y_ayudas').cargar(apps, connection.schema_editor())
        city = Ciudad.objects.create(nombre='Ciudad programa QA', departamento='QA')
        self.foundation = Fundacion.objects.create(entidad=self.entidad, ciudad=city, nit='QA-PROGRAM', acepta_voluntarios=True)
        self.other = Fundacion.objects.create(entidad=self.ajena, ciudad=city, nit='QA-PROGRAM-OTHER')
        self.path = f'/api/ayudas/organizaciones/{self.foundation.pk}/programa/'
        self.client_manager = self.cliente(self.carlos)

    def body(self):
        return {
            'version': self.client_manager.get(self.path).data['version'],
            'actividades': [{'titulo': 'Paseos QA', 'descripcion': 'Actividad ficticia supervisada.', 'horario': 'Por acordar', 'requisitos': 'Inducción de la organización'}],
            'canales': [{'titulo': 'Sitio QA', 'descripcion': 'Información oficial del ejemplo', 'url': 'https://example.invalid/ayudas'}],
            'publicada': True, 'confirmar_publicacion': True,
        }

    def public(self):
        return next(row for row in APIClient().get('/api/red/organizaciones/').data if row['id'] == self.foundation.pk)

    def test_publish_draft_withdraw_and_explicit_public_whitelist(self):
        self.assertIsNone(self.public()['programa_ayuda'])
        body = self.body()
        response = self.client_manager.patch(self.path, body, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response['Cache-Control'], 'no-store')
        public = self.public()['programa_ayuda']
        self.assertEqual(set(public), {'actividades', 'canales'})
        self.assertEqual(public['actividades'], body['actividades'])
        self.assertNotIn('editor', str(public))
        body.update(version=response.data['version'], publicada=False, confirmar_publicacion=False)
        self.assertEqual(self.client_manager.patch(self.path, body, format='json').status_code, 200)
        self.assertIsNone(self.public()['programa_ayuda'])
        self.assertEqual(ProgramaAyuda.objects.get().actividades, body['actividades'])
        self.assertEqual(EventoSeguridad.objects.filter(accion='ayudas.programa_publico').count(), 2)

    def test_anonymous_citizen_other_foundation_and_revocation_are_rejected(self):
        self.assertEqual(APIClient().get(self.path).status_code, 401)
        self.assertEqual(self.cliente(self.ciudadano).get(self.path).status_code, 403)
        self.assertEqual(self.client_manager.get(f'/api/ayudas/organizaciones/{self.other.pk}/programa/').status_code, 403)
        body = self.body()
        RolPermiso.objects.filter(rol__codigo='RESPONSABLE_SECUNDARIO', permiso__codigo='ayudas.gestionar').delete()
        self.assertEqual(self.client_manager.patch(self.path, body, format='json').status_code, 403)
        self.assertFalse(ProgramaAyuda.objects.exists())

    def test_stale_version_does_not_overwrite_newer_publication(self):
        body = self.body()
        self.assertEqual(self.client_manager.patch(self.path, body, format='json').status_code, 200)
        body['actividades'][0]['titulo'] = 'No sobrescribir'
        self.assertEqual(self.client_manager.patch(self.path, body, format='json').status_code, 409)
        self.assertEqual(ProgramaAyuda.objects.get().actividades[0]['titulo'], 'Paseos QA')

    def test_consent_limits_and_nested_private_fields_are_validated(self):
        for change in (
            {'confirmar_publicacion': False},
            {'actividades': [], 'canales': []},
            {'actividades': self.body()['actividades'] * 9},
            {'canales': [{'titulo': 'Canal QA', 'descripcion': 'QA', 'url': 'http://example.invalid'}]},
            {'canales': [{'titulo': 'Canal QA', 'descripcion': 'QA', 'url': 'https://user:secret@example.invalid'}]},
            {'actividades': [{**self.body()['actividades'][0], 'usuario_id': self.otro.pk}]},
            {'actividades': [{**self.body()['actividades'][0], 'requisitos': ''}]},
        ):
            body = {**self.body(), **change}
            self.assertEqual(self.client_manager.patch(self.path, body, format='json').status_code, 400)
        self.assertFalse(ProgramaAyuda.objects.exists())

    def test_closed_volunteer_intake_hides_activities_but_preserves_official_channels(self):
        self.assertEqual(self.client_manager.patch(self.path, self.body(), format='json').status_code, 200)
        self.foundation.acepta_voluntarios = False
        self.foundation.save(update_fields=['acepta_voluntarios'])
        self.assertEqual(self.public()['programa_ayuda']['actividades'], [])
        self.assertEqual(len(self.public()['programa_ayuda']['canales']), 1)
        self.assertEqual(self.client_manager.patch(self.path, self.body(), format='json').status_code, 400)

    def test_directory_query_count_does_not_grow_with_programs(self):
        with CaptureQueriesContext(connection) as first:
            APIClient().get('/api/red/organizaciones/')
        ProgramaAyuda.objects.create(fundacion=self.foundation, editor=self.carlos, publicada=True)
        ProgramaAyuda.objects.create(fundacion=self.other, editor=self.admin, publicada=True)
        with CaptureQueriesContext(connection) as second:
            APIClient().get('/api/red/organizaciones/')
        self.assertEqual(len(first), len(second))

    def test_panel_form_is_scoped_and_csrf_protected(self):
        web = Client(enforce_csrf_checks=True)
        web.force_login(self.carlos)
        path = f'/panel/ayudas/{self.foundation.pk}/programa/'
        self.assertEqual(web.get(path).status_code, 200)
        self.assertEqual(web.post(path, {}).status_code, 403)
        form = {
            'version': self.body()['version'],
            'actividades-TOTAL_FORMS': '8', 'actividades-INITIAL_FORMS': '0',
            'canales-TOTAL_FORMS': '4', 'canales-INITIAL_FORMS': '0',
            'actividades-0-titulo': 'Actividad desde panel QA',
            'actividades-0-descripcion': 'Actividad ficticia',
            'actividades-0-horario': 'Por acordar',
            'actividades-0-requisitos': 'Inducción',
            'publicada': 'on', 'confirmar_publicacion': 'on',
        }
        form['csrfmiddlewaretoken'] = web.cookies['csrftoken'].value
        response = web.post(path, form)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.public()['programa_ayuda']['actividades'][0]['titulo'], 'Actividad desde panel QA')
        response = web.post(path, form)
        self.assertEqual(response.status_code, 409, [response.context['estado_programa'].errors, [(title, group.errors) for title, group in response.context['grupos_programa']]])
        web.force_login(self.ciudadano)
        self.assertEqual(web.get(path).status_code, 403)

    def test_activity_interest_keeps_snapshot_and_rejects_closed_or_withdrawn_activity(self):
        self.assertEqual(self.client_manager.patch(self.path, self.body(), format='json').status_code, 200)
        person = self.cliente(self.ciudadano)
        path = '/api/ayudas/intereses/'
        body = {'fundacion_id': self.foundation.pk, 'modalidad': 'voluntariado', 'actividad': 'Paseos QA', 'mensaje': 'Mi disponibilidad ficticia'}
        self.assertEqual(person.post(path, body, format='json').status_code, 201)
        self.assertEqual(person.post(path, body, format='json').status_code, 200)
        self.assertEqual(person.get(path).data[0]['actividad'], 'Paseos QA')
        profile = ProgramaAyuda.objects.get()
        profile.publicada = False
        profile.save(update_fields=['publicada'])
        self.assertEqual(self.cliente(self.otro).post(path, body, format='json').status_code, 400)
        self.foundation.acepta_voluntarios = False
        self.foundation.save(update_fields=['acepta_voluntarios'])
        self.assertEqual(person.post(path, {**body, 'actividad': ''}, format='json').status_code, 400)
