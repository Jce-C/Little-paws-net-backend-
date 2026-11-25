from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from getpass import getpass
from secrets import token_hex

from animals.models import CustodiaMascota, Mascota
from core.models import (
    Ciudad, EntidadMiembro, EntidadMiembroRol, EntidadVerificable, Fundacion,
    Rol, UsuarioRol, ValorMaestro,
)


class Command(BaseCommand):
    help = "Crea un escenario sintético de adopción en la base QA local."

    @transaction.atomic
    def handle(self, *args, **options):
        database = settings.DATABASES["default"]
        if not (
            settings.DEBUG
            and database["HOST"] == "127.0.0.1"
            and database["NAME"] == "lpn_panel_qa_29"
        ):
            raise CommandError("Usa config.settings_qa y su base MySQL local aislada.")

        password = getpass("Contraseña temporal para las cuentas QA (mínimo 12 caracteres): ")
        if len(password) < 12:
            raise CommandError("La contraseña temporal requiere al menos 12 caracteres.")

        code = token_hex(4)
        user = get_user_model()
        citizen = user.objects.create_user(
            email=f"adoptante-{code}@example.invalid",
            nombre="Adoptante QA",
            password=password,
        )
        manager = user.objects.create_user(
            email=f"gestor-{code}@example.invalid",
            nombre="Gestor de adopciones QA",
            password=password,
        )
        role = Rol.objects.get(codigo="CIUDADANO", activo=True)
        for account in (citizen, manager):
            UsuarioRol.objects.create(usuario=account, rol=role)

        city, _ = Ciudad.objects.get_or_create(
            codigo_divipola="44001",
            defaults={"nombre": "RIOHACHA", "departamento": "LA GUAJIRA", "activo": True},
        )
        entity = EntidadVerificable.objects.create(
            nombre=f"Fundación móvil QA {code}",
            estado_verificacion=ValorMaestro.objects.get(
                tipo__nombre="estado_verificacion", nombre="Verificada",
            ),
        )
        foundation = Fundacion.objects.create(entidad=entity, ciudad=city, nit=str(entity.pk))
        membership = EntidadMiembro.objects.create(usuario=manager, entidad=entity)
        EntidadMiembroRol.objects.create(
            miembro=membership,
            rol=Rol.objects.get(codigo="GESTOR_ADOPCIONES", activo=True),
        )
        pet = Mascota.objects.create(
            nombre=f"Luna QA {code}",
            descripcion_especie="Perro",
            estado_mascota=ValorMaestro.objects.get(
                tipo__nombre="estado_mascota", nombre="En adopción",
            ),
        )
        CustodiaMascota.objects.create(
            mascota=pet, fundacion=foundation, usuario_registrador=manager,
            fecha_inicio=timezone.now(),
        )
        self.stdout.write(f"Adoptante: {citizen.email}")
        self.stdout.write(f"Gestor: {manager.email}")
        self.stdout.write(f"Mascota: {pet.nombre} · ID {pet.pk}")
        self.stdout.write(f"Fundación: {entity.nombre} · ID {entity.pk}")
