from django.db import models


class Rol(models.IntegerChoices):
    ADMIN = 1, "Admin"
    PASAJERO = 2, "Pasajero"
    CONDUCTOR = 3, "Conductor"
    AMBOS = 4, "Ambos"


class TipoVehiculo(models.TextChoices):
    CAMIONETA = "CAMIONETA", "Camioneta"
    COCHE = "COCHE", "Coche"
    TROCA = "TROCA", "Troca"


class Sexo(models.TextChoices):
    M = "M", "Masculino"
    F = "F", "Femenino"
    X = "X", "Otro"

class PreferenciaCompatibilidad(models.TextChoices):
    """Solo se puede elegir mismo sexo o mixto: nadie puede pedir exclusivamente el sexo opuesto."""

    MISMO_SEXO = "MISMO_SEXO", "Mismo sexo"
    MIXTO = "MIXTO", "Mixto"
