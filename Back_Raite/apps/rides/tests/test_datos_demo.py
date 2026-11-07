"""El comando crear_datos_demo deja datos útiles para probar todas las pantallas."""

from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from apps.accounts.tests.factories import cliente_para, crear_usuario
from apps.ratings.services import pendientes
from apps.rides.models import Solicitud, Viaje
from apps.rides.models_choices import EstadoSolicitud, EstadoViaje


def correr(*args):
    call_command("crear_datos_demo", *args, stdout=StringIO())


class CrearDatosDemoTests(TestCase):
    def setUp(self):
        correr()
        self.usuarios = get_user_model().objects.filter(correo__contains=".demo@")

    def usuario(self, nombre):
        return self.usuarios.get(nombre=nombre)

    def test_crea_usuarios_verificados_con_contrasena_conocida(self):
        self.assertEqual(self.usuarios.count(), 7)
        andrea = self.usuario("Andrea")
        self.assertTrue(andrea.correo_verificado)
        self.assertTrue(andrea.check_password("raite1234"))
        self.assertTrue(all(u.correo.endswith("@alumnos.uacj.mx") for u in self.usuarios))

    def test_cubre_todos_los_estados(self):
        viajes = Viaje.objects.filter(conductor__in=self.usuarios)
        for estado in (EstadoViaje.PUBLICADO, EstadoViaje.FINALIZADO, EstadoViaje.CANCELADO):
            self.assertTrue(viajes.filter(estado=estado).exists(), estado)
        self.assertTrue(any(v.esta_vencido for v in viajes))
        solicitudes = Solicitud.objects.filter(viaje__in=viajes)
        for estado in EstadoSolicitud.values:
            self.assertTrue(solicitudes.filter(estado=estado).exists(), estado)

    def test_hay_algo_para_cada_pantalla(self):
        andrea, mariana = self.usuario("Andrea"), self.usuario("Mariana")
        self.assertEqual(len(pendientes(andrea)), 1)  # Calificar
        self.assertTrue(andrea.notificaciones.exists())  # Avisos
        mios = cliente_para(mariana).get("/api/viajes/mios/").data["results"]
        self.assertTrue(any(v["solicitudes_pendientes"] > 0 for v in mios))  # Solicitudes del conductor
        historial = cliente_para(andrea).get("/api/historial/").data["count"]
        self.assertGreater(historial, 0)

    def test_la_busqueda_encuentra_viajes_cerca_del_punto_ancla(self):
        punto = Viaje.objects.filter(conductor__in=self.usuarios, notas__startswith="Salgo").get().punto_referencia
        respuesta = cliente_para(crear_usuario()).get("/api/viajes/", {"punto": punto.pk})
        self.assertGreaterEqual(respuesta.data["count"], 3)

    def test_sin_reiniciar_no_duplica(self):
        with self.assertRaises(CommandError):
            correr()

    def test_reiniciar_borra_y_crea_de_nuevo(self):
        otro = crear_usuario()
        correr("--reiniciar")
        self.assertEqual(self.usuarios.count(), 7)
        self.assertTrue(get_user_model().objects.filter(pk=otro.pk).exists())  # no toca a nadie más
