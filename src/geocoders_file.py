import time
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

class Geocoders:
    ''' Class to handle geocoding operations '''

    def __init__(self, user_agent: str = "rutafem_geocoder"):
        ''' Initialize the geocoder with a user agent '''

        self.geolocator = Nominatim(user_agent=user_agent)

    # -----

    def _geocode_longitude_latitude_method(self, param_locations: dict) -> dict:
        ''' Method to get longitude and latitude of a location '''

        location_dictionary = {}
        for key, location in param_locations.items():
            location_dictionary[key] = {}

            locations = location if isinstance(location, list) else [location]

            for location in locations:
                try:
                    geo_location = self.geolocator.geocode(location, timeout=10)

                    if geo_location:
                        location_dictionary[key][location] = {
                            'latitude': geo_location.latitude,
                            'longitude': geo_location.longitude
                        }
                    else:
                        location_dictionary[key][location] = {
                            'latitude': None,
                            'longitude': None
                        }

                    time.sleep(1)

                except GeocoderTimedOut as error:
                    print(f"Problem geocoding {location}: {error}")
                    location_dictionary[key][location] = {
                        'latitude': None,
                        'longitude': None
                    }

                except Exception as error:
                    print(f"Unexpected error geocoding {location}: {error}")
                    location_dictionary[key][location] = {
                        'latitude': None,
                        'longitude': None
                    }

        return location_dictionary

    # -----

    def geocode_distance_method(self, param_locations: dict) -> float | None:
        ''' Method to geocode distance between two locations using location_dictionary '''

        location_dictionary = self._geocode_longitude_latitude_method(param_locations)

        start_location = param_locations['start']
        end_location = param_locations['end']

        start_coords = location_dictionary['start'].get(start_location)
        end_coords = location_dictionary['end'].get(end_location)

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
