"""Validación de entradas para reportes, rescate y apadrinamiento."""

from decimal import Decimal

from rest_framework import serializers

from animals.models import Mascota
from core.models import ValorMaestro, Ciudad


class ReporteCrearSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if hasattr(data, "keys"):
            unknown = set(data.keys()) - set(self.fields)
            if unknown:
                raise serializers.ValidationError({key: "Campo no permitido." for key in sorted(unknown)})
        return super().to_internal_value(data)

    archivo = serializers.ImageField(required=False, write_only=True)
    confirmar_foto_publica = serializers.BooleanField(default=False)
    tipo_reporte = serializers.PrimaryKeyRelatedField(queryset=ValorMaestro.objects.all())
    mascota = serializers.PrimaryKeyRelatedField(queryset=Mascota.objects.all(), required=False, allow_null=True)
    descripcion = serializers.CharField(max_length=5000)
    contacto_reportante = serializers.CharField(max_length=150, required=False, allow_blank=True)
    ciudad_id = serializers.PrimaryKeyRelatedField(queryset=Ciudad.objects.filter(activo=True))
    barrio = serializers.CharField(max_length=120)
    direccion = serializers.CharField(max_length=255)
    indicaciones = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    latitud = serializers.DecimalField(max_digits=9, decimal_places=6, min_value=-90, max_value=90, required=False)
    longitud = serializers.DecimalField(max_digits=9, decimal_places=6, min_value=-180, max_value=180, required=False)

    def validate(self, attrs):
        if attrs.get('archivo'):
            if not attrs.get('confirmar_foto_publica'):
                raise serializers.ValidationError('Autoriza mostrar la foto con el reporte público.')
            from core.public_images import normalizar
            attrs['foto_normalizada'] = normalizar(attrs['archivo'], max_side=960, max_output=128*1024)
        if ('latitud' in attrs) != ('longitud' in attrs):
            raise serializers.ValidationError('Las coordenadas deben incluir latitud y longitud juntas.')
        return attrs

    def validate_tipo_reporte(self, value):
        if value.tipo.nombre != "tipo_reporte" or not value.tipo.activo:
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
