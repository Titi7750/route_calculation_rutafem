import streamlit as st
import requests

from src.geocoders_file import Geocoders
from src.gasoline_file import Gasoline
from src.v2.route_comparator import RouteComparatorV2


class StreamlitCalculationGeneratorV2:
    def streamlit_interface_method(self) -> None:
        st.set_page_config(
            page_title="Rutafem - Route Calculator",
            layout="centered",
        )

        st.title("Rutafem - Route Calculator")
        st.caption("Version V2 – comparaison intelligente des itinéraires")

        commission = st.sidebar.checkbox("Include 15% commission", True)
        persons = st.sidebar.slider("Passengers", 1, 5, 3)
        liter_km = st.sidebar.slider("Fuel consumption (L/100km)", 3.0, 15.0, 5.0)
        fuel_type = st.sidebar.selectbox(
            "Fuel type", ["SP95", "SP98", "Gazole", "GPLc", "E10"]
        )

        start = st.text_input("Start location")
        end = st.text_input("End location")

        if st.button("Calculate Route (V2)"):
            self._run(start, end, liter_km, fuel_type, persons, commission)

        if "routes_v2" in st.session_state:
            self._display_routes(st.session_state.routes_v2)

    def _run(self, start, end, liter_km, fuel_type, persons, commission):
        geo = Geocoders()
        gas = Gasoline()
        comparator = RouteComparatorV2()

        start_coords = geo.geocode_coordinates_method(start)
        end_coords = geo.geocode_coordinates_method(end)

        fuel_data = gas.get_data_fuel_method()
        stations = geo.find_closest_gas_stations_method(start, fuel_data, 1, 100)
        fuel_price = float(stations[0]["fuel_prices"][fuel_type])

        st.session_state.routes_v2 = comparator.get_alternative_routes(
            start_coords=start_coords,
            end_coords=end_coords,
            liter_per_100km=liter_km,
            fuel_price_per_liter=fuel_price,
            persons=persons,
            commission=commission,
        )

    def _display_routes(self, routes):
        labels = [
            f"Route {r.index} — {', '.join(r.tags)} — {r.cost_per_person:.2f} €/pers"
            for r in routes
        ]

        idx = st.radio("Available routes", range(len(routes)), format_func=lambda i: labels[i])
        r = routes[idx]

        st.subheader("Selected route details")
        st.write(f"Distance: {r.distance_km} km")
        st.write(f"Duration: {r.duration_min} min")
        st.write(f"Fuel cost: {r.fuel_cost} €")
        st.write(f"Toll cost: {r.toll_cost} €")
        st.write(f"Total: {r.total_cost} €")
        st.write(f"Per person: {r.cost_per_person} €")
        st.info(f"Tags: {', '.join(r.tags)}")
