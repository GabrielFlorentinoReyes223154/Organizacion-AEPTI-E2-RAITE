"""Piezas comunes del API: errores y manejador de excepciones."""

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.views import exception_handler


class Conflicto(APIException):
    """409: la acción choca con el estado actual (transición inválida, viaje lleno, cruce de horario…)."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "La acción no es posible en el estado actual."
    default_code = "conflicto"


def _como_drf(error: DjangoValidationError) -> DRFValidationError:
    if hasattr(error, "error_dict"):
        detalle = {
            ("non_field_errors" if campo == "__all__" else campo): mensajes
            for campo, mensajes in error.message_dict.items()
        }
    else:
        detalle = {"non_field_errors": error.messages}
    return DRFValidationError(detalle)


def manejar_excepcion(exc, context):
    """Igual que el de DRF, pero también convierte la ValidationError de Django
    (la que lanzan `full_clean()` y los servicios) en una respuesta 400."""
    if isinstance(exc, DjangoValidationError):
        exc = _como_drf(exc)
    return exception_handler(exc, context)
