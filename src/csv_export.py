"""
csv_export.py — Rutafem CSV Export Module
Generates a clean, Supabase-ready CSV after each route calculation run.

Tables covered (one sheet per table):
    routes, trips, tolls, fuel_prices, co2_results, price_comparison

Usage (inside streamlit_interface.py):
    from src.csv_export import RutafemCSVExporter
    exporter = RutafemCSVExporter()
    exporter.export_run(run_data)          # writes CSV to disk
    exporter.offer_download(run_data)      # also shows st.download_button
"""

from __future__ import annotations

import csv
import io
import os
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
# Data container – fill this from _calculate_and_display_route()
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class RunData:
    """
    One complete calculation run.  Pass every value you already compute
    inside _calculate_and_display_route(); leave unknowns as None.
    """

    # ── Route ─────────────────────────────────────────────────────────────
    origin_city: str = ""
    destination_city: str = ""
    distance_km: float = 0.0

    # ── Trip ──────────────────────────────────────────────────────────────
    passengers: int = 1
    rutafem_price: float = 0.0          # total cost (all persons)
    travel_date: Optional[date] = None

    # ── Fuel ──────────────────────────────────────────────────────────────
    fuel_type: str = ""
    price_per_liter: float = 0.0
    fuel_consumption_l_100: float = 0.0  # sidebar slider value

    # ── Tolls ─────────────────────────────────────────────────────────────
    toll_price: float = 0.0

    # ── CO2 ───────────────────────────────────────────────────────────────
    co2_car_total_kg: float = 0.0
    co2_car_per_person_kg: float = 0.0
    co2_train_total_kg: float = 0.0
    co2_train_per_person_kg: float = 0.0

    # ── Price comparison ──────────────────────────────────────────────────
    train_price: float = 0.0
    ouigo_price: float = 0.0
    cheapest_option: str = ""           # e.g. "car", "train", "ouigo"

    # ── Meta ──────────────────────────────────────────────────────────────
    run_ts: datetime = field(default_factory=datetime.utcnow)


# ─────────────────────────────────────────────────────────────────────────────
# Column definitions (maps 1-to-1 with Supabase tables)
# ─────────────────────────────────────────────────────────────────────────────

_COLUMNS = {
    # ── routes ──────────────────────────────────────────────────────────
    "origin_city": "routes.origin_city",
    "destination_city": "routes.destination_city",
    "distance_km": "routes.distance_km",
    "routes_created_at": "routes.created_at",

    # ── trips ────────────────────────────────────────────────────────────
    "passengers": "trips.passengers",
    "rutafem_price": "trips.rutafem_price",
    "travel_date": "trips.travel_date",

    # ── tolls ────────────────────────────────────────────────────────────
    "toll_price": "tolls.price",

    # ── fuel_prices ──────────────────────────────────────────────────────
    "fuel_type": "fuel_prices.fuel_type",
    "price_per_liter": "fuel_prices.price_per_liter",
    "fuel_date": "fuel_prices.date",

    # ── co2_results ──────────────────────────────────────────────────────
    "co2_car_total_kg": "co2_results.car_total",
    "co2_car_per_person_kg": "co2_results.car_per_person",
    "co2_train_total_kg": "co2_results.train_total",
    "co2_train_per_person_kg": "co2_results.train_per_person",

    # ── price_comparison ─────────────────────────────────────────────────
    "train_price": "price_comparison.train_price",
    "ouigo_price": "price_comparison.ouigo_price",
    "cheapest_option": "price_comparison.cheapest_option",

    # ── extra ────────────────────────────────────────────────────────────
    "run_timestamp": "meta.run_timestamp",
}

# Human-friendly CSV headers (same order, no table prefix)
_HEADERS = [
    "origin_city",
    "destination_city",
    "distance_km",
    "routes_created_at",
    "passengers",
    "rutafem_price",
    "travel_date",
    "toll_price",
    "fuel_type",
    "price_per_liter",
    "fuel_date",
    "co2_car_total_kg",
    "co2_car_per_person_kg",
    "co2_train_total_kg",
    "co2_train_per_person_kg",
    "train_price",
    "ouigo_price",
    "cheapest_option",
    "run_timestamp",
]


# ─────────────────────────────────────────────────────────────────────────────
# Exporter
# ─────────────────────────────────────────────────────────────────────────────

class RutafemCSVExporter:
    """
    Converts a RunData instance into a single-row CSV and
    appends it to `output_path` (one file, multiple runs).
    """

    def __init__(self, output_path: str = "rutafem_runs.csv"):
        self.output_path = output_path

    # ── public API ────────────────────────────────────────────────────────

    def export_run(self, run: RunData) -> str:
        """
        Append `run` as a new row to `self.output_path`.
        Creates the file + header row on first call.
        Returns the absolute path of the CSV file.
        """
        row = self._build_row(run)
        file_exists = os.path.isfile(self.output_path)

        with open(self.output_path, "a", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=_HEADERS)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

        return os.path.abspath(self.output_path)

    def offer_download(self, run: RunData) -> None:
        """
        Appends the run to disk AND renders a Streamlit download button
        so the user can grab the whole CSV in-browser.
        """
        abs_path = self.export_run(run)

        # Read back the full file for the download button
        with open(abs_path, "rb") as fh:
            csv_bytes = fh.read()

        st.download_button(
            label="⬇️  Télécharger le CSV (tous les trajets)",
            data=csv_bytes,
            file_name="rutafem_runs.csv",
            mime="text/csv",
            help="CSV formaté pour import direct dans Supabase",
        )

    def to_bytes(self, run: RunData) -> bytes:
        """
        Return a single-run CSV as raw bytes (useful for tests or
        custom upload logic without touching disk).
        """
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=_HEADERS)
        writer.writeheader()
        writer.writerow(self._build_row(run))
        return buf.getvalue().encode("utf-8")

    # ── internals ─────────────────────────────────────────────────────────

    @staticmethod
    def _build_row(run: RunData) -> dict:
        today = date.today().isoformat()
        return {
            "origin_city":           run.origin_city,
            "destination_city":      run.destination_city,
            "distance_km":           round(run.distance_km, 4),
            "routes_created_at":     run.run_ts.isoformat(timespec="seconds"),
            "passengers":            run.passengers,
            "rutafem_price":         round(run.rutafem_price, 4),
            "travel_date":           run.travel_date.isoformat() if run.travel_date else today,
            "toll_price":            round(run.toll_price, 4),
            "fuel_type":             run.fuel_type,
            "price_per_liter":       round(run.price_per_liter, 4),
            "fuel_date":             today,
            "co2_car_total_kg":      round(run.co2_car_total_kg, 4),
            "co2_car_per_person_kg": round(run.co2_car_per_person_kg, 4),
            "co2_train_total_kg":    round(run.co2_train_total_kg, 4),
            "co2_train_per_person_kg": round(run.co2_train_per_person_kg, 4),
            "train_price":           round(run.train_price, 4),
            "ouigo_price":           round(run.ouigo_price, 4),
            "cheapest_option":       run.cheapest_option,
            "run_timestamp":         run.run_ts.isoformat(timespec="seconds"),
        }
