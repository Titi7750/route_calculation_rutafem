''' Module to handle geocoding operations '''

import time
import requests
from haversine import haversine, Unit
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

class Geocoders:
    ''' Class to handle geocoding operations '''

    def __init__(self, user_agent: str = "rutafem_geocoder"):
        ''' Initialize the geocoder with a user agent '''

        self.geolocator = Nominatim(user_agent=user_agent)

    # -----

    def _geocode_longitude_latitude_method(self, param_location: str) -> dict:
        ''' Method to get longitude and latitude of a single location '''

        try:
            geo_location = self.geolocator.geocode(param_location, timeout=10)
            if geo_location:
                return {
                    'latitude': geo_location.latitude,
                    'longitude': geo_location.longitude
                }
            else:
                return {
                    'latitude': None,
                    'longitude': None
                }

        except GeocoderTimedOut as error:
            print(f"Problem geocoding {param_location}: {error}")
            return {'latitude': None, 'longitude': None}

        except Exception as error:
            print(f"Unexpected error geocoding {param_location}: {error}")
            return {'latitude': None, 'longitude': None}

    # -----

    def geocode_distance_method(self, param_locations: dict) -> float | None:
        ''' Method to calculate distance between two locations '''

        start_location = param_locations['start']
        end_location = param_locations['end']

        start_coords = self._geocode_longitude_latitude_method(start_location)
        time.sleep(1)
        end_coords = self._geocode_longitude_latitude_method(end_location)
        time.sleep(1)

        if not start_coords or not end_coords:
            print("Could not retrieve coordinates for one or both locations")
            return None

        if start_coords['latitude'] is None or start_coords['longitude'] is None or \
            end_coords['latitude'] is None or end_coords['longitude'] is None:
            print("Both locations could not be geocoded")
            return None

        lon_start = start_coords['longitude']
        lat_start = start_coords['latitude']
        lon_end = end_coords['longitude']
        lat_end = end_coords['latitude']

        url = f"https://router.project-osrm.org/route/v1/driving/{lon_start},{lat_start};{lon_end},{lat_end}"
        url_params = {
            'overview': 'false',
            'alternatives': 'false',
            'steps': 'false'
        }

        try:
            response = requests.get(url, params=url_params, timeout=10)
            response.raise_for_status()
            data = response.json()

            routes = data.get('routes', [])
            if not routes:

                print("No routes found in OSRM response")
                return None

            distance_km = round(routes[0]['distance'] / 1000, 2)

            return distance_km

        except requests.exceptions.RequestException as error:
            print(f"Problem calculating distance with OSRM: {error}")

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

        start_coords = self._geocode_longitude_latitude_method(param_start_location)

        if start_coords['latitude'] is None or start_coords['longitude'] is None:
            print(f"Could not geocode start location: {param_start_location}")
            return []

        start_point = (start_coords['latitude'], start_coords['longitude'])

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
    
    def geocode_coordinates_method(
        self,
        param_location: str
    ) -> tuple[float, float] | None:
        """Return (latitude, longitude) for a given address"""

        coords = self._geocode_longitude_latitude_method(param_location)

        if coords['latitude'] is not None and coords['longitude'] is not None:
            return (coords['latitude'], coords['longitude'])

        return None

