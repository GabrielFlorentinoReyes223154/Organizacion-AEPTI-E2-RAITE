import json
import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.locations import osm

ENTRADA = settings.BASE_DIR.parent / "RaiteDocs" / "BD_PuntosMapa" / "Oxxo.json"
SALIDA = Path(__file__).resolve().parents[2] / "data" / "puntos_referencia.json"


class Command(BaseCommand):
    help = (
        "Genera apps/locations/data/puntos_referencia.json a partir del export de Overpass, "
        "nombrando cada punto con su calle y colonia (Nominatim). Requiere internet; "
        "se corre una sola vez y el resultado se versiona."
    )

    def add_arguments(self, parser):
        parser.add_argument("--entrada", default=str(ENTRADA), help="JSON exportado de Overpass Turbo")
        parser.add_argument("--salida", default=str(SALIDA))
        parser.add_argument(
            "--pausa", type=float, default=1.1, help="Segundos entre peticiones a Nominatim (mínimo 1)"
        )

    def handle(self, *args, **opciones):
        entrada = Path(opciones["entrada"])
        if not entrada.exists():
            raise CommandError(f"No existe {entrada}")
        puntos, descartados = osm.extraer_puntos(json.loads(entrada.read_text(encoding="utf-8")))
        for motivo, cantidad in descartados.items():
            self.stdout.write(f"Descartados ({motivo}): {cantidad}")
        self.stdout.write(f"Consultando Nominatim para {len(puntos)} puntos…")

        pausa = opciones["pausa"]
        total = len(puntos)

        def geocodificar(lat, lon, _estado={"n": 0}):
            _estado["n"] += 1
            if _estado["n"] > 1:
                time.sleep(pausa)
            if _estado["n"] % 20 == 0:
                self.stdout.write(f"  {_estado['n']}/{total}")
            return osm.geocodificar_inverso(lat, lon)

        resultado = osm.nombrar_puntos(puntos, geocodificar)

        salida = Path(opciones["salida"])
        salida.parent.mkdir(parents=True, exist_ok=True)
        salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        inactivos = sum(1 for p in resultado if not p["activo"])
        self.stdout.write(
            self.style.SUCCESS(
                f"Escritos {len(resultado)} puntos en {salida} ({inactivos} inactivos por falta de calle)."
            )
        )
