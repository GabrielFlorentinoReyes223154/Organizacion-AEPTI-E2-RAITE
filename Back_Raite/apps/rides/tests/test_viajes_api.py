"""Publicar, editar y cambiar estado de viajes (RF-02, RF-03), incluido el vencimiento calculado."""

from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status

from apps.accounts.models_choices import Rol, Sexo
from apps.accounts.tests.factories import cliente_para, crear_conductor, crear_usuario
from apps.notifications.models import Notificacion
from apps.notifications.models_choices import TipoNotificacion
from apps.rides.models import Viaje
from apps.rides.models_choices import EstadoSolicitud, EstadoViaje
from apps.rides.tests.factories import crear_campus, crear_punto, crear_solicitud, crear_viaje


def mover(viaje, **delta):
    """Cambia la hora del viaje sin pasar por full_clean (para simular el paso del tiempo)."""
    Viaje.objects.filter(pk=viaje.pk).update(fecha_hora=timezone.now() + timedelta(**delta))
    viaje.refresh_from_db()
    return viaje


@override_settings(VENTANA_CRUCE_MINUTOS=60, INICIO_ANTICIPACION_MINUTOS=30, VENCIMIENTO_HORAS=2)
class PublicarViajeTests(TestCase):
    def setUp(self):
        self.conductor = crear_conductor(asientos=4)
        self.cliente = cliente_para(self.conductor)
        self.punto, self.campus = crear_punto(), crear_campus()

    def datos(self, **cambios):
        valores = {
            "punto_referencia": self.punto.id,
            "campus": self.campus.id,
            "sentido": "HACIA_CAMPUS",
            "fecha_hora": (timezone.now() + timedelta(days=1)).isoformat(),
            "lugares_ofrecidos": 3,
            "notas": "Paso por el estacionamiento.",
        }
        valores.update(cambios)
        return valores

    def publicar(self, cliente=None, **cambios):
        return (cliente or self.cliente).post("/api/viajes/", self.datos(**cambios), format="json")

    def test_publicar(self):
        respuesta = self.publicar()
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED, respuesta.data)
        viaje = Viaje.objects.get()
        self.assertEqual((viaje.conductor, viaje.vehiculo), (self.conductor, self.conductor.vehiculo))
        self.assertEqual(respuesta.data["estado"], EstadoViaje.PUBLICADO)
        self.assertEqual(respuesta.data["lugares_disponibles"], 3)
        self.assertEqual(respuesta.data["preferencia_compatibilidad"], self.conductor.preferencia_compatibilidad)
        # El conductor ve sus propias placas
        self.assertEqual(respuesta.data["vehiculo"]["placas"], self.conductor.vehiculo.placas)

    def test_hora_sin_zona_se_toma_de_juarez(self):
        manana = timezone.localtime() + timedelta(days=1)
        respuesta = self.publicar(fecha_hora=manana.strftime("%Y-%m-%dT08:00:00"))
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED, respuesta.data)
        self.assertEqual(timezone.localtime(Viaje.objects.get().fecha_hora).hour, 8)

    def test_quien_no_puede_publicar(self):
        casos = {
            "pasajero": crear_usuario(rol=Rol.PASAJERO),
            "sin vehículo": crear_conductor(con_vehiculo=False),
            "suspendido": crear_conductor(suspendido=True),
            "sin verificar": crear_conductor(correo_verificado=False),
        }
        for nombre, usuario in casos.items():
            with self.subTest(nombre):
                self.assertEqual(self.publicar(cliente_para(usuario)).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.publicar(cliente_para()).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_validaciones_del_modelo_desde_el_api(self):
        casos = {
            "fecha_hora": {"fecha_hora": (timezone.now() - timedelta(hours=1)).isoformat()},
            "lugares_ofrecidos": {"lugares_ofrecidos": 5},  # el vehículo tiene 4
            "notas": {"notas": "x" * 301},
        }
        for campo, cambios in casos.items():
            with self.subTest(campo):
                respuesta = self.publicar(**cambios)
                self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(campo, respuesta.data)

    def test_punto_o_campus_inactivo(self):
        self.assertEqual(self.publicar(punto_referencia=crear_punto(activo=False).id).status_code, 400)
        self.assertEqual(self.publicar(campus=crear_campus(activo=False).id).status_code, 400)

    def test_cruce_con_otro_viaje_propio(self):
        manana = timezone.now() + timedelta(days=1)
        crear_viaje(self.conductor, fecha_hora=manana)
        respuesta = self.publicar(fecha_hora=(manana + timedelta(minutes=45)).isoformat())
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(self.publicar(fecha_hora=(manana + timedelta(minutes=61)).isoformat()).status_code, 201)

    def test_cruce_con_solicitud_propia_como_pasajero(self):
        ambos = crear_conductor(rol=Rol.AMBOS)
        manana = timezone.now() + timedelta(days=1)
        crear_solicitud(crear_viaje(fecha_hora=manana), ambos)
        respuesta = self.publicar(cliente_para(ambos), fecha_hora=(manana + timedelta(minutes=30)).isoformat())
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)

    def test_viaje_vencido_no_cuenta_para_cruce(self):
        vencido = crear_viaje(self.conductor)
        mover(vencido, hours=-3)
        respuesta = self.publicar(fecha_hora=(timezone.now() + timedelta(minutes=10)).isoformat())
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED, respuesta.data)

    def test_viaje_cancelado_no_cuenta_para_cruce(self):
        manana = timezone.now() + timedelta(days=1)
        viaje = crear_viaje(self.conductor, fecha_hora=manana, estado=EstadoViaje.CANCELADO)
        self.assertEqual(viaje.estado, EstadoViaje.CANCELADO)
        self.assertEqual(self.publicar(fecha_hora=manana.isoformat()).status_code, 201)


