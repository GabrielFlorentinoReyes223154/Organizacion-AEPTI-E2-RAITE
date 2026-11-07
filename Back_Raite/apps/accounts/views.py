from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView


from . import services
from .permissions import CorreoVerificado
from .serializers import (
    CorreoSerializer,
    LoginSerializer,
    PerfilEditableSerializer,
    RegistroResponseSerializer,
    RegistroSerializer,
    UsuarioSerializer,
    VehiculoEditableSerializer,
    VehiculoRegistroResponseSerializer,
    VehiculoRegistroSerializer,
    VehiculoSerializer,
    VerificarCorreoSerializer,
)


def tokens_para(usuario) -> dict:
    refresh = RefreshToken.for_user(usuario)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


class LoginView(TokenObtainPairView):
    """Login por correo y contraseña. 403 `correo_no_verificado` si falta verificar el correo."""

    serializer_class = LoginSerializer


class MeView(APIView):
    """GET: perfil propio. PATCH: teléfono, carrera y preferencia de compatibilidad (RF-07)."""

    def get(self, request):
        return Response(UsuarioSerializer(request.user).data)

    def patch(self, request):
        serializer = PerfilEditableSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        usuario = services.actualizar_perfil(request.user, serializer.validated_data)
        return Response(UsuarioSerializer(usuario).data)


class RegistroView(APIView):
    """Paso 1: crea el usuario sin verificar y le manda el código. Si tiene rol conductor,
    devuelve requiere_vehiculo=True (el vehículo se registra después de verificar)."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = services.registrar(serializer.validated_data)
        response_serializer = RegistroResponseSerializer(
            {
                "id": user.id,
                "correo": user.correo,
                "rol": user.rol,
                "rol_display": user.get_rol_display(),
                "suspendido": user.suspendido,
                "requiere_vehiculo": user.es_conductor,
                "requiere_verificacion": True,
            }
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class VerificarCorreoView(APIView):
    """Activa la cuenta con el código de 6 dígitos y devuelve los tokens de sesión."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerificarCorreoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = services.verificar_correo(**serializer.validated_data)
        return Response({**tokens_para(usuario), "usuario": UsuarioSerializer(usuario).data})


class ReenviarCodigoView(APIView):
    """Manda un código nuevo. Responde igual exista o no el correo."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CorreoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.reenviar_codigo(serializer.validated_data["correo"])
        return Response(
            {"detail": "Si el correo está registrado y sin verificar, te enviamos un código nuevo."}
        )


class VehiculoView(APIView):
    """POST: registra el vehículo (paso 2 del registro del conductor, o un pasajero que quiere
    ofrecer raites: su rol pasa a AMBOS). GET/PATCH: ver o editar el vehículo propio."""

    permission_classes = [IsAuthenticated, CorreoVerificado]

    def _vehiculo(self, request):
        vehiculo = getattr(request.user, "vehiculo", None)
        if vehiculo is None:
            raise NotFound("Aún no registras un vehículo.")
        return vehiculo

    def get(self, request):
        return Response(VehiculoSerializer(self._vehiculo(request)).data)

    def patch(self, request):
        vehiculo = self._vehiculo(request)
        serializer = VehiculoEditableSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        vehiculo = services.actualizar_vehiculo(vehiculo, serializer.validated_data)
        return Response(VehiculoSerializer(vehiculo).data)

    def post(self, request):
        serializer = VehiculoRegistroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vehiculo = services.registrar_vehiculo(request.user, serializer.validated_data)
        response_serializer = VehiculoRegistroResponseSerializer(
            {
                "id": vehiculo.id,
                "placas": vehiculo.placas,
                "vehiculo_valido": vehiculo.es_valido_para_conducir(),
                "rol": request.user.rol,
                "rol_display": request.user.get_rol_display(),
            }
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
