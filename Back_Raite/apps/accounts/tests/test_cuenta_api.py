"""Registro con código, verificación, bloqueo de login, perfil y vehículo (RF-01, RF-07)."""

import re
import time
from unittest.mock import patch

from django.core import mail, signing
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework import status

from apps.accounts.models import CodigoVerificacion, Usuario
from apps.accounts.models_choices import PreferenciaCompatibilidad, Rol
from apps.accounts.tests.factories import cliente_para, crear_carrera, crear_conductor, crear_usuario, crear_vehiculo
from apps.rides.tests.factories import crear_viaje

CORREO = "ana.lopez@alumnos.uacj.mx"
DATOS_REGISTRO = {
    "nombre": "Ana",
    "apellidos": "López",
    "correo": "Ana.Lopez@alumnos.uacj.mx",
    "password": "password123",
    "edad": 21,
    "sexo": "F",
    "telefono": "6561112233",
}


def codigo_del_correo(indice=-1) -> str:
    return re.search(r"\b(\d{6})\b", mail.outbox[indice].body).group(1)


class RegistroBase(TestCase):
    def setUp(self):
        cache.clear()
        self.carrera = crear_carrera(nombre="Licenciatura en Psicología")

    def registrar(self, **cambios):
        datos = {**DATOS_REGISTRO, "carrera": self.carrera.pk, **cambios}
        return cliente_para().post("/api/auth/register/", datos, format="json")

    def verificar(self, token, codigo):
        return cliente_para().post("/api/auth/verificar/", {"token": token, "codigo": codigo}, format="json")

    def login(self, password="password123"):
        return cliente_para().post(
            "/api/auth/token/", {"correo": CORREO, "password": password}, format="json"
        )