class VencimientoModeloTests(TestCase):
    @override_settings(VENCIMIENTO_HORAS=2)
    def test_vencido_se_calcula_con_la_fecha(self):
        viaje = crear_viaje()
        self.assertFalse(viaje.esta_vencido)
        self.assertFalse(mover(viaje, hours=-1).esta_vencido)  # pasó la hora, pero no 2 h
        self.assertTrue(mover(viaje, hours=-3).esta_vencido)
        self.assertIn(viaje, Viaje.objects.vencidos())
        self.assertNotIn(viaje, Viaje.objects.vigentes())
        self.assertEqual(viaje.estado, EstadoViaje.PUBLICADO)  # no hay estado nuevo

    def test_en_curso_nunca_vence(self):
        viaje = crear_viaje(estado=EstadoViaje.EN_CURSO)
        mover(viaje, hours=-10)
        self.assertFalse(viaje.esta_vencido)
        self.assertIn(viaje, Viaje.objects.vigentes())


@override_settings(INICIO_ANTICIPACION_MINUTOS=30, VENCIMIENTO_HORAS=2)
class EstadosViajeTests(TestCase):
    def setUp(self):
        self.conductor = crear_conductor()
        self.cliente = cliente_para(self.conductor)
        self.viaje = crear_viaje(self.conductor)

    def accion(self, nombre, cliente=None, viaje=None):
        viaje = viaje or self.viaje
        return (cliente or self.cliente).post(f"/api/viajes/{viaje.pk}/{nombre}/")

    def recargar(self):
        self.viaje.refresh_from_db()
        return self.viaje

    def test_iniciar_antes_de_30_minutos_es_409(self):
        mover(self.viaje, minutes=31)
        respuesta = self.accion("iniciar")
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("Podrás iniciar", str(respuesta.data["detail"]))
        self.assertEqual(self.recargar().estado, EstadoViaje.PUBLICADO)

    def test_iniciar_desde_30_minutos_antes(self):
        mover(self.viaje, minutes=29)
        self.assertEqual(self.accion("iniciar").status_code, status.HTTP_200_OK)
        self.assertEqual(self.recargar().estado, EstadoViaje.EN_CURSO)

    def test_iniciar_con_retraso_menor_a_2_horas(self):
        mover(self.viaje, minutes=-90)
        self.assertEqual(self.accion("iniciar").status_code, status.HTTP_200_OK)

    def test_vencido_no_se_inicia_ni_edita_pero_si_se_cancela(self):
        mover(self.viaje, hours=-3)
        respuesta = self.accion("iniciar")
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("venció", str(respuesta.data["detail"]))
        respuesta = self.cliente.patch(f"/api/viajes/{self.viaje.pk}/", {"notas": "x"}, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(self.accion("cancelar").status_code, status.HTTP_200_OK)
        self.assertEqual(self.recargar().estado, EstadoViaje.CANCELADO)

    def test_iniciar_rechaza_pendientes_y_conserva_aceptadas(self):
        pendiente = crear_solicitud(self.viaje, crear_usuario())
        aceptada = crear_solicitud(self.viaje, crear_usuario(), estado=EstadoSolicitud.ACEPTADA)
        mover(self.viaje, minutes=10)
        self.accion("iniciar")
        pendiente.refresh_from_db()
        aceptada.refresh_from_db()
        self.assertEqual((pendiente.estado, aceptada.estado), (EstadoSolicitud.RECHAZADA, EstadoSolicitud.ACEPTADA))
        self.assertIsNotNone(pendiente.respondida_en)
        self.assertTrue(
            Notificacion.objects.filter(usuario=pendiente.pasajero, tipo=TipoNotificacion.SOLICITUD_RECHAZADA).exists()
        )

    def test_finalizar_notifica_a_los_aceptados(self):
        aceptada = crear_solicitud(self.viaje, crear_usuario(), estado=EstadoSolicitud.ACEPTADA)
        mover(self.viaje, minutes=10)
        self.accion("iniciar")
        self.assertEqual(self.accion("finalizar").status_code, status.HTTP_200_OK)
        self.assertEqual(self.recargar().estado, EstadoViaje.FINALIZADO)
        self.assertEqual(
            list(Notificacion.objects.filter(tipo=TipoNotificacion.VIAJE_FINALIZADO).values_list("usuario", flat=True)),
            [aceptada.pasajero_id],
        )

    def test_transiciones_invalidas_son_409(self):
        self.assertEqual(self.accion("finalizar").status_code, status.HTTP_409_CONFLICT)  # PUBLICADO → FINALIZADO
        self.accion("cancelar")
        for nombre in ("cancelar", "iniciar", "finalizar"):
            with self.subTest(nombre):
                self.assertEqual(self.accion(nombre).status_code, status.HTTP_409_CONFLICT)

    def test_en_curso_no_se_cancela(self):
        mover(self.viaje, minutes=10)
        self.accion("iniciar")
        self.assertEqual(self.accion("cancelar").status_code, status.HTTP_409_CONFLICT)

    def test_cancelar_cancela_solicitudes_activas_y_notifica(self):
        pendiente = crear_solicitud(self.viaje, crear_usuario())
        aceptada = crear_solicitud(self.viaje, crear_usuario(), estado=EstadoSolicitud.ACEPTADA)
        rechazada = crear_solicitud(self.viaje, crear_usuario(), estado=EstadoSolicitud.RECHAZADA)
        self.assertEqual(self.accion("cancelar").status_code, status.HTTP_200_OK)
        for solicitud, esperado in (
            (pendiente, EstadoSolicitud.CANCELADA),
            (aceptada, EstadoSolicitud.CANCELADA),
            (rechazada, EstadoSolicitud.RECHAZADA),
        ):
            solicitud.refresh_from_db()
            self.assertEqual(solicitud.estado, esperado)
        notificados = set(
            Notificacion.objects.filter(tipo=TipoNotificacion.VIAJE_CANCELADO).values_list("usuario", flat=True)
        )
        self.assertEqual(notificados, {pendiente.pasajero_id, aceptada.pasajero_id})

    def test_solo_el_conductor_cambia_el_estado(self):
        otro = cliente_para(crear_conductor())
        for nombre in ("cancelar", "iniciar", "finalizar"):
            with self.subTest(nombre):
                self.assertEqual(self.accion(nombre, cliente=otro).status_code, status.HTTP_403_FORBIDDEN)

    def test_viaje_inexistente_es_404(self):
        import uuid

        respuesta = self.cliente.post(f"/api/viajes/{uuid.uuid4()}/cancelar/")
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)


