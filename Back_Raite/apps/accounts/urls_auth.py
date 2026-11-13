from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

from .views import FotoView, LoginView, MeView, ReenviarCodigoView, RegistroView, VehiculoView, VerificarCorreoView

urlpatterns = [
    path("token/", LoginView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("me/", MeView.as_view(), name="me"),
    path("me/foto/", FotoView.as_view(), name="me_foto"),
    path("register/", RegistroView.as_view(), name="register"),
    path("verificar/", VerificarCorreoView.as_view(), name="verificar_correo"),
    path("reenviar-codigo/", ReenviarCodigoView.as_view(), name="reenviar_codigo"),
    path("vehicle/", VehiculoView.as_view(), name="vehicle_register"),
]
