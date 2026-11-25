from datetime import timedelta
from django.test import Client
from django.utils import timezone
from core.models import Rol,RolPermiso,UsuarioRol,Permiso,EntidadMiembro
from .tests import BaseRBAC,cuenta
from .autorizacion import puede,tiene_base
from .excepciones import guardar
from .models import ExcepcionPermiso,RevisionPanel,EventoSeguridad


class RBACDinamicoTests(BaseRBAC):
    def preparar_robert(self):
        rol=Rol.objects.get(codigo='CIUDADANO')
        UsuarioRol.objects.get_or_create(usuario=self.ciudadano,rol=rol)
        EntidadMiembro.objects.create(usuario=self.ciudadano,entidad=self.entidad)
        permiso=Permiso.objects.get(codigo='adopcion.ver')
        RolPermiso.objects.get_or_create(rol=rol,permiso=permiso)
        return permiso

    def test_robert_conserva_ciudadano_y_su_excepcion_no_afecta_a_otros(self):
        adopcion=self.preparar_robert()
        otro=cuenta('otro_ciudadano')
        UsuarioRol.objects.get_or_create(usuario=otro,rol=Rol.objects.get(codigo='CIUDADANO'))
        EntidadMiembro.objects.create(usuario=otro,entidad=self.entidad)
        self.assertTrue(tiene_base(self.ciudadano,'adopcion.ver',entidad_id=self.entidad.pk))
        guardar(self.admin,self.ciudadano.pk,Permiso.objects.get(codigo='usuarios.ver').pk,'PERMITIR','Demostración de consulta administrativa')
        guardar(self.admin,self.ciudadano.pk,adopcion.pk,'DENEGAR','Bloqueo individual de adopciones',self.entidad.pk)
        self.assertTrue(puede(self.ciudadano,'usuarios.ver'))
        self.assertFalse(tiene_base(self.ciudadano,'adopcion.ver',entidad_id=self.entidad.pk))
        self.assertTrue(tiene_base(otro,'adopcion.ver',entidad_id=self.entidad.pk))
        self.assertFalse(puede(otro,'usuarios.ver'))
        self.assertTrue(UsuarioRol.objects.filter(usuario=self.ciudadano,rol__codigo='CIUDADANO',fecha_revocacion__isnull=True).exists())
        self.assertEqual(self.cliente(self.ciudadano).get('/api/seguridad/usuarios/').status_code,200)
        self.assertEqual(self.cliente(self.ciudadano).patch(f'/api/seguridad/usuarios/{otro.pk}/',{'nombre':'No autorizado'},format='json').status_code,403)

    def test_heredar_quita_la_excepcion_no_bloquea_los_roles(self):
        self.preparar_robert()
        p=Permiso.objects.get(codigo='adopcion.ver')
        guardar(self.admin,self.ciudadano.pk,p.pk,'DENEGAR','Bloquear',self.entidad.pk)
        guardar(self.admin,self.ciudadano.pk,p.pk,'HEREDAR','Volver a los roles',self.entidad.pk)
        self.assertTrue(tiene_base(self.ciudadano,p.codigo,entidad_id=self.entidad.pk))
        self.assertFalse(ExcepcionPermiso.objects.filter(usuario=self.ciudadano,permiso=p).exists())

    def test_denegar_prevalece_sobre_varios_roles(self):
        rol=Rol.objects.get(codigo='MODERADOR');p=Permiso.objects.get(codigo='usuarios.ver')
        RolPermiso.objects.create(rol=rol,permiso=p)
        UsuarioRol.objects.get_or_create(usuario=self.ciudadano,rol=rol)
        UsuarioRol.objects.create(usuario=self.ciudadano,rol=Rol.objects.get(codigo='ADMIN_SEGURIDAD'))
        guardar(self.admin,self.ciudadano.pk,p.pk,'DENEGAR','Denegación expresa')
        self.assertFalse(puede(self.ciudadano,p.codigo))

    def test_excepcion_caducada_y_revocacion_se_reflejan_sin_nuevo_login(self):
        p=Permiso.objects.get(codigo='usuarios.ver')
        guardar(self.admin,self.ciudadano.pk,p.pk,'PERMITIR','Acceso temporal',expira=timezone.now()+timedelta(minutes=1))
        c=Client();c.force_login(self.ciudadano)
        self.assertEqual(c.get('/panel/usuarios/').status_code,200)
        ExcepcionPermiso.objects.filter(usuario=self.ciudadano).update(expira=timezone.now()-timedelta(seconds=1))
        self.assertEqual(c.get('/panel/usuarios/').status_code,403)

    def test_superusuario_tiene_precedencia_y_no_se_concede_al_equipo(self):
        p=Permiso.objects.get(codigo='usuarios.ver')
        guardar(self.admin,self.ciudadano.pk,p.pk,'DENEGAR','Denegación ordinaria')
        self.ciudadano.is_superuser=True;self.ciudadano.save()
        self.assertTrue(puede(self.ciudadano,p.codigo))
        self.assertTrue(self.ciudadano.has_perm('accounts.change_usuario'))
        self.admin.refresh_from_db();self.assertFalse(self.admin.is_superuser)
        self.ciudadano.is_active=False;self.ciudadano.save()
        self.assertFalse(puede(self.ciudadano,p.codigo))

    def test_admin_tecnico_no_ofrece_un_segundo_editor_de_grupos(self):
        from django.contrib import admin
        from django.contrib.auth.models import Group
        self.assertFalse(admin.site.is_registered(Group))
        self.ciudadano.is_staff=self.ciudadano.is_superuser=True;self.ciudadano.save()
        c=Client();c.force_login(self.ciudadano)
        for url in ('/admin/','/admin/accounts/usuario/','/admin/core/rol/','/admin/seguridad/excepcionpermiso/'):
            with self.subTest(url=url):self.assertEqual(c.get(url).status_code,200)

    def test_excepcion_no_salta_membresia_ni_asignacion(self):
        p=self.preparar_robert()
        guardar(self.admin,self.ciudadano.pk,p.pk,'PERMITIR','Capacidad con contexto',self.entidad.pk)
        self.assertFalse(puede(self.ciudadano,p.codigo,entidad_id=self.entidad.pk))
        self.assertFalse(tiene_base(self.ciudadano,p.codigo,entidad_id=self.ajena.pk))

    def test_menu_y_encabezado_usan_el_nombre_guardado_del_recurso(self):
        from core.models import Recurso
        Recurso.objects.filter(codigo='usuarios').update(nombre='Personas del refugio')
        c=Client();c.force_login(self.admin)
        page=c.get('/panel/usuarios/')
        self.assertContains(page,'Personas del refugio')

    def test_excepcion_tiene_historial_anterior_nuevo_y_revision(self):
        antes=RevisionPanel.objects.get(pk=1).version
        guardar(self.admin,self.ciudadano.pk,Permiso.objects.get(codigo='usuarios.ver').pk,'PERMITIR','Demostración autorizada')
        evento=EventoSeguridad.objects.filter(accion='permiso.excepcion').first()
        self.assertEqual(evento.datos['anterior']['efecto'],'HEREDAR')
        self.assertEqual(evento.datos['nuevo']['efecto'],'PERMITIR')
        self.assertGreater(RevisionPanel.objects.get(pk=1).version,antes)

    def test_api_excepciones_no_permite_autoasignacion(self):
        p=Permiso.objects.get(codigo='usuarios.ver')
        r=self.cliente(self.ciudadano).post(f'/api/seguridad/usuarios/{self.ciudadano.pk}/excepciones/',{'permiso_id':p.pk,'efecto':'PERMITIR','motivo':'Intento'},format='json')
        self.assertEqual(r.status_code,403)

    def test_consultar_no_dispara_bucle_de_sincronizacion(self):
        from .servicios import auditar
        revision=RevisionPanel.objects.get(pk=1).version
        auditar(self.admin,'registro.consultar','adopcion',1)
        self.assertEqual(RevisionPanel.objects.get(pk=1).version,revision)

    def test_el_permiso_de_preparar_cuentas_se_puede_revocar(self):
        from .models import DelegacionCuenta
        from .tests import miembro_con_rol
        miembro=miembro_con_rol(self.ciudadano,self.entidad,'RESPONSABLE_SECUNDARIO')
        DelegacionCuenta.objects.create(entidad=self.entidad,miembro=miembro,otorgante=self.ana)
        self.assertTrue(puede(self.ciudadano,'cuenta.preparar',entidad_id=self.entidad.pk))
        guardar(self.admin,self.ciudadano.pk,Permiso.objects.get(codigo='cuenta.preparar').pk,'DENEGAR','Retirar capacidad delegada',self.entidad.pk)
        self.assertFalse(puede(self.ciudadano,'cuenta.preparar',entidad_id=self.entidad.pk))

    def test_matriz_en_pantalla_guarda_ciudadano_y_detecta_conflicto(self):
        c=Client();c.force_login(self.admin)
        rol=Rol.objects.get(codigo='CIUDADANO')
        endpoint=f'/panel/seguridad/?tab=permisos&rol={rol.pk}'
        pagina=c.get(endpoint)
        self.assertContains(pagina,'Consultar')
        self.assertNotContains(pagina,'<dialog')
        firma=pagina.context['firma'];p=Permiso.objects.get(codigo='usuarios.ver')
        r=c.post(endpoint,{'rol':rol.pk,'firma':firma,'permisos':[p.pk]})
        self.assertEqual(r.status_code,302)
        r=c.post(endpoint,{'rol':rol.pk,'firma':firma,'permisos':[]})
        self.assertContains(r,'Otra persona modificó esta matriz')

    def test_excepciones_en_pantalla_no_sobrescriben_un_cambio_concurrente(self):
        c=Client();c.force_login(self.admin)
        url=f'/panel/seguridad/?tab=excepciones&usuario={self.ciudadano.pk}'
        firma=c.get(url).context['firma_persona']
        p=Permiso.objects.get(codigo='usuarios.ver')
        guardar(self.admin,self.ciudadano.pk,p.pk,'DENEGAR','Cambio realizado en otra sesión')
        r=c.post(url,{'usuario':self.ciudadano.pk,'firma_persona':firma,'motivo':'Formulario obsoleto',f'excepcion_{p.pk}':'PERMITIR'})
        self.assertContains(r,'Las excepciones de esta persona cambiaron')
        self.assertEqual(ExcepcionPermiso.objects.get(usuario=self.ciudadano,permiso=p).efecto,'DENEGAR')

    def test_varios_roles_se_guardan_juntos_y_se_listan_en_usuarios(self):
        c=Client();c.force_login(self.admin)
        url=f'/panel/seguridad/?tab=usuarios&usuario={self.ciudadano.pk}'
        pagina=c.get(url);roles=list(Rol.objects.filter(codigo__in=['CIUDADANO','MODERADOR']).values_list('pk',flat=True))
        r=c.post(url,{'usuario':self.ciudadano.pk,'firma_persona':pagina.context['firma_persona'],'roles':roles,'motivo':'Dos roles simultáneos'})
        self.assertEqual(r.status_code,302)
        self.assertEqual(UsuarioRol.objects.filter(usuario=self.ciudadano,fecha_revocacion__isnull=True).count(),2)
        pagina=c.get('/panel/usuarios/')
        persona=next(p for p in pagina.context['personas'] if p['id_usuario']==self.ciudadano.pk)
        self.assertEqual(len(persona['roles_actuales']),2)
