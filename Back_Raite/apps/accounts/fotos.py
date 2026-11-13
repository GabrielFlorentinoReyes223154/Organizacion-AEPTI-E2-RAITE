"""Revisión y reducción de la foto de perfil con Pillow.

Se revisa el contenido real del archivo (no su nombre ni el tipo que dice el navegador), se
endereza según el EXIF y se vuelve a guardar como WebP sin metadatos (así se pierde también la
ubicación GPS que traen muchas fotos del celular).
"""

from io import BytesIO

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image, ImageOps

FORMATOS_PERMITIDOS = {"JPEG", "PNG", "WEBP"}
MAX_MEGAPIXELES = 40
CALIDAD_WEBP = 82

MENSAJE_FORMATO = "Sube una imagen JPG, PNG o WebP."


def _error(mensaje: str) -> ValidationError:
    return ValidationError({"foto": mensaje})


def procesar_foto(archivo) -> ContentFile:
    """Devuelve la foto lista para guardar: WebP de FOTO_MAX_PX de lado como máximo."""
    if archivo is None:
        raise _error("Elige una foto.")
    if archivo.size > settings.FOTO_MAX_MB * 1024 * 1024:
        raise _error(f"La foto pesa más de {settings.FOTO_MAX_MB} MB. Elige una más ligera.")

    try:
        archivo.seek(0)
        with Image.open(archivo) as imagen:
            formato = imagen.format
            ancho, alto = imagen.size
            imagen.verify()  # detecta archivos dañados o que no son imagen
        if formato not in FORMATOS_PERMITIDOS:
            raise _error(MENSAJE_FORMATO)
        if ancho * alto > MAX_MEGAPIXELES * 1_000_000:
            raise _error("La imagen es demasiado grande. Usa una de menos de 40 megapíxeles.")

        archivo.seek(0)  # verify() deja la imagen inservible: se abre otra vez
        with Image.open(archivo) as imagen:
            imagen = ImageOps.exif_transpose(imagen)
            con_transparencia = imagen.mode in ("RGBA", "LA", "PA") or "transparency" in imagen.info
            imagen = imagen.convert("RGBA" if con_transparencia else "RGB")
            imagen.thumbnail((settings.FOTO_MAX_PX, settings.FOTO_MAX_PX), Image.Resampling.LANCZOS)
            salida = BytesIO()
            imagen.save(salida, format="WEBP", quality=CALIDAD_WEBP, method=6)
    except ValidationError:
        raise
    except (OSError, SyntaxError, ValueError, Image.DecompressionBombError) as error:
        raise _error(MENSAJE_FORMATO) from error

    return ContentFile(salida.getvalue(), name="foto.webp")
