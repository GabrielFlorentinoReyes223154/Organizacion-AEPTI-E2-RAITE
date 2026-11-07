from rest_framework import serializers

from .models import ASIENTOS_MAX, ASIENTOS_MIN, Usuario, Vehiculo
from .models_choices import Rol, TipoVehiculo


class UsuarioSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    es_pasajero = serializers.BooleanField(read_only=True)
    es_conductor = serializers.BooleanField(read_only=True)
    es_admin = serializers.BooleanField(read_only=True)
    rol_display = serializers.CharField(source="get_rol_display", read_only=True)

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
            "telefono",
            "preferencia_compatibilidad",
            "calificacion",
            "correo_verificado",
            "suspendido",
            "rol",
            "rol_display",
            "es_pasajero",
            "es_conductor",
            "es_admin",
        ]
        read_only_fields = ["id", "calificacion", "correo_verificado", "suspendido"]


class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    rol = serializers.ChoiceField(choices=[Rol.PASAJERO, Rol.CONDUCTOR, Rol.AMBOS], required=False)

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
            "telefono",
            "rol",
        ]
        extra_kwargs = {
            "edad": {"required": True},
            "sexo": {"required": True},
            "carrera": {"required": True},
            "telefono": {"required": True},
        }

    def validate_correo(self, value):
        if Usuario.objects.filter(correo__iexact=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value.lower()

    def validate_rol(self, value):
        if value == Rol.ADMIN:
            raise serializers.ValidationError("El rol ADMIN no se otorga en el registro público.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        rol = validated_data.pop("rol", None)
        return Usuario.objects.create_user(password=password, rol=rol, **validated_data)


class RegistroResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    rol = serializers.IntegerField()
    rol_display = serializers.CharField()
    suspendido = serializers.BooleanField()
    requiere_vehiculo = serializers.BooleanField()


class VehiculoRegistroSerializer(serializers.Serializer):
    marca = serializers.CharField(max_length=60)
    modelo = serializers.CharField(max_length=60)
    color = serializers.CharField(max_length=40)
    placas = serializers.CharField(max_length=12)
    tipo = serializers.ChoiceField(choices=[TipoVehiculo.CAMIONETA, TipoVehiculo.COCHE, TipoVehiculo.TROCA])
    asientos_disponibles = serializers.IntegerField(min_value=ASIENTOS_MIN, max_value=ASIENTOS_MAX)

    def validate_placas(self, value):
        normalized = value.upper().replace("-", "").replace(" ", "")
        if Vehiculo.objects.filter(placas=normalized).exists():
            raise serializers.ValidationError("Esta placa ya está registrada.")
        return normalized


class VehiculoRegistroResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    placas = serializers.CharField()
    vehiculo_valido = serializers.BooleanField()