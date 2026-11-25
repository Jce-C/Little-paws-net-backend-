from io import StringIO
from django.test import Client
from django.core.management import call_command
from rest_framework.test import APIClient
from rest_framework.exceptions import ValidationError
from seguridad.tests import BaseRBAC,valor
from core.models import Ciudad,Rol,EntidadMiembro,EntidadMiembroRol,Fundacion,CapacidadFundacion
from animals.models import Especie,Raza,Mascota
from rescue.models import Reporte
from geography.models import ReporteUbicacion,CoberturaCiudadFundacion
from seguridad.models import EventoSeguridad
from seguridad.administracion_segura import preparar_confirmacion,ejecutar_baja
from seguridad.catalogos import guardar,version

class FaseTresTests(BaseRBAC):
    def browser(self,u=None):
        c=Client();c.force_login(u or self.admin);return c
    def api(self,u=None):
        c=APIClient();c.force_authenticate(u or self.admin);return c
    def test_production_catalog_load_is_idempotent_and_creates_no_business_records(self):
        before=(Mascota.objects.count(),Reporte.objects.count());out=StringIO()
        call_command('cargar_catalogos_produccion',stdout=out);first=(Ciudad.objects.count(),Raza.objects.count())
        call_command('cargar_catalogos_produccion',stdout=out)
        self.assertEqual(first,(Ciudad.objects.count(),Raza.objects.count()));self.assertGreaterEqual(first[0],1100)
        self.assertEqual(before,(Mascota.objects.count(),Reporte.objects.count()))
        self.assertTrue(Ciudad.objects.filter(codigo_divipola='44001').exists())
    def test_simple_deactivation_needs_confirmation_but_no_reason_or_typing(self):
        data=preparar_confirmacion(self.admin,'usuarios',self.ciudadano.pk)
        result=ejecutar_baja(self.admin,'usuarios',self.ciudadano.pk,'desactivar',confirmacion=data['confirmacion_token'],nombre='',motivo='',acepto=True)
        self.assertFalse(result['estado']['activo']);self.assertTrue(EventoSeguridad.objects.filter(accion='usuarios.desactivar').exists())
    def test_deletion_still_requires_reason_and_typed_identity(self):
        d=preparar_confirmacion(self.admin,'usuarios',self.ciudadano.pk)
        with self.assertRaises(ValidationError):ejecutar_baja(self.admin,'usuarios',self.ciudadano.pk,'eliminar',confirmacion=d['confirmacion_token'],nombre='',motivo='',acepto=True)
        self.ciudadano.refresh_from_db();self.assertTrue(self.ciudadano.is_active)
    def test_simple_confirmation_has_no_unnecessary_fields(self):
        r=self.browser().get(f'/panel/bajas/usuarios/{self.ciudadano.pk}/?accion=desactivar')
        self.assertNotContains(r,'name="confirmar_nombre"');self.assertNotContains(r,'name="motivo"');self.assertContains(r,'name="confirmacion_token"')
    def test_report_with_written_address_has_no_fabricated_coordinates(self):
        city=Ciudad.objects.create(nombre='Riohacha',departamento='La Guajira')
        r=self.api(self.ciudadano).post('/api/reportes/',{'tipo_reporte':valor('tipo_reporte','Rescate').pk,'descripcion':'Animal requiere ayuda','ciudad_id':city.pk,'barrio':'Centro','direccion':'Frente al parque'},format='json')
        self.assertEqual(r.status_code,201,r.data);obj=Reporte.objects.get(pk=r.data['id_reporte'])
        self.assertEqual(obj.ciudad,city);self.assertEqual(obj.barrio,'Centro');self.assertFalse(ReporteUbicacion.objects.filter(reporte=obj).exists())
        self.assertTrue(EventoSeguridad.objects.filter(accion='reporte.crear',objeto_id=obj.pk).exists())
    def test_report_rejects_incomplete_written_location(self):
        r=self.api(self.ciudadano).post('/api/reportes/',{'tipo_reporte':valor('tipo_reporte','Rescate').pk,'descripcion':'Animal requiere ayuda'},format='json')
        self.assertEqual(r.status_code,400);self.assertIn('ciudad_id',r.data);self.assertIn('barrio',r.data);self.assertIn('direccion',r.data)
    def test_city_coverage_is_explicit_and_required_for_address_only_report(self):
        from rescue.services import _fundacion_tiene_cobertura
        city=Ciudad.objects.create(nombre='Ciudad prueba',departamento='Prueba')
        fund=Fundacion.objects.create(entidad=self.entidad,ciudad=city,nit='123456')
        report=Reporte.objects.create(usuario_reportante=self.ciudadano,ciudad=city,barrio='Centro',direccion='Parque',descripcion='Prueba',estado_reporte=valor('estado_reporte','Pendiente'),tipo_reporte=valor('tipo_reporte','Rescate'))
        self.assertFalse(_fundacion_tiene_cobertura(fund.pk,report.pk))
        CoberturaCiudadFundacion.objects.create(fundacion=fund,ciudad=city)
        self.assertTrue(_fundacion_tiene_cobertura(fund.pk,report.pk))
    def test_contexts_show_real_organizations_and_require_explicit_membership(self):
        c=self.browser();url=f'/panel/seguridad/?tab=usuarios&usuario={self.ciudadano.pk}&entidad={self.entidad.pk}'
        r=c.get(url);self.assertTrue(r.context['requiere_membresia']);self.assertContains(r,self.entidad.nombre)
        data={'usuario':self.ciudadano.pk,'entidad':self.entidad.pk,'roles':[Rol.objects.get(codigo='GESTOR_RESCATES').pk],'firma_persona':r.context['firma_persona'],'motivo':'Incorporación autorizada'}
        response=c.post(url,data);self.assertEqual(response.status_code,200);self.assertFalse(EntidadMiembro.objects.filter(usuario=self.ciudadano,entidad=self.entidad).exists())
        data['incorporar']='1';response=c.post(url,data);self.assertEqual(response.status_code,302)
        self.assertTrue(EntidadMiembroRol.objects.filter(miembro__usuario=self.ciudadano,miembro__entidad=self.entidad,rol__codigo='GESTOR_RESCATES',fecha_revocacion__isnull=True).exists())
    def test_limited_actor_does_not_see_unrelated_context(self):
        from core.models import UsuarioRol,RolPermiso,Permiso
        role=Rol.objects.create(codigo='ASIGNADOR_LIMITADO',nombre='Asignador limitado',ambito='GLOBAL');RolPermiso.objects.create(rol=role,permiso=Permiso.objects.get(codigo='roles.asignar'));UsuarioRol.objects.create(usuario=self.ciudadano,rol=role)
        r=self.browser(self.ciudadano).get(f'/panel/seguridad/?tab=usuarios&usuario={self.ana.pk}&entidad={self.entidad.pk}');self.assertEqual(r.status_code,403)
    def test_catalog_edits_are_versioned_and_keep_existing_relations(self):
        city=guardar(self.admin,'ciudades',{'nombre':'Prueba catálogo','departamento':'Pruebas','activo':True})
        old=version(city);city=guardar(self.admin,'ciudades',{'nombre':'Prueba nueva','departamento':'Pruebas','activo':False},city.pk,old)
        self.assertFalse(city.activo);self.assertTrue(Ciudad.objects.filter(pk=city.pk).exists())
        with self.assertRaises(ValidationError):guardar(self.admin,'ciudades',{'nombre':'Conflicto','departamento':'Pruebas','activo':True},city.pk,old)
    def test_unknown_animal_no_longer_requires_a_breed_catalog(self):
        r=self.browser().get('/panel/areas/mascotas/?accion=crear-ficha')
        self.assertContains(r,'Otra especie o animal no identificado');self.assertFalse(r.context['form_operacion'].bloqueos)
    def test_dashboard_count_matches_filtered_pet_list_and_labels_permissions(self):
        raza=Raza.objects.create(especie=Especie.objects.create(nombre='Perro'),nombre='Mestizo')
        Mascota.objects.create(nombre='Disponible',raza=raza,estado_mascota=valor('estado_mascota','En adopción'))
        c=self.browser();home=c.get('/panel/');metric=next(x for x in home.context['indicadores'] if x['nombre']=='Mascotas disponibles para adopción')
        listing=c.get(metric['url']);self.assertEqual(metric['valor'],len(listing.context['registros']));self.assertContains(home,'permisos</small>')
    def test_catalogs_and_role_editor_are_connected_and_grouped(self):
        c=self.browser();self.assertEqual(c.get('/panel/catalogos/').status_code,200)
        r=c.get('/panel/seguridad/?tab=roles&editar='+str(Rol.objects.get(codigo='CIUDADANO').pk));self.assertContains(r,'permission-category');self.assertGreater(len(r.context['grupos_permisos_rol']),5)
    def test_audit_group_has_period_and_expandable_events(self):
        from seguridad.servicios import auditar
        auditar(self.admin,'catalogos.crear','catalogos',1)
        r=self.browser().get('/panel/auditoria/?agrupar=usuario');self.assertTrue(r.context['grupos_auditoria']);self.assertContains(r,'<details class="audit-group">')

    def test_city_coverage_and_new_report_complete_the_rescue_flow(self):
        city=Ciudad.objects.create(nombre='Ciudad de cobertura',departamento='Prueba')
        fund=Fundacion.objects.create(entidad=self.entidad,ciudad=city,nit='987654')
        CapacidadFundacion.objects.create(fundacion=fund,cupos_totales=2,usuario_actualizador=self.ana)
        r=self.api(self.ana).post(f'/api/seguridad/organizaciones/{fund.pk}/cobertura/',{'ciudad_id':city.pk,'activo':True},format='json')
        self.assertEqual(r.status_code,200,r.data)
        r=self.api(self.ciudadano).post('/api/reportes/',{'tipo_reporte':valor('tipo_reporte','Rescate').pk,'descripcion':'Ayuda para rescate','ciudad_id':city.pk,'barrio':'Centro','direccion':'Frente al parque'},format='json')
        self.assertEqual(r.status_code,201,r.data)
        EntidadMiembroRol.objects.create(miembro=self.carlos_m,rol=Rol.objects.get(codigo='GESTOR_RESCATES'))
        accepted=self.api(self.carlos).post(f"/api/reportes/{r.data['id_reporte']}/aceptar/",{'id_fundacion':fund.pk},format='json')
        self.assertEqual(accepted.status_code,201,accepted.data)
        from rescue.models import CasoRescate
        self.assertTrue(CasoRescate.objects.filter(reporte_id=r.data['id_reporte'],fundacion=fund).exists())
        # Continue through custody, publication and adoption using real endpoints.
        race=Raza.objects.create(especie=Especie.objects.create(nombre='Perro rescatado'),nombre='Mestizo')
        pet_result=self.api(self.carlos).post(f"/api/seguridad/casos/{accepted.data['id_caso']}/mascota/",{'nombre':'Rescatada en flujo completo','raza_id':race.pk},format='json')
        self.assertEqual(pet_result.status_code,201,pet_result.data);pet_id=pet_result.data['id']
        again=self.api(self.carlos).post(f"/api/seguridad/casos/{accepted.data['id_caso']}/mascota/",{'nombre':'Duplicada','raza_id':race.pk},format='json');self.assertEqual(again.status_code,400)
        EntidadMiembroRol.objects.create(miembro=self.carlos_m,rol=Rol.objects.get(codigo='GESTOR_ADOPCIONES'))
        published=self.api(self.carlos).post(f'/api/seguridad/mascotas-administrar/{pet_id}/disponibilidad/',{'confirmar':True,'disponible':True},format='json');self.assertEqual(published.status_code,200,published.data)
        application=self.api(self.ciudadano).post('/api/adopcion/solicitudes/',{'id_mascota':pet_id},format='json');self.assertEqual(application.status_code,201,application.data)
        aid=application.data['id_solicitud_adopcion']
        taken=self.api(self.carlos).post(f'/api/seguridad/asignaciones/adopcion/{aid}/tomar/',{},format='json');self.assertEqual(taken.status_code,200,taken.data)
        resolved=self.api(self.carlos).post(f'/api/adopcion/solicitudes/{aid}/resolver/',{'id_fundacion':fund.pk,'aprobar':True},format='json');self.assertEqual(resolved.status_code,200,resolved.data)
        pet=Mascota.objects.get(pk=pet_id);self.assertEqual(pet.estado_mascota.nombre,'Adoptada');self.assertEqual(pet.dueno_id,self.ciudadano.pk)

    def test_historical_report_coordinates_remain_consultable(self):
        report=Reporte.objects.create(usuario_reportante=self.ciudadano,descripcion='Reporte anterior',estado_reporte=valor('estado_reporte','Pendiente'),tipo_reporte=valor('tipo_reporte','Rescate'))
        point=ReporteUbicacion.objects.create(reporte=report,latitud='4.600000',longitud='-74.080000')
        r=self.browser().get('/panel/areas/reportes/?detalle='+str(report.pk))
        self.assertEqual(r.status_code,200);self.assertContains(r,'4.600000')
        point.refresh_from_db();self.assertEqual(str(point.longitud),'-74.080000');report.refresh_from_db();self.assertIsNone(report.ciudad_id)
    def test_catalog_permission_is_required_and_inactive_breed_cannot_be_used(self):
        self.assertEqual(self.api(self.ciudadano).post('/api/seguridad/catalogos/especies/',{'nombre':'Nueva especie','activo':True},format='json').status_code,403)
        race=Raza.objects.create(especie=Especie.objects.create(nombre='Prueba'),nombre='Inactiva',activo=False)
        r=self.api(self.ciudadano).post('/api/seguridad/operaciones/mascotas-propias/',{'nombre':'Nueva ficha','raza_id':race.pk},format='json')
        self.assertEqual(r.status_code,400);self.assertFalse(Mascota.objects.filter(nombre='Nueva ficha').exists())
    def test_species_labels_are_readable_in_catalog_form(self):
        Especie.objects.create(nombre='Nombre legible')
        r=self.browser().get('/panel/catalogos/?tipo=razas&nuevo=1')
        self.assertContains(r,'Nombre legible');self.assertNotContains(r,'Especie object')

    def test_availability_cannot_override_private_ownership(self):
        race=Raza.objects.create(especie=Especie.objects.create(nombre='Perro propio'),nombre='Mestizo')
        pet=Mascota.objects.create(nombre='Tiene dueño',dueno=self.ciudadano,raza=race,estado_mascota=valor('estado_mascota','Con dueño'))
        r=self.api().post(f'/api/seguridad/mascotas-administrar/{pet.pk}/disponibilidad/',{'confirmar':True,'disponible':True},format='json')
        self.assertEqual(r.status_code,400);pet.refresh_from_db();self.assertEqual(pet.dueno_id,self.ciudadano.pk)
