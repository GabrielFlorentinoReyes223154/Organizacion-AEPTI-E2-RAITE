"""Reglas de negocio de viajes y solicitudes (RF-02 a RF-07, RNF-02).

Toda acción que cambia un viaje bloquea su fila (`select_for_update`) para que dos
peticiones simultáneas no rebasen el cupo ni se salten la tabla de transiciones.
"""

from datetime import timedelta

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.notifications.models_choices import TipoNotificacion
from apps.notifications.services import describir_viaje, notificar
from Raite_DjangoRest.api import Conflicto

from .compatibilidad import MISMO_SEXO, grupo_compatible, integrantes_del_viaje
from .models import Solicitud, Viaje
from .models_choices import ESTADOS_SOLICITUD_ACTIVOS, EstadoSolicitud, EstadoViaje

# --- Utilidades ---


def bloquear_viaje(viaje_id) -> Viaje:
    """Lee el viaje con la fila bloqueada hasta el fin de la transacción."""
    try:
        return Viaje.objects.select_for_update().get(pk=viaje_id)
    except Viaje.DoesNotExist:
        from django.http import Http404

        raise Http404("No existe el viaje.")


def exigir_conductor(viaje, usuario):
    if viaje.conductor_id != usuario.pk:
        raise PermissionDenied("Solo el conductor del viaje puede hacer esto.")


def hay_cruce(usuario, fecha_hora, excluir_viaje=None, excluir_solicitud=None) -> bool:
    """¿Tiene el usuario otro viaje vigente (como conductor) o una solicitud activa en un
    viaje vigente a menos de VENTANA_CRUCE_MINUTOS de `fecha_hora`? Los vencidos no cuentan."""
    ventana = timedelta(minutes=settings.VENTANA_CRUCE_MINUTOS)
    rango = {"fecha_hora__gt": fecha_hora - ventana, "fecha_hora__lt": fecha_hora + ventana}

    viajes = Viaje.objects.vigentes().filter(conductor=usuario, **rango)
    if excluir_viaje is not None:
        viajes = viajes.exclude(pk=excluir_viaje.pk)
    if viajes.exists():
        return True

    solicitudes = Solicitud.objects.filter(
        pasajero=usuario,
        estado__in=ESTADOS_SOLICITUD_ACTIVOS,
        viaje__in=Viaje.objects.vigentes().filter(**rango),
    )
    if excluir_solicitud is not None:
        solicitudes = solicitudes.exclude(pk=excluir_solicitud.pk)
    if excluir_viaje is not None:
        solicitudes = solicitudes.exclude(viaje=excluir_viaje)
    return solicitudes.exists()


MENSAJE_CRUCE = "Ya tienes otro viaje o solicitud a menos de {} minutos de esa hora."


def _exigir_sin_cruce(usuario, fecha_hora, **excluir):
    if hay_cruce(usuario, fecha_hora, **excluir):
        raise Conflicto(MENSAJE_CRUCE.format(settings.VENTANA_CRUCE_MINUTOS))


def _pasajeros(solicitudes):
    return [s.pasajero for s in solicitudes]


# --- Viajes ---


@transaction.atomic
def publicar_viaje(conductor, datos: dict) -> Viaje:
    if not conductor.puede_publicar_viaje():
        raise PermissionDenied("No puedes publicar viajes.")
    viaje = Viaje(conductor=conductor, vehiculo=conductor.vehiculo, **datos)
    viaje.full_clean()
    _exigir_sin_cruce(conductor, viaje.fecha_hora)
    viaje.save()
    return viaje


@transaction.atomic
def editar_viaje(viaje_id, conductor, datos: dict) -> Viaje:
    viaje = bloquear_viaje(viaje_id)
    exigir_conductor(viaje, conductor)
    if viaje.estado != EstadoViaje.PUBLICADO:
        raise Conflicto("Solo se puede editar un viaje publicado.")
    if viaje.esta_vencido:
        raise Conflicto("El viaje ya venció; solo puedes cancelarlo.")

    nueva_fecha = datos.get("fecha_hora")
    if nueva_fecha is not None and nueva_fecha != viaje.fecha_hora:
        if nueva_fecha <= timezone.now():
            raise ValidationError({"fecha_hora": "La hora de salida debe ser en el futuro."})
        _exigir_sin_cruce(conductor, nueva_fecha, excluir_viaje=viaje)

    if datos.get("preferencia_compatibilidad") == MISMO_SEXO:
        integrantes = [(sexo, MISMO_SEXO) for sexo, _ in integrantes_del_viaje(viaje)]
        if not grupo_compatible(integrantes):
            raise ValidationError(
                {"preferencia_compatibilidad": "Ya aceptaste pasajeros de otro sexo en este viaje."}
            )

    for campo, valor in datos.items():
        setattr(viaje, campo, valor)
    viaje.full_clean()
    viaje.save()

    activas = viaje.solicitudes.filter(estado__in=ESTADOS_SOLICITUD_ACTIVOS).select_related("pasajero")
    notificar(
        _pasajeros(activas),
        TipoNotificacion.VIAJE_MODIFICADO,
        f"El conductor modificó el viaje {describir_viaje(viaje)}.",
        viaje,
    )
    return viaje


