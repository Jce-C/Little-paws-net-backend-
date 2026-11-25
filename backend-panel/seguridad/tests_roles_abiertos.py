from django.test import Client
from rest_framework.exceptions import ValidationError
from seguridad.tests import BaseRBAC
from core.models import Rol,RolPermiso,Permiso,UsuarioRol,EntidadMiembroRol
from seguridad.asignaciones import guardar_roles,firma_persona
from seguridad.autorizacion import motor,principal_de
from seguridad.models import ResponsableEntidad,ExcepcionPermiso,EventoSeguridad


class RolesAbiertosTests(BaseRBAC):
    def guardar(self,roles,entidad=None,**extra):
        return guardar_roles(self.admin,self.carlos.pk,[r.pk for r in roles],entidad,
            firma_persona(self.carlos,entidad,'usuarios'),'Configuración explícita de perfiles',**extra)

    def test_general_accepts_every_active_unbound_profile_and_real_permissions(self):
        roles=list(Rol.objects.filter(activo=True,entidad__isnull=True))
        self.guardar(roles)
        self.assertCountEqual(UsuarioRol.objects.filter(usuario=self.carlos,fecha_revocacion__isnull=True).values_list('rol_id',flat=True),[r.pk for r in roles])
        m=motor(self.carlos)
        self.assertTrue(m.base('usuarios.ver'))
        self.assertTrue(m.base('caso.ver',self.entidad.pk))
        self.assertFalse(m.base('caso.ver',self.ajena.pk))

    def test_organization_also_accepts_a_platform_profile(self):
        role=Rol.objects.get(codigo='MODERADOR')
        self.guardar([role],self.entidad.pk)
        self.assertTrue(motor(self.carlos).base('verificacion.ver'))
        self.assertTrue(EntidadMiembroRol.objects.filter(miembro=self.carlos_m,rol=role,fecha_revocacion__isnull=True).exists())

    def test_assign_revoke_and_refresh_same_session_for_former_entity_role(self):
        role=Rol.objects.get(codigo='GESTOR_ADOPCIONES')
        p=Permiso.objects.get(codigo='usuarios.ver');RolPermiso.objects.get_or_create(rol=role,permiso=p)
        c=Client();c.force_login(self.carlos)
        self.assertEqual(c.get('/panel/usuarios/').status_code,403)
        self.guardar([role])
        self.assertEqual(c.get('/panel/usuarios/').status_code,200)
        self.assertTrue(motor(self.carlos).base('adopcion.ver',self.entidad.pk))
        self.guardar([])
        self.assertEqual(c.get('/panel/usuarios/').status_code,403)

    def test_inactive_profiles_need_explicit_activation_and_record_it(self):
        role=Rol.objects.get(codigo='GESTOR_FUNDACION');self.assertFalse(role.activo)
        RolPermiso.objects.get_or_create(rol=role,permiso=Permiso.objects.get(codigo='caso.ver'))
        with self.assertRaises(ValidationError):self.guardar([role])
        self.guardar([role],activar_inactivos=True)
        role.refresh_from_db();self.assertTrue(role.activo)
        self.assertTrue(EventoSeguridad.objects.filter(accion='roles.restaurar',objeto_id=role.pk).exists())
        self.assertTrue(motor(self.carlos).base('caso.ver',self.entidad.pk))

    def test_principal_profile_does_not_transfer_real_responsibility(self):
        principal=Rol.objects.get(codigo='RESPONSABLE_PRINCIPAL')
        before=ResponsableEntidad.objects.get(entidad=self.entidad).principal_id
        self.guardar([principal])
        self.assertTrue(motor(self.carlos).base('principal.transferir',self.entidad.pk))
        self.assertFalse(principal_de(self.carlos,self.entidad.pk))
        self.assertEqual(ResponsableEntidad.objects.get(entidad=self.entidad).principal_id,before)

    def test_all_current_profiles_are_available_without_three_role_whitelist(self):
        c=Client();c.force_login(self.admin)
        page=c.get(f'/panel/seguridad/?tab=usuarios&usuario={self.carlos.pk}')
        entries=page.context['cargos']
        self.assertEqual(len(entries),Rol.objects.count())
        self.assertFalse(any(r['bloqueado'] for r in entries))
        self.assertGreater(page.context['cantidad_asignables'],3)
        self.assertContains(page,'activar_inactivos')

    def test_individual_denial_still_wins_after_open_assignment(self):
        role=Rol.objects.get(codigo='GESTOR_RESCATES')
        p=Permiso.objects.get(codigo='usuarios.ver');RolPermiso.objects.get_or_create(rol=role,permiso=p)
        self.guardar([role])
        ExcepcionPermiso.objects.create(usuario=self.carlos,permiso=p,contexto_id=0,efecto='DENEGAR',motivo='Restricción individual explícita',autor=self.admin)
        self.assertFalse(motor(self.carlos).base('usuarios.ver'))
