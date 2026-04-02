"""
push_to_supabase.py
===================
Run this script MANUALLY whenever you want to push rutafem_runs.csv to Supabase.

Usage:
    python push_to_supabase.py
    python push_to_supabase.py --csv path/to/rutafem_runs.csv   # custom path

Requirements:
    pip install supabase python-dotenv

.env file (same folder as this script):
    SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
    SUPABASE_KEY=your-service-role-key
"""

import argparse
import csv
import os
from datetime import date, datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# Connect
# ─────────────────────────────────────────────────────────────────────────────

def get_client():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        raise EnvironmentError(
            "Missing SUPABASE_URL or SUPABASE_KEY in your .env file."
        )
    return create_client(url, key)


# ─────────────────────────────────────────────────────────────────────────────
# Push one CSV row into all 6 tables (FK-safe order)
# ─────────────────────────────────────────────────────────────────────────────

def push_row(db, row: dict) -> dict:
    """
    Inserts one CSV row into Supabase in FK-safe order:
        routes → trips → tolls / fuel_prices / co2_results / price_comparison
    Returns a dict of {table: inserted_id}.
    """

    def f(key):   # safe float
        try: return float(row.get(key) or 0)
        except: return 0.0

    def i(key):   # safe int
        try: return int(row.get(key) or 0)
        except: return 0

    today = date.today().isoformat()

    # 1. routes ───────────────────────────────────────────────────────────────
    r = db.table("routes").insert({
        "origin_city":      row.get("origin_city", ""),
        "destination_city": row.get("destination_city", ""),
        "distance_km":      f("distance_km"),
    }).execute()
    route_id = r.data[0]["id"]

    # 2. trips ────────────────────────────────────────────────────────────────
    t = db.table("trips").insert({
        "route_id":      route_id,
        "passengers":    i("passengers"),
        "rutafem_price": f("rutafem_price"),
        "travel_date":   row.get("travel_date") or today,
        "vehicle_id":    None,
    }).execute()
    trip_id = t.data[0]["id"]

    # 3. tolls ────────────────────────────────────────────────────────────────
    tl = db.table("tolls").insert({
        "route_id": route_id,
        "price":    f("toll_price"),
    }).execute()

    # 4. fuel_prices ──────────────────────────────────────────────────────────
    fp = db.table("fuel_prices").insert({
        "fuel_type":       row.get("fuel_type", ""),
        "price_per_liter": f("price_per_liter"),
        "date":            row.get("fuel_date") or today,
    }).execute()

    # 5. co2_results ──────────────────────────────────────────────────────────
    co2 = db.table("co2_results").insert({
        "trip_id":          trip_id,
        "car_total":        f("co2_car_total_kg"),
        "car_per_person":   f("co2_car_per_person_kg"),
        "train_total":      f("co2_train_total_kg"),
        "train_per_person": f("co2_train_per_person_kg"),
    }).execute()

    # 6. price_comparison ─────────────────────────────────────────────────────
    pc = db.table("price_comparison").insert({
        "trip_id":         trip_id,
        "rutafem_price":   f("rutafem_price"),
        "train_price":     f("train_price"),
        "ouigo_price":     f("ouigo_price"),
        "cheapest_option": row.get("cheapest_option", ""),
    }).execute()

    return {
        "routes":            route_id,
        "trips":             trip_id,
        "tolls":             tl.data[0]["id"],
        "fuel_prices":       fp.data[0]["id"],
        "co2_results":       co2.data[0]["id"],
        "price_comparison":  pc.data[0]["id"],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Push rutafem_runs.csv → Supabase")
    parser.add_argument(
        "--csv",
        default="rutafem_runs.csv",
        help="Path to the CSV (default: rutafem_runs.csv)",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.csv):
        print(f"❌  File not found: {args.csv}")
        return

    db = get_client()
    print(f"\n📂  Reading {args.csv} …\n")

    success = 0
    errors  = 0

    with open(args.csv, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    print(f"   {len(rows)} row(s) found.\n")

    for idx, row in enumerate(rows, 1):
        origin = row.get("origin_city", "?")
        dest   = row.get("destination_city", "?")
        try:
            ids = push_row(db, row)
            print(
                f"  ✅  [{idx}/{len(rows)}]  {origin} → {dest}  |  "
                f"route={ids['routes']}  trip={ids['trips']}"
            )
            success += 1
        except Exception as e:
            print(f"  ❌  [{idx}/{len(rows)}]  {origin} → {dest}  |  ERROR: {e}")
            errors += 1

    print(f"\n{'─'*55}")
    print(f"  Done.  {success} pushed  |  {errors} failed\n")


if __name__ == "__main__":
    main()