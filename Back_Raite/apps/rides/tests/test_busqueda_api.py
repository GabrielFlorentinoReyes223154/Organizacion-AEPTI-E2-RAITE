"""Búsqueda por cercanía (haversine), campus, sentido y horario, con compatibilidad por sexo (RF-04, RF-07)."""

from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status

from apps.accounts.models_choices import PreferenciaCompatibilidad as Pref
from apps.accounts.models_choices import Sexo
from apps.accounts.tests.factories import cliente_para, crear_conductor, crear_usuario
from apps.rides.compatibilidad import grupo_compatible
from apps.rides.models import Viaje
from apps.rides.models_choices import EstadoSolicitud, EstadoViaje
from apps.rides.tests.factories import crear_campus, crear_punto, crear_solicitud, crear_viaje


class GrupoCompatibleTests(TestCase):
    def test_reglas(self):
        M, F, X = Sexo.M, Sexo.F, Sexo.X
        casos = [
            ([(M, Pref.MIXTO), (F, Pref.MIXTO)], True),
            ([(M, Pref.MISMO_SEXO), (F, Pref.MIXTO)], False),
            ([(M, Pref.MIXTO), (F, Pref.MISMO_SEXO)], False),
            ([(F, Pref.MISMO_SEXO), (F, Pref.MIXTO), (F, Pref.MISMO_SEXO)], True),
            ([(X, Pref.MISMO_SEXO), (X, Pref.MIXTO)], True),
            ([(X, Pref.MISMO_SEXO), (M, Pref.MIXTO)], False),
        ]
        for integrantes, esperado in casos:
            with self.subTest(integrantes=integrantes):
                self.assertEqual(grupo_compatible(integrantes), esperado)


