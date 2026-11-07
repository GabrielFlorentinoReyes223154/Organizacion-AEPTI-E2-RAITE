"""Manda una muestra del correo del código de verificación para revisarlo en un buzón real.

No crea usuarios ni códigos: el código es de ejemplo y no activa ninguna cuenta.
"""

import secrets
from types import SimpleNamespace

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.accounts.correos import correo_codigo


class Command(BaseCommand):
    help = "Manda una prueba del correo del código de verificación a uno o más correos."

    def add_arguments(self, parser):
        parser.add_argument("correos", nargs="+", help="Correos que reciben la prueba.")
        parser.add_argument("--nombre", default="Prueba", help="Nombre del saludo (por defecto: Prueba).")

    def handle(self, *args, **opciones):
        codigo = f"{secrets.randbelow(10**6):06d}"
        for correo in opciones["correos"]:
            usuario = SimpleNamespace(nombre=opciones["nombre"], correo=correo)
            correo_codigo(usuario, codigo).send()
            self.stdout.write(f"Enviado a {correo}")
        self.stdout.write(
            self.style.SUCCESS(f"Código de muestra {codigo} · backend: {settings.EMAIL_BACKEND}")
        )
