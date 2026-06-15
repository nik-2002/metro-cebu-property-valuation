"""Geocode scraped Lamudi rows that are missing coordinates.

Scope (per author, 2026-06-05): fill lat/long ONLY for the land and house
families (the scarce/target strata). Condos are plentiful, so coord-less
condos are left to be dropped downstream.

- Service: Google Maps Geocoding API (matches the project's existing geocoder;
  GOOGLE_MAPS_API_KEY in thesis_main/.env).
- Caches results by address string in playwright/data/geocode_cache.json so
  re-runs are free and idempotent.
- Reads the raw scrape (lamudi_scraped.csv), writes a filled copy to
  lamudi_scraped_geocoded.csv with the SAME 15-column schema (clean append to
  canonical), and a side report (geocode_report.csv) of what was filled.
- Sanity-bounds results to Cebu province; out-of-bounds hits are rejected and
  the row is left coord-less rather than poisoned with a bad point.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pandas as pd
import googlemaps
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
THESIS_DIR = HERE.parent
DATA_DIR = HERE / "data"

RAW_CSV = DATA_DIR / "lamudi_scraped.csv"
OUT_CSV = DATA_DIR / "lamudi_scraped_geocoded.csv"
REPORT_CSV = DATA_DIR / "geocode_report.csv"
CACHE_JSON = DATA_DIR / "geocode_cache.json"

TARGET_FAMILIES = {"land", "house"}

# Cebu province bounding box — reject anything outside (catches Manila/other-province hits).
CEBU_BOUNDS = dict(lat_min=9.3, lat_max=11.6, lon_min=123.0, lon_max=124.8)

CHECKPOINT_EVERY = 10


def family(property_type_raw: str) -> str:
    parts = [p.strip() for p in str(property_type_raw).split("|")]
    cat = parts[1].lower() if len(parts) > 1 else ""
    return cat.split("/")[0]


def load_cache() -> dict:
    if CACHE_JSON.exists():
        with CACHE_JSON.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def save_cache(cache: dict) -> None:
    with CACHE_JSON.open("w", encoding="utf-8") as fh:
        json.dump(cache, fh, ensure_ascii=False, indent=2)


def in_cebu(lat: float, lng: float) -> bool:
    return (
        CEBU_BOUNDS["lat_min"] <= lat <= CEBU_BOUNDS["lat_max"]
        and CEBU_BOUNDS["lon_min"] <= lng <= CEBU_BOUNDS["lon_max"]
    )


def build_query(addr: str) -> str:
    addr = str(addr).strip()
    low = addr.lower()
    if "cebu" not in low:
        addr = f"{addr}, Cebu"
    if "philippin" not in low and "pilipinas" not in low:
        addr = f"{addr}, Philippines"
    return addr


def main() -> None:
    load_dotenv(THESIS_DIR / ".env")
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        raise SystemExit("ERROR: GOOGLE_MAPS_API_KEY not set in thesis_main/.env")
    gmaps = googlemaps.Client(key=api_key)

    df = pd.read_csv(RAW_CSV)
    df["_fam"] = df["property_type_raw"].apply(family)

    targets = df[
        df["latitude"].isna() & df["longitude"].isna() & df["_fam"].isin(TARGET_FAMILIES)
    ]
    print(f"Rows missing coords in land/house families: {len(targets)}")

    cache = load_cache()
    report_rows = []
    filled = rejected = failed = 0

    for n, (idx, row) in enumerate(targets.iterrows(), start=1):
        query = build_query(row["street_address"])
        if query in cache:
            res = cache[query]
        else:
            try:
                geo = gmaps.geocode(query)
                if geo:
                    loc = geo[0]["geometry"]["location"]
                    res = {
                        "lat": loc["lat"],
                        "lng": loc["lng"],
                        "formatted": geo[0].get("formatted_address", ""),
                        "loc_type": geo[0]["geometry"].get("location_type", ""),
                    }
                else:
                    res = None
            except Exception as exc:  # noqa: BLE001
                print(f"  [!] error geocoding '{query}': {exc}")
                res = None
            cache[query] = res
            time.sleep(0.1)  # gentle pacing

        status = "failed"
        if res is not None and in_cebu(res["lat"], res["lng"]):
            df.at[idx, "latitude"] = res["lat"]
            df.at[idx, "longitude"] = res["lng"]
            filled += 1
            status = "filled"
        elif res is not None:
            rejected += 1
            status = "rejected_out_of_bounds"
        else:
            failed += 1

        report_rows.append(
            {
                "url": row["url"],
                "family": row["_fam"],
                "city": row["city"],
                "query": query,
                "status": status,
                "lat": (res or {}).get("lat") if res else None,
                "lng": (res or {}).get("lng") if res else None,
                "loc_type": (res or {}).get("loc_type") if res else None,
                "formatted": (res or {}).get("formatted") if res else None,
            }
        )

        if n % CHECKPOINT_EVERY == 0:
            save_cache(cache)
            print(f"  ...{n}/{len(targets)} processed (filled={filled})")

    save_cache(cache)
    df.drop(columns=["_fam"]).to_csv(OUT_CSV, index=False)
    pd.DataFrame(report_rows).to_csv(REPORT_CSV, index=False)

    print("\n=== GEOCODE SUMMARY ===")
    print(f"  filled:   {filled}")
    print(f"  rejected (out of Cebu bounds): {rejected}")
    print(f"  failed (no result):            {failed}")
    print(f"  wrote: {OUT_CSV.name}, {REPORT_CSV.name}, {CACHE_JSON.name}")
    still = df["latitude"].isna().sum()
    print(f"  rows still missing coords (all families): {still}")


if __name__ == "__main__":
    main()
