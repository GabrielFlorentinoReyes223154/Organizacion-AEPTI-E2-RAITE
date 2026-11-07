from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notificacion
from .serializers import NotificacionSerializer


class NotificacionesView(generics.ListAPIView):
    """Notificaciones propias, de la más nueva a la más vieja. `?no_leidas=1` filtra."""

    serializer_class = NotificacionSerializer

    def get_queryset(self):
        notificaciones = Notificacion.objects.filter(usuario=self.request.user)
        if self.request.query_params.get("no_leidas") in ("1", "true"):
            notificaciones = notificaciones.filter(leida=False)
        return notificaciones


class ConteoView(APIView):
    """Lo que el frontend consulta periódicamente."""

    def get(self, request):
        return Response({"no_leidas": Notificacion.objects.filter(usuario=request.user, leida=False).count()})


class LeerView(APIView):
    def post(self, request, pk):
        notificacion = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
        if not notificacion.leida:
            notificacion.leida = True
            notificacion.save(update_fields=["leida"])
        return Response(NotificacionSerializer(notificacion).data)


class LeerTodasView(APIView):
    def post(self, request):
        marcadas = Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
        return Response({"marcadas": marcadas})
