import copy
import os
from unittest.mock import patch
from cryptography.fernet import Fernet
from django.core.exceptions import ImproperlyConfigured
from django.test import Client, override_settings
from django.utils import timezone
from rest_framework.test import APIClient
from animals.models import CustodiaMascota, Mascota
from core.models import Ciudad, Fundacion, UsuarioRol
from seguridad.tests import BaseRBAC, valor, miembro_con_rol
from seguridad.autorizacion import invalidar
from seguridad.servicios import tomar
from seguridad.models import EventoSeguridad
from .models import EvaluacionAdopcion, SolicitudAdopcion
from .questionnaire import consultar, VERSION


def respuestas():
    return dict(nombre='Persona QA ficticia', documento='QA-000-PRIVADO', telefono='0000000000',
        email='qa@example.invalid', direccion='Dirección ficticia QA', vivienda='casa', tenencia='propia',
        seguridad_espacio='Ventanas protegidas con mallas', personas_hogar=2, acuerdo_hogar=True,
        tiempo_cuidado='diario', recursos_cuidado='disponibles', cuidados_especiales='si', seguimiento='si',
        mascotas_actuales=False, experiencia_previa=False, motivo='Quiero ofrecer un hogar responsable.',
        datos_correctos=True, autoriza_evaluacion=True, version=VERSION)


