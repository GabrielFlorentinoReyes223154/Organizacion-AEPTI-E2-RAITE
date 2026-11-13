from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView


from . import services
from .permissions import CorreoVerificado
from .serializers import (
    FotoSerializer,
    LoginSerializer,
    PerfilEditableSerializer,
    ReenviarCodigoSerializer,
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


class FotoView(APIView):
    """PUT (multipart, campo `foto`): sube o cambia la foto de perfil. DELETE: la quita.
    Las dos devuelven el perfil propio con la URL nueva."""

    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):
        serializer = FotoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = services.cambiar_foto(request.user, serializer.validated_data["foto"])
        return Response(UsuarioSerializer(usuario).data)

    def delete(self, request):
        usuario = services.quitar_foto(request.user)
        return Response(UsuarioSerializer(usuario).data)


class RegistroView(APIView):
    """Paso 1: valida los datos y manda el código, sin guardar nada. Devuelve el token que se
    presenta en `verificar/`. Si tiene rol conductor, devuelve requiere_vehiculo=True (el
    vehículo se registra después de verificar)."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = services.registrar(serializer.validated_data)
        response_serializer = RegistroResponseSerializer(
            {
                "correo": user.correo,
                "rol": user.rol,
                "rol_display": user.get_rol_display(),
                "requiere_vehiculo": user.es_conductor,
                "requiere_verificacion": True,
                "token": token,
            }
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class VerificarCorreoView(APIView):
    """Crea la cuenta con el token del registro y el código, y devuelve los tokens de sesión."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerificarCorreoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = services.verificar_correo(**serializer.validated_data)
        return Response({**tokens_para(usuario), "usuario": UsuarioSerializer(usuario).data})


class ReenviarCodigoView(APIView):
    """Manda un código nuevo y devuelve el token que reemplaza al anterior."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ReenviarCodigoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = services.reenviar_codigo(serializer.validated_data["token"])
        return Response({"detail": "Te enviamos un código nuevo.", "token": token})


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
