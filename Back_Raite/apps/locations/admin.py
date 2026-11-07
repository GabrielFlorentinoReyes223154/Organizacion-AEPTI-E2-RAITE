from django.contrib import admin

from .models import Campus, PuntoReferencia


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "latitud", "longitud", "activo")
    list_editable = ("activo",)
    list_filter = ("activo",)
    search_fields = ("codigo", "nombre")


@admin.register(PuntoReferencia)
class PuntoReferenciaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "latitud", "longitud", "activo", "osm_id", "updated_at")
    list_editable = ("activo",)
    list_filter = ("activo",)
    search_fields = ("nombre", "osm_id")
    readonly_fields = ("created_at", "updated_at")
    actions = ["activar", "desactivar"]

    @admin.action(description="Activar los puntos seleccionados")
    def activar(self, request, queryset):
        self.message_user(request, f"{queryset.update(activo=True)} punto(s) activados.")

    @admin.action(description="Desactivar los puntos seleccionados")
    def desactivar(self, request, queryset):
        self.message_user(request, f"{queryset.update(activo=False)} punto(s) desactivados.")
