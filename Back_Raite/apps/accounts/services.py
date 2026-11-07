"""Reglas de negocio de cuentas: registro, verificación de correo y edición de perfil/vehículo (RF-01, RF-07)."""

from datetime import timedelta

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from Raite_DjangoRest.api import Conflicto

from .correos import correo_codigo
from .models import CodigoVerificacion, Usuario, Vehiculo
from .models_choices import Rol

MENSAJE_CODIGO_INVALIDO = "El código es incorrecto o ya venció."


def enviar_codigo(usuario) -> None:
    """Genera un código nuevo y lo manda al correo del usuario (en desarrollo sale en la terminal).
    Se usa al registrarse y al pedir otro código."""
    _, codigo = CodigoVerificacion.generar(usuario)
    correo_codigo(usuario, codigo).send()


@transaction.atomic
def registrar(datos: dict) -> Usuario:
    """Crea el usuario sin verificar (validando el modelo completo) y le envía el código."""
    datos = dict(datos)
    password = datos.pop("password")
    rol = datos.pop("rol", None) or Rol.PASAJERO
    usuario = Usuario(rol=rol, **datos)
    usuario.correo = Usuario.objects.normalize_email(usuario.correo).lower()
    usuario.set_password(password)
    usuario.full_clean()
    usuario.save()
    enviar_codigo(usuario)
    return usuario


def _usuario_por_correo(correo):
    return Usuario.objects.filter(correo__iexact=(correo or "").strip()).first()


def verificar_correo(correo: str, codigo: str) -> Usuario:
    """Activa la cuenta si el código vigente más reciente coincide.

    Los intentos fallidos se guardan aunque la petición termine en error, por eso
    `comprobar()` no va dentro de una transacción que se revierta.
    """
    usuario = _usuario_por_correo(correo)
    if usuario is None:
        raise ValidationError({"codigo": MENSAJE_CODIGO_INVALIDO})
    if usuario.correo_verificado:
        raise Conflicto("Tu correo ya está verificado. Inicia sesión.")

    registro = usuario.codigos_verificacion.filter(usado=False).first()
    if registro is None or not registro.comprobar(codigo):
        if registro is not None and registro.intentos_agotados():
            raise ValidationError({"codigo": "Agotaste los intentos. Pide un código nuevo."})
        raise ValidationError({"codigo": MENSAJE_CODIGO_INVALIDO})

    with transaction.atomic():
        registro.usado = True
        registro.save(update_fields=["usado"])
        usuario.correo_verificado = True
        usuario.save(update_fields=["correo_verificado", "updated_at"])
    return usuario


@transaction.atomic
def reenviar_codigo(correo: str) -> None:
    """Anula los códigos anteriores y manda uno nuevo. Si el correo no existe o ya está
    verificado no hace nada (la vista responde igual en todos los casos)."""
    usuario = _usuario_por_correo(correo)
    if usuario is None or usuario.correo_verificado:
        return
    ultimo = usuario.codigos_verificacion.first()
    espera = timedelta(seconds=settings.CODIGO_REENVIO_SEGUNDOS)
    if ultimo and timezone.now() - ultimo.creado_en < espera:
        raise Conflicto(
            f"Espera {settings.CODIGO_REENVIO_SEGUNDOS} segundos antes de pedir otro código."
        )
    usuario.codigos_verificacion.filter(usado=False).update(usado=True)
    enviar_codigo(usuario)


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
