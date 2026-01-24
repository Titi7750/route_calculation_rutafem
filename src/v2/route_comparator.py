from typing import List, Tuple
from src.v2.models import RouteOption
from src.v2.cost_calculator import CostCalculatorV2
from src.v2.toll_service import TollServiceV2
from src.v2.routing_service import RoutingServiceV2


class RouteComparatorV2:
    def __init__(self) -> None:
        self.cost_calculator = CostCalculatorV2()
        self.toll_service = TollServiceV2()
        self.routing_service = RoutingServiceV2()

    def get_alternative_routes(
        self,
        start_coords: Tuple[float, float],
        end_coords: Tuple[float, float],
        liter_per_100km: float,
        fuel_price_per_liter: float,
        persons: int,
        commission: bool,
        max_alternatives: int = 2,
    ) -> List[RouteOption]:

        osrm_data = self.routing_service.get_routes(
            start_coords, end_coords, max_alternatives
        )

        routes = osrm_data[: max_alternatives + 1]
        options: List[RouteOption] = []

        for idx, route in enumerate(routes, start=1):
            distance_km = round(route["distance"] / 1000, 2)
            duration_min = round(route["duration"] / 60, 1)

            toll_info = self.toll_service.analyze_route(route)
            toll_cost = float(toll_info["toll_cost"])

            cost = self.cost_calculator.compute_costs(
                distance_km=distance_km,
                duration_min=duration_min,
                liter_per_100km=liter_per_100km,
                fuel_price_per_liter=fuel_price_per_liter,
                toll_cost=toll_cost,
                persons=persons,
                commission=commission,
            )

            options.append(
                RouteOption(
                    index=idx,
                    distance_km=distance_km,
                    duration_min=duration_min,
                    fuel_cost=cost.fuel_cost,
                    toll_cost=toll_cost,
                    total_cost=cost.total_vehicle_cost,
                    cost_per_person=cost.cost_per_person,
                    tags=[],
                    raw_route=route,
                )
            )

        return self._tag_routes(options)

    def _tag_routes(self, routes: List[RouteOption]) -> List[RouteOption]:
        cheapest = min(routes, key=lambda r: r.total_cost)
        fastest = min(routes, key=lambda r: r.duration_min)

        for r in routes:
            if r is cheapest:
                r.tags.append("le moins cher")
            if r is fastest:
                r.tags.append("le plus rapide")
            if r.toll_cost == 0:
                r.tags.append("sans péage")

        return routes
