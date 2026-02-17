''' Script to get latitude, longitude and region of French cities and save them to a CSV file. '''

import time
import requests
import pandas as pd
from src.geocoders_file import Geocoder

cities = [
    "Paris",
    "Lyon",
    "Marseille",
    "Lille",
    "Bordeaux",
    "Toulouse",
    "Nice",
    "Nantes",
    "Strasbourg",
    "Montpellier",
    "Rennes",
    "Reims",
    "Le Havre",
    "Saint-Étienne",
    "Toulon",
    "Grenoble",
    "Dijon",
    "Angers",
    "Nîmes",
    "Villeurbanne",
    "Clermont-Ferrand",
    "Le Mans",
    "Aix-en-Provence",
    "Brest",
    "Tours",
    "Amiens",
    "Limoges",
    "Annecy",
    "Perpignan",
    "Besançon",
    "Metz",
    "Nancy",
    "Avignon",
    "La Rochelle",
    "Pau",
    "Bayonne",
    "Albi",
    "Rodez",
    "Cahors",
    "Montauban",
    "Agen",
    "Auch",
    "Foix",
    "Carcassonne",
    "Narbonne",
    "Béziers",
    "Sète",
    "Mende",
    "Millau",
    "Brive-la-Gaillarde",
    "Tarbes",
    "Saint-Gaudens",
    "Agde",
    "Narbonne-Plage",
    "Poitiers",
    "Niort",
    "La Roche-sur-Yon",
    "Angoulême",
    "Périgueux",
    "Bergerac",
    "Libourne",
    "Arcachon",
    "Dax",
    "Mont-de-Marsan",
    "Saint-Jean-de-Luz",
    "Aurillac",
    "Saint-Flour",
    "Issoire",
    "Montluçon",
    "Moulins",
    "Nevers",
    "Bourges",
    "Châteauroux",
    "Vierzon",
    "Chartres",
    "Orléans",
    "Blois",
    "Montargis",
    "Riom",
    "Le Puy-en-Velay",
    "Troyes",
    "Chaumont",
    "Langres",
    "Vesoul",
    "Belfort",
    "Mulhouse",
    "Colmar",
    "Haguenau",
    "Saverne",
    "Forbach",
    "Thionville",
    "Verdun",
    "Bar-le-Duc",
    "Épinal",
    "Saint-Dié-des-Vosges",
    "Auxerre",
    "Sens",
    "Dole",
    "Lons-le-Saunier",
    "Saint-Claude",
    "Oyonnax",
    "Bourg-en-Bresse",
    "Autun",
    "Beaune",
    "Villefranche-sur-Saône",
    "Roanne",
    "Montbrison",
    "Annonay",
    "Valence",
    "Montélimar",
    "Romans-sur-Isère",
    "Bollène",
    "Gap",
    "Briançon",
    "Digne-les-Bains",
    "Sisteron",
    "Manosque",
    "Draguignan",
    "Fréjus",
    "Grasse",
    "Cannes",
    "Antibes",
    "Menton",
    "Hyères",
    "Orange",
    "Carpentras",
    "Uzès",
    "Arras",
    "Lens",
    "Douai",
    "Valenciennes",
    "Calais",
    "Boulogne-sur-Mer",
    "Saint-Malo",
    "Lorient",
    "Vannes",
    "Quimper",
    "Morlaix",
    "Saint-Brieuc",
    "Rouen",
    "Évreux",
    "Caen",
    "Cherbourg-en-Cotentin",
    "Versailles",
    "Nanterre",
    "Créteil",
    "Évry-Courcouronnes",
    "Melun",
    "Meaux",
    "Cergy",
    "Laval",
    "Mayenne",
    "Alençon",
    "Flers"
]

def get_region_from_latlon(param_latitude: float, param_longitude: float) -> str | None:
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "format": "json",
        "lat": param_latitude,
        "lon": param_longitude,
        "zoom": 10,
        "addressdetails": 1,
        "accept-language": "fr",
    }
    request = requests.get(
        url,
        params=params,
        headers={
            "User-Agent": "school-project-peages"
        }
    )
    request.raise_for_status()
    data = request.json()
    address = data.get("address", {})

    return address.get("state") or address.get("region")

rows = []
geocoder = Geocoder()
for city in cities:
    query = f"{city}, France"
    coords = geocoder._geocode_longitude_latitude_method(query)

    lat = coords["latitude"]
    lon = coords["longitude"]

    region = None
    try:
        region = get_region_from_latlon(lat, lon)
    except Exception as e:
        print(f"Region not found for {city}: {e}")

    rows.append([city, lat, lon, region])

    time.sleep(1.0)

dataframe = pd.DataFrame(rows, columns=["city", "lat", "lon", "region"])
dataframe = dataframe.dropna(subset=["region"]).copy()
dataframe.to_csv("./data/csv/cities_with_regions.csv", index=False)
