from importlib import import_module
from django.apps import apps
from django.core.cache import cache
from django.db import connection
from rest_framework.test import APIClient
from core.models import PublicacionComunidad, ComentarioComunidad, ReaccionComunidad, InteresAyuda, Ciudad, Fundacion, RolPermiso, Rol, Permiso
from seguridad.models import BajaAdministrativa
from seguridad.tests import BaseRBAC, valor


class CommunityTests(BaseRBAC):
    def setUp(self):
        cache.clear()
        import_module('seguridad.migrations.0020_comunidad_y_ayudas').cargar(apps, connection.schema_editor())
        self.path = '/api/comunidad/publicaciones/'
        self.post = PublicacionComunidad.objects.create(autor=self.ciudadano, contenido='Mensaje público QA')

    def test_public_read_has_no_personal_contacts_and_creation_requires_permission(self):
        response = APIClient().get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('email', str(response.data))
        self.assertEqual(response['Cache-Control'], 'no-store')
        self.assertFalse(response.data['puede_publicar'])
        self.assertEqual(APIClient().post(self.path, {'contenido': 'QA'}, format='json').status_code, 401)
        client = self.cliente(self.ciudadano)
        self.assertEqual(client.post(self.path, {'contenido': '   '}, format='json').status_code, 400)
        response = client.post(self.path, {'contenido': 'Nueva publicación QA', 'autor_id': self.otro.pk}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(PublicacionComunidad.objects.get(pk=response.data['id']).autor, self.ciudadano)
        RolPermiso.objects.filter(rol__codigo='CIUDADANO', permiso__codigo='comunidad.participar').delete()
        self.assertEqual(client.post(self.path, {'contenido': 'No guardar'}, format='json').status_code, 403)
        self.assertFalse(client.get(self.path).data['puede_publicar'])

    def test_reactions_are_idempotent_and_belong_to_current_user(self):
        path = f'{self.path}{self.post.pk}/reaccion/'
        client = self.cliente(self.ciudadano)
        self.assertEqual(client.post(path, {}, format='json').data['total'], 1)
        self.assertEqual(client.post(path, {}, format='json').data['total'], 1)
        self.assertEqual(self.cliente(self.otro).post(path, {}, format='json').data['total'], 2)
        self.assertEqual(client.delete(path).data['total'], 1)
        self.assertEqual(client.delete(path).data['total'], 1)
        self.assertEqual(ReaccionComunidad.objects.get().usuario, self.otro)

    def test_comments_and_replies_cannot_cross_posts_or_reply_to_reply(self):
        client = self.cliente(self.ciudadano)
        path = f'{self.path}{self.post.pk}/comentarios/'
        response = client.post(path, {'contenido':'Comentario QA'}, format='json')
        self.assertEqual(response.status_code, 201)
        parent = response.data['id']
        response = client.post(path, {'contenido':'Respuesta QA', 'respuesta_a':parent}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(client.post(path, {'contenido':'No anidar', 'respuesta_a':response.data['id']}, format='json').status_code, 404)
        other = PublicacionComunidad.objects.create(autor=self.otro, contenido='Otro mensaje QA')
        self.assertEqual(client.post(f'{self.path}{other.pk}/comentarios/', {'contenido':'No cruzar', 'respuesta_a':parent}, format='json').status_code, 404)
        self.assertEqual(len(APIClient().get(path).data['results']), 2)

    def test_moderation_can_be_granted_to_any_role_and_withdrawal_hides_thread(self):
        path = f'{self.path}{self.post.pk}/retirar/'
        other = self.cliente(self.otro)
        self.assertEqual(other.post(path, {'motivo':'Moderación QA'}, format='json').status_code, 403)
        RolPermiso.objects.create(rol=Rol.objects.get(codigo='CIUDADANO'), permiso=Permiso.objects.get(codigo='comunidad.moderar'))
        self.assertEqual(other.post(path, {'motivo':'Moderación QA'}, format='json').status_code, 200)
        self.assertEqual(APIClient().get(self.path).data['results'], [])
        self.assertEqual(APIClient().get(f'{self.path}{self.post.pk}/comentarios/').status_code, 404)
        self.assertTrue(PublicacionComunidad.objects.get(pk=self.post.pk).oculta)

    def test_feed_pages_are_bounded_and_do_not_repeat(self):
        PublicacionComunidad.objects.bulk_create([PublicacionComunidad(autor=self.ciudadano, contenido=f'QA {i}') for i in range(22)])
        client = APIClient()
        first = client.get(self.path).data
        second = client.get(self.path, {'antes':first['antes']}).data
        self.assertEqual(len(first['results']), 20)
        self.assertEqual(len(second['results']), 3)
        self.assertFalse({r['id'] for r in first['results']} & {r['id'] for r in second['results']})
        self.assertIsNone(second['antes'])

    def test_moderator_can_withdraw_own_post_without_participation_permission(self):
        RolPermiso.objects.filter(rol__codigo='CIUDADANO', permiso__codigo='comunidad.participar').delete()
        RolPermiso.objects.create(rol=Rol.objects.get(codigo='CIUDADANO'), permiso=Permiso.objects.get(codigo='comunidad.moderar'))
        response = self.cliente(self.ciudadano).post(f'{self.path}{self.post.pk}/retirar/', {'motivo':'Moderación propia QA'}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_help_interest_is_owned_idempotent_and_requires_verified_entity(self):
        city = Ciudad.objects.create(nombre='Ciudad QA', departamento='QA')
        foundation = Fundacion.objects.create(entidad=self.entidad, ciudad=city, nit='QA-COMMUNITY')
        client = self.cliente(self.ciudadano)
        body = {'fundacion_id': foundation.pk, 'modalidad':'especie', 'mensaje':'Ofrecimiento sintético QA'}
        path = '/api/ayudas/intereses/'
        self.assertEqual(client.post(path, body, format='json').status_code, 201)
        self.assertEqual(client.post(path, body, format='json').status_code, 200)
        self.assertEqual(InteresAyuda.objects.count(), 1)
        self.assertEqual(self.cliente(self.otro).get(path).data, [])
        self.assertEqual(len(client.get(path).data), 1)
        body['mensaje'] = 'No reemplazar silenciosamente'
        self.assertEqual(client.post(path, body, format='json').status_code, 409)
        BajaAdministrativa.objects.create(tipo='entidades', objeto_id=foundation.pk, autor=self.admin, activo=False, motivo='QA')
        self.assertEqual(client.post(path, body, format='json').status_code, 404)

    def test_help_management_is_scoped_and_optimistic_with_private_offers(self):
        city = Ciudad.objects.create(nombre='Ciudad gestión QA', departamento='QA')
        foundation = Fundacion.objects.create(entidad=self.entidad, ciudad=city, nit='QA-MANAGE')
        other = Fundacion.objects.create(entidad=self.ajena, ciudad=city, nit='QA-OTHER')
        manager = self.cliente(self.carlos)
        path = f'/api/ayudas/organizaciones/{foundation.pk}/'
        self.assertEqual([row['id'] for row in manager.get('/api/ayudas/organizaciones/').data], [foundation.pk])
        self.assertEqual(manager.get(f'/api/ayudas/organizaciones/{other.pk}/').status_code, 403)
        self.assertEqual(self.cliente(self.ciudadano).get(path).status_code, 403)
        InteresAyuda.objects.create(usuario=self.ciudadano, fundacion=foundation, modalidad='especie', mensaje='Mensaje privado QA')
        data = manager.get(path).data
        self.assertEqual(data['ofrecimientos'][0]['mensaje'], 'Mensaje privado QA')
        self.assertNotIn('email', str(data))
        body = {'version':data['version'], 'acepta_voluntarios':True, 'necesidades_ayuda':'Alimentos sellados'}
        updated = manager.patch(path, body, format='json')
        self.assertEqual(updated.status_code, 200)
        self.assertNotEqual(updated.data['version'], data['version'])
        self.assertEqual(manager.patch(path, body, format='json').status_code, 409)
        self.assertEqual(Fundacion.objects.get(pk=foundation.pk).necesidades_ayuda, 'Alimentos sellados')
        RolPermiso.objects.filter(rol__codigo='RESPONSABLE_SECUNDARIO', permiso__codigo='ayudas.gestionar').delete()
        self.assertEqual(manager.get(path).status_code, 403)
        self.assertEqual(manager.patch(path, updated.data, format='json').status_code, 403)

    def test_interest_notifies_responsible_only_once(self):
        from core.models import Notificacion
        city = Ciudad.objects.create(nombre='Ciudad aviso QA', departamento='QA')
        foundation = Fundacion.objects.create(entidad=self.entidad, ciudad=city, nit='QA-NOTIFY', acepta_voluntarios=True)
        client = self.cliente(self.ciudadano)
        body = {'fundacion_id':foundation.pk, 'modalidad':'voluntariado', 'mensaje':'Interés sintético QA'}
        for _ in range(2):
            self.assertIn(client.post('/api/ayudas/intereses/', body, format='json').status_code, [200, 201])
        notices = Notificacion.objects.filter(usuario=self.ana, tipo_notificacion__nombre='Interés de ayuda')
        self.assertEqual(notices.count(), 1)
