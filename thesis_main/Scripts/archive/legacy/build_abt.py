"""
build_abt.py
------------
Builds the Analytics Base Table (ABT) for the Metro Cebu property valuation model.

Sources merged:
  - BDO foreclosures     (floor price, 22 rows)   — already geocoded via Google Maps
  - Pag-IBIG acquired    (floor price, 96 rows)   — geocoded via Nominatim
  - Lamudi listings      (ceiling price, ~743 rows) — coordinates from scraper

Scope: full Metro Cebu corridor — Danao City (north) to Carcar City (south),
  plus Mactan Island (Lapu-Lapu, Cordova).

Standardised schema output:
  All structural fields + placeholders for GIS-derived features that will be
  computed in QGIS / Python GIS phase:
      dist_cbd_m, dist_airport_m, dist_cbrt_nearest_m
      amenity_score_education, _health, _finance, _grocery, _transport, _security
      amenity_score_composite
      spatial_lag_price
      bir_zonal_value, valuation_gap

Output: Data/processed/analytics_base_table.csv
"""

import re
import math
import numpy as np
import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────────
BDO_CSV     = "thesis_main/Scripts/Geocoding/geocoded_bdo_properties_cebu.csv"
PAGIBIG_CSV = "thesis_main/Data/processed/floor_price/pagibig_geocoded.csv"
LAMUDI_CSV  = "thesis_main/Data/webscraping-lamudi/lamudi_cebu_clean.csv"
OUTPUT_CSV  = "thesis_main/Data/processed/analytics_base_table.csv"

# ── Metro Cebu filter — full Danao-to-Carcar coastal corridor + Mactan ─────────
METRO_CEBU_LAMUDI = {
    # Core
    "Cebu", "Lapu-Lapu", "Mandaue",
    # Mactan island
    "Cordova",
    # North corridor
    "Consolacion", "Liloan", "Compostela", "Carmen", "Danao",
    # South corridor
    "Talisay", "Minglanilla", "San Fernando", "Naga", "Carcar",
}
METRO_CEBU_PAGIBIG = {
    "CEBU CITY", "MANDAUE CITY", "LAPU-LAPU CITY (OPON)",
    "TALISAY CITY", "MINGLANILLA", "CONSOLACION",
    "LILOAN", "COMPOSTELA", "CARMEN", "DANAO CITY",
    "CORDOVA", "SAN FERNANDO", "CITY OF NAGA", "CARCAR CITY",
}

