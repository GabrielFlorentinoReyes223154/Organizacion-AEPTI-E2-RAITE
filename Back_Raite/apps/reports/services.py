"""Reportes de comportamiento inadecuado (RF-12). Los resuelve un admin desde el admin de Django."""

from django.core.exceptions import PermissionDenied
from django.db import transaction

from Raite_DjangoRest.api import Conflicto

from .models import Reporte
from .models_choices import EstadoReporte


@transaction.atomic
def reportar(reportante, viaje, reportado, motivo: str) -> Reporte:
    if not viaje.es_participante(reportante):
        raise PermissionDenied("Solo quien participó en el viaje puede reportar.")
    pendiente = Reporte.objects.filter(
        viaje=viaje, reportante=reportante, reportado=reportado, estado=EstadoReporte.PENDIENTE
    )
    if pendiente.exists():
        raise Conflicto("Ya tienes un reporte pendiente contra esta persona en este viaje.")
    reporte = Reporte(viaje=viaje, reportante=reportante, reportado=reportado, motivo=motivo)
    reporte.full_clean()  # reportante ≠ reportado, ambos participantes, motivo ≤ 1000
    reporte.save()
    return reporte
