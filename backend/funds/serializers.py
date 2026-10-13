"""Entrada validada y salida pública del catálogo de fondos externos."""

from decimal import Decimal

from rest_framework import serializers

from core.models import ArchivoDigital, Fundacion
from core.i18n import etiqueta, texto

from .models import FondoExterno


class FondoExternoCrearSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=150, allow_blank=False, trim_whitespace=True)
    instrucciones_transferencia = serializers.CharField(
        max_length=2000, allow_blank=False, trim_whitespace=True,
    )


def representar_fondo(fondo):
    return {"id_fondo_externo": fondo.pk, "nombre": fondo.nombre}


class CompromisoDonacionCrearSerializer(serializers.Serializer):
    id_fondo_externo = serializers.PrimaryKeyRelatedField(
        queryset=FondoExterno.objects.all(), source="fondo_externo",
    )
    monto_comprometido = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01"),
    )


class ResolverDonacionSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=("Confirmada", "Rechazada"))
    observacion = serializers.CharField(max_length=2000, allow_blank=False, trim_whitespace=True)
    referencia_externa = serializers.CharField(
        max_length=120, required=False, allow_blank=True, trim_whitespace=True,
        help_text="Identificador del comprobante externo; no incluya datos bancarios sensibles.",
    )

    def validate(self, attrs):
        if attrs["estado"] == "Confirmada" and not attrs.get("referencia_externa", ""):
            raise serializers.ValidationError({
                "referencia_externa": texto(
                    "Se requiere una referencia externa para confirmar la donación.",
                    "An external reference is required to confirm the donation.",
                ),
            })
        return attrs


def representar_donacion(donacion, *, incluir_historial=False):
    avisos = {
        "Comprometida": "Compromiso registrado; no acredita recepción de dinero",
        "Confirmada": "Recepción registrada por un administrador; Little Paws Net no procesó el pago",
        "Rechazada": "Compromiso rechazado; no se registró dinero recibido",
        "Cancelada": "Compromiso cancelado; no se registró dinero recibido",
    }
    datos = {
        "id_donacion": donacion.pk,
        "id_fondo_externo": donacion.fondo_externo_id,
        "fondo": donacion.fondo_externo.nombre,
        "id_usuario_donante": donacion.usuario_donante_id,
        "estado": etiqueta(donacion.estado_donacion.nombre),
        "monto_comprometido": str(donacion.monto_comprometido),
        "fecha_compromiso": donacion.fecha_compromiso,
        "aviso": texto(
            avisos.get(donacion.estado_donacion.nombre, "Estado informativo; sin procesamiento de pagos"),
            {
                "Comprometida": "Pledge recorded; receipt of funds is not confirmed",
                "Confirmada": "Receipt recorded by an administrator; Little Paws Net did not process the payment",
                "Rechazada": "Pledge rejected; no receipt of funds was recorded",
                "Cancelada": "Pledge cancelled; no receipt of funds was recorded",
            }.get(donacion.estado_donacion.nombre, "Informational status; no payment processing"),
        ),
    }
    if incluir_historial:
        datos["historial"] = [
            {
                "id_historial_donacion": cambio.pk,
                "estado_anterior": None if cambio.estado_anterior_id is None else etiqueta(cambio.estado_anterior.nombre),
                "estado_nuevo": etiqueta(cambio.estado_nuevo.nombre),
                "id_usuario_actor": cambio.usuario_actor_id,
                "fecha_cambio": cambio.fecha_cambio,
                "observacion": cambio.observacion,
            }
            for cambio in donacion.historialestadodonacion_set.select_related(
                "estado_anterior", "estado_nuevo",
            ).order_by("fecha_cambio", "pk")
        ]
    return datos


class DistribucionCrearSerializer(serializers.Serializer):
    id_fondo_externo = serializers.PrimaryKeyRelatedField(
        queryset=FondoExterno.objects.all(), source="fondo_externo",
    )
    id_fundacion = serializers.PrimaryKeyRelatedField(
        queryset=Fundacion.objects.all(), source="fundacion",
    )
    monto_reportado = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))
    fecha_distribucion = serializers.DateTimeField()
    criterio = serializers.CharField(max_length=2000, allow_blank=False, trim_whitespace=True)
    id_archivo_evidencia = serializers.PrimaryKeyRelatedField(
        queryset=ArchivoDigital.objects.all(), source="archivo_evidencia",
    )


class ConfirmarDistribucionSerializer(serializers.Serializer):
    observacion_confirmacion = serializers.CharField(
        max_length=2000, allow_blank=False, trim_whitespace=True,
    )


def representar_distribucion(distribucion):
    return {
        "id_distribucion": distribucion.pk,
        "id_fondo_externo": distribucion.fondo_externo_id,
        "id_fundacion": distribucion.fundacion_id,
        "monto_reportado": str(distribucion.monto_reportado),
        "estado": etiqueta(distribucion.estado_distribucion.nombre),
        "fecha_distribucion": distribucion.fecha_distribucion,
        "fecha_reporte": distribucion.fecha_reporte,
        "id_usuario_reportador": distribucion.usuario_reportador_id,
        "criterio": distribucion.criterio,
        "id_archivo_evidencia": distribucion.archivo_evidencia_id,
        "id_usuario_confirmador": distribucion.usuario_confirmador_id,
        "fecha_confirmacion": distribucion.fecha_confirmacion,
        "observacion_confirmacion": distribucion.observacion_confirmacion,
        "aviso": texto(
            "Registro informativo de una distribución externa; Little Paws Net no transfiere fondos",
            "Informational record of an external distribution; Little Paws Net does not transfer funds",
        ),
    }
