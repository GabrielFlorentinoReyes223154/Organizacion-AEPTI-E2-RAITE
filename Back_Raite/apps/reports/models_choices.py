from django.db import models


class EstadoReporte(models.TextChoices):
    PENDIENTE = "PENDIENTE", "Pendiente"
    RESUELTO = "RESUELTO", "Resuelto"
    DESCARTADO = "DESCARTADO", "Descartado"
