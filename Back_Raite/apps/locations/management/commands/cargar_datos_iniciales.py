import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.locations.models import Campus, PuntoReferencia

DATOS = Path(__file__).resolve().parents[2] / "data"


class Command(BaseCommand):
    help = (
        "Carga los campus y los puntos de referencia desde apps/locations/data/. "
        "No usa internet y se puede correr varias veces sin duplicar."
    )

    def add_arguments(self, parser):
        parser.add_argument("--campus", default=str(DATOS / "campus.json"))
        parser.add_argument("--puntos", default=str(DATOS / "puntos_referencia.json"))
        parser.add_argument(
            "--actualizar-estados",
            action="store_true",
            help=(
                "También copia `activo` del JSON a los puntos que ya existen "
                "(sobrescribe lo que se haya activado o desactivado en el admin)."
            ),
        )

    @transaction.atomic
    def handle(self, *args, **opciones):
        campus = self._leer(opciones["campus"])
        puntos = self._leer(opciones["puntos"])

        c_creados = c_actualizados = 0
        for dato in campus:
            obj = Campus(**{k: dato[k] for k in ("codigo", "nombre", "latitud", "longitud")})
            obj.full_clean(exclude=["codigo"], validate_unique=False)
            _, creado = Campus.objects.update_or_create(
                codigo=dato["codigo"],
                defaults={"nombre": dato["nombre"], "latitud": dato["latitud"], "longitud": dato["longitud"]},
            )
            c_creados += creado
            c_actualizados += not creado

        actualizar_estados = opciones["actualizar_estados"]
        p_creados = p_actualizados = 0
        for dato in puntos:
            obj = PuntoReferencia(
                nombre=dato["nombre"], latitud=dato["latitud"], longitud=dato["longitud"]
            )
            obj.full_clean(exclude=["osm_id"], validate_unique=False)
            # Por defecto `activo` solo se fija al crear, para no pisar lo editado en el admin.
            punto, creado = PuntoReferencia.objects.get_or_create(
                osm_id=dato["osm_id"],
                defaults={
                    "nombre": dato["nombre"],
                    "latitud": dato["latitud"],
                    "longitud": dato["longitud"],
                    "activo": dato.get("activo", True),
                },
            )
            if creado:
                p_creados += 1
            else:
                punto.latitud, punto.longitud = dato["latitud"], dato["longitud"]
                campos = ["latitud", "longitud", "updated_at"]
                if actualizar_estados:
                    punto.activo = dato.get("activo", True)
                    campos.append("activo")
                punto.save(update_fields=campos)
                p_actualizados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Campus: {c_creados} creados, {c_actualizados} actualizados. "
                f"Puntos de referencia: {p_creados} creados, {p_actualizados} actualizados."
            )
        )

    def _leer(self, ruta):
        return json.loads(Path(ruta).read_text(encoding="utf-8"))
