import uuid
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.accounts.models import ASIENTOS_MAX, ASIENTOS_MIN
from apps.accounts.models_choices import PreferenciaCompatibilidad

from .models_choices import (
    ESTADOS_SOLICITUD_ACTIVOS,
    TRANSICIONES_SOLICITUD,
    TRANSICIONES_VIAJE,
    EstadoSolicitud,
    EstadoViaje,
    SentidoViaje,
)


def limite_vencimiento():
    """Un viaje PUBLICADO cuya hora es anterior a esto está vencido."""
    return timezone.now() - timedelta(hours=settings.VENCIMIENTO_HORAS)


class ViajeQuerySet(models.QuerySet):
    def vencidos(self):
        """PUBLICADO cuya hora pasó hace más de VENCIMIENTO_HORAS. Solo se pueden cancelar."""
        return self.filter(estado=EstadoViaje.PUBLICADO, fecha_hora__lt=limite_vencimiento())

    def vigentes(self):
        """PUBLICADO sin vencer o EN_CURSO: los que cuentan para cruces de horario."""
        return self.filter(
            Q(estado=EstadoViaje.PUBLICADO, fecha_hora__gte=limite_vencimiento())
            | Q(estado=EstadoViaje.EN_CURSO)
        )


class Viaje(models.Model):
    """Viaje publicado por un conductor entre un punto de referencia y un campus (RF-02, RF-03)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conductor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="viajes_como_conductor"
    )
    vehiculo = models.ForeignKey("accounts.Vehiculo", on_delete=models.PROTECT, related_name="viajes")
    punto_referencia = models.ForeignKey(
        "locations.PuntoReferencia",
        on_delete=models.PROTECT,
        related_name="viajes",
        limit_choices_to={"activo": True},
    )
    campus = models.ForeignKey(
        "locations.Campus", on_delete=models.PROTECT, related_name="viajes", limit_choices_to={"activo": True}
    )
    sentido = models.CharField(
        max_length=12, choices=SentidoViaje.choices, default=SentidoViaje.HACIA_CAMPUS
    )
    fecha_hora = models.DateTimeField(help_text="Hora de salida.")
    lugares_ofrecidos = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(ASIENTOS_MIN), MaxValueValidator(ASIENTOS_MAX)],
        help_text="De 1 a 5, sin superar los asientos del vehículo.",
    )
    preferencia_compatibilidad = models.CharField(
        max_length=12,
        choices=PreferenciaCompatibilidad.choices,
        blank=True,
        help_text="Si se deja vacío se copia la preferencia del conductor.",
    )
    notas = models.TextField(
        max_length=300,
        blank=True,
        validators=[MaxLengthValidator(300)],
        help_text="Detalles del punto de encuentro (opcional).",
    )
    estado = models.CharField(max_length=12, choices=EstadoViaje.choices, default=EstadoViaje.PUBLICADO)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ViajeQuerySet.as_manager()

    class Meta:
        ordering = ["fecha_hora"]
        indexes = [models.Index(fields=["estado", "campus", "fecha_hora"])]
        constraints = [
            models.CheckConstraint(
                condition=Q(lugares_ofrecidos__gte=ASIENTOS_MIN) & Q(lugares_ofrecidos__lte=ASIENTOS_MAX),
                name="viaje_lugares_1_a_5",
            ),
        ]

    def __str__(self):
        flecha = "→" if self.sentido == SentidoViaje.HACIA_CAMPUS else "←"
        hora = timezone.localtime(self.fecha_hora) if self.fecha_hora else None
        return f"{self.punto_referencia} {flecha} {self.campus.codigo} ({hora:%Y-%m-%d %H:%M})"

    def clean(self):
        super().clean()
        errores = {}
        conductor = self.conductor if self.conductor_id else None
        vehiculo = self.vehiculo if self.vehiculo_id else None

        if conductor and not conductor.es_conductor:
            errores["conductor"] = "El usuario no tiene rol de conductor."
        if vehiculo and conductor and vehiculo.usuario_id != conductor.pk:
            errores["vehiculo"] = "El vehículo no pertenece al conductor."
        elif vehiculo and not vehiculo.es_valido_para_conducir():
            errores["vehiculo"] = "El vehículo no está activo."
        if vehiculo and self.lugares_ofrecidos and self.lugares_ofrecidos > vehiculo.asientos_disponibles:
            errores["lugares_ofrecidos"] = (
                f"El vehículo solo tiene {vehiculo.asientos_disponibles} asiento(s) disponibles."
            )
        if self.pk and not self._state.adding and self.lugares_ofrecidos is not None:
            if self.lugares_ofrecidos < self.lugares_ocupados:
                errores["lugares_ofrecidos"] = "No puede ser menor que los pasajeros ya aceptados."

        if self._state.adding:
            if self.fecha_hora and self.fecha_hora <= timezone.now():
                errores["fecha_hora"] = "La hora de salida debe ser en el futuro."
            if self.punto_referencia_id and not self.punto_referencia.activo:
                errores["punto_referencia"] = "El punto de referencia no está activo."
            if self.campus_id and not self.campus.activo:
                errores["campus"] = "El campus no está activo."

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        if not self.preferencia_compatibilidad and self.conductor_id:
            self.preferencia_compatibilidad = self.conductor.preferencia_compatibilidad
        super().save(*args, **kwargs)

    # --- Lectura ---

    @property
    def solicitudes_aceptadas(self):
        return self.solicitudes.filter(estado=EstadoSolicitud.ACEPTADA)

    @property
    def lugares_ocupados(self) -> int:
        """Cada solicitud aceptada ocupa un lugar (el SRS dice "solicite un lugar")."""
        return self.solicitudes_aceptadas.count()

    @property
    def lugares_disponibles(self) -> int:
        return max(self.lugares_ofrecidos - self.lugares_ocupados, 0)

    @property
    def esta_lleno(self) -> bool:
        return self.lugares_disponibles == 0

    @property
    def pasajeros_confirmados(self):
        from django.contrib.auth import get_user_model

        return get_user_model().objects.filter(
            solicitudes__viaje=self, solicitudes__estado=EstadoSolicitud.ACEPTADA
        )

    def es_participante(self, usuario) -> bool:
        """Conductor o pasajero con solicitud aceptada."""
        if usuario is None:
            return False
        return usuario.pk == self.conductor_id or self.solicitudes_aceptadas.filter(pasajero=usuario).exists()

    def puede_cambiar_a(self, estado) -> bool:
        return estado in TRANSICIONES_VIAJE[self.estado]

    @property
    def esta_vencido(self) -> bool:
        """Calculado con la fecha; no es un estado guardado."""
        return self.estado == EstadoViaje.PUBLICADO and self.fecha_hora < limite_vencimiento()

    @property
    def inicio_permitido_desde(self):
        return self.fecha_hora - timedelta(minutes=settings.INICIO_ANTICIPACION_MINUTOS)


class Solicitud(models.Model):
    """Solicitud de un pasajero para ocupar un lugar en un viaje (RF-05, RF-06)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE, related_name="solicitudes")
    pasajero = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="solicitudes"
    )
    preferencia_compatibilidad = models.CharField(
        max_length=12,
        choices=PreferenciaCompatibilidad.choices,
        blank=True,
        help_text="Copia de la preferencia del pasajero al momento de solicitar.",
    )
    estado = models.CharField(
        max_length=10, choices=EstadoSolicitud.choices, default=EstadoSolicitud.PENDIENTE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    respondida_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "solicitudes"
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["viaje", "pasajero"],
                condition=Q(estado__in=ESTADOS_SOLICITUD_ACTIVOS),
                name="solicitud_activa_unica_por_viaje",
                violation_error_message="Ya tienes una solicitud activa en este viaje.",
            ),
        ]

    def __str__(self):
        return f"{self.pasajero} en {self.viaje} [{self.get_estado_display()}]"

    def clean(self):
        super().clean()
        errores = {}
        if self.pasajero_id:
            if not self.pasajero.es_pasajero:
                errores["pasajero"] = "El usuario no tiene rol de pasajero."
            elif self.viaje_id and self.pasajero_id == self.viaje.conductor_id:
                errores["pasajero"] = "El conductor no puede solicitar lugar en su propio viaje."
        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        if not self.preferencia_compatibilidad and self.pasajero_id:
            self.preferencia_compatibilidad = self.pasajero.preferencia_compatibilidad
        super().save(*args, **kwargs)

    @property
    def esta_activa(self) -> bool:
        return self.estado in ESTADOS_SOLICITUD_ACTIVOS

    def puede_cambiar_a(self, estado) -> bool:
        return estado in TRANSICIONES_SOLICITUD[self.estado]
