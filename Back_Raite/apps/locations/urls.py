from django.urls import path

from .views import CampusListView, PuntoReferenciaListView

urlpatterns = [
    path("campus/", CampusListView.as_view(), name="campus_lista"),
    path("puntos/", PuntoReferenciaListView.as_view(), name="puntos_lista"),
]
