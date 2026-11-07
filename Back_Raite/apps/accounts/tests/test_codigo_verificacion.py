from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone

from apps.accounts.models import CodigoVerificacion
from apps.accounts.tests.factories import crear_usuario


class CodigoVerificacionTests(TestCase):
    def setUp(self):
        self.usuario = crear_usuario(correo_verificado=False)

    def test_genera_codigo_de_6_digitos(self):
        _, codigo = CodigoVerificacion.generar(self.usuario)
        self.assertEqual(len(codigo), 6)
        self.assertTrue(codigo.isdigit())

    def test_codigo_se_guarda_con_hash(self):
        registro, codigo = CodigoVerificacion.generar(self.usuario)
        self.assertNotEqual(registro.codigo_hash, codigo)
        self.assertNotIn(codigo, registro.codigo_hash)

    @override_settings(CODIGO_VERIFICACION_MINUTOS=15)
    def test_expira_en_los_minutos_configurados(self):
        antes = timezone.now()
        registro, _ = CodigoVerificacion.generar(self.usuario)
        self.assertAlmostEqual(
            (registro.expira_en - antes).total_seconds(), 15 * 60, delta=5
        )

    def test_codigo_correcto(self):
        registro, codigo = CodigoVerificacion.generar(self.usuario)
        self.assertTrue(registro.comprobar(codigo))
        registro.refresh_from_db()
        self.assertEqual(registro.intentos, 1)

    def test_codigo_incorrecto(self):
        registro, codigo = CodigoVerificacion.generar(self.usuario)
        incorrecto = "000000" if codigo != "000000" else "111111"
        self.assertFalse(registro.comprobar(incorrecto))
        registro.refresh_from_db()
        self.assertEqual(registro.intentos, 1)

    def test_codigo_expirado(self):
        registro, codigo = CodigoVerificacion.generar(self.usuario)
        registro.expira_en = timezone.now() - timedelta(seconds=1)
        registro.save()
        self.assertFalse(registro.esta_vigente())
        self.assertFalse(registro.comprobar(codigo))

    def test_codigo_usado(self):
        registro, codigo = CodigoVerificacion.generar(self.usuario)
        registro.usado = True
        registro.save()
        self.assertFalse(registro.comprobar(codigo))

    @override_settings(CODIGO_VERIFICACION_MAX_INTENTOS=3)
    def test_intentos_agotados(self):
        registro, codigo = CodigoVerificacion.generar(self.usuario)
        for _ in range(3):
            registro.comprobar("no-es")
        self.assertTrue(registro.intentos_agotados())
        self.assertFalse(registro.comprobar(codigo))
        registro.refresh_from_db()
        self.assertEqual(registro.intentos, 3)  # ya no suma intentos

    def test_se_borran_con_el_usuario(self):
        CodigoVerificacion.generar(self.usuario)
        self.usuario.delete()
        self.assertEqual(CodigoVerificacion.objects.count(), 0)
