import haversine
import pandas as pd

HUBS = ["Paris", "Lyon", "Marseille", "Lille", "Bordeaux"]

MIN_DIST_KM = 120
MAX_DIST_KM = 900
PER_REGION = 2
MAX_REGIONS_PER_CITY = None

cities = pd.read_csv("./data/csv/cities.csv")
routes = set()
city_set = set(cities["city"])
all_regions = sorted(cities["region"].unique().tolist())
city_to_region = dict(zip(cities["city"], cities["region"])) # Map city to its region

for _, row in cities.iterrows():
    origin_city = row["city"]
    origin_region = row["region"]
    origin_lat_lon = (row["lat"], row["lon"])

    for hub in HUBS:
        if hub != origin_city and hub in city_set:
            destination_region = city_to_region.get(hub)
            if destination_region:
                routes.add((origin_city, origin_region, hub, destination_region))

    regions_added = 0
    for region in all_regions:
        if region == origin_region:
            continue

        candidates_dataframe = cities[cities["region"] == region]

        distances = []
        for _, other_row in candidates_dataframe.iterrows():
            destination_city = other_row["city"]
            if destination_city == origin_city:
                continue

            destination_lat_lon = (other_row["lat"], other_row["lon"])
            distance = haversine.haversine(origin_lat_lon, destination_lat_lon)

            if MIN_DIST_KM <= distance <= MAX_DIST_KM:
                distances.append((destination_city, distance))

        if not distances:
            continue

        distances.sort(key=lambda x: x[1])

        for destination_city, distance in distances[:PER_REGION]:
            destination_region = city_to_region.get(destination_city)
            if destination_region:
                routes.add((origin_city, origin_region, destination_city, destination_region))

        regions_added += 1
        if MAX_REGIONS_PER_CITY is not None and regions_added >= MAX_REGIONS_PER_CITY:
            break

df_routes = pd.DataFrame(
    sorted(list(routes)), columns=["from_city", "from_region", "to_city", "to_region"]
)
df_routes.to_csv("./data/csv/routes_to_scrape.csv", index=False)
