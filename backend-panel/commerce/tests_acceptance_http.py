"""Local HTTP + MySQL acceptance; synthetic accounts, never a deployed database."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4

from django.core.cache import cache
from django.test import Client, LiveServerTestCase, override_settings
from core.models import Ciudad, Tienda, Rol, Recurso, Permiso, RolPermiso
from seguridad.tests import BaseRBAC, valor, miembro_con_rol
from .models import Producto, PedidoIniciado


class StoreAndRBACHTTPTests(LiveServerTestCase):
    def setUp(self):
        cache.clear()
        BaseRBAC.setUpTestData.__func__(type(self))
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        config = override_settings(LPN_PRIVATE_ROOT=temp.name)
        config.enable()
        self.addCleanup(config.disable)

    def request(self, method, path, headers=None, value=None, body=None):
        headers = dict(headers or {})
        if value is not None:
            body = json.dumps(value).encode()
            headers['Content-Type'] = 'application/json'
        req = Request(self.live_server_url + path, data=body, headers=headers, method=method)
        try:
            response = urlopen(req, timeout=15)
        except HTTPError as error:
            response = error
        with response:
            payload = response.read(1024 * 1024 + 1)
            self.assertLessEqual(len(payload), 1024 * 1024)
            kind = response.headers.get('Content-Type', '')
            data = json.loads(payload) if 'application/json' in kind else payload
            return response.status, data, response.headers

    def login(self, user):
        status, data, _ = self.request('POST', '/api/auth/token/', value={
            'email': user.email, 'password': 'Clave-Sintetica-Para-Pruebas-6549',
        })
        self.assertEqual(status, 200)
        self.assertIsInstance(data.get('access'), str)
        return {'Authorization': 'Bearer ' + data['access']}

    def test_complete_store_and_two_session_rbac_journey(self):
        self.store_journey()
        self.rbac_journey()

    def store_journey(self):
        city = Ciudad.objects.create(nombre='Ciudad tienda HTTP QA', departamento='QA')
        store = Tienda.objects.create(entidad=self.entidad, ciudad=city, direccion='Dirección sintética')
        miembro_con_rol(self.carlos, self.entidad, 'GESTOR_CATALOGO')
        product = Producto.objects.create(tienda=store, nombre='Alimento de ejemplo HTTP', precio='35000.50', existencias=2,
            categoria_producto=valor('categoria_producto', 'Alimentos'), tipo_producto=valor('tipo_producto', 'Alimento seco'), estado_producto=valor('estado_producto', 'Disponible'))
        orders_before = PedidoIniciado.objects.count()
        owner, buyer, other = self.login(self.carlos), self.login(self.ciudadano), self.login(self.otro)
        status, _, _ = self.request('POST', '/api/pedidos/', value={'id_tienda': store.pk, 'lineas': [{'id_producto': product.pk, 'cantidad': 1}]})
        self.assertEqual(status, 401)
        file = Path(__file__).with_name('fixtures') / 'catalogo-demo' / 'alimento-demo.webp'
        boundary = uuid4().hex
        body = (f'--{boundary}\r\nContent-Disposition: form-data; name="confirmar_publicacion"\r\n\r\ntrue\r\n'
                f'--{boundary}\r\nContent-Disposition: form-data; name="archivo"; filename="muestra.webp"\r\nContent-Type: image/webp\r\n\r\n').encode() + file.read_bytes() + f'\r\n--{boundary}--\r\n'.encode()
        status, data, _ = self.request('POST', f'/api/catalogo/productos/{product.pk}/foto-publica/', headers={**owner, 'Content-Type': 'multipart/form-data; boundary=' + boundary}, body=body)
        self.assertEqual(status, 201, data)
        status, catalog, _ = self.request('GET', '/api/catalogo/productos/')
        self.assertEqual(status, 200)
        row = next(row for row in catalog if row['id_producto'] == product.pk)
        self.assertIsInstance(row['foto'], dict)
        status, photo, headers = self.request('GET', row['foto']['url'])
        self.assertEqual(status, 200)
        self.assertEqual(headers['Content-Type'], 'image/webp')
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertEqual(len(photo), row['foto']['bytes'])
        request = {'id_tienda': store.pk, 'lineas': [{'id_producto': product.pk, 'cantidad': 3}]}
        self.assertEqual(self.request('POST', '/api/pedidos/', headers=buyer, value=request)[0], 400)
        self.assertEqual(PedidoIniciado.objects.count(), orders_before)
        request['lineas'][0]['cantidad'] = 2
        status, receipt, _ = self.request('POST', '/api/pedidos/', headers=buyer, value=request)
        self.assertEqual(status, 201, receipt)
        self.assertEqual(receipt['total_referencial'], '70001.00')
        self.assertEqual(receipt['lineas'][0]['precio_referencia'], '35000.50')
        self.assertFalse(receipt['cobrado'])
        product.precio = '40000.00'
        product.save(update_fields=['precio'])
        path = f"/api/pedidos/{receipt['id_pedido']}/"
        self.assertEqual(self.request('GET', path, headers=buyer)[1]['total_referencial'], '70001.00')
        self.assertEqual(self.request('GET', path, headers=other)[0], 404)
        RolPermiso.objects.filter(rol__codigo='CIUDADANO', permiso__codigo='pedido.participar').delete()
        self.assertEqual(self.request('GET', path, headers=buyer)[0], 403)
        self.assertEqual(self.request('POST', '/api/pedidos/', headers=buyer, value=request)[0], 403)
        self.assertEqual(self.request('DELETE', f'/api/catalogo/productos/{product.pk}/foto-publica/', headers=owner)[0], 204)
        self.assertEqual(self.request('GET', row['foto']['url'])[0], 404)

    def rbac_journey(self):
        admin = self.login(self.admin)
        accounts = [self.login(user) for user in [self.ciudadano, self.otro]]
        for headers in accounts:
            self.assertEqual(self.request('GET', '/api/seguridad/usuarios/', headers=headers)[0], 403)
        role = Rol.objects.get(codigo='CIUDADANO')
        original = list(RolPermiso.objects.filter(rol=role).values_list('permiso_id', flat=True))
        permission = Permiso.objects.get(codigo='usuarios.ver')
        path = f'/api/seguridad/roles/{role.pk}/permisos/'
        self.assertEqual(self.request('POST', path, headers=admin, value={'permisos': original + [permission.pk]})[0], 200)
        for headers in accounts:
            self.assertEqual(self.request('GET', '/api/seguridad/usuarios/', headers=headers)[0], 200)
        resource = Recurso.objects.get(codigo='usuarios')
        self.assertEqual(self.request('PATCH', f'/api/seguridad/recursos/{resource.pk}/', headers=admin, value={'nombre': 'Personas de QA HTTP'})[0], 200)
        web = Client()
        web.force_login(self.ciudadano)
        cookie = {'Cookie': 'sessionid=' + web.cookies['sessionid'].value}
        status, page, _ = self.request('GET', '/panel/', headers=cookie)
        self.assertEqual(status, 200)
        self.assertIn(b'Personas de QA HTTP', page)
        self.assertEqual(self.request('POST', path, headers=admin, value={'permisos': original})[0], 200)
        for headers in accounts:
            self.assertEqual(self.request('GET', '/api/seguridad/usuarios/', headers=headers)[0], 403)
        status, page, _ = self.request('GET', '/panel/', headers=cookie)
        self.assertEqual(status, 200)
        self.assertNotIn(b'Personas de QA HTTP', page)
