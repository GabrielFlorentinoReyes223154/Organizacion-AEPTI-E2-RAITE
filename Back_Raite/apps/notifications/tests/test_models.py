from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.accounts.tests.factories import crear_usuario
from apps.notifications.models import Notificacion
from apps.notifications.models_choices import TipoNotificacion
from apps.rides.tests.factories import crear_viaje


class NotificacionTests(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()

    def test_valores_por_defecto(self):
        n = Notificacion.objects.create(
            usuario=self.usuario, tipo=TipoNotificacion.SOLICITUD_NUEVA, mensaje="Tienes una solicitud"
        )
        n.full_clean()
        self.assertFalse(n.leida)
        self.assertIsNone(n.viaje)

    def test_tipo_invalido(self):
        n = Notificacion(usuario=self.usuario, tipo="OTRO", mensaje="x")
        with self.assertRaises(ValidationError):
            n.full_clean()

    def test_mensaje_maximo_255(self):
        n = Notificacion(usuario=self.usuario, tipo=TipoNotificacion.VIAJE_CANCELADO, mensaje="x" * 256)
        with self.assertRaises(ValidationError):
            n.full_clean()

    def test_ordenadas_de_la_mas_nueva(self):
        vieja = Notificacion.objects.create(usuario=self.usuario, tipo=TipoNotificacion.VIAJE_MODIFICADO, mensaje="1")
        nueva = Notificacion.objects.create(usuario=self.usuario, tipo=TipoNotificacion.VIAJE_MODIFICADO, mensaje="2")
        Notificacion.objects.filter(pk=vieja.pk).update(created_at=timezone.now() - timedelta(hours=1))
        self.assertEqual(list(self.usuario.notificaciones.all()), [nueva, vieja])

    def test_sobrevive_si_se_borra_el_viaje(self):
        viaje = crear_viaje()
        n = Notificacion.objects.create(
            usuario=self.usuario, tipo=TipoNotificacion.VIAJE_CANCELADO, mensaje="Cancelado", viaje=viaje
        )
        viaje.delete()
        n.refresh_from_db()
        self.assertIsNone(n.viaje)
