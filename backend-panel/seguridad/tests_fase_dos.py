from django.test import Client
from django.utils import timezone
from rest_framework.exceptions import ValidationError,PermissionDenied
from core.models import Rol,Permiso,RolPermiso,UsuarioRol,EntidadMiembro
from accounts.models import Usuario
from seguridad.tests import BaseRBAC,cuenta
from seguridad.administracion_segura import preparar_confirmacion,ejecutar_baja,validar_rol
from seguridad.roles_admin import guardar_rol,guardar_permisos,version_rol
from seguridad.models import EventoSeguridad,OperacionAdministrativa,BajaAdministrativa
from seguridad.autorizacion import puede,motor
from seguridad.servicios import auditar
from django.test import override_settings
from django.http import JsonResponse
from django.urls import path
from django.core.management import call_command
from tempfile import TemporaryDirectory
from io import StringIO
from pathlib import Path
from datetime import timedelta

def audit_probe(request):
    a=auditar(request.user,'registro.consultar','mascotas',105)
    b=auditar(request.user,'registro.consultar','mascotas',105)
    return JsonResponse({'a':a.pk,'b':b.pk})

urlpatterns=[path('_audit-probe/',audit_probe)]

class FaseDosTests(BaseRBAC):
    def browser(self,user=None):
        c=Client();c.force_login(user or self.admin);return c
    def execute(self,tipo,obj,accion='eliminar',token=None):
        p=preparar_confirmacion(self.admin,tipo,obj.pk)
        return ejecutar_baja(self.admin,tipo,obj.pk,accion,motivo='Prueba de baja segura',confirmacion=token or p['confirmacion_token'],nombre=p['confirmacion_nombre'],acepto=True)
    def test_navigation_is_grouped_and_counted_from_authorizations(self):
        r=self.browser().get('/panel/seguridad/?tab=roles')
        security=next(g for g in r.context['grupos_navegacion'] if g['codigo']=='seguridad')
        self.assertEqual([m['codigo'] for m in security['modulos']],['usuarios','accesos','auditoria'])
        self.assertEqual(security['cantidad'],3)
        self.assertEqual(len(r.context['tarjetas_seguridad']),4)
        self.assertContains(r,'security-card-track')
        self.assertEqual(r.context['cantidad_modulos'],sum(g['cantidad'] for g in r.context['grupos_navegacion']))
    def test_single_permission_produces_a_single_visible_module(self):
        role=Rol.objects.get(codigo='CIUDADANO');RolPermiso.objects.filter(rol=role).exclude(permiso__codigo='mascotas.participar').delete()
        r=self.browser(self.ciudadano).get('/panel/')
        self.assertEqual(r.context['cantidad_modulos'],1)
        self.assertFalse(any(g['codigo']=='seguridad' for g in r.context['grupos_navegacion']))
    def test_role_creation_assigns_permissions_atomically_and_keeps_scope(self):
        p=Permiso.objects.get(codigo='caso.ver')
        role=guardar_rol(self.admin,{'codigo':'EQUIPO_LOCAL','nombre':'Equipo local','descripcion':'Consulta local','ambito':'ENTIDAD','delegable':True,'entidad':self.entidad,'permisos':[p.pk]})
        self.assertTrue(RolPermiso.objects.filter(rol=role,permiso=p).exists())
        with self.assertRaises(ValidationError):validar_rol(self.admin,role,self.ajena.pk)
    def test_limited_editor_cannot_escalate_a_role(self):
        role=Rol.objects.create(codigo='EDITOR_LIMITADO',nombre='Editor limitado',ambito='GLOBAL')
        for code in ('roles.editar','roles.ver'):RolPermiso.objects.create(rol=role,permiso=Permiso.objects.get(codigo=code))
        UsuarioRol.objects.create(usuario=self.ciudadano,rol=role)
        with self.assertRaises(PermissionDenied):guardar_permisos(self.ciudadano,Rol.objects.get(codigo='CIUDADANO'),[Permiso.objects.get(codigo='usuarios.editar').pk])
    def test_logical_user_removal_keeps_history_and_is_idempotent(self):
        p=preparar_confirmacion(self.admin,'usuarios',self.ciudadano.pk);before=EventoSeguridad.objects.count()
        args=dict(motivo='Baja de pruebas',confirmacion=p['confirmacion_token'],nombre=p['confirmacion_nombre'],acepto=True)
        a=ejecutar_baja(self.admin,'usuarios',self.ciudadano.pk,'eliminar',**args)
        b=ejecutar_baja(self.admin,'usuarios',self.ciudadano.pk,'eliminar',**args)
        self.assertEqual(a,b);self.assertTrue(Usuario.objects.filter(pk=self.ciudadano.pk).exists())
        self.assertFalse(puede(self.ciudadano,'mascotas.participar'))
        self.assertEqual(OperacionAdministrativa.objects.count(),1)
        self.assertEqual(EventoSeguridad.objects.count(),before+1)
        self.assertTrue(UsuarioRol.objects.filter(usuario=self.ciudadano).exists())
    def test_physical_removal_is_blocked_by_dependencies(self):
        with self.assertRaises(ValidationError):self.execute('usuarios',self.ciudadano,'fisica')
        self.assertTrue(Usuario.objects.filter(pk=self.ciudadano.pk).exists())
    def test_physical_removal_is_allowed_only_for_an_unused_account(self):
        user=Usuario.objects.create_user(email='sin-vinculos@example.invalid',nombre='Sin vínculos',password='Prueba-unica-19384')
        self.execute('usuarios',user,'fisica')
        self.assertFalse(Usuario.objects.filter(pk=user.pk).exists())
    def test_essential_role_and_own_account_are_protected(self):
        for tipo,obj in [('roles',Rol.objects.get(codigo='ADMIN_SEGURIDAD')),('usuarios',self.admin)]:
            with self.assertRaises(ValidationError):self.execute(tipo,obj)
    def test_confirmation_and_concurrency_are_revalidated(self):
        p=preparar_confirmacion(self.admin,'usuarios',self.ciudadano.pk)
        self.ciudadano.nombre='Cambio concurrente';self.ciudadano.save(update_fields=['nombre'])
        with self.assertRaises(ValidationError):self.execute('usuarios',self.ciudadano,token=p['confirmacion_token'])
        self.assertFalse(BajaAdministrativa.objects.exists())
    def test_entity_deactivation_preserves_memberships_and_blocks_scoped_access(self):
        self.assertTrue(puede(self.carlos,'miembros.ver',entidad_id=self.entidad.pk))
        self.execute('entidades',self.entidad,'desactivar')
        self.assertFalse(puede(self.carlos,'miembros.ver',entidad_id=self.entidad.pk))
        self.assertTrue(EntidadMiembro.objects.filter(pk=self.carlos_m.pk).exists())
        self.execute('entidades',self.entidad,'restaurar')
        self.assertTrue(puede(self.carlos,'miembros.ver',entidad_id=self.entidad.pk))
    def test_audit_redacts_secrets_and_snapshots_actor(self):
        e=auditar(self.admin,'registro.consultar','mascotas',105,password='NEVER',nested={'token':'HIDDEN','dato':'visible'})
        self.assertNotIn('NEVER',str(e.datos));self.assertNotIn('HIDDEN',str(e.datos))
        self.assertEqual(e.datos['_contexto']['actor_id'],self.admin.pk)
        self.assertIn('ADMIN_SEGURIDAD',e.datos['_contexto']['roles_vigentes'])
    def test_audit_grouping_and_export_keep_individual_events(self):
        a=auditar(self.admin,'registro.consultar','mascotas',105);b=auditar(self.admin,'registro.consultar','mascotas',106)
        c=self.browser();r=c.get('/panel/auditoria/?agrupar=usuario')
        self.assertContains(r,'#105');self.assertContains(r,'#106')
        self.assertTrue(EventoSeguridad.objects.filter(pk=a.pk).exists())
        exported=c.get('/panel/auditoria/?exportar=csv');self.assertEqual(exported.status_code,200)
        body=b''.join(exported.streaming_content).decode();self.assertIn('mascotas',body);self.assertNotIn('password',body)

    @override_settings(ROOT_URLCONF=__name__)
    def test_duplicate_audit_calls_inside_one_request_are_deduplicated(self):
        before=EventoSeguridad.objects.count();r=self.browser().get('/_audit-probe/')
        self.assertEqual(r.json()['a'],r.json()['b'])
        self.assertEqual(EventoSeguridad.objects.count(),before+1)

    def test_archiving_is_private_and_does_not_delete_history(self):
        e=auditar(self.admin,'registro.consultar','mascotas',105);before=EventoSeguridad.objects.count()
        with TemporaryDirectory() as temp:
            with override_settings(LPN_PRIVATE_ROOT=temp):
                call_command('archivar_auditoria',antes=(timezone.now()+timedelta(days=1)).isoformat(),escribir=True,stdout=StringIO())
            self.assertEqual(len(list(Path(temp).rglob('*.jsonl.gz'))),1)
            self.assertEqual(len(list(Path(temp).rglob('*.manifest.json'))),1)
        self.assertEqual(EventoSeguridad.objects.count(),before)
        self.assertTrue(EventoSeguridad.objects.filter(pk=e.pk).exists())

    def test_role_form_version_rejects_concurrent_overwrite(self):
        role=guardar_rol(self.admin,{'codigo':'VERSIONADO','nombre':'Versionado','descripcion':'Prueba de concurrencia','ambito':'GLOBAL'})
        old=version_rol(role)
        guardar_rol(self.admin,{'nombre':'Nombre actualizado'},role,version=old)
        with self.assertRaises(ValidationError):guardar_rol(self.admin,{'nombre':'Nombre obsoleto'},role,version=old)
        role.refresh_from_db();self.assertEqual(role.nombre,'Nombre actualizado')

    def test_delete_permission_does_not_require_the_separate_deactivation_permission(self):
        role=Rol.objects.create(codigo='BAJAS_LIMITADAS',nombre='Bajas limitadas',ambito='GLOBAL')
        RolPermiso.objects.create(rol=role,permiso=Permiso.objects.get(codigo='usuarios.eliminar'))
        UsuarioRol.objects.create(usuario=self.carlos,rol=role)
        target=cuenta('destino_baja')
        data=preparar_confirmacion(self.carlos,'usuarios',target.pk)
        ejecutar_baja(self.carlos,'usuarios',target.pk,'eliminar',motivo='Baja autorizada',confirmacion=data['confirmacion_token'],nombre=data['confirmacion_nombre'],acepto=True)
        target.refresh_from_db();self.assertFalse(target.is_active)

    def test_technical_admin_form_rejects_last_superuser_demotion(self):
        from accounts.admin import CuentaForm
        root=Usuario.objects.create_superuser(email='raiz-tecnica@example.invalid',nombre='Raíz',password='Prueba-Superusuario-983424')
        form=CuentaForm(data={'nombre':root.nombre,'email':root.email,'is_active':True,'is_staff':True,'is_superuser':False},instance=root)
        self.assertFalse(form.is_valid())
        root.refresh_from_db();self.assertTrue(root.is_superuser)

    def test_technical_admin_form_reports_deactivation_as_validation_error(self):
        from accounts.admin import CuentaForm
        root=Usuario.objects.create_superuser(email='raiz-protegida@example.invalid',nombre='Raíz protegida',password='Prueba-Superusuario-983424')
        form=CuentaForm(data={'nombre':root.nombre,'email':root.email,'is_active':False,'is_staff':True,'is_superuser':True},instance=root)
        self.assertFalse(form.is_valid())
        self.assertIn('protegida',str(form.errors))

    def test_removal_confirmation_includes_the_reviewed_role_description(self):
        role=guardar_rol(self.admin,{'codigo':'BAJA_VERSION','nombre':'Baja versionada','descripcion':'Descripción revisada','ambito':'GLOBAL'})
        data=preparar_confirmacion(self.admin,'roles',role.pk)
        role.descripcion='Descripción modificada';role.save(update_fields=['descripcion'])
        with self.assertRaises(ValidationError):ejecutar_baja(self.admin,'roles',role.pk,'eliminar',motivo='Prueba de versión',confirmacion=data['confirmacion_token'],nombre=role.nombre,acepto=True)
        role.refresh_from_db();self.assertTrue(role.activo)

    def test_out_of_range_identifier_does_not_break_failure_auditing(self):
        response=self.cliente(self.admin).get('/api/seguridad/roles/9999999999999999999999999999999999/')
        self.assertEqual(response.status_code,404)
        event=EventoSeguridad.objects.latest('pk')
        self.assertIsNone(event.objeto_id)
        self.assertEqual(event.datos['_contexto']['resultado'],'FALLIDA')

    def test_organization_aliases_count_as_one_shared_screen(self):
        r=self.browser(self.carlos).get('/panel/')
        entries=[m for g in r.context['grupos_navegacion'] for m in g['modulos']]
        org=[m for m in entries if m['url']=='/panel/areas/organizaciones/']
        self.assertEqual(len(org),1)
        self.assertIn('Responsable secundario',str(r.context['rol_visible']))

    def test_declared_accounts_module_opens_without_unrelated_team_permission(self):
        user=cuenta('cuentas_limitadas')
        role=Rol.objects.create(codigo='CUENTAS_VISTA',nombre='Gestión de cuentas',descripcion='Gestión específica',ambito='ENTIDAD')
        member=EntidadMiembro.objects.create(usuario=user,entidad=self.entidad)
        RolPermiso.objects.create(rol=role,permiso=Permiso.objects.get(codigo='cuenta.aprobar'))
        from core.models import EntidadMiembroRol
        EntidadMiembroRol.objects.create(miembro=member,rol=role)
        self.assertFalse(motor(user).base('miembros.ver',self.entidad.pk))
        r=self.browser(user).get('/panel/areas/organizaciones/')
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.context['equipo_area'],[])
        self.assertIn('Gestión de cuentas',str(r.context['rol_visible']))

    def test_assignment_lists_the_whole_catalog_without_losing_scope(self):
        local=Rol.objects.create(codigo='SOLO_ORG_A',nombre='Coordinador A',ambito='ENTIDAD',entidad=self.entidad)
        inactive=Rol.objects.create(codigo='ARCHIVADO',nombre='Rol archivado',ambito='GLOBAL',activo=False)
        r=self.browser().get(f'/panel/seguridad/?tab=usuarios&usuario={self.carlos.pk}')
        cargos={c['rol'].pk:c for c in r.context['cargos']}
        self.assertEqual(set(cargos),set(Rol.objects.values_list('pk',flat=True)))
        self.assertTrue(cargos[local.pk]['bloqueado'])
        self.assertFalse(cargos[inactive.pk]['bloqueado'])
        self.assertContains(r,'type="reset"')
        self.assertContains(r,'assignment-list')
        r=self.browser().get(f'/panel/seguridad/?tab=usuarios&usuario={self.carlos.pk}&entidad={self.entidad.pk}')
        cargos={c['rol'].pk:c for c in r.context['cargos']}
        self.assertFalse(cargos[local.pk]['bloqueado'])
        self.assertFalse(cargos[Rol.objects.get(codigo='ADMIN_SEGURIDAD').pk]['bloqueado'])

    def test_assignment_rejects_roles_bound_to_another_organization(self):
        local=Rol.objects.create(codigo='SOLO_ORG_B',nombre='Coordinador B',ambito='ENTIDAD',entidad=self.ajena)
        c=self.browser();url=f'/panel/seguridad/?tab=usuarios&usuario={self.carlos.pk}&entidad={self.entidad.pk}'
        r=c.get(url)
        response=c.post(url,{'usuario':self.carlos.pk,'entidad':self.entidad.pk,'firma_persona':r.context['firma_persona'],'roles':[local.pk],'motivo':'Probar límite de organización'})
        self.assertEqual(response.status_code,200)
        self.assertTrue(response.context['error_admin'])
        from core.models import EntidadMiembroRol
        self.assertFalse(EntidadMiembroRol.objects.filter(miembro=self.carlos_m,rol=local,fecha_revocacion__isnull=True).exists())
        self.assertTrue(EntidadMiembroRol.objects.filter(miembro=self.carlos_m,rol__codigo='RESPONSABLE_SECUNDARIO',fecha_revocacion__isnull=True).exists())

    def test_actions_catalog_explains_assignment_and_lists_real_actions(self):
        r=self.browser().get('/panel/acciones/?codigo=usuarios.ver')
        self.assertEqual(r.status_code,200)
        self.assertContains(r,'action-guide')
        self.assertContains(r,'usuarios.ver')
        self.assertContains(r,'type="reset"')

    def test_audit_advanced_filters_remain_open_when_applied(self):
        r=self.browser().get('/panel/auditoria/?tipo=seguridad')
        self.assertContains(r,'class="audit-filter-advanced" open')
