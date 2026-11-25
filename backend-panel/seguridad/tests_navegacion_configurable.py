from django.test import Client
from django.utils.translation import override
from core.models import Recurso
from seguridad.models import ConfiguracionPanel, EventoSeguridad
from seguridad.tests import BaseRBAC


class TitulosNavegacionTests(BaseRBAC):
    def browser(self, usuario=None):
        client = Client()
        client.force_login(usuario or self.admin)
        return client

    def test_grupos_inicio_y_opciones_cambian_sin_alterar_accesos(self):
        c = self.browser()
        antes = c.get('/panel/').context
        codigos = [m['codigo'] for m in antes['modulos']]
        permisos = [p['codigo'] for p in antes['resumen_permisos']]
        r = c.post('/panel/configuracion/', {
            'nav_grupo_seguridad':'Control de plataforma', 'nav_accesos':'Control de accesos',
            'nav_inicio':'Mi resumen', 'nav_mod_usuarios':'Personas autorizadas',
            'nav_mod_roles_usuario':'Perfiles por persona', 'motivo':'Personalizar navegación',
        })
        self.assertEqual(r.status_code,302)
        page = c.get('/panel/usuarios/')
        self.assertContains(page,'Control de plataforma')
        self.assertContains(page,'Control de accesos')
        self.assertContains(page,'Mi resumen')
        self.assertContains(page,'<h1 data-nav-page-title>Personas autorizadas</h1>',html=True)
        self.assertContains(page,'href="/panel/usuarios/"')
        despues = c.get('/panel/').context
        self.assertEqual(codigos,[m['codigo'] for m in despues['modulos']])
        self.assertEqual(permisos,[p['codigo'] for p in despues['resumen_permisos']])
        self.assertEqual(antes['cantidad_modulos'],despues['cantidad_modulos'])
        asignacion = c.get('/panel/seguridad/?tab=usuarios')
        self.assertContains(asignacion,'<h1 data-nav-page-title>Perfiles por persona</h1>',html=True)

    def test_recurso_sigue_dando_nombre_por_defecto_y_blanco_restaura_herencia(self):
        c=self.browser()
        recurso=Recurso.objects.get(codigo='usuarios')
        recurso.nombre='Cuentas de la comunidad'
        recurso.save(update_fields=['nombre'])
        self.assertContains(c.get('/panel/usuarios/'),'Cuentas de la comunidad')
        c.post('/panel/configuracion/',{'nav_mod_usuarios':'Personas','motivo':'Título visible'})
        self.assertContains(c.get('/panel/usuarios/'),'<h1 data-nav-page-title>Personas</h1>',html=True)
        c.post('/panel/configuracion/',{'nav_mod_usuarios':'','motivo':'Restablecer nombre del recurso'})
        self.assertFalse(ConfiguracionPanel.objects.filter(clave='nav_mod_usuarios').exists())
        self.assertContains(c.get('/panel/usuarios/'),'<h1 data-nav-page-title>Cuentas de la comunidad</h1>',html=True)

    def test_personalizar_no_otorga_derechos_y_post_ciudadano_se_rechaza(self):
        admin=self.browser()
        admin.post('/panel/configuracion/',{'nav_grupo_seguridad':'Acceso público','nav_mod_usuarios':'Personas'})
        ciudadano=self.browser(self.ciudadano)
        self.assertEqual(ciudadano.get('/panel/usuarios/').status_code,403)
        self.assertEqual(ciudadano.post('/panel/configuracion/',{'nav_mod_usuarios':'Prohibido'}).status_code,403)
        self.assertEqual(ConfiguracionPanel.objects.get(clave='nav_mod_usuarios').valor,'Personas')
        self.assertNotContains(ciudadano.get('/panel/'),'data-module="usuarios"')

    def test_cambio_se_publica_en_estado_y_audita_antes_y_despues(self):
        c=self.browser()
        antes=c.get('/panel/estado/').json()
        c.post('/panel/configuracion/',{'nav_accesos':'Perfiles y capacidades','motivo':'Claridad del menú'})
        despues=c.get('/panel/estado/').json()
        self.assertNotEqual(antes['firma'],despues['firma'])
        grupos=despues['navegacion']['grupos']
        seguridad=next(g for g in grupos if g['codigo']=='seguridad')
        self.assertEqual(next(m for m in seguridad['modulos'] if m['codigo']=='accesos')['nombre'],'Perfiles y capacidades')
        evento=EventoSeguridad.objects.filter(accion='configuracion.editar').latest('pk')
        self.assertEqual(evento.datos['anterior'],{'nav_accesos':''})
        self.assertEqual(evento.datos['nuevo'],{'nav_accesos':'Perfiles y capacidades'})
        auditoria=c.get('/panel/auditoria/')
        fila=next(e for e in auditoria.context['eventos'] if e['obj'].pk==evento.pk)
        self.assertEqual(fila['nuevo'],'Roles y recursos: Perfiles y capacidades')
        self.assertEqual(fila['anterior'],'Roles y recursos: Usar nombre habitual')

    def test_titulo_largo_revierte_todo_y_conserva_borrador(self):
        c=self.browser()
        page=c.post('/panel/configuracion/',{'nav_inicio':'Mi resumen','nav_accesos':'x'*81})
        self.assertContains(page,'máximo de 80')
        self.assertFalse(ConfiguracionPanel.objects.filter(clave='nav_inicio').exists())
        self.assertContains(page,'value="Mi resumen"')

    def test_edicion_con_version_antigua_no_sobrescribe_a_otra_persona(self):
        c=self.browser()
        version=c.get('/panel/configuracion/').context['version_config']
        c.post('/panel/configuracion/',{'nav_inicio':'Nuevo resumen','version_config':version})
        page=c.post('/panel/configuracion/',{'nav_inicio':'Borrador anterior','version_config':version})
        self.assertContains(page,'Otra persona cambió la configuración')
        self.assertEqual(ConfiguracionPanel.objects.get(clave='nav_inicio').valor,'Nuevo resumen')
        self.assertContains(page,'value="Borrador anterior"')

    def test_etiquetas_personalizadas_son_texto_y_no_html_ejecutable(self):
        c=self.browser()
        c.post('/panel/configuracion/',{'nav_inicio':'<script>alert(1)</script>'})
        page=c.get('/panel/')
        self.assertNotContains(page,'<script>alert(1)</script>')
        self.assertContains(page,'&lt;script&gt;alert(1)&lt;/script&gt;')

    def test_grupos_conservan_identidad_y_personalizacion_en_ingles(self):
        c=self.browser()
        c.post('/panel/configuracion/',{'nav_grupo_participacion':'Comunidad activa'})
        c.cookies['lpn_language']='en'
        with override('en'):
            page=c.get('/panel/')
            grupos=page.context['grupos_navegacion']
            grupo=next(g for g in grupos if g['codigo']=='grupo-participacion')
            self.assertEqual(grupo['nombre'],'Comunidad activa')
