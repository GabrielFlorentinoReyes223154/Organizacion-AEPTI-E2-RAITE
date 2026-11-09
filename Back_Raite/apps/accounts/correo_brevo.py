"""Envío de correos por la API HTTP de Brevo.

Render gratuito bloquea los puertos SMTP (25, 465 y 587); esta API usa HTTPS (443).
Se activa con `EMAIL_BACKEND=apps.accounts.correo_brevo.BrevoEmailBackend` y `BREVO_API_KEY`.
"""

import json
import logging
import urllib.error
import urllib.request
from email.utils import parseaddr

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)

URL_BREVO = "https://api.brevo.com/v3/smtp/email"


class ErrorBrevo(Exception):
    """Brevo rechazó el correo o no se pudo hablar con su API."""


def _contacto(direccion: str) -> dict:
    nombre, correo = parseaddr(direccion)
    return {"name": nombre, "email": correo} if nombre else {"email": correo}


def _datos(mensaje) -> dict:
    datos = {
        "sender": _contacto(mensaje.from_email or settings.DEFAULT_FROM_EMAIL),
        "to": [_contacto(d) for d in mensaje.to],
        "subject": mensaje.subject,
        "textContent": mensaje.body,
    }
    if mensaje.cc:
        datos["cc"] = [_contacto(d) for d in mensaje.cc]
    if mensaje.bcc:
        datos["bcc"] = [_contacto(d) for d in mensaje.bcc]
    if mensaje.reply_to:
        datos["replyTo"] = _contacto(mensaje.reply_to[0])
    for contenido, tipo in getattr(mensaje, "alternatives", []):
        if tipo == "text/html":
            datos["htmlContent"] = contenido
    return datos


class BrevoEmailBackend(BaseEmailBackend):
    def _enviar(self, mensaje) -> None:
        clave = settings.BREVO_API_KEY
        if not clave:
            raise ImproperlyConfigured("Falta la variable de entorno BREVO_API_KEY.")
        peticion = urllib.request.Request(
            URL_BREVO,
            data=json.dumps(_datos(mensaje)).encode(),
            headers={
                "accept": "application/json",
                "api-key": clave,
                "content-type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(peticion, timeout=settings.EMAIL_TIMEOUT):
                pass
        except urllib.error.HTTPError as error:
            detalle = error.read().decode(errors="replace")
            # Queda en los logs del servidor: es lo que dice por qué Brevo no lo envió.
            logger.error("Brevo rechazó el correo (%s): %s", error.code, detalle)
            raise ErrorBrevo(f"Brevo respondió {error.code}") from error
        except OSError as error:
            logger.error("No se pudo conectar con Brevo: %s", error)
            raise ErrorBrevo("No se pudo conectar con Brevo") from error

    def send_messages(self, email_messages):
        enviados = 0
        for mensaje in email_messages:
            if not mensaje.recipients():
                continue
            try:
                self._enviar(mensaje)
            except (ErrorBrevo, ImproperlyConfigured):
                if not self.fail_silently:
                    raise
            else:
                enviados += 1
        return enviados
