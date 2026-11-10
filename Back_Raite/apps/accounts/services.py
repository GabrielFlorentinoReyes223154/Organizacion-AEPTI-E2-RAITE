"""Reglas de negocio de cuentas: registro, verificación de correo y edición de perfil/vehículo (RF-01, RF-07)."""

import hashlib
import secrets
import uuid
from types import SimpleNamespace

from django.conf import settings
from django.core import signing
from django.core.cache import cache
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.utils.crypto import constant_time_compare, salted_hmac

from Raite_DjangoRest.api import Conflicto

from .correos import correo_codigo
from .models import Usuario, Vehiculo
from .models_choices import Rol

MENSAJE_CODIGO_INVALIDO = "El código es incorrecto o ya venció."
MENSAJE_REGISTRO_VENCIDO = "Tu registro venció. Vuelve a registrarte."
SAL_REGISTRO = "accounts.registro-pendiente"
CAMPOS_REGISTRO = (
    "correo",
    "nombre",
    "apellidos",
    "edad",
    "sexo",
    "carrera",
    "telefono",
    "preferencia_compatibilidad",
    "rol",
    "password",
)


def _clave_envio(correo: str) -> str:
    return f"registro:envio:{hashlib.sha256(correo.encode()).hexdigest()}"


def _hash_codigo(jti: str, codigo: str) -> str:
    return salted_hmac(SAL_REGISTRO, f"{jti}:{codigo}").hexdigest()


def _emitir_registro(datos: dict) -> str:
    """Manda un código nuevo y devuelve el token firmado con los datos del registro.

    El token lo conserva el navegador de quien se registra; en el servidor solo queda, por
    60 s, el hash del correo para no permitir envíos seguidos.
    """
    espera = settings.CODIGO_REENVIO_SEGUNDOS
    clave = _clave_envio(datos["correo"])
    if not cache.add(clave, True, espera):
        raise Conflicto(f"Espera {espera} segundos antes de pedir otro código.")

    codigo = f"{secrets.randbelow(10**6):06d}"
    jti = uuid.uuid4().hex
    try:
        correo_codigo(SimpleNamespace(nombre=datos["nombre"], correo=datos["correo"]), codigo).send()
    except Exception:
        cache.delete(clave)
        raise
    return signing.dumps({**datos, "jti": jti, "codigo_hash": _hash_codigo(jti, codigo)}, salt=SAL_REGISTRO, compress=True)


def _leer_registro(token: str) -> dict:
    try:
        return signing.loads(token, salt=SAL_REGISTRO, max_age=settings.CODIGO_VERIFICACION_MINUTOS * 60)
    except signing.BadSignature:
        raise ValidationError({"codigo": MENSAJE_REGISTRO_VENCIDO})


def registrar(datos: dict) -> tuple[Usuario, str]:
    """Valida el registro y manda el código sin guardar nada en la base de datos.

    Devuelve el usuario sin guardar (solo para armar la respuesta) y el token del registro.
    El correo no queda apartado: la cuenta se crea hasta confirmar el código.
    """
    datos = dict(datos)
    password = datos.pop("password")
    rol = datos.pop("rol", None) or Rol.PASAJERO
    usuario = Usuario(rol=rol, **datos)
    usuario.correo = Usuario.objects.normalize_email(usuario.correo).lower()
    usuario.set_password(password)
    usuario.full_clean(validate_unique=False)
    return usuario, _emitir_registro({campo: getattr(usuario, campo) for campo in CAMPOS_REGISTRO})


def verificar_correo(token: str, codigo: str) -> Usuario:
    """Crea la cuenta, ya verificada, si el código del token coincide.

    Una cuenta antigua que se quedó sin verificar se reemplaza, porque quien confirma el
    código demuestra ser dueño del correo.
    """
    datos = _leer_registro(token)
    clave = f"registro:intentos:{datos['jti']}"
    cache.add(clave, 0, settings.CODIGO_VERIFICACION_MINUTOS * 60)
    intentos = cache.incr(clave)
    maximo = settings.CODIGO_VERIFICACION_MAX_INTENTOS
    agotados = ValidationError({"codigo": "Agotaste los intentos. Pide un código nuevo."})
    if intentos > maximo:
        raise agotados
    if not constant_time_compare(_hash_codigo(datos["jti"], codigo), datos["codigo_hash"]):
        raise agotados if intentos >= maximo else ValidationError({"codigo": MENSAJE_CODIGO_INVALIDO})

    conflicto = Conflicto("Tu correo ya está verificado. Inicia sesión.")
    try:
        with transaction.atomic():
            previo = Usuario.objects.select_for_update().filter(correo__iexact=datos["correo"]).first()
            if previo is not None and previo.correo_verificado:
                raise conflicto
            if previo is not None:
                previo.delete()
            usuario = Usuario(correo_verificado=True, **{campo: datos[campo] for campo in CAMPOS_REGISTRO})
            usuario.full_clean()
            usuario.save()
    except IntegrityError:
        raise conflicto
    return usuario


def reenviar_codigo(token: str) -> str:
    """Manda un código nuevo y devuelve el token que reemplaza al anterior."""
    datos = _leer_registro(token)
    if Usuario.objects.filter(correo__iexact=datos["correo"], correo_verificado=True).exists():
        raise Conflicto("Tu correo ya está verificado. Inicia sesión.")
    return _emitir_registro({campo: datos[campo] for campo in CAMPOS_REGISTRO})


@transaction.atomic
def actualizar_perfil(usuario: Usuario, datos: dict) -> Usuario:
    for campo, valor in datos.items():
        setattr(usuario, campo, valor)
    usuario.full_clean()
    usuario.save()
    return usuario


@transaction.atomic
def registrar_vehiculo(usuario: Usuario, datos: dict) -> Vehiculo:
    """Registra el vehículo del usuario. Un PASAJERO que registra vehículo pasa a AMBOS,
    porque cualquier estudiante puede alternar entre pasajero y conductor (SRS §2 y §5)."""
    if usuario.es_admin:
        raise PermissionDenied("Las cuentas de administrador no registran vehículo.")
    if hasattr(usuario, "vehiculo"):
        raise Conflicto("Ya tienes un vehículo registrado. Edítalo en lugar de crear otro.")
    vehiculo = Vehiculo(usuario=usuario, **datos)
    vehiculo.full_clean()
    vehiculo.save()
    if usuario.rol == Rol.PASAJERO:
        usuario.rol = Rol.AMBOS
        usuario.save(update_fields=["rol", "updated_at"])
    return vehiculo


@transaction.atomic
def actualizar_vehiculo(vehiculo: Vehiculo, datos: dict) -> Vehiculo:
    from apps.rides.models import Viaje

    nuevos_asientos = datos.get("asientos_disponibles")
    if nuevos_asientos is not None:
        excedidos = Viaje.objects.vigentes().filter(vehiculo=vehiculo, lugares_ofrecidos__gt=nuevos_asientos)
        if excedidos.exists():
            raise ValidationError(
                {"asientos_disponibles": "Tienes viajes vigentes que ofrecen más lugares que eso."}
            )
    for campo, valor in datos.items():
        setattr(vehiculo, campo, valor)
    vehiculo.full_clean()
    vehiculo.save()
    return vehiculo
