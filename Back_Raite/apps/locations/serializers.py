from rest_framework import serializers

from .models import Campus, Carrera, PuntoReferencia


class CampusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campus
        fields = ["id", "codigo", "nombre", "latitud", "longitud"]


class CarreraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrera
        fields = ["id", "campus", "nombre", "area"]


class PuntoReferenciaSerializer(serializers.ModelSerializer):
    distancia_km = serializers.SerializerMethodField()

    class Meta:
        model = PuntoReferencia
        fields = ["id", "nombre", "latitud", "longitud", "distancia_km"]

    def get_distancia_km(self, punto):
        distancia = getattr(punto, "distancia_km", None)
        return round(distancia, 2) if distancia is not None else None


class CoordenadasSerializer(serializers.Serializer):
    """`lat` y `lon` opcionales, pero si viene uno debe venir el otro."""

    lat = serializers.FloatField(required=False, min_value=-90, max_value=90)
    lon = serializers.FloatField(required=False, min_value=-180, max_value=180)

    def validate(self, attrs):
        if ("lat" in attrs) != ("lon" in attrs):
            raise serializers.ValidationError("Envía lat y lon juntos.")
        return attrs
