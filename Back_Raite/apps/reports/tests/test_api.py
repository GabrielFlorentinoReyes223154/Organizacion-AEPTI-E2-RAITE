from django.test import TestCase
from rest_framework import status

from apps.accounts.tests.factories import cliente_para, crear_conductor, crear_usuario
from apps.reports.models import Reporte
from apps.reports.models_choices import EstadoReporte
from apps.rides.models_choices import EstadoSolicitud
from apps.rides.tests.factories import crear_solicitud, crear_viaje


class ReportesApiTests(TestCase):
    def setUp(self):
        self.conductor = crear_conductor()
        self.pasajero = crear_usuario()
        self.viaje = crear_viaje(self.conductor)
        crear_solicitud(self.viaje, self.pasajero, estado=EstadoSolicitud.ACEPTADA)

    def reportar(self, autor, reportado, motivo="Manejó con exceso de velocidad."):
        return cliente_para(autor).post(
            "/api/reportes/",
            {"viaje": str(self.viaje.pk), "reportado": str(reportado.pk), "motivo": motivo},
            format="json",
        )

    def test_pasajero_reporta_al_conductor_y_viceversa(self):
        respuesta = self.reportar(self.pasajero, self.conductor)
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.data["estado"], EstadoReporte.PENDIENTE)
        self.assertNotIn("notas_admin", respuesta.data)
        self.assertEqual(self.reportar(self.conductor, self.pasajero).status_code, status.HTTP_201_CREATED)

    def test_duplicado_pendiente_es_409_pero_resuelto_permite_otro(self):
        self.reportar(self.pasajero, self.conductor)
        self.assertEqual(self.reportar(self.pasajero, self.conductor).status_code, status.HTTP_409_CONFLICT)
        Reporte.objects.update(estado=EstadoReporte.RESUELTO)
        self.assertEqual(self.reportar(self.pasajero, self.conductor).status_code, status.HTTP_201_CREATED)

    def test_no_participante_es_403(self):
        pendiente = crear_usuario()
        crear_solicitud(self.viaje, pendiente)
        for autor in (crear_usuario(), pendiente):
            self.assertEqual(self.reportar(autor, self.conductor).status_code, status.HTTP_403_FORBIDDEN)

    def test_reglas_del_modelo_desde_el_api(self):
        self.assertEqual(self.reportar(self.pasajero, self.pasajero).status_code, 400)  # a sí mismo
        self.assertEqual(self.reportar(self.pasajero, crear_usuario()).status_code, 400)  # ajeno al viaje
        self.assertEqual(self.reportar(self.pasajero, self.conductor, motivo="x" * 1001).status_code, 400)
        self.assertEqual(self.reportar(self.pasajero, self.conductor, motivo="").status_code, 400)
        self.assertFalse(Reporte.objects.exists())

    def test_mis_reportes(self):
        self.reportar(self.pasajero, self.conductor)
        self.reportar(self.conductor, self.pasajero)
        datos = cliente_para(self.pasajero).get("/api/reportes/mios/").data
        self.assertEqual(datos["count"], 1)
        self.assertEqual(datos["results"][0]["reportado"]["id"], str(self.conductor.pk))
        self.assertEqual(cliente_para().get("/api/reportes/mios/").status_code, 401)
