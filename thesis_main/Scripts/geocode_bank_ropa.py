"""
geocode_bank_ropa.py
---------------------
Forward-geocodes Metro Cebu bank ROPA properties using the Google Maps
Geocoding API.  Deduplicates by (project_name, city) so each unique
subdivision / project is only geocoded once.  Individual properties
with no project_name are geocoded by full address.

Requires: pip install googlemaps python-dotenv
API key:  thesis_main/.env  →  GOOGLE_MAPS_API_KEY=...

Input:  Data/raw/bank_ropa_cebu.csv
Output: Data/processed/bank_ropa_geocoded.csv   (original columns + lat/lon)
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
INPUT_CSV  = "thesis_main/Data/raw/bank_ropa_cebu.csv"
OUTPUT_CSV = "thesis_main/Data/processed/bank_ropa_geocoded.csv"

# ── Helpers ────────────────────────────────────────────────────────────────────

def _city_suffix(city: str) -> str:
    """Return a human-readable city string for geocoding queries."""
    city = city.strip()
    # Cities already named clearly; just append Cebu/Philippines context
    city_map = {
        "Cebu City":     "Cebu City, Cebu",
        "Mandaue City":  "Mandaue City, Cebu",
        "Lapu-Lapu City": "Lapu-Lapu City, Cebu",
        "Talisay City":  "Talisay City, Cebu",
        "Minglanilla":   "Minglanilla, Cebu",
        "Consolacion":   "Consolacion, Cebu",
        "Liloan":        "Liloan, Cebu",
        "Cordova":       "Cordova, Cebu",
        "Compostela":    "Compostela, Cebu",
        "San Fernando":  "San Fernando, Cebu",
        "City of Naga":  "City of Naga, Cebu",
        "Carcar City":   "Carcar City, Cebu",
        "Danao City":    "Danao City, Cebu",
    }
    return city_map.get(city, f"{city}, Cebu")


def geocode_key(row: pd.Series) -> str:
    """Unique key used for deduplication and caching."""
    project = str(row["project_name"]).strip()
    city = str(row["city"]).strip()
    if project and project.lower() != "nan":
        return f"{project}|{city}"
    # Fall back to full address for properties without a project name
    return f"{str(row['address']).strip()}|{city}"


def build_query(row: pd.Series) -> str:
    """Build a Google Maps geocoding query string."""
    project = str(row["project_name"]).strip()
    city = str(row["city"]).strip()
    city_str = _city_suffix(city)
    if project and project.lower() != "nan":
        # Strip phase/block/lot prefixes that can confuse geocoders
        name = re.sub(
            r'\s*(phase|blk|block|lot|unit)\s*[\dIVX]+',
            '', project, flags=re.IGNORECASE
        ).strip()
        return f"{name}, {city_str}, Philippines"
    # No project name — use the raw address
    return f"{str(row['address']).strip()}, {city_str}, Philippines"


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
        except Exception as exc:
            print(f"  ⚠ attempt {attempt + 1} failed ({exc}), retrying…")
            time.sleep(2 ** attempt)
    return None, None, None


def main():
    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df)} rows from {INPUT_CSV}")

    # Build unique-key column for deduplication
    df["_geo_key"] = df.apply(geocode_key, axis=1)

    unique_keys = df["_geo_key"].unique()
    print(f"Unique geocoding keys: {len(unique_keys)}")
    print()

    geocache: dict[str, dict] = {}

    for i, key in enumerate(unique_keys):
        # Use any row with this key to build the query
        sample_row = df[df["_geo_key"] == key].iloc[0]
        query = build_query(sample_row)
        print(f"[{i + 1}/{len(unique_keys)}] {query}")

        lat, lon, formatted = gmaps_geocode(query)

        if lat is None:
            # Fallback: city-level geocode
            city_str = _city_suffix(str(sample_row["city"]).strip())
            fallback = f"{city_str}, Philippines"
            print(f"  → No result. Trying city fallback: {fallback}")
            lat, lon, formatted = gmaps_geocode(fallback)

        if lat is not None:
            print(f"  ✓ {lat:.6f}, {lon:.6f}  |  {formatted}")
        else:
            print(f"  ✗ Could not geocode.")

        geocache[key] = {
            "latitude":       lat,
            "longitude":      lon,
            "geocode_source": "Google Maps API" if lat is not None else None,
            "gmaps_formatted_address": formatted,
        }

        # Polite delay to avoid rate-limiting
        time.sleep(0.2)

    # Broadcast cached results back to all rows
    df["latitude"]       = df["_geo_key"].map(lambda k: geocache[k]["latitude"])
    df["longitude"]      = df["_geo_key"].map(lambda k: geocache[k]["longitude"])
    df["geocode_source"] = df["_geo_key"].map(lambda k: geocache[k]["geocode_source"])
    df["gmaps_formatted_address"] = df["_geo_key"].map(
        lambda k: geocache[k]["gmaps_formatted_address"]
    )

    df.drop(columns=["_geo_key"], inplace=True)

    geocoded_count = df["latitude"].notna().sum()
    print(f"\n✅ Geocoded: {geocoded_count}/{len(df)} rows ({geocoded_count / len(df) * 100:.1f}%)")

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved → {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
