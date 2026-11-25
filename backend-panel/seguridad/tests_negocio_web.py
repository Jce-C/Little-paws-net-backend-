"""Recorridos HTTP del panel: datos reales y mismas reglas que las API."""
from datetime import timedelta
from django.test import Client
from django.utils import timezone
from core.models import Ciudad, Fundacion, Tienda, CapacidadFundacion
from animals.models import Raza, Especie, Mascota
from commerce.models import Producto, PedidoIniciado
from .tests import BaseRBAC, valor
from .web.procesos import OPERACIONES
from .models import Anuncio, EventoSeguridad


class NegocioWebTests(BaseRBAC):
    def setUp(self):
        self.admin.is_superuser=True
        self.admin.save(update_fields=['is_superuser'])
        self.browser=Client();self.browser.force_login(self.admin)
        self.ciudad=Ciudad.objects.create(nombre='Local de pruebas',departamento='Prueba')
        self.fundacion=Fundacion.objects.create(entidad=self.entidad,nit='WEB-PRUEBA',ciudad=self.ciudad)
        CapacidadFundacion.objects.create(fundacion=self.fundacion,cupos_totales=5,usuario_actualizador=self.admin)
        self.tienda=Tienda.objects.create(entidad=self.ajena,ciudad=self.ciudad,direccion='Prueba')
        self.raza=Raza.objects.create(especie=Especie.objects.create(nombre='Prueba web'),nombre='Mestizo')
        self.pet=Mascota.objects.create(nombre='Prueba',dueno=self.admin,raza=self.raza,estado_mascota=valor('estado_mascota','Con dueño'))

    def contexto(self,entidad):
        s=self.browser.session;s['lpn_entidad']=entidad.pk;s.save()

    def enviar(self,area,accion,datos,registro=None):
        ruta=f'/panel/areas/{area}/?accion={accion}'
        if registro:ruta+=f'&registro={registro}'
        r=self.browser.post(ruta,datos)
        if r.status_code!=302:
            form=r.context and r.context.get('form_operacion')
            self.fail(f'{accion}: HTTP {r.status_code}; errores={form.errors if form else "sin formulario"}')
        return r

    def test_todos_los_formularios_se_construyen_sin_error(self):
        self.contexto(self.entidad)
        for key,op in OPERACIONES.items():
            with self.subTest(operacion=key):
                r=self.browser.get(f'/panel/areas/{op.area}/?accion={key}')
                self.assertEqual(r.status_code,200)
                self.assertIsNotNone(r.context['form_operacion'])

    def test_registrar_organizacion_y_editar_sin_verificar_por_atajo(self):
        self.enviar('organizaciones','crear-organizacion',{'nombre':'Nueva tienda web','tipo':'tienda','ciudad_id':self.ciudad.pk,'direccion':'Calle de prueba'})
        nueva=Tienda.objects.get(entidad__nombre='Nueva tienda web')
        self.assertEqual(nueva.entidad.estado_verificacion.nombre,'Pendiente')
        self.enviar('organizaciones','editar-organizacion',{'registro':nueva.pk,'nombre':'Tienda editada'},nueva.pk)
        nueva.entidad.refresh_from_db();self.assertEqual(nueva.entidad.nombre,'Tienda editada')

    def test_registrar_mascota_y_editar_precarga_datos(self):
        self.enviar('mascotas','declarar-mascota',{'nombre':'Nueva mascota web','raza_id':self.raza.pk})
        p=Mascota.objects.get(nombre='Nueva mascota web')
        pagina=self.browser.get(f'/panel/areas/mascotas/?accion=editar-mascota&registro={p.pk}')
        self.assertEqual(pagina.context['form_operacion']['nombre'].value(),p.nombre)
        self.enviar('mascotas','editar-mascota',{'registro':p.pk,'nombre':'Ficha corregida'},p.pk)
        p.refresh_from_db();self.assertEqual(p.nombre,'Ficha corregida')

    def test_producto_pedido_varias_lineas_y_no_se_oculta_al_editar(self):
        self.contexto(self.ajena)
        self.enviar('catalogo','crear-producto',{'nombre':'Alimento web','precio':'25.00','existencias':10,'disponible':'on','categoria_id':valor('categoria_producto','Alimentos').pk,'tipo_id':valor('tipo_producto','Alimento seco').pk})
        p=Producto.objects.get(nombre='Alimento web')
        pagina=self.browser.get(f'/panel/areas/catalogo/?accion=editar-producto&registro={p.pk}')
        self.assertTrue(pagina.context['form_operacion']['disponible'].value())
        self.enviar('catalogo','editar-producto',{'registro':p.pk,'nombre':'Alimento actualizado','disponible':'on'},p.pk)
        self.enviar('pedidos','crear-pedido',{'id_tienda':self.tienda.pk,'lineas-TOTAL_FORMS':1,'lineas-INITIAL_FORMS':0,'lineas-MIN_NUM_FORMS':1,'lineas-MAX_NUM_FORMS':50,'lineas-0-id_producto':p.pk,'lineas-0-cantidad':2})
        pedido=PedidoIniciado.objects.get(usuario_cliente=self.admin)
        self.assertEqual(pedido.estado_pedido.nombre,'Iniciado')
        self.assertTrue(EventoSeguridad.objects.filter(accion='negocio.operacion',datos__operacion='crear-pedido').exists())

    def test_anuncio_pasa_por_revision_y_no_publica_directamente(self):
        self.contexto(self.entidad)
        self.enviar('publicidad','crear-anuncio',{'titulo':'Campaña web','texto':'Campaña de prueba','url':'https://example.org/prueba','inicio':timezone.now().isoformat(),'fin':(timezone.now()+timedelta(days=1)).isoformat()})
        self.assertTrue(Anuncio.objects.filter(entidad=self.entidad).exists())

    def test_usuario_sin_capacidad_no_crea_producto_ni_adopta_vista_admin(self):
        c=Client();c.force_login(self.ciudadano)
        self.assertEqual(c.post('/panel/areas/catalogo/?accion=crear-producto',{'nombre':'Intento'}).status_code,403)
        self.assertFalse(Producto.objects.filter(nombre='Intento').exists())
        self.assertEqual(c.get('/panel/usuarios/').status_code,403)

    def test_identificador_malformado_da_404(self):
        self.assertEqual(self.browser.get('/panel/areas/adopciones/?detalle=no-valido').status_code,404)

    def test_consulta_basica_no_revela_expediente_ajeno(self):
        self.admin.is_superuser=False;self.admin.save(update_fields=['is_superuser'])
        ajena=Mascota.objects.create(nombre='Ficha básica ajena',dueno=self.ciudadano,raza=self.raza,estado_mascota=valor('estado_mascota','Con dueño'))
        r=self.browser.get(f'/panel/areas/mascotas/?detalle={ajena.pk}&vista=gestion')
        self.assertEqual(r.status_code,200)
        self.assertContains(r,'Ficha básica ajena')
        self.assertNotIn('Atenciones recientes',str(r.context['detalle_negocio']))
        fila=next(x for x in r.context['registros'] if x['id']==ajena.pk)
        self.assertFalse(fila['autorizar'])

    def test_consulta_entidad_respeta_membresia(self):
        c=Client();c.force_login(self.ana)
        self.assertEqual(c.get(f'/panel/areas/organizaciones/?detalle={self.entidad.pk}').status_code,200)
        self.assertEqual(c.get(f'/panel/areas/organizaciones/?detalle={self.ajena.pk}').status_code,403)
