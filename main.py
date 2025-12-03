''' Python version : 3.13.9 '''

import os
import json
from bs4 import BeautifulSoup

def main() -> None:

    data_xml = os.path.join(
        os.getcwd(),
        "data",
        "xml",
        "essence",
        "PrixCarburants_instantane.xml"
    )
    
    with open(data_xml, "r") as file:
        data = file.read()

    soup = BeautifulSoup(data, "xml")
    
    pdv_beacon = soup.find_all("pdv")
    for pdv in pdv_beacon:
        if pdv.find('adresse'):
            address_beacon = pdv.find('adresse')
        if pdv.find('ville'):
            city_beacon = pdv.find('ville')
        if pdv.find_all('prix'):
            price_beacon = pdv.find_all('prix')

    fuel_name_beacon, fuel_price_beacon = [], []
    for price in price_beacon:
        if price.get('nom'):
            fuel_name_beacon.append(price.get('nom'))
            fuel_price_beacon.append(price.get('valeur'))

    dictionnary_fuel = {}
    for city, address, fuel_name, fuel_price in zip(city_beacon, address_beacon, fuel_name_beacon, fuel_price_beacon):
        if city.text not in dictionnary_fuel:
            dictionnary_fuel[city.text] = {
                address.text: {}
            }

        # else:
        #     if address.text not in dictionnary_fuel[city.text]:
        #         dictionnary_fuel[city.text][address.text] = {}

    os.makedirs('output', exist_ok=True)
    with open('output/fuel_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(dictionnary_fuel, json_file, ensure_ascii=False, indent=4)

    return None

if __name__ == "__main__":
    main()