class EvaluacionTests(BaseRBAC):
    url = '/api/adopcion/solicitudes/evaluacion/'

    def setUp(self):
        key = patch.dict(os.environ, {'LPN_DATA_KEY': Fernet.generate_key().decode()})
        key.start(); self.addCleanup(key.stop)
        city, _ = Ciudad.objects.get_or_create(nombre='Riohacha', departamento='La Guajira')
        self.foundation = Fundacion.objects.create(entidad=self.entidad, ciudad=city, nit='QA-EVALUACION')
        self.pet = Mascota.objects.create(nombre='Mascota QA evaluación', descripcion_especie='Perro',
            estado_mascota=valor('estado_mascota', 'En adopción'))
        CustodiaMascota.objects.create(mascota=self.pet, fundacion=self.foundation,
            usuario_registrador=self.ana, fecha_inicio=timezone.now())
        miembro_con_rol(self.carlos, self.entidad, 'GESTOR_ADOPCIONES')
        invalidar()
        self.api = self.cliente(self.ciudadano)
        self.payload = {'id_mascota': self.pet.pk, 'evaluacion': respuestas()}

    def crear(self):
        response = self.api.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        return response.data['id_solicitud_adopcion']

    def test_crea_cifrada_sin_copias_personales_en_observaciones_historial_o_auditoria(self):
        pk = self.crear()
        row = EvaluacionAdopcion.objects.get(solicitud_id=pk)
        self.assertNotIn(b'QA-000-PRIVADO', bytes(row.contenido_cifrado))
        self.assertEqual(consultar(pk)['respuestas'], respuestas())
        self.assertEqual(row.fundacion_id, self.foundation.pk)
        self.assertIsNotNone(row.aceptada_en)
        application = SolicitudAdopcion.objects.get(pk=pk)
        self.assertEqual(application.observaciones, '')
        self.assertNotIn('hogar responsable', str(list(application.historialestadoadopcion_set.values())))
        events = str(list(EventoSeguridad.objects.values('datos')))
        for value in ('QA-000-PRIVADO', 'Dirección ficticia QA', 'qa@example.invalid', 'hogar responsable'):
            self.assertNotIn(value, events)

    def test_validacion_rechaza_campos_internos_consentimientos_y_motivo_vacio(self):
        cases = [('motivo', ''), ('autoriza_evaluacion', False), ('datos_correctos', False),
            ('version', 'desconocida'), ('usuario_adoptante_id', self.otro.pk), ('personas_hogar', 0),
            ('email', 'incorrecto'), ('motivo', 'x' * 2001)]
        for field, value in cases:
            with self.subTest(field=field):
                payload = copy.deepcopy(self.payload); payload['evaluacion'][field] = value
                response = self.api.post(self.url, payload, format='json')
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response['Cache-Control'], 'no-store')
        self.assertFalse(SolicitudAdopcion.objects.exists())

    def test_requiere_detalles_condicionales(self):
        for field, value in [('tenencia', 'arrendada'), ('mascotas_actuales', True), ('experiencia_previa', True)]:
            payload = copy.deepcopy(self.payload); payload['evaluacion'][field] = value
            self.assertEqual(self.api.post(self.url, payload, format='json').status_code, 400)
        self.assertFalse(EvaluacionAdopcion.objects.exists())

    def test_descarta_respuestas_ocultas_y_no_usa_identidad_del_cliente(self):
        self.payload['evaluacion'].update(autorizacion_propietario='no', cantidad_mascotas=3,
            otras_mascotas='Respuesta vieja', esterilizacion='no', experiencia='Dato anterior')
        pk = self.crear()
        data = consultar(pk)['respuestas']
        for key in ('autorizacion_propietario', 'cantidad_mascotas', 'otras_mascotas', 'esterilizacion', 'experiencia'):
            self.assertNotIn(key, data)
        self.assertEqual(SolicitudAdopcion.objects.get(pk=pk).usuario_adoptante_id, self.ciudadano.pk)

    def test_fallo_de_cifrado_revierte_solicitud_y_auditoria(self):
        with patch('adoption.questionnaire.cifrar', side_effect=ImproperlyConfigured('QA sin clave')):
            response = self.api.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, 503)
        self.assertFalse(SolicitudAdopcion.objects.exists())
        self.assertFalse(EvaluacionAdopcion.objects.exists())
        self.assertFalse(EventoSeguridad.objects.filter(accion='adopcion.participar').exists())

    def test_reenvio_no_crea_dos_solicitudes_pendientes(self):
        self.crear()
        self.assertEqual(self.api.post(self.url, self.payload, format='json').status_code, 400)
        self.assertEqual(SolicitudAdopcion.objects.count(), 1)
        self.assertEqual(EvaluacionAdopcion.objects.count(), 1)

    def test_titular_lee_otra_cuenta_y_anonimo_no(self):
        pk = self.crear(); url = f'/api/adopcion/solicitudes/{pk}/'
        response = self.api.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['evaluacion']['respuestas']['documento'], 'QA-000-PRIVADO')
        self.assertEqual(response['Cache-Control'], 'no-store')
        for client, code in [(self.cliente(self.otro), 404), (APIClient(), 401)]:
            denied = client.get(url)
            self.assertEqual(denied.status_code, code)
            self.assertEqual(denied['Cache-Control'], 'no-store')
            self.assertNotIn('QA-000-PRIVADO', str(denied.data))

    def test_revocacion_bloquea_creacion_y_lectura_incluso_con_usuario_autenticado(self):
        pk = self.crear()
        UsuarioRol.objects.filter(usuario=self.ciudadano).update(fecha_revocacion=timezone.now())
        invalidar()
        self.assertEqual(self.api.post(self.url, self.payload, format='json').status_code, 403)
        self.assertEqual(self.api.get(f'/api/adopcion/solicitudes/{pk}/').status_code, 403)

    def test_revision_asignada_y_panel_muestran_evaluacion_sin_otorgar_acceso_a_otra_entidad(self):
        pk = self.crear()
        from seguridad.flujos_views import RegistroPrivadoView
        from rest_framework.test import APIRequestFactory, force_authenticate
        tomar(self.carlos, 'adopcion', pk)
        def get(actor):
            req = APIRequestFactory().get('/api/qa/'); force_authenticate(req, actor)
            return RegistroPrivadoView.as_view()(req, recurso='adopcion', pk=pk)
        response = get(self.carlos)
        self.assertEqual(response.status_code, 200)
        self.assertIn('QA-000-PRIVADO', str(response.data['evaluacion_inicial']))
        self.assertEqual(response['Cache-Control'], 'no-store')
        self.assertEqual(get(self.otro).status_code, 403)

    def test_decision_no_sobrescribe_evaluacion_inicial(self):
        pk = self.crear()
        tomar(self.carlos, 'adopcion', pk)
        from .services import resolver_solicitud
        resolver_solicitud(solicitud_id=pk, fundacion_id=self.foundation.pk,
            usuario_actor_id=self.carlos.pk, aprobar=False, observacion='Motivo administrativo QA')
        self.assertEqual(consultar(pk)['respuestas'], respuestas())
        self.assertEqual(SolicitudAdopcion.objects.get(pk=pk).observaciones, 'Motivo administrativo QA')

    def test_anonymous_cannot_submit_or_see_profile_capability(self):
        self.assertEqual(APIClient().post(self.url, self.payload, format='json').status_code, 401)
        self.assertTrue(self.api.get('/api/auth/perfil/').data['evaluacion_adopcion'])

    @override_settings(SESSION_COOKIE_SECURE=False, CSRF_COOKIE_SECURE=False)
    def test_panel_y_admin_consultan_sin_editar_evaluacion_inicial(self):
        pk = self.crear()
        self.admin.is_staff = self.admin.is_superuser = True
        self.admin.save(update_fields=['is_staff', 'is_superuser']); invalidar()
        browser = Client(); browser.force_login(self.admin)
        session = browser.session; session['lpn_entidad'] = self.entidad.pk; session.save()
        response = browser.get(f'/panel/areas/adopciones/?detalle={pk}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'QA-000-PRIVADO')
        self.assertContains(response, 'Documento de identidad')
        row = EvaluacionAdopcion.objects.get(solicitud_id=pk)
        url = f'/admin/adoption/evaluacionadopcion/{row.pk}/change/'
        response = browser.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'QA-000-PRIVADO')
        self.assertNotContains(response, 'name="contenido_cifrado"')
        self.assertFalse(response.context['has_change_permission'])
        self.assertTrue(EventoSeguridad.objects.filter(accion='registro.consultar',
            objeto_id=pk, datos__operacion='consulta-tecnica-evaluacion').exists())
        self.carlos.is_staff = True; self.carlos.save(update_fields=['is_staff']); invalidar()
        browser.force_login(self.carlos)
        denied = browser.get(url)
        self.assertEqual(denied.status_code, 403)
        self.assertNotContains(denied, 'QA-000-PRIVADO', status_code=403)

    def test_texto_de_autorizacion_guardado_no_cambia_al_modificar_el_aviso_actual(self):
        pk = self.crear()
        before = consultar(pk)['autorizacion']
        with patch('adoption.questionnaire.NOTICE', 'Texto futuro QA'):
            self.assertEqual(consultar(pk)['autorizacion'], before)

    def test_evaluacion_no_aparece_en_listados_publicos(self):
        self.crear()
        response = APIClient().get('/api/adopcion/catalogo/')
        self.assertEqual(response.status_code, 200)
        for text in ('QA-000-PRIVADO', 'Dirección ficticia QA', 'evaluacion_privada', 'contenido_cifrado'):
            self.assertNotIn(text, str(response.data))

    def test_no_admite_archivos_ni_multipart_en_el_formulario_json(self):
        response = self.api.generic('POST', self.url, b'not-a-form',
            content_type='multipart/form-data; boundary=qa')
        self.assertEqual(response.status_code, 415)
        self.assertEqual(response['Cache-Control'], 'no-store')
        self.assertFalse(EvaluacionAdopcion.objects.exists())
