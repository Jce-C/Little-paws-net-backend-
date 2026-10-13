"""Etiquetas y mensajes estables de la API comercial en español e inglés.

Los valores de catálogo mantienen su nombre original en la base: traducir la
respuesta no modifica las claves foráneas ni las reglas de negocio.
"""

from django.utils.translation import get_language


def ingles_activo():
    return get_language().startswith("en")


def texto(es, en):
    return en if ingles_activo() else es


ETIQUETAS = {
    "Alimentos": "Food",
    "Accesorios": "Accessories",
    "Salud": "Health",
    "Alimento seco": "Dry food",
    "Collar": "Collar",
    "Otro": "Other",
    "Disponible": "Available",
    "Inactivo": "Inactive",
    "Iniciado": "Started",
    "Cancelado": "Cancelled",
    "Banner": "Banner",
    "Mensual": "Monthly",
}


def etiqueta(nombre):
    return ETIQUETAS.get(nombre, nombre) if ingles_activo() else nombre


ERRORES = {
    "No puede gestionar productos de esta tienda": "You cannot manage this store's products",
    "La tienda debe estar verificada": "The store must be verified",
    "Precio y existencias no válidos": "Invalid price or stock",
    "Producto inexistente": "Product not found",
    "La cuenta del cliente no está activa": "The customer account is inactive",
    "El pedido requiere entre 1 y 50 productos": "The order requires 1 to 50 products",
    "No se puede repetir un producto en el mismo pedido": "A product cannot appear twice in the same order",
    "Todos los productos deben pertenecer a la tienda seleccionada": "All products must belong to the selected store",
    "Uno de los productos no está disponible": "A product is unavailable",
    "Cantidad superior a las existencias disponibles": "Quantity exceeds available stock",
    "Uno de los productos no tiene precio válido": "A product has an invalid price",
    "No puede publicar anuncios para este anunciante": "You cannot publish ads for this advertiser",
    "El anunciante debe estar verificado": "The advertiser must be verified",
    "Tipo de publicidad inválido": "Invalid advertising type",
    "El periodo de publicación debe ser válido y no estar vencido": "The publication period must be valid and not expired",
    "El destino debe ser una URL HTTPS pública": "The destination must be a public HTTPS URL",
    "El archivo debe ser público, tener URL y pertenecer al publicador": "The file must be public, have a URL, and belong to the publisher",
    "Solo un administrador autorizado puede crear tarifas": "Only an authorized administrator can create rates",
    "Tipo, monto o periodo de tarifa no válidos": "Invalid rate type, amount, or period",
    "El concepto es obligatorio": "The description is required",
    "Ya existe una tarifa de este tipo que se superpone en fechas": "A rate of this type already overlaps these dates",
}


def error(mensaje):
    return ERRORES.get(mensaje, mensaje) if ingles_activo() else mensaje
