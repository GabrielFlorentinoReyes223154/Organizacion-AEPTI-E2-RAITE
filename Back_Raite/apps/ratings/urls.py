from django.urls import path

from . import views

urlpatterns = [
    path("viajes/<uuid:pk>/calificaciones/", views.CalificarView.as_view(), name="viaje_calificar"),
    path("calificaciones/pendientes/", views.PendientesView.as_view(), name="calificaciones_pendientes"),
]
