from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from PIL import Image
from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework.test import APIClient
from seguridad.tests import BaseRBAC, miembro_con_rol, valor
from core.models import Ciudad, Fundacion, EntidadMiembroRol, ValorMaestro
from animals.models import Mascota, CustodiaMascota, FotoPublicaMascota
from animals import public_photos


def upload(color="green"):
    data = BytesIO()
    exif = Image.Exif()
    exif[270] = "Metadato privado de prueba"
    exif[274] = 6
    Image.new("RGB", (1800, 900), color).save(data, format="JPEG", exif=exif)
    return SimpleUploadedFile("foto-original.jpg", data.getvalue(), content_type="image/jpeg")


class FotosPublicasTests(BaseRBAC):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.override = override_settings(LPN_PRIVATE_ROOT=Path(self.temp.name))
        self.override.enable()
        self.addCleanup(self.override.disable)
        city, _ = Ciudad.objects.get_or_create(nombre="Riohacha", departamento="La Guajira")
        self.foundation = Fundacion.objects.create(entidad=self.entidad, ciudad=city, nit="QA-FOTO-PUBLICA")
        self.pet = Mascota.objects.create(nombre="Ficha sintética de foto", descripcion_especie="Perro", estado_mascota=valor("estado_mascota", "En adopción"))
        self.custody = CustodiaMascota.objects.create(mascota=self.pet, fundacion=self.foundation, usuario_registrador=self.ana, fecha_inicio=timezone.now())
        miembro_con_rol(self.ana, self.entidad, "GESTOR_ADOPCIONES")
        miembro_con_rol(self.otro, self.ajena, "GESTOR_ADOPCIONES")
        self.manage = f"/api/mascotas/{self.pet.pk}/foto-publica/"
        self.public = f"/api/adopcion/mascotas/{self.pet.pk}/foto/"

    def publish(self, actor=None, **extra):
        return self.cliente(actor or self.ana).post(self.manage, {"archivo": upload(), "confirmar_publicacion": "true", **extra}, format="multipart")

    def test_publicacion_autorizada_normaliza_webp_y_elimina_metadatos(self):
        response = self.publish()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(set(response.data), {"foto_url", "ancho", "alto", "bytes"})
        self.assertEqual((response.data["ancho"], response.data["alto"]), (640, 1280))
        self.assertLessEqual(response.data["bytes"], 512 * 1024)
        public = APIClient().get(self.public)
        self.assertEqual(public.status_code, 200)
        self.assertEqual(public["Content-Type"], "image/webp")
        self.assertEqual(public["Cache-Control"], "no-store")
        self.assertEqual(public["X-Content-Type-Options"], "nosniff")
        data = public.content
        with Image.open(BytesIO(data)) as image:
            self.assertEqual(image.format, "WEBP")
            self.assertEqual(dict(image.getexif()), {})
            self.assertNotIn("xmp", image.info)
            self.assertNotIn("icc_profile", image.info)
        self.assertNotIn(b"Metadato privado", data)

    def test_confirmacion_explicita_es_obligatoria(self):
        self.assertEqual(self.publish(confirmar_publicacion="false").status_code, 400)
        self.assertFalse(FotoPublicaMascota.objects.exists())
        self.assertFalse(public_photos.raiz().exists())

    def test_anomina_ciudadano_y_otro_contexto_no_publican(self):
        self.assertEqual(APIClient().post(self.manage, {}, format="multipart").status_code, 401)
        self.assertEqual(self.publish(actor=self.ciudadano).status_code, 403)
        self.assertEqual(self.publish(actor=self.otro).status_code, 403)
        self.assertFalse(FotoPublicaMascota.objects.exists())

    def test_revocacion_del_rol_se_aplica_en_la_siguiente_operacion(self):
        self.assertEqual(self.publish().status_code, 201)
        EntidadMiembroRol.objects.filter(miembro__usuario=self.ana, rol__codigo="GESTOR_ADOPCIONES").update(fecha_revocacion=timezone.now())
        self.assertEqual(self.publish().status_code, 403)
        self.assertEqual(self.cliente(self.ana).delete(self.manage).status_code, 403)

    def test_rechaza_contenido_falso_animado_y_limites_de_entrada(self):
        invalid = [b"<svg xmlns='http://www.w3.org/2000/svg'></svg>", b"%PDF-1.7 falso", b"\x89PNG\r\n\x1a\ntruncado", b"x" * (public_photos.MAX_INPUT + 1)]
        too_wide = BytesIO()
        Image.new("RGB", (6001, 1)).save(too_wide, format="PNG")
        invalid.append(too_wide.getvalue())
        animated = BytesIO()
        Image.new("RGB", (8, 8), "red").save(animated, format="WEBP", save_all=True, append_images=[Image.new("RGB", (8, 8), "blue")], duration=100, loop=0)
        invalid.append(animated.getvalue())
        for content in invalid:
            with self.subTest(length=len(content)):
                response = self.publish(archivo=SimpleUploadedFile("falsa.jpg", content, content_type="image/jpeg"))
                self.assertEqual(response.status_code, 400)
        self.assertFalse(FotoPublicaMascota.objects.exists())

    def test_retirada_de_publicacion_oculta_y_borra_el_archivo(self):
        self.assertEqual(self.publish().status_code, 201)
        path = public_photos.ruta(FotoPublicaMascota.objects.get().clave)
        with self.captureOnCommitCallbacks(execute=True):
            self.assertEqual(self.cliente(self.ana).delete(self.manage).status_code, 204)
        self.assertFalse(path.exists())
        self.assertEqual(APIClient().get(self.public).status_code, 404)

    def test_perdida_de_disponibilidad_verificacion_o_baja_oculta_la_foto(self):
        self.assertEqual(self.publish().status_code, 201)
        self.pet.dueno = self.ciudadano
        self.pet.save(update_fields=["dueno"])
        self.assertEqual(APIClient().get(self.public).status_code, 404)
        self.pet.dueno = None
        self.pet.save(update_fields=["dueno"])
        verified = self.entidad.estado_verificacion
        self.entidad.estado_verificacion = ValorMaestro.objects.filter(tipo__nombre="estado_verificacion").exclude(nombre="Verificada").first()
        self.entidad.save(update_fields=["estado_verificacion"])
        self.assertEqual(APIClient().get(self.public).status_code, 404)
        self.entidad.estado_verificacion = verified
        self.entidad.save(update_fields=["estado_verificacion"])
        from seguridad.models import BajaAdministrativa
        BajaAdministrativa.objects.create(tipo="entidades", objeto_id=self.entidad.pk, activo=False, autor=self.admin, motivo="Prueba foto")
        self.assertEqual(APIClient().get(self.public).status_code, 404)

    def test_cambio_de_custodia_no_hereda_la_autorizacion_de_la_foto(self):
        self.assertEqual(self.publish().status_code, 201)
        self.custody.fecha_fin = timezone.now()
        self.custody.save(update_fields=["fecha_fin"])
        other = Fundacion.objects.create(entidad=self.ajena, ciudad=self.foundation.ciudad, nit="QA-FOTO-OTRA")
        CustodiaMascota.objects.create(mascota=self.pet, fundacion=other, usuario_registrador=self.otro, fecha_inicio=timezone.now())
        self.assertEqual(APIClient().get(self.public).status_code, 404)
        self.assertEqual(self.publish(actor=self.ana).status_code, 403)
        self.assertIsNone(APIClient().get(f"/api/adopcion/mascotas/{self.pet.pk}/").data["foto"])
        self.assertIsNone(APIClient().get("/api/adopcion/catalogo/").data["results"][0]["foto"])

    def test_fallo_de_auditoria_revierte_metadatos_y_archivo_nuevo(self):
        with patch("animals.public_photos.auditar", side_effect=RuntimeError("Fallo sintético de auditoría")):
            with self.assertRaises(RuntimeError):
                self.publish()
        self.assertFalse(FotoPublicaMascota.objects.exists())
        self.assertEqual(list(public_photos.raiz().glob("*")), [])

    def test_reemplazo_retira_archivo_anterior_y_no_acepta_ids_de_documentos(self):
        self.assertEqual(self.publish().status_code, 201)
        old = public_photos.ruta(FotoPublicaMascota.objects.get().clave)
        with self.captureOnCommitCallbacks(execute=True):
            self.assertEqual(self.publish(archivo=upload("blue")).status_code, 201)
        self.assertFalse(old.exists())
        self.assertEqual(FotoPublicaMascota.objects.count(), 1)
        self.assertEqual(self.publish(archivo_id=1).status_code, 400)


    def test_revalida_permiso_si_se_revoca_durante_la_normalizacion(self):
        normalize = public_photos.normalizar
        def revoke(file):
            result = normalize(file)
            EntidadMiembroRol.objects.filter(miembro__usuario=self.ana, rol__codigo="GESTOR_ADOPCIONES").update(fecha_revocacion=timezone.now())
            return result
        with patch("animals.public_photos.normalizar", side_effect=revoke):
            self.assertEqual(self.publish().status_code, 403)
        self.assertFalse(FotoPublicaMascota.objects.exists())
        self.assertFalse(public_photos.raiz().exists())

    def test_limita_cargas_sin_impedir_la_retirada(self):
        self.assertEqual(self.publish().status_code, 201)
        for _ in range(9):
            self.assertEqual(self.publish(confirmar_publicacion="false").status_code, 400)
        self.assertEqual(self.publish().status_code, 429)
        self.assertEqual(self.cliente(self.ana).delete(self.manage).status_code, 204)
        response = APIClient().get(self.public)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response["Cache-Control"], "no-store")


    def test_error_de_almacenamiento_devuelve_503_sin_rutas_ni_archivos_huerfanos(self):
        with patch("pathlib.Path.open", side_effect=PermissionError("Ruta interna que no debe publicarse")):
            response = self.publish()
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("Ruta interna", str(response.data))
        self.assertFalse(FotoPublicaMascota.objects.exists())
        self.assertEqual(self.publish().status_code, 201)
        with patch("pathlib.Path.open", side_effect=PermissionError("Ruta interna que no debe publicarse")):
            response = APIClient().get(self.public)
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("Ruta interna", str(response.data))
        self.assertEqual(response["Cache-Control"], "no-store")


    def test_descriptores_solo_para_publicaciones_vigentes_y_cambian_al_reemplazar(self):
        client = APIClient()
        catalog_url = "/api/adopcion/catalogo/"
        detail_url = f"/api/adopcion/mascotas/{self.pet.pk}/"
        self.assertIsNone(client.get(detail_url).data["foto"])
        self.assertIsNone(client.get(catalog_url).data["results"][0]["foto"])
        self.assertEqual(self.publish().status_code, 201)
        first = client.get(detail_url).data["foto"]
        self.assertEqual(set(first), {"url", "ancho", "alto", "bytes"})
        self.assertTrue(first["url"].startswith(self.public + "?v="))
        self.assertEqual(client.get(catalog_url).data["results"][0]["foto"], first)
        self.assertEqual(self.publish(archivo=upload("blue")).status_code, 201)
        self.assertNotEqual(client.get(detail_url).data["foto"]["url"], first["url"])
        self.assertEqual(self.cliente(self.ana).delete(self.manage).status_code, 204)
        self.assertIsNone(client.get(detail_url).data["foto"])
        self.assertIsNone(client.get(catalog_url).data["results"][0]["foto"])

    def test_listado_no_consulta_una_foto_por_cada_mascota(self):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext
        for index in range(10):
            pet = Mascota.objects.create(nombre=f"Sin foto {index}", descripcion_especie="Perro", estado_mascota=self.pet.estado_mascota)
            CustodiaMascota.objects.create(mascota=pet, fundacion=self.foundation, usuario_registrador=self.ana, fecha_inicio=timezone.now())
        with CaptureQueriesContext(connection) as queries:
            response = APIClient().get("/api/adopcion/catalogo/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 11)
        self.assertLessEqual(len(queries), 3)
        self.assertTrue(all(row["foto"] is None for row in response.data["results"]))


    def test_ensayo_de_foto_rechaza_una_base_que_no_es_qa(self):
        from django.core.management import call_command
        from django.core.management.base import CommandError
        with self.assertRaises(CommandError):
            call_command("preparar_foto_publica_qa")
