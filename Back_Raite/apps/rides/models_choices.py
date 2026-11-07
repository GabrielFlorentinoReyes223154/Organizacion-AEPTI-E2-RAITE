from django.db import models


class SentidoViaje(models.TextChoices):
    HACIA_CAMPUS = "HACIA_CAMPUS", "Hacia el campus"
    DESDE_CAMPUS = "DESDE_CAMPUS", "Desde el campus"


class EstadoViaje(models.TextChoices):
    PUBLICADO = "PUBLICADO", "Publicado"
    EN_CURSO = "EN_CURSO", "En curso"
    FINALIZADO = "FINALIZADO", "Finalizado"
    CANCELADO = "CANCELADO", "Cancelado"


class EstadoSolicitud(models.TextChoices):
    PENDIENTE = "PENDIENTE", "Pendiente"
    ACEPTADA = "ACEPTADA", "Aceptada"
    RECHAZADA = "RECHAZADA", "Rechazada"
    CANCELADA = "CANCELADA", "Cancelada"


# Transiciones permitidas. Quién puede ejecutarlas se valida en los servicios (Capa 2).
TRANSICIONES_VIAJE = {
    EstadoViaje.PUBLICADO: {EstadoViaje.EN_CURSO, EstadoViaje.CANCELADO},
    EstadoViaje.EN_CURSO: {EstadoViaje.FINALIZADO},
    EstadoViaje.FINALIZADO: set(),
    EstadoViaje.CANCELADO: set(),
}

TRANSICIONES_SOLICITUD = {
    EstadoSolicitud.PENDIENTE: {EstadoSolicitud.ACEPTADA, EstadoSolicitud.RECHAZADA, EstadoSolicitud.CANCELADA},
    EstadoSolicitud.ACEPTADA: {EstadoSolicitud.CANCELADA},
    EstadoSolicitud.RECHAZADA: set(),
    EstadoSolicitud.CANCELADA: set(),
}

ESTADOS_SOLICITUD_ACTIVOS = (EstadoSolicitud.PENDIENTE, EstadoSolicitud.ACEPTADA)
