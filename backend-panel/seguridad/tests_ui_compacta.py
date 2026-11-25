from django.test import Client
from django.utils import timezone
from seguridad.tests import BaseRBAC
from seguridad.models import ConfiguracionPanel,EventoSeguridad
from seguridad.servicios import auditar

class InterfazCompactaTests(BaseRBAC):
 def browser(self,usuario=None):
  c=Client();c.force_login(usuario or self.admin);return c
 def test_color_no_tiene_selector_y_configuracion_esta_en_cabecera(self):
  r=self.browser().get('/panel/')
  self.assertNotContains(r,'name="perfil_visual"')
  self.assertContains(r,'data-modal-url href="/panel/configuracion/"')
  # Metrics are now an immediately visible grid, not the previous carousel.
  self.assertContains(r,'class="metric-track metric-grid"')
  self.assertContains(r,'class="metric-card"',count=len(r.context['indicadores']))
 def test_matriz_solo_switch_y_selector_superior(self):
  r=self.browser().get('/panel/seguridad/?tab=permisos')
  self.assertContains(r,'id="rol-configurado"')
  self.assertContains(r,'role="switch"')
  self.assertNotContains(r,'data-control-style')
  self.assertNotContains(r,'class="security-tabs"')
 def test_busqueda_personas_no_carga_catalogo_completo(self):
  c=self.browser();r=c.get('/panel/seguridad/?tab=usuarios')
  self.assertEqual(r.context['usuarios_catalogo'],[])
  self.assertIsNone(r.context['usuario_elegido'])
  r=c.get('/panel/seguridad/',{'tab':'usuarios','q':self.ciudadano.nombre})
  self.assertIn(self.ciudadano.pk,[u.pk for u in r.context['usuarios_catalogo']])
 def test_fondo_configurable_valida_y_se_refleja_en_login_sin_js_externo(self):
  c=self.browser();r=c.post('/panel/configuracion/',{'login_fondo_opacidad':'0.75','login_fondo_velo':'0.2','login_fondo_posicion':'center top','login_fondo_visible':'si','motivo':'Ajustar legibilidad'})
  self.assertEqual(r.status_code,302)
  page=Client().get('/panel/login/')
  self.assertEqual(page.context['fondo_login']['opacidad'],.75)
  self.assertEqual(page.context['fondo_login']['posicion'],'center top')
  self.assertNotContains(page,'<script src=')
  r=c.post('/panel/configuracion/',{'login_fondo_opacidad':'2','motivo':'Fuera de rango'})
  self.assertContains(r,'entre')
  self.assertEqual(ConfiguracionPanel.objects.get(clave='login_fondo_opacidad').valor,'0.75')
 def test_ciudadano_no_modifica_configuracion_ni_formulario_de_recurso(self):
  c=self.browser(self.ciudadano)
  self.assertEqual(c.post('/panel/configuracion/',{'login_fondo_velo':'0'}).status_code,403)
  self.assertEqual(c.get('/panel/seguridad/?tab=recursos&nuevo=1').status_code,403)
 def test_auditoria_filtra_sin_reescribir_historial(self):
  auditar(self.admin,'roles.editar','roles',motivo='Cambio trazable')
  auditar(self.ciudadano,'sesion.web_iniciar','sesion')
  antes=EventoSeguridad.objects.count();c=self.browser()
  r=c.get('/panel/auditoria/',{'actor':self.ciudadano.pk,'tipo':'acceso','desde':timezone.localdate().isoformat()})
  self.assertEqual(r.context['total_eventos'],1)
  self.assertEqual(r.context['eventos'][0]['categoria'],'Acceso')
  self.assertContains(r,'data-audit-detail')
  self.assertEqual(EventoSeguridad.objects.count(),antes)
  r=c.get('/panel/auditoria/',{'desde':'invalida'})
  self.assertEqual(r.status_code,200);self.assertTrue(r.context['error_filtros'])
 def test_graficos_salen_del_resumen_de_permisos(self):
  r=self.browser().get('/panel/');self.assertEqual(r.status_code,200)
  self.assertEqual(sum(x['valor'] for x in r.context['grafico_accesos']+r.context['grafico_restante']),r.context['total_capacidades'])
 def test_formulario_recurso_conserva_ruta_y_validacion(self):
  c=self.browser();url='/panel/seguridad/?tab=recursos&nuevo=1';r=c.get(url)
  self.assertContains(r,'data-modal-content')
  r=c.post(url,{'nuevo':'1','codigo':'recurso_prueba_ui','nombre':'Recurso UI','descripcion':'Solo metadatos'})
  self.assertEqual(r.status_code,302)

 def test_guardar_recurso_inexistente_devuelve_aviso_y_404(self):
  c=self.browser()
  respuesta=c.post('/panel/seguridad/?tab=recursos&editar=2147483647',{
      'id':'2147483647','nombre':'Un nombre válido','descripcion':'',
  })
  self.assertContains(respuesta,'El recurso ya no está disponible',status_code=404)
  self.assertContains(respuesta,'role="alert"',status_code=404)
  self.assertFalse(EventoSeguridad.objects.filter(accion='recursos.editar').exists())
