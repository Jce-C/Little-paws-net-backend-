"""Atomic, actor-scoped replay protection for citizen creations."""
import hashlib
import json
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework.response import Response
from .models import OperacionCiudadana

@transaction.atomic
def crear_una_vez(request, operacion, datos, crear):
    raw = request.headers.get('Idempotency-Key')
    if raw is None:
        return crear()
    clave = serializers.UUIDField().run_validation(raw)
    huella = hashlib.sha256(json.dumps(datos, sort_keys=True, ensure_ascii=False, default=str).encode('utf-8')).hexdigest()
    # Serialize competing retries on the same actor, even before a receipt exists.
    get_user_model().objects.select_for_update().get(pk=request.user.pk)
    previous = OperacionCiudadana.objects.filter(usuario=request.user, operacion=operacion, clave=clave).first()
    if previous:
        if previous.huella != huella:
            return Response({'detalle':'Esta operación ya se utilizó con otros datos. Revisa el registro original.'}, status=409)
        response = Response(previous.respuesta, status=previous.estado_http)
        response['Idempotency-Replayed'] = 'true'
    else:
        response = crear()
        if 200 <= response.status_code < 300:
            OperacionCiudadana.objects.create(usuario=request.user, operacion=operacion, clave=clave, huella=huella, respuesta=response.data, estado_http=response.status_code)
    response['Cache-Control'] = 'no-store'
    return response