def _cambiar_estado(viaje, nuevo):
    if not viaje.puede_cambiar_a(nuevo):
        raise Conflicto(
            f"No se puede pasar de {viaje.get_estado_display().lower()} a {EstadoViaje(nuevo).label.lower()}."
        )
    viaje.estado = nuevo
    viaje.save(update_fields=["estado", "updated_at"])


def _cerrar_solicitudes(solicitudes, estado):
    solicitudes = list(solicitudes.select_related("pasajero"))
    ahora = timezone.now()
    for solicitud in solicitudes:
        solicitud.estado = estado
        solicitud.respondida_en = ahora
    Solicitud.objects.bulk_update(solicitudes, ["estado", "respondida_en"])
    return solicitudes


@transaction.atomic
def cancelar_viaje(viaje_id, conductor) -> Viaje:
    viaje = bloquear_viaje(viaje_id)
    exigir_conductor(viaje, conductor)
    _cambiar_estado(viaje, EstadoViaje.CANCELADO)
    cerradas = _cerrar_solicitudes(
        viaje.solicitudes.filter(estado__in=ESTADOS_SOLICITUD_ACTIVOS), EstadoSolicitud.CANCELADA
    )
    notificar(
        _pasajeros(cerradas),
        TipoNotificacion.VIAJE_CANCELADO,
        f"El conductor canceló el viaje {describir_viaje(viaje)}.",
        viaje,
    )
    return viaje


@transaction.atomic
def iniciar_viaje(viaje_id, conductor) -> Viaje:
    viaje = bloquear_viaje(viaje_id)
    exigir_conductor(viaje, conductor)
    if viaje.estado == EstadoViaje.PUBLICADO:
        if viaje.esta_vencido:
            raise Conflicto("El viaje ya venció; solo puedes cancelarlo.")
        if timezone.now() < viaje.inicio_permitido_desde:
            desde = timezone.localtime(viaje.inicio_permitido_desde)
            raise Conflicto(f"Podrás iniciar el viaje desde las {desde:%H:%M} del {desde:%d/%m}.")
    _cambiar_estado(viaje, EstadoViaje.EN_CURSO)
    rechazadas = _cerrar_solicitudes(
        viaje.solicitudes.filter(estado=EstadoSolicitud.PENDIENTE), EstadoSolicitud.RECHAZADA
    )
    notificar(
        _pasajeros(rechazadas),
        TipoNotificacion.SOLICITUD_RECHAZADA,
        f"El viaje {describir_viaje(viaje)} ya salió sin confirmar tu lugar.",
        viaje,
    )
    return viaje


@transaction.atomic
def finalizar_viaje(viaje_id, conductor) -> Viaje:
    viaje = bloquear_viaje(viaje_id)
    exigir_conductor(viaje, conductor)
    _cambiar_estado(viaje, EstadoViaje.FINALIZADO)
    notificar(
        list(viaje.pasajeros_confirmados),
        TipoNotificacion.VIAJE_FINALIZADO,
        f"Terminó el viaje {describir_viaje(viaje)}. Califica a tu conductor.",
        viaje,
    )
    return viaje


# --- Lectura ---


def puede_ver_viaje(viaje, usuario) -> bool:
    """Publicado: cualquiera. Otro estado: el conductor o quien tuvo una solicitud en él."""
    if viaje.estado == EstadoViaje.PUBLICADO and not viaje.esta_vencido:
        return True
    return viaje.conductor_id == usuario.pk or viaje.solicitudes.filter(pasajero=usuario).exists()


def tiene_lugar_confirmado(viaje, usuario) -> bool:
    """Contacto y placas solo se muestran con solicitud ACEPTADA (regla 4, RNF-02)."""
    return viaje.solicitudes.filter(pasajero=usuario, estado=EstadoSolicitud.ACEPTADA).exists()


def viajes_del_conductor(conductor, estado=None):
    viajes = Viaje.objects.filter(conductor=conductor).select_related("punto_referencia", "campus", "vehiculo")
    if estado:
        return viajes.filter(estado=estado)
    return viajes.filter(Q(estado=EstadoViaje.PUBLICADO) | Q(estado=EstadoViaje.EN_CURSO))
