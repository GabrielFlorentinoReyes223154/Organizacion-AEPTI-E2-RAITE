"""`Usuario.carrera` pasa de texto libre a una FK al catálogo de carreras (0014 ya borró a los alumnos)."""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0014_borrar_alumnos"),
        ("locations", "0002_carrera"),
    ]

    operations = [
        migrations.RemoveField(model_name="usuario", name="carrera"),
        migrations.AddField(
            model_name="usuario",
            name="carrera",
            field=models.ForeignKey(
                blank=True,
                help_text="Del catálogo de la UACJ; el campus del alumno sale de aquí. Vacía solo en administradores.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="alumnos",
                to="locations.carrera",
            ),
        ),
    ]
