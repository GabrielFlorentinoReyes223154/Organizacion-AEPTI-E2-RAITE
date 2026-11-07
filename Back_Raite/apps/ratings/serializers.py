from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.rides.serializers import UsuarioPublicoSerializer

from .models import Calificacion


class CalificacionEntradaSerializer(serializers.Serializer):
    calificado = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    puntuacion = serializers.IntegerField(min_value=1, max_value=5)
    comentario = serializers.CharField(max_length=500, required=False, allow_blank=True, default="")


class CalificacionSerializer(serializers.ModelSerializer):
    calificado = UsuarioPublicoSerializer(read_only=True)

    class Meta:
        model = Calificacion
        fields = ["id", "viaje", "calificado", "puntuacion", "comentario", "created_at"]
        read_only_fields = fields


class PendienteSerializer(serializers.Serializer):
    viaje = serializers.SerializerMethodField()
    usuario = serializers.SerializerMethodField()

    def get_viaje(self, par):
        viaje = par[0]
        return {
            "id": str(viaje.id),
            "punto_referencia": viaje.punto_referencia.nombre,
            "campus": viaje.campus.codigo,
            "sentido": viaje.sentido,
            "fecha_hora": serializers.DateTimeField().to_representation(viaje.fecha_hora),
        }

    def get_usuario(self, par):
        return UsuarioPublicoSerializer(par[1]).data
