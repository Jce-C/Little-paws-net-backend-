from django.db.models import Count,Q
from animals.models import Mascota

def disponibles_adopcion():
    from seguridad.models import BajaAdministrativa
    bajas=BajaAdministrativa.objects.filter(tipo='entidades',activo=False).values('objeto_id')
    return Mascota.objects.filter(estado_mascota__tipo__nombre='estado_mascota',estado_mascota__nombre='En adopción',dueno__isnull=True).annotate(
        custodias_vigentes=Count('custodiamascota',filter=Q(custodiamascota__fecha_fin__isnull=True))
    ).filter(custodias_vigentes=1,custodiamascota__fecha_fin__isnull=True,custodiamascota__fundacion__entidad__estado_verificacion__nombre='Verificada').exclude(custodiamascota__fundacion_id__in=bajas).exclude(solicitudadopcion__estado_adopcion__nombre='Pendiente')
