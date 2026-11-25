from django.test import Client
from rest_framework.test import APIClient
from rest_framework.exceptions import ValidationError,PermissionDenied
from seguridad.tests import BaseRBAC,valor
from core.models import Rol,RolPermiso,Permiso,UsuarioRol,EntidadMiembro,EntidadMiembroRol,Ciudad,Tienda
from commerce.models import Producto,PedidoIniciado,DetallePedido
from seguridad.models import EventoSeguridad,BajaAdministrativa,CambioProducto
from seguridad.administracion_segura import preparar_confirmacion,ejecutar_baja
from seguridad.asignaciones import guardar_roles,firma_persona

class FaseCuatroTests(BaseRBAC):
    def api(self,u=None):
        c=APIClient();c.force_authenticate(u or self.admin);return c
    def browser(self):
        c=Client();c.force_login(self.admin);return c
    def role(self,code,ambito='GLOBAL',entidad=None,cap='mascotas.ver'):
        r=Rol.objects.create(codigo=code,nombre=code,ambito=ambito,entidad=entidad)
        RolPermiso.objects.create(rol=r,permiso=Permiso.objects.get(codigo=cap));return r
    def test_dynamic_global_assignment_accepts_one_two_three_and_more_than_three(self):
        roles=[Rol.objects.get(codigo='CIUDADANO')]+[self.role('CUSTOM_'+str(i)) for i in range(4)]
        c=self.api();url=f'/api/seguridad/usuarios/{self.ciudadano.pk}/asignaciones-roles/'
        for count in (1,2,3,5):
            with self.subTest(count=count):
                version=c.get(url).data['version'];ids=[r.pk for r in roles[:count]]
                response=c.put(url,{'roles':ids,'version':version,'motivo':'Asignación múltiple autorizada'},format='json');self.assertEqual(response.status_code,200,response.data)
                self.assertCountEqual(c.get(url).data['roles'],ids)
                self.assertEqual(UsuarioRol.objects.filter(usuario=self.ciudadano,fecha_revocacion__isnull=True).count(),count)
        ids=[r.pk for r in roles if r!=roles[2]];response=c.put(url,{'roles':ids,'version':c.get(url).data['version'],'motivo':'Retirar solo un rol'},format='json');self.assertEqual(response.status_code,200,response.data)
        self.assertCountEqual(c.get(url).data['roles'],ids)
    def test_multiple_organization_roles_keep_global_and_other_contexts(self):
        global_role=self.role('CUSTOM_GLOBAL');guardar_roles(self.admin,self.ciudadano.pk,[Rol.objects.get(codigo='CIUDADANO').pk,global_role.pk],version=firma_persona(self.ciudadano,None,'usuarios'),motivo='Preparar roles globales')
        roles=[Rol.objects.get(codigo=x) for x in ['GESTOR_RESCATES','GESTOR_ADOPCIONES','GESTOR_APORTES','GESTOR_CATALOGO']]+[self.role('CUSTOM_ORG','ENTIDAD',self.entidad,'caso.ver')]
        ids=[r.pk for r in roles];guardar_roles(self.admin,self.ciudadano.pk,ids,self.entidad.pk,firma_persona(self.ciudadano,self.entidad.pk,'usuarios'),'Cinco roles en organización',True)
        other=self.role('CUSTOM_OTHER','ENTIDAD',self.ajena,'caso.ver');guardar_roles(self.admin,self.ciudadano.pk,[other.pk],self.ajena.pk,firma_persona(self.ciudadano,self.ajena.pk,'usuarios'),'Segundo contexto',True)
        guardar_roles(self.admin,self.ciudadano.pk,ids[1:],self.entidad.pk,firma_persona(self.ciudadano,self.entidad.pk,'usuarios'),'Retirar uno del primer contexto')
        self.assertEqual(EntidadMiembroRol.objects.filter(miembro__usuario=self.ciudadano,miembro__entidad=self.entidad,fecha_revocacion__isnull=True).count(),4)
        self.assertTrue(EntidadMiembroRol.objects.filter(miembro__usuario=self.ciudadano,miembro__entidad=self.ajena,rol=other,fecha_revocacion__isnull=True).exists())
        self.assertTrue(UsuarioRol.objects.filter(usuario=self.ciudadano,rol=global_role,fecha_revocacion__isnull=True).exists())
    def test_unauthorized_assignment_and_stale_overwrite_are_rejected(self):
        limited=self.role('LIMITED_ASSIGNER',cap='roles.asignar');UsuarioRol.objects.create(usuario=self.otro,rol=limited)
        url=f'/api/seguridad/usuarios/{self.ciudadano.pk}/asignaciones-roles/';c=self.api(self.otro);v=c.get(url).data['version']
        response=c.put(url,{'roles':[Rol.objects.get(codigo='ADMIN_SEGURIDAD').pk],'version':v,'motivo':'Intento no autorizado'},format='json');self.assertEqual(response.status_code,403)
        added=self.role('ADDED');a=self.api();response=a.put(url,{'roles':[added.pk],'version':v,'motivo':'Cambio válido'},format='json');self.assertEqual(response.status_code,200)
        response=a.put(url,{'roles':[],'version':v,'motivo':'Formulario antiguo'},format='json');self.assertEqual(response.status_code,400)
        self.assertCountEqual(a.get(url).data['roles'],[added.pk])
    def test_unchanged_roles_above_actor_authority_are_preserved(self):
        readonly=self.role('LIMITED_ASSIGNER',cap='roles.asignar');UsuarioRol.objects.create(usuario=self.otro,rol=readonly)
        admin_role=Rol.objects.get(codigo='ADMIN_SEGURIDAD');UsuarioRol.objects.create(usuario=self.ciudadano,rol=admin_role)
        existing=[Rol.objects.get(codigo='CIUDADANO').pk,admin_role.pk]
        guardar_roles(self.otro,self.ciudadano.pk,existing,version=firma_persona(self.ciudadano,None,'usuarios'),motivo='Mantener asignaciones existentes')
        self.assertTrue(UsuarioRol.objects.filter(usuario=self.ciudadano,rol=admin_role,fecha_revocacion__isnull=True).exists())
        with self.assertRaises(PermissionDenied):guardar_roles(self.otro,self.ciudadano.pk,[existing[0]],version=firma_persona(self.ciudadano,None,'usuarios'),motivo='Intento de revocación no autorizado')
    def product(self,history=False):
        city=Ciudad.objects.create(nombre='Ciudad tienda',departamento='Prueba');store=Tienda.objects.create(entidad=self.entidad,ciudad=city,direccion='Dirección prueba')
        member,_=EntidadMiembro.objects.get_or_create(usuario=self.admin,entidad=self.entidad)
        EntidadMiembroRol.objects.get_or_create(miembro=member,rol=Rol.objects.get(codigo='GESTOR_CATALOGO'))
        p=Producto.objects.create(tienda=store,nombre='Alimento de prueba',precio='15000',existencias=5,categoria_producto=__import__('core.models',fromlist=['ValorMaestro']).ValorMaestro.objects.filter(tipo__nombre='categoria_producto').first(),tipo_producto=__import__('core.models',fromlist=['ValorMaestro']).ValorMaestro.objects.filter(tipo__nombre='tipo_producto').first(),estado_producto=valor('estado_producto','Disponible'))
        if history:
            order=PedidoIniciado.objects.create(tienda=store,usuario_cliente=self.ciudadano,estado_pedido=valor('estado_pedido','Iniciado'))
            DetallePedido.objects.create(pedido=order,tienda=store,producto=p,cantidad=1,precio_referencia=p.precio)
        return p
    def execute(self,p,action='eliminar',token=None):
        d=preparar_confirmacion(self.admin,'productos',p.pk)
        return ejecutar_baja(self.admin,'productos',p.pk,action,motivo='Retiro autorizado de catálogo',confirmacion=token or d['confirmacion_token'],nombre=p.nombre if action=='fisica' else '',acepto=True)
    def test_product_with_order_is_archived_without_deleting_history(self):
        p=self.product(True);result=self.execute(p);p.refresh_from_db();self.assertEqual(p.estado_producto.nombre,'Inactivo');self.assertTrue(result['estado']['eliminado'])
        self.assertTrue(DetallePedido.objects.filter(producto=p).exists());self.assertTrue(BajaAdministrativa.objects.filter(tipo='productos',objeto_id=p.pk,eliminado=True).exists())
        from commerce.consultas import productos_vigentes
        self.assertFalse(productos_vigentes().filter(pk=p.pk).exists());self.assertTrue(EventoSeguridad.objects.filter(accion='productos.eliminar',objeto_id=p.pk).exists())
        with self.assertRaises(ValidationError):self.execute(p,'fisica')
    def test_product_without_dependencies_can_be_physically_deleted_and_retry_is_idempotent(self):
        p=self.product();d=preparar_confirmacion(self.admin,'productos',p.pk);pk=p.pk
        self.assertTrue(d['fisica_disponible']);first=self.execute(p,'fisica',d['confirmacion_token']);self.assertFalse(Producto.objects.filter(pk=pk).exists())
        again=ejecutar_baja(self.admin,'productos',pk,'fisica',motivo='Retiro autorizado de catálogo',confirmacion=d['confirmacion_token'],nombre=p.nombre,acepto=True)
        self.assertEqual(first,again);self.assertEqual(EventoSeguridad.objects.filter(accion='productos.fisica',objeto_id=pk).count(),1)
    def test_product_scope_and_editor_reject_unauthorized_or_archived_changes(self):
        p=self.product();c=self.api(self.otro);self.assertEqual(c.get(f'/api/seguridad/administracion/productos/{p.pk}/baja/').status_code,403)
        self.execute(p)
        response=self.api().patch(f'/api/seguridad/operaciones/productos/{p.pk}/',{'nombre':'Reactivación indebida','disponible':True},format='json')
        self.assertEqual(response.status_code,400,response.data);p.refresh_from_db();self.assertNotEqual(p.nombre,'Reactivación indebida')
    def test_exception_back_icon_keeps_person_and_context(self):
        r=self.browser().get(f'/panel/seguridad/?tab=excepciones&usuario={self.carlos.pk}&entidad={self.entidad.pk}')
        self.assertContains(r,'class="back-icon"');self.assertContains(r,f'tab=usuarios&usuario={self.carlos.pk}&entidad={self.entidad.pk}',html=False)
    def test_audit_grouping_is_separate_and_keeps_filters(self):
        r=self.browser().get('/panel/auditoria/?resultado=RECHAZADA&agrupar=usuario')
        self.assertContains(r,'class="audit-grouping-form"');self.assertContains(r,'name="resultado" value="RECHAZADA"')
        self.assertContains(r,'audit-quick-filters');self.assertContains(r,'?agrupar=usuario')
    def test_multiple_role_endpoint_rejects_missing_target_without_server_error(self):
        response=self.api().put('/api/seguridad/usuarios/999999999/asignaciones-roles/',{'roles':[],'version':'0'*64,'motivo':'Comprobar destino inexistente'},format='json')
        self.assertEqual(response.status_code,404)
