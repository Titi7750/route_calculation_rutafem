''' A module to calculate routes using geocoding and fuel data '''

from typing import List, Tuple
from src.tolls_file import Tolls
from dataclasses import dataclass
from src.gasoline_file import Gasoline
from src.geocoders_file import Geocoders
from src.routing_file import get_route_osrm

# -----

@dataclass
class RouteOption:
    ''' Represents a single route option with its costs '''

    index: int
    distance_km: float
    duration_min: float
    fuel_cost: float
    toll_cost: float
    total_cost: float
    cost_per_person: float
    tags: List[str]

# -----

class RouteCalculator:
    ''' A class to calculate routes based on map data. '''

    COMMISSION_RATE = 0.15
    MIN_PRICE_PER_PERSON = 1.99

    def __init__(self):
        ''' Initialize the RouteCalculator class '''

        self.tolls = Tolls()
        self.gasoline = Gasoline()
        self.geocoder = Geocoders()

    # -----

    def calculate_route_method(
        self,
        param_distance: float,
        param_liter_km: float,
        param_fuel_price: float,
        param_toll: float,
        param_persons: int,
        param_commission: bool
    ) -> float:
        ''' Calculate the total cost based on provided parameters '''

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
        gasoline_price = liters_used * param_fuel_price
        total_cost = gasoline_price + param_toll

        if param_commission:
            commission_amount = total_cost * self.COMMISSION_RATE
            final_cost = total_cost + commission_amount
        else:
            final_cost = total_cost

        cost_per_person = max(round(final_cost / param_persons, 2), self.MIN_PRICE_PER_PERSON)

        return cost_per_person

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
    ) -> List[RouteOption]:
        ''' Fetch up to max_alternatives+1 routes from OSRM and compute costs for each '''

        osrm_data = get_route_osrm(
            origin=param_start_coords,
            destination=param_end_coords,
            alternatives=True,
            steps=True,
        )

        routes = osrm_data.get("routes", [])[:param_max_alternatives + 1]
        options: List[RouteOption] = []

        for idx, route in enumerate(routes, start=1):
            distance_km = round(route["distance"] / 1000, 2)
            duration_min = round(route["duration"] / 60, 1)

            toll_info = self.tolls.get_toll_details({"routes": [route]})
            toll_cost = float(toll_info["toll_cost"])

            liters = distance_km * (param_liter_per_100km / 100)
            fuel_cost = round(liters * param_fuel_price_per_liter, 2)

            cost_per_person = self.calculate_route_method(
                param_distance=distance_km,
                param_liter_km=param_liter_per_100km,
                param_fuel_price=param_fuel_price_per_liter,
                param_toll=toll_cost,
                param_persons=param_persons,
                param_commission=param_commission,
            )
            total_cost = round(cost_per_person * param_persons, 2)

            options.append(RouteOption(
                index=idx,
                distance_km=distance_km,
                duration_min=duration_min,
                fuel_cost=fuel_cost,
                toll_cost=toll_cost,
                total_cost=total_cost,
                cost_per_person=cost_per_person,
                tags=[],
            ))

        return self._tag_routes(options)

    # -----

    def _tag_routes(self, param_route: List[RouteOption]) -> List[RouteOption]:
        ''' Tag routes as cheapest, fastest, or toll-free '''

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
