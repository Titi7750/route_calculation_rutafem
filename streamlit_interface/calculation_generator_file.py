import streamlit as st
from src.calculator_file import RouteCalculator

class StreamlitCalculationGenerator:
    ''' A Streamlit interface for route calculation. '''

    def streamlit_interface_method(self) -> None:
        ''' Create the Streamlit interface for route calculation '''

        st.set_page_config(
            page_title="Rutafem - Route Calculator",
            layout="centered",
            initial_sidebar_state="expanded"
        )

        st.title("Rutafem - Route Calculator")

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
            ["SP95", "SP98", "Gazole", "GPLc", "E10"],
            index=2
        )

        toll = st.sidebar.number_input(
            "Toll cost (€)",
            min_value=0.0,
            value=65.0,
            step=1.0
        )

        st.sidebar.subheader("Number of Persons")
        persons = st.sidebar.slider(
            "Number of persons",
            min_value=1,
            max_value=5,
            value=3
        )

        if st.sidebar.button("Calculate Route", use_container_width=True):
            with st.spinner("Calculating route..."):
                try:
                    route = RouteCalculator()
                    result = route.get_route_data_method(
                        param_start_location=start_location,
                        param_end_location=end_location,
                        param_liter_km=liter_km,
                        param_toll=toll,
                        param_persons=persons,
                        param_fuel_type=fuel_type,
                        param_city=None,
                        param_address=None
                    )

                    if result['success']:
                        st.success("Route calculation successful !")

                        distance_col, fuel_col, total_col = st.columns(3)
                        with distance_col:
                            st.metric(
                                "Distance",
                                f"{result['distance']:.2f} km"
                            )

                        with fuel_col:
                            st.metric(
                                "Fuel Price",
                                f"€{result['fuel_price']}/L"
                            )

                        with total_col:
                            st.metric(
                                "Total Cost",
                                f"€{result['total_cost']:.2f}"
                            )

                        st.subheader("Data Summary")

                        data_summary_col1, data_summary_col2 = st.columns(2)
                        with data_summary_col1:
                            st.write(f"**Start:** {start_location}")
                            st.write(f"**End:** {end_location}")
                            st.write(f"**Fuel Type:** {fuel_type}")

                        with data_summary_col2:
                            st.write(f"**Fuel Consumption:** {liter_km} L/100km")
                            st.write(f"**Toll:** {toll:.2f}€")
                            st.write(f"**Persons:** {persons}")

                        st.subheader("Cost Breakdown")
                        cost_breakdown = {
                            "Fuel Cost": result['total_cost'] - toll,
                            "Toll": toll,
                            "Total": result['total_cost']
                        }

                        breakdown_col1, breakdown_col2 = st.columns(2)
                        with breakdown_col1:
                            for item, cost in cost_breakdown.items():
                                st.write(f"{item}: **{cost:.2f}€**")

                        with breakdown_col2:
                            st.metric(
                                "Cost per person",
                                f"{result['cost_per_person']:.2f}€",
                                delta=f"÷ {persons} persons"
                            )

                    else:
                        st.error(f"Error: {result['error']}")

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
