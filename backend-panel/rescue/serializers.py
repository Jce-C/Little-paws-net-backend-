"""Validación de entradas para reportes, rescate y apadrinamiento."""

from decimal import Decimal

from rest_framework import serializers

from animals.models import Mascota
from core.models import ValorMaestro


class ReporteCrearSerializer(serializers.Serializer):
    tipo_reporte = serializers.PrimaryKeyRelatedField(queryset=ValorMaestro.objects.all())
    mascota = serializers.PrimaryKeyRelatedField(queryset=Mascota.objects.all(), required=False, allow_null=True)
    descripcion = serializers.CharField(max_length=5000)
    contacto_reportante = serializers.CharField(max_length=150, required=False, allow_blank=True)
    latitud = serializers.DecimalField(max_digits=9, decimal_places=6, min_value=-90, max_value=90)
    longitud = serializers.DecimalField(max_digits=9, decimal_places=6, min_value=-180, max_value=180)

    def validate_tipo_reporte(self, value):
        if value.tipo.nombre != "tipo_reporte":
            raise serializers.ValidationError("No corresponde a un tipo de reporte")
        return value


class GestionAnonimaSerializer(serializers.Serializer):
    codigo_gestion = serializers.CharField(write_only=True, max_length=128)
    descripcion = serializers.CharField(max_length=5000, required=False)
    contacto_reportante = serializers.CharField(max_length=150, required=False, allow_blank=True)
    cerrar = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        if not any(campo in attrs for campo in ("descripcion", "contacto_reportante")) and not attrs["cerrar"]:
            raise serializers.ValidationError("Indique un cambio o solicite cerrar el reporte")
        return attrs


class AceptarSerializer(serializers.Serializer):
    id_fundacion = serializers.IntegerField(min_value=1)
    justificacion_sin_cupo = serializers.CharField(required=False, allow_blank=True, max_length=2000)


class CompromisoSerializer(serializers.Serializer):
    id_reporte = serializers.IntegerField(min_value=1)
    monto_comprometido = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))


class CuentaCrearSerializer(serializers.Serializer):
    banco = serializers.CharField(max_length=120)
    tipo_cuenta = serializers.CharField(max_length=60)
    titular = serializers.CharField(max_length=150)
    numero_cuenta = serializers.RegexField(r"^[0-9]{6,34}$", write_only=True)


class DeclaracionSerializer(serializers.Serializer):
    monto_declarado = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))
    referencia = serializers.CharField(max_length=150, required=False, allow_blank=True, write_only=True)
    fecha_transferencia_declarada = serializers.DateTimeField()


class ConfirmacionSerializer(serializers.Serializer):
    monto_confirmado = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))
