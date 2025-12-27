''' Cron : data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/exports/parquet '''

import os
import json
import pandas as pd

class Gasoline:
    ''' Class to retrieve data from different extension files '''

    def get_data_fuel_method(self) -> dict:
        ''' Method to retrieve fuel data from a Parquet file '''

        data_parquet = os.path.join(
            os.getcwd(),
            "data",
            "parquet",
            "prix-des-carburants-en-france-flux-instantane-v2.parquet"
        )
        fuel_dataframe = pd.read_parquet(data_parquet)

        dictionary_fuel = {}
        for _, row in fuel_dataframe.iterrows():
            fuel_key = f"{row['ville']}"

            if fuel_key not in dictionary_fuel:
                dictionary_fuel[fuel_key] = {}

            if row['adresse'] not in dictionary_fuel[fuel_key]:
                dictionary_fuel[fuel_key][row['adresse']] = {}

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
