"""Reglas de negocio de viajes y solicitudes (RF-02 a RF-07, RNF-02).

Toda acción que cambia un viaje bloquea su fila (`select_for_update`) para que dos
peticiones simultáneas no rebasen el cupo ni se salten la tabla de transiciones.
"""

from datetime import timedelta

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.http import Http404
from django.db.models import Count, Prefetch, Q
from django.utils import timezone

from apps.locations.geo import filtro_recuadro, haversine_km
from apps.notifications.models_choices import TipoNotificacion
from apps.notifications.services import describir_viaje, notificar
from Raite_DjangoRest.api import Conflicto

from .compatibilidad import MISMO_SEXO, es_compatible, grupo_compatible, integrantes_del_viaje
from .models import Solicitud, Viaje
from .models_choices import ESTADOS_SOLICITUD_ACTIVOS, EstadoSolicitud, EstadoViaje

# --- Utilidades ---


def bloquear_viaje(viaje_id) -> Viaje:
    """Lee el viaje con la fila bloqueada hasta el fin de la transacción."""
    try:
        return Viaje.objects.select_for_update().get(pk=viaje_id)
    except Viaje.DoesNotExist:
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



# --- Solicitudes (RF-05, RF-06) ---


def _solicitud_bloqueada(solicitud_id):
    """Bloquea primero el viaje y luego la solicitud, siempre en ese orden (evita interbloqueos)."""
    try:
        viaje_id = Solicitud.objects.values_list("viaje_id", flat=True).get(pk=solicitud_id)
    except Solicitud.DoesNotExist:
        raise Http404("No existe la solicitud.")
    viaje = bloquear_viaje(viaje_id)
    solicitud = Solicitud.objects.select_for_update().select_related("pasajero").get(pk=solicitud_id)
    return viaje, solicitud


def _cambiar_solicitud(solicitud, nuevo):
    if not solicitud.puede_cambiar_a(nuevo):
        raise Conflicto(
            f"La solicitud está {solicitud.get_estado_display().lower()}; no se puede cambiar a "
            f"{EstadoSolicitud(nuevo).label.lower()}."
        )
    solicitud.estado = nuevo
    solicitud.respondida_en = timezone.now()
    solicitud.save(update_fields=["estado", "respondida_en"])


def _exigir_viaje_abierto(viaje):
    if viaje.estado != EstadoViaje.PUBLICADO or viaje.esta_vencido:
        raise Conflicto("El viaje ya no admite cambios en sus solicitudes.")


@transaction.atomic
def solicitar_lugar(viaje_id, pasajero) -> Solicitud:
    if not pasajero.puede_solicitar_lugar():
        raise PermissionDenied("No puedes solicitar lugares.")
    viaje = bloquear_viaje(viaje_id)
    if viaje.conductor_id == pasajero.pk:
        raise ValidationError({"viaje": "No puedes pedir lugar en tu propio viaje."})
    if viaje.estado != EstadoViaje.PUBLICADO or viaje.fecha_hora <= timezone.now():
        raise Conflicto("El viaje ya no recibe solicitudes.")
    if viaje.solicitudes.filter(pasajero=pasajero, estado__in=ESTADOS_SOLICITUD_ACTIVOS).exists():
        raise Conflicto("Ya tienes una solicitud activa en este viaje.")
    if viaje.esta_lleno:
        raise Conflicto("El viaje ya está lleno.")
    if not es_compatible(viaje, pasajero):
        raise ValidationError(
            "Este viaje no es compatible con la preferencia de compatibilidad (mismo sexo) "
            "tuya o de sus integrantes."
        )
    _exigir_sin_cruce(pasajero, viaje.fecha_hora, excluir_viaje=viaje)

    solicitud = Solicitud(viaje=viaje, pasajero=pasajero)
    solicitud.full_clean()
    solicitud.save()
    notificar(
        [viaje.conductor],
        TipoNotificacion.SOLICITUD_NUEVA,
        f"{pasajero.nombre_completo} pidió lugar en tu viaje {describir_viaje(viaje)}.",
        viaje,
    )
    return solicitud


