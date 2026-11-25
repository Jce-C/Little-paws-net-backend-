from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from django.test import Client, override_settings
from django.core.cache import cache
from django.utils import timezone
from animals.models import Mascota, CustodiaMascota, FotoPublicaMascota
from animals.tests_public_photos import upload
from core.models import Ciudad, Fundacion, EntidadMiembroRol
from seguridad.tests import BaseRBAC, miembro_con_rol, valor


class FotoPanelTests(BaseRBAC):
    def setUp(self):
        cache.clear()
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        setting = override_settings(LPN_PRIVATE_ROOT=Path(temp.name))
        setting.enable()
        self.addCleanup(setting.disable)
        city, _ = Ciudad.objects.get_or_create(nombre="Riohacha", departamento="La Guajira")
        foundation = Fundacion.objects.create(entidad=self.entidad, ciudad=city, nit="QA-FOTO-PANEL")
        self.pet = Mascota.objects.create(nombre="Foto web QA", descripcion_especie="Perro", estado_mascota=valor("estado_mascota", "En adopción"))
        CustodiaMascota.objects.create(mascota=self.pet, fundacion=foundation, usuario_registrador=self.ana, fecha_inicio=timezone.now())
        miembro_con_rol(self.ana, self.entidad, "GESTOR_ADOPCIONES")
        miembro_con_rol(self.otro, self.ajena, "GESTOR_ADOPCIONES")
        self.url = f"/panel/mascotas/{self.pet.pk}/fotografia/"
        self.browser = Client()
        self.browser.force_login(self.ana)
        session = self.browser.session
        session["lpn_entidad"] = self.entidad.pk
        session.save()

    def post_photo(self, **extra):
        return self.browser.post(self.url, {"archivo": upload(), "confirmar_publicacion": "on", **extra})

    def test_formulario_nativo_no_premarca_confirmacion_y_es_una_pantalla(self):
        response = self.browser.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'enctype="multipart/form-data"')
        self.assertContains(response, 'data-photo-file')
        self.assertFalse(response.context["form_foto"]["confirmar_publicacion"].value())
        self.assertNotContains(response, 'data-modal-content')
        listing = self.browser.get('/panel/areas/mascotas/')
        self.assertContains(listing, self.url)

    def test_publicar_y_retirar_reutilizan_servicio_y_reflejan_estado(self):
        from animals import public_photos
        with patch("seguridad.web.foto_mascota.public_photos.publicar", wraps=public_photos.publicar) as publish:
            self.assertRedirects(self.post_photo(), self.url)
            self.assertEqual(publish.call_count, 1)
        page = self.browser.get(self.url)
        self.assertIsNotNone(page.context["foto_actual"])
        self.assertContains(page, 'Retirar fotografía')
        with self.captureOnCommitCallbacks(execute=True):
            self.assertRedirects(self.browser.post(self.url + '?modo=retirar', {"confirmar_retirada": "on"}), self.url)
        self.assertFalse(FotoPublicaMascota.objects.get().publicada)
        self.assertIsNone(self.browser.get(self.url).context["foto_actual"])

    def test_errores_de_archivo_o_confirmacion_conservan_foto_anterior(self):
        self.assertEqual(self.post_photo().status_code, 302)
        original = FotoPublicaMascota.objects.get().clave
        self.assertEqual(self.browser.post(self.url, {"archivo": upload()}).status_code, 400)
        self.assertEqual(self.browser.post(self.url, {"confirmar_publicacion": "on"}).status_code, 400)
        self.assertEqual(FotoPublicaMascota.objects.get().clave, original)
        self.assertEqual(self.browser.post(self.url + '?modo=retirar', {}).status_code, 400)
        self.assertTrue(FotoPublicaMascota.objects.get().publicada)

    def test_sin_sesion_sin_permiso_o_contexto_ajeno_no_accede(self):
        self.assertEqual(Client().get(self.url).status_code, 302)
        for user in [self.ciudadano, self.otro]:
            browser = Client();browser.force_login(user)
            self.assertEqual(browser.get(self.url).status_code, 403)
            self.assertEqual(browser.post(self.url, {"archivo": upload(), "confirmar_publicacion": "on"}).status_code, 403)
        self.assertFalse(FotoPublicaMascota.objects.exists())

    def test_revocacion_entre_apertura_y_envio_impide_publicar(self):
        self.assertEqual(self.browser.get(self.url).status_code, 200)
        EntidadMiembroRol.objects.filter(miembro__usuario=self.ana, rol__codigo="GESTOR_ADOPCIONES").update(fecha_revocacion=timezone.now())
        self.assertEqual(self.post_photo().status_code, 403)
        self.assertFalse(FotoPublicaMascota.objects.exists())

    def test_post_requiere_csrf(self):
        browser = Client(enforce_csrf_checks=True);browser.force_login(self.ana)
        self.assertEqual(browser.post(self.url, {"archivo": upload(), "confirmar_publicacion": "on"}).status_code, 403)
        self.assertFalse(FotoPublicaMascota.objects.exists())

    def test_retirada_sigue_disponible_si_ficha_sale_del_catalogo(self):
        self.assertEqual(self.post_photo().status_code, 302)
        self.pet.estado_mascota = valor("estado_mascota", "En recuperación")
        self.pet.save(update_fields=["estado_mascota"])
        page = self.browser.get(self.url)
        self.assertNotContains(page, 'data-photo-file')
        self.assertIsNone(page.context["foto_actual"])
        self.assertRedirects(self.browser.post(self.url + '?modo=retirar', {"confirmar_retirada": "on"}), self.url)

    def test_interfaz_inglesa_traduce_etiquetas_y_ayuda(self):
        self.browser.cookies['lpn_language'] = 'en'
        page = self.browser.get(self.url)
        self.assertContains(page, 'Public photograph')
        self.assertContains(page, 'Publish photograph')
        self.assertNotContains(page, 'Tengo autorización')

    def test_cuota_de_carga_compartida_con_api_no_bloquea_retirada(self):
        self.assertEqual(self.post_photo().status_code, 302)
        from animals.photo_views import FotoPublicaThrottle
        for _ in range(9):FotoPublicaThrottle().allow_request(self.browser.get(self.url).wsgi_request, None)
        self.assertEqual(self.post_photo().status_code, 429)
        self.assertEqual(self.browser.post(self.url + '?modo=retirar', {"confirmar_retirada": "on"}).status_code, 302)


    def test_nombre_de_recurso_personalizado_se_refleja_en_el_retorno(self):
        from core.models import Recurso
        Recurso.objects.filter(codigo="mascotas").update(nombre="Animales QA")
        self.assertContains(self.browser.get(self.url), "Volver a Animales QA")
