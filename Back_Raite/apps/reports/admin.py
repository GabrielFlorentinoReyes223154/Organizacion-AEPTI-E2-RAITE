from django.contrib import admin
from django.utils import timezone

from .models import Reporte
from .models_choices import EstadoReporte


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ("created_at", "reportante", "reportado", "viaje", "estado", "reportado_suspendido")
    list_filter = ("estado",)
    search_fields = ("reportante__correo", "reportado__correo", "motivo")
    autocomplete_fields = ("viaje", "reportante", "reportado")
    readonly_fields = ("created_at", "resuelto_en", "resuelto_por")
    actions = ["marcar_resuelto", "descartar", "suspender_reportado"]

    @admin.display(boolean=True, description="Reportado suspendido")
    def reportado_suspendido(self, obj):
        return obj.reportado.suspendido

    def _cerrar(self, request, queryset, estado):
        return queryset.filter(estado=EstadoReporte.PENDIENTE).update(
            estado=estado, resuelto_por=request.user, resuelto_en=timezone.now()
        )

    @admin.action(description="Marcar como resueltos")
    def marcar_resuelto(self, request, queryset):
        self.message_user(request, f"{self._cerrar(request, queryset, EstadoReporte.RESUELTO)} reporte(s) resueltos.")

    @admin.action(description="Descartar")
    def descartar(self, request, queryset):
        self.message_user(request, f"{self._cerrar(request, queryset, EstadoReporte.DESCARTADO)} reporte(s) descartados.")

    @admin.action(description="Suspender a los usuarios reportados (y resolver el reporte)")
    def suspender_reportado(self, request, queryset):
        from django.contrib.auth import get_user_model

        ids = set(queryset.values_list("reportado_id", flat=True))
        suspendidos = get_user_model().objects.filter(pk__in=ids, suspendido=False).update(suspendido=True)
        self._cerrar(request, queryset, EstadoReporte.RESUELTO)
        self.message_user(request, f"{suspendidos} usuario(s) suspendidos.")
