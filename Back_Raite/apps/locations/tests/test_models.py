from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from apps.locations.models import Campus, PuntoReferencia, esta_en_juarez

# IIT, Ciudad Juárez
LAT, LON = Decimal("31.742765"), Decimal("-106.431511")


class CampusTests(TestCase):
    def test_crear_campus_valido(self):
        campus = Campus.objects.create(codigo="IIT", nombre="Ingeniería", latitud=LAT, longitud=LON)
        campus.full_clean()
        self.assertTrue(campus.activo)
        self.assertEqual(str(campus), "IIT – Ingeniería")

    def test_codigo_unico(self):
        Campus.objects.create(codigo="CU", nombre="CU", latitud=LAT, longitud=LON)
        with self.assertRaises(IntegrityError):
            Campus.objects.create(codigo="CU", nombre="Otro", latitud=LAT, longitud=LON)

    def test_coordenadas_fuera_de_juarez_rechazadas(self):
        # Monterrey y Chihuahua capital
        for lat, lon in ((Decimal("25.686"), Decimal("-100.316")), (Decimal("28.632"), Decimal("-106.069"))):
            with self.subTest(lat=lat, lon=lon):
                campus = Campus(codigo="X", nombre="Fuera", latitud=lat, longitud=lon)
                with self.assertRaises(ValidationError):
                    campus.full_clean()


class PuntoReferenciaTests(TestCase):
    def test_crear_punto_valido(self):
        punto = PuntoReferencia.objects.create(nombre="Oxxo – Av. de las Torres", latitud=LAT, longitud=LON)
        punto.full_clean()
        self.assertTrue(punto.activo)
        self.assertIsNone(punto.osm_id)

    def test_osm_id_unico_pero_opcional(self):
        PuntoReferencia.objects.create(nombre="A", latitud=LAT, longitud=LON)
        PuntoReferencia.objects.create(nombre="B", latitud=LAT, longitud=LON)  # dos sin osm_id
        PuntoReferencia.objects.create(nombre="C", latitud=LAT, longitud=LON, osm_id="node/1")
        with self.assertRaises(IntegrityError):
            PuntoReferencia.objects.create(nombre="D", latitud=LAT, longitud=LON, osm_id="node/1")

    def test_coordenadas_fuera_de_juarez_rechazadas(self):
        punto = PuntoReferencia(nombre="Oxxo Monterrey", latitud=Decimal("25.6"), longitud=Decimal("-100.1"))
        with self.assertRaises(ValidationError) as ctx:
            punto.full_clean()
        self.assertIn("latitud", ctx.exception.message_dict)
        self.assertIn("longitud", ctx.exception.message_dict)

    def test_esta_en_juarez(self):
        self.assertTrue(esta_en_juarez(LAT, LON))
        self.assertTrue(esta_en_juarez(31.48992, -106.414574))  # CU
        self.assertFalse(esta_en_juarez(25.6, -100.1))
