import haversine
import pandas as pd

HUBS = ["Paris", "Lyon", "Marseille", "Lille", "Bordeaux"]

MIN_DIST_KM = 120
MAX_DIST_KM = 500
NUMBER_OF_TRAJECT_BY_CITY = 7

cities = pd.read_csv("./data/csv/cities.csv")
routes = set()

for _, row in cities.iterrows():
    city = row["city"]
    origin_lat_lon = (row["lat"], row["lon"])

    distances = []
    for _, other_row in cities.iterrows():
        if city == other_row["city"]:
            continue

        destination_city = other_row["city"]
        destination_lat_lon = (other_row["lat"], other_row["lon"])

        distance = haversine.haversine(origin_lat_lon, destination_lat_lon)
        distances.append((destination_city, distance))

    for hub in HUBS:
        if hub != city:
            routes.add((city, hub))

    candidates = []
    for destination, distance in distances:
        if MIN_DIST_KM <= distance <= MAX_DIST_KM:
            candidates.append((destination, distance))

    candidates.sort(key=lambda x: x[1])

    for destination, distance in candidates[:NUMBER_OF_TRAJECT_BY_CITY]:
        routes.add((city, destination))

df_routes = pd.DataFrame(list(routes), columns=["from_city", "to_city"])
df_routes.to_csv("./data/csv/routes_to_scrape.csv", index=False)
