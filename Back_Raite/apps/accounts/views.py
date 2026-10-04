from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Usuario, Vehiculo
from .serializers import (
    RegistroResponseSerializer,
    RegistroSerializer,
    UsuarioSerializer,
    VehiculoRegistroResponseSerializer,
    VehiculoRegistroSerializer,
)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UsuarioSerializer(request.user).data)


class RegistroView(APIView):
    """Paso 1: Crea usuario y roles. Si tiene CONDUCTOR, devuelve requiere_vehiculo=True."""

    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        requiere_vehiculo = user.es_conductor
        response_serializer = RegistroResponseSerializer(
            {
                "id": user.id,
                "roles": [r.rol.lower() for r in user.usuario_roles.all()],
                "suspendido": user.suspendido,
                "requiere_vehiculo": requiere_vehiculo,
            }
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class VehiculoRegistroView(APIView):
    """Paso 2 (condicional): Crea vehículo para usuarios con rol CONDUCTOR."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if not user.es_conductor:
            return Response(
                {"detail": "Solo usuarios con rol de conductor pueden registrar vehículo."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = VehiculoRegistroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        vehiculo = Vehiculo.objects.create(
            usuario=user,
            marca=serializer.validated_data["marca"],
            modelo=serializer.validated_data["modelo"],
            color=serializer.validated_data["color"],
            placas=serializer.validated_data["placas"],
            tipo=serializer.validated_data["tipo"],
            asientos_disponibles=serializer.validated_data["asientos_disponibles"],
        )

        response_serializer = VehiculoRegistroResponseSerializer(
            {
                "id": vehiculo.id,
                "placas": vehiculo.placas,
                "vehiculo_valido": True,
            }
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)