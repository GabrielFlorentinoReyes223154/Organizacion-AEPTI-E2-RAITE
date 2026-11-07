from decimal import Decimal

from django.test import TestCase
from rest_framework import status

from apps.accounts.tests.factories import cliente_para, crear_conductor, crear_usuario
from apps.ratings.models import Calificacion
from apps.rides.models import Viaje
from apps.rides.models_choices import EstadoSolicitud, EstadoViaje
from apps.rides.tests.factories import crear_solicitud, crear_viaje


class CalificacionesApiTests(TestCase):
    def setUp(self):
        self.conductor = crear_conductor()
        self.p1, self.p2 = crear_usuario(), crear_usuario()
        self.viaje = crear_viaje(self.conductor)
        for p in (self.p1, self.p2):
            crear_solicitud(self.viaje, p, estado=EstadoSolicitud.ACEPTADA)
        Viaje.objects.filter(pk=self.viaje.pk).update(estado=EstadoViaje.FINALIZADO)

    def calificar(self, autor, calificado, puntuacion=5, viaje=None, **extra):
        viaje = viaje or self.viaje
        return cliente_para(autor).post(
            f"/api/viajes/{viaje.pk}/calificaciones/",
            {"calificado": str(calificado.pk), "puntuacion": puntuacion, **extra},
            format="json",
        )

    def test_recalcula_el_promedio(self):
        self.assertEqual(self.calificar(self.p1, self.conductor, 4).status_code, status.HTTP_201_CREATED)
        self.calificar(self.p2, self.conductor, 5)
        self.conductor.refresh_from_db()
        self.assertEqual(self.conductor.calificacion, Decimal("4.50"))

    def test_promedio_redondeado_a_dos_decimales(self):
        otro = crear_viaje(self.conductor)
        p3 = crear_usuario()
        crear_solicitud(otro, p3, estado=EstadoSolicitud.ACEPTADA)
        Viaje.objects.filter(pk=otro.pk).update(estado=EstadoViaje.FINALIZADO)
        self.calificar(self.p1, self.conductor, 5)
        self.calificar(self.p2, self.conductor, 5)
        self.calificar(p3, self.conductor, 4, viaje=otro)
        self.conductor.refresh_from_db()
        self.assertEqual(self.conductor.calificacion, Decimal("4.67"))

    def test_conductor_califica_a_pasajero(self):
        respuesta = self.calificar(self.conductor, self.p1, 3, comentario="Puntual")
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.calificacion, Decimal("3.00"))

    def test_duplicado_es_400(self):
        self.calificar(self.p1, self.conductor)
        self.assertEqual(self.calificar(self.p1, self.conductor).status_code, status.HTTP_400_BAD_REQUEST)

    def test_reglas_del_modelo_desde_el_api(self):
        casos = {
            "pasajero a pasajero": (self.p1, self.p2),
            "a sí mismo": (self.p1, self.p1),
        }
        for nombre, (autor, calificado) in casos.items():
            with self.subTest(nombre):
                self.assertEqual(self.calificar(autor, calificado).status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.calificar(self.p1, self.conductor, 6).status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.calificar(self.p1, self.conductor, comentario="x" * 501).status_code, 400)

    def test_viaje_no_finalizado_es_400(self):
        Viaje.objects.filter(pk=self.viaje.pk).update(estado=EstadoViaje.EN_CURSO)
        self.assertEqual(self.calificar(self.p1, self.conductor).status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_participante_es_403(self):
        rechazado = crear_usuario()
        crear_solicitud(self.viaje, rechazado, estado=EstadoSolicitud.RECHAZADA)
        for autor in (crear_usuario(), rechazado):
            self.assertEqual(self.calificar(autor, self.conductor).status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Calificacion.objects.exists())

    def test_pendientes(self):
        cliente = cliente_para(self.conductor)
        pendientes = cliente.get("/api/calificaciones/pendientes/").data
        self.assertEqual({p["usuario"]["id"] for p in pendientes}, {str(self.p1.pk), str(self.p2.pk)})
        self.calificar(self.conductor, self.p1)
        pendientes = cliente.get("/api/calificaciones/pendientes/").data
        self.assertEqual([p["usuario"]["id"] for p in pendientes], [str(self.p2.pk)])

        del_pasajero = cliente_para(self.p1).get("/api/calificaciones/pendientes/").data
        self.assertEqual([p["usuario"]["id"] for p in del_pasajero], [str(self.conductor.pk)])
        self.assertEqual(del_pasajero[0]["viaje"]["id"], str(self.viaje.pk))
        self.assertNotIn("telefono", del_pasajero[0]["usuario"])
