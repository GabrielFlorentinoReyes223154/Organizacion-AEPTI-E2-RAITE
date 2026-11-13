"""Foto de perfil opcional (solo agrega la columna; no toca datos)."""

import apps.accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0015_usuario_carrera_catalogo"),
    ]

    operations = [
        migrations.AddField(
            model_name="usuario",
            name="foto",
            field=models.ImageField(
                blank=True,
                help_text="Opcional. Se guarda como WebP de 512 px como máximo; solo la ven usuarios con sesión.",
                max_length=150,
                upload_to=apps.accounts.models.ruta_foto,
                verbose_name="foto de perfil",
            ),
        ),
    ]
