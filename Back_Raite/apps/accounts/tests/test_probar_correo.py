from io import StringIO

from django.core import mail
from django.core.management import call_command
from django.test import TestCase

from apps.accounts.models import CodigoVerificacion, Usuario


class ProbarCorreoTests(TestCase):
    def test_manda_la_muestra_a_cada_correo_sin_tocar_la_bd(self):
        salida = StringIO()
        call_command("probar_correo", "a@alumnos.uacj.mx", "b@gmail.com", "--nombre", "Gabriel", stdout=salida)
        self.assertEqual([c.to for c in mail.outbox], [["a@alumnos.uacj.mx"], ["b@gmail.com"]])
        self.assertTrue(mail.outbox[0].subject.startswith("Tu código de Raite: "))
        self.assertIn("Hola, Gabriel.", mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].alternatives[0].mimetype, "text/html")
        self.assertFalse(Usuario.objects.exists())
        self.assertFalse(CodigoVerificacion.objects.exists())
