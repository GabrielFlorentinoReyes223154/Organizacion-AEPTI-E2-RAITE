"""Correos de cuentas con versión HTML y de texto plano (RF-01).

El logo va como enlace público si hay `CORREO_LOGO_URL` (necesario con la API de Brevo). Si no, va
adjunto como imagen relacionada (CID), porque Gmail no muestra SVG ni imágenes en data URI.
"""

from functools import cache
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

LOGO = Path(__file__).resolve().parent / "recursos" / "logo-raite.png"
CID_LOGO = "logo-raite@raite"


@cache
def _logo() -> bytes:
    return LOGO.read_bytes()


class CorreoConImagenes(EmailMultiAlternatives):
    """Correo cuyo HTML lleva imágenes incrustadas con CID.

    Las imágenes se agregan como `multipart/related` junto al HTML (no como adjuntos sueltos),
    para que Gmail y Outlook las muestren dentro del correo y no al final como archivos.
    """

    def __init__(self, *args, imagenes=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.imagenes = list(imagenes)  # [(cid, bytes, nombre de archivo)]

    def message(self, *args, **kwargs):
        msg = super().message(*args, **kwargs)
        if self.imagenes:
            html = next(p for p in msg.walk() if p.get_content_type() == "text/html")
            for cid, datos, nombre in self.imagenes:
                html.add_related(
                    datos,
                    maintype="image",
                    subtype="png",
                    cid=f"<{cid}>",
                    disposition="inline",
                    filename=nombre,
                )
        return msg


def correo_codigo(usuario, codigo: str) -> CorreoConImagenes:
    """Correo con el código de verificación; se usa al registrarse y al pedir otro código."""
    contexto = {
        "nombre": usuario.nombre,
        "codigo": codigo,
        "minutos": settings.CODIGO_VERIFICACION_MINUTOS,
        "logo_src": settings.CORREO_LOGO_URL or f"cid:{CID_LOGO}",
    }
    correo = CorreoConImagenes(
        subject=f"Tu código de Raite: {codigo}",
        body=render_to_string("accounts/correo/codigo_verificacion.txt", contexto),
        to=[usuario.correo],
        imagenes=[] if settings.CORREO_LOGO_URL else [(CID_LOGO, _logo(), "raite.png")],
    )
    correo.attach_alternative(
        render_to_string("accounts/correo/codigo_verificacion.html", contexto), "text/html"
    )
    return correo
