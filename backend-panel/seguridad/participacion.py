"""Permisos configurables para los recorridos propios; nunca reemplazan titularidad."""
import re
from rest_framework.permissions import BasePermission
from .autorizacion import exigir

RUTAS=[
 ('POST',r'/api/adopcion/solicitudes/','adopcion.participar'),
 ('POST',r'/api/adopcion/solicitudes/evaluacion/','adopcion.participar'),
 ('POST',r'/api/seguridad/operaciones/adopciones/\d+/(respuestas|retirar)/','adopcion.participar'),
 ('POST',r'/api/apadrinamientos/','aporte.participar'),
 ('GET',r'/api/apadrinamientos/mios/','aporte.participar'),
 ('POST',r'/api/apadrinamientos/\d+/declaraciones/','aporte.participar'),
 ('GET',r'/api/apadrinamientos/\d+/cuenta/','aporte.participar'),
 ('POST',r'/api/pedidos/','pedido.participar'),
 ('GET',r'/api/pedidos/\d+/','pedido.participar'),
 ('POST',r'/api/fondos/donaciones/','fondo.participar'),
 ('POST',r'/api/reportes/','reportes.participar'),
 ('POST',r'/api/seguridad/operaciones/mascotas-propias/','mascotas.participar'),
 ('POST',r'/api/seguridad/operaciones/reclamaciones/','reclamacion.presentar'),
 ('POST',r'/api/seguridad/operaciones/reportes/\d+/(correcciones|propio-pendiente)/','reportes.participar'),
]


def comprobar(request):
    if not request.user.is_authenticated:return
    if request.method not in ('GET','HEAD','OPTIONS'):
        comprobar_entidades(request)
    for metodo,patron,codigo in RUTAS:
        if request.method==metodo and re.fullmatch(patron,request.path):
            exigir(request.user,codigo)
            return

def comprobar_entidades(request):
    """Resolve organizations from actual foreign keys before citizen mutations."""
    from .autorizacion import motor
    from rest_framework.exceptions import PermissionDenied
    bajas=motor(request.user).bajas_entidad
    if not bajas:return
    d=request.data
    if not hasattr(d,'get') or request.path.startswith('/api/seguridad/operaciones/reclamaciones/'):return
    def integer(key):
        from rest_framework.fields import IntegerField
        from rest_framework.exceptions import ValidationError
        try:return IntegerField(min_value=1).run_validation(d.get(key))
        except ValidationError:return None
    ids={integer(k) for k in ('entidad_id','id_fundacion','fundacion_id','id_tienda','tienda_id','clinica_id')}-{None}
    mascota=integer('id_mascota') or integer('mascota_id')
    if mascota:
        from animals.models import CustodiaMascota
        ids.update(CustodiaMascota.objects.filter(mascota_id=mascota,fecha_fin__isnull=True).values_list('fundacion_id',flat=True))
    reporte=integer('id_reporte')
    if reporte:
        from rescue.models import CasoRescate
        ids.update(CasoRescate.objects.filter(reporte_id=reporte).values_list('fundacion_id',flat=True))
    fondo=integer('id_fondo_externo') or integer('fondo_id')
    if fondo:
        from funds.models import FondoExterno
        ids.update(FondoExterno.objects.filter(pk=fondo).values_list('entidad_id',flat=True))
    if ids & bajas:raise PermissionDenied('La organización está desactivada. No admite nuevas operaciones.')


class Participacion(BasePermission):
    def has_permission(self,request,view):
        comprobar(request)
        return True
