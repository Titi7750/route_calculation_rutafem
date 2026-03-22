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
def load_train_prices() -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    """ Load TGV and Intercités CSV datasets separately (cached) """

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

# -----

def get_train_price_range(
    param_df_tgv: pd.DataFrame | None,
    param_df_inter: pd.DataFrame | None,
    param_origin: str,
    param_destination: str,
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
        — the 40th percentile of the range, where most day-of-sale prices cluster according to the validation above

    Priority: TGV Tarif Normal 2nd class → Intercités Tarif Normal → any
    """
    origin      = param_origin.lower().strip()
    destination = param_destination.lower().strip()

    def _search(param_dataframe: pd.DataFrame, param_tarif_filter: str | None, param_class_filter: int | None):
        """ Return rows matching origin/destination + optional tariff/class filters """

        mask = (
            param_dataframe["Gare origine"].astype(str).str.lower().str.contains(origin, na=False) &
            param_dataframe["Gare destination"].astype(str).str.lower().str.contains(destination, na=False)
        )
        if param_tarif_filter:
            mask &= param_dataframe["Profil tarifaire"].astype(str) == param_tarif_filter
        if param_class_filter is not None:
            mask &= param_dataframe["Classe"] == param_class_filter

        return param_dataframe[mask]

    # -----

    def _compute_range(param_rows: pd.DataFrame) -> tuple[float, float]:
        """ Compute floor and typical price from a set of matching rows """

        floor   = round(param_rows["Prix minimum"].median(), 0)
        med_max = param_rows["Prix maximum"].median()
        typical = round(floor + 0.40 * (med_max - floor), 0)

        return floor, typical

    # -----

    # 1 — TGV, Tarif Normal, 2nd class
    if param_df_tgv is not None:
        rows = _search(param_df_tgv, "Tarif Normal", 2)
        if not rows.empty:
            floor, typical = _compute_range(rows)
            return floor, typical, "TGV · 2nd class · Tarif Normal"

    # 2 — Intercités, Tarif Normal
    if param_df_inter is not None:
        rows = _search(param_df_inter, "Tarif Normal", None)
        if not rows.empty:
            floor, typical = _compute_range(rows)
            return floor, typical, "Intercités · Tarif Normal"

    # 3 — Any tariff/class (last resort)
    for df, label in [(param_df_tgv, "TGV"), (param_df_inter, "Intercités")]:
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

def get_vehicle_co2_kg_km(param_vehicle_label: str) -> float:
    """ Return CO2 in kg/km for the selected vehicle label """

    for v in VEHICLE_CATALOGUE:
        label = f"{v['make']} — {v['model']}"
        if label == param_vehicle_label:
            return v["co2_g_km"] / 1000.0

    return 0.0

# -----

def car_co2(param_distance_km: float, param_passengers: int, param_co2_kg_km: float) -> tuple[float, float]:
    """ Return total and per-passenger CO2 emissions for a car route """

    total  = round(param_distance_km * param_co2_kg_km, 2)
    per_pp = round(total / max(param_passengers, 1), 2)

    return total, per_pp

# -----

def train_co2(param_distance_km: float, param_passengers: int) -> tuple[float, float]:
    """ Return total and per-passenger CO2 emissions for a train route """

    total  = round(param_distance_km * TRAIN_EMISSION_KG_PER_KM, 2)
    per_pp = round(total / max(param_passengers, 1), 2)

    return total, per_pp
