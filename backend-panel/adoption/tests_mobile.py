from rest_framework.test import APIClient

from adoption.models import SolicitudAdopcion
from animals.models import CustodiaMascota, Mascota
from core.models import Ciudad, Fundacion, ValorMaestro
from django.utils import timezone
from django.db import IntegrityError, transaction
from datetime import date
from seguridad.tests import BaseRBAC, valor


class SeguimientoMovilTests(BaseRBAC):
    def test_mis_registros_muestra_solo_adopciones_del_adoptante(self):
        pet = Mascota.objects.create(
            nombre="Luna de prueba",
            descripcion_especie="Perro",
            estado_mascota=valor("estado_mascota", "En adopción"),
        )
        pending = valor("estado_adopcion", "Pendiente")
        mine = SolicitudAdopcion.objects.create(
            mascota=pet,
            estado_adopcion=pending,
            usuario_adoptante=self.ciudadano,
            observaciones="Solo se comparte según las reglas del proceso",
        )
        SolicitudAdopcion.objects.create(
            mascota=pet,
            estado_adopcion=pending,
            usuario_adoptante=self.otro,
        )

        url = "/api/seguridad/operaciones/mis-registros/"
        citizen = APIClient()
        citizen.force_authenticate(user=self.ciudadano)
        response = citizen.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["adopciones"]), 1)
        row = response.data["adopciones"][0]
        self.assertEqual(row["id_solicitud_adopcion"], mine.pk)
        self.assertEqual(row["mascota_id"], pet.pk)
        self.assertEqual(row["mascota__nombre"], pet.nombre)
        self.assertEqual(row["estado_adopcion__nombre"], "Pendiente")
        self.assertEqual(row["fecha_solicitud"], mine.fecha_solicitud)
        self.assertNotIn("observaciones", row)
        self.assertEqual(APIClient().get(url).status_code, 401)


