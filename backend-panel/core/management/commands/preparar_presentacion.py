"""Instala una demostración nueva; nunca borra ni reutiliza registros anteriores."""
import os
from io import StringIO

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from accounts.models import Usuario
from animals.models import Mascota, PresentacionPublicaMascota
from commerce.models import Producto
from core.demo_presentation import PEOPLE_NAMES, presentation_name, separate_pending_applications
from core.models import EntidadVerificable, Fundacion, PerfilPublicoEntidad, Rol, UsuarioRol
from rescue.models import Reporte
from seguridad.servicios import auditar


def validate_target(name, confirmation, enabled):
    if enabled != '1' or not name.endswith('_demo') or name != confirmation:
        raise CommandError('Requiere LPN_ALLOW_DEMO_SEED=1 y --database-name igual a una base terminada en _demo.')


class Command(BaseCommand):
    help = 'Prepara datos ficticios de presentación únicamente en una base demo vacía; no elimina datos.'

    def add_arguments(self, parser):
        parser.add_argument('--database-name', required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        validate_target(connection.settings_dict['NAME'], options['database_name'], os.getenv('LPN_ALLOW_DEMO_SEED'))
        if any(model.objects.exists() for model in (Usuario, Mascota, Producto, Reporte, EntidadVerificable)):
            raise CommandError('La base contiene datos. No se sobrescribe: utiliza una base demo nueva tras respaldar la anterior.')
        call_command('cargar_catalogos_produccion', stdout=StringIO())
        call_command('seed_demo', stdout=StringIO())
        for index, user in enumerate(Usuario.objects.order_by('pk')):
            user.nombre = PEOPLE_NAMES[index]
            user.telefono = ''  # No inventar números que puedan pertenecer a personas reales.
            user.save(update_fields=['nombre', 'telefono'])
        for pet in Mascota.objects.all():
            pet.nombre = presentation_name(pet.nombre)
            pet.save(update_fields=['nombre'])
        separate_pending_applications()
        manager = Usuario.objects.get(email='demo01@example.invalid')
        foundation = Fundacion.objects.get(entidad__nombre='Fundación demo 1')
        descriptions = (
            ('Canela disfruta los paseos tranquilos y la compañía.', 'Paseos diarios y adaptación gradual al nuevo hogar.'),
            ('Oliver es curioso y busca una familia que respete su ritmo.', 'Rutina estable y acompañamiento durante la adaptación.'),
            ('Sol disfruta explorar y jugar con supervisión.', 'Juego diario y seguimiento veterinario habitual.'),
            ('Frida busca un hogar paciente y afectuoso.', 'Presentaciones graduales con otros animales.'),
            ('Leo disfruta la compañía y los paseos cortos.', 'Actividad adecuada a su condición y revisión veterinaria.'),
        )
        for name, (description, care) in zip(('Canela', 'Oliver', 'Sol', 'Frida', 'Leo'), descriptions):
            pet = Mascota.objects.get(nombre=name)
            PresentacionPublicaMascota.objects.create(
                mascota=pet, fundacion=foundation, editor=manager, publicada=True,
                descripcion=description + ' Historia ficticia de demostración.',
                cuidados=care + ' Orientación simulada; no es un diagnóstico.',
                espacio='Hogar seguro, agua disponible y acompañamiento responsable.',
            )
        for product in Producto.objects.all():
            product.nombre = presentation_name(product.nombre)
            product.descripcion = 'Producto ficticio para demostrar el catálogo y la solicitud de pedido. Precio referencial en COP; no se realizan cobros.'
            product.save(update_fields=['nombre', 'descripcion'])
        for report in Reporte.objects.all():
            report.descripcion = presentation_name(report.descripcion)
            report.save(update_fields=['descripcion'])
        for entity in EntidadVerificable.objects.all():
            entity.nombre = presentation_name(entity.nombre)
            entity.save(update_fields=['nombre'])
            PerfilPublicoEntidad.objects.create(
                entidad=entity, editor=manager, publicada=True,
                descripcion='Organización ficticia para una demostración académica. No presta servicios reales ni recibe aportes.',
                servicios='Información simulada sobre acompañamiento y bienestar animal.',
            )
        # Los contactos simulados anteriores no deben convertirse en enlaces de llamada.
        from core.models import Tienda
        Tienda.objects.update(whatsapp='')
        admin = Usuario.objects.create_user(email='administracion@example.invalid', password=os.environ['LPN_DEMO_PASSWORD'], nombre='Administración de la demostración')
        UsuarioRol.objects.create(usuario=admin, rol=Rol.objects.get(codigo='ADMIN_SEGURIDAD'))
        auditar(admin, 'demo.preparar', 'usuarios', admin.pk, motivo='Base nueva de presentación con datos sintéticos; sin borrar instalaciones anteriores.')
        call_command('verify_demo', presentacion=True, stdout=StringIO())
        self.stdout.write(self.style.SUCCESS('Presentación preparada y verificada. Datos ficticios; no se ha borrado ninguna otra base.'))
        self.stdout.write('Ciudadano: demo20@example.invalid | Responsable: demo01@example.invalid | Administración: administracion@example.invalid')
        self.stdout.write('Fotografías: pendientes de publicación autorizada; no se inventan licencias ni se reutilizan archivos privados.')
