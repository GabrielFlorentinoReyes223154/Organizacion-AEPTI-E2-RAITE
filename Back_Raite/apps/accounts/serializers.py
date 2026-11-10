"""Forma de entrada/salida del API de cuentas. Las reglas de negocio viven en services.py."""

from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import ASIENTOS_MAX, ASIENTOS_MIN, Usuario, Vehiculo
from .models_choices import Rol, TipoVehiculo


class VehiculoSerializer(serializers.ModelSerializer):
    """Vehículo propio (con placas). Para otros usuarios ver apps.rides.serializers."""

    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)

    class Meta:
        model = Vehiculo
        fields = ["id", "marca", "modelo", "color", "placas", "tipo", "tipo_display", "asientos_disponibles", "activo"]
        read_only_fields = ["id", "placas", "tipo", "activo"]


class UsuarioSerializer(serializers.ModelSerializer):
    """Perfil propio (`/api/auth/me/`)."""

    nombre_completo = serializers.CharField(read_only=True)
    es_pasajero = serializers.BooleanField(read_only=True)
    es_conductor = serializers.BooleanField(read_only=True)
    es_admin = serializers.BooleanField(read_only=True)
    rol_display = serializers.CharField(source="get_rol_display", read_only=True)
    vehiculo = serializers.SerializerMethodField()

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
            "vehiculo",
        ]
        read_only_fields = fields

    def get_vehiculo(self, usuario):
        vehiculo = getattr(usuario, "vehiculo", None)
        return VehiculoSerializer(vehiculo).data if vehiculo else None


class PerfilEditableSerializer(serializers.ModelSerializer):
    """Lo que el usuario puede cambiar de su perfil. Correo, sexo y rol no se editan."""

    class Meta:
        model = Usuario
        fields = ["telefono", "carrera", "preferencia_compatibilidad"]


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
            "preferencia_compatibilidad",
            "rol",
        ]
        extra_kwargs = {
            "edad": {"required": True},
            "sexo": {"required": True},
            "carrera": {"required": True},
            "telefono": {"required": True},
            # La unicidad se revisa en validate_correo (sin distinguir mayúsculas).
            "correo": {"validators": []},
        }

    def validate_correo(self, value):
        # Una cuenta sin verificar no aparta el correo.
        if Usuario.objects.filter(correo__iexact=value, correo_verificado=True).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value.lower()

    def validate_rol(self, value):
        if value == Rol.ADMIN:
            raise serializers.ValidationError("El rol ADMIN no se otorga en el registro público.")
        return value


class RegistroResponseSerializer(serializers.Serializer):
    correo = serializers.EmailField()
    rol = serializers.IntegerField()
    rol_display = serializers.CharField()
    requiere_vehiculo = serializers.BooleanField()
    requiere_verificacion = serializers.BooleanField()
    token = serializers.CharField()


class VerificarCorreoSerializer(serializers.Serializer):
    token = serializers.CharField()
    codigo = serializers.RegexField(r"^\d{6}$", error_messages={"invalid": "El código tiene 6 dígitos."})


class ReenviarCodigoSerializer(serializers.Serializer):
    token = serializers.CharField()


class CorreoNoVerificado(APIException):
    status_code = 403
    default_code = "correo_no_verificado"

    def __init__(self):
        super().__init__(
            {
                "detail": "No completaste la verificación de esta cuenta. Regístrate de nuevo con este correo.",
                "codigo": "correo_no_verificado",
            }
        )


class LoginSerializer(TokenObtainPairSerializer):
    """Login normal de SimpleJWT, pero sin tokens si el correo no está verificado."""

    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.correo_verificado:
            raise CorreoNoVerificado()
        return data


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


class VehiculoEditableSerializer(serializers.Serializer):
    marca = serializers.CharField(max_length=60, required=False)
    modelo = serializers.CharField(max_length=60, required=False)
    color = serializers.CharField(max_length=40, required=False)
    asientos_disponibles = serializers.IntegerField(min_value=ASIENTOS_MIN, max_value=ASIENTOS_MAX, required=False)


class VehiculoRegistroResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    placas = serializers.CharField()
    vehiculo_valido = serializers.BooleanField()
    rol = serializers.IntegerField()
    rol_display = serializers.CharField()
