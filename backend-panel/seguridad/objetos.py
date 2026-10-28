"""Registro cerrado de objetos asignables; nunca confiar en entidad_id del cliente."""
from dataclasses import dataclass

from django.apps import apps
from rest_framework.exceptions import NotFound, ValidationError


MODELOS = {
    "adopcion": ("adoption", "SolicitudAdopcion"),
    "aporte": ("rescue", "Apadrinamiento"),
    "pedido": ("commerce", "PedidoIniciado"),
    "fondo": ("funds", "FondoExterno"),
    "verificacion": ("core", "SolicitudValidacion"),
}


@dataclass
class Contexto:
    objeto: object
    entidad_id: int | None
    disponible: bool
    propietario_id: int | None = None


def contexto(codigo, objeto_id, *, bloquear=False):
    if codigo not in MODELOS:
        raise ValidationError("Este recurso no tiene operaciones de asignación implementadas")
    modelo = apps.get_model(*MODELOS[codigo])
    # El servicio de resolución bloquea primero la mascota. Conservar el mismo orden.
    if codigo == "adopcion" and bloquear:
        mascota_id = modelo.objects.filter(pk=objeto_id).values_list("mascota_id", flat=True).first()
        if mascota_id is None:
            raise NotFound("Registro no disponible")
        apps.get_model("animals", "Mascota").objects.select_for_update().get(pk=mascota_id)
    qs = modelo.objects.select_for_update() if bloquear else modelo.objects.all()
    obj = qs.filter(pk=objeto_id).first()
    if obj is None:
        raise NotFound("Registro no disponible")
    if codigo == "verificacion":
        return Contexto(obj, obj.entidad_id, obj.fecha_resolucion is None and obj.estado_solicitud.nombre == "Pendiente", obj.usuario_solicitante_id)
    if codigo == "adopcion":
        ids = list(apps.get_model("animals", "CustodiaMascota").objects.filter(
            mascota_id=obj.mascota_id, fecha_fin__isnull=True).values_list("fundacion_id", flat=True)[:2])
        return Contexto(obj, ids[0] if len(ids) == 1 else None,
                        len(ids) == 1 and obj.estado_adopcion.nombre == "Pendiente"
                        and obj.mascota.estado_mascota.nombre == "En adopción", obj.usuario_adoptante_id)
    if codigo == "aporte":
        entidad_id = apps.get_model("rescue", "CasoRescate").objects.filter(
            reporte_id=obj.reporte_id).values_list("fundacion_id", flat=True).first()
        return Contexto(obj, entidad_id, entidad_id is not None and obj.estado_apadrinamiento.nombre in ("En espera", "Aceptado"), obj.usuario_padrino_id)
    if codigo == "pedido":
        return Contexto(obj, obj.tienda_id, obj.estado_pedido.nombre in ("Iniciado", "Contactado"), obj.usuario_cliente_id)
    return Contexto(obj, obj.entidad_id, obj.entidad_id is not None and obj.estado_fondo.nombre == "Activo")
