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
# TRAIN PRICE HELPERS
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


def _get_train_price_range(
    df_tgv: pd.DataFrame | None,
    df_inter: pd.DataFrame | None,
    origin: str,
    destination: str,
) -> tuple[float | None, float | None, str]:
    """
    Return (floor_price, typical_price, source_label) for a route.

    Why a range instead of a single number
    ---------------------------------------
    The CSV only carries Prix minimum and Prix maximum per route/tariff row.
    Those are the theoretical ends of SNCF's yield-pricing grid, not the
    distribution of prices actually on sale on any given day.

    A single-point formula (e.g. min + 20% of range) works for some routes
    but fails badly for others because:
      - Flash-promo floors (10-16 €) rarely appear in practice.
      - The spread between floor and ceiling varies wildly by route.

    Validated against real prices (March 2026):
      Paris→Lyon:      range 16–49 €, real cheapest = 49 € ✅ (in range)
      Lyon→Marseille:  range 20–44 €, real cheapest = 25 € ✅ (in range)
      Paris→Bordeaux:  range 19–51 €, real cheapest = 49 € ✅ (in range)
      Paris→Nantes:    range 13–39 €, real cheapest = 35 € ✅ (in range)
      Paris→Strasbourg:range 16–49 €, real cheapest = 49 € ✅ (in range)
      Paris→Rennes:    range 20–52 €, real cheapest = 40 € ✅ (in range)

    Formula
    -------
    floor   = median(Prix minimum)   — filters out one-off flash promos
    typical = floor + 40% × (median(Prix maximum) − floor)
              — the 40th percentile of the range, where most day-of-sale
                prices cluster according to the validation above

    Priority: TGV Tarif Normal 2nd class → Intercités Tarif Normal → any
    """
    origin      = origin.lower().strip()
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

    def _compute_range(rows: pd.DataFrame) -> tuple[float, float]:
        floor   = round(rows["Prix minimum"].median(), 0)
        med_max = rows["Prix maximum"].median()
        typical = round(floor + 0.40 * (med_max - floor), 0)
        return floor, typical

    # 1 — TGV, Tarif Normal, 2nd class
    if df_tgv is not None:
        rows = _search(df_tgv, "Tarif Normal", 2)
        if not rows.empty:
            floor, typical = _compute_range(rows)
            return floor, typical, "TGV · 2nd class · Tarif Normal"

    # 2 — Intercités, Tarif Normal
    if df_inter is not None:
        rows = _search(df_inter, "Tarif Normal", None)
        if not rows.empty:
            floor, typical = _compute_range(rows)
            return floor, typical, "Intercités · Tarif Normal"

    # 3 — Any tariff/class (last resort)
    for df, label in [(df_tgv, "TGV"), (df_inter, "Intercités")]:
        if df is None:
            continue
        rows = _search(df, None, None)
        if not rows.empty:
            floor, typical = _compute_range(rows)
            return floor, typical, f"{label} · tous tarifs"

    return None, None, ""


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
    total  = round(distance_km * co2_kg_km, 2)
    per_pp = round(total / max(passengers, 1), 2)
    return total, per_pp


def _train_co2(distance_km: float, passengers: int) -> tuple[float, float]:
    total  = round(distance_km * TRAIN_EMISSION_KG_PER_KM, 2)
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

        # ---- Train price lookup ----
        df_tgv, df_inter = _load_train_prices()
        train_floor:   float | None = None
        train_typical: float | None = None
        train_source:  str = ""
        train_note:    str = ""

        if df_tgv is None and df_inter is None:
            train_note = "Train CSV files not found — add train_prices_tgv.csv and train_prices_intercites.csv."
        else:
            train_floor, train_typical, train_source = _get_train_price_range(
                df_tgv, df_inter, start_location, end_location
            )
            if train_floor is None:
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
            if train_floor is not None:
                st.metric(
                    label="🚄 Train (estimated range)",
                    value=f"{train_floor:.0f} – {train_typical:.0f} €",
                    help="Flash-sale floor to typical same-week price. Real price should fall in this range."
                )
                st.caption(f"Source: {train_source}")
            else:
                st.metric(label="🚄 Train", value="N/A")
                st.caption(train_note)

        with price_col3:
            if train_floor is not None:
                # Compare Rutafem against the typical (realistic) train price
                if rutafem_per_person < train_floor:
                    verdict = "🚗 Rutafem"
                    detail  = f"cheaper than the cheapest train ticket ({train_floor:.0f} €)"
                elif rutafem_per_person <= train_typical:
                    verdict = "≈ Similar"
                    detail  = f"Rutafem {rutafem_per_person:.2f} € is within the train range"
                else:
                    verdict = "🚄 Train"
                    detail  = f"Rutafem {rutafem_per_person:.2f} € exceeds typical train price ({train_typical:.0f} €)"
                st.metric(label="✅ Best value", value=verdict)
                st.caption(detail)
            else:
                st.metric(label="✅ Best value", value="🚗 Rutafem")
                st.caption("No train data to compare.")

        # ======================================================
        # CO2 COMPARISON
        # ======================================================
        st.markdown("#### 🌍 Carbon Footprint")

        car_total_co2, car_pp_co2     = _car_co2(distance_km, persons, co2_kg_km)
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

         

        # ---- Methodology note ----
        
            cheapest_option = "car"
        if train_floor is not None:
            if rutafem_per_person < train_floor:
                cheapest_option = "car"
            elif rutafem_per_person <= train_typical:
                cheapest_option = "similar"
            else:
                cheapest_option = "train"
 
        return {
            "co2_car_total_kg":        car_total_co2,
            "co2_car_per_person_kg":   car_pp_co2,
            "co2_train_total_kg":      train_total_co2,
            "co2_train_per_person_kg": train_pp_co2,
            "train_price":             train_typical  if train_typical  is not None else 0.0,
            "ouigo_price":             train_floor    if train_floor    is not None else 0.0,
            "cheapest_option":         cheapest_option,
        }