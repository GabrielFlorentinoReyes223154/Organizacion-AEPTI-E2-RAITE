from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import CorreoVerificado, IsDriver, PuedePublicar

from . import services
from .models import Viaje
from .models_choices import EstadoViaje
from .serializers import (
    BusquedaSerializer,
    ViajeDetalleSerializer,
    ViajeEdicionSerializer,
    ViajeEntradaSerializer,
    ViajeSerializer,
)

VIAJE_RELACIONES = ("conductor", "vehiculo", "punto_referencia", "campus")


def respuesta_viaje(request, viaje, codigo=status.HTTP_200_OK):
    viaje = Viaje.objects.select_related(*VIAJE_RELACIONES).get(pk=viaje.pk)
    es_conductor = viaje.conductor_id == request.user.pk
    visibles = {viaje.pk} if services.tiene_lugar_confirmado(viaje, request.user) else set()
    contexto = {"request": request, "es_conductor": es_conductor, "contacto_visible": visibles}
    return Response(ViajeDetalleSerializer(viaje, context=contexto).data, status=codigo)


class ViajesView(generics.GenericAPIView):
    """GET: buscar viajes (RF-04, RF-07). POST: publicar un viaje (RF-02, RF-03)."""

    serializer_class = ViajeSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), CorreoVerificado(), PuedePublicar()]
        return super().get_permissions()

    def get(self, request):
        filtros = BusquedaSerializer(data=request.query_params)
        filtros.is_valid(raise_exception=True)
        viajes = services.buscar_viajes(request.user, filtros.validated_data)
        pagina = self.paginate_queryset(viajes)
        return self.get_paginated_response(self.get_serializer(pagina, many=True).data)

    def post(self, request):
        entrada = ViajeEntradaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        viaje = services.publicar_viaje(request.user, entrada.validated_data)
        return respuesta_viaje(request, viaje, status.HTTP_201_CREATED)


class MisViajesView(generics.ListAPIView):
    """Viajes que publicó el conductor. Por defecto los publicados y en curso (incluye vencidos)."""

    serializer_class = ViajeSerializer
    permission_classes = [IsAuthenticated, CorreoVerificado, IsDriver]

    def get_queryset(self):
        estado = self.request.query_params.get("estado")
        if estado and estado not in EstadoViaje.values:
            raise ValidationError({"estado": f"Usa uno de: {', '.join(EstadoViaje.values)}."})
        return services.viajes_del_conductor(self.request.user, estado).select_related("conductor")

    def get_serializer_context(self):
        return {**super().get_serializer_context(), "es_conductor": True}


class ViajeDetalleView(APIView):
    """GET: detalle (contacto y placas solo con lugar confirmado). PATCH: editar (solo el conductor)."""

    def get(self, request, pk):
        viaje = get_object_or_404(Viaje, pk=pk)
        if not services.puede_ver_viaje(viaje, request.user):
            raise Http404
        return respuesta_viaje(request, viaje)

    def patch(self, request, pk):
        entrada = ViajeEdicionSerializer(data=request.data, partial=True)
        entrada.is_valid(raise_exception=True)
        viaje = services.editar_viaje(pk, request.user, entrada.validated_data)
        return respuesta_viaje(request, viaje)


class AccionViajeView(APIView):
    """POST viajes/{id}/cancelar|iniciar|finalizar/ (solo el conductor)."""

    accion = None  # función de services

    def post(self, request, pk):
        viaje = type(self).accion(pk, request.user)
        return respuesta_viaje(request, viaje)


class CancelarViajeView(AccionViajeView):
    accion = services.cancelar_viaje


class IniciarViajeView(AccionViajeView):
    accion = services.iniciar_viaje


class FinalizarViajeView(AccionViajeView):
    accion = services.finalizar_viaje
