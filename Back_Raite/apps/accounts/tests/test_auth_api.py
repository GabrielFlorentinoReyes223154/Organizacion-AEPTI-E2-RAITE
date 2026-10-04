from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.accounts.models import Rol, Sexo


class AuthAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            correo="test@uacj.mx",
            password="password123",
            nombre="Test",
            apellidos="User",
            edad=20,
            sexo=Sexo.F,
            carrera="Ingeniería",
            roles=[Rol.PASAJERO],
        )

    def test_obtener_token_login_valido(self):
        response = self.client.post(
            "/api/auth/token/",
            {"correo": "test@uacj.mx", "password": "password123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_contraseña_incorrecta(self):
        response = self.client.post(
            "/api/auth/token/",
            {"correo": "test@uacj.mx", "password": "wrongpassword"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_campo_email_rechazado(self):
        response = self.client.post(
            "/api/auth/token/",
            {"email": "test@uacj.mx", "password": "password123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_me_endpoint_autenticado(self):
        response = self.client.post(
            "/api/auth/token/",
            {"correo": "test@uacj.mx", "password": "password123"},
            format="json",
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["correo"], "test@uacj.mx")
        self.assertEqual(response.data["nombre"], "Test")
        self.assertEqual(response.data["apellidos"], "User")
        self.assertIn("nombre_completo", response.data)
        self.assertIn("roles", response.data)
        self.assertNotIn("password", response.data)
        self.assertNotIn("is_superuser", response.data)

    def test_me_endpoint_sin_token(self):
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_blacklist_refresh_token(self):
        response = self.client.post(
            "/api/auth/token/",
            {"correo": "test@uacj.mx", "password": "password123"},
            format="json",
        )
        refresh = response.data["refresh"]
        response = self.client.post(
            "/api/auth/token/blacklist/",
            {"refresh": refresh},
            format="json",
        )
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_205_RESET_CONTENT])
        response = self.client.post(
            "/api/auth/token/refresh/",
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Tests nuevos para C10
    def test_registro_crea_dos_filas_para_ambos(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "nombre": "Ambos",
                "apellidos": "Test",
                "correo": "ambos@uacj.mx",
                "password": "password123",
                "edad": 20,
                "sexo": "M",
                "carrera": "Ingeniería",
                "roles": ["PASAJERO", "CONDUCTOR"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = self.User.objects.get(correo="ambos@uacj.mx")
        self.assertEqual(user.usuario_roles.count(), 2)
        self.assertTrue(user.es_pasajero)
        self.assertTrue(user.es_conductor)

    def test_registro_rechaza_admin(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "nombre": "Admin",
                "apellidos": "Test",
                "correo": "admin@uacj.mx",
                "password": "password123",
                "edad": 20,
                "sexo": "M",
                "carrera": "Ingeniería",
                "roles": ["ADMIN"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registro_rechaza_roles_duplicados(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "nombre": "Dup",
                "apellidos": "Test",
                "correo": "dup@uacj.mx",
                "password": "password123",
                "edad": 20,
                "sexo": "M",
                "carrera": "Ingeniería",
                "roles": ["PASAJERO", "PASAJERO"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registro_devuelve_requiere_vehiculo(self):
        # Con CONDUCTOR
        response = self.client.post(
            "/api/auth/register/",
            {
                "nombre": "Conductor",
                "apellidos": "Test",
                "correo": "conductor@uacj.mx",
                "password": "password123",
                "edad": 20,
                "sexo": "M",
                "carrera": "Ingeniería",
                "roles": ["CONDUCTOR"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["requiere_vehiculo"])

        # Sin CONDUCTOR
        response = self.client.post(
            "/api/auth/register/",
            {
                "nombre": "Pasajero",
                "apellidos": "Test",
                "correo": "pasajero@uacj.mx",
                "password": "password123",
                "edad": 20,
                "sexo": "F",
                "carrera": "Ingeniería",
                "roles": ["PASAJERO"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data["requiere_vehiculo"])