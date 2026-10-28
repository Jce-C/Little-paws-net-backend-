"""Contratos de entrada explícitos para los recorridos de la etapa 2."""
from rest_framework import serializers as s
from .serializers import EntradaEstricta


class Decision(EntradaEstricta, s.Serializer):
    aprobar = s.BooleanField()
    motivo = s.CharField(max_length=500)


class Accion(EntradaEstricta, s.Serializer):
    accion = s.CharField(max_length=30)
    motivo = s.CharField(max_length=500)


class ExcepcionEntrada(EntradaEstricta, s.Serializer):
    recurso = s.ChoiceField(choices=["historial", "soporte", "adopcion", "aporte", "pedido", "verificacion"])
    objeto_id = s.IntegerField(min_value=1)
    motivo = s.CharField(max_length=500)


class DecisionExcepcion(Decision):
    horas = s.IntegerField(min_value=1, max_value=24, default=24)


class DelegacionEntrada(EntradaEstricta, s.Serializer):
    miembro_id = s.IntegerField(min_value=1)
    revocar = s.BooleanField(default=False)


class CuentaEntrada(EntradaEstricta, s.Serializer):
    numero = s.RegexField(regex=r"\A[0-9]{4,40}\Z", max_length=40)
    banco = s.CharField(max_length=120)
    tipo = s.CharField(max_length=60)
    titular = s.CharField(max_length=150)


class EnmiendaEntrada(EntradaEstricta, s.Serializer):
    detalle = s.CharField(max_length=12000)
    motivo = s.CharField(max_length=500)


class SoporteEntrada(EntradaEstricta, s.Serializer):
    resultado = s.ChoiceField(choices=["VALIDADO", "ACLARACIONES"])
    observacion = s.CharField(max_length=500)


class RespuestasEntrada(EntradaEstricta, s.Serializer):
    respuestas = s.DictField(child=s.CharField(max_length=2000), allow_empty=False)


class RetirarEntrada(EntradaEstricta, s.Serializer):
    confirmar = s.BooleanField()


class CorreccionEntrada(EntradaEstricta, s.Serializer):
    propuesta = s.DictField(child=s.CharField(max_length=5000))
    motivo = s.CharField(max_length=500)


class VersionEntrada(EntradaEstricta, s.Serializer):
    titulo = s.CharField(max_length=150)
    texto = s.CharField(max_length=1000)
    url = s.URLField(max_length=2048)
    inicio = s.DateTimeField()
    fin = s.DateTimeField()

    def validate(self, datos):
        if datos["fin"] <= datos["inicio"] or not datos["url"].startswith("https://"):
            raise s.ValidationError("Vigencia inválida o destino sin HTTPS")
        return datos


class TitularidadEntrada(EntradaEstricta, s.Serializer):
    dueno_actual_id = s.IntegerField(min_value=1, allow_null=True)
    nuevo_dueno_id = s.IntegerField(min_value=1)
    motivo = s.CharField(max_length=500)


class EstadoEntrada(EntradaEstricta, s.Serializer):
    estado = s.CharField(max_length=30)
    motivo = s.CharField(max_length=500)


class ReclamarEntrada(EntradaEstricta, s.Serializer):
    mascota_id = s.IntegerField(min_value=1)
    motivo = s.CharField(max_length=500)


class MascotaEntrada(EntradaEstricta, s.Serializer):
    nombre = s.CharField(max_length=120)
    raza_id = s.IntegerField(min_value=1)
    fecha_nacimiento = s.DateField(required=False, allow_null=True)


class ProductoEntrada(EntradaEstricta, s.Serializer):
    nombre = s.CharField(max_length=150, required=False)
    descripcion = s.CharField(max_length=5000, required=False, allow_blank=True)
    precio = s.DecimalField(max_digits=12, decimal_places=2, min_value=0, required=False)
    existencias = s.IntegerField(min_value=0, required=False)
    disponible = s.BooleanField(required=False)
    categoria_id = s.IntegerField(min_value=1, required=False)
    tipo_id = s.IntegerField(min_value=1, required=False)