@transaction.atomic
def aceptar_solicitud(solicitud_id, conductor) -> Solicitud:
    """Con la fila del viaje bloqueada, dos aceptaciones simultáneas no rebasan el cupo."""
    viaje, solicitud = _solicitud_bloqueada(solicitud_id)
    exigir_conductor(viaje, conductor)
    _exigir_viaje_abierto(viaje)
    if solicitud.estado == EstadoSolicitud.PENDIENTE:
        if viaje.lugares_ocupados >= viaje.lugares_ofrecidos:
            raise Conflicto("Ya no hay lugares disponibles en el viaje.")
        if not es_compatible(viaje, solicitud.pasajero, preferencia=solicitud.preferencia_compatibilidad):
            raise Conflicto("El pasajero ya no es compatible con los integrantes aceptados.")
    _cambiar_solicitud(solicitud, EstadoSolicitud.ACEPTADA)
    notificar(
        [solicitud.pasajero],
        TipoNotificacion.SOLICITUD_ACEPTADA,
        f"Te aceptaron en el viaje {describir_viaje(viaje)}. Ya puedes ver el contacto del conductor.",
        viaje,
    )
    return solicitud


@transaction.atomic
def rechazar_solicitud(solicitud_id, conductor) -> Solicitud:
    viaje, solicitud = _solicitud_bloqueada(solicitud_id)
    exigir_conductor(viaje, conductor)
    _exigir_viaje_abierto(viaje)
    _cambiar_solicitud(solicitud, EstadoSolicitud.RECHAZADA)
    notificar(
        [solicitud.pasajero],
        TipoNotificacion.SOLICITUD_RECHAZADA,
        f"El conductor rechazó tu solicitud en el viaje {describir_viaje(viaje)}.",
        viaje,
    )
    return solicitud


@transaction.atomic
def cancelar_solicitud(solicitud_id, pasajero) -> Solicitud:
    viaje, solicitud = _solicitud_bloqueada(solicitud_id)
    if solicitud.pasajero_id != pasajero.pk:
        raise PermissionDenied("Solo quien hizo la solicitud puede cancelarla.")
    if viaje.estado != EstadoViaje.PUBLICADO:
        raise Conflicto("Solo puedes cancelar mientras el viaje no haya salido.")
    _cambiar_solicitud(solicitud, EstadoSolicitud.CANCELADA)
    notificar(
        [viaje.conductor],
        TipoNotificacion.SOLICITUD_CANCELADA,
        f"{pasajero.nombre_completo} canceló su lugar en tu viaje {describir_viaje(viaje)}.",
        viaje,
    )
    return solicitud


def solicitudes_del_viaje(viaje, conductor):
    exigir_conductor(viaje, conductor)
    return viaje.solicitudes.select_related("pasajero__carrera__campus").order_by("created_at")


def solicitudes_del_pasajero(pasajero, estado=None):
    solicitudes = (
        Solicitud.objects.filter(pasajero=pasajero)
        .select_related("viaje__conductor__carrera__campus", "viaje__vehiculo", "viaje__punto_referencia", "viaje__campus")
        .order_by("-created_at")
    )
    return solicitudes.filter(estado=estado) if estado else solicitudes


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
    """Viajes del conductor con `solicitudes_pendientes` anotado (para "Mis viajes")."""
    viajes = (
        Viaje.objects.filter(conductor=conductor)
        .select_related("punto_referencia", "campus", "vehiculo")
        .annotate(solicitudes_pendientes=Count("solicitudes", filter=Q(solicitudes__estado=EstadoSolicitud.PENDIENTE)))
    )
    if estado:
        return viajes.filter(estado=estado)
    return viajes.filter(Q(estado=EstadoViaje.PUBLICADO) | Q(estado=EstadoViaje.EN_CURSO))


