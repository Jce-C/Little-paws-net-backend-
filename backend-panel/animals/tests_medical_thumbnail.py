import base64
from pathlib import Path
from tempfile import TemporaryDirectory
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient
from seguridad.tests import BaseRBAC, valor, miembro_con_rol
from core.models import Ciudad, Fundacion
from .models import Mascota, CustodiaMascota
from .tests_public_photos import upload


class MedicalThumbnailTests(BaseRBAC):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        config = override_settings(LPN_PRIVATE_ROOT=Path(temp.name))
        config.enable()
        self.addCleanup(config.disable)
        city = Ciudad.objects.create(nombre='Ciudad retrato QA', departamento='QA')
        org = Fundacion.objects.create(entidad=self.entidad, ciudad=city, nit='QA-RETRATO')
        self.pet = Mascota.objects.create(nombre='Mascota propia QA', descripcion_especie='Perro', estado_mascota=valor('estado_mascota','En adopción'))
        self.custody = CustodiaMascota.objects.create(mascota=self.pet, fundacion=org, usuario_registrador=self.ana, fecha_inicio=timezone.now())
        miembro_con_rol(self.ana, self.entidad, 'GESTOR_ADOPCIONES')
        self.manage = f'/api/mascotas/{self.pet.pk}/foto-publica/'
        response = self.cliente(self.ana).post(self.manage, {'archivo':upload(), 'confirmar_publicacion':'true'}, format='multipart')
        self.assertEqual(response.status_code,201,response.data)
        self.record = f'/api/seguridad/operaciones/registros/expediente/{self.pet.pk}/'

    def adopt(self):
        self.custody.fecha_fin = timezone.now()
        self.custody.save(update_fields=['fecha_fin'])
        self.pet.dueno = self.ciudadano
        self.pet.estado_mascota = valor('estado_mascota','Con dueño')
        self.pet.save(update_fields=['dueno','estado_mascota'])
    def test_portrait_is_bounded_and_only_inside_authorized_record(self):
        self.adopt()
        self.assertEqual(APIClient().get(self.record).status_code,401)
        self.assertIn(self.cliente(self.otro).get(self.record).status_code,[403,404])
        response = self.cliente(self.ciudadano).get(self.record)
        self.assertEqual(response.status_code,200,response.data)
        self.assertEqual(response['Cache-Control'],'no-store')
        photo = response.data['foto_miniatura']
        self.assertEqual(photo['tipo'],'image/webp')
        self.assertLessEqual(max(photo['ancho'],photo['alto']),160)
        data = base64.b64decode(photo['datos'])
        self.assertLessEqual(len(data),32768)
        self.assertTrue(data.startswith(b'RIFF'))
        self.assertNotIn(b'Metadato privado',data)

    def test_withdrawal_removes_portrait_from_later_reads(self):
        self.assertEqual(self.cliente(self.ana).delete(self.manage).status_code,204)
        self.adopt()
        self.assertIsNone(self.cliente(self.ciudadano).get(self.record).data['foto_miniatura'])

    def test_custody_change_does_not_reuse_former_organization_portrait(self):
        self.custody.fecha_fin = timezone.now()
        self.custody.save(update_fields=['fecha_fin'])
        other = Fundacion.objects.create(entidad=self.ajena, ciudad=self.custody.fundacion.ciudad, nit='QA-OTRO-RETRATO')
        CustodiaMascota.objects.create(mascota=self.pet, fundacion=other, usuario_registrador=self.admin, fecha_inicio=timezone.now())
        from .medical_thumbnail import miniatura
        self.assertIsNone(miniatura(self.pet))
        self.assertIn(self.cliente(self.ciudadano).get(self.record).status_code,[403,404])

    def test_closed_custody_keeps_the_portrait_private_for_the_adopter(self):
        self.adopt()
        self.assertIsNotNone(self.cliente(self.ciudadano).get(self.record).data['foto_miniatura'])
        self.assertIn(self.cliente(self.otro).get(self.record).status_code,[403,404])
