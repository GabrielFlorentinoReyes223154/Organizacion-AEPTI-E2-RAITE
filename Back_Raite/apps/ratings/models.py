import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from apps.rides.models_choices import EstadoViaje


class Calificacion(models.Model):
    """Calificación entre conductor y pasajero al terminar un viaje (RF-10)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    viaje = models.ForeignKey("rides.Viaje", on_delete=models.CASCADE, related_name="calificaciones")
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="calificaciones_hechas"
    )
    calificado = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="calificaciones_recibidas"
    )
    puntuacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], help_text="De 1 a 5 estrellas."
    )
    comentario = models.TextField(max_length=500, blank=True, validators=[MaxLengthValidator(500)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "calificación"
        verbose_name_plural = "calificaciones"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["viaje", "autor", "calificado"],
                name="calificacion_unica_por_viaje",
                violation_error_message="Ya calificaste a este usuario en este viaje.",
            ),
            models.CheckConstraint(
                condition=Q(puntuacion__gte=1) & Q(puntuacion__lte=5), name="calificacion_1_a_5"
            ),
            models.CheckConstraint(
                condition=~Q(autor=models.F("calificado")), name="calificacion_no_a_si_mismo"
            ),
        ]

    def __str__(self):
        return f"{self.autor} → {self.calificado}: {self.puntuacion}★"

    def clean(self):
        super().clean()
        if not (self.viaje_id and self.autor_id and self.calificado_id):
            return
        if self.autor_id == self.calificado_id:
            raise ValidationError({"calificado": "No puedes calificarte a ti mismo."})
        if self.viaje.estado != EstadoViaje.FINALIZADO:
            raise ValidationError({"viaje": "Solo se califica un viaje finalizado."})

        conductor_id = self.viaje.conductor_id
        if conductor_id not in (self.autor_id, self.calificado_id):
            raise ValidationError("La calificación es entre el conductor y un pasajero del viaje.")
        pasajero = self.calificado if self.autor_id == conductor_id else self.autor
        if not self.viaje.solicitudes_aceptadas.filter(pasajero=pasajero).exists():
            raise ValidationError("El pasajero no tuvo un lugar confirmado en este viaje.")
