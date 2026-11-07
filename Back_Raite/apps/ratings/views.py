from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .serializers import CalificacionEntradaSerializer, CalificacionSerializer, PendienteSerializer


class CalificarView(APIView):
    """POST viajes/{id}/calificaciones/: califica al conductor o a un pasajero confirmado."""

    def post(self, request, pk):
        entrada = CalificacionEntradaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        calificacion = services.calificar(pk, request.user, entrada.validated_data)
        return Response(CalificacionSerializer(calificacion).data, status=status.HTTP_201_CREATED)


class PendientesView(APIView):
    """A quién le falta calificar en sus viajes finalizados (sin paginar)."""

    def get(self, request):
        return Response(PendienteSerializer(services.pendientes(request.user), many=True).data)
