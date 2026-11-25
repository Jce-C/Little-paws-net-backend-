"""Normalización compartida de copias públicas; no guarda originales."""
from io import BytesIO
import warnings
from PIL import Image, ImageOps, UnidentifiedImageError
from rest_framework.exceptions import APIException, ValidationError

MAX_INPUT = 5 * 1024 * 1024
MAX_OUTPUT = 512 * 1024


class StorageUnavailable(APIException):
    status_code = 503
    default_detail = "El almacenamiento de fotografías no está disponible. Intenta de nuevo más tarde."

def normalizar(archivo, *, max_side=1280, max_output=MAX_OUTPUT):
    if not archivo or not 0 < archivo.size <= MAX_INPUT:
        raise ValidationError("La fotografía debe ocupar entre 1 byte y 5 MB.")
    data = archivo.read(MAX_INPUT + 1)
    if len(data) > MAX_INPUT:
        raise ValidationError("La fotografía supera los 5 MB.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(data), formats=["JPEG", "PNG", "WEBP"]) as image:
                if image.width * image.height > 16_000_000 or max(image.size) > 6000 or getattr(image, "n_frames", 1) != 1:
                    raise ValidationError("Usa una imagen fija de hasta 16 megapíxeles y 6000 px por lado.")
                image.verify()
            with Image.open(BytesIO(data), formats=["JPEG", "PNG", "WEBP"]) as image:
                pixels = ImageOps.exif_transpose(image).convert("RGBA")
                pixels.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
                clean = Image.new("RGB", pixels.size, (255, 249, 236))
                clean.paste(pixels, mask=pixels.getchannel("A"))
                for quality in (80, 65, 50):
                    output = BytesIO()
                    clean.save(output, format="WEBP", quality=quality, method=4, exif=b"", icc_profile=None, xmp=b"")
                    result = output.getvalue()
                    if len(result) <= max_output:
                        return result, clean.width, clean.height
        raise ValidationError(f"No pudimos optimizar la imagen a {max_output // 1024} KB. Utiliza otra imagen.")
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ValidationError("Usa una imagen JPEG, PNG o WebP válida y sin animación.") from exc