class FichaPublicaMovilTests(BaseRBAC):
    def setUp(self):
        city, _ = Ciudad.objects.get_or_create(nombre="Riohacha", departamento="La Guajira")
        self.foundation = Fundacion.objects.create(entidad=self.entidad, ciudad=city, nit="QA-FICHA-MOVIL")
        self.pet = Mascota.objects.create(nombre="Luna ficha QA", descripcion_especie="Perro",
            estado_mascota=valor("estado_mascota", "En adopción"), fecha_nacimiento=date(2024, 6, 1), es_estimada=True)
        self.custody = CustodiaMascota.objects.create(mascota=self.pet, fundacion=self.foundation,
            usuario_registrador=self.ana, fecha_inicio=timezone.now())
        self.url = f"/api/adopcion/mascotas/{self.pet.pk}/"

    def test_ficha_anonima_muestra_datos_reales_sin_expediente_ni_identidad_personal(self):
        response = APIClient().get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["nombre"], self.pet.nombre)
        self.assertEqual(response.data["organizacion"], self.entidad.nombre)
        self.assertEqual(response.data["ciudad"], "Riohacha")
        self.assertTrue(response.data["edad_estimada"])
        self.assertGreaterEqual(response.data["edad_meses"], 0)
        self.assertEqual(set(response.data), {"id_mascota", "nombre", "especie", "raza", "edad_meses", "edad_estimada", "tamano", "sexo", "estado", "organizacion", "ciudad", "custodia_desde", "foto", "fotos", "presentacion"})

    def test_mascota_con_dueno_o_fuera_de_adopcion_no_tiene_ficha_publica(self):
        self.pet.dueno = self.ciudadano
        self.pet.save(update_fields=["dueno"])
        self.assertEqual(APIClient().get(self.url).status_code, 404)
        self.pet.dueno = None
        self.pet.estado_mascota = ValorMaestro.objects.filter(tipo__nombre="estado_mascota").exclude(nombre="En adopción").first()
        self.pet.save(update_fields=["dueno", "estado_mascota"])
        self.assertEqual(APIClient().get(self.url).status_code, 404)

    def test_organizacion_no_verificada_o_custodia_no_vigente_ocultan_ficha(self):
        self.custody.fecha_fin = timezone.now()
        self.custody.save(update_fields=["fecha_fin"])
        self.assertEqual(APIClient().get(self.url).status_code, 404)
        self.custody.fecha_fin = None
        self.custody.save(update_fields=["fecha_fin"])
        self.entidad.estado_verificacion = ValorMaestro.objects.filter(tipo__nombre="estado_verificacion").exclude(nombre="Verificada").first()
        self.entidad.save(update_fields=["estado_verificacion"])
        self.assertEqual(APIClient().get(self.url).status_code, 404)

    def test_fecha_desconocida_no_inventa_edad(self):
        self.pet.fecha_nacimiento = None
        self.pet.es_estimada = False
        self.pet.save(update_fields=["fecha_nacimiento", "es_estimada"])
        response = APIClient().get(self.url)
        self.assertIsNone(response.data["edad_meses"])
        self.assertIsNone(response.data["tamano"])
        self.assertIsNone(response.data["sexo"])

    def test_organizacion_desactivada_oculta_la_ficha(self):
        from seguridad.models import BajaAdministrativa
        BajaAdministrativa.objects.create(tipo="entidades", objeto_id=self.entidad.pk, activo=False, autor=self.admin, motivo="Baja sintética QA")
        self.assertEqual(APIClient().get(self.url).status_code, 404)

    def test_base_impide_custodias_simultaneas_y_conserva_una_ficha_consistente(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            CustodiaMascota.objects.create(mascota=self.pet, fundacion=self.foundation, usuario_registrador=self.ana, fecha_inicio=timezone.now())
        self.assertEqual(APIClient().get(self.url).status_code, 200)
        self.assertEqual(CustodiaMascota.objects.filter(mascota=self.pet, fecha_fin__isnull=True).count(), 1)


class CatalogoPaginadoMovilTests(BaseRBAC):
    url = "/api/adopcion/catalogo/"

    def setUp(self):
        city, _ = Ciudad.objects.get_or_create(nombre="Riohacha", departamento="La Guajira")
        self.foundation = Fundacion.objects.create(entidad=self.entidad, ciudad=city, nit="QA-CATALOGO-PAGINADO")
        self.available = valor("estado_mascota", "En adopción")
        self.pets = [self.crear_mascota(f"Mascota paginada QA {i}") for i in range(27)]

    def crear_mascota(self, name, **extra):
        pet = Mascota.objects.create(nombre=name, descripcion_especie="Perro", estado_mascota=self.available, **extra)
        CustodiaMascota.objects.create(mascota=pet, fundacion=self.foundation, usuario_registrador=self.ana, fecha_inicio=timezone.now())
        return pet

    def test_paginas_acotadas_sin_duplicados_ni_campos_privados(self):
        client = APIClient()
        first = client.get(self.url)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(len(first.data["results"]), 24)
        self.assertIsNone(first.data["previous"])
        self.assertEqual(first["Cache-Control"], "no-store")
        second = client.get(first.data["next"])
        self.assertEqual(second.status_code, 200)
        self.assertEqual(len(second.data["results"]), 3)
        self.assertIsNone(second.data["next"])
        ids = [row["id_mascota"] for row in first.data["results"] + second.data["results"]]
        self.assertEqual(ids, [pet.pk for pet in self.pets])
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(first.data), {"next", "previous", "results", "species"})
        self.assertEqual(set(first.data["results"][0]), {"id_mascota", "nombre", "especie", "raza", "foto", "sexo", "tamano", "estado", "edad_meses", "presentacion"})

    def test_cambio_de_disponibilidad_se_respeta_entre_paginas(self):
        client = APIClient()
        next_url = client.get(self.url).data["next"]
        withdrawn = self.pets[-1]
        withdrawn.dueno = self.ciudadano
        withdrawn.save(update_fields=["dueno"])
        result = client.get(next_url)
        self.assertEqual(result.status_code, 200)
        self.assertEqual([row["id_mascota"] for row in result.data["results"]], [pet.pk for pet in self.pets[24:26]])

    def test_no_publica_propias_sin_custodia_o_entidad_desactivada(self):
        self.crear_mascota("Ficha propia oculta", dueno=self.ciudadano)
        Mascota.objects.create(nombre="Sin custodia", descripcion_especie="Perro", estado_mascota=self.available)
        client = APIClient()
        ids = []
        url = self.url
        while url:
            result = client.get(url)
            ids.extend(row["id_mascota"] for row in result.data["results"])
            url = result.data["next"]
        self.assertEqual(ids, [pet.pk for pet in self.pets])
        from seguridad.models import BajaAdministrativa
        BajaAdministrativa.objects.create(tipo="entidades", objeto_id=self.entidad.pk, activo=False, autor=self.admin, motivo="QA paginación")
        self.assertEqual(client.get(self.url).data["results"], [])

    def test_cursor_invalido_y_limite_no_configurable_por_el_cliente(self):
        client = APIClient()
        self.assertEqual(client.get(self.url, {"cursor": "cursor-invalido"}).status_code, 404)
        self.assertEqual(len(client.get(self.url, {"page_size": 999999}).data["results"]), 24)

    def test_endpoint_anterior_conserva_su_lista(self):
        response = APIClient().get("/api/adopcion/mascotas/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 27)


    def test_filtro_se_aplica_al_catalogo_completo_y_conserva_especies_globales(self):
        cat = self.crear_mascota("Gato al final del catálogo")
        cat.descripcion_especie = "Gato"
        cat.save(update_fields=["descripcion_especie"])
        response = APIClient().get(self.url, {"especie": "Gato"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["id_mascota"] for row in response.data["results"]], [cat.pk])
        self.assertEqual(response.data["species"], ["Gato", "Perro"])
        self.assertIsNone(response.data["next"])
        self.assertEqual(APIClient().get(self.url, {"especie": "No existente"}).data["results"], [])
        self.assertEqual(APIClient().get(self.url, {"especie": "x" * 151}).status_code, 400)


    def test_preparacion_catalogo_rechaza_contexto_que_no_es_qa(self):
        from django.core.management import call_command
        from django.core.management.base import CommandError
        with self.assertRaises(CommandError):
            call_command("preparar_catalogo_qa")
