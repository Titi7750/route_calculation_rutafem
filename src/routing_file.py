""" Module for routing operations using OSRM """

import requests
from typing import Tuple, Dict

# -----

OSRM_ROUTE_URL = "http://router.project-osrm.org/route/v1/driving"

# -----

def get_route_osrm_method(
    param_origin: Tuple[float, float],
    param_destination: Tuple[float, float],
    param_alternatives: bool = False,
    param_steps: bool = True,
    param_overview: bool | str = "false"
) -> Dict:
    """ Get route data from OSRM API """

    lat1, lon1 = param_origin
    lat2, lon2 = param_destination

    url = f"{OSRM_ROUTE_URL}/{lon1},{lat1};{lon2},{lat2}"
    params = {
        "steps": "true" if param_steps else "false",
        "overview": "false",
        "alternatives": "true" if param_alternatives else "false",
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()
