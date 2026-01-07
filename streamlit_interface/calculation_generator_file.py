''' A Streamlit interface for route calculation '''

import streamlit as st
from src.gasoline_file import Gasoline
from src.geocoders_file import Geocoders
from src.calculator_file import RouteCalculator

class StreamlitCalculationGenerator:
    ''' A Streamlit interface for route calculation. '''

    def streamlit_interface_method(self) -> None:
        ''' Create the Streamlit interface for route calculation '''

        self._configure_page()
        self._display_title()

        # Get user inputs
        start_location, end_location = self._get_location_inputs()
        liter_km, fuel_type = self._get_fuel_inputs()
        toll, persons = self._get_toll_and_persons_inputs()

        if st.sidebar.button("Calculate Route", use_container_width=True):
            self._calculate_and_display_route(
                start_location, end_location, liter_km, fuel_type, toll, persons
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

    def _get_location_inputs(self) -> tuple[str, str]:
        ''' Get start and end location inputs '''

        st.sidebar.header("Route Parameters")

        start_col, end_col = st.columns(2)
        with start_col:
            start_location = st.text_input(
                "Start Location",
                placeholder="Paris"
            )

        with end_col:
            end_location = st.text_input(
                "End Location",
                placeholder="Lyon"
            )

        if start_location:
            with st.expander("Find Nearby Gas Stations"):
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
                geocoders = Geocoders()

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

    ) -> None:
        ''' Calculate route and display results using closest gas station price or selected station '''

        with st.spinner("Calculating route..."):
            try:
                gasoline = Gasoline()
                geocoders = Geocoders()

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
                    route = RouteCalculator()
                    start_coords = geocoders.geocode_coordinates_method(param_start_location)
                    end_coords = geocoders.geocode_coordinates_method(param_end_location)
                    # Nombre de péages détectés
                    has_toll = False
                    detected_toll = 0.0
                    toll_count = 0
                    if start_coords and end_coords:
                        has_toll = route.tolls.has_toll_on_route(
                        start=start_coords,
                        end=end_coords
                     )
                    toll_count = route.tolls.count_tolls_on_route(
                    start=start_coords,
                    end=end_coords
                    )
                    detected_toll = 15.0 if has_toll else 0.0


                        
    



                    if distance is not None:
                        route = RouteCalculator()
                        cost_per_person = route.calculate_route_method(
                            distance,
                            param_liter_km,
                            closest_fuel_price,
                            detected_toll,
                            param_persons
                        )
                        total_cost = cost_per_person * param_persons

                        result = {
                            'success': True,
                            'error': None,
                            'cost_per_person': cost_per_person,
                            'total_cost': round(total_cost, 2),
                            'distance': distance,
                            'fuel_price': closest_fuel_price,
                            'closest_station': closest_station,
                            'has_toll': has_toll,
                            'toll_count': toll_count,
                            'detected_toll': detected_toll,
                        }

                        self._display_success_results(
                            result,
                            param_start_location,
                            param_end_location,
                            param_liter_km,
                            param_fuel_type,
                            param_toll,
                            param_persons
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
        param_persons: int
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
            param_persons,
            param_result["has_toll"],
            param_result["toll_count"],
            param_result["detected_toll"],
        )
        self._display_cost_breakdown(
            param_result,
            param_toll,
            param_persons
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
        param_persons: int,
        param_has_toll: bool,
        param_toll_count: int,
        param_detected_toll: float
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
            st.write(f"**Toll:** {param_detected_toll:.2f}€")
            if param_has_toll:
                st.write("**Toll detected:**  Yes")
                st.write(f"**Toll count:** {param_toll_count}")
            else:
                st.write("**Toll detected:**  No")
                st.write("**Toll count:** 0")
            st.write(f"**Persons:** {param_persons}")

        return None

    # -----

    def _display_cost_breakdown(
        self,
        param_result: dict,
        param_toll: float,
        param_persons: int
    ) -> None:
        ''' Display cost breakdown '''

        st.subheader("Cost Breakdown")

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
