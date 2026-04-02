""" A Streamlit interface for route calculation """

import requests
import streamlit as st
from typing import List
from src.gasoline_file import Gasoline
from src.geocoders_file import Geocoders
from src.tolls_file import estimate_route_toll
from src.routing_file import get_route_osrm_method
from src.calculator_file import RouteCalculator, Route
from src.csv_export import RutafemCSVExporter, RunData

# ── NEW: import the eco comparison module ──────────────────────────────────────
from src.eco_comparison import EcoComparison, VEHICLE_OPTIONS, car_co2, get_train_price_range, get_vehicle_co2_kg_km, load_train_prices, train_co2
# ──────────────────────────────────────────────────────────────────────────────

# -----

class StreamlitCalculationGenerator:
    """ A Streamlit interface for route calculation. """

    def _find_closest_stations(
        self,
        param_start_location: str,
        param_max_results: int,
        param_max_distance_km: float,
    ) -> list[dict]:
        """ Load fuel data and return closest stations for a location """

        gasoline = Gasoline()
        geocoders = Geocoders()
        fuel_data = gasoline.get_data_fuel_method()

        return geocoders.find_closest_gas_stations_method(
            param_start_location=param_start_location,
            param_fuel_data=fuel_data,
            param_max_results=param_max_results,
            param_max_distance_km=param_max_distance_km,
        )

    # -----

    def streamlit_interface_method(self) -> None:
        """ Create the Streamlit interface for route calculation """

        st.set_page_config(
            page_title="Rutafem - Calculateur d'itinéraire",
            layout="centered",
            initial_sidebar_state="expanded"
        )
        st.title("Rutafem - Calculateur d'itinéraire")

        # Get user inputs
        commission = self._get_commission_input()
        start_location, end_location = self._get_location_inputs()
        liter_km, fuel_type = self._get_fuel_inputs()
        persons = self._get_persons_inputs()

        calculate_clicked = st.sidebar.button("Calculer l'itinéraire", use_container_width=True)

        if calculate_clicked:
            self._calculate_and_display_route(
                start_location, end_location, liter_km, fuel_type, persons, commission
            )
        elif "calculation_result" in st.session_state:
            self._render_cached_calculation()

        return None

    # -----

    def _get_commission_input(self) -> bool:
        """ Get commission inclusion input """

        st.sidebar.subheader("Commission")
        commission = st.sidebar.checkbox(
            "Include 15% commission",
            value=True
        )

        return commission

    # -----

    def _get_all_french_cities_from_api(self) -> list[str]:
        """ Get ALL French cities from government API (36,000+ communes) """

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
        """ Get start and end location inputs with all french cities from API """

        st.sidebar.header("Paramètres de l'itinéraire")

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
        """ Display nearby gas stations for the start location """

        try:
            with st.spinner("Finding nearby gas stations..."):
                closest_stations = self._find_closest_stations(
                    param_start_location=start_location,
                    param_max_results=5,
                    param_max_distance_km=10.0
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
                    st.warning("No nearby gas stations found within 10 km of the start location.")

        except Exception as e:
            st.error(f"Error finding gas stations: {str(e)}")

        return None

    # -----

    def _get_fuel_inputs(self) -> tuple[float, str]:
        """ Get fuel consumption and fuel type inputs """

        st.sidebar.subheader("Carburant")
        liter_km = st.sidebar.slider(
            "Consommation de carburant (L/100km)",
            min_value=3.0,
            max_value=15.0,
            value=5.0,
            step=0.1
        )

        fuel_type = st.sidebar.selectbox(
            "Type de carburant",
            ["Sélectionner", "SP95", "SP98", "Gazole", "GPLc", "E10"],
            index=0
        )

        return liter_km, fuel_type

    # -----

    def _get_persons_inputs(self) -> int:
        """ Get number of persons inputs """

        st.sidebar.subheader("Nombre de personnes")
        persons = st.sidebar.slider(
            "Personnes partageant le trajet",
            min_value=1,
            max_value=5,
            value=3
        )

        return persons

    # -----

    def _calculate_and_display_route(
        self,
        param_start_location: str,
        param_end_location: str,
        param_liter_km: float,
        param_fuel_type: str,
        param_persons: int,
        param_commission: bool
        ) -> None:
        """Calculate route and display results — now also writes to CSV."""
 
        if not param_start_location or not param_end_location:
            st.error("Please provide both start and end locations")
            return None
 
        if param_fuel_type == "Select":
            st.error("Please select a fuel type")
            return None
 
        with st.spinner("Calculating route..."):
            try:
                geocoders = Geocoders()
                route_calculator = RouteCalculator()
    
                closest_stations = self._find_closest_stations(
                    param_start_location=param_start_location,
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

                    start_coords = geocoders.geocode_coordinates_method(param_start_location)
                    end_coords = geocoders.geocode_coordinates_method(param_end_location)
    
                    if not start_coords or not end_coords:
                        st.error("Could not geocode one or both locations")
                        return None

                    osrm_data = get_route_osrm_method(
                        param_origin=start_coords,
                        param_destination=end_coords,
                        param_steps=True,
                        param_overview="false"
                    )
    
                    routes = osrm_data.get('routes', [])
                    if not routes:
                        st.error("Could not calculate route between locations")
                        return None
    
                    distance = round(routes[0]['distance'] / 1000, 2)

                    # Nombre de péages détectés
                    toll_info = estimate_route_toll(osrm_data)
                    has_toll = toll_info['has_toll']
                    toll_count = len(toll_info['segments'])
                    detected_toll = float(toll_info['toll_cost'])

                    # Create Route object using the calculator
                    route = route_calculator.calculate_route_method(
                        param_distance=distance,
                        param_liter_km=param_liter_km,
                        param_fuel_price=closest_fuel_price,
                        param_toll=detected_toll,
                        param_persons=param_persons,
                        param_commission=param_commission,
                        param_has_toll=has_toll,
                        param_toll_count=toll_count,
                        param_closest_station=closest_station
                    )

                    st.session_state.calculation_result = {
                        "start_location": param_start_location,
                        "end_location": param_end_location,
                        "start_coords": start_coords,
                        "end_coords": end_coords,
                        "distance": distance,
                        "route": route,
                        "param_liter_km": param_liter_km,
                        "closest_fuel_price": closest_fuel_price,
                        "param_persons": param_persons,
                        "param_commission": param_commission,
                    }

                    self._render_cached_calculation()

                else:
                    st.error(
                        f"Could not find fuel price for {param_fuel_type} at selected stations"
                    )
    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
        return None

    # -----

    def _render_cached_calculation(self) -> None:
        """ Render the most recent calculation stored in session state """

        calculation_result = st.session_state.get("calculation_result")
        if not calculation_result:
            return None

        route = calculation_result["route"]

        self._display_success_results(route)

        self._display_alternative_routes(
            calculation_result["start_coords"],
            calculation_result["end_coords"],
            calculation_result["param_liter_km"],
            calculation_result["closest_fuel_price"],
            calculation_result["param_persons"],
            calculation_result["param_commission"],
        )

        self._display_section(
            param_start_location=calculation_result["start_location"],
            param_end_location=calculation_result["end_location"],
            param_distance_km=calculation_result["distance"],
            param_rutafem_price=route.total_cost,
            param_persons=calculation_result["param_persons"],
        )

        return None

    # -----

    def _display_success_results(self, param_route: Route) -> None:
        """ Display successful calculation results """

        if param_route.closest_station:
            st.info(
                f"Station la plus proche: **{param_route.closest_station['address']}** "
                f"({param_route.closest_station['distance_km']} km de votre point de départ)"
            )

        self._display_key_metrics(param_route)
        self._display_summary(param_route)
        self._display_cost_breakdown(param_route)

        return None

    # -----

    def _display_key_metrics(self, param_route: Route) -> None:
        """ Display distance, fuel price, and total cost """

        distance_col, fuel_col, total_col = st.columns(3)
        with distance_col:
            st.metric("Distance", f"{param_route.distance_km:.2f} km")

        with fuel_col:
            st.metric("Prix essence", f"€{param_route.fuel_price:.2f}/L")

        with total_col:
            st.metric("Coût Total", f"€{param_route.total_cost:.2f}")

    # -----

    def _display_summary(self, param_route: Route) -> None:
        """ Display data summary """

        st.subheader("Résumé des données")

        data_summary_col1, data_summary_col2 = st.columns(2)
        with data_summary_col1:
            st.write(f"**Distance:** {param_route.distance_km} km")
            st.write(f"**Prix essence:** €{param_route.fuel_price:.2f}/L")
            st.write(f"**Coût du carburant:** €{param_route.fuel_cost:.2f}")

        with data_summary_col2:
            st.write(f"**Péage:** €{param_route.toll_cost:.2f}")
            if param_route.has_toll:
                st.write("**Péage détecté:** Oui")
                st.write(f"**Nombre de péages:** {param_route.toll_count}")
            else:
                st.write("**Péage détecté:** Non")
                st.write("**Nombre de péages:** 0")

        return None

    # -----

    def _display_cost_breakdown(self, param_route: Route) -> None:
        """ Display cost breakdown """

        st.subheader("Répartition des coûts")

        cost_breakdown = {
            "Coût du carburant": param_route.fuel_cost,
            "Péage": param_route.toll_cost,
            "Total": param_route.total_cost
        }

        breakdown_col1, breakdown_col2 = st.columns(2)

        with breakdown_col1:
            for item, cost in cost_breakdown.items():
                st.write(f"{item}: **{cost:.2f}€**")

        with breakdown_col2:
            st.metric(
                "Coût par personne",
                f"{param_route.cost_per_person:.2f}€"
            )

        return None

    # -----

    def _display_alternative_routes(
        self,
        param_start_coords: tuple,
        param_end_coords: tuple,
        param_liter_km: float,
        param_fuel_price: float,
        param_persons: int,
        param_commission: bool,
    ) -> None:
        """ Fetch and display alternative routes comparison """

        try:
            route_calculator = RouteCalculator()
            routes: List[Route] = route_calculator.get_alternative_routes(
                param_start_coords=param_start_coords,
                param_end_coords=param_end_coords,
                param_liter_per_100km=param_liter_km,
                param_fuel_price_per_liter=param_fuel_price,
                param_persons=param_persons,
                param_commission=param_commission,
            )

            if not routes:
                return None

            st.subheader("Itinéraires alternatifs")
            st.caption("Comparaison des routes proposées par OSRM")

            labels = [
                f"Route {r.index}  —  {', '.join(r.tags) if r.tags else '—'}  —  {r.cost_per_person:.2f} €/pers"
                for r in routes
            ]

            selected_idx = st.radio(
                "Sélectionner un itinéraire",
                range(len(routes)),
                format_func=lambda i: labels[i]
            )

            r = routes[selected_idx]

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Distance", f"{r.distance_km} km")
            with col2:
                st.metric("Durée", f"{r.duration_min} min")
            with col3:
                st.metric("Péages", f"{r.toll_cost:.2f} €")
            with col4:
                st.metric("Par personne", f"{r.cost_per_person:.2f} €")

            with st.expander("Détail des coûts de cet itinéraire"):
                st.write(f"**Carburant :** {r.fuel_cost:.2f} €")
                st.write(f"**Péages :** {r.toll_cost:.2f} €")
                st.write(f"**Total :** {r.total_cost:.2f} €")
                st.write(f"**Par personne :** {r.cost_per_person:.2f} €")
                if r.tags:
                    st.info(f"Tags : {', '.join(r.tags)}")

        except Exception as e:
            st.warning(f"Impossible de calculer les itinéraires alternatifs : {str(e)}")

        return None
    
    # -----
    
    def _display_section(
        self,
        param_start_location: str,
        param_end_location: str,
        param_distance_km: float,
        param_rutafem_price: float,
        param_persons: int,
    ) -> None:
        """ Display eco comparison section """
        
        try:
            eco = EcoComparison()
            eco.display_section(
                start_location=param_start_location,
                end_location=param_end_location,
                distance_km=param_distance_km,
                rutafem_price=param_rutafem_price,
                persons=param_persons,
            )
        except Exception as e:
            st.warning(f"Could not display eco comparison: {str(e)}")
        
        return None