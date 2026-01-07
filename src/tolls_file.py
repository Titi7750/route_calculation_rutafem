import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point


class Tolls:
    """
    Handle toll detection using toll portiques (points)
    """

    def __init__(
        self,
        excel_path: str = "data/portiques-free-flow-25-10-2025.xlsx"
    ):
        # 1️⃣ Charger l’Excel
        df = pd.read_excel(excel_path)

        # 2️⃣ Séparer latitude / longitude
        df[["latitude", "longitude"]] = (
            df["Coordonnées GPS"]
            .str.split(",", expand=True)
            .astype(float)
        )

        # 3️⃣ Créer les points géographiques
        geometry = [
            Point(lon, lat)
            for lat, lon in zip(df["latitude"], df["longitude"])
        ]

        # 4️⃣ Créer un GeoDataFrame
        self.portiques = gpd.GeoDataFrame(
            df,
            geometry=geometry,
            crs="EPSG:4326"
        ).to_crs(epsg=2154)

    # -------------------------------------------------

    def _build_route_buffer(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        buffer_m: int
    ):
        """
        Create buffered route geometry
        """
        line = LineString([
            (start[1], start[0]),
            (end[1], end[0])
        ])

        gdf = gpd.GeoDataFrame(
            geometry=[line],
            crs="EPSG:4326"
        ).to_crs(epsg=2154)

        return gdf.buffer(buffer_m).iloc[0]

    # -------------------------------------------------

    def has_toll_on_route(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        buffer_m: int = 2000
    ) -> bool:
        """
        Return True if at least one toll portique is detected
        """

        zone = self._build_route_buffer(start, end, buffer_m)

        return self.portiques.intersects(zone).any()

    # -------------------------------------------------

    def count_tolls_on_route(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        buffer_m: int = 500
    ) -> int:
        """
        Return number of toll portiques detected on route
        """

        zone = self._build_route_buffer(start, end, buffer_m)

        return int(self.portiques.intersects(zone).sum())
