import json
import tempfile
from io import StringIO
from pathlib import Path
from unittest import mock

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase

from apps.locations import osm
from apps.locations.models import Campus, PuntoReferencia

DATOS_REALES = Path(__file__).resolve().parents[1] / "data"

OVERPASS = {
    "elements": [
        {"type": "node", "id": 3, "lat": 31.70, "lon": -106.40, "tags": {"name": "Oxxo", "shop": "convenience"}},
        {"type": "node", "id": 1, "lat": 31.71, "lon": -106.41, "tags": {"name": "OXXO", "shop": "convenience"}},
        {"type": "way", "id": 2, "center": {"lat": 31.72, "lon": -106.42}, "tags": {"name": "Oxxo", "amenity": "fuel"}},
        {"type": "node", "id": 4, "lat": 31.73, "lon": -106.43, "tags": {"name": "Centro de distribución Oxxo"}},
        {"type": "node", "id": 5, "lat": 31.74, "lon": -106.44, "tags": {"name": "CEDIS Oxxo"}},
        {"type": "node", "id": 6, "lat": 25.60, "lon": -100.10, "tags": {"name": "Oxxo", "shop": "convenience"}},
        {"type": "way", "id": 7, "nodes": [], "tags": {"name": "Oxxo"}},
    ]
}


def respuesta(calle="", colonia=""):
    direccion = {}
    if calle:
        direccion["road"] = calle
    if colonia:
        direccion["suburb"] = colonia
    return {"address": direccion}


class ExtraerPuntosTests(SimpleTestCase):
    def test_filtra_y_clasifica(self):
        puntos, descartados = osm.extraer_puntos(OVERPASS)
        self.assertEqual([p["osm_id"] for p in puntos], ["node/1", "node/3", "way/2"])
        self.assertEqual({p["osm_id"]: p["marca"] for p in puntos}["way/2"], "Oxxo Gas")
        self.assertEqual(descartados["no es tienda (centro de distribución)"], 2)
        self.assertEqual(descartados["fuera de Ciudad Juárez"], 1)
        self.assertEqual(descartados["sin coordenadas"], 1)

    def test_coordenadas_con_seis_decimales(self):
        puntos, _ = osm.extraer_puntos(
            {"elements": [{"type": "node", "id": 1, "lat": 31.69377712, "lon": -106.374282, "tags": {"name": "Oxxo"}}]}
        )
        self.assertEqual((puntos[0]["latitud"], puntos[0]["longitud"]), ("31.693777", "-106.374282"))


class NombrarPuntosTests(SimpleTestCase):
    def setUp(self):
        self.puntos, _ = osm.extraer_puntos(OVERPASS)

    def test_nombre_con_calle_y_colonia(self):
        resultado = osm.nombrar_puntos(self.puntos[:1], lambda lat, lon: respuesta("Av. de las Torres", "Las Dunas"))
        self.assertEqual(resultado[0]["nombre"], "Oxxo – Av. de las Torres, Col. Las Dunas")
        self.assertTrue(resultado[0]["activo"])

    def test_sin_calle_o_colonia_queda_inactivo(self):
        casos = [
            (respuesta(), "Oxxo – (sin calle)"),
            (respuesta(calle="Av. Tecnológico"), "Oxxo – Av. Tecnológico"),
            (respuesta(colonia="Centro"), "Oxxo – Col. Centro"),
        ]
        for resp, nombre in casos:
            with self.subTest(nombre=nombre):
                resultado = osm.nombrar_puntos(self.puntos[:1], lambda lat, lon, r=resp: r)
                self.assertEqual(resultado[0]["nombre"], nombre)
                self.assertFalse(resultado[0]["activo"])

    def test_fallo_de_red_deja_punto_inactivo(self):
        def falla(lat, lon):
            raise OSError("sin red")

        resultado = osm.nombrar_puntos(self.puntos, falla)
        self.assertEqual(len(resultado), 3)
        self.assertTrue(all(not p["activo"] for p in resultado))

    def test_desambigua_nombres_repetidos(self):
        resultado = osm.nombrar_puntos(self.puntos[:2], lambda lat, lon: respuesta("Av. Juárez", "Centro"))
        self.assertEqual(
            [p["nombre"] for p in resultado],
            ["Oxxo – Av. Juárez, Col. Centro", "Oxxo – Av. Juárez, Col. Centro (2)"],
        )

    def test_gasolinera_lleva_su_marca(self):
        resultado = osm.nombrar_puntos(self.puntos[2:], lambda lat, lon: respuesta("Blvd. Zaragoza", "Infonavit"))
        self.assertEqual(resultado[0]["nombre"], "Oxxo Gas – Blvd. Zaragoza, Col. Infonavit")


