"""Solicitar, aceptar, rechazar y cancelar lugares; cupo, compatibilidad y contacto (RF-05, RF-06, RNF-02)."""

import threading
from datetime import timedelta

from django.db import connection
from django.test import TestCase, TransactionTestCase, override_settings
from django.utils import timezone
from rest_framework import status

from apps.accounts.models_choices import PreferenciaCompatibilidad as Pref
from apps.accounts.models_choices import Rol, Sexo
from apps.accounts.tests.factories import cliente_para, crear_conductor, crear_usuario
from apps.notifications.models import Notificacion
from apps.notifications.models_choices import TipoNotificacion
from apps.rides.models import Solicitud, Viaje
from apps.rides.models_choices import EstadoSolicitud, EstadoViaje
from apps.rides.tests.factories import crear_solicitud, crear_viaje


def notificado(usuario, tipo) -> bool:
    return Notificacion.objects.filter(usuario=usuario, tipo=tipo).exists()


@override_settings(VENTANA_CRUCE_MINUTOS=60, VENCIMIENTO_HORAS=2)
class SolicitarTests(TestCase):
    def setUp(self):
        self.conductor = crear_conductor(sexo=Sexo.M)
        self.viaje = crear_viaje(self.conductor, lugares_ofrecidos=2)
        self.pasajero = crear_usuario(sexo=Sexo.M)

    def solicitar(self, usuario=None, viaje=None):
        viaje = viaje or self.viaje
        return cliente_para(usuario or self.pasajero).post(f"/api/viajes/{viaje.pk}/solicitudes/")

    def test_solicitar_crea_pendiente_y_notifica_al_conductor(self):
        respuesta = self.solicitar()
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED, respuesta.data)
        self.assertEqual(respuesta.data["estado"], EstadoSolicitud.PENDIENTE)
        solicitud = Solicitud.objects.get()
        self.assertEqual(solicitud.preferencia_compatibilidad, self.pasajero.preferencia_compatibilidad)
        self.assertTrue(notificado(self.conductor, TipoNotificacion.SOLICITUD_NUEVA))

    def test_quien_no_puede_solicitar(self):
        casos = {
            "conductor puro": crear_conductor(),
            "suspendido": crear_usuario(suspendido=True),
            "sin verificar": crear_usuario(correo_verificado=False),
        }
        for nombre, usuario in casos.items():
            with self.subTest(nombre):
                self.assertEqual(self.solicitar(usuario).status_code, status.HTTP_403_FORBIDDEN)

    def test_no_en_su_propio_viaje(self):
        ambos = crear_conductor(rol=Rol.AMBOS)
        viaje = crear_viaje(ambos)
        self.assertEqual(self.solicitar(ambos, viaje).status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_dos_activas_en_el_mismo_viaje_pero_si_tras_cancelar(self):
        self.solicitar()
        self.assertEqual(self.solicitar().status_code, status.HTTP_409_CONFLICT)
        Solicitud.objects.update(estado=EstadoSolicitud.CANCELADA)
        self.assertEqual(self.solicitar().status_code, status.HTTP_201_CREATED)

    def test_viaje_lleno(self):
        crear_solicitud(self.viaje, crear_usuario(), estado=EstadoSolicitud.ACEPTADA)
        crear_solicitud(self.viaje, crear_usuario(), estado=EstadoSolicitud.ACEPTADA)
        self.assertEqual(self.solicitar().status_code, status.HTTP_409_CONFLICT)

    def test_viaje_no_publicado_pasado_o_vencido(self):
        for cambio in (
            {"estado": EstadoViaje.CANCELADO},
            {"estado": EstadoViaje.EN_CURSO},
            {"fecha_hora": timezone.now() - timedelta(minutes=30)},
            {"fecha_hora": timezone.now() - timedelta(hours=3)},
        ):
            with self.subTest(cambio=cambio):
                viaje = crear_viaje(fecha_hora=timezone.now() + timedelta(days=5))
                Viaje.objects.filter(pk=viaje.pk).update(**cambio)
                self.assertEqual(self.solicitar(viaje=viaje).status_code, status.HTTP_409_CONFLICT)

    def test_incompatible_es_400(self):
        mujer = crear_usuario(sexo=Sexo.F, preferencia_compatibilidad=Pref.MISMO_SEXO)
        self.assertEqual(self.solicitar(mujer).status_code, status.HTTP_400_BAD_REQUEST)
        mujer_mixta = crear_usuario(sexo=Sexo.F)
        self.assertEqual(self.solicitar(mujer_mixta).status_code, status.HTTP_201_CREATED)

    def test_cruce_con_otra_solicitud(self):
        self.solicitar()
        cercano = crear_viaje(fecha_hora=self.viaje.fecha_hora + timedelta(minutes=30))
        self.assertEqual(self.solicitar(viaje=cercano).status_code, status.HTTP_409_CONFLICT)
        lejano = crear_viaje(fecha_hora=self.viaje.fecha_hora + timedelta(hours=3))
        self.assertEqual(self.solicitar(viaje=lejano).status_code, status.HTTP_201_CREATED)

    def test_solicitud_en_viaje_vencido_no_cuenta_para_cruce(self):
        viejo = crear_viaje(fecha_hora=timezone.now() + timedelta(days=9))
        crear_solicitud(viejo, self.pasajero)
        Viaje.objects.filter(pk=viejo.pk).update(fecha_hora=timezone.now() - timedelta(hours=3))
        nuevo = crear_viaje(fecha_hora=timezone.now() + timedelta(minutes=20))
        self.assertEqual(self.solicitar(viaje=nuevo).status_code, status.HTTP_201_CREATED)


@override_settings(VENCIMIENTO_HORAS=2)
class ResponderSolicitudTests(TestCase):
    def setUp(self):
        self.conductor = crear_conductor(sexo=Sexo.F)
        self.viaje = crear_viaje(self.conductor, lugares_ofrecidos=1)
        self.pasajero = crear_usuario(sexo=Sexo.F)
        self.solicitud = crear_solicitud(self.viaje, self.pasajero)
        self.cliente = cliente_para(self.conductor)

    def accion(self, nombre, cliente=None, solicitud=None):
        solicitud = solicitud or self.solicitud
        return (cliente or self.cliente).post(f"/api/solicitudes/{solicitud.pk}/{nombre}/")

    def estado(self, solicitud=None):
        solicitud = solicitud or self.solicitud
        solicitud.refresh_from_db()
        return solicitud.estado

    def test_aceptar_y_notificar(self):
        respuesta = self.accion("aceptar")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(self.estado(), EstadoSolicitud.ACEPTADA)
        self.assertIsNotNone(Solicitud.objects.get().respondida_en)
        self.assertTrue(notificado(self.pasajero, TipoNotificacion.SOLICITUD_ACEPTADA))
        self.assertEqual(respuesta.data["pasajero"]["telefono"], self.pasajero.telefono)

    def test_aceptar_sin_cupo_es_409(self):
        otra = crear_solicitud(self.viaje, crear_usuario(sexo=Sexo.F))
        self.accion("aceptar")
        self.assertEqual(self.accion("aceptar", solicitud=otra).status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(self.estado(otra), EstadoSolicitud.PENDIENTE)

    def test_aceptar_revisa_compatibilidad_contra_aceptados(self):
        Viaje.objects.filter(pk=self.viaje.pk).update(lugares_ofrecidos=2)
        hombre = crear_usuario(sexo=Sexo.M)
        del_hombre = crear_solicitud(self.viaje, hombre)  # compatible cuando pidió (todos mixtos)
        Solicitud.objects.filter(pk=self.solicitud.pk).update(preferencia_compatibilidad=Pref.MISMO_SEXO)
        self.accion("aceptar")  # entra la pasajera con "mismo sexo"
        self.assertEqual(self.accion("aceptar", solicitud=del_hombre).status_code, status.HTTP_409_CONFLICT)

    def test_rechazar_y_notificar(self):
        self.assertEqual(self.accion("rechazar").status_code, status.HTTP_200_OK)
        self.assertEqual(self.estado(), EstadoSolicitud.RECHAZADA)
        self.assertTrue(notificado(self.pasajero, TipoNotificacion.SOLICITUD_RECHAZADA))

    def test_transiciones_invalidas(self):
        self.accion("rechazar")
        self.assertEqual(self.accion("aceptar").status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(self.accion("rechazar").status_code, status.HTTP_409_CONFLICT)
        aceptada = crear_solicitud(self.viaje, crear_usuario(sexo=Sexo.F), estado=EstadoSolicitud.ACEPTADA)
        self.assertEqual(self.accion("rechazar", solicitud=aceptada).status_code, status.HTTP_409_CONFLICT)

    def test_solo_el_conductor_responde(self):
        for cliente in (cliente_para(crear_conductor()), cliente_para(self.pasajero)):
            self.assertEqual(self.accion("aceptar", cliente).status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(self.accion("rechazar", cliente).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.estado(), EstadoSolicitud.PENDIENTE)

    def test_no_se_responde_en_viaje_cerrado_o_vencido(self):
        Viaje.objects.filter(pk=self.viaje.pk).update(fecha_hora=timezone.now() - timedelta(hours=3))
        self.assertEqual(self.accion("aceptar").status_code, status.HTTP_409_CONFLICT)
        Viaje.objects.filter(pk=self.viaje.pk).update(estado=EstadoViaje.CANCELADO)
        self.assertEqual(self.accion("rechazar").status_code, status.HTTP_409_CONFLICT)

    def test_pasajero_cancela_pendiente_o_aceptada(self):
        pasajero = cliente_para(self.pasajero)
        self.accion("aceptar")
        respuesta = self.accion("cancelar", pasajero)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(self.estado(), EstadoSolicitud.CANCELADA)
        self.assertTrue(notificado(self.conductor, TipoNotificacion.SOLICITUD_CANCELADA))
        self.assertEqual(self.accion("cancelar", pasajero).status_code, status.HTTP_409_CONFLICT)
        # El lugar se libera
        self.viaje.refresh_from_db()
        self.assertEqual(self.viaje.lugares_disponibles, 1)

    def test_solo_el_pasajero_cancela_y_no_con_viaje_en_curso(self):
        self.assertEqual(self.accion("cancelar").status_code, status.HTTP_403_FORBIDDEN)  # el conductor
        Viaje.objects.filter(pk=self.viaje.pk).update(estado=EstadoViaje.EN_CURSO)
        self.assertEqual(self.accion("cancelar", cliente_para(self.pasajero)).status_code, status.HTTP_409_CONFLICT)

    def test_solicitud_inexistente_es_404(self):
        import uuid

        self.assertEqual(self.cliente.post(f"/api/solicitudes/{uuid.uuid4()}/aceptar/").status_code, 404)


class ListadosDeSolicitudesTests(TestCase):
    def setUp(self):
        self.conductor = crear_conductor()
        self.viaje = crear_viaje(self.conductor)
        self.pendiente = crear_solicitud(self.viaje, crear_usuario())
        self.aceptada = crear_solicitud(self.viaje, crear_usuario(), estado=EstadoSolicitud.ACEPTADA)

    def test_conductor_ve_las_solicitudes_y_telefono_solo_de_aceptadas(self):
        datos = cliente_para(self.conductor).get(f"/api/viajes/{self.viaje.pk}/solicitudes/").data["results"]
        por_id = {d["id"]: d for d in datos}
        self.assertNotIn("telefono", por_id[str(self.pendiente.pk)]["pasajero"])
        self.assertEqual(por_id[str(self.aceptada.pk)]["pasajero"]["telefono"], self.aceptada.pasajero.telefono)

    def test_otros_no_ven_las_solicitudes(self):
        respuesta = cliente_para(self.pendiente.pasajero).get(f"/api/viajes/{self.viaje.pk}/solicitudes/")
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_mis_solicitudes(self):
        cliente = cliente_para(self.pendiente.pasajero)
        datos = cliente.get("/api/solicitudes/mias/").data
        self.assertEqual(datos["count"], 1)
        self.assertEqual(datos["results"][0]["viaje"]["id"], str(self.viaje.pk))
        self.assertEqual(cliente.get("/api/solicitudes/mias/", {"estado": "ACEPTADA"}).data["count"], 0)
        self.assertEqual(cliente.get("/api/solicitudes/mias/", {"estado": "X"}).status_code, 400)
        self.assertEqual(cliente_para(self.conductor).get("/api/solicitudes/mias/").status_code, 403)


class VisibilidadDeContactoTests(TestCase):
    """Regla 4 / RNF-02: teléfono y placas solo entre conductor y pasajero confirmado."""

    def setUp(self):
        self.conductor = crear_conductor()
        self.viaje = crear_viaje(self.conductor)
        self.pasajero = crear_usuario()
        self.solicitud = crear_solicitud(self.viaje, self.pasajero)

    def detalle(self, usuario=None):
        return cliente_para(usuario or self.pasajero).get(f"/api/viajes/{self.viaje.pk}/").data

    def mis_solicitudes(self):
        return cliente_para(self.pasajero).get("/api/solicitudes/mias/").data["results"][0]["viaje"]

    def test_pendiente_no_ve_contacto(self):
        for datos in (self.detalle(), self.mis_solicitudes()):
            self.assertNotIn("telefono", datos["conductor"])
            self.assertNotIn("placas", datos["vehiculo"])

    def test_aceptada_ve_contacto(self):
        cliente_para(self.conductor).post(f"/api/solicitudes/{self.solicitud.pk}/aceptar/")
        for datos in (self.detalle(), self.mis_solicitudes()):
            self.assertEqual(datos["conductor"]["telefono"], self.conductor.telefono)
            self.assertEqual(datos["vehiculo"]["placas"], self.conductor.vehiculo.placas)
        self.assertEqual(self.detalle()["mi_solicitud"]["estado"], EstadoSolicitud.ACEPTADA)

    def test_al_cancelar_deja_de_verse(self):
        cliente_para(self.conductor).post(f"/api/solicitudes/{self.solicitud.pk}/aceptar/")
        cliente_para(self.pasajero).post(f"/api/solicitudes/{self.solicitud.pk}/cancelar/")
        datos = self.detalle()
        self.assertNotIn("telefono", datos["conductor"])
        self.assertNotIn("placas", datos["vehiculo"])

    def test_otros_pasajeros_no_ven_contactos(self):
        cliente_para(self.conductor).post(f"/api/solicitudes/{self.solicitud.pk}/aceptar/")
        otro = crear_usuario()
        datos = self.detalle(otro)
        self.assertNotIn("telefono", datos["conductor"])
        self.assertIsNone(datos["pasajeros_confirmados"])

    def test_conductor_ve_telefono_de_sus_confirmados(self):
        cliente_para(self.conductor).post(f"/api/solicitudes/{self.solicitud.pk}/aceptar/")
        confirmados = self.detalle(self.conductor)["pasajeros_confirmados"]
        self.assertEqual([p["telefono"] for p in confirmados], [self.pasajero.telefono])


class AceptacionesSimultaneasTests(TransactionTestCase):
    """Dos aceptaciones al mismo tiempo en un viaje de 1 lugar: solo una entra (PostgreSQL)."""

    def test_no_rebasan_el_cupo(self):
        conductor = crear_conductor()
        viaje = crear_viaje(conductor, lugares_ofrecidos=1)
        solicitudes = [crear_solicitud(viaje, crear_usuario()) for _ in range(2)]
        barrera = threading.Barrier(2)
        codigos = []

        def aceptar(solicitud):
            try:
                cliente = cliente_para(conductor)
                barrera.wait()
                codigos.append(cliente.post(f"/api/solicitudes/{solicitud.pk}/aceptar/").status_code)
            finally:
                connection.close()

        hilos = [threading.Thread(target=aceptar, args=(s,)) for s in solicitudes]
        for hilo in hilos:
            hilo.start()
        for hilo in hilos:
            hilo.join()

        self.assertEqual(sorted(codigos), [status.HTTP_200_OK, status.HTTP_409_CONFLICT])
        self.assertEqual(viaje.solicitudes.filter(estado=EstadoSolicitud.ACEPTADA).count(), 1)
