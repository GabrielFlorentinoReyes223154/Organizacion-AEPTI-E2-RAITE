"""Envío por la API de Brevo (sin llamar a la red) y logo del correo."""

import io
import json
import urllib.error
from unittest.mock import MagicMock, patch

from django.core.mail import EmailMultiAlternatives, get_connection
from django.test import SimpleTestCase, override_settings

from apps.accounts.correo_brevo import ErrorBrevo
from apps.accounts.correos import correo_codigo

BACKEND = "apps.accounts.correo_brevo.BrevoEmailBackend"
URLOPEN = "apps.accounts.correo_brevo.urllib.request.urlopen"


def mensaje():
    correo = EmailMultiAlternatives(
        subject="Tu código",
        body="Texto plano",
        from_email="Raite <no-reply@raite.online>",
        to=["ana@alumnos.uacj.mx"],
    )
    correo.attach_alternative("<p>HTML</p>", "text/html")
    return correo


def http_error(codigo, cuerpo):
    return urllib.error.HTTPError("url", codigo, "error", {}, io.BytesIO(cuerpo))


@override_settings(BREVO_API_KEY="clave-de-prueba", EMAIL_TIMEOUT=7)
class BrevoEmailBackendTests(SimpleTestCase):
    @patch(URLOPEN)
    def test_manda_el_correo_a_la_api(self, urlopen):
        urlopen.return_value = MagicMock()

        enviados = get_connection(BACKEND).send_messages([mensaje()])

        self.assertEqual(enviados, 1)
        peticion = urlopen.call_args.args[0]
        self.assertEqual(peticion.full_url, "https://api.brevo.com/v3/smtp/email")
        self.assertEqual(peticion.get_header("Api-key"), "clave-de-prueba")
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 7)
        self.assertEqual(
            json.loads(peticion.data),
            {
                "sender": {"name": "Raite", "email": "no-reply@raite.online"},
                "to": [{"email": "ana@alumnos.uacj.mx"}],
                "subject": "Tu código",
                "textContent": "Texto plano",
                "htmlContent": "<p>HTML</p>",
            },
        )

    @patch(URLOPEN)
    def test_si_brevo_rechaza_lanza_error(self, urlopen):
        urlopen.side_effect = http_error(401, b'{"code":"unauthorized"}')

        with self.assertLogs("apps.accounts.correo_brevo", level="ERROR") as registros:
            with self.assertRaises(ErrorBrevo):
                get_connection(BACKEND).send_messages([mensaje()])
        self.assertIn("unauthorized", registros.output[0])

    @patch(URLOPEN)
    def test_si_no_hay_conexion_lanza_error(self, urlopen):
        urlopen.side_effect = TimeoutError()

        with self.assertLogs("apps.accounts.correo_brevo", level="ERROR"):
            with self.assertRaises(ErrorBrevo):
                get_connection(BACKEND).send_messages([mensaje()])

    @patch(URLOPEN)
    def test_fail_silently_no_lanza(self, urlopen):
        urlopen.side_effect = TimeoutError()

        with self.assertLogs("apps.accounts.correo_brevo", level="ERROR"):
            enviados = get_connection(BACKEND, fail_silently=True).send_messages([mensaje()])
        self.assertEqual(enviados, 0)


class LogoDelCorreoTests(SimpleTestCase):
    usuario = MagicMock(nombre="Ana", correo="ana@alumnos.uacj.mx")

    @override_settings(CORREO_LOGO_URL="https://www.raite.online/correo/logo-raite.png")
    def test_con_url_usa_el_enlace_y_no_incrusta(self):
        correo = correo_codigo(self.usuario, "123456")
        html = correo.alternatives[0][0]
        self.assertIn('src="https://www.raite.online/correo/logo-raite.png"', html)
        self.assertEqual(correo.imagenes, [])

    @override_settings(CORREO_LOGO_URL="")
    def test_sin_url_incrusta_el_logo(self):
        correo = correo_codigo(self.usuario, "123456")
        self.assertIn('src="cid:logo-raite@raite"', correo.alternatives[0][0])
        self.assertEqual(len(correo.imagenes), 1)
