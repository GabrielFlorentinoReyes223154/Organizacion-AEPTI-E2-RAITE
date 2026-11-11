from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import RequestFactory, TestCase

from apps.accounts.tests.factories import crear_conductor, crear_usuario
from apps.reports.admin import ReporteAdmin
from apps.reports.models import Reporte
from apps.reports.models_choices import EstadoReporte
from apps.rides.models_choices import EstadoSolicitud
from apps.rides.tests.factories import crear_solicitud, crear_viaje


class ReporteTests(TestCase):
    def setUp(self):
        self.conductor = crear_conductor()
        self.viaje = crear_viaje(self.conductor)
        self.pasajero = crear_usuario()
        self.otro_pasajero = crear_usuario()
        crear_solicitud(self.viaje, self.pasajero, estado=EstadoSolicitud.ACEPTADA)
        crear_solicitud(self.viaje, self.otro_pasajero, estado=EstadoSolicitud.ACEPTADA)

    def reporte(self, **datos):
        valores = {
            "viaje": self.viaje,
            "reportante": self.pasajero,
            "reportado": self.conductor,
            "motivo": "Manejó de forma peligrosa.",
        }
        valores.update(datos)
        return Reporte(**valores)

    def test_reporte_valido(self):
        reporte = self.reporte()
        reporte.full_clean()
        reporte.save()
        self.assertEqual(reporte.estado, EstadoReporte.PENDIENTE)
        self.assertIsNone(reporte.resuelto_por)

    def test_entre_pasajeros_tambien_se_permite(self):
        self.reporte(reportado=self.otro_pasajero).full_clean()

    def test_no_a_si_mismo(self):
        with self.assertRaises(ValidationError):
            self.reporte(reportado=self.pasajero).full_clean()
        with self.assertRaises(IntegrityError):
            self.reporte(reportado=self.pasajero).save()

    def test_reportante_debe_haber_participado(self):
        with self.assertRaises(ValidationError) as ctx:
            self.reporte(reportante=crear_usuario()).full_clean()
        self.assertIn("reportante", ctx.exception.message_dict)

    def test_reportado_debe_haber_participado(self):
        pendiente = crear_usuario()
        crear_solicitud(self.viaje, pendiente)
        with self.assertRaises(ValidationError) as ctx:
            self.reporte(reportado=pendiente).full_clean()
        self.assertIn("reportado", ctx.exception.message_dict)

    def test_motivo_obligatorio_y_maximo_1000(self):
        for motivo in ("", "x" * 1001):
            with self.subTest(largo=len(motivo)), self.assertRaises(ValidationError):
                self.reporte(motivo=motivo).full_clean()


class ReporteAdminTests(TestCase):
    def setUp(self):
        conductor = crear_conductor()
        viaje = crear_viaje(conductor)
        pasajero = crear_usuario()
        crear_solicitud(viaje, pasajero, estado=EstadoSolicitud.ACEPTADA)
        self.reporte = Reporte.objects.create(viaje=viaje, reportante=pasajero, reportado=conductor, motivo="x")
        self.admin_user = get_admin()
        self.model_admin = ReporteAdmin(Reporte, AdminSite())
        self.request = RequestFactory().post("/")
        self.request.user = self.admin_user
        self.model_admin.message_user = lambda *a, **k: None

    def test_suspender_reportado(self):
        self.model_admin.suspender_reportado(self.request, Reporte.objects.all())
        self.reporte.refresh_from_db()
        self.assertTrue(self.reporte.reportado.suspendido)
        self.assertEqual(self.reporte.estado, EstadoReporte.RESUELTO)
        self.assertEqual(self.reporte.resuelto_por, self.admin_user)
        self.assertIsNotNone(self.reporte.resuelto_en)

    def test_descartar(self):
        self.model_admin.descartar(self.request, Reporte.objects.all())
        self.reporte.refresh_from_db()
        self.assertEqual(self.reporte.estado, EstadoReporte.DESCARTADO)
        self.assertFalse(self.reporte.reportado.suspendido)


def get_admin():
    from django.contrib.auth import get_user_model

    return get_user_model().objects.create_superuser(
        correo="admin@ejemplo.com",
        password="password123",
        nombre="Admin",
        apellidos="Raite",
        edad=30,
        sexo="M",
        telefono="6560000000",
    )
