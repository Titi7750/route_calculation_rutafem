''' Module to handle geocoding operations '''

from haversine import haversine, Unit
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

class Geocoders:
    ''' Class to handle geocoding operations '''

    def __init__(self, user_agent: str = "rutafem_geocoder"):
        ''' Initialize the geocoder with a user agent '''

        self.geolocator = Nominatim(user_agent=user_agent)

    # -----

    def geocode_coordinates_method(
        self,
        param_location: str
    ) -> tuple[float, float] | None:
        """Return (latitude, longitude) for a given address"""

        try:
            geo_location = self.geolocator.geocode(param_location, timeout=10)
            if geo_location:
                return (geo_location.latitude, geo_location.longitude)

            return None

        except GeocoderTimedOut as error:
            print(f"Problem geocoding {param_location}: {error}")
            return None

        except Exception as error:
            print(f"Unexpected error geocoding {param_location}: {error}")
            return None

    # -----

    def find_closest_gas_stations_method(
        self,
        param_start_location: str,
        param_fuel_data: dict,
        param_max_results: int = 5,
        param_max_distance_km: float = 50.0
    ) -> list:
        ''' Find closest gas stations to the start location using pre-geocoded coordinates '''

        start_coords = self.geocode_coordinates_method(param_start_location)

        if not start_coords:
            print(f"Could not geocode start location: {param_start_location}")
            return []

        start_point = start_coords

        gas_stations = []
        for city, addresses in param_fuel_data.items():
            for address, fuel_info in addresses.items():
                try:
                    latitude = fuel_info.get('latitude')
                    longitude = fuel_info.get('longitude')

                    if latitude is None or longitude is None:
                        continue

                    station_point = (latitude, longitude)

                    distance = haversine(start_point, station_point, unit=Unit.KILOMETERS)

                    if distance <= param_max_distance_km:
                        gas_stations.append({
                            'city': city,
                            'address': address,
                            'distance_km': round(distance, 2),
                            'fuel_prices': fuel_info.get('prix', {})
                        })

                except Exception as error:
                    print(f"Error processing station {address}, {city}: {error}")
                    continue

        gas_stations.sort(key=lambda x: x['distance_km'])
        return gas_stations[:param_max_results]

