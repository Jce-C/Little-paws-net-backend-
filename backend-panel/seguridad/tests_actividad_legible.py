from types import SimpleNamespace
from django.test import Client, SimpleTestCase
from django.utils.translation import override
from seguridad.tests import BaseRBAC
from seguridad.models import EventoSeguridad
from seguridad.web.dashboard import descripcion_evento
from seguridad.web.presentacion_eventos import informacion_evento


def evento(accion, **datos):
    return SimpleNamespace(accion=accion, datos=datos, motivo='', recurso='mascotas', objeto_id=7)


class PresentacionActividadTests(SimpleTestCase):
    def test_fotografias_actuales_y_alias_historicos_se_explican(self):
        for prefix in ('mascota', 'mascotas'):
            with self.subTest(prefix=prefix):
                self.assertEqual(descripcion_evento(evento(prefix+'.foto_publicar')), 'Publicó una fotografía para adopción')
                self.assertEqual(descripcion_evento(evento(prefix+'.foto_retirar')), 'Retiró la fotografía pública de adopción')
                self.assertEqual(descripcion_evento(evento(prefix+'.foto_publicar', reemplazo=True)), 'Reemplazó la fotografía pública para adopción')
                self.assertEqual(descripcion_evento(evento(prefix+'.foto_publicar', reemplazo='false')), 'Publicó una fotografía para adopción')

    def test_detalle_de_imagen_no_expone_claves_ni_otros_metadatos(self):
        obj=evento('mascotas.foto_publicar', nuevo={'ancho':1280,'alto':720,'bytes':20480,'clave':'PRIVATE-IMAGE-KEY','telefono':'PRIVATE-PHONE'})
        self.assertEqual(informacion_evento(obj), 'Imagen: 1280 × 720 px · 20480 bytes.')
        for value in (None, {}, {'ancho':True,'alto':720,'bytes':20}, {'ancho':-1,'alto':720,'bytes':20}):
            self.assertEqual(informacion_evento(evento('mascotas.foto_publicar', nuevo=value)), '')

    def test_perfil_describe_campos_y_no_valores_personales(self):
        obj=evento('perfil.actualizar', campos=['telefono','nombre','password'], telefono='PRIVATE-PHONE', nombre='PRIVATE-NAME', password='PRIVATE-SECRET')
        self.assertEqual(descripcion_evento(obj), 'Actualizó sus datos de contacto')
        text=informacion_evento(obj)
        self.assertIn('Nombre', text);self.assertIn('Teléfono',text)
        self.assertNotIn('PRIVATE-',text);self.assertNotIn('password',text)
        self.assertEqual(informacion_evento(evento('perfil.actualizar', campos='nombre')), '')

    def test_solicitud_no_se_confunde_con_resolucion_o_titularidad(self):
        self.assertEqual(descripcion_evento(evento('adopcion.participar', operacion='solicitar-adopcion')), 'Envió una solicitud de adopción')
        self.assertNotEqual(descripcion_evento(evento('adopcion.participar', operacion='retirar-adopcion')), 'Envió una solicitud de adopción')

    def test_errores_no_inventan_motivos_ni_cambios_guardados(self):
        self.assertEqual(descripcion_evento(evento('operacion.fallida')), 'La operación devolvió un error')
        self.assertEqual(descripcion_evento(evento('operacion.rechazada')), 'La operación fue rechazada')
        self.assertEqual(informacion_evento(evento('operacion.fallida', estado_http=500, operacion='PRIVATE-DATA')), 'Respuesta HTTP: 500.')
        self.assertEqual(informacion_evento(evento('operacion.fallida', estado_http='500')), '')

    def test_textos_nuevos_se_traducen_en_el_servidor(self):
        with override('en'):
            self.assertEqual(descripcion_evento(evento('mascotas.foto_publicar')), 'Published an adoption photograph')
            self.assertEqual(descripcion_evento(evento('operacion.rechazada')), 'The operation was rejected')
            self.assertEqual(informacion_evento(evento('operacion.fallida', estado_http=400)), 'HTTP response: 400.')
            self.assertEqual(informacion_evento(evento('mascotas.foto_publicar', nuevo={'ancho':100,'alto':80,'bytes':800})), 'Image: 100 × 80 px · 800 bytes.')

    def test_accion_futura_conserva_el_codigo_para_trazabilidad(self):
        self.assertIn('nueva.accion', descripcion_evento(evento('nueva.accion')))
        self.assertEqual(informacion_evento(evento('nueva.accion')), '')


class ActividadLegiblePanelTests(BaseRBAC):
    def setUp(self):
        super().setUp()
        self.event=EventoSeguridad.objects.create(actor=self.admin, accion='mascotas.foto_publicar', recurso='mascotas', objeto_id=7,
            datos={'nuevo':{'ancho':100,'alto':80,'bytes':800},'_contexto':{'resultado':'EXITO'}}, motivo='Evento sintético de prueba')

    def browser(self, usuario=None, idioma='es'):
        c=Client();c.force_login(usuario or self.admin);c.cookies['lpn_language']=idioma;return c

    def test_dashboard_y_detalle_usen_el_mismo_texto_y_conserven_codigo(self):
        c=self.browser()
        self.assertContains(c.get('/panel/'),'Publicó una fotografía para adopción')
        audit=c.get('/panel/auditoria/')
        self.assertContains(audit,'Publicó una fotografía para adopción')
        self.assertContains(audit,'Imagen: 100 × 80 px · 800 bytes.')
        self.assertContains(audit,'<dd>Exitosa</dd>',html=True)
        self.assertContains(audit,'mascotas.foto_publicar')
        self.event.refresh_from_db();self.assertEqual(self.event.accion,'mascotas.foto_publicar')

    def test_detalle_en_ingles_y_denegacion_a_ciudadano(self):
        audit=self.browser(idioma='en').get('/panel/auditoria/')
        self.assertContains(audit,'Published an adoption photograph')
        self.assertContains(audit,'Image: 100 × 80 px · 800 bytes.')
        self.assertContains(audit,'<dd>Successful</dd>',html=True)
        self.assertEqual(self.browser(self.ciudadano).get('/panel/auditoria/').status_code,403)
