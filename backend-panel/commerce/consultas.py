from .models import Producto

def productos_vigentes():
    from seguridad.models import BajaAdministrativa
    return Producto.objects.exclude(pk__in=BajaAdministrativa.objects.filter(tipo='productos',eliminado=True).values('objeto_id'))
