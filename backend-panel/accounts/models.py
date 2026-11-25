from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from .managers import UsuarioManager


class Usuario(AbstractBaseUser):
    """Identidad de inicio de sesión, distinta de los roles de negocio V2.

    El catálogo de seguridad es canónico también para la correspondencia con
    Django Admin. El superusuario activo tiene precedencia administrativa total.
    """

    id_usuario = models.AutoField(primary_key=True)
    password = models.CharField(max_length=255, db_column="password_hash")
    email = models.EmailField(unique=True, max_length=254, db_column="correo")
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    debe_cambiar_clave = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre"]

    class Meta:
        db_table = "Usuario"
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        from seguridad.django_permisos import permitido
        return permitido(self, perm, obj)

    def has_module_perms(self, app_label):
        from seguridad.django_permisos import modulo_permitido
        return modulo_permitido(self, app_label)
