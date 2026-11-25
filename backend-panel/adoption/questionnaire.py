"""Bounded and encrypted adoption answers. No originals, diagnoses or child identities."""
import json
from django.core.exceptions import ImproperlyConfigured
from rest_framework import serializers
from rest_framework.exceptions import APIException
from seguridad.serializers import EntradaEstricta
from core.crypto import cifrar, descifrar
from .models import EvaluacionAdopcion

VERSION = "adopcion-evaluacion-v1"
NOTICE = ("Autorizo a la organización responsable de esta adopción a consultar estas "
    "respuestas privadas para evaluar mi solicitud y contactarme sobre este proceso. "
    "No autorizo publicidad ni entrenamiento de IA. No debo incluir datos de otras personas.")


class EvaluacionEntrada(EntradaEstricta, serializers.Serializer):
    nombre = serializers.CharField(max_length=150)
    documento = serializers.CharField(max_length=40)
    telefono = serializers.CharField(max_length=30)
    email = serializers.EmailField(max_length=254)
    direccion = serializers.CharField(max_length=300)
    vivienda = serializers.ChoiceField(choices=["casa", "apartamento", "otra"])
    tenencia = serializers.ChoiceField(choices=["propia", "arrendada", "otra"])
    autorizacion_propietario = serializers.ChoiceField(choices=["si", "no", "pendiente"], required=False)
    seguridad_espacio = serializers.CharField(max_length=600)
    personas_hogar = serializers.IntegerField(min_value=1, max_value=50)
    acuerdo_hogar = serializers.BooleanField()
    tiempo_cuidado = serializers.ChoiceField(choices=["diario", "compartido", "por_organizar"])
    recursos_cuidado = serializers.ChoiceField(choices=["disponibles", "con_apoyo", "por_organizar"])
    cuidados_especiales = serializers.ChoiceField(choices=["si", "necesito_orientacion"])
    seguimiento = serializers.ChoiceField(choices=["si", "necesito_informacion"])
    mascotas_actuales = serializers.BooleanField()
    cantidad_mascotas = serializers.IntegerField(min_value=1, max_value=50, required=False)
    otras_mascotas = serializers.CharField(max_length=600, required=False)
    esterilizacion = serializers.ChoiceField(choices=["si", "no", "parcial", "no_se"], required=False)
    experiencia_previa = serializers.BooleanField()
    experiencia = serializers.CharField(max_length=1000, required=False)
    motivo = serializers.CharField(min_length=10, max_length=2000)
    datos_correctos = serializers.BooleanField()
    autoriza_evaluacion = serializers.BooleanField()
    version = serializers.ChoiceField(choices=[VERSION])

    def validate(self, data):
        errors = {}
        for field in ("datos_correctos", "autoriza_evaluacion"):
            if not data[field]:
                errors[field] = "Debes confirmar esta opción antes de enviar."
        groups = [
            (data["tenencia"] == "arrendada", ("autorizacion_propietario",)),
            (data["mascotas_actuales"], ("cantidad_mascotas", "otras_mascotas", "esterilizacion")),
            (data["experiencia_previa"], ("experiencia",)),
        ]
        for active, fields in groups:
            for field in fields:
                if active and field not in data:
                    errors[field] = "Completa esta respuesta."
                elif not active:
                    data.pop(field, None)  # Do not retain stale hidden answers.
        if errors:
            raise serializers.ValidationError(errors)
        return data


class EvaluacionNoDisponible(APIException):
    status_code = 503
    default_detail = "El servicio de respuestas protegidas no está disponible. Conserva el formulario o vuelve a consultar más tarde."


def guardar(solicitud, fundacion_id, answers):
    try:
        encrypted = cifrar(json.dumps({"respuestas": answers, "autorizacion": NOTICE},
            ensure_ascii=False, sort_keys=True))
    except (ImproperlyConfigured, ValueError, UnicodeError) as exc:
        raise EvaluacionNoDisponible() from exc
    return EvaluacionAdopcion.objects.create(solicitud=solicitud,
        fundacion_id=fundacion_id, contenido_cifrado=encrypted, version=VERSION)


def consultar(solicitud_id):
    """Call only after object-level authorization, never from public serializers."""
    row = EvaluacionAdopcion.objects.filter(solicitud_id=solicitud_id).first()
    if row is None:
        return None
    try:
        stored = json.loads(descifrar(row.contenido_cifrado))
        answers = stored["respuestas"]
        notice = stored["autorizacion"]
    except (ImproperlyConfigured, ValueError, UnicodeError, KeyError, TypeError) as exc:
        raise EvaluacionNoDisponible() from exc
    return {"respuestas": answers, "version": row.version,
        "aceptada_en": row.aceptada_en, "organizacion_receptora": row.fundacion_id,
        "autorizacion": notice}


LABELS = {
    "nombre": "Nombre completo", "documento": "Documento de identidad",
    "telefono": "Teléfono", "email": "Correo electrónico", "direccion": "Dirección",
    "vivienda": "Tipo de vivienda", "tenencia": "Tenencia de la vivienda",
    "autorizacion_propietario": "Autorización del propietario",
    "seguridad_espacio": "Seguridad del espacio", "personas_hogar": "Personas en el hogar",
    "acuerdo_hogar": "Acuerdo del hogar", "tiempo_cuidado": "Disponibilidad de tiempo",
    "recursos_cuidado": "Recursos para los cuidados", "cuidados_especiales": "Cuidados especiales",
    "seguimiento": "Seguimiento de la organización", "mascotas_actuales": "Tiene mascotas",
    "cantidad_mascotas": "Cantidad de mascotas", "otras_mascotas": "Especies y edades",
    "esterilizacion": "Esterilización", "experiencia_previa": "Experiencia previa",
    "experiencia": "Qué ocurrió con sus mascotas anteriores", "motivo": "Motivo de adopción",
    "datos_correctos": "Confirma datos correctos", "autoriza_evaluacion": "Autoriza evaluación privada",
    "version": "Versión del formulario",
}
VALUES = {"si": "Sí", "no": "No", "pendiente": "Pendiente de confirmar",
    "por_organizar": "Por organizar", "con_apoyo": "Con apoyo", "no_se": "No lo sabe",
    "necesito_orientacion": "Necesita orientación", "necesito_informacion": "Solicita más información"}


def para_revision(data):
    if data is None:
        return "Esta solicitud se creó sin el formulario por etapas."
    return {"Respuestas iniciales": {LABELS.get(k, k): VALUES.get(v, v) if isinstance(v, str) else v
                for k, v in data["respuestas"].items()},
        "Aceptada el": data["aceptada_en"], "Versión": data["version"],
        "Organización receptora": data["organizacion_receptora"], "Finalidad autorizada": data["autorizacion"]}
