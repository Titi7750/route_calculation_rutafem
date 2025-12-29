''' Python version : 3.13.9 '''

from src.calculator_file import RouteCalculator

def main() -> None:
    ''' Main function to run the route calculation '''

    route = RouteCalculator()
    result = route.get_route_data_method(
        param_start_location="Paris",
        param_end_location="Lyon", 
        param_liter_km=5,
        param_toll=65,
        param_persons=3,
        param_fuel_type="Gazole",
        param_city="Paris",
        param_address="101 BLD MORTIER"
    )

    if result['success']:
        print(f"Distance: {result['distance']} km")
        print(f"Fuel city: {result['fuel_city']}")
        print(f"Fuel address: {result['fuel_address']}")
        print(f"Fuel price: €{result['fuel_price']}/L")
        print(f"Total cost: €{result['total_cost']}")
        print(f"Cost per person: €{result['cost_per_person']}")
    else:
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    main()