# --- Historial (RF-11) ---

PAPEL_CONDUCTOR, PAPEL_PASAJERO = "conductor", "pasajero"


def historial(usuario, papel=None):
    """Viajes FINALIZADO o CANCELADO en los que participó, del más reciente al más viejo.

    Como pasajero: finalizados con su lugar ACEPTADO y cancelados donde su solicitud quedó
    CANCELADA (al cancelarse el viaje sus solicitudes activas pasan a ese estado).
    """
    como_conductor = Q(conductor=usuario)
    como_pasajero = Q(
        estado=EstadoViaje.FINALIZADO,
        solicitudes__pasajero=usuario,
        solicitudes__estado=EstadoSolicitud.ACEPTADA,
    ) | Q(
        estado=EstadoViaje.CANCELADO,
        solicitudes__pasajero=usuario,
        solicitudes__estado=EstadoSolicitud.CANCELADA,
    )
    condicion = {PAPEL_CONDUCTOR: como_conductor, PAPEL_PASAJERO: como_pasajero}.get(
        papel, como_conductor | como_pasajero
    )
    return (
        Viaje.objects.filter(estado__in=(EstadoViaje.FINALIZADO, EstadoViaje.CANCELADO))
        .filter(condicion)
        .distinct()
        .select_related("conductor__carrera__campus", "vehiculo", "punto_referencia", "campus")
        .order_by("-fecha_hora")
    )


# --- Búsqueda (RF-04) ---


def buscar_viajes(usuario, filtros: dict) -> list[Viaje]:
    """Viajes PUBLICADO a futuro (los vencidos quedan fuera), con lugar libre, que no sean del
    usuario y compatibles con él. Si hay punto o lat/lon, filtra por radio y ordena por distancia.

    `filtros`: punto, lat, lon, radio_km, campus, sentido, desde, hasta (todos opcionales).
    """
    viajes = (
        Viaje.objects.filter(estado=EstadoViaje.PUBLICADO, fecha_hora__gt=timezone.now())
        .exclude(conductor=usuario)
        .select_related("conductor__carrera__campus", "vehiculo", "punto_referencia", "campus")
        .prefetch_related(
            Prefetch(
                "solicitudes",
                queryset=Solicitud.objects.filter(estado=EstadoSolicitud.ACEPTADA).select_related("pasajero__carrera__campus"),
                to_attr="aceptadas_cache",
            )
        )
    )
    if filtros.get("campus"):
        viajes = viajes.filter(campus=filtros["campus"])
    if filtros.get("sentido"):
        viajes = viajes.filter(sentido=filtros["sentido"])
    if filtros.get("desde"):
        viajes = viajes.filter(fecha_hora__gte=filtros["desde"])
    if filtros.get("hasta"):
        viajes = viajes.filter(fecha_hora__lte=filtros["hasta"])

    centro = None
    if filtros.get("punto"):
        centro = (filtros["punto"].latitud, filtros["punto"].longitud)
    elif filtros.get("lat") is not None:
        centro = (filtros["lat"], filtros["lon"])
    radio = filtros.get("radio_km") or settings.BUSQUEDA_RADIO_KM
    if centro:
        viajes = viajes.filter(**filtro_recuadro(*centro, radio, prefijo="punto_referencia__"))

    resultado = []
    for viaje in viajes:
        aceptadas = viaje.aceptadas_cache
        if len(aceptadas) >= viaje.lugares_ofrecidos:
            continue
        if not es_compatible(viaje, usuario, aceptadas=aceptadas):
            continue
        if centro:
            viaje.distancia_km = haversine_km(*centro, viaje.punto_referencia.latitud, viaje.punto_referencia.longitud)
            if viaje.distancia_km > radio:
                continue
        resultado.append(viaje)

    if centro:
        resultado.sort(key=lambda v: (v.distancia_km, v.fecha_hora))
    else:
        resultado.sort(key=lambda v: v.fecha_hora)
    return resultado
