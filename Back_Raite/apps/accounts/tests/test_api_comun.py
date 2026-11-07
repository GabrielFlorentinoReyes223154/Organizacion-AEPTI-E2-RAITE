"""Piezas comunes del API: manejador de errores y permisos por defecto."""

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase
from rest_framework import status

from apps.accounts.tests.factories import cliente_para, crear_usuario
from Raite_DjangoRest.api import manejar_excepcion


class ManejadorDeErroresTests(SimpleTestCase):
    def test_validation_error_de_django_con_campos_es_400(self):
        respuesta = manejar_excepcion(ValidationError({"correo": "Malo.", "__all__": "General."}), {})
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(respuesta.data["correo"], ["Malo."])
        self.assertEqual(respuesta.data["non_field_errors"], ["General."])

    def test_validation_error_de_django_sin_campos_es_400(self):
        respuesta = manejar_excepcion(ValidationError("Algo falló."), {})
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(respuesta.data["non_field_errors"], ["Algo falló."])


class PermisosPorDefectoTests(TestCase):
    def test_sin_sesion_es_401(self):
        self.assertEqual(cliente_para().get("/api/auth/me/").status_code, status.HTTP_401_UNAUTHORIZED)

    def test_correo_sin_verificar_es_403(self):
        usuario = crear_usuario(correo_verificado=False)
        respuesta = cliente_para(usuario).get("/api/auth/me/")
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Verifica tu correo", str(respuesta.data["detail"]))

    def test_correo_verificado_pasa(self):
        self.assertEqual(cliente_para(crear_usuario()).get("/api/auth/me/").status_code, status.HTTP_200_OK)
