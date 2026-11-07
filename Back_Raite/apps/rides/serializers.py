"""Forma de entrada/salida de viajes y solicitudes. Las reglas viven en services.py.

Datos de contacto (teléfono) y placas solo salen con solicitud ACEPTADA (regla 4, RNF-02).
La vista pasa en el contexto `contacto_visible` (ids de viajes donde quien consulta tiene
lugar confirmado) y `es_conductor` (True si quien consulta es el conductor del viaje).
"""

from django.conf import settings
from rest_framework import serializers

from apps.accounts.models import Usuario
from apps.locations.models import Campus, PuntoReferencia
from apps.locations.serializers import CampusSerializer, PuntoReferenciaSerializer

from .models import Solicitud, Viaje
from .models_choices import SentidoViaje


class UsuarioPublicoSerializer(serializers.ModelSerializer):
    """Lo que cualquier usuario puede ver de otro."""

    nombre_completo = serializers.CharField(read_only=True)

    class Meta:
        model = Usuario
        fields = ["id", "nombre", "nombre_completo", "sexo", "carrera", "calificacion"]
        read_only_fields = fields


class UsuarioConContactoSerializer(UsuarioPublicoSerializer):
    class Meta(UsuarioPublicoSerializer.Meta):
        fields = [*UsuarioPublicoSerializer.Meta.fields, "telefono"]
        read_only_fields = fields


class ViajeEntradaSerializer(serializers.ModelSerializer):
    """Publicar un viaje. El conductor y el vehículo salen de la sesión."""

    punto_referencia = serializers.PrimaryKeyRelatedField(
        queryset=PuntoReferencia.objects.filter(activo=True)
    )
    campus = serializers.PrimaryKeyRelatedField(queryset=Campus.objects.filter(activo=True))

    class Meta:
        model = Viaje
        fields = [
            "punto_referencia",
            "campus",
            "sentido",
            "fecha_hora",
            "lugares_ofrecidos",
            "preferencia_compatibilidad",
            "notas",
        ]


class ViajeEdicionSerializer(serializers.ModelSerializer):
    """Editar un viaje publicado. Punto, campus y sentido no cambian: se cancela y se publica otro."""

    class Meta:
        model = Viaje
        fields = ["fecha_hora", "lugares_ofrecidos", "preferencia_compatibilidad", "notas"]


