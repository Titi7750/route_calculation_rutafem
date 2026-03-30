""" A module to calculate routes using geocoding and fuel data """

from typing import List, Tuple
from src.routing_file import get_route_osrm_method
from src.tolls_file import estimate_route_toll

# -----

class Route:
    """ Represents a calculated route with all cost details """

    def __init__(
        self,
        distance_km: float,
        fuel_cost: float,
        toll_cost: float,
        total_cost: float,
        cost_per_person: float,
        duration_min: float = 0.0,
        fuel_price: float = 0.0,
        has_toll: bool = False,
        toll_count: int = 0,
        closest_station: dict = None,
        index: int = 0,
        tags: List[str] = None,
    ):
        self.distance_km = distance_km
        self.fuel_cost = fuel_cost
        self.toll_cost = toll_cost
        self.total_cost = total_cost
        self.cost_per_person = cost_per_person
        self.duration_min = duration_min
        self.fuel_price = fuel_price
        self.has_toll = has_toll
        self.toll_count = toll_count
        self.closest_station = closest_station or {}
        self.index = index
        self.tags = tags or []

# -----

class RouteCalculator:
    """ A class to calculate routes based on map data. """

    COMMISSION_RATE = 0.15
    MIN_PRICE_PER_PERSON = 1.99

    # -----

    def calculate_route_method(
        self,
        param_distance: float,
        param_liter_km: float,
        param_fuel_price: float,
        param_toll: float,
        param_persons: int,
        param_commission: bool,
        param_has_toll: bool,
        param_toll_count: int,
        param_closest_station: dict,
    ) -> Route:
        """ Calculate and return a Route object with all cost details """

        if param_distance <= 0:
            raise ValueError("Distance must be positive")
        if param_liter_km <= 0:
            raise ValueError("Fuel consumption must be positive")
        if param_fuel_price <= 0:
            raise ValueError("Fuel price must be positive")
        if param_toll < 0:
            raise ValueError("Toll cannot be negative")
        if param_persons <= 0:
            raise ValueError("Number of persons must be positive")

        liters_used = (param_distance * param_liter_km) / 100
        fuel_cost = round(liters_used * param_fuel_price, 2)
        total_before_commission = fuel_cost + param_toll

        if param_commission:
            commission_amount = total_before_commission * self.COMMISSION_RATE
            total_cost = total_before_commission + commission_amount
        else:
            total_cost = total_before_commission

        cost_per_person = max(round(total_cost / param_persons, 2), self.MIN_PRICE_PER_PERSON)

        return Route(
            distance_km=param_distance,
            fuel_cost=fuel_cost,
            toll_cost=param_toll,
            total_cost=round(total_cost, 2),
            cost_per_person=cost_per_person,
            fuel_price=param_fuel_price,
            has_toll=param_has_toll,
            toll_count=param_toll_count,
            closest_station=param_closest_station,
        )

    # -----

    def get_alternative_routes(
        self,
        param_start_coords: Tuple[float, float],
        param_end_coords: Tuple[float, float],
        param_liter_per_100km: float,
        param_fuel_price_per_liter: float,
        param_persons: int,
        param_commission: bool,
        param_max_alternatives: int = 2,
    ) -> List[Route]:
        """ Fetch up to max_alternatives+1 routes from OSRM and compute costs for each """

        osrm_data = get_route_osrm_method(
            param_origin=param_start_coords,
            param_destination=param_end_coords,
            param_alternatives=True,
            param_steps=True,
        )

        routes = osrm_data.get("routes", [])[:param_max_alternatives + 1]

        options: List[Route] = []
        for idx, route in enumerate(routes, start=1):
            distance_km = round(route["distance"] / 1000, 2)
            duration_min = round(route["duration"] / 60, 1)

            toll_info = estimate_route_toll({"routes": [route]})
            toll_cost = float(toll_info["toll_cost"])
            has_toll = toll_info['has_toll']
            toll_count = len(toll_info['segments'])

            # Use calculate_route_method to get all cost details
            route_obj = self.calculate_route_method(
                param_distance=distance_km,
                param_liter_km=param_liter_per_100km,
                param_fuel_price=param_fuel_price_per_liter,
                param_toll=toll_cost,
                param_persons=param_persons,
                param_commission=param_commission,
                param_has_toll=has_toll,
                param_toll_count=toll_count,
                param_closest_station={},  # Not needed for alternatives
            )

            # Update route object with alternative-specific data
            route_obj.index = idx
            route_obj.duration_min = duration_min
            options.append(route_obj)

        return self._tag_routes(options)

    # -----

    def _tag_routes(self, param_route: List[Route]) -> List[Route]:
        """ Tag routes as cheapest, fastest, or toll-free """

        if not param_route:
            return param_route

        cheapest = min(param_route, key=lambda road: road.total_cost)
        fastest = min(param_route, key=lambda road: road.duration_min)

        for route in param_route:
            if route is cheapest:
                route.tags.append("le moins cher")
            if route is fastest:
                route.tags.append("le plus rapide")
            if route.toll_cost == 0:
                route.tags.append("sans péage")

        return param_route
