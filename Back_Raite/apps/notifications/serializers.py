from rest_framework import serializers

from .models import Notificacion


class NotificacionSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)

    class Meta:
        model = Notificacion
        fields = ["id", "tipo", "tipo_display", "mensaje", "viaje", "leida", "created_at"]
        read_only_fields = fields
