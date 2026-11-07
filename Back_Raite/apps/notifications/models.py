import uuid

from django.conf import settings
from django.db import models

from .models_choices import TipoNotificacion


class Notificacion(models.Model):
    """Aviso dentro de la app (RF-09). El frontend las consulta periódicamente; no hay push."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificaciones",
        help_text="Destinatario.",
    )
    tipo = models.CharField(max_length=20, choices=TipoNotificacion.choices)
    mensaje = models.CharField(max_length=255)
    viaje = models.ForeignKey(
        "rides.Viaje", on_delete=models.SET_NULL, null=True, blank=True, related_name="notificaciones"
    )
    leida = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "notificación"
        verbose_name_plural = "notificaciones"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["usuario", "leida"])]

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.usuario}: {self.mensaje}"
