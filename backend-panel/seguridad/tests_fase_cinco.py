from django.test import Client
from rest_framework.test import APIClient
from seguridad.tests import BaseRBAC,valor,entidad
from seguridad.flujos_serializers import MascotaEntrada
from core.models import Rol,UsuarioRol,Permiso,RolPermiso,EntidadMiembro,Fundacion,Ciudad,CapacidadFundacion,SolicitudValidacion
from animals.models import Mascota,Especie,Raza,CustodiaMascota
from seguridad.models import ResponsableEntidad,TransferenciaResponsabilidad
from seguridad.servicios import iniciar_transferencia
from adoption.consultas import disponibles_adopcion

class FaseCincoTests(BaseRBAC):
    def web(self,u=None):
        c=Client();c.force_login(u or self.admin);return c
    def api(self,u=None):
        c=APIClient();c.force_authenticate(u or self.admin);return c
    def test_unknown_animal_is_valid_without_fake_species_or_breed(self):
        before=(Especie.objects.count(),Raza.objects.count())
        r=self.api(self.ciudadano).post('/api/seguridad/operaciones/mascotas-propias/',{'nombre':'Ave encontrada','descripcion_especie':'Ave pequeña de plumaje amarillo'},format='json')
        self.assertEqual(r.status_code,201,r.data);p=Mascota.objects.get(pk=r.data['id'])
        self.assertIsNone(p.raza_id);self.assertIsNone(p.especie_id);self.assertEqual(p.especie_nombre,'Ave pequeña de plumaje amarillo')
        self.assertEqual((Especie.objects.count(),Raza.objects.count()),before)
    def test_species_without_breed_and_incompatible_breed_validation(self):
        a=Especie.objects.create(nombre='Ave');b=Especie.objects.create(nombre='Reptil');raza=Raza.objects.create(especie=a,nombre='Ejemplo de raza')
        s=MascotaEntrada(data={'nombre':'Animal','especie_id':a.pk});self.assertTrue(s.is_valid(),s.errors)
        s=MascotaEntrada(data={'nombre':'Animal','especie_id':b.pk,'raza_id':raza.pk});self.assertFalse(s.is_valid());self.assertIn('raza_id',s.errors)
        s=MascotaEntrada(data={'nombre':'Sin identificar'});self.assertFalse(s.is_valid());self.assertIn('descripcion_especie',s.errors)
    def test_designation_uses_organization_in_form_without_header_membership(self):
        e=entidad('Nueva organización de prueba');url=f'/panel/areas/organizaciones/?accion=designar-principal&organizacion={e.pk}'
        c=self.web();r=c.get(url);self.assertEqual(r.status_code,200)
        self.assertIn('organizacion',r.context['form_operacion'].fields)
        r=c.post(url,{'organizacion':e.pk,'usuario_id':self.ciudadano.pk,'recuperar':False,'motivo':'Designación inicial autorizada'})
        self.assertEqual(r.status_code,302, r.context['form_operacion'].errors if r.status_code==200 else '')
        self.assertEqual(ResponsableEntidad.objects.get(entidad=e).principal.usuario_id,self.ciudadano.pk)
        self.assertFalse(EntidadMiembro.objects.filter(usuario=self.admin,entidad=e).exists())
    def test_verification_uses_selected_entity_and_rejects_duplicate(self):
        e=entidad('Organización para verificar');url=f'/panel/areas/organizaciones/?accion=pedir-verificacion&organizacion={e.pk}'
        c=self.web();r=c.post(url,{'organizacion':e.pk});self.assertEqual(r.status_code,302)
        self.assertTrue(SolicitudValidacion.objects.filter(entidad=e,usuario_solicitante=self.admin).exists())
        r=c.post(url,{'organizacion':e.pk});self.assertEqual(r.status_code,200);self.assertTrue(r.context['form_operacion'].errors)
    def test_wrong_entity_is_rejected_before_dispatch(self):
        r=self.web(self.carlos).get(f'/panel/areas/organizaciones/?accion=incorporar-miembro&organizacion={self.ajena.pk}')
        self.assertEqual(r.status_code,403)
    def test_transfer_form_names_people_and_entity_and_accepts(self):
        transfer=iniciar_transferencia(self.ana,self.entidad.pk,self.carlos_m.pk,True)
        url=f'/panel/areas/organizaciones/?accion=resolver-transferencia&organizacion={self.entidad.pk}';c=self.web(self.carlos);r=c.get(url)
        self.assertEqual(r.status_code,200);self.assertContains(r,self.ana.nombre);self.assertContains(r,self.entidad.nombre)
        r=c.post(url,{'organizacion':self.entidad.pk,'registro':transfer.pk,'aceptar':True})
        self.assertEqual(r.status_code,302,r.context['form_operacion'].errors if r.status_code==200 else '')
        self.assertEqual(ResponsableEntidad.objects.get(entidad=self.entidad).principal_id,self.carlos_m.pk)
    def pet(self,name,state='En adopción'):
        p=Mascota.objects.create(nombre=name,descripcion_especie='Ave',estado_mascota=valor('estado_mascota',state))
        city=Ciudad.objects.create(nombre='Ciudad '+name,departamento='Prueba')
        from django.utils import timezone
        f=Fundacion.objects.create(entidad=entidad('Fundación '+name),ciudad=city,nit=str(p.pk));CustodiaMascota.objects.create(mascota=p,fundacion=f,usuario_registrador=self.admin,fecha_inicio=timezone.now())
        return p
    def test_public_catalog_excludes_nonadoptable_and_null_breed_is_safe(self):
        p=self.pet('Disponible');other=self.pet('En atención','En recuperación')
        from adoption.api import MascotasAdopcionView
        from rest_framework.test import APIRequestFactory
        r=MascotasAdopcionView.as_view()(APIRequestFactory().get('/'))
        self.assertIn(p.pk,[x['id_mascota'] for x in r.data]);self.assertNotIn(other.pk,[x['id_mascota'] for x in r.data])
        r=self.web().get('/panel/areas/mascotas/');self.assertContains(r,'Disponible');self.assertNotContains(r,'En atención')
        r=self.web().get('/panel/areas/mascotas/?vista=gestion');self.assertContains(r,'En atención')
    def test_stale_adoption_request_and_double_click(self):
        p=self.pet('Solicitud');c=self.api(self.ciudadano);url='/api/adopcion/solicitudes/'
        self.assertEqual(c.post(url,{'id_mascota':p.pk},format='json').status_code,201)
        self.assertEqual(c.post(url,{'id_mascota':p.pk},format='json').status_code,400)
        p.estado_mascota=valor('estado_mascota','En recuperación');p.save()
        self.assertEqual(self.api(self.otro).post(url,{'id_mascota':p.pk},format='json').status_code,400)
    def test_city_is_searchable_and_uses_identifier(self):
        city=Ciudad.objects.create(nombre='RIOHACHA',departamento='LA GUAJIRA',codigo_divipola='44001')
        r=self.web(self.ciudadano).get('/panel/areas/reportes/?accion=crear-reporte')
        self.assertContains(r,'RIOHACHA');self.assertContains(r,'data-searchable-select');self.assertContains(r,'¿Qué situación quieres reportar?')
    def test_landing_capsules_and_no_asset_added_to_idle_login(self):
        c=Client();r=c.get('/');self.assertContains(r,'capsule-section');self.assertContains(r,'capsula-nube-izquierda-arriba.svg')
        r=c.get('/panel/login/');self.assertNotContains(r,'capsulas.js');self.assertNotContains(r,'recorridos.js')
