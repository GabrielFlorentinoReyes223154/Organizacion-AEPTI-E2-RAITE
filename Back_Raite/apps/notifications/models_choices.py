from django.db import models


class TipoNotificacion(models.TextChoices):
    SOLICITUD_NUEVA = "SOLICITUD_NUEVA", "Nueva solicitud"
    SOLICITUD_ACEPTADA = "SOLICITUD_ACEPTADA", "Solicitud aceptada"
    SOLICITUD_RECHAZADA = "SOLICITUD_RECHAZADA", "Solicitud rechazada"
    SOLICITUD_CANCELADA = "SOLICITUD_CANCELADA", "Solicitud cancelada"
    VIAJE_MODIFICADO = "VIAJE_MODIFICADO", "Viaje modificado"
    VIAJE_CANCELADO = "VIAJE_CANCELADO", "Viaje cancelado"
    VIAJE_FINALIZADO = "VIAJE_FINALIZADO", "Viaje finalizado (califica)"
