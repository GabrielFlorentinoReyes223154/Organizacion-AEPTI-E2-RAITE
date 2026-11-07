from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.accounts.tests.factories import crear_conductor, crear_usuario
from apps.ratings.models import Calificacion
from apps.rides.models_choices import EstadoSolicitud, EstadoViaje
from apps.rides.tests.factories import crear_solicitud, crear_viaje


class CalificacionTests(TestCase):
    def setUp(self):
        self.conductor = crear_conductor()
        self.viaje = crear_viaje(self.conductor)
        self.pasajero = crear_usuario()
        self.otro_pasajero = crear_usuario()
        crear_solicitud(self.viaje, self.pasajero, estado=EstadoSolicitud.ACEPTADA)
        crear_solicitud(self.viaje, self.otro_pasajero, estado=EstadoSolicitud.ACEPTADA)
        self.viaje.estado = EstadoViaje.FINALIZADO
        self.viaje.save()

    def calificacion(self, **datos):
        valores = {"viaje": self.viaje, "autor": self.pasajero, "calificado": self.conductor, "puntuacion": 5}
        valores.update(datos)
        return Calificacion(**valores)

    def assertInvalida(self, calificacion):
        with self.assertRaises(ValidationError):
            calificacion.full_clean()

    def test_pasajero_califica_conductor_y_viceversa(self):
        self.calificacion(comentario="Muy puntual").full_clean()
        self.calificacion(autor=self.conductor, calificado=self.pasajero, puntuacion=4).full_clean()

    def test_puntuacion_entre_1_y_5(self):
        for puntos in (0, 6):
            with self.subTest(puntos=puntos):
                self.assertInvalida(self.calificacion(puntuacion=puntos))
        for puntos in (1, 5):
            self.calificacion(puntuacion=puntos).full_clean()

    def test_puntuacion_bloqueada_en_bd(self):
        with self.assertRaises(IntegrityError):
            self.calificacion(puntuacion=9).save()

    def test_comentario_maximo_500(self):
        self.assertInvalida(self.calificacion(comentario="x" * 501))

    def test_una_por_viaje_autor_y_calificado(self):
        self.calificacion().save()
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.calificacion(puntuacion=1).save()

    def test_no_a_si_mismo(self):
        self.assertInvalida(self.calificacion(calificado=self.pasajero))
        with self.assertRaises(IntegrityError):
            self.calificacion(calificado=self.pasajero).save()

    def test_solo_viajes_finalizados(self):
        viaje = crear_viaje(self.conductor)
        crear_solicitud(viaje, self.pasajero, estado=EstadoSolicitud.ACEPTADA)
        self.assertInvalida(self.calificacion(viaje=viaje))

    def test_pasajero_no_participante(self):
        ajeno = crear_usuario()
        self.assertInvalida(self.calificacion(autor=ajeno))
        self.assertInvalida(self.calificacion(autor=self.conductor, calificado=ajeno))

    def test_solicitud_no_aceptada_no_cuenta(self):
        pendiente = crear_usuario()
        crear_solicitud(self.viaje, pendiente)
        self.assertInvalida(self.calificacion(autor=pendiente))

    def test_no_entre_pasajeros(self):
        self.assertInvalida(self.calificacion(calificado=self.otro_pasajero))
