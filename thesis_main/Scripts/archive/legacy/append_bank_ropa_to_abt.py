"""
append_bank_ropa_to_abt.py
---------------------------
Maps geocoded bank ROPA properties to the ABT schema and appends them
as new rows.  Enrichment columns (distances, amenity scores, BIR zonal,
spatial lag) are left as NaN — re-run enrich_abt.py and join_bir_zonal.py
after this script to populate those fields.

Inputs:
  Data/processed/bank_ropa_geocoded.csv
  Data/processed/analytics_base_table.csv

Output (overwrites):
  Data/processed/analytics_base_table.csv

Run order:
  1. geocode_bank_ropa.py
  2. append_bank_ropa_to_abt.py        ← this script
  3. enrich_abt.py                     (re-run enrichment on full ABT)
  4. join_bir_zonal.py                 (re-run BIR zonal join)
"""

import os
import numpy as np
import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────────
ROPA_CSV = "thesis_main/Data/processed/bank_ropa_geocoded.csv"
ABT_CSV  = "thesis_main/Data/processed/analytics_base_table.csv"

# ── Column order from the existing ABT ────────────────────────────────────────
ABT_COLUMNS = [
    "property_id",
    "source",
    "price_type",
    "property_name",
    "address",
    "city",
    "property_type",
    "lot_area_sqm",
    "floor_area_sqm",
    "bedrooms",
    "bathrooms",
    "price_php",
    "latitude",
    "longitude",
    "geocode_source",
    "price_outlier_flag",
    "price_per_sqm",
    "log_price",
    "dist_cbd_m",
    "dist_airport_m",
    "dist_cbrt_nearest_m",
    "amenity_score_education",
    "amenity_score_health",
    "amenity_score_finance",
    "amenity_score_grocery",
    "amenity_score_transport",
    "amenity_score_security",
    "amenity_score_composite",
    "spatial_lag_price",
    "bir_zonal_value",
    "valuation_gap",
    "dist_cebu_business_park_m",
    "dist_it_park_m",
    "dist_mandaue_cbd_m",
    "dist_mactan_cbd_m",
    "dist_srp_m",
    "dist_talisay_tabunok_m",
    "dist_consolacion_m",
    "dist_naga_city_m",
    "dist_minglanilla_poblacion_m",
    "dist_minglanilla_lipata_m",
    "barangay_geocoded",
    "bir_zonal_rr_median",
    "bir_zonal_cr_median",
    "bir_zonal_rc_median",
    "bir_zonal_rr_log",
]

# ── Columns to leave as NaN (filled by downstream enrichment scripts) ──────────
ENRICHMENT_COLUMNS = [
    "price_outlier_flag",
    "dist_cbd_m",
    "dist_airport_m",
    "dist_cbrt_nearest_m",
    "amenity_score_education",
    "amenity_score_health",
    "amenity_score_finance",
    "amenity_score_grocery",
    "amenity_score_transport",
    "amenity_score_security",
    "amenity_score_composite",
    "spatial_lag_price",
    "bir_zonal_value",
    "valuation_gap",
    "dist_cebu_business_park_m",
    "dist_it_park_m",
    "dist_mandaue_cbd_m",
    "dist_mactan_cbd_m",
    "dist_srp_m",
    "dist_talisay_tabunok_m",
    "dist_consolacion_m",
    "dist_naga_city_m",
    "dist_minglanilla_poblacion_m",
    "dist_minglanilla_lipata_m",
    "barangay_geocoded",
    "bir_zonal_rr_median",
    "bir_zonal_cr_median",
    "bir_zonal_rc_median",
    "bir_zonal_rr_log",
]


