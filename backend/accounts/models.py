"""Modelo propio de usuario, definido antes de la primera migración."""

from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from .managers import UsuarioManager


class Usuario(AbstractBaseUser):
    id_usuario = models.AutoField(primary_key=True)
    password = models.CharField(max_length=255, db_column="password_hash")
    email = models.EmailField(unique=True, max_length=254, db_column="correo")
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

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
        return self.is_active and self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_active and self.is_superuser
