from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models_choices import PreferenciaCompatibilidad, Rol, Sexo
from apps.accounts.tests.factories import crear_conductor, crear_usuario, crear_vehiculo
from apps.rides.models import Viaje
from apps.rides.models_choices import EstadoSolicitud, EstadoViaje, SentidoViaje
from apps.rides.tests.factories import crear_campus, crear_punto, crear_solicitud, crear_viaje


class ViajeTests(TestCase):
    def setUp(self):
        self.conductor = crear_conductor(asientos=4)

    def viaje_sin_guardar(self, **datos):
        valores = {
            "conductor": self.conductor,
            "vehiculo": self.conductor.vehiculo,
            "punto_referencia": crear_punto(),
            "campus": crear_campus(),
            "fecha_hora": timezone.now() + timedelta(hours=2),
            "lugares_ofrecidos": 2,
        }
        valores.update(datos)
        return Viaje(**valores)

    def assertErrorEn(self, viaje, campo):
        with self.assertRaises(ValidationError) as ctx:
            viaje.full_clean()
        self.assertIn(campo, ctx.exception.message_dict)

    def test_crear_viaje_valido(self):
        viaje = crear_viaje(self.conductor, notas="Te espero en la entrada principal.")
        self.assertEqual(viaje.estado, EstadoViaje.PUBLICADO)
        self.assertEqual(viaje.sentido, SentidoViaje.HACIA_CAMPUS)
        self.assertEqual(viaje.lugares_disponibles, 3)

    def test_lugares_entre_1_y_5(self):
        self.assertErrorEn(self.viaje_sin_guardar(lugares_ofrecidos=0), "lugares_ofrecidos")
        conductor_grande = crear_conductor(asientos=5)
        self.assertErrorEn(
            self.viaje_sin_guardar(conductor=conductor_grande, vehiculo=conductor_grande.vehiculo, lugares_ofrecidos=6),
            "lugares_ofrecidos",
        )
        self.viaje_sin_guardar(conductor=conductor_grande, vehiculo=conductor_grande.vehiculo, lugares_ofrecidos=5).full_clean()

    def test_lugares_bloqueados_en_bd(self):
        viaje = self.viaje_sin_guardar(lugares_ofrecidos=6)
        with self.assertRaises(IntegrityError):
            viaje.save()

    def test_lugares_no_superan_asientos_del_vehiculo(self):
        self.assertErrorEn(self.viaje_sin_guardar(lugares_ofrecidos=5), "lugares_ofrecidos")  # vehículo de 4
        self.viaje_sin_guardar(lugares_ofrecidos=4).full_clean()

    def test_conductor_debe_tener_rol_conductor(self):
        pasajero = crear_usuario(rol=Rol.PASAJERO)
        vehiculo = crear_vehiculo(pasajero)
        self.assertErrorEn(self.viaje_sin_guardar(conductor=pasajero, vehiculo=vehiculo), "conductor")

    def test_vehiculo_debe_ser_del_conductor(self):
        otro = crear_conductor()
        self.assertErrorEn(self.viaje_sin_guardar(vehiculo=otro.vehiculo), "vehiculo")

    def test_vehiculo_debe_estar_activo(self):
        self.conductor.vehiculo.activo = False
        self.conductor.vehiculo.save()
        self.assertErrorEn(self.viaje_sin_guardar(), "vehiculo")

    def test_fecha_en_el_pasado_rechazada(self):
        self.assertErrorEn(self.viaje_sin_guardar(fecha_hora=timezone.now() - timedelta(minutes=1)), "fecha_hora")

    def test_viaje_existente_en_el_pasado_sigue_siendo_valido(self):
        viaje = crear_viaje(self.conductor)
        Viaje.objects.filter(pk=viaje.pk).update(fecha_hora=timezone.now() - timedelta(days=1))
        viaje.refresh_from_db()
        viaje.estado = EstadoViaje.FINALIZADO
        viaje.full_clean()  # editar un viaje pasado (ej. finalizarlo) no debe fallar por la fecha

    def test_punto_y_campus_deben_estar_activos(self):
        self.assertErrorEn(self.viaje_sin_guardar(punto_referencia=crear_punto(activo=False)), "punto_referencia")
        self.assertErrorEn(self.viaje_sin_guardar(campus=crear_campus(activo=False)), "campus")

    def test_notas_maximo_300(self):
        self.assertErrorEn(self.viaje_sin_guardar(notas="x" * 301), "notas")
        self.viaje_sin_guardar(notas="x" * 300).full_clean()

    def test_preferencia_por_defecto_es_la_del_conductor(self):
        conductor = crear_conductor(preferencia_compatibilidad=PreferenciaCompatibilidad.MISMO_SEXO)
        self.assertEqual(crear_viaje(conductor).preferencia_compatibilidad, PreferenciaCompatibilidad.MISMO_SEXO)
        viaje = crear_viaje(conductor, preferencia_compatibilidad=PreferenciaCompatibilidad.MIXTO)
        self.assertEqual(viaje.preferencia_compatibilidad, PreferenciaCompatibilidad.MIXTO)

    def test_lugares_disponibles_y_lleno(self):
        viaje = crear_viaje(self.conductor, lugares_ofrecidos=2)
        p1, p2, p3 = (crear_usuario() for _ in range(3))
        crear_solicitud(viaje, p1, estado=EstadoSolicitud.ACEPTADA)
        crear_solicitud(viaje, p2)  # pendiente: no ocupa lugar
        self.assertEqual(viaje.lugares_ocupados, 1)
        self.assertEqual(viaje.lugares_disponibles, 1)
        self.assertFalse(viaje.esta_lleno)

        crear_solicitud(viaje, p3, estado=EstadoSolicitud.ACEPTADA)
        self.assertTrue(viaje.esta_lleno)
        self.assertEqual(set(viaje.pasajeros_confirmados), {p1, p3})

    def test_no_reducir_lugares_por_debajo_de_aceptados(self):
        viaje = crear_viaje(self.conductor, lugares_ofrecidos=3)
        for _ in range(2):
            crear_solicitud(viaje, crear_usuario(), estado=EstadoSolicitud.ACEPTADA)
        viaje.lugares_ofrecidos = 1
        self.assertErrorEn(viaje, "lugares_ofrecidos")

    def test_es_participante(self):
        viaje = crear_viaje(self.conductor)
        aceptado, pendiente, ajeno = crear_usuario(), crear_usuario(), crear_usuario()
        crear_solicitud(viaje, aceptado, estado=EstadoSolicitud.ACEPTADA)
        crear_solicitud(viaje, pendiente)
        self.assertTrue(viaje.es_participante(self.conductor))
        self.assertTrue(viaje.es_participante(aceptado))
        self.assertFalse(viaje.es_participante(pendiente))
        self.assertFalse(viaje.es_participante(ajeno))

    def test_transiciones_de_estado(self):
        viaje = crear_viaje(self.conductor)
        self.assertTrue(viaje.puede_cambiar_a(EstadoViaje.EN_CURSO))
        self.assertTrue(viaje.puede_cambiar_a(EstadoViaje.CANCELADO))
        self.assertFalse(viaje.puede_cambiar_a(EstadoViaje.FINALIZADO))
        viaje.estado = EstadoViaje.EN_CURSO
        self.assertTrue(viaje.puede_cambiar_a(EstadoViaje.FINALIZADO))
        self.assertFalse(viaje.puede_cambiar_a(EstadoViaje.CANCELADO))
        viaje.estado = EstadoViaje.FINALIZADO
        self.assertFalse(viaje.puede_cambiar_a(EstadoViaje.PUBLICADO))

    def test_no_se_borra_conductor_con_viajes(self):
        from django.db.models import ProtectedError

        crear_viaje(self.conductor)
        with self.assertRaises(ProtectedError):
            self.conductor.delete()


