"""Alta explícita del primer administrador; no imprime ni acepta contraseñas por CLI."""
from getpass import getpass

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.db import transaction

from accounts.models import Usuario
from core.models import Rol, UsuarioRol
from seguridad.servicios import auditar, bloqueo_seguridad


class Command(BaseCommand):
    help = "Crea o autoriza una cuenta activa como primer Administrador de seguridad (sin superusuario técnico)."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--nombre", default="Responsable de seguridad")

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            validate_email(options["email"])
        except ValidationError as exc:
            raise CommandError("Correo inválido") from exc
        try:
            rol = bloqueo_seguridad()
        except Rol.DoesNotExist as exc:
            raise CommandError("Aplica primero las migraciones") from exc
        if UsuarioRol.objects.filter(rol=rol, usuario__is_active=True, fecha_revocacion__isnull=True).exists():
            raise CommandError("Ya existe un administrador activo; utiliza la administración de roles")
        email = Usuario.objects.normalize_email(options["email"]).strip()
        usuario = Usuario.objects.filter(email__iexact=email).first()
        if usuario and not usuario.is_active:
            raise CommandError("La cuenta está desactivada; no se reactiva automáticamente")
        if usuario is None:
            password = getpass("Contraseña inicial (oculta): ")
            if password != getpass("Repite la contraseña: "):
                raise CommandError("Las contraseñas no coinciden")
            usuario = Usuario(email=email, nombre=options["nombre"])
            try:
                validate_password(password, usuario)
            except ValidationError as exc:
                raise CommandError("; ".join(exc.messages)) from exc
            usuario.set_password(password)
            usuario.save()
        asignacion, _ = UsuarioRol.objects.get_or_create(usuario=usuario, rol=rol)
        asignacion.fecha_revocacion = None
        asignacion.save(update_fields=["fecha_revocacion"])
        auditar(usuario, "seguridad.inicializar", "usuarios", usuario.pk)
        self.stdout.write(self.style.SUCCESS("Primer Administrador de seguridad autorizado. La contraseña no se imprime."))
