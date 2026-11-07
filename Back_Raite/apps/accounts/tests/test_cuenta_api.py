"""Registro con código, verificación, bloqueo de login, perfil y vehículo (RF-01, RF-07)."""

import re
from datetime import timedelta

from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status

from apps.accounts.models import CodigoVerificacion, Usuario
from apps.accounts.models_choices import PreferenciaCompatibilidad, Rol
from apps.accounts.tests.factories import cliente_para, crear_conductor, crear_usuario, crear_vehiculo
from apps.rides.tests.factories import crear_viaje

DATOS_REGISTRO = {
    "nombre": "Ana",
    "apellidos": "López",
    "correo": "Ana.Lopez@alumnos.uacj.mx",
    "password": "password123",
    "edad": 21,
    "sexo": "F",
    "carrera": "Psicología",
    "telefono": "6561112233",
}


def codigo_del_correo(indice=-1) -> str:
    return re.search(r"\b(\d{6})\b", mail.outbox[indice].body).group(1)


class RegistroTests(TestCase):
    def registrar(self, **cambios):
        return cliente_para().post("/api/auth/register/", {**DATOS_REGISTRO, **cambios}, format="json")

    def test_registro_crea_usuario_sin_verificar_y_envia_codigo(self):
        respuesta = self.registrar()
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertTrue(respuesta.data["requiere_verificacion"])
        usuario = Usuario.objects.get(correo="ana.lopez@alumnos.uacj.mx")
        self.assertFalse(usuario.correo_verificado)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["ana.lopez@alumnos.uacj.mx"])
        self.assertRegex(codigo_del_correo(), r"^\d{6}$")
        self.assertEqual(CodigoVerificacion.objects.filter(usuario=usuario).count(), 1)

    def test_registro_rechaza_correo_no_institucional(self):
        respuesta = self.registrar(correo="ana@gmail.com")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("correo", respuesta.data)
        self.assertFalse(Usuario.objects.exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_registro_rechaza_telefono_invalido(self):
        respuesta = self.registrar(telefono="656-111")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("telefono", respuesta.data)

    def test_registro_rechaza_correo_repetido_sin_importar_mayusculas(self):
        crear_usuario(correo="ana.lopez@alumnos.uacj.mx")
        respuesta = self.registrar(correo="ANA.LOPEZ@alumnos.uacj.mx")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registro_acepta_preferencia(self):
        self.registrar(preferencia_compatibilidad=PreferenciaCompatibilidad.MISMO_SEXO)
        self.assertEqual(
            Usuario.objects.get().preferencia_compatibilidad, PreferenciaCompatibilidad.MISMO_SEXO
        )


class VerificacionTests(TestCase):
    def setUp(self):
        cliente_para().post("/api/auth/register/", DATOS_REGISTRO, format="json")
        self.usuario = Usuario.objects.get()
        self.codigo = codigo_del_correo()

    def verificar(self, codigo, correo="ana.lopez@alumnos.uacj.mx"):
        return cliente_para().post("/api/auth/verificar/", {"correo": correo, "codigo": codigo}, format="json")

    def login(self):
        return cliente_para().post(
            "/api/auth/token/", {"correo": "ana.lopez@alumnos.uacj.mx", "password": "password123"}, format="json"
        )

    def test_login_sin_verificar_es_403(self):
        respuesta = self.login()
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(respuesta.data["codigo"], "correo_no_verificado")
        self.assertNotIn("access", respuesta.data)

    def test_verificar_activa_la_cuenta_y_devuelve_tokens(self):
        respuesta = self.verificar(self.codigo)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn("access", respuesta.data)
        self.assertIn("refresh", respuesta.data)
        self.assertTrue(respuesta.data["usuario"]["correo_verificado"])
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.correo_verificado)
        self.assertEqual(self.login().status_code, status.HTTP_200_OK)

        # El token sirve para el paso siguiente
        cliente = cliente_para()
        cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {respuesta.data['access']}")
        self.assertEqual(cliente.get("/api/auth/me/").status_code, status.HTTP_200_OK)

    def test_verificar_acepta_correo_con_mayusculas(self):
        self.assertEqual(self.verificar(self.codigo, correo="ANA.LOPEZ@alumnos.uacj.mx").status_code, 200)

    def test_codigo_incorrecto(self):
        malo = "000000" if self.codigo != "000000" else "111111"
        respuesta = self.verificar(malo)
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("codigo", respuesta.data)
        self.assertEqual(CodigoVerificacion.objects.get().intentos, 1)  # el intento se guarda

    def test_codigo_con_formato_invalido(self):
        self.assertEqual(self.verificar("12ab").status_code, status.HTTP_400_BAD_REQUEST)

    def test_codigo_vencido(self):
        CodigoVerificacion.objects.update(expira_en=timezone.now() - timedelta(seconds=1))
        self.assertEqual(self.verificar(self.codigo).status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(CODIGO_VERIFICACION_MAX_INTENTOS=5)
    def test_intentos_agotados_bloquean_incluso_el_codigo_correcto(self):
        malo = "000000" if self.codigo != "000000" else "111111"
        for _ in range(5):
            self.verificar(malo)
        respuesta = self.verificar(self.codigo)
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Agotaste", str(respuesta.data["codigo"]))

    def test_codigo_no_se_reutiliza(self):
        self.verificar(self.codigo)
        self.assertEqual(self.verificar(self.codigo).status_code, status.HTTP_409_CONFLICT)

    def test_correo_inexistente(self):
        self.assertEqual(self.verificar(self.codigo, correo="nadie@alumnos.uacj.mx").status_code, 400)


class ReenviarCodigoTests(TestCase):
    def setUp(self):
        cliente_para().post("/api/auth/register/", DATOS_REGISTRO, format="json")

    def reenviar(self, correo="ana.lopez@alumnos.uacj.mx"):
        return cliente_para().post("/api/auth/reenviar-codigo/", {"correo": correo}, format="json")

    def test_antes_de_la_espera_es_409(self):
        self.assertEqual(self.reenviar().status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(len(mail.outbox), 1)

    def test_reenvio_anula_el_codigo_anterior(self):
        anterior = codigo_del_correo()
        CodigoVerificacion.objects.update(creado_en=timezone.now() - timedelta(minutes=2))
        self.assertEqual(self.reenviar().status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 2)
        nuevo = codigo_del_correo()

        verificar = lambda codigo: cliente_para().post(  # noqa: E731
            "/api/auth/verificar/", {"correo": "ana.lopez@alumnos.uacj.mx", "codigo": codigo}, format="json"
        )
        if anterior != nuevo:
            self.assertEqual(verificar(anterior).status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(verificar(nuevo).status_code, status.HTTP_200_OK)

    def test_correo_inexistente_o_verificado_responde_igual_sin_enviar(self):
        verificado = crear_usuario()
        for correo in ("nadie@alumnos.uacj.mx", verificado.correo):
            with self.subTest(correo=correo):
                self.assertEqual(self.reenviar(correo).status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)


class PerfilTests(TestCase):
    def test_me_incluye_vehiculo_con_placas(self):
        conductor = crear_conductor()
        datos = cliente_para(conductor).get("/api/auth/me/").data
        self.assertEqual(datos["vehiculo"]["placas"], conductor.vehiculo.placas)
        self.assertIsNone(cliente_para(crear_usuario()).get("/api/auth/me/").data["vehiculo"])

    def test_patch_me_edita_campos_permitidos(self):
        usuario = crear_usuario()
        respuesta = cliente_para(usuario).patch(
            "/api/auth/me/",
            {"telefono": "6569998877", "carrera": "Derecho", "preferencia_compatibilidad": "MISMO_SEXO"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        usuario.refresh_from_db()
        self.assertEqual(
            (usuario.telefono, usuario.carrera, usuario.preferencia_compatibilidad),
            ("6569998877", "Derecho", "MISMO_SEXO"),
        )

    def test_patch_me_ignora_campos_protegidos(self):
        usuario = crear_usuario(sexo="M")
        cliente_para(usuario).patch(
            "/api/auth/me/",
            {"sexo": "F", "rol": Rol.ADMIN, "correo": "x@gmail.com", "suspendido": False, "calificacion": "5.00"},
            format="json",
        )
        usuario.refresh_from_db()
        self.assertEqual((usuario.sexo, usuario.rol), ("M", Rol.PASAJERO))
        self.assertTrue(usuario.correo.endswith("@alumnos.uacj.mx"))

    def test_patch_me_valida(self):
        respuesta = cliente_para(crear_usuario()).patch("/api/auth/me/", {"telefono": "123"}, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)


class VehiculoTests(TestCase):
    DATOS = {"marca": "Kia", "modelo": "Rio", "color": "Rojo", "placas": "abc-123", "tipo": "COCHE", "asientos_disponibles": 4}

    def test_registrar_vehiculo(self):
        conductor = crear_conductor(con_vehiculo=False)
        respuesta = cliente_para(conductor).post("/api/auth/vehicle/", self.DATOS, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.data["placas"], "ABC123")

    def test_registrar_segundo_vehiculo_es_409(self):
        conductor = crear_conductor()
        respuesta = cliente_para(conductor).post("/api/auth/vehicle/", self.DATOS, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)

    def test_pasajero_que_registra_vehiculo_pasa_a_ambos(self):
        pasajero = crear_usuario(rol=Rol.PASAJERO)
        cliente = cliente_para(pasajero)
        self.assertEqual(cliente.get("/api/auth/vehicle/").status_code, status.HTTP_404_NOT_FOUND)
        respuesta = cliente.post("/api/auth/vehicle/", self.DATOS, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.data["rol"], Rol.AMBOS)
        pasajero.refresh_from_db()
        self.assertEqual(pasajero.rol, Rol.AMBOS)
        self.assertTrue(pasajero.puede_publicar_viaje())
        self.assertEqual(cliente.get("/api/auth/vehicle/").status_code, status.HTTP_200_OK)

    def test_conductor_que_registra_vehiculo_conserva_su_rol(self):
        conductor = crear_conductor(con_vehiculo=False)
        respuesta = cliente_para(conductor).post("/api/auth/vehicle/", self.DATOS, format="json")
        self.assertEqual(respuesta.data["rol"], Rol.CONDUCTOR)

    def test_vehiculo_invalido_no_cambia_el_rol(self):
        pasajero = crear_usuario(rol=Rol.PASAJERO)
        datos = {**self.DATOS, "asientos_disponibles": 9}
        self.assertEqual(cliente_para(pasajero).post("/api/auth/vehicle/", datos, format="json").status_code, 400)
        pasajero.refresh_from_db()
        self.assertEqual(pasajero.rol, Rol.PASAJERO)

    def test_admin_no_registra_vehiculo(self):
        from django.contrib.auth import get_user_model

        admin = get_user_model().objects.create_superuser("admin@uacj.mx", "password123")
        respuesta = cliente_para(admin).post("/api/auth/vehicle/", self.DATOS, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_sin_verificar_no_registra_vehiculo(self):
        conductor = crear_conductor(con_vehiculo=False, correo_verificado=False)
        respuesta = cliente_para(conductor).post("/api/auth/vehicle/", self.DATOS, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_sin_vehiculo_es_404(self):
        cliente = cliente_para(crear_conductor(con_vehiculo=False))
        self.assertEqual(cliente.get("/api/auth/vehicle/").status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_vehiculo(self):
        conductor = crear_conductor(asientos=4)
        cliente = cliente_para(conductor)
        respuesta = cliente.patch("/api/auth/vehicle/", {"color": "Azul", "asientos_disponibles": 5, "placas": "ZZZ999"}, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        conductor.vehiculo.refresh_from_db()
        self.assertEqual((conductor.vehiculo.color, conductor.vehiculo.asientos_disponibles), ("Azul", 5))
        self.assertNotEqual(conductor.vehiculo.placas, "ZZZ999")  # las placas no se editan

    def test_patch_no_baja_asientos_bajo_un_viaje_vigente(self):
        conductor = crear_conductor(asientos=4)
        crear_viaje(conductor, lugares_ofrecidos=3)
        cliente = cliente_para(conductor)
        respuesta = cliente.patch("/api/auth/vehicle/", {"asientos_disponibles": 2}, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(cliente.patch("/api/auth/vehicle/", {"asientos_disponibles": 3}, format="json").status_code, 200)

    def test_patch_fuera_de_rango(self):
        cliente = cliente_para(crear_conductor())
        self.assertEqual(cliente.patch("/api/auth/vehicle/", {"asientos_disponibles": 6}, format="json").status_code, 400)
