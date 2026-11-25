"""Publica ejemplos originales mediante los servicios reales y sus permisos."""
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from accounts.models import Usuario
from animals.models import Mascota, FotoPublicaMascota
from animals.public_photos import publicar as publicar_mascota
from commerce.models import Producto, FotoPublicaProducto
from commerce.public_photos import publicar as publicar_producto
from core.demo_illustrations import illustration
from core.demo_presentation import PET_NAMES, PRODUCT_NAMES
from core.management.commands.preparar_presentacion import validate_target


class Command(BaseCommand):
    help = 'Añade ilustraciones originales de ejemplo a una presentación aislada; conserva imágenes existentes.'

    def add_arguments(self, parser):
        parser.add_argument('--database-name', required=True)

    def handle(self, *args, **options):
        validate_target(connection.settings_dict['NAME'], options['database_name'], os.getenv('LPN_ALLOW_DEMO_SEED'))
        if Usuario.objects.exclude(email__endswith='@example.invalid').exists() or not Usuario.objects.filter(email='administracion@example.invalid').exists():
            raise CommandError('Solo se permite sobre la instalación ficticia creada con preparar_presentacion.')
        manager = Usuario.objects.get(email='demo01@example.invalid')
        shop_manager = Usuario.objects.get(email='demo04@example.invalid')
        count = 0
        # Cada servicio confirma permisos, disponibilidad, normalización WebP y auditoría.
        # No hay transacción externa: cada publicación confirma metadatos y su archivo juntos.
        for index, pet in enumerate(Mascota.objects.filter(nombre__in=PET_NAMES[10:]).order_by('pk')):
            if FotoPublicaMascota.objects.filter(mascota=pet).exists():
                continue
            upload = SimpleUploadedFile('ejemplo.webp', illustration('pet', index, pet.nombre), content_type='image/webp')
            publicar_mascota(manager, pet.pk, upload, confirmar=True)
            count += 1
        for index, product in enumerate(Producto.objects.filter(nombre__in=PRODUCT_NAMES).order_by('pk')):
            if FotoPublicaProducto.objects.filter(producto=product).exists():
                continue
            upload = SimpleUploadedFile('ejemplo.webp', illustration('product', index, product.nombre), content_type='image/webp')
            publicar_producto(shop_manager, product.pk, upload, confirmar=True)
            count += 1
        self.stdout.write(self.style.SUCCESS(f'{count} ilustraciones publicadas. Las imágenes previas se conservaron.'))
