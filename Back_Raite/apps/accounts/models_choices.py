from django.db import models


class Rol(models.TextChoices):
    PASAJERO = "PASAJERO", "Pasajero"
    CONDUCTOR = "CONDUCTOR", "Conductor"
    ADMIN = "ADMIN", "Admin"


class TipoVehiculo(models.TextChoices):
    CAMIONETA = "CAMIONETA", "Camioneta"
    COCHE = "COCHE", "Coche"
    TROCA = "TROCA", "Troca"


class Sexo(models.TextChoices):
    M = "M", "Masculino"
    F = "F", "Femenino"
    X = "X", "Otro"