from django.test import SimpleTestCase, TestCase
from rest_framework import status

from apps.accounts.tests.factories import cliente_para, crear_carrera, crear_usuario
from apps.locations.geo import filtro_recuadro, haversine_km
from apps.locations.models import PuntoReferencia
from apps.rides.tests.factories import crear_campus, crear_punto


class HaversineTests(SimpleTestCase):
    def test_misma_coordenada_es_cero(self):
        self.assertEqual(haversine_km(31.7, -106.4, 31.7, -106.4), 0)

    def test_distancia_conocida(self):
        # CU (31.4899, -106.4146) a ICSA (31.7568, -106.4499): ~29.8 km
        self.assertAlmostEqual(haversine_km(31.489920, -106.414574, 31.756756, -106.449914), 29.8, delta=0.3)

    def test_un_grado_de_latitud(self):
        self.assertAlmostEqual(haversine_km(31, -106, 32, -106), 111.2, delta=0.2)

    def test_recuadro_contiene_el_radio(self):
        caja = filtro_recuadro(31.7, -106.4, 3, prefijo="p__")
        self.assertLess(caja["p__latitud__gte"], 31.7 - 0.026)
        self.assertGreater(caja["p__longitud__lte"], -106.4 + 0.031)


class CatalogosApiTests(TestCase):
    def setUp(self):
        self.cliente = cliente_para(crear_usuario())

    def test_campus_solo_activos(self):
        crear_campus(codigo="CU")
        crear_campus(codigo="OLD", activo=False)
        respuesta = self.cliente.get("/api/campus/")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual([c["codigo"] for c in respuesta.data], ["CU"])

    def test_puntos_solo_activos_y_busqueda(self):
        crear_punto(nombre="Oxxo – Av. Tecnológico")
        crear_punto(nombre="Oxxo – Calle Sur")
        crear_punto(nombre="Oxxo – Tecnológico viejo", activo=False)
        respuesta = self.cliente.get("/api/puntos/", {"q": "tecno"})
        self.assertEqual([p["nombre"] for p in respuesta.data], ["Oxxo – Av. Tecnológico"])
        self.assertEqual(len(self.cliente.get("/api/puntos/").data), 2)

    def test_puntos_ordenados_por_cercania(self):
        lejos = crear_punto(latitud="31.75", longitud="-106.45")
        cerca = crear_punto(latitud="31.701", longitud="-106.401")
        respuesta = self.cliente.get("/api/puntos/", {"lat": 31.70, "lon": -106.40})
        self.assertEqual([p["id"] for p in respuesta.data], [cerca.id, lejos.id])
        self.assertLess(respuesta.data[0]["distancia_km"], 0.2)

    def test_lat_sin_lon_es_400(self):
        self.assertEqual(self.cliente.get("/api/puntos/", {"lat": 31.7}).status_code, 400)

    def test_puntos_requieren_sesion_verificada(self):
        self.assertEqual(cliente_para().get("/api/puntos/").status_code, 401)
        self.assertEqual(cliente_para(crear_usuario(correo_verificado=False)).get("/api/puntos/").status_code, 403)
        self.assertEqual(PuntoReferencia.objects.count(), 0)

    def test_campus_y_carreras_son_publicos(self):
        """El registro elige campus y carrera antes de tener sesión."""
        crear_carrera()
        self.assertEqual(cliente_para().get("/api/campus/").status_code, 200)
        self.assertEqual(cliente_para().get("/api/carreras/").status_code, 200)


class CarrerasApiTests(TestCase):
    def setUp(self):
        self.cu = crear_campus(codigo="CU")
        self.iit = crear_campus(codigo="IIT")
        self.software = crear_carrera(self.cu, nombre="Ingeniería de Software", area="Ingenierías")
        self.derecho_cu = crear_carrera(self.cu, nombre="Licenciatura en Derecho")
        self.mecatronica = crear_carrera(self.iit, nombre="Ingeniería en Mecatrónica")
        crear_carrera(self.cu, nombre="Carrera cerrada", activo=False)
        crear_carrera(crear_campus(codigo="OLD", activo=False), nombre="De campus inactivo")

    def test_lista_activas_de_campus_activos(self):
        datos = cliente_para().get("/api/carreras/").data
        self.assertEqual(
            {c["id"] for c in datos}, {self.software.id, self.derecho_cu.id, self.mecatronica.id}
        )
        software = next(c for c in datos if c["id"] == self.software.id)
        self.assertEqual(software, {"id": self.software.id, "campus": self.cu.id, "nombre": "Ingeniería de Software", "area": "Ingenierías"})

    def test_filtra_por_campus(self):
        datos = cliente_para().get("/api/carreras/", {"campus": self.iit.id}).data
        self.assertEqual([c["nombre"] for c in datos], ["Ingeniería en Mecatrónica"])
        self.assertEqual(cliente_para().get("/api/carreras/", {"campus": "abc"}).data, [])
