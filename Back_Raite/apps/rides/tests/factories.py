from datetime import timedelta
from decimal import Decimal
from itertools import count

from django.utils import timezone

from apps.accounts.tests.factories import crear_conductor
from apps.locations.models import Campus, PuntoReferencia
from apps.rides.models import Solicitud, Viaje

_secuencia = count(1)


def crear_campus(**datos):
    n = next(_secuencia)
    valores = {"codigo": f"C{n}", "nombre": f"Campus {n}", "latitud": Decimal("31.742765"), "longitud": Decimal("-106.431511")}
    valores.update(datos)
    return Campus.objects.create(**valores)


def crear_punto(**datos):
    n = next(_secuencia)
    valores = {"nombre": f"Oxxo – Calle {n}", "latitud": Decimal("31.70"), "longitud": Decimal("-106.40")}
    valores.update(datos)
    return PuntoReferencia.objects.create(**valores)


def crear_viaje(conductor=None, **datos):
    """Crea un viaje válido (validado con full_clean) a una hora futura."""
    conductor = conductor or crear_conductor()
    valores = {
        "conductor": conductor,
        "vehiculo": conductor.vehiculo,
        "punto_referencia": datos.pop("punto_referencia", None) or crear_punto(),
        "campus": datos.pop("campus", None) or crear_campus(),
        "fecha_hora": timezone.now() + timedelta(days=1),
        "lugares_ofrecidos": 3,
    }
    valores.update(datos)
    viaje = Viaje(**valores)
    viaje.full_clean()
    viaje.save()
    return viaje


def crear_solicitud(viaje, pasajero, **datos):
    return Solicitud.objects.create(viaje=viaje, pasajero=pasajero, **datos)
