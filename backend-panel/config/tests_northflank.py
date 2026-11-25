from django.test import SimpleTestCase, RequestFactory, override_settings


class NorthflankProxyTests(SimpleTestCase):
    def test_public_ingress_header_and_spoofed_forwarded_headers(self):
        from seguridad.web.acceso import ip_cliente
        request = RequestFactory().get('/', REMOTE_ADDR='10.0.0.1', HTTP_X_ENVOY_EXTERNAL_ADDRESS='203.0.113.24', HTTP_X_REAL_IP='192.0.2.66', HTTP_X_FORWARDED_FOR='192.0.2.99, 192.0.2.66')
        with override_settings(LPN_TRUST_NORTHFLANK_PROXY=True, LPN_TRUST_RAILWAY_PROXY=False):
            self.assertEqual(ip_cliente(request), '203.0.113.24')
            request.META['HTTP_X_ENVOY_EXTERNAL_ADDRESS'] = 'invalid, 203.0.113.24'
            self.assertEqual(ip_cliente(request), '10.0.0.1')
            del request.META['HTTP_X_ENVOY_EXTERNAL_ADDRESS']
            self.assertEqual(ip_cliente(request), '10.0.0.1')

    def test_normal_server_ignores_northflank_header(self):
        from seguridad.web.acceso import ip_cliente
        request = RequestFactory().get('/', REMOTE_ADDR='127.0.0.1', HTTP_X_ENVOY_EXTERNAL_ADDRESS='203.0.113.24')
        with override_settings(LPN_TRUST_NORTHFLANK_PROXY=False, LPN_TRUST_RAILWAY_PROXY=False):
            self.assertEqual(ip_cliente(request), '127.0.0.1')