@override_settings(VENTANA_CRUCE_MINUTOS=60)
class EditarViajeTests(TestCase):
    def setUp(self):
        self.conductor = crear_conductor(asientos=4, sexo=Sexo.M)
        self.cliente = cliente_para(self.conductor)
        self.viaje = crear_viaje(self.conductor, lugares_ofrecidos=3)

    def editar(self, cliente=None, **datos):
        return (cliente or self.cliente).patch(f"/api/viajes/{self.viaje.pk}/", datos, format="json")

    def test_editar_y_notificar_activas(self):
        pendiente = crear_solicitud(self.viaje, crear_usuario())
        respuesta = self.editar(notas="Nuevo punto exacto", lugares_ofrecidos=2)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK, respuesta.data)
        self.viaje.refresh_from_db()
        self.assertEqual((self.viaje.notas, self.viaje.lugares_ofrecidos), ("Nuevo punto exacto", 2))
        self.assertTrue(
            Notificacion.objects.filter(usuario=pendiente.pasajero, tipo=TipoNotificacion.VIAJE_MODIFICADO).exists()
        )

    def test_no_edita_punto_campus_ni_sentido(self):
        original = (self.viaje.punto_referencia_id, self.viaje.campus_id, self.viaje.sentido)
        self.editar(punto_referencia=crear_punto().id, campus=crear_campus().id, sentido="DESDE_CAMPUS")
        self.viaje.refresh_from_db()
        self.assertEqual((self.viaje.punto_referencia_id, self.viaje.campus_id, self.viaje.sentido), original)

    def test_lugares_no_menos_que_aceptados_ni_mas_que_asientos(self):
        crear_solicitud(self.viaje, crear_usuario(), estado=EstadoSolicitud.ACEPTADA)
        crear_solicitud(self.viaje, crear_usuario(), estado=EstadoSolicitud.ACEPTADA)
        self.assertEqual(self.editar(lugares_ofrecidos=1).status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.editar(lugares_ofrecidos=5).status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.editar(lugares_ofrecidos=2).status_code, status.HTTP_200_OK)

    def test_fecha_pasada_o_con_cruce(self):
        pasada = (timezone.now() - timedelta(minutes=5)).isoformat()
        self.assertEqual(self.editar(fecha_hora=pasada).status_code, status.HTTP_400_BAD_REQUEST)
        otro = crear_viaje(self.conductor, fecha_hora=timezone.now() + timedelta(days=3))
        cruce = (otro.fecha_hora + timedelta(minutes=20)).isoformat()
        self.assertEqual(self.editar(fecha_hora=cruce).status_code, status.HTTP_409_CONFLICT)
        # Mover un poco su propia hora no choca consigo mismo
        propia = (self.viaje.fecha_hora + timedelta(minutes=15)).isoformat()
        self.assertEqual(self.editar(fecha_hora=propia).status_code, status.HTTP_200_OK)

    def test_no_pasa_a_mismo_sexo_con_aceptados_de_otro_sexo(self):
        crear_solicitud(self.viaje, crear_usuario(sexo=Sexo.F), estado=EstadoSolicitud.ACEPTADA)
        respuesta = self.editar(preferencia_compatibilidad="MISMO_SEXO")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("preferencia_compatibilidad", respuesta.data)

    def test_pasa_a_mismo_sexo_si_todos_coinciden(self):
        crear_solicitud(self.viaje, crear_usuario(sexo=Sexo.M), estado=EstadoSolicitud.ACEPTADA)
        self.assertEqual(self.editar(preferencia_compatibilidad="MISMO_SEXO").status_code, status.HTTP_200_OK)

    def test_solo_el_conductor_y_solo_publicado(self):
        self.assertEqual(self.editar(cliente_para(crear_conductor()), notas="x").status_code, 403)
        Viaje.objects.filter(pk=self.viaje.pk).update(estado=EstadoViaje.EN_CURSO)
        self.assertEqual(self.editar(notas="x").status_code, status.HTTP_409_CONFLICT)


