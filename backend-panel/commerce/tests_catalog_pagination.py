from rest_framework.test import APIClient
from seguridad.tests import BaseRBAC, valor
from core.models import Ciudad,Tienda
from .models import Producto


class ProductPaginationTests(BaseRBAC):
    def setUp(self):
        city=Ciudad.objects.create(nombre='Ciudad paginación QA',departamento='QA')
        self.store=Tienda.objects.create(entidad=self.entidad,ciudad=city,direccion='Dirección QA')
        self.category=valor('categoria_producto','Alimentos')
        self.type=valor('tipo_producto','Alimento seco')
        self.available=valor('estado_producto','Disponible')
        Producto.objects.bulk_create([Producto(tienda=self.store,nombre=f'Producto QA {i:03}',precio='1000',existencias=3,categoria_producto=self.category,tipo_producto=self.type,estado_producto=self.available) for i in range(107)])
        self.client=APIClient()
        self.url='/api/catalogo/productos/'

    def test_can_read_beyond_one_hundred_without_duplicates_and_legacy_stays_compatible(self):
        self.assertEqual(len(self.client.get(self.url).data),100)
        ids=[];cursor='0'
        while cursor is not None:
            response=self.client.get(self.url,{'paginado':'1','limite':'20','despues':cursor})
            self.assertEqual(response.status_code,200)
            self.assertLessEqual(len(response.data['results']),20)
            ids.extend(r['id_producto'] for r in response.data['results'])
            cursor=response.data['next_cursor']
        self.assertEqual(len(ids),107)
        self.assertEqual(ids,sorted(set(ids)))

    def test_search_covers_late_records_and_metadata_contains_categories(self):
        response=self.client.get(self.url,{'paginado':'1','buscar':'106','categoria':'Alimentos'})
        self.assertEqual([r['nombre'] for r in response.data['results']],['Producto QA 106'])
        self.assertIn('Alimentos',response.data['categorias'])
        self.assertIsNone(response.data['next_cursor'])
        self.assertEqual(self.client.get(self.url,{'paginado':'1','categoria':'No existe'}).data['results'],[])

    def test_invalid_parameters_are_rejected_not_clamped_or_interpreted_as_urls(self):
        for params in [{'paginado':'0'},{'paginado':'1','limite':'51'},{'paginado':'1','limite':'0'},{'paginado':'1','limite':'9'*5000},{'paginado':'1','despues':'https://example.invalid/'},{'paginado':'1','despues':'-1'},{'paginado':'1','despues':'9'*30},{'paginado':'1','buscar':'x'*101}]:
            with self.subTest(params=str(params)[:80]):self.assertEqual(self.client.get(self.url,params).status_code,400)

    def test_page_queries_are_bounded_and_unavailable_items_do_not_leak(self):
        with self.assertNumQueries(2):response=self.client.get(self.url,{'paginado':'1','limite':'20'})
        with self.assertNumQueries(1):self.client.get(self.url,{'paginado':'1','despues':response.data['next_cursor']})
        product=Producto.objects.first();product.estado_producto=valor('estado_producto','Inactivo');product.save()
        response=self.client.get(self.url,{'paginado':'1','limite':'50'})
        self.assertNotIn(product.pk,[r['id_producto'] for r in response.data['results']])