class GenerarPuntosOsmComandoTests(SimpleTestCase):
    def test_escribe_json_sin_usar_internet(self):
        with tempfile.TemporaryDirectory() as tmp:
            entrada, salida = Path(tmp, "oxxo.json"), Path(tmp, "salida.json")
            entrada.write_text(json.dumps(OVERPASS), encoding="utf-8")
            with mock.patch.object(osm, "geocodificar_inverso", return_value=respuesta("Calle 1", "Col 1")) as geo:
                call_command("generar_puntos_osm", entrada=str(entrada), salida=str(salida), pausa=0, stdout=StringIO())
            self.assertEqual(geo.call_count, 3)
            datos = json.loads(salida.read_text(encoding="utf-8"))
            self.assertEqual(len(datos), 3)
            self.assertEqual(
                set(datos[0]), {"osm_id", "nombre", "calle", "colonia", "latitud", "longitud", "activo"}
            )


class CargarDatosInicialesTests(TestCase):
    def escribir(self, carpeta, nombre, datos):
        ruta = Path(carpeta, nombre)
        ruta.write_text(json.dumps(datos), encoding="utf-8")
        return str(ruta)

    def test_carga_y_es_idempotente(self):
        campus = [
            {"codigo": c, "nombre": f"Campus {c}", "latitud": "31.742765", "longitud": "-106.431511"}
            for c in ("CU", "IIT", "ICB", "ICSA", "IADA")
        ]
        puntos = [
            {"osm_id": "node/1", "nombre": "Oxxo – A, Col. B", "latitud": "31.70", "longitud": "-106.40", "activo": True},
            {"osm_id": "node/2", "nombre": "Oxxo – (sin calle)", "latitud": "31.71", "longitud": "-106.41", "activo": False},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            args = {"campus": self.escribir(tmp, "c.json", campus), "puntos": self.escribir(tmp, "p.json", puntos)}
            call_command("cargar_datos_iniciales", stdout=StringIO(), **args)
            self.assertEqual(Campus.objects.count(), 5)
            self.assertEqual(PuntoReferencia.objects.count(), 2)
            self.assertFalse(PuntoReferencia.objects.get(osm_id="node/2").activo)

            # Cambios hechos en el admin no se pisan al recargar
            PuntoReferencia.objects.filter(osm_id="node/2").update(nombre="Oxxo Dunas", activo=True)

            salida = StringIO()
            call_command("cargar_datos_iniciales", stdout=salida, **args)
            self.assertEqual(Campus.objects.count(), 5)
            self.assertEqual(PuntoReferencia.objects.count(), 2)
            punto = PuntoReferencia.objects.get(osm_id="node/2")
            self.assertEqual((punto.nombre, punto.activo), ("Oxxo Dunas", True))
            self.assertIn("0 creados, 5 actualizados", salida.getvalue())

    def test_rechaza_coordenadas_fuera_de_juarez(self):
        from django.core.exceptions import ValidationError

        puntos = [{"osm_id": "node/9", "nombre": "Oxxo", "latitud": "25.6", "longitud": "-100.1"}]
        with tempfile.TemporaryDirectory() as tmp:
            args = {"campus": self.escribir(tmp, "c.json", []), "puntos": self.escribir(tmp, "p.json", puntos)}
            with self.assertRaises(ValidationError):
                call_command("cargar_datos_iniciales", stdout=StringIO(), **args)
        self.assertEqual(PuntoReferencia.objects.count(), 0)

    def test_archivos_versionados_son_validos(self):
        """Los JSON reales del repo deben cargar sin errores."""
        call_command("cargar_datos_iniciales", stdout=StringIO())
        self.assertEqual(
            set(Campus.objects.values_list("codigo", flat=True)), {"CU", "IIT", "ICB", "ICSA", "IADA"}
        )
        self.assertGreater(PuntoReferencia.objects.count(), 100)
