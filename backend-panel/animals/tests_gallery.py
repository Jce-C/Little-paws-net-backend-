import animals.tests_public_photos as legacy
from animals.models import FotoGaleriaMascota, FotoPublicaMascota
from animals import public_photos
from rest_framework.test import APIClient


class GalleryTests(legacy.FotosPublicasTests):
    def add_photo(self, actor=None, consent="true"):
        return self.cliente(actor or self.ana).post(f"/api/mascotas/{self.pet.pk}/galeria/", {
            "archivo": legacy.upload(), "confirmar_publicacion": consent,
        }, format="multipart")

    def test_cover_and_gallery_keep_legacy_cover_and_real_descriptors(self):
        self.assertEqual(self.publish().status_code, 201)
        cover = FotoPublicaMascota.objects.get().clave
        response = self.add_photo()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(FotoPublicaMascota.objects.get().clave, cover)
        photos = public_photos.galeria_descriptor(self.pet, self.foundation.pk)
        self.assertEqual(len(photos), 2)
        for photo in photos:
            self.assertEqual(APIClient().get(photo["url"]).status_code, 200)
        self.assertNotIn("clave", str(photos))

    def test_consent_access_and_limit_are_enforced(self):
        self.assertEqual(self.add_photo(self.ciudadano).status_code, 403)
        self.assertEqual(self.add_photo(self.otro).status_code, 403)
        self.assertEqual(self.add_photo(consent="false").status_code, 400)
        for _ in range(5):
            self.assertEqual(self.add_photo().status_code, 201)
        self.assertEqual(self.add_photo().status_code, 400)
        self.assertEqual(FotoGaleriaMascota.objects.filter(publicada=True).count(), 5)

    def test_withdrawal_and_loss_of_public_availability_hide_extra_photo(self):
        response = self.add_photo()
        self.assertEqual(response.status_code, 201)
        photo = FotoGaleriaMascota.objects.get()
        url = response.data["foto_url"]
        self.assertEqual(APIClient().get(url).status_code, 200)
        self.pet.dueno = self.ciudadano
        self.pet.save(update_fields=["dueno"])
        self.assertEqual(APIClient().get(url).status_code, 404)
        self.pet.dueno = None
        self.pet.save(update_fields=["dueno"])
        self.assertEqual(self.cliente(self.otro).delete(f"/api/mascotas/{self.pet.pk}/galeria/{photo.pk}/").status_code, 403)
        with self.captureOnCommitCallbacks(execute=True):
            self.assertEqual(self.cliente(self.ana).delete(f"/api/mascotas/{self.pet.pk}/galeria/{photo.pk}/").status_code, 204)
        self.assertEqual(APIClient().get(url).status_code, 404)
