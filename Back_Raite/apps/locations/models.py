from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

# Rectángulo aproximado del municipio de Juárez, Chihuahua.
# La cobertura fuera de Ciudad Juárez está fuera de alcance (carta del proyecto).
LATITUD_MIN, LATITUD_MAX = Decimal("31.25"), Decimal("31.80")
LONGITUD_MIN, LONGITUD_MAX = Decimal("-106.95"), Decimal("-106.15")


def esta_en_juarez(latitud, longitud) -> bool:
    lat, lon = Decimal(str(latitud)), Decimal(str(longitud))
    return LATITUD_MIN <= lat <= LATITUD_MAX and LONGITUD_MIN <= lon <= LONGITUD_MAX


def validar_latitud(valor):
    if not LATITUD_MIN <= Decimal(str(valor)) <= LATITUD_MAX:
        raise ValidationError("La latitud está fuera de Ciudad Juárez.")


def validar_longitud(valor):
    if not LONGITUD_MIN <= Decimal(str(valor)) <= LONGITUD_MAX:
        raise ValidationError("La longitud está fuera de Ciudad Juárez.")


class UbicacionBase(models.Model):
    latitud = models.DecimalField(max_digits=9, decimal_places=6, validators=[validar_latitud])
    longitud = models.DecimalField(max_digits=9, decimal_places=6, validators=[validar_longitud])
    activo = models.BooleanField(default=True, help_text="Si está inactivo no aparece en la app.")

    class Meta:
        abstract = True


class Campus(UbicacionBase):
    """Campus o instituto de la UACJ que sirve como destino (u origen) de un viaje."""

    codigo = models.CharField(max_length=10, unique=True, help_text="Ej. CU, IIT, ICB, ICSA, IADA")
    nombre = models.CharField(max_length=120)

    class Meta:
        verbose_name = "campus"
        verbose_name_plural = "campus"
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} – {self.nombre}"


class PuntoReferencia(UbicacionBase):
    """Lugar conocido (ej. un Oxxo) desde el que sale un viaje.

    El punto exacto de recogida lo acuerdan conductor y pasajero después de confirmar el raite.
    """

    nombre = models.CharField(max_length=150)
    osm_id = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        help_text="Identificador de OpenStreetMap (ej. node/880963315). Vacío si se dio de alta a mano.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "punto de referencia"
        verbose_name_plural = "puntos de referencia"
        ordering = ["nombre"]
        indexes = [models.Index(fields=["activo", "nombre"])]

    def __str__(self):
        return self.nombre


class Carrera(models.Model):
    """Licenciatura o ingeniería que se ofrece en un campus (catálogo oficial de la UACJ).

    Una misma carrera puede darse en varios campus; cada combinación es un registro.
    El campus del alumno se obtiene de su carrera.
    """

    campus = models.ForeignKey(Campus, on_delete=models.PROTECT, related_name="carreras")
    nombre = models.CharField(max_length=120)
    area = models.CharField(max_length=80, blank=True, help_text="Área del conocimiento (ej. Ingenierías).")
    activo = models.BooleanField(default=True, help_text="Si está inactiva no se puede elegir en la app.")

    class Meta:
        verbose_name = "carrera"
        verbose_name_plural = "carreras"
        ordering = ["campus__codigo", "nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["campus", "nombre"],
                name="carrera_unica_por_campus",
                violation_error_message="Esa carrera ya existe en este campus.",
            ),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.campus.codigo})"
