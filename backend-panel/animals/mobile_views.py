"""Listado privado de las mascotas asociadas a la cuenta móvil."""
from django.db.models import Exists, OuterRef
from rest_framework.response import Response

from seguridad.autorizacion import exigir
from seguridad.flujos_views import Privada
from .models import CustodiaMascota, Mascota


class MisMascotasView(Privada):
    def get(self, request):
        from rest_framework import serializers
        paginated = request.query_params.get('pagina') == '1'
        limit = serializers.IntegerField(min_value=1, max_value=20).run_validation(request.query_params.get('limite', 20)) if paginated else 100
        before = request.query_params.get('antes')
        before = serializers.IntegerField(min_value=1,max_value=2147483647).run_validation(before) if before is not None else None
        exigir(request.user, "mascotas.participar")
        custody = CustodiaMascota.objects.filter(mascota_id=OuterRef("pk"), fecha_fin__isnull=True)
        pets = Mascota.objects.filter(dueno=request.user).select_related("especie", "raza__especie", "estado_mascota", "perfil_personal").annotate(
            custodia_vigente=Exists(custody),
        ).order_by("-pk")
        if before is not None:pets=pets.filter(pk__lt=before)
        if not paginated:pets=pets.defer('perfil_personal__foto')
        pets=list(pets[:limit + 1 if paginated else 100])
        more=paginated and len(pets)>limit
        if paginated:pets=pets[:limit]
        from .personal_views import personal_descriptor
        rows = [{
            "id_mascota": pet.pk,
            "nombre": pet.nombre,
            "especie": pet.especie_nombre,
            "raza": pet.raza_nombre,
            "estado": pet.estado_mascota.nombre,
            "custodia_vigente": pet.custodia_vigente,
            "personal": personal_descriptor(pet, include_photo=paginated),
        } for pet in pets]
        if not paginated:
            for row in rows:
                if row["personal"] is not None:row["personal"].pop("foto_miniatura",None)
        response=Response({"results":rows,"next_cursor":str(pets[-1].pk) if more else None} if paginated else rows)
        response["Cache-Control"]="no-store"
        return response
