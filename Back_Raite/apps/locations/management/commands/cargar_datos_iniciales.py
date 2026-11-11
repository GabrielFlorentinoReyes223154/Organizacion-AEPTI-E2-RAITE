import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.locations.models import Campus, Carrera, PuntoReferencia

DATOS = Path(__file__).resolve().parents[2] / "data"


class Command(BaseCommand):
    help = (
        "Carga los campus, sus carreras y los puntos de referencia desde apps/locations/data/. "
        "No usa internet y se puede correr varias veces sin duplicar."
    )

    def add_arguments(self, parser):
        parser.add_argument("--campus", default=str(DATOS / "campus.json"))
        parser.add_argument("--puntos", default=str(DATOS / "puntos_referencia.json"))
        parser.add_argument("--carreras", default=str(DATOS / "carreras.json"))
        parser.add_argument(
            "--actualizar-estados",
            action="store_true",
            help=(
                "También copia `activo` del JSON a los puntos y carreras que ya existen "
                "(sobrescribe lo que se haya activado o desactivado en el admin)."
            ),
        )

    @transaction.atomic
    def handle(self, *args, **opciones):
        campus = self._leer(opciones["campus"])
        puntos = self._leer(opciones["puntos"])
        carreras = self._leer(opciones["carreras"])

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

        k_creadas, k_actualizadas = self._cargar_carreras(carreras, actualizar_estados)

        self.stdout.write(
            self.style.SUCCESS(
                f"Campus: {c_creados} creados, {c_actualizados} actualizados. "
                f"Puntos de referencia: {p_creados} creados, {p_actualizados} actualizados. "
                f"Carreras: {k_creadas} creadas, {k_actualizadas} actualizadas."
            )
        )

    def _cargar_carreras(self, carreras, actualizar_estados):
        """Catálogo oficial de la UACJ por campus. Se identifican por (código de campus, nombre).

        Como con los puntos, `activo` solo se fija al crear, salvo con --actualizar-estados.
        """
        campus = {c.codigo: c for c in Campus.objects.all()}
        creadas = actualizadas = 0
        for dato in carreras:
            if dato["campus"] not in campus:
                raise CommandError(f"La carrera «{dato['nombre']}» es de un campus que no existe: {dato['campus']}.")
            obj = Carrera(campus=campus[dato["campus"]], nombre=dato["nombre"], area=dato.get("area", ""))
            obj.full_clean(validate_unique=False, validate_constraints=False)
            carrera, creada = Carrera.objects.get_or_create(
                campus=obj.campus,
                nombre=obj.nombre,
                defaults={"area": obj.area, "activo": dato.get("activo", True)},
            )
            if creada:
                creadas += 1
                continue
            carrera.area = obj.area
            campos = ["area"]
            if actualizar_estados:
                carrera.activo = dato.get("activo", True)
                campos.append("activo")
            carrera.save(update_fields=campos)
            actualizadas += 1
        return creadas, actualizadas

    def _leer(self, ruta):
        return json.loads(Path(ruta).read_text(encoding="utf-8"))