def map_ropa_to_abt(ropa: pd.DataFrame, max_existing_id: int) -> pd.DataFrame:
    """
    Transform geocoded bank ROPA rows into the ABT column schema.

    Column mapping
    --------------
    bank           → source
    project_name   → property_name
    price          → price_php
    lot_area_sqm   → lot_area_sqm  (0 treated as missing)
    floor_area_sqm → floor_area_sqm (0 treated as missing)
    latitude       → latitude       (from geocoding step)
    longitude      → longitude      (from geocoding step)
    geocode_source → geocode_source (from geocoding step)

    Derived fields computed here
    ----------------------------
    property_id     : max_existing_id + 1, incrementing
    price_type      : "asking" (bank ROPA listed prices)
    price_per_sqm   : price_php / floor_area_sqm (fallback to lot_area_sqm)
    log_price       : ln(price_php)
    bedrooms        : NaN
    bathrooms       : NaN
    """
    out = pd.DataFrame()

    # Identifiers
    out["property_id"]   = range(max_existing_id + 1, max_existing_id + 1 + len(ropa))
    out["source"]        = ropa["bank"].str.strip()
    out["price_type"]    = "asking"
    out["property_name"] = ropa["project_name"].str.strip().replace("", np.nan)
    out["address"]       = ropa["address"].str.strip()
    out["city"]          = ropa["city"].str.strip()
    out["property_type"] = ropa["property_type"].str.strip()

    # Areas (0 → NaN so downstream logic treats them as missing)
    out["lot_area_sqm"]   = pd.to_numeric(ropa["lot_area_sqm"], errors="coerce").replace(0, np.nan)
    out["floor_area_sqm"] = pd.to_numeric(ropa["floor_area_sqm"], errors="coerce").replace(0, np.nan)

    # Bedrooms / bathrooms not available in ROPA data
    out["bedrooms"]  = np.nan
    out["bathrooms"] = np.nan

    # Price
    out["price_php"] = pd.to_numeric(ropa["price"], errors="coerce")

    # Geocoords
    out["latitude"]       = pd.to_numeric(ropa["latitude"], errors="coerce")
    out["longitude"]      = pd.to_numeric(ropa["longitude"], errors="coerce")
    out["geocode_source"] = ropa["geocode_source"]

    # Derived: price per sqm (floor area preferred, lot area as fallback)
    area = out["floor_area_sqm"].combine_first(out["lot_area_sqm"])
    out["price_per_sqm"] = np.where(
        (area.notna()) & (area > 0),
        out["price_php"] / area,
        np.nan
    )

    # Derived: log price
    out["log_price"] = np.where(
        out["price_php"].notna() & (out["price_php"] > 0),
        np.log(out["price_php"]),
        np.nan
    )

    # Enrichment columns — left as NaN for downstream scripts
    for col in ENRICHMENT_COLUMNS:
        out[col] = np.nan

    return out.reset_index(drop=True)


def main():
    if not os.path.exists(ROPA_CSV):
        raise FileNotFoundError(
            f"Geocoded ROPA file not found: {ROPA_CSV}\n"
            "Run geocode_bank_ropa.py first."
        )

    ropa = pd.read_csv(ROPA_CSV)
    abt  = pd.read_csv(ABT_CSV)

    print(f"ABT rows (before): {len(abt)}")
    print(f"ROPA rows to append: {len(ropa)}")

    # Check for already-appended ROPA rows (idempotency guard)
    # Only check the actual bank names present in bank_ropa_cebu.csv
    existing_ropa_sources = {
        "BPI", "Metrobank", "Bank of Commerce", "Landbank", "China Bank Savings",
    }
    abt_bank_rows = abt[abt["source"].isin(existing_ropa_sources)]
    if len(abt_bank_rows) > 0:
        print(
            f"\n⚠  ABT already contains {len(abt_bank_rows)} rows from bank sources."
        )
        print("   Re-running will create duplicates.  Aborting.")
        print("   To re-append, remove existing bank rows from the ABT first.")
        return

    max_id = int(abt["property_id"].max())
    print(f"Max existing property_id: {max_id}")

    new_rows = map_ropa_to_abt(ropa, max_id)

    # Ensure column order matches ABT
    new_rows = new_rows[ABT_COLUMNS]

    combined = pd.concat([abt, new_rows], ignore_index=True)

    print(f"ABT rows (after):  {len(combined)}")
    print(f"New property_ids:  {max_id + 1} → {max_id + len(ropa)}")

    geocoded_new = new_rows["latitude"].notna().sum()
    missing_geo  = len(new_rows) - geocoded_new
    print(f"Geocoded new rows: {geocoded_new}/{len(new_rows)}", end="")
    if missing_geo:
        print(f"  ⚠  {missing_geo} rows missing geocoords — enrichment columns will be empty")
    else:
        print()

    combined.to_csv(ABT_CSV, index=False)
    print(f"\n✅ Saved → {ABT_CSV}")
    print()
    print("Next steps:")
    print("  python thesis_main/Scripts/enrich_abt.py    # distances + amenity scores")
    print("  python thesis_main/Scripts/join_bir_zonal.py  # BIR zonal + barangay")


if __name__ == "__main__":
    main()
