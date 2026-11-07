from django.urls import path

from . import views

urlpatterns = [
    path("viajes/", views.ViajesView.as_view(), name="viajes"),
    path("viajes/mios/", views.MisViajesView.as_view(), name="viajes_mios"),
    path("viajes/<uuid:pk>/", views.ViajeDetalleView.as_view(), name="viaje_detalle"),
    path("viajes/<uuid:pk>/cancelar/", views.CancelarViajeView.as_view(), name="viaje_cancelar"),
    path("viajes/<uuid:pk>/iniciar/", views.IniciarViajeView.as_view(), name="viaje_iniciar"),
    path("viajes/<uuid:pk>/finalizar/", views.FinalizarViajeView.as_view(), name="viaje_finalizar"),
]
