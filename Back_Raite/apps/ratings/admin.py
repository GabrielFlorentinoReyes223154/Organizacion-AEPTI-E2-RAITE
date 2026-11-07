from django.contrib import admin

from .models import Calificacion


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ("created_at", "viaje", "autor", "calificado", "puntuacion")
    list_filter = ("puntuacion",)
    search_fields = ("autor__correo", "calificado__correo", "comentario")
    autocomplete_fields = ("viaje", "autor", "calificado")
    readonly_fields = ("created_at",)
