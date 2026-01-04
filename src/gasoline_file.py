''' Module to handle gasoline data files '''

import os
import json
import shutil
import subprocess
import pandas as pd

class Gasoline:
    ''' Class to retrieve data from different extension files '''

    def __init__(self):
        ''' Constructor of the Gasoline class '''

        self.curl_parquet = (
            "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/exports/parquet"
        )

        self._download_parquet_file_method()

    # -----

    def _download_parquet_file_method(self) -> None:
        ''' Method to download the Parquet file '''

        data_dir = os.path.join(
            os.getcwd(),
            "data",
            "parquet"
        )
        os.makedirs(data_dir, exist_ok=True)

        file_path = os.path.join(data_dir, "prix-des-carburants-en-france-flux-instantane-v2.parquet")
        new_file_path = os.path.join(
            data_dir,
            'prix-des-carburants-en-france-flux-instantane-v2_old.parquet'
        )

        try:
            if not os.path.isfile(file_path):
                print("Downloading parquet file from API...")
                subprocess.run([
                    "curl", "-o", file_path, self.curl_parquet
                ], check=True, capture_output=True, text=True)
                print("Download completed successfully.")

            if os.path.isfile(file_path):
                if os.path.isfile(new_file_path):
                    os.remove(new_file_path)

                shutil.copy(file_path, new_file_path)
                os.remove(file_path)

                print("Updating parquet file...")
                subprocess.run([
                    "curl", "-o", file_path, self.curl_parquet
                ], check=True, capture_output=True, text=True)
                print("Update completed successfully.")

        except subprocess.CalledProcessError as e:
            print(f"Error downloading parquet file: {e.stderr if e.stderr else e}")

            if os.path.isfile(new_file_path):
                print("Restoring backup file...")
                shutil.copy(new_file_path, file_path)
            else:
                print("Warning: No backup file available.")
        except Exception as e:
            print(f"Unexpected error during download: {e}")

        return None

    # -----

    def get_data_fuel_method(self) -> dict:
        ''' Method to retrieve fuel data including latitude and longitude from parquet file '''

        data_parquet = os.path.join(
            os.getcwd(),
            "data",
            "parquet",
            "prix-des-carburants-en-france-flux-instantane-v2.parquet"
        )

        if not os.path.isfile(data_parquet):
            raise FileNotFoundError(f"Parquet file not found at {data_parquet}. Please ensure data has been downloaded.")

        fuel_dataframe = pd.read_parquet(data_parquet)

        dictionary_fuel = {}
        for _, row in fuel_dataframe.iterrows():
            fuel_key = f"{row['ville']}"

            if fuel_key not in dictionary_fuel:
                dictionary_fuel[fuel_key] = {}

            if row['adresse'] not in dictionary_fuel[fuel_key]:
                try:
                    lat = float(row.get('latitude')) if row.get('latitude') is not None else None
                    lon = float(row.get('longitude')) if row.get('longitude') is not None else None

                    if lat is not None and (lat > 90 or lat < -90): # -90 to 90 (S to N)
                        lat = lat / 100000
                    if lon is not None and (lon > 180 or lon < -180): # -180 to 180 (W to E)
                        lon = lon / 100000

                    latitude = lat
                    longitude = lon
                except (ValueError, TypeError):
                    latitude = None
                    longitude = None

                dictionary_fuel[fuel_key][row['adresse']] = {
                    'latitude': latitude,
                    'longitude': longitude
                }

            if isinstance(row['prix'], str):
                try:
                    prix_list = json.loads(row['prix']) # Convert string to list of dictionaries
                except:
                    prix_list = []
            else:
                prix_list = row['prix'] if isinstance(row['prix'], list) else []

            price_key = 'prix'
            if price_key not in dictionary_fuel[fuel_key][row['adresse']]:
                dictionary_fuel[fuel_key][row['adresse']][price_key] = {}

            for price_dict in prix_list:
                if isinstance(price_dict, dict):
                    name_fuel = price_dict.get('@nom')
                    value_price = price_dict.get('@valeur')
                    if name_fuel and value_price:
                        dictionary_fuel[fuel_key][row['adresse']][price_key][name_fuel] = value_price

        return dictionary_fuel