class RegistroTests(RegistroBase):
    def test_registro_pide_carrera_del_catalogo(self):
        inactiva = crear_carrera(activo=False)
        for valor in (None, 999999, inactiva.pk, "Psicología"):
            with self.subTest(valor=valor):
                respuesta = self.registrar(carrera=valor)
                self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("carrera", respuesta.data)
        self.assertEqual(len(mail.outbox), 0)

    def test_cuenta_verificada_guarda_la_carrera(self):
        respuesta = self.registrar()
        self.verificar(respuesta.data["token"], codigo_del_correo())
        self.assertEqual(Usuario.objects.get(correo=CORREO).carrera, self.carrera)

    def test_registro_no_guarda_nada_y_envia_codigo(self):
        respuesta = self.registrar()
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertTrue(respuesta.data["requiere_verificacion"])
        self.assertTrue(respuesta.data["token"])
        self.assertFalse(Usuario.objects.exists())
        self.assertFalse(CodigoVerificacion.objects.exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [CORREO])
        self.assertRegex(codigo_del_correo(), r"^\d{6}$")

    def test_sin_verificar_el_correo_sigue_libre(self):
        self.registrar()
        cache.clear()  # pasó el minuto de espera
        self.assertEqual(self.registrar().status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 2)
        self.assertFalse(Usuario.objects.exists())

    def test_no_se_mandan_dos_correos_seguidos(self):
        self.registrar()
        self.assertEqual(self.registrar().status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(len(mail.outbox), 1)

    def test_si_falla_el_envio_se_puede_reintentar_de_inmediato(self):
        with patch("apps.accounts.services.correo_codigo", side_effect=RuntimeError):
            with self.assertRaises(RuntimeError):
                self.registrar()
        self.assertEqual(self.registrar().status_code, status.HTTP_201_CREATED)

    def test_el_token_no_lleva_la_contrasena_ni_el_codigo_en_claro(self):
        token = self.registrar().data["token"]
        contenido = str(signing.loads(token, salt="accounts.registro-pendiente"))
        self.assertNotIn("password123", contenido)
        self.assertNotIn(codigo_del_correo(), contenido)

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

    def test_registro_rechaza_correo_verificado_sin_importar_mayusculas(self):
        crear_usuario(correo=CORREO)
        respuesta = self.registrar(correo="ANA.LOPEZ@alumnos.uacj.mx")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cuenta_antigua_sin_verificar_no_aparta_el_correo(self):
        crear_usuario(correo=CORREO, correo_verificado=False)
        self.assertEqual(self.registrar().status_code, status.HTTP_201_CREATED)

    def test_registro_acepta_preferencia(self):
        token = self.registrar(preferencia_compatibilidad=PreferenciaCompatibilidad.MISMO_SEXO).data["token"]
        self.verificar(token, codigo_del_correo())
        self.assertEqual(
            Usuario.objects.get().preferencia_compatibilidad, PreferenciaCompatibilidad.MISMO_SEXO
        )


class VerificacionTests(RegistroBase):
    def setUp(self):
        super().setUp()
        self.token = self.registrar().data["token"]
        self.codigo = codigo_del_correo()
        self.malo = "000000" if self.codigo != "000000" else "111111"

    def test_verificar_crea_la_cuenta_y_devuelve_tokens(self):
        respuesta = self.verificar(self.token, self.codigo)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn("access", respuesta.data)
        self.assertIn("refresh", respuesta.data)
        self.assertTrue(respuesta.data["usuario"]["correo_verificado"])
        usuario = Usuario.objects.get()
        self.assertEqual(usuario.correo, CORREO)
        self.assertTrue(usuario.correo_verificado)
        self.assertEqual(self.login().status_code, status.HTTP_200_OK)

        # El token sirve para el paso siguiente
        cliente = cliente_para()
        cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {respuesta.data['access']}")
        self.assertEqual(cliente.get("/api/auth/me/").status_code, status.HTTP_200_OK)

    def test_sin_verificar_no_se_puede_iniciar_sesion(self):
        self.assertEqual(self.login().status_code, status.HTTP_401_UNAUTHORIZED)

    def test_codigo_incorrecto_no_crea_la_cuenta(self):
        respuesta = self.verificar(self.token, self.malo)
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("codigo", respuesta.data)
        self.assertFalse(Usuario.objects.exists())

    def test_codigo_con_formato_invalido(self):
        self.assertEqual(self.verificar(self.token, "12ab").status_code, status.HTTP_400_BAD_REQUEST)

    def test_registro_vencido(self):
        with patch("django.core.signing.time.time", return_value=time.time() + 16 * 60):
            respuesta = self.verificar(self.token, self.codigo)
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("venció", str(respuesta.data["codigo"]))
        self.assertFalse(Usuario.objects.exists())

    def test_token_alterado(self):
        self.assertEqual(self.verificar(self.token + "x", self.codigo).status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Usuario.objects.exists())

    @override_settings(CODIGO_VERIFICACION_MAX_INTENTOS=5)
    def test_intentos_agotados_bloquean_incluso_el_codigo_correcto(self):
        for _ in range(5):
            self.verificar(self.token, self.malo)
        respuesta = self.verificar(self.token, self.codigo)
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Agotaste", str(respuesta.data["codigo"]))
        self.assertFalse(Usuario.objects.exists())

    def test_codigo_no_se_reutiliza(self):
        self.verificar(self.token, self.codigo)
        self.assertEqual(self.verificar(self.token, self.codigo).status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(Usuario.objects.count(), 1)

    def test_reemplaza_una_cuenta_antigua_sin_verificar(self):
        crear_usuario(correo=CORREO, correo_verificado=False, nombre="Vieja")
        self.assertEqual(self.verificar(self.token, self.codigo).status_code, status.HTTP_200_OK)
        usuario = Usuario.objects.get(correo=CORREO)
        self.assertEqual(usuario.nombre, "Ana")
        self.assertTrue(usuario.correo_verificado)
        self.assertEqual(self.login().status_code, status.HTTP_200_OK)

    def test_no_reemplaza_una_cuenta_verificada(self):
        crear_usuario(correo=CORREO, nombre="Dueña")
        self.assertEqual(self.verificar(self.token, self.codigo).status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(Usuario.objects.get(correo=CORREO).nombre, "Dueña")


class ReenviarCodigoTests(RegistroBase):
    def setUp(self):
        super().setUp()
        self.token = self.registrar().data["token"]

    def reenviar(self, token=None):
        return cliente_para().post("/api/auth/reenviar-codigo/", {"token": token or self.token}, format="json")

    def test_antes_de_la_espera_es_409(self):
        self.assertEqual(self.reenviar().status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(len(mail.outbox), 1)

    def test_reenvio_cambia_el_codigo_y_el_token(self):
        anterior = codigo_del_correo()
        cache.clear()
        respuesta = self.reenviar()
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 2)
        nuevo = codigo_del_correo()
        if anterior != nuevo:
            self.assertEqual(self.verificar(respuesta.data["token"], anterior).status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.verificar(respuesta.data["token"], nuevo).status_code, status.HTTP_200_OK)

    def test_token_invalido_no_envia(self):
        self.assertEqual(self.reenviar("no-es-un-token").status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 1)

    def test_correo_ya_verificado_es_409_y_no_envia(self):
        crear_usuario(correo=CORREO)
        cache.clear()
        self.assertEqual(self.reenviar().status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(len(mail.outbox), 1)


class CorreoCodigoTests(RegistroBase):
    """El correo del código trae HTML, texto plano y el logo incrustado (RF-01)."""

    def partes(self, correo):
        return list(correo.message().walk())

    def revisar_correo(self, correo):
        codigo = re.search(r"\b(\d{6})\b", correo.body).group(1)
        self.assertEqual(correo.subject, f"Tu código de Raite: {codigo}")

        html, tipo = correo.alternatives[0]
        self.assertEqual(tipo, "text/html")
        self.assertIn(codigo, html)
        self.assertIn("cid:logo-raite@raite", html)
        self.assertIn('alt="Raite"', html)

        partes = self.partes(correo)
        relacionado = next(p for p in partes if p.get_content_type() == "multipart/related")
        tipos = [p.get_content_type() for p in relacionado.iter_parts()]
        self.assertEqual(tipos, ["text/html", "image/png"])
        logo = next(p for p in partes if p.get_content_type() == "image/png")
        self.assertEqual(logo["Content-ID"], "<logo-raite@raite>")
        self.assertEqual(logo.get_content_disposition(), "inline")
        self.assertTrue(logo.get_content().startswith(b"\x89PNG"))

    def test_registro_manda_html_con_logo(self):
        self.registrar()
        self.assertEqual(len(mail.outbox), 1)
        self.revisar_correo(mail.outbox[0])

    def test_reenvio_usa_el_mismo_correo(self):
        token = self.registrar().data["token"]
        cache.clear()
        cliente_para().post("/api/auth/reenviar-codigo/", {"token": token}, format="json")
        self.assertEqual(len(mail.outbox), 2)
        self.revisar_correo(mail.outbox[1])


class PerfilTests(TestCase):
    def test_me_incluye_vehiculo_con_placas(self):
        conductor = crear_conductor()
        datos = cliente_para(conductor).get("/api/auth/me/").data
        self.assertEqual(datos["vehiculo"]["placas"], conductor.vehiculo.placas)
        self.assertIsNone(cliente_para(crear_usuario()).get("/api/auth/me/").data["vehiculo"])

    def test_patch_me_edita_campos_permitidos(self):
        usuario = crear_usuario()
        derecho = crear_carrera(nombre="Licenciatura en Derecho")
        respuesta = cliente_para(usuario).patch(
            "/api/auth/me/",
            {"telefono": "6569998877", "carrera": derecho.pk, "preferencia_compatibilidad": "MISMO_SEXO"},
            format="json",
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        usuario.refresh_from_db()
        self.assertEqual(
            (usuario.telefono, usuario.carrera, usuario.preferencia_compatibilidad),
            ("6569998877", derecho, "MISMO_SEXO"),
        )
        self.assertEqual(respuesta.data["carrera"], "Licenciatura en Derecho")
        self.assertEqual(respuesta.data["carrera_id"], derecho.pk)
        self.assertEqual(respuesta.data["campus"]["codigo"], derecho.campus.codigo)

    def test_patch_me_rechaza_carrera_inactiva_o_inexistente(self):
        usuario = crear_usuario()
        inactiva = crear_carrera(activo=False)
        for valor in (inactiva.pk, 999999, None):
            with self.subTest(valor=valor):
                respuesta = cliente_para(usuario).patch("/api/auth/me/", {"carrera": valor}, format="json")
                self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("carrera", respuesta.data)

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
