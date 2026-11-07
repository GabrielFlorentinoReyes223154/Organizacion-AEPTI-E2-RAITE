"""Creación de avisos dentro de la app (RF-09). Los servicios de cada app la llaman de forma explícita."""

from django.utils import timezone

from .models import Notificacion


def describir_viaje(viaje) -> str:
    hora = timezone.localtime(viaje.fecha_hora)
    return f"{viaje.punto_referencia.nombre} ↔ {viaje.campus.codigo}, {hora:%d/%m %H:%M}"


def notificar(usuarios, tipo, mensaje: str, viaje=None) -> list[Notificacion]:
    """Crea una notificación por usuario (sin repetir)."""
    vistos, avisos = set(), []
    for usuario in usuarios:
        if usuario.pk in vistos:
            continue
        vistos.add(usuario.pk)
        avisos.append(Notificacion(usuario=usuario, tipo=tipo, mensaje=mensaje[:255], viaje=viaje))
    return Notificacion.objects.bulk_create(avisos)
