"""Funciones para crear datos de prueba. Las usan los tests de todas las apps."""

from itertools import count

from django.contrib.auth import get_user_model

from apps.accounts.models import Vehiculo
from apps.accounts.models_choices import Rol, Sexo, TipoVehiculo

_secuencia = count(1)


def crear_usuario(**datos):
    """Crea un usuario válido y verificado. Cualquier campo se puede sobrescribir."""
    n = next(_secuencia)
    valores = {
        "correo": f"alumno{n}@alumnos.uacj.mx",
        "password": "password123",
        "nombre": f"Alumno{n}",
        "apellidos": "Prueba",
        "edad": 20,
        "sexo": Sexo.M,
        "carrera": "Ingeniería en Sistemas",
        "telefono": f"656{n:07d}",
        "rol": Rol.PASAJERO,
        "correo_verificado": True,
    }
    valores.update(datos)
    return get_user_model().objects.create_user(**valores)


def crear_conductor(con_vehiculo=True, asientos=4, **datos):
    datos.setdefault("rol", Rol.CONDUCTOR)
    usuario = crear_usuario(**datos)
    if con_vehiculo:
        crear_vehiculo(usuario, asientos_disponibles=asientos)
    return usuario


def crear_vehiculo(usuario, **datos):
    n = next(_secuencia)
    valores = {
        "marca": "Nissan",
        "modelo": "Versa",
        "color": "Gris",
        "placas": f"ABC{n:04d}",
        "tipo": TipoVehiculo.COCHE,
        "asientos_disponibles": 4,
    }
    valores.update(datos)
    return Vehiculo.objects.create(usuario=usuario, **valores)
