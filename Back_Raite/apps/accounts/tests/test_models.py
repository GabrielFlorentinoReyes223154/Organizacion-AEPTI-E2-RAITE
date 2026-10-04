from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from apps.accounts.models import Rol, Sexo, Usuario


class UsuarioModelTests(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_crear_usuario_con_datos_validos(self):
        user = self.User.objects.create_user(
            correo="test@uacj.mx",
            password="password123",
            nombre="Juan",
            apellidos="Pérez",
            edad=20,
            sexo=Sexo.M,
            carrera="Ingeniería",
            roles=[Rol.PASAJERO],
        )
        self.assertEqual(user.correo, "test@uacj.mx")
        self.assertEqual(user.nombre, "Juan")
        self.assertEqual(user.apellidos, "Pérez")
        self.assertEqual(user.edad, 20)
        self.assertEqual(user.sexo, Sexo.M)
        self.assertEqual(user.carrera, "Ingeniería")
        self.assertTrue(user.es_pasajero)
        self.assertFalse(user.es_conductor)
        self.assertEqual(user.cuenta_activa, 0)  # IntegerField default=0 (no Raite activo)
        self.assertFalse(user.activo)
        self.assertFalse(user.suspendido)
        self.assertEqual(user.calificacion, Decimal("0.00"))

    def test_edad_fuera_de_rango_falla(self):
        with self.assertRaises(Exception):
            self.User.objects.create_user(
                correo="edad_menor@uacj.mx",
                password="password123",
                nombre="Menor",
                apellidos="Test",
                edad=16,
                sexo=Sexo.F,
                carrera="Ingeniería",
            )
        with self.assertRaises(Exception):
            self.User.objects.create_user(
                correo="edad_mayor@uacj.mx",
                password="password123",
                nombre="Mayor",
                apellidos="Test",
                edad=71,
                sexo=Sexo.F,
                carrera="Ingeniería",
            )

    def test_edad_en_limites_funciona(self):
        user_min = self.User.objects.create_user(
            correo="edad_17@uacj.mx",
            password="password123",
            nombre="Edad17",
            apellidos="Test",
            edad=17,
            sexo=Sexo.M,
            carrera="Ingeniería",
        )
        self.assertEqual(user_min.edad, 17)

        user_max = self.User.objects.create_user(
            correo="edad_70@uacj.mx",
            password="password123",
            nombre="Edad70",
            apellidos="Test",
            edad=70,
            sexo=Sexo.M,
            carrera="Ingeniería",
        )
        self.assertEqual(user_max.edad, 70)

    def test_correo_unico(self):
        self.User.objects.create_user(
            correo="duplicado@uacj.mx",
            password="password123",
            nombre="Uno",
            apellidos="Test",
            edad=20,
            sexo=Sexo.M,
            carrera="Ingeniería",
        )
        with self.assertRaises(IntegrityError):
            self.User.objects.create_user(
                correo="duplicado@uacj.mx",
                password="password456",
                nombre="Dos",
                apellidos="Test",
                edad=20,
                sexo=Sexo.F,
                carrera="Medicina",
            )

    def test_es_pasajero_es_conductor(self):
        user_pasajero = self.User.objects.create_user(
            correo="pasajero@uacj.mx",
            password="password123",
            nombre="Pasajero",
            apellidos="Test",
            edad=20,
            sexo=Sexo.F,
            carrera="Ingeniería",
            roles=[Rol.PASAJERO],
        )
        user_conductor = self.User.objects.create_user(
            correo="conductor@uacj.mx",
            password="password123",
            nombre="Conductor",
            apellidos="Test",
            edad=22,
            sexo=Sexo.M,
            carrera="Ingeniería",
            roles=[Rol.CONDUCTOR],
        )
        user_ambos = self.User.objects.create_user(
            correo="ambos@uacj.mx",
            password="password123",
            nombre="Ambos",
            apellidos="Test",
            edad=21,
            sexo=Sexo.X,
            carrera="Ingeniería",
            roles=[Rol.PASAJERO, Rol.CONDUCTOR],
        )
        self.assertTrue(user_pasajero.es_pasajero)
        self.assertFalse(user_pasajero.es_conductor)
        self.assertFalse(user_conductor.es_pasajero)
        self.assertTrue(user_conductor.es_conductor)
        self.assertTrue(user_ambos.es_pasajero)
        self.assertTrue(user_ambos.es_conductor)

    def test_nombre_completo(self):
        user = self.User.objects.create_user(
            correo="nombre@uacj.mx",
            password="password123",
            nombre="Ana",
            apellidos="López",
            edad=19,
            sexo=Sexo.F,
            carrera="Derecho",
        )
        self.assertEqual(user.nombre_completo, "Ana López")

    def test_puede_crear_raite(self):
        user = self.User.objects.create_user(
            correo="crear@uacj.mx",
            password="password123",
            nombre="Crea",
            apellidos="Raite",
            edad=20,
            sexo=Sexo.F,
            carrera="Ingeniería",
            roles=[Rol.PASAJERO],
        )
        self.assertTrue(user.puede_crear_raite())
        user.cuenta_activa = 1  # Tiene un Raite activo
        user.save()
        self.assertFalse(user.puede_crear_raite())
        user.cuenta_activa = 0
        user.suspendido = True
        user.save()
        self.assertFalse(user.puede_crear_raite())

    def test_puede_aceptar_raite(self):
        user = self.User.objects.create_user(
            correo="aceptar@uacj.mx",
            password="password123",
            nombre="Acepta",
            apellidos="Raite",
            edad=22,
            sexo=Sexo.M,
            carrera="Ingeniería",
            roles=[Rol.CONDUCTOR],
        )
        self.assertFalse(user.puede_aceptar_raite())
        # Crear vehículo real (sin PerfilConductor)
        from apps.accounts.models import Vehiculo
        vehiculo = Vehiculo.objects.create(
            usuario=user,
            marca="Toyota",
            modelo="Corolla",
            color="Blanco",
            placas="ABC1234",
            tipo="COCHE",
            asientos_disponibles=4,
            activo=True,
        )
        self.assertTrue(user.puede_aceptar_raite())
        user.cuenta_activa = 1  # Tiene un Raite activo
        user.save()
        self.assertFalse(user.puede_aceptar_raite())

    def test_authenticate_por_correo(self):
        self.User.objects.create_user(
            correo="auth@uacj.mx",
            password="password123",
            nombre="Auth",
            apellidos="Test",
            edad=20,
            sexo=Sexo.M,
            carrera="Ingeniería",
        )
        from django.contrib.auth import authenticate
        user = authenticate(request=None, correo="auth@uacj.mx", password="password123")
        self.assertIsNotNone(user)
        self.assertEqual(user.correo, "auth@uacj.mx")
        user_fail = authenticate(request=None, correo="auth@uacj.mx", password="wrong")
        self.assertIsNone(user_fail)

    # Tests nuevos para C1
    def test_ambos_es_dos_filas(self):
        user = self.User.objects.create_user(
            correo="ambos2@uacj.mx",
            password="password123",
            nombre="Ambos",
            apellidos="Dos",
            edad=21,
            sexo=Sexo.X,
            carrera="Ingeniería",
            roles=[Rol.PASAJERO, Rol.CONDUCTOR],
        )
        self.assertEqual(user.usuario_roles.count(), 2)
        self.assertTrue(user.es_pasajero)
        self.assertTrue(user.es_conductor)

    def test_usuario_rol_es_unico(self):
        user = self.User.objects.create_user(
            correo="unico@uacj.mx",
            password="password123",
            nombre="Unico",
            apellidos="Test",
            edad=20,
            sexo=Sexo.M,
            carrera="Ingeniería",
            roles=[Rol.PASAJERO],
        )
        with self.assertRaises(IntegrityError):
            from apps.accounts.models import UsuarioRol
            UsuarioRol.objects.create(usuario=user, rol=Rol.PASAJERO)

    def test_rol_admin_no_esta_en_el_enum_ambos(self):
        self.assertFalse(hasattr(Rol, "AMBOS"))

    def test_sexo_es_obligatorio(self):
        # Sin sexo, el campo es requerido (no default). En SQLite no siempre falla,
        # pero en PostgreSQL sí. Verificamos que no haya default en el campo.
        from django.db import connection
        field = self.User._meta.get_field('sexo')
        self.assertFalse(field.has_default())
        # En PostgreSQL esto fallaría con IntegrityError
        if connection.vendor == 'postgresql':
            user = self.User(
                correo="sin_sexo@uacj.mx",
                password="password123",
                nombre="Sin",
                apellidos="Sexo",
                edad=20,
                carrera="Ingeniería",
            )
            user.set_password("password123")
            with self.assertRaises(IntegrityError):
                user.save()

    def test_sexo_no_tiene_prefiere_no_decir(self):
        self.assertFalse(hasattr(Sexo, "PREFIERE_NO_DECIR"))

    # Tests nuevos para C5
    def test_is_staff_requiere_rol_admin(self):
        user = self.User.objects.create_user(
            correo="staff@uacj.mx",
            password="password123",
            nombre="Staff",
            apellidos="Test",
            edad=20,
            sexo=Sexo.M,
            carrera="Ingeniería",
            roles=[Rol.PASAJERO],
        )
        user.is_staff = True
        with self.assertRaises(ValidationError):
            user.save()

    def test_create_superuser_crea_rol_admin(self):
        user = self.User.objects.create_superuser(
            correo="super@uacj.mx",
            password="password123",
            nombre="Super",
            apellidos="User",
            edad=25,
            sexo=Sexo.M,
            carrera="Ingeniería",
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.es_admin)
        self.assertEqual(user.usuario_roles.filter(rol=Rol.ADMIN).count(), 1)

    def test_admin_no_deriva_pasajero(self):
        user = self.User.objects.create_superuser(
            correo="admin2@uacj.mx",
            password="password123",
            nombre="Admin",
            apellidos="Two",
            edad=25,
            sexo=Sexo.M,
            carrera="Ingeniería",
        )
        roles = [r.rol.lower() for r in user.usuario_roles.all()]
        self.assertEqual(roles, ["admin"])
        self.assertFalse(user.es_pasajero)
        self.assertFalse(user.es_conductor)

    # Tests nuevos para C4
    def test_suspendido_bloquea_crear_y_aceptar(self):
        user = self.User.objects.create_user(
            correo="suspendido@uacj.mx",
            password="password123",
            nombre="Suspendido",
            apellidos="Test",
            edad=20,
            sexo=Sexo.M,
            carrera="Ingeniería",
            roles=[Rol.PASAJERO, Rol.CONDUCTOR],
        )
        # Set up vehicle for conductor test
        from apps.accounts.models import Vehiculo
        Vehiculo.objects.create(
            usuario=user,
            marca="Toyota",
            modelo="Corolla",
            color="Blanco",
            placas="ABC1234",
            tipo="COCHE",
            asientos_disponibles=4,
            activo=True,
        )
        self.assertTrue(user.puede_crear_raite())
        self.assertTrue(user.puede_aceptar_raite())
        user.suspendido = True
        user.save()
        self.assertFalse(user.puede_crear_raite())
        self.assertFalse(user.puede_aceptar_raite())

    def test_suspendido_permite_login(self):
        self.User.objects.create_user(
            correo="login@uacj.mx",
            password="password123",
            nombre="Login",
            apellidos="Test",
            edad=20,
            sexo=Sexo.M,
            carrera="Ingeniería",
            roles=[Rol.PASAJERO],
            suspendido=True,
        )
        from django.contrib.auth import authenticate
        user = authenticate(request=None, correo="login@uacj.mx", password="password123")
        self.assertIsNotNone(user)
        self.assertTrue(user.suspendido)