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

    def geocode_longitude_latitude_method(self, param_locations: dict) -> dict:
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

                    print(f"Problem geocoding {error}")

        return location_dictionary

    # -----

    def geocode_distance_method(self, param_locations: dict) -> None:
        ''' Method to geocode distance between two locations using location_dictionary '''

        location_dictionary = self.geocode_longitude_latitude_method(param_locations)

        start_location = param_locations['start']
        end_location = param_locations['end']

        start_coords = location_dictionary['start'].get(start_location)
        end_coords = location_dictionary['end'].get(end_location)

        if start_coords and end_coords:
            if start_coords['latitude'] and start_coords['longitude'] and \
               end_coords['latitude'] and end_coords['longitude']:

                try:
                    lon_start = start_coords['longitude']
                    lat_start = start_coords['latitude']
                    lon_end = end_coords['longitude']
                    lat_end = end_coords['latitude']

                    url = f"https://router.project-osrm.org/route/v1/driving/{lon_start},{lat_start};{lon_end},{lat_end}?overview=false"

                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if data['routes']:
                            # Distance in meters, convert to km
                            distance_km = data['routes'][0]['distance'] / 1000
                            print(f"Distance exacte :{distance_km:.2f}km")
                            return distance_km
                    else:
                        print(f"OSRM API error: {response.status_code}")

                except requests.exceptions.RequestException as error:
                    print(f"Problem calculating distance with OSRM: {error}")

        print("Unable to calculate distance - missing coordinates")

        return None
