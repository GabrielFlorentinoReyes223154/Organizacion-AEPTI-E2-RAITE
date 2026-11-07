from rest_framework import generics
from rest_framework.response import Response

from .geo import haversine_km
from .models import Campus, PuntoReferencia
from .serializers import CampusSerializer, CoordenadasSerializer, PuntoReferenciaSerializer


class CampusListView(generics.ListAPIView):
    """Campus activos (sin paginar: son 5)."""

    serializer_class = CampusSerializer
    pagination_class = None
    queryset = Campus.objects.filter(activo=True).order_by("codigo")


class PuntoReferenciaListView(generics.GenericAPIView):
    """Puntos de referencia activos (sin paginar, para el mapa).

    `?q=` filtra por nombre; `?lat=&lon=` ordena por cercanía y agrega `distancia_km`.
    """

    serializer_class = PuntoReferenciaSerializer

    def get(self, request):
        coordenadas = CoordenadasSerializer(data=request.query_params)
        coordenadas.is_valid(raise_exception=True)
        puntos = PuntoReferencia.objects.filter(activo=True).order_by("nombre")
        if q := request.query_params.get("q", "").strip():
            puntos = puntos.filter(nombre__icontains=q)
        puntos = list(puntos)

        if "lat" in coordenadas.validated_data:
            lat, lon = coordenadas.validated_data["lat"], coordenadas.validated_data["lon"]
            for punto in puntos:
                punto.distancia_km = haversine_km(lat, lon, punto.latitud, punto.longitud)
            puntos.sort(key=lambda p: p.distancia_km)

        return Response(self.get_serializer(puntos, many=True).data)
