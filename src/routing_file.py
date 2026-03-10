""" Module for routing operations using OSRM and geocoding with Nominatim"""

import requests
from typing import Tuple, Dict
from src.geocoders_file import Geocoders

# -----

OSRM_ROUTE_URL = "http://router.project-osrm.org/route/v1/driving"

# -----

def geocode_address(address: str) -> Tuple[float, float]:
    """ Geocoding wrapper kept for backward compatibility """

    geocoder = Geocoders(user_agent="rutafem-routing")
    coordinates = geocoder.geocode_coordinates_method(address)

    if not coordinates:
        raise ValueError(f"Adresse introuvable : {address}")

    return coordinates

# -----

def get_route_osrm(
    origin: Tuple[float, float],
    destination: Tuple[float, float],
    alternatives: bool = False,
    steps: bool = True,
    overview: bool | str = "false",
) -> Dict:
    """ Get route data from OSRM API """

    lat1, lon1 = origin
    lat2, lon2 = destination

    url = f"{OSRM_ROUTE_URL}/{lon1},{lat1};{lon2},{lat2}"
    params = {
        "steps": "true" if steps else "false",
        "overview": "false",
        "alternatives": "true" if alternatives else "false",
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()
