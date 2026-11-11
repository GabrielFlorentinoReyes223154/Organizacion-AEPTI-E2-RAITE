from decimal import Decimal

from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.accounts.models import Rol, Sexo, Vehiculo
from apps.accounts.models_choices import PreferenciaCompatibilidad
from apps.accounts.tests.factories import crear_carrera, crear_conductor, crear_usuario, crear_vehiculo


class UsuarioModelTests(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def crear_admin(self, **datos):
        valores = {
            "correo": "admin@ejemplo.com",
            "password": "password123",
            "nombre": "Admin",
            "apellidos": "Raite",
            "edad": 30,
            "sexo": Sexo.M,
            "telefono": "6560000000",
        }
        valores.update(datos)
        return self.User.objects.create_superuser(**valores)

    # --- Creación y valores por defecto ---

    def test_crear_usuario_con_datos_validos(self):
        user = crear_usuario(
            correo="juan@alumnos.uacj.mx",
            nombre="Juan",
            apellidos="Pérez",
            sexo=Sexo.M,
            telefono="6561234567",
            correo_verificado=False,
        )
        user.full_clean()
        self.assertEqual(user.correo, "juan@alumnos.uacj.mx")
        self.assertEqual(user.telefono, "6561234567")
        self.assertEqual(user.rol, Rol.PASAJERO)
        self.assertTrue(user.es_pasajero)
        self.assertFalse(user.es_conductor)
        self.assertFalse(user.suspendido)
        self.assertEqual(user.calificacion, Decimal("0.00"))

    def test_valores_por_defecto(self):
        user = self.User.objects.create_user(
            correo="defecto@alumnos.uacj.mx",
            password="password123",
            nombre="Defecto",
            apellidos="Test",
            sexo=Sexo.F,
            carrera=crear_carrera(),
            telefono="6561112233",
        )
        self.assertEqual(user.rol, Rol.PASAJERO)
        self.assertFalse(user.correo_verificado)
        self.assertEqual(user.preferencia_compatibilidad, PreferenciaCompatibilidad.MIXTO)

    def test_edad_fuera_de_rango_falla(self):
        for edad in (16, 71):
            with self.subTest(edad=edad), self.assertRaises(Exception), transaction.atomic():
                crear_usuario(edad=edad)

    def test_edad_en_limites_funciona(self):
        self.assertEqual(crear_usuario(edad=17).edad, 17)
        self.assertEqual(crear_usuario(edad=70).edad, 70)

    def test_correo_unico(self):
        crear_usuario(correo="duplicado@alumnos.uacj.mx")
        with self.assertRaises(IntegrityError):
            crear_usuario(correo="duplicado@alumnos.uacj.mx")

    def test_nombre_completo(self):
        self.assertEqual(crear_usuario(nombre="Ana", apellidos="López").nombre_completo, "Ana López")

    # --- Correo institucional ---

    def test_correo_institucional_valido(self):
        crear_usuario(correo="ok@alumnos.uacj.mx").full_clean()

    def test_correo_no_institucional_rechazado(self):
        for correo in ("alguien@gmail.com", "profe@uacj.mx", "x@alumnos.uacj.mx.com"):
            with self.subTest(correo=correo):
                user = crear_usuario(correo=correo)
                with self.assertRaises(ValidationError) as ctx:
                    user.full_clean()
                self.assertIn("correo", ctx.exception.message_dict)

    def test_correo_institucional_ignora_mayusculas(self):
        crear_usuario(correo="Mayus@Alumnos.UACJ.mx").full_clean()

    def test_admin_puede_tener_cualquier_correo(self):
        self.crear_admin(correo="coordinacion@gmail.com").full_clean()

    def test_alumno_necesita_carrera_y_admin_no(self):
        alumno = crear_usuario()
        alumno.carrera = None
        with self.assertRaises(ValidationError) as error:
            alumno.full_clean()
        self.assertIn("carrera", error.exception.message_dict)
        admin = self.crear_admin()
        self.assertIsNone(admin.carrera)
        self.assertIsNone(admin.campus)
        admin.full_clean()

    def test_campus_sale_de_la_carrera(self):
        carrera = crear_carrera()
        self.assertEqual(crear_usuario(carrera=carrera).campus, carrera.campus)

    # --- Teléfono ---

    def test_telefono_valido(self):
        crear_usuario(telefono="6561234567").full_clean()

    def test_telefono_invalido(self):
        user = crear_usuario()
        for telefono in ("", "656123456", "65612345678", "656-123-456", "abcdefghij"):
            with self.subTest(telefono=telefono):
                user.telefono = telefono  # sin guardar: en PostgreSQL 11 caracteres no caben en la columna
                with self.assertRaises(ValidationError) as ctx:
                    user.full_clean()
                self.assertIn("telefono", ctx.exception.message_dict)

    # --- Sexo y preferencia ---

    def test_sexo_es_obligatorio(self):
        field = self.User._meta.get_field("sexo")
        self.assertFalse(field.has_default())
        user = crear_usuario()
        user.sexo = ""
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_sexo_acepta_m_f_x(self):
        for sexo in (Sexo.M, Sexo.F, Sexo.X):
            with self.subTest(sexo=sexo):
                crear_usuario(sexo=sexo).full_clean()

    def test_sexo_no_tiene_prefiere_no_decir(self):
        self.assertEqual({c[0] for c in Sexo.choices}, {"M", "F", "X"})

    def test_preferencia_solo_mismo_sexo_o_mixto(self):
        self.assertEqual(
            {c[0] for c in PreferenciaCompatibilidad.choices}, {"MISMO_SEXO", "MIXTO"}
        )
        user = crear_usuario()
        user.preferencia_compatibilidad = "SEXO_OPUESTO"
        with self.assertRaises(ValidationError):
            user.full_clean()

    # --- Roles ---

    def test_es_pasajero_es_conductor_es_admin(self):
        pasajero = crear_usuario(rol=Rol.PASAJERO)
        conductor = crear_usuario(rol=Rol.CONDUCTOR)
        ambos = crear_usuario(rol=Rol.AMBOS)
        admin = self.crear_admin()

        self.assertEqual((pasajero.es_pasajero, pasajero.es_conductor, pasajero.es_admin), (True, False, False))
        self.assertEqual((conductor.es_pasajero, conductor.es_conductor, conductor.es_admin), (False, True, False))
        self.assertEqual((ambos.es_pasajero, ambos.es_conductor, ambos.es_admin), (True, True, False))
        self.assertEqual((admin.es_pasajero, admin.es_conductor, admin.es_admin), (False, False, True))

    def test_tiene_rol(self):
        user = crear_usuario(rol=Rol.PASAJERO)
        self.assertTrue(user.tiene_rol(Rol.PASAJERO))
        self.assertFalse(user.tiene_rol(Rol.CONDUCTOR))

    def test_no_se_puede_crear_usuario_con_rol_admin_via_create_user(self):
        with self.assertRaises(ValueError):
            crear_usuario(rol=Rol.ADMIN)

    def test_is_staff_requiere_rol_admin(self):
        user = crear_usuario()
        user.is_staff = True
        with self.assertRaises(ValidationError):
            user.save()

    def test_create_superuser_crea_admin_verificado(self):
        user = self.crear_admin()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.rol, Rol.ADMIN)
        self.assertTrue(user.correo_verificado)
        self.assertFalse(user.es_pasajero)
        self.assertFalse(user.es_conductor)

    # --- Permisos de cuenta para viajes ---

    def test_puede_solicitar_lugar(self):
        user = crear_usuario(rol=Rol.PASAJERO)
        self.assertTrue(user.puede_solicitar_lugar())

        user.correo_verificado = False
        self.assertFalse(user.puede_solicitar_lugar())

        user.correo_verificado = True
        user.suspendido = True
        self.assertFalse(user.puede_solicitar_lugar())

    def test_conductor_puro_no_puede_solicitar_lugar(self):
        self.assertFalse(crear_conductor().puede_solicitar_lugar())

    def test_puede_publicar_viaje(self):
        user = crear_conductor(con_vehiculo=False)
        self.assertFalse(user.puede_publicar_viaje())  # sin vehículo

        vehiculo = crear_vehiculo(user)
        user.refresh_from_db()
        self.assertTrue(user.puede_publicar_viaje())

        user.correo_verificado = False
        self.assertFalse(user.puede_publicar_viaje())
        user.correo_verificado = True

        user.suspendido = True
        self.assertFalse(user.puede_publicar_viaje())
        user.suspendido = False

        vehiculo.activo = False
        vehiculo.save()
        user.refresh_from_db()
        self.assertFalse(user.puede_publicar_viaje())

    def test_pasajero_puro_no_puede_publicar_viaje(self):
        user = crear_usuario(rol=Rol.PASAJERO)
        crear_vehiculo(user)
        user.refresh_from_db()
        self.assertFalse(user.puede_publicar_viaje())

    def test_rol_ambos_puede_publicar_y_solicitar(self):
        user = crear_conductor(rol=Rol.AMBOS)
        self.assertTrue(user.puede_publicar_viaje())
        self.assertTrue(user.puede_solicitar_lugar())

    # --- Login ---

    def test_authenticate_por_correo(self):
        crear_usuario(correo="auth@alumnos.uacj.mx")
        self.assertIsNotNone(authenticate(request=None, correo="auth@alumnos.uacj.mx", password="password123"))
        self.assertIsNone(authenticate(request=None, correo="auth@alumnos.uacj.mx", password="mala"))

    def test_suspendido_permite_login(self):
        crear_usuario(correo="login@alumnos.uacj.mx", suspendido=True)
        user = authenticate(request=None, correo="login@alumnos.uacj.mx", password="password123")
        self.assertIsNotNone(user)
        self.assertTrue(user.suspendido)


