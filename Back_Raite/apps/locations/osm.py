"""Convierte el export de Overpass (OpenStreetMap) en puntos de referencia con nombre.

Lo usa el comando `generar_puntos_osm`. Las funciones no usan internet, salvo `geocodificar_inverso`.
"""

import json
import urllib.parse
import urllib.request
from collections import Counter
from decimal import ROUND_HALF_UP, Decimal

from .models import esta_en_juarez

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
USER_AGENT = "raite-uacj-proyecto-escolar/1.0"

# Claves de Nominatim que se usan como "colonia", en orden de preferencia.
CLAVES_COLONIA = ("neighbourhood", "suburb", "quarter", "residential", "city_district")
PALABRAS_EXCLUIDAS = ("distribución", "distribucion", "cedis")

SIN_DATO = "(sin calle)"


def _seis_decimales(valor) -> str:
    return str(Decimal(str(valor)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))


def marca_de(tags: dict) -> str | None:
    """'Oxxo', 'Oxxo Gas' o None si el elemento no es una tienda/gasolinera."""
    nombre = (tags.get("name") or "").lower()
    if any(p in nombre for p in PALABRAS_EXCLUIDAS):
        return None
    if tags.get("amenity") == "fuel" or "gas" in nombre or "gas" in (tags.get("brand") or "").lower():
        return "Oxxo Gas"
    return "Oxxo"


def extraer_puntos(datos_overpass: dict) -> tuple[list[dict], Counter]:
    """Devuelve (puntos, descartados). Cada punto: osm_id, marca, latitud, longitud."""
    puntos, descartados = [], Counter()
    for elemento in datos_overpass.get("elements", []):
        coords = elemento if "lat" in elemento else elemento.get("center")
        if not coords:
            descartados["sin coordenadas"] += 1
            continue
        marca = marca_de(elemento.get("tags", {}))
        if marca is None:
            descartados["no es tienda (centro de distribución)"] += 1
            continue
        if not esta_en_juarez(coords["lat"], coords["lon"]):
            descartados["fuera de Ciudad Juárez"] += 1
            continue
        puntos.append(
            {
                "osm_id": f"{elemento['type']}/{elemento['id']}",
                "marca": marca,
                "latitud": _seis_decimales(coords["lat"]),
                "longitud": _seis_decimales(coords["lon"]),
            }
        )
    puntos.sort(key=lambda p: p["osm_id"])
    return puntos, descartados


def calle_y_colonia(respuesta_nominatim: dict | None) -> tuple[str, str]:
    direccion = (respuesta_nominatim or {}).get("address", {})
    calle = direccion.get("road", "")
    colonia = next((direccion[c] for c in CLAVES_COLONIA if direccion.get(c)), "")
    return calle.strip(), colonia.strip()


def componer_nombre(marca: str, calle: str, colonia: str) -> str:
    partes = [p for p in (calle, colonia and f"Col. {colonia}") if p]
    return f"{marca} – {', '.join(partes) if partes else SIN_DATO}"


def desambiguar(puntos: list[dict]) -> None:
    """Agrega (2), (3)… a los nombres repetidos, en orden de osm_id."""
    vistos = Counter()
    totales = Counter(p["nombre"] for p in puntos)
    for punto in puntos:
        nombre = punto["nombre"]
        if totales[nombre] > 1:
            vistos[nombre] += 1
            if vistos[nombre] > 1:
                punto["nombre"] = f"{nombre} ({vistos[nombre]})"


def nombrar_puntos(puntos: list[dict], geocodificar) -> list[dict]:
    """Agrega nombre, calle, colonia y activo a cada punto usando `geocodificar(lat, lon)`.

    Un punto sin calle o sin colonia queda con activo=False para revisarlo en el admin.
    """
    resultado = []
    for punto in puntos:
        try:
            respuesta = geocodificar(punto["latitud"], punto["longitud"])
        except Exception:  # noqa: BLE001 - un fallo de red no debe detener la generación
            respuesta = None
        calle, colonia = calle_y_colonia(respuesta)
        resultado.append(
            {
                "osm_id": punto["osm_id"],
                "nombre": componer_nombre(punto["marca"], calle, colonia),
                "calle": calle,
                "colonia": colonia,
                "latitud": punto["latitud"],
                "longitud": punto["longitud"],
                "activo": bool(calle and colonia),
            }
        )
    desambiguar(resultado)
    return resultado


def geocodificar_inverso(latitud, longitud, timeout=20) -> dict:
    """Consulta Nominatim (máximo 1 petición por segundo según su política de uso)."""
    parametros = urllib.parse.urlencode(
        {
            "lat": latitud,
            "lon": longitud,
            "format": "jsonv2",
            "zoom": 18,
            "addressdetails": 1,
            "accept-language": "es",
        }
    )
    peticion = urllib.request.Request(
        f"{NOMINATIM_URL}?{parametros}", headers={"User-Agent": USER_AGENT}
    )
    with urllib.request.urlopen(peticion, timeout=timeout) as respuesta:
        return json.load(respuesta)
