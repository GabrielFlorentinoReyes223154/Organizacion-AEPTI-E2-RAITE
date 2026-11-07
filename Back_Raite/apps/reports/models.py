import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.db import models
from django.db.models import Q

from .models_choices import EstadoReporte


class Reporte(models.Model):
    """Reporte de comportamiento inadecuado de otro integrante del viaje (RF-12).

    Lo revisa un admin desde el admin de Django, que puede suspender al usuario reportado.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    viaje = models.ForeignKey("rides.Viaje", on_delete=models.PROTECT, related_name="reportes")
    reportante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reportes_hechos"
    )
    reportado = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reportes_recibidos"
    )
    motivo = models.TextField(max_length=1000, validators=[MaxLengthValidator(1000)])
    estado = models.CharField(max_length=10, choices=EstadoReporte.choices, default=EstadoReporte.PENDIENTE)
    notas_admin = models.TextField(blank=True)
    resuelto_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reportes_resueltos",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resuelto_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["estado", "created_at"])]
        constraints = [
            models.CheckConstraint(
                condition=~Q(reportante=models.F("reportado")), name="reporte_no_a_si_mismo"
            ),
        ]

    def __str__(self):
        return f"{self.reportante} reporta a {self.reportado} [{self.get_estado_display()}]"

    def clean(self):
        super().clean()
        if not (self.viaje_id and self.reportante_id and self.reportado_id):
            return
        if self.reportante_id == self.reportado_id:
            raise ValidationError({"reportado": "No puedes reportarte a ti mismo."})
        if not self.viaje.es_participante(self.reportante):
            raise ValidationError({"reportante": "Solo puede reportar quien participó en el viaje."})
        if not self.viaje.es_participante(self.reportado):
            raise ValidationError({"reportado": "El usuario reportado no participó en el viaje."})