# Normalise city display names to consistent title-case
CITY_NORM = {
    # Pag-IBIG keys
    "CEBU CITY":             "Cebu City",
    "MANDAUE CITY":          "Mandaue City",
    "LAPU-LAPU CITY (OPON)": "Lapu-Lapu City",
    "TALISAY CITY":          "Talisay City",
    "MINGLANILLA":           "Minglanilla",
    "CONSOLACION":           "Consolacion",
    "LILOAN":                "Liloan",
    "COMPOSTELA":            "Compostela",
    "CARMEN":                "Carmen",
    "DANAO CITY":            "Danao City",
    "CORDOVA":               "Cordova",
    "SAN FERNANDO":          "San Fernando",
    "CITY OF NAGA":          "Naga City",
    "CARCAR CITY":           "Carcar City",
    # Lamudi keys
    "Cebu":                  "Cebu City",
    "Mandaue":               "Mandaue City",
    "Lapu-Lapu":             "Lapu-Lapu City",
    "Talisay":               "Talisay City",
    "Minglanilla":           "Minglanilla",
    "Consolacion":           "Consolacion",
    "Liloan":                "Liloan",
    "Compostela":            "Compostela",
    "Carmen":                "Carmen",
    "Danao":                 "Danao City",
    "Cordova":               "Cordova",
    "San Fernando":          "San Fernando",
    "Naga":                  "Naga City",
    "Carcar":                "Carcar City",
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def normalise_price(val) -> float | None:
    """Extract a numeric peso value from a raw price string or number."""
    if pd.isna(val):
        return None
    s = str(val).strip()
    if re.search(r'/month|for.?rent|request|contact', s, re.IGNORECASE):
        return None
    # Remove currency symbols, commas, whitespace
    s = re.sub(r'[₱PHP,\s]', '', s, flags=re.IGNORECASE)
    try:
        v = float(s)
        return v if v > 0 else None
    except ValueError:
        return None

def parse_bedrooms(val) -> float | None:
    if pd.isna(val):
        return None
    s = str(val).strip().lower()
    if s in ('studio', '0', 'nan'):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return None

def normalise_area(val) -> float | None:
    if pd.isna(val):
        return None
    try:
        v = float(str(val).replace(',', ''))
        return v if v > 0 else None
    except ValueError:
        return None

# ── Load BDO ──────────────────────────────────────────────────────────────────

def load_bdo() -> pd.DataFrame:
    df = pd.read_csv(BDO_CSV)

    # Parse bedrooms/bathrooms from description
    def _parse_desc(desc):
        if pd.isna(desc):
            return None, None
        br = re.search(r'(\d+)\s*(?:BR|Bedroom)', str(desc), re.IGNORECASE)
        tb = re.search(r'(\d+)\s*(?:TB|T&B|Bathroom)', str(desc), re.IGNORECASE)
        return (int(br.group(1)) if br else None,
                int(tb.group(1)) if tb else None)

    brs, tbs = zip(*df["Property Description"].apply(_parse_desc))

    out = pd.DataFrame({
        "source":          "BDO",
        "price_type":      "floor",
        "property_name":   df["Project Name"],
        "address":         df["Property Address"],
        "city":            df["City"].map(CITY_NORM).fillna(df["City"]),
        "property_type":   df["Property Type"],
        "lot_area_sqm":    df["Lot Area (sqm)"].apply(normalise_area),
        "floor_area_sqm":  df["Floor Area (sqm)"].apply(normalise_area),
        "bedrooms":        list(brs),
        "bathrooms":       list(tbs),
        "price_php":       df["Advertised Price (Php)"].apply(normalise_price),
        "latitude":        pd.to_numeric(df["latitude"], errors="coerce"),
        "longitude":       pd.to_numeric(df["longitude"], errors="coerce"),
        "geocode_source":  "Google Maps API",
    })
    print(f"BDO loaded:    {len(out):>4} rows  |  with price: {out['price_php'].notna().sum()}")
    return out

# ── Load Pag-IBIG ─────────────────────────────────────────────────────────────

def load_pagibig() -> pd.DataFrame:
    df = pd.read_csv(PAGIBIG_CSV)
    df = df[df["City"].isin(METRO_CEBU_PAGIBIG)].copy()

    out = pd.DataFrame({
        "source":          "PagIBIG",
        "price_type":      "floor",
        "property_name":   df["Property_Name"],
        "address":         df["Property_Name"] + ", " + df["City"].str.title(),
        "city":            df["City"].map(CITY_NORM).fillna(df["City"]),
        "property_type":   df["Property_Type"],
        "lot_area_sqm":    df["Lot_Area_sqm"].apply(normalise_area),
        "floor_area_sqm":  df["Floor_Area_sqm"].apply(normalise_area),
        "bedrooms":        np.nan,
        "bathrooms":       np.nan,
        "price_php":       df["Price_PHP"].apply(normalise_price),
        "latitude":        pd.to_numeric(df["latitude"], errors="coerce"),
        "longitude":       pd.to_numeric(df["longitude"], errors="coerce"),
        "geocode_source":  "Nominatim (OSM)",
    })
    print(f"Pag-IBIG loaded: {len(out):>4} rows  |  with price: {out['price_php'].notna().sum()}")
    return out

# ── Load Lamudi ───────────────────────────────────────────────────────────────

def load_lamudi() -> pd.DataFrame:
    df = pd.read_csv(LAMUDI_CSV)
    df = df[df["city"].isin(METRO_CEBU_LAMUDI)].copy()

    # Parse bedrooms (may contain "Studio")
    df["bedrooms_clean"] = df["bedrooms"].apply(parse_bedrooms)
    df["bathrooms_clean"] = pd.to_numeric(df["bathrooms"], errors="coerce")

    # Infer property type from title
    def _ptype(title):
        t = str(title).lower()
        if "condo" in t:   return "Condominium"
        if "house" in t:   return "Single Detached"
        if "townhouse" in t: return "Townhouse"
        if "lot" in t:     return "Lot Only"
        if "apartment" in t: return "Apartment"
        return "Residential"

    out = pd.DataFrame({
        "source":          "Lamudi",
        "price_type":      "ceiling",
        "property_name":   df["title"],
        "address":         df["street_address"].fillna(df["city"]),
        "city":            df["city"].map(CITY_NORM).fillna(df["city"]),
        "property_type":   df["title"].apply(_ptype),
        "lot_area_sqm":    np.nan,   # Lamudi rarely has lot area
        "floor_area_sqm":  df["floor_area_sqm"].apply(normalise_area),
        "bedrooms":        df["bedrooms_clean"],
        "bathrooms":       df["bathrooms_clean"],
        "price_php":       df["price"].apply(normalise_price),
        "latitude":        pd.to_numeric(df["latitude"], errors="coerce"),
        "longitude":       pd.to_numeric(df["longitude"], errors="coerce"),
        "geocode_source":  "Lamudi scraper",
    })

    # Drop rentals and rows without prices
    out = out[out["price_php"].notna()].reset_index(drop=True)
    print(f"Lamudi loaded:  {len(out):>4} rows  |  with price: {out['price_php'].notna().sum()}")
    return out

# ── Merge & enrich ────────────────────────────────────────────────────────────

def add_derived_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Add computable derived fields. GIS features left as NaN placeholders."""

    # Price per sqm (use floor area first, fall back to lot area)
    area = df["floor_area_sqm"].combine_first(df["lot_area_sqm"])
    df["price_per_sqm"] = np.where(
        (area.notna()) & (area > 0),
        df["price_php"] / area,
        np.nan
    )

    # Log price (natural log, for modelling)
    df["log_price"] = np.where(
        df["price_php"] > 0,
        np.log(df["price_php"]),
        np.nan
    )

    # ── GIS-derived placeholders (to be filled via QGIS / Python GIS phase) ──
    gis_placeholders = [
        "dist_cbd_m",           # Haversine to Ayala Center Cebu
        "dist_airport_m",       # Haversine to MCIA
        "dist_cbrt_nearest_m",  # Haversine to nearest planned CBRT station
        "amenity_score_education",
        "amenity_score_health",
        "amenity_score_finance",
        "amenity_score_grocery",
        "amenity_score_transport",
        "amenity_score_security",
        "amenity_score_composite",  # Weighted index
        "spatial_lag_price",        # Mean price of neighbours within 1 km
        "bir_zonal_value",          # BIR zonal value per barangay
        "valuation_gap",            # price_php - bir_zonal_value
    ]
    for col in gis_placeholders:
        df[col] = np.nan

    return df

def main():
    print("=" * 60)
    print("Building Analytics Base Table (ABT)")
    print("=" * 60)

    bdo     = load_bdo()
    pagibig = load_pagibig()
    lamudi  = load_lamudi()

    abt = pd.concat([bdo, pagibig, lamudi], ignore_index=True)

    # Sequential property ID
    abt.insert(0, "property_id", range(1, len(abt) + 1))

    # Drop rows with no price
    before = len(abt)
    abt = abt[abt["price_php"].notna()].reset_index(drop=True)
    abt["property_id"] = range(1, len(abt) + 1)
    print(f"\nDropped {before - len(abt)} rows with no price.")

    # Extreme price outliers — flag but keep (model can decide)
    p01 = abt["price_php"].quantile(0.01)
    p99 = abt["price_php"].quantile(0.99)
    abt["price_outlier_flag"] = ~abt["price_php"].between(p01, p99)
    n_flags = abt["price_outlier_flag"].sum()

    # Add derived + placeholder fields
    abt = add_derived_fields(abt)

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("ABT Summary")
    print("=" * 60)
    print(f"Total rows:        {len(abt)}")
    print(f"  Floor price:     {(abt['price_type']=='floor').sum()}  (BDO + Pag-IBIG)")
    print(f"  Ceiling price:   {(abt['price_type']=='ceiling').sum()}  (Lamudi)")
    print(f"Price outlier flag:{n_flags}  (outside p01–p99)")
    print(f"Has lat/lon:       {abt['latitude'].notna().sum()}")
    print(f"Price range:       ₱{abt['price_php'].min():,.0f} – ₱{abt['price_php'].max():,.0f}")
    print(f"Median price:      ₱{abt['price_php'].median():,.0f}")
    print()
    print("City breakdown:")
    print(abt.groupby(["city", "source"])["property_id"].count().to_string())
    print()
    print(f"Columns: {list(abt.columns)}")

    abt.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✅ Saved → {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
