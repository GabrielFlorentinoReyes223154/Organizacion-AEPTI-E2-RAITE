from rest_framework import serializers

from .models import Usuario, Vehiculo
from .models_choices import Rol, TipoVehiculo


class UsuarioSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    es_pasajero = serializers.BooleanField(read_only=True)
    es_conductor = serializers.BooleanField(read_only=True)
    es_admin = serializers.BooleanField(read_only=True)
    roles = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            "id",
            "correo",
            "nombre",
            "apellidos",
            "nombre_completo",
            "edad",
            "sexo",
            "carrera",
            "calificacion",
            "activo",
            "cuenta_activa",
            "suspendido",
            "es_pasajero",
            "es_conductor",
            "es_admin",
            "roles",
        ]
        read_only_fields = ["id", "calificacion", "activo", "cuenta_activa", "suspendido"]

    def get_roles(self, obj):
        return [r.rol.lower() for r in obj.usuario_roles.all()]


class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    roles = serializers.ListField(
        child=serializers.ChoiceField(choices=[Rol.PASAJERO, Rol.CONDUCTOR]),
        allow_empty=False,
        max_length=2,
    )

    class Meta:
        model = Usuario
        fields = [
            "nombre",
            "apellidos",
            "correo",
            "password",
            "edad",
            "sexo",
            "carrera",
            "roles",
        ]
        extra_kwargs = {
            "edad": {"required": True},
            "sexo": {"required": True},
            "carrera": {"required": True},
        }

    def validate_correo(self, value):
        if Usuario.objects.filter(correo__iexact=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value.lower()

    def validate_roles(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("No repitas roles.")
        if Rol.ADMIN in value:
            raise serializers.ValidationError("El rol ADMIN no se otorga en el registro público.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        roles = validated_data.pop("roles")
        return Usuario.objects.create_user(password=password, roles=roles, **validated_data)


class RegistroResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    roles = serializers.ListField(child=serializers.CharField())
    suspendido = serializers.BooleanField()
    requiere_vehiculo = serializers.BooleanField()


class VehiculoRegistroSerializer(serializers.Serializer):
    marca = serializers.CharField(max_length=60)
    modelo = serializers.CharField(max_length=60)
    color = serializers.CharField(max_length=40)
    placas = serializers.CharField(max_length=12)
    tipo = serializers.ChoiceField(choices=[TipoVehiculo.CAMIONETA, TipoVehiculo.COCHE, TipoVehiculo.TROCA])
    asientos_disponibles = serializers.IntegerField(min_value=1, max_value=8)

    def validate_placas(self, value):
        normalized = value.upper().replace("-", "").replace(" ", "")
        if Vehiculo.objects.filter(placas=normalized).exists():
            raise serializers.ValidationError("Esta placa ya está registrada.")
        return normalized


class VehiculoRegistroResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    placas = serializers.CharField()
    vehiculo_valido = serializers.BooleanField()