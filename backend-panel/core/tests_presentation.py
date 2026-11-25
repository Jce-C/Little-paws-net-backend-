"""Protección de bases existentes y aceptación de datos relacionados de la demo."""
import os
from io import StringIO
from unittest.mock import patch
from tempfile import TemporaryDirectory
from pathlib import Path

from cryptography.fernet import Fernet
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.test import TestCase, SimpleTestCase, override_settings

from accounts.models import Usuario
from animals.models import Mascota, PresentacionPublicaMascota, FotoPublicaMascota
from commerce.models import FotoPublicaProducto
from core.management.commands.preparar_presentacion import validate_target
from core.models import Ciudad, UsuarioRol


class TargetProtectionTests(SimpleTestCase):
    def test_rejects_unconfirmed_real_or_disabled_database(self):
        for name, confirmation, enabled in (
            ('production', 'production', '1'), ('example_demo', 'other_demo', '1'),
            ('example_demo', 'example_demo', '0'),
        ):
            with self.subTest(name=name, enabled=enabled), self.assertRaises(CommandError):
                validate_target(name, confirmation, enabled)
        validate_target('example_demo', 'example_demo', '1')


class PresentationTests(TestCase):
    def test_existing_account_is_never_replaced(self):
        existing = Usuario.objects.create_user(email='conservar@example.invalid', password='original-only-for-test')
        with patch.dict(os.environ, {'LPN_ALLOW_DEMO_SEED': '1'}), patch(
            'core.management.commands.preparar_presentacion.validate_target'
        ), self.assertRaisesMessage(CommandError, 'contiene datos'):
            call_command('preparar_presentacion', database_name=connection.settings_dict['NAME'], stdout=StringIO())
        self.assertTrue(Usuario.objects.get(pk=existing.pk).check_password('original-only-for-test'))
        self.assertEqual(Usuario.objects.count(), 1)

    def test_fresh_presentation_and_reversible_http_checks(self):
        environment = {'LPN_ALLOW_DEMO_SEED': '1', 'LPN_DEMO_PASSWORD': 'only-for-isolated-tests-29!', 'LPN_DATA_KEY': Fernet.generate_key().decode()}
        # The isolated test runner owns its test schema; production guard is tested above.
        with patch.dict(os.environ, environment), patch('core.management.commands.preparar_presentacion.validate_target'):
            call_command('preparar_presentacion', database_name=connection.settings_dict['NAME'], stdout=StringIO())
            before = (Usuario.objects.count(), Mascota.objects.count())
            call_command('verify_demo', presentacion=True, stdout=StringIO())
            self.assertEqual(before, (Usuario.objects.count(), Mascota.objects.count()))
            with TemporaryDirectory() as storage, override_settings(LPN_PRIVATE_ROOT=Path(storage)), patch('core.management.commands.ilustrar_presentacion.validate_target'):
                call_command('ilustrar_presentacion', database_name=connection.settings_dict['NAME'], stdout=StringIO())
                keys = list(FotoPublicaMascota.objects.values_list('clave', flat=True))
                self.assertEqual(len(keys), 5)
                self.assertEqual(FotoPublicaProducto.objects.count(), 15)
                self.assertTrue(all(path.stat().st_size < 25000 for path in Path(storage).rglob('*.webp')))
                call_command('ilustrar_presentacion', database_name=connection.settings_dict['NAME'], stdout=StringIO())
                self.assertEqual(keys, list(FotoPublicaMascota.objects.values_list('clave', flat=True)))
                self.assertEqual(len(list(Path(storage).rglob('*.webp'))), 20)
        self.assertEqual(before, (21, 20))
        from adoption.consultas import disponibles_adopcion
        self.assertEqual(disponibles_adopcion().count(), 5)
        self.assertEqual(PresentacionPublicaMascota.objects.filter(publicada=True).count(), 5)
        self.assertTrue(Ciudad.objects.filter(nombre__iexact='Riohacha').exists())
        self.assertFalse(Usuario.objects.filter(is_superuser=True).exists())
        self.assertFalse(Usuario.objects.exclude(telefono='').exists())
        self.assertTrue(UsuarioRol.objects.filter(usuario__email='administracion@example.invalid', rol__codigo='ADMIN_SEGURIDAD', fecha_revocacion__isnull=True).exists())
