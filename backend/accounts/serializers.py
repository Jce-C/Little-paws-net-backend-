"""Validación de entrada del registro de usuarios."""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Usuario


class RegistroSerializer(serializers.Serializer):
    email = serializers.EmailField()
    nombre = serializers.CharField(max_length=150)
    telefono = serializers.CharField(max_length=20, allow_blank=True, required=False)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_email(self, value):
        email = Usuario.objects.normalize_email(value).strip()
        if Usuario.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("El correo ya está registrado")
        return email

    def validate(self, attrs):
        candidato = Usuario(email=attrs["email"], nombre=attrs["nombre"])
        validate_password(attrs["password"], user=candidato)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        return Usuario.objects.create_user(password=password, **validated_data)
