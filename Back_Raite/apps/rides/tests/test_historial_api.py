"""Historial de viajes por usuario (RF-11)."""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.accounts.models_choices import Rol
from apps.accounts.tests.factories import cliente_para, crear_conductor, crear_usuario
from apps.rides.models import Viaje
from apps.rides.models_choices import EstadoSolicitud, EstadoViaje
from apps.rides.tests.factories import crear_solicitud, crear_viaje


class HistorialTests(TestCase):
    def setUp(self):
        self.usuario = crear_conductor(rol=Rol.AMBOS)
        self.cliente = cliente_para(self.usuario)

    def viaje(self, dias, estado, **datos):
        viaje = crear_viaje(fecha_hora=timezone.now() + timedelta(days=dias), **datos)
        Viaje.objects.filter(pk=viaje.pk).update(estado=estado, fecha_hora=timezone.now() - timedelta(days=dias))
        return viaje

    def ids(self, **filtros):
        return [v["id"] for v in self.cliente.get("/api/historial/", filtros).data["results"]]

    def test_que_aparece_y_en_que_orden(self):
        conducido = self.viaje(1, EstadoViaje.FINALIZADO, conductor=self.usuario)
        como_pasajero = self.viaje(2, EstadoViaje.FINALIZADO)
        crear_solicitud(como_pasajero, self.usuario, estado=EstadoSolicitud.ACEPTADA)
        cancelado_propio = self.viaje(3, EstadoViaje.CANCELADO, conductor=self.usuario)
        cancelado_por_conductor = self.viaje(4, EstadoViaje.CANCELADO)
        crear_solicitud(cancelado_por_conductor, self.usuario, estado=EstadoSolicitud.CANCELADA)

        # No aparecen: vigente, rechazado, ajeno
        crear_viaje(self.usuario, fecha_hora=timezone.now() + timedelta(days=9))
        rechazado = self.viaje(5, EstadoViaje.FINALIZADO)
        crear_solicitud(rechazado, self.usuario, estado=EstadoSolicitud.RECHAZADA)
        self.viaje(6, EstadoViaje.FINALIZADO)

        esperados = [conducido, como_pasajero, cancelado_propio, cancelado_por_conductor]
        self.assertEqual(self.ids(), [str(v.pk) for v in esperados])
        self.assertEqual(self.ids(rol="conductor"), [str(conducido.pk), str(cancelado_propio.pk)])
        self.assertEqual(self.ids(rol="pasajero"), [str(como_pasajero.pk), str(cancelado_por_conductor.pk)])

    def test_mi_papel_y_contacto(self):
        conducido = self.viaje(1, EstadoViaje.FINALIZADO, conductor=self.usuario)
        como_pasajero = self.viaje(2, EstadoViaje.FINALIZADO)
        crear_solicitud(como_pasajero, self.usuario, estado=EstadoSolicitud.ACEPTADA)
        datos = {v["id"]: v for v in self.cliente.get("/api/historial/").data["results"]}
        self.assertEqual(datos[str(conducido.pk)]["mi_papel"], "conductor")
        self.assertEqual(datos[str(como_pasajero.pk)]["mi_papel"], "pasajero")
        self.assertEqual(datos[str(como_pasajero.pk)]["conductor"]["telefono"], como_pasajero.conductor.telefono)

    def test_rol_invalido_y_permisos(self):
        self.assertEqual(self.cliente.get("/api/historial/", {"rol": "x"}).status_code, 400)
        self.assertEqual(cliente_para().get("/api/historial/").status_code, 401)
        self.assertEqual(cliente_para(crear_usuario()).get("/api/historial/").data["count"], 0)
