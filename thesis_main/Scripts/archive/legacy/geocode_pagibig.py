"""
geocode_pagibig.py
------------------
Geocodes Metro Cebu Pag-IBIG properties using the Google Maps Geocoding API.
Deduplicates by project name so each unique project is only geocoded once.

Requires: pip install googlemaps python-dotenv
API key:  thesis_main/.env  →  GOOGLE_MAPS_API_KEY=...

Output: Data/processed/floor_price/pagibig_geocoded.csv
"""

import os
import re
import time
import pandas as pd
import googlemaps
from dotenv import load_dotenv

# ── Load API key ───────────────────────────────────────────────────────────────
load_dotenv(os.path.join("thesis_main", ".env"))
API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")
if not API_KEY:
    raise RuntimeError("GOOGLE_MAPS_API_KEY not found. Check thesis_main/.env")

gmaps = googlemaps.Client(key=API_KEY)

# ── Paths ──────────────────────────────────────────────────────────────────────
INPUT_CSV  = "thesis_main/Data/processed/floor_price/pagibig_clean.csv"
OUTPUT_CSV = "thesis_main/Data/processed/floor_price/pagibig_geocoded.csv"

# ── Metro Cebu cities to include ───────────────────────────────────────────────
METRO_CEBU_CITIES = {
    "CEBU CITY",
    "MANDAUE CITY",
    "LAPU-LAPU CITY (OPON)",
    "TALISAY CITY",
    "MINGLANILLA",
    "CONSOLACION",
}

CITY_DISPLAY = {
    "CEBU CITY":             "Cebu City",
    "MANDAUE CITY":          "Mandaue City",
    "LAPU-LAPU CITY (OPON)": "Lapu-Lapu City",
    "TALISAY CITY":          "Talisay, Cebu",
    "MINGLANILLA":           "Minglanilla, Cebu",
    "CONSOLACION":           "Consolacion, Cebu",
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def build_query(project_name: str, city_raw: str) -> str:
    """Build a query string for the Google Maps Geocoding API."""
    # Strip building/phase suffixes that confuse geocoders
    name = re.sub(r'\s*-\s*(BLDG|PHASE|BUILDING)\s*[\dIVX]+', '', project_name, flags=re.IGNORECASE)
    name = re.sub(r'\s+\d+$', '', name).strip()
    city = CITY_DISPLAY.get(city_raw, city_raw.title())
    return f"{name}, {city}, Cebu, Philippines"

def gmaps_geocode(query: str, retries: int = 3) -> tuple:
    """Return (lat, lon, formatted_address) or (None, None, None) on failure."""
    for attempt in range(retries):
        try:
            results = gmaps.geocode(query)
            if results:
                loc = results[0]["geometry"]["location"]
                formatted = results[0].get("formatted_address", "")
                return loc["lat"], loc["lng"], formatted
            return None, None, None
        except Exception as e:
            print(f"  ⚠ attempt {attempt+1} failed ({e}), retrying…")
            time.sleep(2 ** attempt)
    return None, None, None

def main():
    df = pd.read_csv(INPUT_CSV)
    metro_df = df[df["City"].isin(METRO_CEBU_CITIES)].copy().reset_index(drop=True)
    print(f"Metro Cebu Pag-IBIG properties: {len(metro_df)}")

    # Geocode once per unique (Property_Name, City) combination
    unique_projects = (
        metro_df[["Property_Name", "City"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    print(f"Unique project × city combinations to geocode: {len(unique_projects)}")
    print()

    geocache: dict[tuple, dict] = {}

    for idx, row in unique_projects.iterrows():
        key = (row["Property_Name"], row["City"])
        query = build_query(row["Property_Name"], row["City"])
        print(f"[{idx+1}/{len(unique_projects)}] {query}")

        lat, lon, formatted = gmaps_geocode(query)

        if lat is None:
            # Fallback: just city name
            city_display = CITY_DISPLAY.get(row["City"], row["City"].title())
            fallback = f"{city_display}, Cebu, Philippines"
            print(f"  → No result. Trying city fallback: {fallback}")
            lat, lon, formatted = gmaps_geocode(fallback)

        if lat is not None:
            print(f"  ✓ {lat:.6f}, {lon:.6f}  |  {formatted}")
        else:
            print(f"  ✗ Could not geocode.")

        geocache[key] = {
            "latitude":              lat,
            "longitude":             lon,
            "gmaps_formatted_address": formatted,
        }

    # Broadcast cached results back to all rows
    metro_df["latitude"] = metro_df.apply(
        lambda r: geocache.get((r["Property_Name"], r["City"]), {}).get("latitude"), axis=1
    )
    metro_df["longitude"] = metro_df.apply(
        lambda r: geocache.get((r["Property_Name"], r["City"]), {}).get("longitude"), axis=1
    )
    metro_df["gmaps_formatted_address"] = metro_df.apply(
        lambda r: geocache.get((r["Property_Name"], r["City"]), {}).get("gmaps_formatted_address"), axis=1
    )

    geocoded_count = metro_df["latitude"].notna().sum()
    print(f"\n✅ Geocoded: {geocoded_count}/{len(metro_df)} rows ({geocoded_count/len(metro_df)*100:.1f}%)")

    metro_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved → {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
