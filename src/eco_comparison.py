"""
eco_comparison.py
-----------------
Rutafem Eco + Train Comparison Module
Integrated into the group Streamlit project.

Drop this file next to calculation_generator_file.py
(or wherever your src/ lives) and call
    EcoComparison().display_section(start, end, distance_km)
after the cost breakdown in _display_success_results.
"""

import os
import pandas as pd
import streamlit as st
import random
from datetime import datetime, timedelta

# --------------------------------------------------
# FILE PATHS  (keep next to your existing CSVs)
# --------------------------------------------------

TGV_CSV_FILE = os.path.join(
    os.getcwd(),
    "data",
    "csv",
    "train_prices_tgv.csv"
)
INTERCITES_CSV_FILE = os.path.join(
    os.getcwd(),
    "data",
    "csv",
    "train_prices_intercites.csv"
)

TRAIN_EMISSION_KG_PER_KM = 0.02   # kg CO2 / km / passenger (ADEME average)

# --------------------------------------------------
# REALISTIC PRICE MULTIPLIERS (based on real SNCF pricing patterns)
# --------------------------------------------------

# Base price multipliers for different scenarios (applied to CSV median price)
DAY_MULTIPLIERS = {
    "Monday": 0.95,
    "Tuesday": 0.90,
    "Wednesday": 0.90,
    "Thursday": 1.00,
    "Friday": 1.15,
    "Saturday": 1.20,
    "Sunday": 1.25
}

# Seasonal multipliers (approximate)
SEASON_MULTIPLIERS = {
    "Winter": 1.0,      # Jan-Feb
    "Spring": 1.05,     # Mar-May
    "Summer": 1.30,     # Jun-Aug (peak season)
    "Autumn": 1.0,      # Sep-Nov
    "Holidays": 1.40    # Christmas/New Year
}

# Booking horizon multipliers (days before departure)
def get_booking_multiplier():
    """Simulate random booking horizon between 7-60 days"""
    days_before = random.randint(7, 60)
    if days_before > 30:
        return 0.85  # Early bird discount
    elif days_before > 14:
        return 1.0   # Normal price
    else:
        return 1.15  # Last minute premium

# High-demand route multipliers (popular routes)
HIGH_DEMAND_ROUTES = [
    ("paris", "lyon"),
    ("paris", "marseille"),
    ("paris", "bordeaux"),
    ("paris", "nice"),
    ("lyon", "marseille"),
    ("paris", "strasbourg"),
    ("paris", "rennes"),
    ("paris", "lille"),
    ("paris", "toulouse"),
]

# --------------------------------------------------
# VEHICLE CATALOGUE  (hardcoded — no external CSV needed)
# --------------------------------------------------

