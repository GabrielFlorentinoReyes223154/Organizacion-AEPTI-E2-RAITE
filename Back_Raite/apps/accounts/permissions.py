from rest_framework import permissions


def _autenticado(request) -> bool:
    return bool(request.user and request.user.is_authenticated)


class CorreoVerificado(permissions.BasePermission):
    message = "Verifica tu correo institucional para continuar."

    def has_permission(self, request, view):
        return _autenticado(request) and request.user.correo_verificado


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return _autenticado(request) and request.user.es_admin


class IsPassenger(permissions.BasePermission):
    message = "Necesitas el rol de pasajero."

    def has_permission(self, request, view):
        return _autenticado(request) and request.user.es_pasajero


class IsDriver(permissions.BasePermission):
    message = "Necesitas el rol de conductor."

    def has_permission(self, request, view):
        return _autenticado(request) and request.user.es_conductor


class PuedePublicar(permissions.BasePermission):
    """Conductor verificado, no suspendido y con vehículo activo."""

    message = "Para publicar necesitas rol de conductor, un vehículo activo y no estar suspendido."

    def has_permission(self, request, view):
        return _autenticado(request) and request.user.puede_publicar_viaje()


class PuedeSolicitar(permissions.BasePermission):
    """Pasajero verificado y no suspendido."""

    message = "Para pedir lugar necesitas rol de pasajero y no estar suspendido."

    def has_permission(self, request, view):
        return _autenticado(request) and request.user.puede_solicitar_lugar()
