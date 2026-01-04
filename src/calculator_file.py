''' A module to calculate routes using geocoding and fuel data '''

from src.gasoline_file import Gasoline
from src.geocoders_file import Geocoders

class RouteCalculator:
    ''' A class to calculate routes based on map data. '''

    def __init__(self):
        ''' Initialize the RouteCalculator class '''

        self.geocoder = Geocoders()
        self.gasoline = Gasoline()

    # -----

    def _calculate_route_method(
        self,
        param_distance: float,
        param_liter_km: float,
        param_fuel_price: float,
        param_toll: float,
        param_persons: int
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

        total_cost_divided = total_cost / param_persons

        return round(total_cost_divided, 2)

    # -----

    def get_route_data_method(
        self,
        param_start_location: str,
        param_end_location: str,
        param_liter_km: float,
        param_fuel_type: str,
        param_toll: float,
        param_persons: int
    ) -> dict:
        ''' Calculate route cost using geocoding and real fuel prices '''

        try:
            locations = {
                'start': param_start_location,
                'end': param_end_location
            }
            distance = self.geocoder.geocode_distance_method(locations)

            if distance is None:
                return {
                    'success': False,
                    'error': 'Could not calculate distance between locations',
                    'cost_per_person': None,
                    'total_cost': None,
                    'distance': None,
                    'fuel_price': None
                }

            fuel_data = self.gasoline.get_data_fuel_method()
            fuel_price = None

            if fuel_price is None:
                for city_data in fuel_data.values():
                    for address_data in city_data.values():
                        prices = address_data.get('prix', {})
                        if param_fuel_type in prices:
                            fuel_price = float(prices[param_fuel_type])
                            break

                    if fuel_price:
                        break

            if fuel_price is None:
                return {
                    'success': False,
                    'error': f'Could not find fuel price for {param_fuel_type}',
                    'cost_per_person': None,
                    'total_cost': None,
                    'distance': distance,
                    'fuel_price': None
                }

            cost_per_person = self._calculate_route_method(
                distance,
                param_liter_km,
                fuel_price,
                param_toll,
                param_persons
            )
            total_cost = cost_per_person * param_persons

            return {
                'success': True,
                'error': None,
                'cost_per_person': cost_per_person,
                'total_cost': round(total_cost, 2),
                'distance': distance,
                'fuel_price': fuel_price
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'cost_per_person': None,
                'total_cost': None,
                'distance': None,
                'fuel_price': None
            }