class VehiculoModelTests(TestCase):
    def test_asientos_en_limites_validos(self):
        for asientos in (1, 5):
            with self.subTest(asientos=asientos):
                crear_vehiculo(crear_conductor(con_vehiculo=False), asientos_disponibles=asientos).full_clean()

    def test_asientos_fuera_de_rango_no_pasan_validacion(self):
        for asientos in (0, 6, 8):
            with self.subTest(asientos=asientos):
                vehiculo = Vehiculo(
                    usuario=crear_conductor(con_vehiculo=False),
                    marca="Ford",
                    modelo="Ranger",
                    color="Negro",
                    placas=f"ZZZ{asientos:04d}",
                    tipo="TROCA",
                    asientos_disponibles=asientos,
                )
                with self.assertRaises(ValidationError) as ctx:
                    vehiculo.full_clean()
                self.assertIn("asientos_disponibles", ctx.exception.message_dict)

    def test_asientos_fuera_de_rango_bloqueado_en_bd(self):
        with self.assertRaises(IntegrityError):
            crear_vehiculo(crear_conductor(con_vehiculo=False), asientos_disponibles=6)

    def test_placas_unicas(self):
        crear_vehiculo(crear_conductor(con_vehiculo=False), placas="DUP0001")
        with self.assertRaises(IntegrityError):
            crear_vehiculo(crear_conductor(con_vehiculo=False), placas="DUP0001")

    def test_tiene_capacidad(self):
        vehiculo = crear_vehiculo(crear_conductor(con_vehiculo=False), asientos_disponibles=3)
        self.assertTrue(vehiculo.tiene_capacidad(3))
        self.assertFalse(vehiculo.tiene_capacidad(4))




class MigracionBorrarAlumnosTests(TestCase):
    """Migración 0014: borra a los alumnos (y lo que depende de ellos) y conserva a los admins."""

    def test_borra_alumnos_con_sus_viajes_y_conserva_admins(self):
        import importlib

        from django.apps import apps

        from apps.rides.models import Solicitud, Viaje
        from apps.rides.tests.factories import crear_solicitud, crear_viaje

        admin = get_user_model().objects.create_superuser(
            correo="admin@ejemplo.com", password="password123", nombre="Admin", apellidos="Raite",
            edad=30, sexo=Sexo.M, telefono="6560000000",
        )
        conductor = crear_conductor()
        viaje = crear_viaje(conductor)
        crear_solicitud(viaje, crear_usuario())

        migracion = importlib.import_module("apps.accounts.migrations.0014_borrar_alumnos")
        migracion.borrar_alumnos(apps, None)

        self.assertEqual(list(get_user_model().objects.all()), [admin])
        self.assertFalse(Viaje.objects.exists())
        self.assertFalse(Solicitud.objects.exists())
        self.assertFalse(Vehiculo.objects.exists())
