"""Pantalla de fotografía: misma autorización y servicio que las API."""
from django import forms
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException
from animals.models import FotoPublicaMascota, FotoGaleriaMascota
from animals import public_photos
from animals.photo_views import FotoPublicaThrottle
from adoption.consultas import disponibles_adopcion
from seguridad.i18n import traducir_formulario, texto_error
from .views import protegido


class FotoForm(forms.Form):
    adicional = forms.BooleanField(required=False, label=_("Añadir a la galería sin reemplazar la portada (máximo cinco adicionales)."))
    archivo = forms.FileField(label=_("Fotografía"), widget=forms.FileInput(attrs={"accept": "image/jpeg,image/png,image/webp", "aria-describedby": "foto-ayuda", "data-photo-file": ""}))
    confirmar_publicacion = forms.BooleanField(label=_("Tengo autorización para publicar esta fotografía y he revisado que no exponga datos personales."))


class RetirarForm(forms.Form):
    confirmar_retirada = forms.BooleanField(label=_("Confirmo que quiero retirar la fotografía del catálogo público."))


@protegido
@csrf_protect
@require_http_methods(["GET", "POST"])
def fotografia(request, mascota_id):
    pet, custody = public_photos.custodia_autorizada(request.user, mascota_id, bloquear=False)
    mode = request.GET.get("modo", "publicar")
    if mode not in {"publicar", "retirar"}:
        from django.http import Http404
        raise Http404
    extra_id = request.GET.get("foto_id")
    if extra_id is not None and not extra_id.isdecimal():
        from django.http import Http404
        raise Http404
    extra_id = int(extra_id) if extra_id is not None else None
    photo = FotoGaleriaMascota.objects.filter(mascota=pet, pk=extra_id).first() if extra_id is not None else FotoPublicaMascota.objects.filter(mascota=pet).first()
    can_publish = disponibles_adopcion().filter(pk=pet.pk).exists()
    if mode == "retirar" and not (photo and photo.publicada):
        return redirect("panel:foto_mascota", mascota_id=pet.pk)
    cls = RetirarForm if mode == "retirar" else FotoForm
    form = cls(request.POST if request.method == "POST" else None, request.FILES if request.method == "POST" else None)
    status = 200
    if request.method == "POST":
        if not form.is_valid():
            status = 400
        else:
            try:
                if mode == "retirar":
                    public_photos.retirar(request.user, pet.pk, foto_id=extra_id)
                    messages.success(request, _("Fotografía retirada del catálogo público."))
                else:
                    limiter = FotoPublicaThrottle()
                    if not limiter.allow_request(request, None):
                        from rest_framework.exceptions import Throttled
                        raise Throttled(wait=limiter.wait())
                    public_photos.publicar(request.user, pet.pk, form.cleaned_data["archivo"], form.cleaned_data["confirmar_publicacion"], adicional=form.cleaned_data["adicional"])
                    messages.success(request, _("Fotografía publicada. Ya está disponible en el catálogo y la app."))
                return redirect("panel:foto_mascota", mascota_id=pet.pk)
            except APIException as exc:
                if exc.status_code in (401, 403):
                    raise
                form.add_error(None, texto_error(exc.detail))
                status = exc.status_code
    descriptor = public_photos.foto_descriptor(pet, custody.fundacion_id) if can_publish else None
    actual = next((item for item in request.panel["modulos"] if item["codigo"] == "mascotas"), None)
    recurso_nombre = _(actual["nombre"] if actual else "Mascotas")
    context = {**request.panel, "actual": actual, "volver_fotos_label": _("Volver a %(recurso)s") % {"recurso": recurso_nombre}, "mascota_foto": pet, "fundacion_foto": custody.fundacion.entidad.nombre,
               "foto_actual": descriptor, "tiene_publicacion": bool(photo and photo.publicada), "puede_publicar_foto": can_publish,
               "modo_foto": mode, "form_foto": traducir_formulario(form), "volver_fotos": reverse("panel:area", args=["mascotas"]) + "?vista=gestion"}
    context["galeria_fotos"] = [{"id": photo.pk, "url": f"/api/adopcion/mascotas/{pet.pk}/fotos/{photo.pk}/", "ancho": photo.ancho, "alto": photo.alto}
                                for photo in FotoGaleriaMascota.objects.filter(mascota=pet, fundacion=custody.fundacion, publicada=True).order_by("pk")[:5]] if can_publish else []
    return render(request, "seguridad/web/foto_mascota.html", context, status=status)
