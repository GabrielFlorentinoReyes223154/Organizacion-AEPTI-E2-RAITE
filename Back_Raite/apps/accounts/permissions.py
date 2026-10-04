from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.es_admin)


class IsPassenger(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.es_pasajero


class IsDriver(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.es_conductor