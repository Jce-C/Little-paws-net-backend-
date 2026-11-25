from unittest.mock import patch
from cryptography.fernet import Fernet
from rest_framework.test import APIClient
from seguridad.tests import BaseRBAC, valor
from seguridad.autorizacion import invalidar
from core.models import Ciudad,Fundacion,ValorMaestro,Permiso
from core.crypto import cifrar
from rescue.models import Reporte,CasoRescate,CuentaFundacion

class CierreCiudadano72(BaseRBAC):
    def setUp(self):
        city,_=Ciudad.objects.get_or_create(nombre='Riohacha',departamento='La Guajira')
        self.foundation=Fundacion.objects.create(entidad=self.entidad,ciudad=city,nit='AUDITORIA71')
        self.report=Reporte.objects.create(usuario_reportante=self.ciudadano,tipo_reporte=ValorMaestro.objects.filter(tipo__nombre='tipo_reporte').first(),estado_reporte=valor('estado_reporte','Pendiente'),descripcion='Caso sintético de auditoría',ciudad=city)
        CasoRescate.objects.create(reporte=self.report,fundacion=self.foundation,estado_caso=ValorMaestro.objects.filter(tipo__nombre='estado_caso').first(),usuario_ultimo_cambio=self.ana)
        self.client=self.cliente(self.ciudadano)

    def test_sponsorship_reveals_only_the_recipient_and_only_to_the_sponsor(self):
        with patch.dict('os.environ',{'LPN_DATA_KEY':Fernet.generate_key().decode('ascii')}):
            CuentaFundacion.objects.create(fundacion=self.foundation,numero_cuenta_cifrado=cifrar('0000000071'),numero_cuenta_ultimos4='0071',banco='Banco sintético QA',tipo_cuenta='Ahorros QA',titular='Titular sintético QA')
            created=self.client.post('/api/apadrinamientos/',{'id_reporte':self.report.pk,'monto_comprometido':'10000'},format='json')
            self.assertEqual(created.status_code,201,created.data)
            url=f"/api/apadrinamientos/{created.data['id_apadrinamiento']}/cuenta/"
            result=self.client.get(url)
            self.assertEqual(result.status_code,200,result.data)
            self.assertEqual(result.data['organizacion_id'],self.entidad.pk)
            self.assertEqual(result.data['numero_cuenta'],'0000000071')
            self.assertEqual(result['Cache-Control'],'no-store')
            self.assertNotEqual(self.cliente(self.otro).get(url).status_code,200)
            with patch.dict('os.environ',{'LPN_DATA_KEY':Fernet.generate_key().decode('ascii')}):
                self.assertEqual(self.client.get(url).status_code,503)

    def test_my_reports_prevent_private_browser_caching(self):
        result=self.client.get('/api/reportes/mios/')
        self.assertEqual(result.status_code,200)
        self.assertIn('no-store',result.get('Cache-Control',''))

    def test_my_reports_recheck_revoked_participation_like_pets_and_requests(self):
        Permiso.objects.filter(codigo='reportes.participar').update(activo=False);invalidar()
        self.assertEqual(self.client.get('/api/reportes/mios/').status_code,403)

    def test_personal_retry_replays_receipt_and_does_not_create_another_pet(self):
        import uuid
        from animals.models import Mascota
        from core.models import OperacionCiudadana
        key=str(uuid.uuid4());body={'nombre':'Reintento QA','especie':'Gato','edad_meses':8}
        first=self.client.post('/api/mascotas/personales/',body,format='json',HTTP_IDEMPOTENCY_KEY=key)
        second=self.client.post('/api/mascotas/personales/',body,format='json',HTTP_IDEMPOTENCY_KEY=key)
        self.assertEqual(first.status_code,201,first.data);self.assertEqual(second.data,first.data)
        self.assertEqual(second['Idempotency-Replayed'],'true')
        self.assertEqual(Mascota.objects.filter(nombre='Reintento QA').count(),1)
        self.assertEqual(OperacionCiudadana.objects.count(),1)
        different=self.client.post('/api/mascotas/personales/',{**body,'nombre':'Otro dato'},format='json',HTTP_IDEMPOTENCY_KEY=key)
        self.assertEqual(different.status_code,409)
        other=self.cliente(self.otro).post('/api/mascotas/personales/',body,format='json',HTTP_IDEMPOTENCY_KEY=key)
        self.assertEqual(other.status_code,201);self.assertNotEqual(other.data['id_mascota'],first.data['id_mascota'])
        Permiso.objects.filter(codigo='mascotas.participar').update(activo=False);invalidar()
        self.assertEqual(self.client.post('/api/mascotas/personales/',body,format='json',HTTP_IDEMPOTENCY_KEY=key).status_code,403)

    def test_photo_retry_has_the_same_durable_receipt(self):
        import uuid
        from animals.tests_pdf_corrections import photo
        from animals.models import Mascota
        key=str(uuid.uuid4())
        def send():return self.client.post('/api/mascotas/personales/',{'nombre':'Con foto QA','especie':'Conejo','archivo':photo()},format='multipart',HTTP_IDEMPOTENCY_KEY=key)
        first=send();second=send();self.assertEqual(first.status_code,201,first.data);self.assertEqual(second.data,first.data)
        self.assertEqual(Mascota.objects.filter(nombre='Con foto QA').count(),1)

    def test_invalid_input_does_not_consume_the_key_and_legacy_clients_still_work(self):
        import uuid
        from core.models import OperacionCiudadana
        key=str(uuid.uuid4());url='/api/mascotas/personales/'
        self.assertEqual(self.client.post(url,{'nombre':'','especie':'Gato'},format='json',HTTP_IDEMPOTENCY_KEY=key).status_code,400)
        self.assertFalse(OperacionCiudadana.objects.exists())
        self.assertEqual(self.client.post(url,{'nombre':'Dato válido QA','especie':'Gato'},format='json',HTTP_IDEMPOTENCY_KEY=key).status_code,201)
        self.assertEqual(self.client.post(url,{'nombre':'Cliente antiguo QA','especie':'Gato'},format='json').status_code,201)
        self.assertEqual(self.client.post(url,{'nombre':'Clave inválida QA','especie':'Gato'},format='json',HTTP_IDEMPOTENCY_KEY='bad-key').status_code,400)

    def test_sponsorship_retry_does_not_repeat_commitment_or_history(self):
        import uuid
        from rescue.models import Apadrinamiento,HistorialEstadoApadrinamiento
        key=str(uuid.uuid4());body={'id_reporte':self.report.pk,'monto_comprometido':'10000'};url='/api/apadrinamientos/'
        first=self.client.post(url,body,format='json',HTTP_IDEMPOTENCY_KEY=key)
        second=self.client.post(url,body,format='json',HTTP_IDEMPOTENCY_KEY=key)
        self.assertEqual(first.status_code,201,first.data);self.assertEqual(second.data,first.data)
        self.assertEqual(Apadrinamiento.objects.count(),1);self.assertEqual(HistorialEstadoApadrinamiento.objects.count(),1)
        self.assertEqual(self.client.post(url,{**body,'monto_comprometido':'20000'},format='json',HTTP_IDEMPOTENCY_KEY=key).status_code,409)
        Permiso.objects.filter(codigo='aporte.participar').update(activo=False);invalidar()
        self.assertEqual(self.client.post(url,body,format='json',HTTP_IDEMPOTENCY_KEY=key).status_code,403)

    def test_commitment_history_is_private_paginated_and_revocable(self):
        from rescue.models import Apadrinamiento
        for i in range(23):Apadrinamiento.objects.create(reporte=self.report,usuario_padrino=self.ciudadano,estado_apadrinamiento=valor('estado_apadrinamiento','En espera'),monto_comprometido='10000')
        url='/api/apadrinamientos/mios/'
        response=self.client.get(url);self.assertEqual(response.status_code,200);self.assertEqual(len(response.data['results']),20)
        self.assertEqual(response['Cache-Control'],'no-store')
        self.assertEqual(len(self.client.get(url,{'antes':response.data['next_cursor']}).data['results']),3)
        self.assertFalse(self.cliente(self.otro).get(url).data['results']);self.assertEqual(APIClient().get(url).status_code,401)
        Permiso.objects.filter(codigo='aporte.participar').update(activo=False);invalidar();self.assertEqual(self.client.get(url).status_code,403)
