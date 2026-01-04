''' A Streamlit interface for route calculation '''

import streamlit as st
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

        # Calculate route if button is clicked
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
                value="Paris",
                placeholder="Paris"
            )

        with end_col:
            end_location = st.text_input(
                "End Location",
                value="Lyon",
                placeholder="Lyon"
            )

        return start_location, end_location

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
        param_persons: int
    ) -> None:
        ''' Calculate route and display results '''

        with st.spinner("Calculating route..."):
            try:
                route = RouteCalculator()
                result = route.get_route_data_method(
                    param_start_location=param_start_location,
                    param_end_location=param_end_location,
                    param_liter_km=param_liter_km,
                    param_toll=param_toll,
                    param_persons=param_persons,
                    param_fuel_type=param_fuel_type
                )

                if result['success']:
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
                    st.error(f"Error: {result['error']}")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

        return None

    # -----

    def _display_success_results(
        self,
        result: dict,
        param_start_location: str,
        param_end_location: str,
        param_liter_km: float,
        param_fuel_type: str,
        param_toll: float,
        param_persons: int
    ) -> None:
        ''' Display successful calculation results '''

        st.success("Route calculation successful !")

        self._display_key_metrics(result)
        self._display_summary(
            param_start_location,
            param_end_location,
            param_liter_km,
            param_fuel_type,
            param_toll,
            param_persons
        )
        self._display_cost_breakdown(
            result,
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