class DetalleYMisViajesTests(TestCase):
    def setUp(self):
        self.conductor = crear_conductor()
        self.viaje = crear_viaje(self.conductor)

    def test_detalle_publicado_lo_ve_cualquiera_sin_contacto(self):
        respuesta = cliente_para(crear_usuario()).get(f"/api/viajes/{self.viaje.pk}/")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertNotIn("telefono", respuesta.data["conductor"])
        self.assertNotIn("placas", respuesta.data["vehiculo"])
        self.assertIsNone(respuesta.data["pasajeros_confirmados"])
        self.assertIsNone(respuesta.data["mi_solicitud"])

    def test_detalle_no_publicado_solo_participantes(self):
        con_solicitud = crear_usuario()
        crear_solicitud(self.viaje, con_solicitud)
        Viaje.objects.filter(pk=self.viaje.pk).update(estado=EstadoViaje.CANCELADO)
        self.assertEqual(cliente_para(crear_usuario()).get(f"/api/viajes/{self.viaje.pk}/").status_code, 404)
        self.assertEqual(cliente_para(con_solicitud).get(f"/api/viajes/{self.viaje.pk}/").status_code, 200)
        self.assertEqual(cliente_para(self.conductor).get(f"/api/viajes/{self.viaje.pk}/").status_code, 200)

    def test_detalle_vencido_no_es_publico(self):
        mover(self.viaje, hours=-3)
        self.assertEqual(cliente_para(crear_usuario()).get(f"/api/viajes/{self.viaje.pk}/").status_code, 404)

    def test_mis_viajes(self):
        crear_viaje(self.conductor, fecha_hora=timezone.now() + timedelta(days=5), estado=EstadoViaje.CANCELADO)
        vencido = mover(crear_viaje(self.conductor, fecha_hora=timezone.now() + timedelta(days=9)), hours=-3)
        cliente = cliente_para(self.conductor)
        datos = cliente.get("/api/viajes/mios/").data
        self.assertEqual({v["id"] for v in datos["results"]}, {str(self.viaje.pk), str(vencido.pk)})
        self.assertTrue(next(v for v in datos["results"] if v["id"] == str(vencido.pk))["esta_vencido"])
        self.assertEqual(cliente.get("/api/viajes/mios/", {"estado": "CANCELADO"}).data["count"], 1)
        self.assertEqual(cliente.get("/api/viajes/mios/", {"estado": "OTRO"}).status_code, 400)

    def test_mis_viajes_cuenta_solicitudes_pendientes(self):
        crear_solicitud(self.viaje, crear_usuario())
        crear_solicitud(self.viaje, crear_usuario())
        crear_solicitud(self.viaje, crear_usuario(), estado=EstadoSolicitud.ACEPTADA)
        crear_solicitud(self.viaje, crear_usuario(), estado=EstadoSolicitud.RECHAZADA)
        otro = crear_viaje(self.conductor, fecha_hora=timezone.now() + timedelta(days=4))
        datos = cliente_para(self.conductor).get("/api/viajes/mios/").data["results"]
        pendientes = {v["id"]: v["solicitudes_pendientes"] for v in datos}
        self.assertEqual(pendientes, {str(self.viaje.pk): 2, str(otro.pk): 0})

    def test_mis_viajes_solo_conductores(self):
        self.assertEqual(cliente_para(crear_usuario()).get("/api/viajes/mios/").status_code, 403)
