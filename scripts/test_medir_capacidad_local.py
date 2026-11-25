import copy
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch
import medir_capacidad_local as capacity
from estimar_trafico_local import estimate


class CapacityGuardsTests(unittest.TestCase):
    def setUp(self):
        self.credentials={'nonce':'synthetic-capacity-instance-123456','schema':'lpn_capacity91_test','actors':[{'token':'private-token-123'} for _ in range(8)],'store':1,'product':1,'email':'qa@example.invalid','password':'test-password-private-987'}
        self.marker={'nonce':self.credentials['nonce'],'schema':self.credentials['schema'],'debug':False,'fixture_only':True,'dataset':{},'configuration':{},'working_set_bytes':100,'private_bytes':200}

    def test_mismatched_instance_debug_and_identifiers_are_rejected(self):
        capacity.validate_fixture(self.credentials,self.marker)
        for key,value in [('nonce','other'),('schema','production'),('debug',True),('fixture_only',False)]:
            wrong={**self.marker,key:value}
            with self.assertRaises(ValueError):capacity.validate_fixture(self.credentials,wrong)
        for field,value in [('product',True),('store',0),('actors',[])]:
            wrong={**self.credentials,field:value}
            with self.assertRaises(ValueError):capacity.validate_fixture(wrong,self.marker)

    def test_route_method_redirect_and_body_size_guards(self):
        seen=[]
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*_):pass
            def do_GET(self):
                seen.append(self.path)
                if self.path=='/api/catalogo/productos/':
                    body=b'x'*(capacity.MAX_BODY+1);self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
                else:
                    self.send_response(302);self.send_header('Location','https://example.invalid/');self.end_headers()
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            with patch.object(capacity,'BASE',f'http://127.0.0.1:{server.server_port}'):
                for method,path in [('GET','/api/seguridad/'),('GET','https://example.invalid/'),('DELETE','/api/pedidos/'),('POST','/api/mascotas/mias/?pagina=1&limite=3')]:
                    with self.assertRaises(ValueError):capacity.request(method,path)
                self.assertEqual(seen,[])
                with self.assertRaisesRegex(ValueError,'redirecciones'):capacity.request('GET','/__qa_capacity__/')
                with self.assertRaisesRegex(ValueError,'1 MiB'):capacity.request('GET','/api/catalogo/productos/')
                self.assertEqual(len(seen),2)
        finally:
            server.shutdown();server.server_close();thread.join(timeout=2)

    def test_fixed_workload_is_bounded_and_report_contains_no_credentials(self):
        calls=[]
        def fake(method,path,body=None,token=None):
            calls.append((method,path))
            row={'method':method,'path':path,'status':201 if method=='POST' and path in capacity.WRITES else 200,'bytes':10,'ms':1}
            return row,copy.deepcopy(self.marker) if path=='/__qa_capacity__/' else {'access':'synthetic','cobrado':False}
        with patch.object(capacity,'request',side_effect=fake):report=capacity.run(self.credentials)
        self.assertEqual([s['sample']['requests'] for s in report['stages']],[24,96,192])
        self.assertEqual(len(calls),322)
        self.assertEqual(sum(method=='POST' and path in capacity.WRITES for method,path in calls),104)
        self.assertEqual(report['unexpected_status_count'],0)
        for secret in [self.credentials['nonce'],self.credentials['password'],self.credentials['email'],self.credentials['actors'][0]['token']]:self.assertNotIn(secret,str(report))

    def test_unverified_server_is_never_given_credentials_or_business_writes(self):
        with patch.object(capacity,'request',return_value=({'status':200},{**self.marker,'nonce':'wrong'})) as send:
            with self.assertRaises(ValueError):capacity.run(self.credentials)
        self.assertEqual(send.call_count,1)

    def test_permission_errors_are_reported_as_failed_load_instead_of_successful_latency(self):
        def fake(method,path,body=None,token=None):
            status=403 if method=='POST' and path=='/api/comunidad/publicaciones/' else 201 if method=='POST' and path=='/api/pedidos/' else 200
            row={'method':method,'path':path,'status':status,'bytes':10,'ms':1}
            return row,copy.deepcopy(self.marker) if path=='/__qa_capacity__/' else {'access':'synthetic','cobrado':False}
        with patch.object(capacity,'request',side_effect=fake):report=capacity.run(self.credentials)
        self.assertEqual(report['unexpected_status_count'],52)

    def test_traffic_estimate_separates_measured_api_from_media_assumptions(self):
        report={'stages':[{'journeys':2,'sample':{'bytes_total':2000,'requests':12}}]}
        result=estimate(report,users=100,journeys_per_day=1,cold_web_mb=5,media_mb=.2)
        self.assertEqual(result['api_requests_per_month'],18000)
        self.assertEqual(result['api_response_gb'],.003)
        self.assertEqual(result['cold_web_gb_assumption'],.5)
        self.assertEqual(result['media_gb_assumption'],.6)
        self.assertEqual(result['total_response_gb_estimate'],1.103)
        self.assertIsNone(result['currency_cost'])
        with self.assertRaises(ValueError):estimate(report,users=0,journeys_per_day=1,cold_web_mb=0,media_mb=0)


if __name__=='__main__':unittest.main()