# co2_g_km values: WLTP combined cycle (g CO2 / km)
# Sources: manufacturer data / ADEME / Les Numériques
VEHICLE_CATALOGUE: list[dict] = [
    # --- Toyota ---
    {"make": "Toyota",   "model": "Prius Hybrid",    "co2_g_km": 92},
    {"make": "Toyota",   "model": "Corolla Hybrid",  "co2_g_km": 102},
    {"make": "Toyota",   "model": "Camry Hybrid",    "co2_g_km": 103},
    {"make": "Toyota",   "model": "Yaris Hybrid",    "co2_g_km": 92},
    {"make": "Toyota",   "model": "C-HR Hybrid",     "co2_g_km": 101},
    # --- Hyundai ---
    {"make": "Hyundai",  "model": "Ioniq Hybrid",    "co2_g_km": 98},
    {"make": "Hyundai",  "model": "Kona Hybrid",     "co2_g_km": 111},
    {"make": "Hyundai",  "model": "Ioniq Electric",  "co2_g_km": 0},
    {"make": "Hyundai",  "model": "Ioniq 6",         "co2_g_km": 0},
    # --- Kia ---
    {"make": "Kia",      "model": "Niro Hybrid",     "co2_g_km": 101},
    {"make": "Kia",      "model": "Niro EV",         "co2_g_km": 0},
    # --- Tesla ---
    {"make": "Tesla",    "model": "Model 3",         "co2_g_km": 0},
    {"make": "Tesla",    "model": "Model Y",         "co2_g_km": 0},
    # --- Renault ---
    {"make": "Renault",  "model": "Clio Diesel",     "co2_g_km": 101},
    {"make": "Renault",  "model": "Clio E-Tech Hybrid", "co2_g_km": 96},
    {"make": "Renault",  "model": "Zoe",             "co2_g_km": 0},
    {"make": "Renault",  "model": "Megane Diesel",   "co2_g_km": 115},
    # --- Peugeot ---
    {"make": "Peugeot",  "model": "208 Diesel",      "co2_g_km": 99},
    {"make": "Peugeot",  "model": "308 Diesel",      "co2_g_km": 112},
    {"make": "Peugeot",  "model": "508 Diesel",      "co2_g_km": 118},
    {"make": "Peugeot",  "model": "e-208",           "co2_g_km": 0},
    # --- Citroën ---
    {"make": "Citroën",  "model": "C4 Diesel",       "co2_g_km": 116},
    {"make": "Citroën",  "model": "e-C4",            "co2_g_km": 0},
    # --- Skoda ---
    {"make": "Skoda",    "model": "Octavia Diesel",  "co2_g_km": 113},
    {"make": "Skoda",    "model": "Superb Diesel",   "co2_g_km": 121},
    {"make": "Skoda",    "model": "Enyaq",           "co2_g_km": 0},
    # --- Volkswagen ---
    {"make": "Volkswagen", "model": "Golf Diesel",   "co2_g_km": 112},
    {"make": "Volkswagen", "model": "Passat Diesel", "co2_g_km": 120},
    {"make": "Volkswagen", "model": "ID.3",          "co2_g_km": 0},
    {"make": "Volkswagen", "model": "ID.4",          "co2_g_km": 0},
    # --- Ford ---
    {"make": "Ford",     "model": "Focus Diesel",    "co2_g_km": 111},
    {"make": "Ford",     "model": "Mondeo Hybrid",   "co2_g_km": 119},
    {"make": "Ford",     "model": "Mustang Mach-E",  "co2_g_km": 0},
    # --- BMW ---
    {"make": "BMW",      "model": "320d Diesel",     "co2_g_km": 122},
    {"make": "BMW",      "model": "i3",              "co2_g_km": 0},
    # --- Mercedes ---
    {"make": "Mercedes", "model": "C-Class Diesel",  "co2_g_km": 128},
    {"make": "Mercedes", "model": "E-Class Diesel",  "co2_g_km": 132},
    {"make": "Mercedes", "model": "EQA",             "co2_g_km": 0},
    # --- Nissan ---
    {"make": "Nissan",   "model": "Leaf",            "co2_g_km": 0},
    # --- Dacia ---
    {"make": "Dacia",    "model": "Logan Diesel",    "co2_g_km": 104},
    {"make": "Dacia",    "model": "Sandero Diesel",  "co2_g_km": 101},
]

# Build a flat display list: "Make — Model"
VEHICLE_OPTIONS: list[str] = [
    f"{v['make']} — {v['model']}" for v in VEHICLE_CATALOGUE
]

# --------------------------------------------------
# TRAIN PRICE HELPERS WITH ENHANCED CALCULATION
# --------------------------------------------------

@st.cache_data(show_spinner=False)
def _load_train_prices() -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    """Load TGV and Intercités CSV datasets separately (cached)."""
    try:
        df_tgv = pd.read_csv(TGV_CSV_FILE, sep=";")
    except Exception:
        df_tgv = None
    try:
        df_inter = pd.read_csv(INTERCITES_CSV_FILE, sep=";")
        if "Type de place" in df_inter.columns:
            df_inter = df_inter.drop(columns=["Type de place"])
    except Exception:
        df_inter = None
    return df_tgv, df_inter

