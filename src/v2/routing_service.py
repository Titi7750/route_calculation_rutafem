from typing import Dict, Any, List, Tuple
from src.routing_file import get_route_osrm

class RoutingServiceV2:

    def get_routes(
        self,
        start_coords: Tuple[float, float],
        end_coords: Tuple[float, float],
        max_alternatives: int = 2,
    ) -> List[Dict[str, Any]]:

        osrm_data = get_route_osrm(
            origin=start_coords,
            destination=end_coords,
            alternatives=True,
            steps=True,
            overview=False,
        )

        routes = osrm_data.get("routes", [])
        if not routes:
            return []

        # route principale + alternatives limitées
        return routes[: max_alternatives + 1]
