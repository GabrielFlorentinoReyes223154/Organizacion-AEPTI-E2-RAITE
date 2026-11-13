"""Señales de cuentas."""

from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Usuario


@receiver(post_delete, sender=Usuario)
def borrar_foto_de_usuario_eliminado(sender, instance, **kwargs):
    """Al eliminar una cuenta (por ejemplo, desde el admin) se borra también su foto."""
    from .services import borrar_foto_al_confirmar

    borrar_foto_al_confirmar(instance, instance.foto.name)