def _get_current_season() -> str:
    """Determine current season based on date"""
    now = datetime.now()
    month = now.month
    
    # Check for holiday period (Dec 20 - Jan 5)
    if (now.month == 12 and now.day >= 20) or (now.month == 1 and now.day <= 5):
        return "Holidays"
    
    if month in [1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Autumn"

def _get_day_multiplier() -> float:
    """Get multiplier based on current day of week"""
    today = datetime.now().strftime("%A")
    return DAY_MULTIPLIERS.get(today, 1.0)

def _is_high_demand_route(origin: str, destination: str) -> bool:
    """Check if route is typically high demand"""
    origin_lower = origin.lower().strip()
    dest_lower = destination.lower().strip()
    
    for (o, d) in HIGH_DEMAND_ROUTES:
        if (origin_lower in o and dest_lower in d) or (origin_lower in d and dest_lower in o):
            return True
    return False

def _get_train_price_range_enhanced(
    df_tgv: pd.DataFrame | None,
    df_inter: pd.DataFrame | None,
    origin: str,
    destination: str,
) -> tuple[float | None, float | None, str]:
    """
    Return (min_price, max_price, source_label) for a route with realistic pricing.
    
    Now calculates a range from lowest possible (early bird, off-peak) to
    highest possible (last minute, peak season, weekend).
    """
    origin = origin.lower().strip()
    destination = destination.lower().strip()

    def _search(df: pd.DataFrame, tariff_filter: str | None, class_filter: int | None):
        mask = (
            df["Gare origine"].astype(str).str.lower().str.contains(origin, na=False) &
            df["Gare destination"].astype(str).str.lower().str.contains(destination, na=False)
        )
        if tariff_filter:
            mask &= df["Profil tarifaire"].astype(str) == tariff_filter
        if class_filter is not None:
            mask &= df["Classe"] == class_filter
        return df[mask]

    def _compute_base_price(rows: pd.DataFrame) -> tuple[float, float]:
        """Get base min and max from CSV"""
        base_min = rows["Prix minimum"].median()
        base_max = rows["Prix maximum"].median()
        return base_min, base_max

    # Search for relevant rows
    base_min = None
    base_max = None
    source_label = ""
    
    # 1 — TGV, Tarif Normal, 2nd class (preferred)
    if df_tgv is not None:
        rows = _search(df_tgv, "Tarif Normal", 2)
        if not rows.empty:
            base_min, base_max = _compute_base_price(rows)
            source_label = "TGV · 2nd class · Tarif Normal"

    # 2 — Intercités, Tarif Normal
    if (base_min is None) and df_inter is not None:
        rows = _search(df_inter, "Tarif Normal", None)
        if not rows.empty:
            base_min, base_max = _compute_base_price(rows)
            source_label = "Intercités · Tarif Normal"

    # 3 — Any tariff/class (last resort)
    if base_min is None:
        for df, label in [(df_tgv, "TGV"), (df_inter, "Intercités")]:
            if df is None:
                continue
            rows = _search(df, None, None)
            if not rows.empty:
                base_min, base_max = _compute_base_price(rows)
                source_label = f"{label} · tous tarifs"
                break

    if base_min is None:
        return None, None, ""

    # Apply realistic pricing multipliers to create a realistic range
    current_day_mult = _get_day_multiplier()
    current_season = _get_current_season()
    season_mult = SEASON_MULTIPLIERS.get(current_season, 1.0)
    
    # High demand route multiplier
    demand_mult = 1.15 if _is_high_demand_route(origin, destination) else 1.0
    
    # Calculate range
    # Lowest price: early bird + off-peak day + off-season
    min_multiplier = 0.85 * 0.90 * 1.0  # early bird (0.85) * off-peak day (0.90) * no demand premium
    
    # Highest price: last minute + peak day + peak season + high demand
    max_multiplier = 1.15 * 1.25 * season_mult * demand_mult
    
    final_min = round(base_min * min_multiplier, 0)
    final_max = round(base_max * max_multiplier, 0)
    
    # Ensure range makes sense (min shouldn't be higher than max)
    if final_min > final_max:
        final_min, final_max = final_max, final_min
    
    # Add a note about the pricing logic
    note = f"Estimation based on {current_season.lower()} season, {datetime.now().strftime('%A')}"
    
    return final_min, final_max, f"{source_label} · {note}"

# Keep old function for backward compatibility
def _get_train_price_range(
    df_tgv: pd.DataFrame | None,
    df_inter: pd.DataFrame | None,
    origin: str,
    destination: str,
) -> tuple[float | None, float | None, str]:
    """Legacy function - now calls enhanced version"""
    return _get_train_price_range_enhanced(df_tgv, df_inter, origin, destination)

# --------------------------------------------------
# CO2 HELPERS
# --------------------------------------------------

def _get_vehicle_co2_kg_km(vehicle_label: str) -> float:
    """Return CO2 in kg/km for the selected vehicle label."""
    for v in VEHICLE_CATALOGUE:
        label = f"{v['make']} — {v['model']}"
        if label == vehicle_label:
            return v["co2_g_km"] / 1000.0
    return 0.0

def _car_co2(distance_km: float, passengers: int, co2_kg_km: float) -> tuple[float, float]:
    total = round(distance_km * co2_kg_km, 2)
    per_pp = round(total / max(passengers, 1), 2)
    return total, per_pp

def _train_co2(distance_km: float, passengers: int) -> tuple[float, float]:
    total = round(distance_km * TRAIN_EMISSION_KG_PER_KM, 2)
    per_pp = round(total / max(passengers, 1), 2)
    return total, per_pp

# --------------------------------------------------
# PUBLIC API  — call this from StreamlitCalculationGenerator
# --------------------------------------------------

class EcoComparison:
    """
    Displays the Eco & Train Comparison section inside the existing
    Streamlit app.  Call display_section() after the cost breakdown.
    """

    def display_section(
        self,
        start_location: str,
        end_location:   str,
        distance_km:    float,
        rutafem_price:  float,
        persons:        int,
    ) -> None:
        """
        Render the full eco+train comparison block.

        Parameters
        ----------
        start_location : str   — already captured by the group form
        end_location   : str   — already captured by the group form
        distance_km    : float — computed by OSRM in the group project
        rutafem_price  : float — total cost computed by the group project
        persons        : int   — number of passengers
        """

        st.divider()
        st.subheader("🌿 Eco & Train Comparison")

        # ---- Vehicle selector ----
        selected_vehicle = st.selectbox(
            "Select vehicle (for CO₂ estimation)",
            options=VEHICLE_OPTIONS,
            index=0,
            help="Choose the car model used for the ride to compare carbon footprint with train."
        )

        co2_kg_km = _get_vehicle_co2_kg_km(selected_vehicle)
        is_electric = co2_kg_km == 0.0

        # ---- Train price lookup with enhanced realistic pricing ----
        df_tgv, df_inter = _load_train_prices()
        train_min:   float | None = None
        train_max:   float | None = None
        train_source:  str = ""
        train_note:    str = ""

        if df_tgv is None and df_inter is None:
            train_note = "Train CSV files not found — add train_prices_tgv.csv and train_prices_intercites.csv."
        else:
            train_min, train_max, train_source = _get_train_price_range_enhanced(
                df_tgv, df_inter, start_location, end_location
            )
            if train_min is None:
                train_note = "Route not found in train dataset."

        # ======================================================
        # PRICE COMPARISON
        # ======================================================
        st.markdown("#### 💶 Price Comparison")

        rutafem_per_person = round(rutafem_price / max(persons, 1), 2)

        price_col1, price_col2, price_col3 = st.columns(3)

        with price_col1:
            st.metric(
                label="🚗 Rutafem (per person)",
                value=f"{rutafem_per_person:.2f} €",
                help=f"Total {rutafem_price:.2f} € ÷ {persons} passenger(s)."
            )
            st.caption(f"Total ride: **{rutafem_price:.2f} €**")

        with price_col2:
            if train_min is not None:
                st.metric(
                    label="🚄 Train (realistic range)",
                    value=f"{train_min:.0f} – {train_max:.0f} €",
                    help="Price range based on season, day of week, and booking horizon. Real prices typically fall in this range."
                )
                st.caption(f"Source: {train_source}")
            else:
                st.metric(label="🚄 Train", value="N/A")
                st.caption(train_note)

        with price_col3:
            if train_min is not None:
                # Compare Rutafem against the realistic train range
                if rutafem_per_person < train_min:
                    verdict = "🚗 Rutafem"
                    detail = f"cheaper than lowest train price ({train_min:.0f} €)"
                    best_value = "car"
                elif rutafem_per_person <= train_max:
                    # Check if it's in the lower or upper part of the range
                    mid_point = (train_min + train_max) / 2
                    if rutafem_per_person <= mid_point:
                        verdict = "≈ Competitive"
                        detail = f"Rutafem {rutafem_per_person:.2f} € is in lower half of train range"
                        best_value = "similar"
                    else:
                        verdict = "🚄 Train likely"
                        detail = f"Train can be cheaper than Rutafem ({rutafem_per_person:.2f} €)"
                        best_value = "train"
                else:
                    verdict = "🚄 Train"
                    detail = f"Train max price ({train_max:.0f} €) is lower than Rutafem"
                    best_value = "train"
                
                st.metric(label="✅ Best value", value=verdict)
                st.caption(detail)
            else:
                st.metric(label="✅ Best value", value="🚗 Rutafem")
                st.caption("No train data to compare.")
                best_value = "car"

        # ======================================================
        # CO2 COMPARISON
        # ======================================================
        st.markdown("#### 🌍 Carbon Footprint")

        car_total_co2, car_pp_co2 = _car_co2(distance_km, persons, co2_kg_km)
        train_total_co2, train_pp_co2 = _train_co2(distance_km, persons)

        co2_col1, co2_col2 = st.columns(2)

        with co2_col1:
            st.markdown(f"**🚗 {selected_vehicle}**")
            if is_electric:
                st.info("⚡ Electric vehicle — 0 g CO₂/km (tailpipe). "
                        "Well-to-wheel emissions depend on the energy mix.")
                st.metric("Total CO₂ (tailpipe)", "0.00 kg")
                st.metric("Per passenger (tailpipe)", "0.00 kg")
            else:
                st.metric("Total CO₂", f"{car_total_co2:.2f} kg")
                st.metric("Per passenger", f"{car_pp_co2:.2f} kg")

        with co2_col2:
            st.markdown("**🚄 Train (ADEME avg)**")
            st.metric("Total CO₂", f"{train_total_co2:.2f} kg")
            st.metric("Per passenger", f"{train_pp_co2:.2f} kg")

        # Logic for the return dictionary
        cheapest_option = best_value if train_min is not None else "car"

        return {
            "co2_car_total_kg":        car_total_co2,
            "co2_car_per_person_kg":   car_pp_co2,
            "co2_train_total_kg":      train_total_co2,
            "co2_train_per_person_kg": train_pp_co2,
            "train_price":             train_max if train_max is not None else 0.0,
            "ouigo_price":             train_min if train_min is not None else 0.0,
            "cheapest_option":         cheapest_option,
        }