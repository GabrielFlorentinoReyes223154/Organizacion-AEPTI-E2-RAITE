from django.urls import path

from .views import CampusListView, CarreraListView, PuntoReferenciaListView

urlpatterns = [
    path("campus/", CampusListView.as_view(), name="campus_lista"),
    path("carreras/", CarreraListView.as_view(), name="carreras_lista"),
    path("puntos/", PuntoReferenciaListView.as_view(), name="puntos_lista"),
]
