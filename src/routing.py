import requests
from typing import Tuple, Dict

OSRM_ROUTE_URL = "http://router.project-osrm.org/route/v1/driving"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def geocode_address(address: str) -> Tuple[float, float]:
    """Géocodage via Nominatim (OpenStreetMap)"""
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }

    response = requests.get(
        NOMINATIM_URL,
        params=params,
        headers={"User-Agent": "rutafem-routing"}
    )
    response.raise_for_status()
    data = response.json()

    if not data:
        raise ValueError(f"Adresse introuvable : {address}")

    return float(data[0]["lat"]), float(data[0]["lon"])


def get_route_osrm(
    origin: Tuple[float, float],
    destination: Tuple[float, float]
) -> Dict:
    lat1, lon1 = origin
    lat2, lon2 = destination

    url = f"{OSRM_ROUTE_URL}/{lon1},{lat1};{lon2},{lat2}"
    params = {
        "steps": "true",
        "overview": "false"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
