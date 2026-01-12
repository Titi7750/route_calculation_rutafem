import streamlit as st

from src.routing import geocode_address, get_route_osrm
from src.tolls_file import estimate_route_toll


st.set_page_config(page_title="Détection des péages (OSRM)", layout="centered")

st.title(" Détection des péages – OSRM")

departure = st.text_input("Adresse de départ", "Paris, France")
arrival = st.text_input("Adresse d’arrivée", "Lyon, France")

if st.button("Calculer"):
    try:
        with st.spinner("Calcul de l'itinéraire..."):
            origin = geocode_address(departure)
            destination = geocode_address(arrival)
            osrm_data = get_route_osrm(origin, destination)

            path = osrm_data["routes"][0]
            distance_km = round(path["distance"] / 1000, 1)
            duration_min = round(path["duration"] / 60)

            toll_info = estimate_route_toll(osrm_data)

        st.success("Calcul terminé")

        st.subheader("Résultat")
        st.write(f"**Distance totale :** {distance_km} km")
        st.write(f"**Péage :** {'Oui' if toll_info['has_toll'] else 'Non'}")
        st.write(f"**Coût estimé :** {toll_info['toll_cost']} €")

        if toll_info["segments"]:
            st.subheader("Autoroutes détectées")
            for seg in toll_info["segments"]:
                st.write(f"• {seg['motorway']} — {seg['distance_km']} km")

    except Exception as e:
        st.error(str(e))
