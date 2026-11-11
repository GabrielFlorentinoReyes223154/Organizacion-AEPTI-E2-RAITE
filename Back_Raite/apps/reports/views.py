from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import Reporte
from .serializers import ReporteEntradaSerializer, ReporteSerializer


class ReportarView(APIView):
    """POST reportes/: reportar a otro integrante de un viaje en el que participó."""

    def post(self, request):
        entrada = ReporteEntradaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        reporte = services.reportar(request.user, **entrada.validated_data)
        return Response(ReporteSerializer(reporte).data, status=status.HTTP_201_CREATED)


class MisReportesView(generics.ListAPIView):
    serializer_class = ReporteSerializer

    def get_queryset(self):
        return Reporte.objects.filter(reportante=self.request.user).select_related("reportado__carrera__campus")
