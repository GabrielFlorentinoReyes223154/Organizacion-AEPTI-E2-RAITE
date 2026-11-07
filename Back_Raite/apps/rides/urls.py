from django.urls import path

from . import views

urlpatterns = [
    path("viajes/", views.ViajesView.as_view(), name="viajes"),
    path("viajes/mios/", views.MisViajesView.as_view(), name="viajes_mios"),
    path("viajes/<uuid:pk>/", views.ViajeDetalleView.as_view(), name="viaje_detalle"),
    path("viajes/<uuid:pk>/cancelar/", views.CancelarViajeView.as_view(), name="viaje_cancelar"),
    path("viajes/<uuid:pk>/iniciar/", views.IniciarViajeView.as_view(), name="viaje_iniciar"),
    path("viajes/<uuid:pk>/finalizar/", views.FinalizarViajeView.as_view(), name="viaje_finalizar"),
    path("viajes/<uuid:pk>/solicitudes/", views.SolicitudesDeViajeView.as_view(), name="viaje_solicitudes"),
    path("solicitudes/mias/", views.MisSolicitudesView.as_view(), name="solicitudes_mias"),
    path("solicitudes/<uuid:pk>/aceptar/", views.AceptarSolicitudView.as_view(), name="solicitud_aceptar"),
    path("solicitudes/<uuid:pk>/rechazar/", views.RechazarSolicitudView.as_view(), name="solicitud_rechazar"),
    path("solicitudes/<uuid:pk>/cancelar/", views.CancelarSolicitudView.as_view(), name="solicitud_cancelar"),
]
