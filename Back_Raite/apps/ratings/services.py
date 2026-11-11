"""Calificaciones entre conductor y pasajero (RF-10)."""

from decimal import ROUND_HALF_UP, Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from apps.rides.models import Viaje
from apps.rides.models_choices import EstadoSolicitud, EstadoViaje

from .models import Calificacion


def recalcular_promedio(usuario_id) -> Decimal:
    """Guarda en `Usuario.calificacion` el promedio de todo lo que ha recibido (2 decimales)."""
    Usuario = get_user_model()
    # Bloquea al usuario para que dos calificaciones simultáneas no se pisen el promedio.
    Usuario.objects.select_for_update().filter(pk=usuario_id).first()
    promedio = Calificacion.objects.filter(calificado_id=usuario_id).aggregate(p=Avg("puntuacion"))["p"]
    valor = Decimal(str(promedio or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    Usuario.objects.filter(pk=usuario_id).update(calificacion=valor)
    return valor


@transaction.atomic
def calificar(viaje_id, autor, datos: dict) -> Calificacion:
    viaje = get_object_or_404(Viaje, pk=viaje_id)
    if not viaje.es_participante(autor):
        raise PermissionDenied("Solo quien participó en el viaje puede calificar.")
    calificacion = Calificacion(viaje=viaje, autor=autor, **datos)
    calificacion.full_clean()  # viaje finalizado, conductor ↔ pasajero aceptado, una sola vez
    calificacion.save()
    recalcular_promedio(calificacion.calificado_id)
    return calificacion


def pendientes(usuario) -> list[tuple[Viaje, object]]:
    """(viaje, usuario) que `usuario` aún no califica en viajes finalizados."""
    hechas = set(Calificacion.objects.filter(autor=usuario).values_list("viaje_id", "calificado_id"))
    resultado = []

    conducidos = (
        Viaje.objects.filter(conductor=usuario, estado=EstadoViaje.FINALIZADO)
        .select_related("punto_referencia", "campus")
        .prefetch_related("solicitudes__pasajero")
        .order_by("-fecha_hora")
    )
    for viaje in conducidos:
        for solicitud in viaje.solicitudes.all():
            if solicitud.estado == EstadoSolicitud.ACEPTADA and (viaje.pk, solicitud.pasajero_id) not in hechas:
                resultado.append((viaje, solicitud.pasajero))

    como_pasajero = (
        Viaje.objects.filter(
            estado=EstadoViaje.FINALIZADO,
            solicitudes__pasajero=usuario,
            solicitudes__estado=EstadoSolicitud.ACEPTADA,
        )
        .select_related("conductor__carrera__campus", "punto_referencia", "campus")
        .order_by("-fecha_hora")
    )
    for viaje in como_pasajero:
        if (viaje.pk, viaje.conductor_id) not in hechas:
            resultado.append((viaje, viaje.conductor))

    resultado.sort(key=lambda par: par[0].fecha_hora, reverse=True)
    return resultado
