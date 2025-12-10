''' Python version : 3.13.9 '''

from src.retrieve_data_file import RetrieverData
from src.geocoders_file import Geocoders

def main() -> None:

    geocoder = Geocoders()
    geocoder.geocode_distance_method(
        param_locations={
            'start': 'Paris, France',
            'end': 'Marseille, France'
        }
    )

if __name__ == "__main__":
    main()
