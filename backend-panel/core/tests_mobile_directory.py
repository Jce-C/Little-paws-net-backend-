from rest_framework.test import APIClient
from core.models import Ciudad, Clinica, Fundacion
from seguridad.models import BajaAdministrativa
from seguridad.tests import BaseRBAC, valor


class PublicDirectoryTests(BaseRBAC):
    def setUp(self):
        city = Ciudad.objects.create(nombre="Ciudad sintética QA", departamento="QA")
        self.foundation = Fundacion.objects.create(entidad=self.entidad, ciudad=city, nit="QA-SYNTHETIC", descripcion="Descripción pública QA")
        self.clinic = Clinica.objects.create(entidad=self.ajena, ciudad=city, direccion="Dirección comercial QA")

    def test_public_whitelist_does_not_expose_members_or_identifiers(self):
        response = APIClient().get("/api/red/organizaciones/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual({row["tipo"] for row in response.data}, {"Fundación", "Veterinaria"})
        for row in response.data:
            self.assertEqual(set(row), {"id", "nombre", "tipo", "ciudad", "descripcion", "direccion", "acepta_voluntarios", "necesidades_ayuda", "perfil_publico", "programa_ayuda", "logo"})
        self.assertEqual(response["Cache-Control"], "no-store")

    def test_unverified_and_deactivated_entities_are_not_listed(self):
        self.entidad.estado_verificacion = valor("estado_verificacion", "Pendiente")
        self.entidad.save()
        BajaAdministrativa.objects.create(tipo="entidades", objeto_id=self.ajena.pk, activo=False, autor=self.admin, motivo="QA")
        self.assertEqual(APIClient().get("/api/red/organizaciones/").data, [])

    def test_directory_is_read_only(self):
        response = self.cliente(self.ciudadano).post("/api/red/organizaciones/", {"nombre": "No guardar"}, format="json")
        self.assertEqual(response.status_code, 405)

    def test_product_catalog_preserves_real_fields_and_hides_administrative_removal(self):
        from decimal import Decimal
        from core.models import EntidadVerificable, Tienda, TipoMaestro, ValorMaestro
        from commerce.models import Producto
        entity = EntidadVerificable.objects.create(nombre='Tienda QA', estado_verificacion=self.entidad.estado_verificacion)
        store = Tienda.objects.create(entidad=entity, ciudad=self.foundation.ciudad, direccion='Dirección QA')
        values = []
        for kind, name in [('categoria_producto','Categoría QA'), ('tipo_producto','Tipo QA'), ('estado_producto','Disponible')]:
            kind, _ = TipoMaestro.objects.get_or_create(nombre=kind)
            value, _ = ValorMaestro.objects.get_or_create(tipo=kind, nombre=name)
            values.append(value)
        product = Producto.objects.create(tienda=store, categoria_producto=values[0], tipo_producto=values[1], estado_producto=values[2], nombre='Producto QA', descripcion='Descripción real QA', precio=Decimal('2000.50'), existencias=3)
        client = APIClient()
        row = client.get('/api/catalogo/productos/').data[0]
        self.assertEqual(row['descripcion'], product.descripcion)
        self.assertEqual(row['precio'], '2000.50')
        self.assertEqual(row['categoria'], 'Categoría QA')
        BajaAdministrativa.objects.create(tipo='productos', objeto_id=product.pk, activo=False, autor=self.admin, motivo='QA')
        self.assertEqual(client.get('/api/catalogo/productos/').data, [])
