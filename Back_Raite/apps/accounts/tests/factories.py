"""Funciones para crear datos de prueba. Las usan los tests de todas las apps."""

from decimal import Decimal
from itertools import count

from django.contrib.auth import get_user_model

from apps.accounts.models import Vehiculo
from apps.accounts.models_choices import Rol, Sexo, TipoVehiculo
from apps.locations.models import Campus, Carrera

_secuencia = count(1)


def crear_carrera(campus=None, **datos):
    """Crea una carrera del catálogo. Sin `campus`, usa uno nuevo y activo."""
    n = next(_secuencia)
    if campus is None:
        campus = Campus.objects.create(
            codigo=f"K{n}", nombre=f"Campus {n}", latitud=Decimal("31.742765"), longitud=Decimal("-106.431511")
        )
    valores = {"nombre": f"Licenciatura {n}", "area": "Ingenierías"}
    valores.update(datos)
    return Carrera.objects.create(campus=campus, **valores)


def carrera_por_defecto():
    """Carrera compartida por los usuarios de prueba.

    Su campus está inactivo para no aparecer en los catálogos que revisan las pruebas.
    """
    campus, _ = Campus.objects.get_or_create(
        codigo="PRUEBA",
        defaults={
            "nombre": "Campus de prueba",
            "latitud": Decimal("31.742765"),
            "longitud": Decimal("-106.431511"),
            "activo": False,
        },
    )
    carrera, _ = Carrera.objects.get_or_create(campus=campus, nombre="Ingeniería en Sistemas Computacionales")
    return carrera


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
        "telefono": f"656{n:07d}",
        "rol": Rol.PASAJERO,
        "correo_verificado": True,
    }
    valores.update(datos)
    if "carrera" not in valores and valores["rol"] != Rol.ADMIN:
        valores["carrera"] = carrera_por_defecto()
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


def cliente_para(usuario=None):
    """APIClient autenticado como `usuario` (o anónimo si es None)."""
    from rest_framework.test import APIClient

    cliente = APIClient()
    if usuario is not None:
        cliente.force_authenticate(usuario)
    return cliente
