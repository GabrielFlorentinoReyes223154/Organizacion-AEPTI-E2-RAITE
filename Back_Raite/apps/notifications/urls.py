from django.urls import path

from . import views

urlpatterns = [
    path("notificaciones/", views.NotificacionesView.as_view(), name="notificaciones"),
    path("notificaciones/conteo/", views.ConteoView.as_view(), name="notificaciones_conteo"),
    path("notificaciones/leer-todas/", views.LeerTodasView.as_view(), name="notificaciones_leer_todas"),
    path("notificaciones/<uuid:pk>/leer/", views.LeerView.as_view(), name="notificacion_leer"),
]
