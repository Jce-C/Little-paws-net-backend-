"""Cifrado autenticado de números de cuenta y referencias privadas."""

import os

from cryptography.fernet import Fernet, InvalidToken
from django.core.exceptions import ImproperlyConfigured


def _cipher():
    clave = os.getenv("LPN_DATA_KEY", "")
    if not clave:
        raise ImproperlyConfigured("Configure LPN_DATA_KEY fuera del repositorio")
    try:
        return Fernet(clave.encode("ascii"))
    except (ValueError, TypeError) as exc:
        raise ImproperlyConfigured("LPN_DATA_KEY no es una clave Fernet válida") from exc


def cifrar(texto):
    return _cipher().encrypt(texto.encode("utf-8"))


def descifrar(token):
    try:
        return _cipher().decrypt(bytes(token)).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("No se pudo descifrar el dato protegido") from exc
