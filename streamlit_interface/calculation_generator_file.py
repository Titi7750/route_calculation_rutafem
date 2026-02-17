''' A Streamlit interface for route calculation '''

import requests
import streamlit as st
from src.gasoline_file import Gasoline
from src.geocoders_file import Geocoder
from src.calculator_file import RouteCalculator

class StreamlitCalculationGenerator:
    ''' A Streamlit interface for route calculation. '''

    def streamlit_interface_method(self) -> None:
        ''' Create the Streamlit interface for route calculation '''

        self._configure_page()
        self._display_title()

        # Get user inputs
        commission = self._get_commission_input()
        start_location, end_location = self._get_location_inputs()
        liter_km, fuel_type = self._get_fuel_inputs()
        toll, persons = self._get_toll_and_persons_inputs()

        if st.sidebar.button("Calculate Route", use_container_width=True):
            self._calculate_and_display_route(
                start_location, end_location, liter_km, fuel_type, toll, persons, commission
            )

        return None

    # -----

    def _configure_page(self) -> None:
        ''' Configure Streamlit page settings '''

        st.set_page_config(
            page_title="Rutafem - Route Calculator",
            layout="centered",
            initial_sidebar_state="expanded"
        )

    # -----

    def _display_title(self) -> None:
        ''' Display page title '''

        st.title("Rutafem - Route Calculator")

        return None

    # -----

    def _get_commission_input(self) -> bool:
        ''' Get commission inclusion input '''

        st.sidebar.subheader("Commission")
        commission = st.sidebar.checkbox(
            "Include 15% commission",
            value=True
        )

        return commission

    # -----

    def _get_all_french_cities_from_api(self) -> list[str]:
        ''' Get ALL French cities from government API (36,000+ communes) '''

        try:
            # Cache pour éviter de refaire l'appel à chaque fois
            if 'french_cities_cache' not in st.session_state:
                with st.spinner("Chargement de toutes les communes françaises..."):
                    response = requests.get(
                        "https://geo.api.gouv.fr/communes?fields=nom,population&format=json",
                        timeout=15
                    )

                    if response.status_code == 200:
                        communes = response.json()

                        cities = []
                        for commune in communes:
                            if commune.get('population', 0) > 500:
                                cities.append(commune['nom'])

                        clean_cities = sorted(set(cities))
                        st.session_state.french_cities_cache = clean_cities

                    else:
                        st.error("Erreur lors du chargement des communes françaises")
                        st.session_state.french_cities_cache = []

            return st.session_state.french_cities_cache

        except Exception as e:
            st.error(f"Erreur de connexion à l'API: {e}")
            return []

    # -----

    def _get_location_inputs(self) -> tuple[str, str]:
        ''' Get start and end location inputs with all french cities from API '''

        st.sidebar.header("Route Parameters")

        all_french_cities = self._get_all_french_cities_from_api()

        if not all_french_cities:
            st.sidebar.error("Impossible de charger les villes. Vérifiez votre connexion internet.")
            return "", ""

        start_col, end_col = st.columns(2)
        with start_col:
            start_location = st.selectbox(
                "Ville de départ",
                options=[""] + all_french_cities,
                index=0,
                placeholder="Tapez pour rechercher une ville...",
                help=f"Recherchez parmi {len(all_french_cities):,} communes françaises"
            )

            if start_location == "":
                start_custom = st.text_input(
                    "Ou saisissez une adresse complète:",
                    placeholder="15 Rue de Rivoli, Paris, France",
                    key="start_custom",
                    help="Adresse précise, code postal, région..."
                )
                if start_custom:
                    start_location = start_custom

        with end_col:
            end_location = st.selectbox(
                "Ville d'arrivée",
                options=[""] + all_french_cities,
                index=0,
                placeholder="Tapez pour rechercher une ville...",
                help=f"Recherchez parmi {len(all_french_cities):,} communes françaises"
            )

            if end_location == "":
                end_custom = st.text_input(
                    "Ou saisissez une adresse complète:",
                    placeholder="Place Bellecour, Lyon, France",
                    key="end_custom",
                    help="Adresse précise, code postal, région..."
                )
                if end_custom:
                    end_location = end_custom

        if start_location and start_location != "":
            with st.expander("Trouver des stations-service proches"):
                self._display_nearby_gas_stations(start_location)

        return start_location, end_location

    # -----

    def _display_nearby_gas_stations(self, start_location: str) -> None:
        ''' Display nearby gas stations for the start location '''

        try:
            search_radius = st.slider(
                "Search radius (km)",
                min_value=10,
                max_value=100,
                value=50,
                step=10
            )

            with st.spinner("Finding nearby gas stations..."):
                gasoline = Gasoline()
                geocoders = Geocoder()

                fuel_data = gasoline.get_data_fuel_method()

                closest_stations = geocoders.find_closest_gas_stations_method(
                    param_start_location=start_location,
                    param_fuel_data=fuel_data,
                    param_max_results=5,
                    param_max_distance_km=search_radius
                )

                if closest_stations:
                    for index, station in enumerate(closest_stations, 1):
                        with st.container():
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.write(f"**#{index} {station['address']}**")
                                st.write(f"{station['city']}")

                            with col2:
                                st.metric(
                                    "Distance",
                                    f"{station['distance_km']} km"
                                )

                            if station['fuel_prices']:
                                prices_text = ", ".join(
                                    [f"{fuel_type}: €{price}"
                                     for fuel_type, price in station['fuel_prices'].items()]
                                )
                                st.write(f"{prices_text}")

                            st.divider()
                else:
                    st.warning(f"No gas stations found within {search_radius}km of {start_location}")

        except Exception as e:
            st.error(f"Error finding gas stations: {str(e)}")

    # -----

    def _get_fuel_inputs(self) -> tuple[float, str]:
        ''' Get fuel consumption and fuel type inputs '''

        st.sidebar.subheader("Fuel Parameters")
        liter_km = st.sidebar.slider(
            "Fuel consumption (L/100km)",
            min_value=3.0,
            max_value=15.0,
            value=5.0,
            step=0.1
        )

        fuel_type = st.sidebar.selectbox(
            "Fuel type",
            ["Select", "SP95", "SP98", "Gazole", "GPLc", "E10"],
            index=0
        )

        return liter_km, fuel_type

    # -----

    def _get_toll_and_persons_inputs(self) -> tuple[float, int]:
        ''' Get toll cost and number of persons inputs '''

        st.sidebar.subheader("Toll Cost (€)")
        toll = st.sidebar.number_input(
            "Toll",
            min_value=0.0,
            value=65.0,
            step=1.0
        )

        st.sidebar.subheader("Number of Persons")
        persons = st.sidebar.slider(
            "Persons",
            min_value=1,
            max_value=5,
            value=3
        )

        return toll, persons

    # -----

    def _calculate_and_display_route(
        self,
        param_start_location: str,
        param_end_location: str,
        param_liter_km: float,
        param_fuel_type: str,
        param_toll: float,
        param_persons: int,
        param_commission: bool
    ) -> None:
        ''' Calculate route and display results using closest gas station price or selected station '''

        with st.spinner("Calculating route..."):
            try:
                gasoline = Gasoline()
                geocoders = Geocoder()

                fuel_data = gasoline.get_data_fuel_method()
                closest_stations = geocoders.find_closest_gas_stations_method(
                    param_start_location=param_start_location,
                    param_fuel_data=fuel_data,
                    param_max_results=1,
                    param_max_distance_km=100.0
                )

                closest_station = None
                closest_fuel_price = None

                if closest_stations:
                    closest_station = closest_stations[0]
                    closest_fuel_price = closest_station['fuel_prices'].get(param_fuel_type)

                if closest_fuel_price:
                    closest_fuel_price = float(closest_fuel_price)

                    locations = {
                        'start': param_start_location,
                        'end': param_end_location
                    }
                    distance = geocoders.geocode_distance_method(locations)

                    if distance is not None:
                        route = RouteCalculator()
                        cost_per_person = route.calculate_route_method(
                            distance,
                            param_liter_km,
                            closest_fuel_price,
                            param_toll,
                            param_persons,
                            param_commission=param_commission
                        )
                        total_cost = cost_per_person * param_persons

                        result = {
                            'success': True,
                            'error': None,
                            'cost_per_person': cost_per_person,
                            'total_cost': round(total_cost, 2),
                            'distance': distance,
                            'fuel_price': closest_fuel_price,
                            'closest_station': closest_station
                        }

                        self._display_success_results(
                            result,
                            param_start_location,
                            param_end_location,
                            param_liter_km,
                            param_fuel_type,
                            param_toll,
                            param_persons,
                            param_commission
                        )
                    else:
                        st.error("Could not calculate distance between locations")
                else:
                    st.error(f"Could not find fuel price for {param_fuel_type} at selected stations")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

        return None

    # -----

    def _display_success_results(
        self,
        param_result: dict,
        param_start_location: str,
        param_end_location: str,
        param_liter_km: float,
        param_fuel_type: str,
        param_toll: float,
        param_persons: int,
        param_commission: bool
    ) -> None:
        ''' Display successful calculation results '''

        if param_result.get('closest_station'):
            with st.info(f"Fuel price from: **{param_result['closest_station']['address']}** ({param_result['closest_station']['distance_km']} km away)"):
                pass

        self._display_key_metrics(param_result)
        self._display_summary(
            param_start_location,
            param_end_location,
            param_liter_km,
            param_fuel_type,
            param_toll,
            param_persons
        )
        self._display_cost_breakdown(
            param_result,
            param_toll,
            param_persons,
            param_commission
        )

        return None

    # -----

    def _display_key_metrics(self, param_result: dict) -> None:
        ''' Display distance, fuel price, and total cost '''

        distance_col, fuel_col, total_col = st.columns(3)
        with distance_col:
            st.metric("Distance", f"{param_result['distance']:.2f} km")

        with fuel_col:
            st.metric("Fuel Price", f"€{param_result['fuel_price']}/L")

        with total_col:
            st.metric("Total Cost", f"€{param_result['total_cost']:.2f}")

        return None

    # -----

    def _display_summary(
        self,
        param_start_location: str,
        param_end_location: str,
        param_liter_km: float,
        param_fuel_type: str,
        param_toll: float,
        param_persons: int
    ) -> None:
        ''' Display data summary '''

        st.subheader("Data Summary")

        data_summary_col1, data_summary_col2 = st.columns(2)
        with data_summary_col1:
            st.write(f"**Start:** {param_start_location}")
            st.write(f"**End:** {param_end_location}")
            st.write(f"**Fuel Type:** {param_fuel_type}")

        with data_summary_col2:
            st.write(f"**Fuel Consumption:** {param_liter_km} L/100km")
            st.write(f"**Toll:** {param_toll:.2f}€")
            st.write(f"**Persons:** {param_persons}")

        return None

    # -----

    def _display_cost_breakdown(
        self,
        param_result: dict,
        param_toll: float,
        param_persons: int,
        param_commission: bool
    ) -> None:
        ''' Display cost breakdown '''

        if param_commission:
            st.subheader(f"Cost Breakdown (including 15% commission)")
        else:
            st.subheader(f"Cost Breakdown (no commission)")

        cost_breakdown = {
            "Fuel Cost": param_result['total_cost'] - param_toll,
            "Toll": param_toll,
            "Total": param_result['total_cost']
        }

        breakdown_col1, breakdown_col2 = st.columns(2)

        with breakdown_col1:
            for item, cost in cost_breakdown.items():
                st.write(f"{item}: **{cost:.2f}€**")

        with breakdown_col2:
            st.metric(
                "Cost per person",
                f"{param_result['cost_per_person']:.2f}€",
                delta=f"÷ {param_persons} persons"
            )

        return None
