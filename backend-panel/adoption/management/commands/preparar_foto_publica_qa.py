"""Patrón sintético de imagen para el ensayo Android, nunca fotos reales."""
from io import BytesIO
from pathlib import Path
import hashlib
import json
import tempfile
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from animals.models import Mascota, CustodiaMascota, FotoPublicaMascota
from animals.public_photos import publicar, retirar
from core.models import EntidadMiembroRol, Fundacion, ValorMaestro
from seguridad.autorizacion import puede


class Command(BaseCommand):
    help = "Prepara un patrón QA de fotografía pública; --limpiar lo retira."

    def add_arguments(self, parser):
        parser.add_argument("--limpiar", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        db = settings.DATABASES["default"]
        if not (settings.DEBUG and db["HOST"] == "127.0.0.1" and db["NAME"] == "lpn_panel_qa_29"):
            raise CommandError("Usa exclusivamente config.settings_qa y su MySQL local aislado.")
        namespace = hashlib.sha256(str(settings.BASE_DIR).encode()).hexdigest()[:12]
        manifest = Path(tempfile.gettempdir()) / f"lpn-photo-qa-{namespace}.json"
        if options["limpiar"]:
            if not manifest.exists():
                raise CommandError("No hay manifiesto de esta prueba; no se elimina ninguna ficha.")
            data = json.loads(manifest.read_text(encoding="utf8"))
            pet = Mascota.objects.filter(pk=data["pet"], nombre="QA Foto Publica", descripcion_especie="QA Foto", dueno__isnull=True).first()
            photo = FotoPublicaMascota.objects.select_related("publicador").filter(mascota=pet).first() if pet else None
            if photo is None or photo.publicador_id != data["actor"]:
                raise CommandError("La ficha temporal cambió; revisa el escenario antes de retirarlo.")
            retirar(photo.publicador, pet.pk)
            photo.delete()
            CustodiaMascota.objects.filter(mascota=pet).delete()
            pet.delete()
            transaction.on_commit(lambda: manifest.unlink())
            self.stdout.write("Patrón y ficha temporal de foto retirados de QA.")
            return
        if manifest.exists() or Mascota.objects.filter(nombre="QA Foto Publica").exists():
            raise CommandError("Ya hay una prueba de foto pendiente de retirar.")
        candidates = EntidadMiembroRol.objects.filter(rol__codigo="GESTOR_ADOPCIONES", fecha_revocacion__isnull=True, miembro__fecha_salida__isnull=True, miembro__usuario__email__endswith="@example.invalid").select_related("miembro__usuario", "miembro__entidad")
        actor = foundation = None
        for role in candidates:
            entity = role.miembro.entidad
            found = Fundacion.objects.filter(pk=entity.pk, entidad__estado_verificacion__nombre="Verificada").first()
            if found and puede(role.miembro.usuario, "mascotas.publicar_adopcion", entidad_id=entity.pk):
                actor, foundation = role.miembro.usuario, found
                break
        if actor is None:
            raise CommandError("Prepara antes un gestor sintético autorizado en una fundación QA.")
        pet = Mascota.objects.create(nombre="QA Foto Publica", descripcion_especie="QA Foto", estado_mascota=ValorMaestro.objects.get(tipo__nombre="estado_mascota", nombre="En adopción"))
        CustodiaMascota.objects.create(mascota=pet, fundacion=foundation, usuario_registrador=actor, fecha_inicio=timezone.now())
        pixels = Image.new("RGB", (1000, 700), "#fcf0d3")
        draw = ImageDraw.Draw(pixels)
        for index, color in enumerate(["#425a36", "#dbb492", "#b2c4a5", "#e8d4ab"]):
            draw.rectangle((index * 250, 420, (index + 1) * 250, 700), fill=color)
        draw.text((70, 100), "PRUEBA QA", font=ImageFont.load_default(size=64), fill="#423222")
        draw.text((70, 210), "IMAGEN SINTETICA", font=ImageFont.load_default(size=42), fill="#423222")
        data = BytesIO()
        pixels.save(data, format="PNG")
        photo = publicar(actor, pet.pk, SimpleUploadedFile("patron-qa.png", data.getvalue(), content_type="image/png"), True)
        try:
            manifest.write_text(json.dumps({"pet": pet.pk, "actor": actor.pk}), encoding="utf8")
        except Exception:
            from animals.public_photos import borrar_obsoleto
            borrar_obsoleto(photo.clave)
            raise
        self.stdout.write("Patrón sintético y ficha de foto preparados en QA, sin usuarios ni permisos nuevos.")