class SolicitudTests(TestCase):
    def setUp(self):
        self.conductor = crear_conductor()
        self.viaje = crear_viaje(self.conductor)
        self.pasajero = crear_usuario(sexo=Sexo.F)

    def test_solicitud_valida(self):
        solicitud = crear_solicitud(self.viaje, self.pasajero)
        solicitud.full_clean()
        self.assertEqual(solicitud.estado, EstadoSolicitud.PENDIENTE)
        self.assertTrue(solicitud.esta_activa)
        self.assertIsNone(solicitud.respondida_en)

    def test_conductor_no_puede_solicitar_su_viaje(self):
        conductor_ambos = crear_conductor(rol=Rol.AMBOS)
        viaje = crear_viaje(conductor_ambos)
        solicitud = crear_solicitud(viaje, conductor_ambos)
        with self.assertRaises(ValidationError) as ctx:
            solicitud.full_clean()
        self.assertIn("pasajero", ctx.exception.message_dict)

    def test_pasajero_debe_tener_rol_pasajero(self):
        solicitud = crear_solicitud(self.viaje, crear_conductor())
        with self.assertRaises(ValidationError):
            solicitud.full_clean()

    def test_preferencia_por_defecto_es_la_del_pasajero(self):
        pasajero = crear_usuario(preferencia_compatibilidad=PreferenciaCompatibilidad.MISMO_SEXO)
        self.assertEqual(
            crear_solicitud(self.viaje, pasajero).preferencia_compatibilidad, PreferenciaCompatibilidad.MISMO_SEXO
        )

    def test_una_sola_solicitud_activa_por_viaje(self):
        crear_solicitud(self.viaje, self.pasajero)
        with self.assertRaises(IntegrityError), transaction.atomic():
            crear_solicitud(self.viaje, self.pasajero)

    def test_unica_tambien_con_aceptada(self):
        crear_solicitud(self.viaje, self.pasajero, estado=EstadoSolicitud.ACEPTADA)
        with self.assertRaises(IntegrityError), transaction.atomic():
            crear_solicitud(self.viaje, self.pasajero)

    def test_puede_volver_a_solicitar_tras_rechazo_o_cancelacion(self):
        crear_solicitud(self.viaje, self.pasajero, estado=EstadoSolicitud.RECHAZADA)
        crear_solicitud(self.viaje, self.pasajero, estado=EstadoSolicitud.CANCELADA)
        nueva = crear_solicitud(self.viaje, self.pasajero)
        self.assertEqual(self.viaje.solicitudes.count(), 3)
        self.assertTrue(nueva.esta_activa)

    def test_validate_constraints_detecta_duplicado(self):
        from apps.rides.models import Solicitud

        crear_solicitud(self.viaje, self.pasajero)
        with self.assertRaises(ValidationError):
            Solicitud(viaje=self.viaje, pasajero=self.pasajero).full_clean()

    def test_transiciones_de_estado(self):
        solicitud = crear_solicitud(self.viaje, self.pasajero)
        for estado in (EstadoSolicitud.ACEPTADA, EstadoSolicitud.RECHAZADA, EstadoSolicitud.CANCELADA):
            self.assertTrue(solicitud.puede_cambiar_a(estado))
        solicitud.estado = EstadoSolicitud.ACEPTADA
        self.assertTrue(solicitud.puede_cambiar_a(EstadoSolicitud.CANCELADA))
        self.assertFalse(solicitud.puede_cambiar_a(EstadoSolicitud.RECHAZADA))
        solicitud.estado = EstadoSolicitud.RECHAZADA
        self.assertFalse(solicitud.puede_cambiar_a(EstadoSolicitud.ACEPTADA))

    def test_se_borran_con_el_viaje(self):
        crear_solicitud(self.viaje, self.pasajero)
        self.viaje.delete()
        self.assertFalse(self.pasajero.solicitudes.exists())
