"""Borra las cuentas de alumnos que existían antes del catálogo de carreras.

`Usuario.carrera` deja de ser texto libre y pasa a apuntar al catálogo oficial de la UACJ (0015).
Decisión del equipo: en lugar de empatar el texto anterior con el catálogo, se borran las cuentas
de alumnos y todo lo que depende de ellas (viajes, solicitudes, calificaciones, reportes, avisos,
vehículos y códigos). Cada alumno vuelve a registrarse eligiendo su campus y su carrera.

Las cuentas de administrador se conservan: no tienen carrera y siguen entrando al admin.

El cambio de esquema va en 0015 porque PostgreSQL no permite alterar una tabla en la misma
transacción en que se borraron filas que la referencian ("pending trigger events").
"""

from django.db import migrations
from django.db.models import Q

ADMIN = 1


def borrar_alumnos(apps, schema_editor):
    Usuario = apps.get_model("accounts", "Usuario")
    Viaje = apps.get_model("rides", "Viaje")
    Solicitud = apps.get_model("rides", "Solicitud")
    Calificacion = apps.get_model("ratings", "Calificacion")
    Reporte = apps.get_model("reports", "Reporte")
    Notificacion = apps.get_model("notifications", "Notificacion")

    alumnos = Usuario.objects.exclude(rol=ADMIN)
    viajes = Viaje.objects.filter(conductor__in=alumnos)

    # Primero lo que protege (PROTECT) a los viajes y a los usuarios.
    Reporte.objects.filter(Q(viaje__in=viajes) | Q(reportante__in=alumnos) | Q(reportado__in=alumnos)).delete()
    Calificacion.objects.filter(Q(viaje__in=viajes) | Q(autor__in=alumnos) | Q(calificado__in=alumnos)).delete()
    Notificacion.objects.filter(Q(viaje__in=viajes) | Q(usuario__in=alumnos)).delete()
    Solicitud.objects.filter(Q(viaje__in=viajes) | Q(pasajero__in=alumnos)).delete()
    viajes.delete()
    # Vehículos, códigos y sesiones se van en cascada (o quedan sin usuario).
    alumnos.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0013_usuario_contacto_verificacion_y_limites"),
        ("rides", "0001_initial"),
        ("ratings", "0001_initial"),
        ("reports", "0001_initial"),
        ("notifications", "0001_initial"),
        ("token_blacklist", "0013_alter_blacklistedtoken_options_and_more"),
        ("admin", "0003_logentry_add_action_flag_choices"),
    ]

    operations = [
        migrations.RunPython(borrar_alumnos, migrations.RunPython.noop),
    ]
