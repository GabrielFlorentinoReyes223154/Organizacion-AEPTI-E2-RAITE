import uuid
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework import status

from apps.accounts.tests.factories import cliente_para, crear_conductor, crear_usuario
from apps.notifications.models import Notificacion
from apps.notifications.models_choices import TipoNotificacion
from apps.notifications.services import notificar
from apps.rides.models import Viaje
from apps.rides.tests.factories import crear_viaje


class NotificarServicioTests(TestCase):
    def test_una_por_usuario_sin_repetir(self):
        a, b = crear_usuario(), crear_usuario()
        viaje = crear_viaje()
        creadas = notificar([a, b, a], TipoNotificacion.VIAJE_MODIFICADO, "Cambió", viaje)
        self.assertEqual(len(creadas), 2)
        self.assertEqual(Notificacion.objects.filter(viaje=viaje).count(), 2)

    def test_mensaje_largo_se_recorta(self):
        notificar([crear_usuario()], TipoNotificacion.SOLICITUD_NUEVA, "x" * 400)
        self.assertEqual(len(Notificacion.objects.get().mensaje), 255)


class NotificacionesApiTests(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()
        self.cliente = cliente_para(self.usuario)
        self.vieja = Notificacion.objects.create(usuario=self.usuario, tipo=TipoNotificacion.SOLICITUD_NUEVA, mensaje="1")
        self.nueva = Notificacion.objects.create(usuario=self.usuario, tipo=TipoNotificacion.SOLICITUD_ACEPTADA, mensaje="2")
        self.ajena = Notificacion.objects.create(usuario=crear_usuario(), tipo=TipoNotificacion.SOLICITUD_NUEVA, mensaje="3")

    def test_lista_solo_las_propias_mas_nuevas_primero(self):
        datos = self.cliente.get("/api/notificaciones/").data
        self.assertEqual([n["id"] for n in datos["results"]], [str(self.nueva.pk), str(self.vieja.pk)])

    def test_conteo_leer_y_filtrar(self):
        self.assertEqual(self.cliente.get("/api/notificaciones/conteo/").data, {"no_leidas": 2})
        respuesta = self.cliente.post(f"/api/notificaciones/{self.vieja.pk}/leer/")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertTrue(respuesta.data["leida"])
        self.assertEqual(self.cliente.get("/api/notificaciones/conteo/").data, {"no_leidas": 1})
        datos = self.cliente.get("/api/notificaciones/", {"no_leidas": 1}).data
        self.assertEqual([n["id"] for n in datos["results"]], [str(self.nueva.pk)])

    def test_leer_todas(self):
        self.assertEqual(self.cliente.post("/api/notificaciones/leer-todas/").data, {"marcadas": 2})
        self.assertEqual(self.cliente.get("/api/notificaciones/conteo/").data, {"no_leidas": 0})
        self.ajena.refresh_from_db()
        self.assertFalse(self.ajena.leida)

    def test_no_lee_la_de_otro_usuario(self):
        self.assertEqual(self.cliente.post(f"/api/notificaciones/{self.ajena.pk}/leer/").status_code, 404)
        self.assertEqual(self.cliente.post(f"/api/notificaciones/{uuid.uuid4()}/leer/").status_code, 404)
        self.ajena.refresh_from_db()
        self.assertFalse(self.ajena.leida)

    def test_requiere_sesion_verificada(self):
        self.assertEqual(cliente_para().get("/api/notificaciones/conteo/").status_code, 401)
        no_verificado = cliente_para(crear_usuario(correo_verificado=False))
        self.assertEqual(no_verificado.get("/api/notificaciones/").status_code, 403)


class NotificacionPorCadaCambioTests(TestCase):
    """Cada cambio de estado crea la notificación correcta para la persona correcta."""

    def test_recorrido_completo(self):
        conductor, pasajero = crear_conductor(), crear_usuario()
        viaje = crear_viaje(conductor)
        c, p = cliente_para(conductor), cliente_para(pasajero)

        solicitud_id = p.post(f"/api/viajes/{viaje.pk}/solicitudes/").data["id"]
        c.post(f"/api/solicitudes/{solicitud_id}/aceptar/")
        c.patch(f"/api/viajes/{viaje.pk}/", {"notas": "Frente a la entrada"}, format="json")
        Viaje.objects.filter(pk=viaje.pk).update(fecha_hora=timezone.now() + timedelta(minutes=5))
        c.post(f"/api/viajes/{viaje.pk}/iniciar/")
        c.post(f"/api/viajes/{viaje.pk}/finalizar/")

        tipos = lambda u: list(  # noqa: E731
            Notificacion.objects.filter(usuario=u).order_by("created_at").values_list("tipo", flat=True)
        )
        self.assertEqual(tipos(conductor), [TipoNotificacion.SOLICITUD_NUEVA])
        self.assertEqual(
            tipos(pasajero),
            [TipoNotificacion.SOLICITUD_ACEPTADA, TipoNotificacion.VIAJE_MODIFICADO, TipoNotificacion.VIAJE_FINALIZADO],
        )
        self.assertTrue(all(n.viaje_id == viaje.pk for n in Notificacion.objects.all()))
