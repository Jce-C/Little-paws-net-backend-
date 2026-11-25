"""Validación de datos de entrada del proceso de identidad."""

from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from .models import Usuario
import re


class PerfilPropioSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=150, required=False)
    telefono = serializers.CharField(max_length=20, allow_blank=True, required=False)

    def to_internal_value(self, data):
        if not isinstance(data, dict) or set(data) - set(self.fields):
            raise serializers.ValidationError({"non_field_errors": ["Solo puedes actualizar tu nombre y teléfono desde el perfil."]})
        if not data:
            raise serializers.ValidationError({"non_field_errors": ["Indica al menos un dato para actualizar."]})
        return super().to_internal_value(data)

    def validate_telefono(self, value):
        if value and (not re.fullmatch(r"[+0-9(). \-]+", value) or not 7 <= len(re.sub(r"\D", "", value)) <= 15):
            raise serializers.ValidationError("Usa entre 7 y 15 dígitos; puedes incluir +, espacios, paréntesis y guiones.")
        return value


class RegistroSerializer(serializers.Serializer):
    email = serializers.EmailField()
    nombre = serializers.CharField(max_length=150)
    telefono = serializers.CharField(max_length=20, allow_blank=True, required=False)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_email(self, value):
        normalizado = Usuario.objects.normalize_email(value).strip()
        if Usuario.objects.filter(email__iexact=normalizado).exists():
            raise serializers.ValidationError("El correo ya está registrado")
        return normalizado

    def validate(self, attrs):
        candidato = Usuario(email=attrs["email"], nombre=attrs["nombre"])
        validate_password(attrs["password"], user=candidato)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        from core.models import Rol, UsuarioRol
        with transaction.atomic():
            usuario = Usuario.objects.create_user(password=password, **validated_data)
            UsuarioRol.objects.create(usuario=usuario, rol=Rol.objects.get(codigo="CIUDADANO", activo=True))
        return usuario
