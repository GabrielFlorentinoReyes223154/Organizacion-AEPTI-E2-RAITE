"""Distancias en línea recta (haversine). Sin PostGIS: el catálogo es pequeño."""

from math import asin, cos, radians, sin, sqrt

RADIO_TIERRA_KM = 6371.0088
KM_POR_GRADO_LATITUD = 111.32


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    lat1, lon1, lat2, lon2 = map(lambda v: radians(float(v)), (lat1, lon1, lat2, lon2))
    a = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
    return 2 * RADIO_TIERRA_KM * asin(sqrt(a))


def recuadro(lat, lon, radio_km) -> dict:
    """Rectángulo que contiene el círculo de `radio_km`, para descartar en SQL lo que está lejos."""
    dlat = radio_km / KM_POR_GRADO_LATITUD
    dlon = radio_km / (KM_POR_GRADO_LATITUD * max(cos(radians(float(lat))), 0.01))
    lat, lon = float(lat), float(lon)
    return {
        "latitud__gte": lat - dlat,
        "latitud__lte": lat + dlat,
        "longitud__gte": lon - dlon,
        "longitud__lte": lon + dlon,
    }


def filtro_recuadro(lat, lon, radio_km, prefijo="") -> dict:
    """Lookups de Django del rectángulo; `prefijo` es la relación, ej. "punto_referencia__"."""
    return {f"{prefijo}{campo}": valor for campo, valor in recuadro(lat, lon, radio_km).items()}
