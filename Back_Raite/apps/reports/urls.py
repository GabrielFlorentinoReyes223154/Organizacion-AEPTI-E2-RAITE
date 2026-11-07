from django.urls import path

from . import views

urlpatterns = [
    path("reportes/", views.ReportarView.as_view(), name="reportar"),
    path("reportes/mios/", views.MisReportesView.as_view(), name="reportes_mios"),
]
