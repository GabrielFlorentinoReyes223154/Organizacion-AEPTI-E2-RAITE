from django.contrib import admin

from .models import Solicitud, Viaje


class SolicitudInline(admin.TabularInline):
    model = Solicitud
    extra = 0
    fields = ("pasajero", "estado", "preferencia_compatibilidad", "created_at", "respondida_en")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("pasajero",)


@admin.register(Viaje)
class ViajeAdmin(admin.ModelAdmin):
    list_display = (
        "fecha_hora",
        "punto_referencia",
        "sentido",
        "campus",
        "conductor",
        "lugares_ofrecidos",
        "lugares_disponibles",
        "preferencia_compatibilidad",
        "estado",
    )
    list_filter = ("estado", "campus", "sentido", "preferencia_compatibilidad")
    search_fields = ("conductor__correo", "conductor__nombre", "punto_referencia__nombre")
    date_hierarchy = "fecha_hora"
    autocomplete_fields = ("conductor", "vehiculo", "punto_referencia")
    readonly_fields = ("created_at", "updated_at")
    inlines = [SolicitudInline]

    @admin.display(description="Lugares libres")
    def lugares_disponibles(self, obj):
        return obj.lugares_disponibles


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ("viaje", "pasajero", "estado", "preferencia_compatibilidad", "created_at", "respondida_en")
    list_filter = ("estado",)
    search_fields = ("pasajero__correo", "pasajero__nombre")
    autocomplete_fields = ("viaje", "pasajero")
    readonly_fields = ("created_at",)
