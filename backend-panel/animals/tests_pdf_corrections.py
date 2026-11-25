"""Cross-boundary acceptance for the citizen flows requested in the correction PDF."""
from io import BytesIO
from unittest.mock import patch
from PIL import Image
from cryptography.fernet import Fernet
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework.test import APIClient
from seguridad.tests import BaseRBAC, valor, miembro_con_rol
from seguridad.models import PublicacionReporte
from seguridad.autorizacion import invalidar
from animals.models import Mascota, CustodiaMascota, PerfilMascotaPersonal
from adoption.models import SolicitudAdopcion
from core.models import Ciudad, Fundacion, Permiso, ValorMaestro
from rescue.models import FotoReporte, Reporte
from funds.models import FondoExterno

def photo(content=None):
    if content is None:
        stream=BytesIO();Image.new('RGB',(100,80),(180,130,80)).save(stream,'PNG');content=stream.getvalue()
    return SimpleUploadedFile('animal.png',content,content_type='image/png')

class CorreccionesCiudadanasTests(BaseRBAC):
    def setUp(self):
        self.city,_=Ciudad.objects.get_or_create(nombre='Riohacha',departamento='La Guajira')
        self.foundation=Fundacion.objects.create(entidad=self.entidad,ciudad=self.city,nit='QA-PDF-CORRECCIONES')
        self.pet=Mascota.objects.create(nombre='Mascota solicitud QA',descripcion_especie='Perro',estado_mascota=valor('estado_mascota','En adopción'))
        CustodiaMascota.objects.create(mascota=self.pet,fundacion=self.foundation,usuario_registrador=self.ana,fecha_inicio=timezone.now())
        self.own=self.cliente(self.ciudadano)
    def report_data(self):
        return {'tipo_reporte':valor('tipo_reporte','Rescate').pk,'ciudad_id':self.city.pk,'barrio':'Centro','direccion':'Referencia pública QA','descripcion':'Animal que necesita ayuda','archivo':photo(),'confirmar_foto_publica':'true'}
    def test_report_photo_is_saved_and_public_only_while_visible(self):
        response=self.own.post('/api/reportes/',self.report_data(),format='multipart');self.assertEqual(response.status_code,201,response.data)
        report_id=response.data['id_reporte'];stored=FotoReporte.objects.get(reporte_id=report_id)
        self.assertLessEqual(len(stored.contenido),128*1024)
        self.assertTrue(bytes(stored.contenido).startswith(b'RIFF'))
        url=f'/api/reportes/{report_id}/foto/'
        result=APIClient().get(url);self.assertEqual(result.status_code,200);self.assertEqual(result['Content-Type'],'image/webp')
        feed=APIClient().get('/api/reportes/publicos/').data['results'];self.assertEqual(feed[0]['foto']['url'],url);self.assertEqual(feed[0]['ciudad'],'Riohacha')
        PublicacionReporte.objects.create(reporte_id=report_id,oculta=True)
        self.assertEqual(APIClient().get(url).status_code,404)
        self.assertFalse(APIClient().get('/api/reportes/publicos/').data['results'])
    def test_report_photo_requires_explicit_public_consent_and_real_image(self):
        data=self.report_data();data['confirmar_foto_publica']='false'
        self.assertEqual(self.own.post('/api/reportes/',data,format='multipart').status_code,400)
        data=self.report_data();data['archivo']=photo(b'not an image')
        self.assertEqual(self.own.post('/api/reportes/',data,format='multipart').status_code,400)
        self.assertEqual(Reporte.objects.count(),0);self.assertEqual(FotoReporte.objects.count(),0)
    def test_anonymous_photo_is_atomic_with_the_report_and_secret(self):
        response=APIClient().post('/api/reportes/',self.report_data(),format='multipart')
        self.assertEqual(response.status_code,201,response.data);self.assertIn('codigo_gestion',response.data)
        feed=APIClient().get('/api/reportes/publicos/').data['results'];self.assertNotIn('codigo_gestion',feed[0]);self.assertNotIn('contacto_reportante',feed[0])
    def test_personal_pet_belongs_to_actor_and_never_enters_adoption(self):
        response=self.own.post('/api/mascotas/personales/',{'nombre':'Mi mascota QA','especie':'Conejo','raza':'Personal no catalogada','edad_meses':4,'sexo':'Hembra','tamano':'Pequeño','color':'Gris','descripcion':'Descripción privada','archivo':photo()},format='multipart')
        self.assertEqual(response.status_code,201,response.data);pet_id=response.data['id_mascota'];pet=Mascota.objects.get(pk=pet_id)
        self.assertEqual(pet.dueno_id,self.ciudadano.pk);self.assertEqual(pet.estado_mascota.nombre,'Con dueño')
        self.assertFalse(CustodiaMascota.objects.filter(mascota=pet).exists());self.assertTrue(PerfilMascotaPersonal.objects.get(mascota=pet).foto)
        detail=f'/api/mascotas/personales/{pet_id}/';self.assertEqual(self.own.get(detail).data['color'],'Gris');self.assertEqual(self.cliente(self.otro).get(detail).status_code,404)
        self.assertNotIn(pet_id,[r['id_mascota'] for r in APIClient().get('/api/adopcion/catalogo/').data['results']])
        self.assertTrue(self.own.get('/api/mascotas/mias/?pagina=1').data['results'][0]['personal']['foto_miniatura'])
        record=self.own.get(f'/api/seguridad/operaciones/registros/expediente/{pet_id}/');self.assertEqual(record.status_code,200);self.assertIsNotNone(record.data['foto_miniatura'])
    def test_personal_creation_rechecks_permission(self):
        Permiso.objects.filter(codigo='mascotas.participar').update(activo=False);invalidar()
        self.assertEqual(self.own.post('/api/mascotas/personales/',{'nombre':'Privada','especie':'Perro'}).status_code,403)
        self.assertEqual(PerfilMascotaPersonal.objects.count(),0)
    def test_pending_request_reserves_catalog_and_rejection_restores_it(self):
        result=self.own.post('/api/adopcion/solicitudes/',{'id_mascota':self.pet.pk,'observaciones':'Mi mensaje privado'});self.assertEqual(result.status_code,201,result.data)
        request_id=result.data['id_solicitud_adopcion'];catalog=lambda:APIClient().get('/api/adopcion/catalogo/').data['results']
        self.assertNotIn(self.pet.pk,[r['id_mascota'] for r in catalog()])
        self.assertEqual(self.cliente(self.otro).post('/api/adopcion/solicitudes/',{'id_mascota':self.pet.pk}).status_code,400)
        detail=f'/api/adopcion/solicitudes/{request_id}/';self.assertEqual(self.cliente(self.otro).get(detail).status_code,404)
        from seguridad.servicios import tomar
        miembro_con_rol(self.carlos,self.entidad,'GESTOR_ADOPCIONES')
        tomar(self.carlos,'adopcion',request_id)
        reject=self.cliente(self.carlos).post(f'/api/adopcion/solicitudes/{request_id}/resolver/',{'id_fundacion':self.foundation.pk,'aprobar':False,'observacion':'El hogar no cumple los requisitos revisados.'})
        self.assertEqual(reject.status_code,200,reject.data)
        own=self.own.get(detail);self.assertEqual(own.data['motivo_decision'],'El hogar no cumple los requisitos revisados.');self.assertEqual(len(own.data['historial']),2)
        self.assertEqual(own.data['historial'][0]['observacion'],'Mi mensaje privado');self.assertIn(self.pet.pk,[r['id_mascota'] for r in catalog()]);self.assertEqual(SolicitudAdopcion.objects.count(),1)
    def test_request_history_pagination_is_private(self):
        for i in range(23):SolicitudAdopcion.objects.create(mascota=self.pet,usuario_adoptante=self.ciudadano,estado_adopcion=valor('estado_adopcion','Rechazada'))
        first=self.own.get('/api/adopcion/solicitudes/mias/');self.assertEqual(len(first.data['results']),20);cursor=first.data['next_cursor'];self.assertIsNotNone(cursor)
        last=self.own.get('/api/adopcion/solicitudes/mias/',{'antes':cursor});self.assertEqual(len(last.data['results']),3);self.assertIsNone(last.data['next_cursor'])
        self.assertFalse(self.cliente(self.otro).get('/api/adopcion/solicitudes/mias/').data['results']);self.assertEqual(APIClient().get('/api/adopcion/solicitudes/mias/').status_code,401)
    def test_bank_recipient_is_not_generic_and_secrets_are_encrypted(self):
        from core.crypto import cifrar
        import json
        key=Fernet.generate_key().decode('ascii')
        with patch.dict('os.environ',{'LPN_DATA_KEY':key}):
            fund=FondoExterno.objects.create(entidad=self.entidad,nombre='Fondo PDF QA',entidad_administradora='Organización QA',tipo_fondo=ValorMaestro.objects.filter(tipo__nombre='tipo_fondo').first(),estado_fondo=valor('estado_fondo','Activo'))
            values={'titular':'Titular sintético QA','banco':'Banco ficticio QA','tipo_cuenta':'Ahorros','numero_cuenta':'000000001234','identificacion_titular':'QA-000000'}
            fund.datos_transferencia_cifrados=cifrar(json.dumps(values));fund.save()
            url=f'/api/fondos/{fund.pk}/datos-aporte/';result=self.own.get(url);self.assertEqual(result.status_code,200,result.data);self.assertEqual(result.data['organizacion_id'],self.entidad.pk);self.assertEqual(result.data['numero_cuenta'],values['numero_cuenta']);self.assertEqual(result['Cache-Control'],'no-store')
            self.assertNotIn(b'000000001234',bytes(fund.datos_transferencia_cifrados));self.assertEqual(APIClient().get(url).status_code,401)
            self.assertEqual(self.own.patch(url,{**values,'confirmar':True},format='json').status_code,403)
            from seguridad.models import AsignacionFondo
            miembro_con_rol(self.carlos,self.entidad,'GESTOR_FONDO')
            assignment=AsignacionFondo.objects.create(fondo=fund,usuario=self.carlos)
            manager=self.cliente(self.carlos)
            self.assertEqual(manager.patch(url,{**values,'confirmar':True},format='json').status_code,200)
            fund.refresh_from_db();self.assertNotIn(values['numero_cuenta'].encode(),bytes(fund.datos_transferencia_cifrados))
            assignment.fecha_revocacion=timezone.now();assignment.save();invalidar()
            self.assertEqual(manager.patch(url,{**values,'confirmar':True},format='json').status_code,403)
            with patch.dict('os.environ',{'LPN_DATA_KEY':Fernet.generate_key().decode('ascii')}):
                self.assertEqual(self.own.get(url).status_code,503)


    def test_request_reads_recheck_revoked_participation(self):
        request=SolicitudAdopcion.objects.create(mascota=self.pet,usuario_adoptante=self.ciudadano,estado_adopcion=valor('estado_adopcion','Pendiente'))
        self.assertEqual(self.own.get(f'/api/adopcion/solicitudes/{request.pk}/').status_code,200)
        Permiso.objects.filter(codigo='adopcion.participar').update(activo=False);invalidar()
        self.assertEqual(self.own.get('/api/adopcion/solicitudes/mias/').status_code,403)
        self.assertEqual(self.own.get(f'/api/adopcion/solicitudes/{request.pk}/').status_code,403)
        self.assertFalse(self.own.get('/api/seguridad/operaciones/mis-registros/').data['adopciones'])

    def test_approval_transfers_ownership_and_never_reopens_the_catalog(self):
        result=self.own.post('/api/adopcion/solicitudes/',{'id_mascota':self.pet.pk})
        self.assertEqual(result.status_code,201,result.data);request_id=result.data['id_solicitud_adopcion']
        from seguridad.servicios import tomar
        miembro_con_rol(self.carlos,self.entidad,'GESTOR_ADOPCIONES');tomar(self.carlos,'adopcion',request_id)
        result=self.cliente(self.carlos).post(f'/api/adopcion/solicitudes/{request_id}/resolver/',{'id_fundacion':self.foundation.pk,'aprobar':True,'observacion':'Requisitos revisados.'})
        self.assertEqual(result.status_code,200,result.data);self.pet.refresh_from_db()
        self.assertEqual(self.pet.estado_mascota.nombre,'Adoptada');self.assertEqual(self.pet.dueno_id,self.ciudadano.pk)
        self.assertFalse(CustodiaMascota.objects.filter(mascota=self.pet,fecha_fin__isnull=True).exists())
        self.assertNotIn(self.pet.pk,[row['id_mascota'] for row in APIClient().get('/api/adopcion/catalogo/').data['results']])
        self.assertEqual(SolicitudAdopcion.objects.count(),1)

    def test_personal_no_acepta_identidad_inyectada_ni_datos_fuera_de_limite(self):
        before = Mascota.objects.count()
        base = {'nombre': 'Mi mascota QA', 'especie': 'Especie libre QA'}
        for extra in [{'dueno': self.otro.pk}, {'estado_mascota': self.pet.estado_mascota_id}, {'nombre': 'x' * 121}, {'edad_meses': 601}]:
            result = self.own.post('/api/mascotas/personales/', {**base, **extra}, format='json')
            self.assertEqual(result.status_code, 400)
            self.assertEqual(Mascota.objects.count(), before)

    def test_preview_limitado_y_foto_personal_no_son_catalogo_publico(self):
        for i in range(5):
            result = self.own.post('/api/mascotas/personales/', {'nombre': f'Personal QA {i}', 'especie': 'Especie libre QA'}, format='json')
            self.assertEqual(result.status_code, 201)
        response = self.own.get('/api/mascotas/mias/?pagina=1&limite=3')
        self.assertEqual(len(response.data['results']), 3)
        self.assertIsNotNone(response.data['next_cursor'])
        self.assertTrue(all(row['especie']=='Especie libre QA' for row in response.data['results']))
        self.assertEqual(self.own.get('/api/mascotas/mias/?pagina=1&limite=10000').status_code, 400)
        self.assertEqual(APIClient().get('/api/mascotas/mias/').status_code, 401)
