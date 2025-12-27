import os
from bs4 import BeautifulSoup

class RetrieverData:
    ''' Class to retrieve data from different extension files '''

    def retrieve_data_fuel_method(self) -> dict:
        ''' Method to retrieve fuel data from an XML file '''

        data_xml = os.path.join(
            os.getcwd(),
            "data",
            "xml",
            "PrixCarburants_quotidien_20251203.xml"
        )

        with open(data_xml, "r") as file:
            data = file.read()

        soup = BeautifulSoup(data, "xml")

        pdv_beacon = soup.find_all("pdv")

        dictionary_fuel = {}
        for pdv in pdv_beacon:
            city_tag = pdv.find('ville')
            address_tag = pdv.find('adresse')

            if not city_tag or not address_tag:
                continue

            city = city_tag.text.strip().upper()
            address = address_tag.text.strip().upper()

            if city not in dictionary_fuel:
                dictionary_fuel[city] = {}

            if address not in dictionary_fuel[city]:
                dictionary_fuel[city][address] = {}

            for price in pdv.find_all('prix'):
                fuel_name = price.get('nom')
                fuel_price = price.get('valeur')

                if fuel_name and fuel_price:
                    dictionary_fuel[city][address][fuel_name] = fuel_price

        return dictionary_fuel
