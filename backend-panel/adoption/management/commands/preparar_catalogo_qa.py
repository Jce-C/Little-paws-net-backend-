"""Escenario reversible de paginación; exclusivamente MySQL QA local."""
import hashlib
import json
import tempfile
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from animals.models import Mascota, CustodiaMascota
from adoption.consultas import disponibles_adopcion


class Command(BaseCommand):
    help = "Prepara 27 fichas sintéticas para catalog_android_test; --limpiar las retira."

    def add_arguments(self, parser):
        parser.add_argument("--limpiar", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        db = settings.DATABASES["default"]
        if not (settings.DEBUG and db["HOST"] == "127.0.0.1" and db["NAME"] == "lpn_panel_qa_29"):
            raise CommandError("Usa exclusivamente config.settings_qa y su MySQL local aislado.")
        namespace = hashlib.sha256(str(settings.BASE_DIR).encode()).hexdigest()[:12]
        manifest = Path(tempfile.gettempdir()) / f"lpn-catalogo-qa-{namespace}.json"
        if options["limpiar"]:
            if not manifest.exists():
                raise CommandError("No hay manifiesto de este escenario; no se elimina ninguna ficha.")
            ids = json.loads(manifest.read_text(encoding="utf8"))["ids"]
            pets = Mascota.objects.filter(pk__in=ids, nombre__startswith="QA Pagina ", descripcion_especie="QA Paginacion", dueno__isnull=True)
            if pets.count() != len(ids):
                raise CommandError("El escenario cambió. Revisa los IDs antes de retirarlo.")
            CustodiaMascota.objects.filter(mascota__in=pets).delete()
            pets.delete()
            transaction.on_commit(lambda: manifest.unlink())
            self.stdout.write("27 fichas temporales retiradas de QA.")
            return
        if manifest.exists() or Mascota.objects.filter(descripcion_especie="QA Paginacion").exists():
            raise CommandError("Hay un escenario pendiente; retíralo antes de crear otro.")
        pet = disponibles_adopcion().first()
        if pet is None:
            raise CommandError("Prepara primero una adopción sintética con custodia verificada en QA.")
        custody = CustodiaMascota.objects.select_related("usuario_registrador", "fundacion__entidad").get(mascota=pet, fecha_fin__isnull=True)
        if not custody.usuario_registrador.email.endswith("@example.invalid") or not any(word in custody.fundacion.entidad.nombre.lower() for word in ("demo", "qa")):
            raise CommandError("La custodia base debe pertenecer al escenario sintético.")
        ids = []
        for index in range(27):
            obj = Mascota.objects.create(nombre=f"QA Pagina {index:02}", descripcion_especie="QA Paginacion", estado_mascota=pet.estado_mascota)
            CustodiaMascota.objects.create(mascota=obj, fundacion=custody.fundacion, usuario_registrador=custody.usuario_registrador, fecha_inicio=timezone.now())
            ids.append(obj.pk)
        manifest.write_text(json.dumps({"ids": ids}), encoding="utf8")
        self.stdout.write("27 fichas temporales de paginación preparadas en QA.")