class ViajeSerializer(serializers.ModelSerializer):
    conductor = serializers.SerializerMethodField()
    vehiculo = serializers.SerializerMethodField()
    punto_referencia = PuntoReferenciaSerializer(read_only=True)
    campus = CampusSerializer(read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    sentido_display = serializers.CharField(source="get_sentido_display", read_only=True)
    lugares_disponibles = serializers.SerializerMethodField()
    esta_vencido = serializers.BooleanField(read_only=True)
    inicio_permitido_desde = serializers.DateTimeField(read_only=True)
    distancia_km = serializers.SerializerMethodField()

    class Meta:
        model = Viaje
        fields = [
            "id",
            "conductor",
            "vehiculo",
            "punto_referencia",
            "campus",
            "sentido",
            "sentido_display",
            "fecha_hora",
            "lugares_ofrecidos",
            "lugares_disponibles",
            "preferencia_compatibilidad",
            "notas",
            "estado",
            "estado_display",
            "esta_vencido",
            "inicio_permitido_desde",
            "distancia_km",
        ]
        read_only_fields = fields

    def _contacto_visible(self, viaje) -> bool:
        visibles = self.context.get("contacto_visible", set())
        return viaje.pk in visibles or self.context.get("es_conductor", False)

    def get_conductor(self, viaje):
        clase = UsuarioConContactoSerializer if self._contacto_visible(viaje) else UsuarioPublicoSerializer
        return clase(viaje.conductor).data

    def get_vehiculo(self, viaje):
        datos = {
            "marca": viaje.vehiculo.marca,
            "modelo": viaje.vehiculo.modelo,
            "color": viaje.vehiculo.color,
            "tipo": viaje.vehiculo.tipo,
        }
        if self._contacto_visible(viaje):
            datos["placas"] = viaje.vehiculo.placas
        return datos

    def get_distancia_km(self, viaje):
        distancia = getattr(viaje, "distancia_km", None)
        return round(distancia, 2) if distancia is not None else None

    def get_lugares_disponibles(self, viaje) -> int:
        aceptadas = getattr(viaje, "aceptadas_cache", None)  # la búsqueda ya las trae
        if aceptadas is None:
            return viaje.lugares_disponibles
        return max(viaje.lugares_ofrecidos - len(aceptadas), 0)


class BusquedaSerializer(serializers.Serializer):
    """Filtros de `GET /api/viajes/`. Horas en ISO 8601 (sin zona = hora de Juárez)."""

    punto = serializers.PrimaryKeyRelatedField(queryset=PuntoReferencia.objects.filter(activo=True), required=False)
    lat = serializers.FloatField(required=False, min_value=-90, max_value=90)
    lon = serializers.FloatField(required=False, min_value=-180, max_value=180)
    radio_km = serializers.FloatField(required=False, min_value=0.1)
    campus = serializers.PrimaryKeyRelatedField(queryset=Campus.objects.filter(activo=True), required=False)
    sentido = serializers.ChoiceField(choices=SentidoViaje.choices, required=False)
    desde = serializers.DateTimeField(required=False)
    hasta = serializers.DateTimeField(required=False)

    def validate_radio_km(self, valor):
        maximo = settings.BUSQUEDA_RADIO_MAX_KM
        if valor > maximo:
            raise serializers.ValidationError(f"El radio máximo es {maximo} km.")
        return valor

    def validate(self, attrs):
        if ("lat" in attrs) != ("lon" in attrs):
            raise serializers.ValidationError("Envía lat y lon juntos.")
        if "punto" in attrs and "lat" in attrs:
            raise serializers.ValidationError("Usa punto o lat/lon, no ambos.")
        if attrs.get("desde") and attrs.get("hasta") and attrs["desde"] > attrs["hasta"]:
            raise serializers.ValidationError({"hasta": "Debe ser posterior a desde."})
        return attrs


class ViajeDetalleSerializer(ViajeSerializer):
    """Detalle: agrega la solicitud propia y, para el conductor, sus pasajeros confirmados."""

    mi_solicitud = serializers.SerializerMethodField()
    pasajeros_confirmados = serializers.SerializerMethodField()

    class Meta(ViajeSerializer.Meta):
        fields = [*ViajeSerializer.Meta.fields, "mi_solicitud", "pasajeros_confirmados"]
        read_only_fields = fields

    def get_mi_solicitud(self, viaje):
        usuario = self.context["request"].user
        solicitud = viaje.solicitudes.filter(pasajero=usuario).order_by("-created_at").first()
        return {"id": solicitud.id, "estado": solicitud.estado} if solicitud else None

    def get_pasajeros_confirmados(self, viaje):
        if not self.context.get("es_conductor"):
            return None
        return UsuarioConContactoSerializer(viaje.pasajeros_confirmados, many=True).data


class SolicitudSerializer(serializers.ModelSerializer):
    """Solicitud vista por el conductor: el teléfono del pasajero solo si está aceptada."""

    pasajero = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)

    class Meta:
        model = Solicitud
        fields = ["id", "viaje", "pasajero", "preferencia_compatibilidad", "estado", "estado_display", "created_at", "respondida_en"]
        read_only_fields = fields

    def get_pasajero(self, solicitud):
        from .models_choices import EstadoSolicitud

        clase = (
            UsuarioConContactoSerializer
            if solicitud.estado == EstadoSolicitud.ACEPTADA
            else UsuarioPublicoSerializer
        )
        return clase(solicitud.pasajero).data


class MiSolicitudSerializer(serializers.ModelSerializer):
    """Solicitud vista por el pasajero, con el resumen del viaje."""

    viaje = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)

    class Meta:
        model = Solicitud
        fields = ["id", "viaje", "estado", "estado_display", "created_at", "respondida_en"]
        read_only_fields = fields

    def get_viaje(self, solicitud):
        from .models_choices import EstadoSolicitud

        visibles = {solicitud.viaje_id} if solicitud.estado == EstadoSolicitud.ACEPTADA else set()
        return ViajeSerializer(solicitud.viaje, context={**self.context, "contacto_visible": visibles}).data
