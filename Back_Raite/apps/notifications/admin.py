from django.contrib import admin

from .models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("created_at", "usuario", "tipo", "mensaje", "leida")
    list_filter = ("tipo", "leida")
    search_fields = ("usuario__correo", "mensaje")
    autocomplete_fields = ("usuario", "viaje")
    readonly_fields = ("created_at",)
