"""Regla de compatibilidad por sexo (regla de negocio 3, RF-07).

Si el conductor (preferencia del viaje) o cualquier pasajero aceptado o el candidato eligió
"mismo sexo", todos los integrantes deben tener el mismo valor en `sexo`. Una solicitud
pendiente no restringe a nadie hasta que se acepta.
"""

from apps.accounts.models_choices import PreferenciaCompatibilidad

MISMO_SEXO = PreferenciaCompatibilidad.MISMO_SEXO


def grupo_compatible(integrantes) -> bool:
    """`integrantes`: pares (sexo, preferencia)."""
    integrantes = list(integrantes)
    if not any(pref == MISMO_SEXO for _, pref in integrantes):
        return True
    return len({sexo for sexo, _ in integrantes}) <= 1


def integrantes_del_viaje(viaje, aceptadas=None):
    """Conductor (con la preferencia del viaje) y pasajeros aceptados."""
    if aceptadas is None:
        aceptadas = viaje.solicitudes_aceptadas.select_related("pasajero")
    yield viaje.conductor.sexo, viaje.preferencia_compatibilidad
    for solicitud in aceptadas:
        yield solicitud.pasajero.sexo, solicitud.preferencia_compatibilidad


def es_compatible(viaje, pasajero, preferencia=None, aceptadas=None) -> bool:
    """¿Puede `pasajero` sumarse a `viaje` sin romper la regla?"""
    candidato = (pasajero.sexo, preferencia or pasajero.preferencia_compatibilidad)
    return grupo_compatible([*integrantes_del_viaje(viaje, aceptadas), candidato])
