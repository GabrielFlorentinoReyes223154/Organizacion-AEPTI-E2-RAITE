from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.rides.models import Viaje
from apps.rides.serializers import UsuarioPublicoSerializer

from .models import Reporte


class ReporteEntradaSerializer(serializers.Serializer):
    viaje = serializers.PrimaryKeyRelatedField(queryset=Viaje.objects.all())
    reportado = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    motivo = serializers.CharField(max_length=1000)


class ReporteSerializer(serializers.ModelSerializer):
    """Lo que ve quien reporta (sin las notas internas del admin)."""

    reportado = UsuarioPublicoSerializer(read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)

    class Meta:
        model = Reporte
        fields = ["id", "viaje", "reportado", "motivo", "estado", "estado_display", "created_at", "resuelto_en"]
        read_only_fields = fields