@override_settings(BUSQUEDA_RADIO_KM=3, BUSQUEDA_RADIO_MAX_KM=15)
class BusquedaTests(TestCase):
    def setUp(self):
        self.pasajero = crear_usuario(sexo=Sexo.F)
        self.cliente = cliente_para(self.pasajero)
        self.centro = crear_punto(latitud="31.700000", longitud="-106.400000")
        self.cerca = crear_punto(latitud="31.710000", longitud="-106.400000")  # ~1.1 km
        self.lejos = crear_punto(latitud="31.750000", longitud="-106.400000")  # ~5.6 km
        self.campus = crear_campus()

    def buscar(self, **filtros):
        respuesta = self.cliente.get("/api/viajes/", filtros)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK, respuesta.data)
        return [v["id"] for v in respuesta.data["results"]], respuesta.data

    def viaje(self, **datos):
        datos.setdefault("campus", self.campus)
        return crear_viaje(**datos)

    def test_radio_y_orden_por_distancia(self):
        en_centro = self.viaje(punto_referencia=self.centro)
        cerca = self.viaje(punto_referencia=self.cerca)
        lejos = self.viaje(punto_referencia=self.lejos)
        ids, datos = self.buscar(punto=self.centro.id)
        self.assertEqual(ids, [str(en_centro.pk), str(cerca.pk)])
        self.assertAlmostEqual(datos["results"][1]["distancia_km"], 1.11, delta=0.05)
        ids, _ = self.buscar(punto=self.centro.id, radio_km=10)
        self.assertEqual(ids, [str(en_centro.pk), str(cerca.pk), str(lejos.pk)])
        ids, _ = self.buscar(lat=31.75, lon=-106.40, radio_km=1)
        self.assertEqual(ids, [str(lejos.pk)])

    def test_sin_ubicacion_ordena_por_hora(self):
        tarde = self.viaje(fecha_hora=timezone.now() + timedelta(days=2))
        temprano = self.viaje(fecha_hora=timezone.now() + timedelta(days=1))
        ids, datos = self.buscar()
        self.assertEqual(ids, [str(temprano.pk), str(tarde.pk)])
        self.assertIsNone(datos["results"][0]["distancia_km"])

    def test_filtros_de_campus_sentido_y_horario(self):
        otro_campus = crear_campus()
        manana = timezone.now() + timedelta(days=1)
        a = self.viaje(fecha_hora=manana)
        b = self.viaje(campus=otro_campus, fecha_hora=manana + timedelta(hours=3))
        c = self.viaje(sentido="DESDE_CAMPUS", fecha_hora=manana + timedelta(hours=6))
        self.assertEqual(self.buscar(campus=otro_campus.id)[0], [str(b.pk)])
        self.assertEqual(self.buscar(sentido="DESDE_CAMPUS")[0], [str(c.pk)])
        desde = (manana + timedelta(hours=1)).isoformat()
        hasta = (manana + timedelta(hours=4)).isoformat()
        self.assertEqual(self.buscar(desde=desde, hasta=hasta)[0], [str(b.pk)])
        self.assertEqual(len(self.buscar()[0]), 3)
        self.assertIsNotNone(a)

    def test_excluye_propios_llenos_pasados_vencidos_y_no_publicados(self):
        visible = self.viaje()
        ambos = crear_conductor(rol=4)  # AMBOS: busca y también publica
        propio = self.viaje(conductor=ambos, fecha_hora=timezone.now() + timedelta(days=2))
        lleno = self.viaje(lugares_ofrecidos=1)
        crear_solicitud(lleno, crear_usuario(), estado=EstadoSolicitud.ACEPTADA)
        pasado = self.viaje()
        Viaje.objects.filter(pk=pasado.pk).update(fecha_hora=timezone.now() - timedelta(minutes=30))
        vencido = self.viaje()
        Viaje.objects.filter(pk=vencido.pk).update(fecha_hora=timezone.now() - timedelta(hours=3))
        self.viaje(estado=EstadoViaje.CANCELADO)
        self.viaje(estado=EstadoViaje.EN_CURSO)

        self.assertEqual(self.buscar()[0], [str(visible.pk), str(propio.pk)])
        ids_ambos = [v["id"] for v in cliente_para(ambos).get("/api/viajes/").data["results"]]
        self.assertEqual(ids_ambos, [str(visible.pk)])  # su propio viaje no le aparece

    def test_lugares_disponibles_descuenta_aceptados(self):
        viaje = self.viaje(lugares_ofrecidos=3)
        crear_solicitud(viaje, crear_usuario(), estado=EstadoSolicitud.ACEPTADA)
        crear_solicitud(viaje, crear_usuario())  # pendiente: no ocupa lugar
        self.assertEqual(self.buscar()[1]["results"][0]["lugares_disponibles"], 2)

    def test_resultados_sin_contacto(self):
        self.viaje()
        resultado = self.buscar()[1]["results"][0]
        self.assertNotIn("telefono", resultado["conductor"])
        self.assertNotIn("placas", resultado["vehiculo"])

    # --- Compatibilidad ---

    def test_mujer_mismo_sexo_no_ve_viaje_de_conductor_hombre(self):
        self.pasajero.preferencia_compatibilidad = Pref.MISMO_SEXO
        self.pasajero.save()
        de_hombre = self.viaje(conductor=crear_conductor(sexo=Sexo.M))
        de_mujer = self.viaje(conductor=crear_conductor(sexo=Sexo.F))
        self.assertEqual(self.buscar()[0], [str(de_mujer.pk)])
        self.assertIsNotNone(de_hombre)

    def test_mujer_mismo_sexo_no_ve_viaje_con_hombres_aceptados(self):
        self.pasajero.preferencia_compatibilidad = Pref.MISMO_SEXO
        self.pasajero.save()
        viaje = self.viaje(conductor=crear_conductor(sexo=Sexo.F))
        self.assertEqual(len(self.buscar()[0]), 1)
        crear_solicitud(viaje, crear_usuario(sexo=Sexo.M), estado=EstadoSolicitud.ACEPTADA)
        self.assertEqual(self.buscar()[0], [])

    def test_viaje_mismo_sexo_oculto_al_otro_sexo(self):
        conductor = crear_conductor(sexo=Sexo.M, preferencia_compatibilidad=Pref.MISMO_SEXO)
        viaje = self.viaje(conductor=conductor)
        self.assertEqual(self.buscar()[0], [])  # pasajera F mixta
        hombre = cliente_para(crear_usuario(sexo=Sexo.M))
        self.assertEqual([v["id"] for v in hombre.get("/api/viajes/").data["results"]], [str(viaje.pk)])

    def test_pasajero_aceptado_mismo_sexo_restringe_al_viaje(self):
        viaje = self.viaje(conductor=crear_conductor(sexo=Sexo.F))
        crear_solicitud(viaje, crear_usuario(sexo=Sexo.F), estado=EstadoSolicitud.ACEPTADA, preferencia_compatibilidad=Pref.MISMO_SEXO)
        self.assertEqual(len(self.buscar()[0]), 1)  # F mixta sí entra
        hombre = cliente_para(crear_usuario(sexo=Sexo.M))
        self.assertEqual(hombre.get("/api/viajes/").data["results"], [])

    def test_x_mismo_sexo_solo_empata_con_x(self):
        x = cliente_para(crear_usuario(sexo=Sexo.X, preferencia_compatibilidad=Pref.MISMO_SEXO))
        con_x = self.viaje(conductor=crear_conductor(sexo=Sexo.X))
        self.viaje(conductor=crear_conductor(sexo=Sexo.F))
        self.assertEqual([v["id"] for v in x.get("/api/viajes/").data["results"]], [str(con_x.pk)])

    # --- Validación de filtros ---

    def test_filtros_invalidos(self):
        casos = [
            {"lat": 31.7},
            {"punto": self.centro.id, "lat": 31.7, "lon": -106.4},
            {"radio_km": 50},
            {"sentido": "OTRO"},
            {"desde": "2030-01-02T00:00", "hasta": "2030-01-01T00:00"},
            {"punto": crear_punto(activo=False).id},
        ]
        for filtros in casos:
            with self.subTest(filtros=filtros):
                self.assertEqual(self.cliente.get("/api/viajes/", filtros).status_code, 400)

    def test_requiere_sesion_verificada(self):
        self.assertEqual(cliente_para().get("/api/viajes/").status_code, 401)
        self.assertEqual(cliente_para(crear_usuario(correo_verificado=False)).get("/api/viajes/").status_code, 403)
