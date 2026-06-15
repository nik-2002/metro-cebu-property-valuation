"""
clean_multisource_2026-06.py
============================
Clean + geocode + dedup the three 2026-06 source scrapes (FilipinoHomes API, DotProperty,
OnePropertee) into ONE staged file in abt_clean schema, ready for canonical enrichment.

Mirrors stage_lamudi_batch.py conventions (price bounds, residential recode, 6-LGU filter via
LGU polygons, spatial cap, area consolidation, BIR join) and adds the multi-source pieces:

  1. NORMALISE each source to a common pre-stage frame.
  2. COORDS:
       - FilipinoHomes: precise embedded coords (geo_coordinates). Drop null-island (0,0).
       - DotProperty / OnePropertee: have only location TEXT -> forward-geocode via Google,
         caching UNIQUE strings only (~1,012 calls, not 7,525 rows). Each gets a
         geocode_precision flag from Google location_type (ROOFTOP/RANGE_INTERPOLATED = precise;
         GEOMETRIC_CENTER/APPROXIMATE = centroid). Reject out-of-Cebu-bounds.
  3. CITY via LGU polygon point-in-polygon (QGIS/data/lgu_boundaries.geojson) — also the 6-LGU
     filter. Rows outside all 6 polygons are dropped (handles Liloan/Naga/Danao/etc.).
  4. FILTERS: price 500k-500M; residential type recode; Vacant Lot scope (area 80-2000);
     valid price_per_sqm.
  5. DEDUP (user choice 2026-06-14: coords + price + area): within the new data AND vs the
     existing ABT. Catches the same property reposted across portals without nuking distinct
     units in one building (those differ on price/area).
  6. SPATIAL CAP 3 per ~11m cell — reduces centroid pile-up (esp. OnePropertee's 58 city
     centroids; user chose to keep OP but let the cap thin it).
  7. BUILD abt_clean base cols + BIR zonal join (reuse legacy reverse_geocode + join).

Output: Data/raw/multisource_batch_2026-06_staged.csv  (abt_clean schema; dist_*/mcrai_*/
spatial_lag_price empty for the canonical enrichment scripts). Does NOT touch abt_clean.csv.

Geocode cache: Data/processed/geocode_cache_multisource.json (rerun-safe; delete to refresh).
Run from the "16 Thesis" workspace root.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from shapely.geometry import Point, shape

SCRIPT_DIR = Path(__file__).resolve().parent
THESIS_DIR = SCRIPT_DIR.parent
LEGACY_DIR = SCRIPT_DIR / "archive" / "legacy"
sys.path.insert(0, str(LEGACY_DIR))
from join_bir_zonal import reverse_geocode_abt, join_bir_to_abt  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

DATA = THESIS_DIR / "Data"
ABT_PATH = DATA / "processed" / "abt_clean.csv"
LGU_GEOJSON = THESIS_DIR / "QGIS" / "data" / "lgu_boundaries.geojson"
BIR_SUMMARY_PATH = DATA / "BIR Zonal Values" / "bir_barangay_summary.csv"
CACHE_PATH = DATA / "processed" / "geocode_cache_multisource.json"
OUT_PATH = DATA / "raw" / "multisource_batch_2026-06_staged.csv"

FH_CSV = DATA / "webscraping-filipinohomes" / "fh_api_raw.csv"
DP_CSV = DATA / "webscraping-dotproperty" / "dp_raw.csv"
OP_CSV = DATA / "webscraping-onepropertee" / "op_raw.csv"

PRICE_MIN, PRICE_MAX = 500_000, 500_000_000
SPATIAL_CAP = 3
LOT_AREA_MIN, LOT_AREA_MAX = 80, 2000           # Vacant Lot scope (Decision 41)
CEBU_BOUNDS = dict(lat_min=9.3, lat_max=11.6, lon_min=123.0, lon_max=124.8)
PRECISE_TYPES = {"ROOFTOP", "RANGE_INTERPOLATED"}

# Residential title recode (stage_lamudi_batch TYPE_RULES).
TYPE_RULES = [
    (r"\bcondo(?:minium)?\b|\bapartment\b|\bpenthouse\b|\bstudio\b", "Condominium"),
    (r"\bsingle[-\s]?detached\b|\bdetached\s+house\b", "Single Detached"),
    (r"\btownhouse\b|\bduplex\b|\browhouse\b|\bsingle[-\s]?attached\b", "Townhouse"),
    (r"\bvacant\s+lot\b|\blot\s+only\b|\bresidential\s+lot\b|\bland\s+for\s+sale\b|\blot\b", "Vacant Lot"),
    (r"\bhouse\s*(?:and|&)\s*lot\b|\bvilla\b|\bhouse\b", "House and Lot"),
]
EXCLUDED_TITLE = re.compile(r"commercial|office|warehouse|farm|industrial|beach house", re.I)
# Distressed / non-arm's-length listings: "For Assume"/pasalo prices are loan balances, not
# market value (same class as the bank_ropa Decision 17 excludes). Drop them.
# Broadened 2026-06-14: `assum` catches assume/assumed/assumption (exact-word \bassume\b missed
# "assumption"/"assumed" — 3 slipped into the first ship).
DISTRESSED_TITLE = re.compile(
    r"assum|pa-?sa-?lo|pasalo|foreclos|repossess|bank[\s-]?owned|take[\s-]?over|distress", re.I)
# Per-stratum price_per_sqm sanity band (catches area errors + extreme mispricing).
PPSQM_BAND = {
    "Condominium": (15_000, 400_000),
    "House and Lot": (8_000, 250_000), "Single Detached": (8_000, 250_000),
    "Townhouse": (8_000, 250_000),
    "Vacant Lot": (2_000, 200_000),
}
# category fallback when the title is uninformative
CAT_FALLBACK = {"house": "House and Lot", "condo": "Condominium", "lot": "Vacant Lot"}


def norm_txt(v):
    return "" if pd.isna(v) else re.sub(r"\s+", " ", str(v)).strip()


def infer_type(title, category):
    t = norm_txt(title)
    if t and EXCLUDED_TITLE.search(t):
        return None
    for pat, label in TYPE_RULES:
        if t and re.search(pat, t, re.I):
            return label
    return CAT_FALLBACK.get(category)


# --------------------------------------------------------------------------- normalise
def load_normalised():
    """Common frame: source,url,title,category,price_php,latitude,longitude,loc_text,
    floor_area_sqm,lot_area_sqm,bedrooms,bathrooms,geocode_source,geocode_precision."""
    frames = []

    fh = pd.read_csv(FH_CSV)
    fh = fh[~((fh["latitude"].abs() < 0.001) & (fh["longitude"].abs() < 0.001))].copy()  # null-island
    frames.append(pd.DataFrame({
        "source": "filipinohomes", "url": fh["url"], "title": fh["title"], "category": fh["category"],
        "price_php": pd.to_numeric(fh["price_php"], errors="coerce"),
        "latitude": pd.to_numeric(fh["latitude"], errors="coerce"),
        "longitude": pd.to_numeric(fh["longitude"], errors="coerce"),
        "loc_text": fh["address"],
        "floor_area_sqm": pd.to_numeric(fh["floor_area_sqm"], errors="coerce"),
        "lot_area_sqm": pd.to_numeric(fh["lot_area_sqm"], errors="coerce"),
        "bedrooms": pd.to_numeric(fh["bedrooms"], errors="coerce"),
        "bathrooms": pd.to_numeric(fh["bathrooms"], errors="coerce"),
        "geocode_source": "fh_listing_embedded", "geocode_precision": "embedded",
    }))

    dp = pd.read_csv(DP_CSV)
    frames.append(pd.DataFrame({
        "source": "dotproperty", "url": dp["url"], "title": dp["title"], "category": dp["category"],
        "price_php": pd.to_numeric(dp["price_php"], errors="coerce"),
        "latitude": np.nan, "longitude": np.nan, "loc_text": dp["location_text"],
        "floor_area_sqm": pd.to_numeric(dp["area_sqm"], errors="coerce"),  # single area field
        "lot_area_sqm": np.nan,
        "bedrooms": pd.to_numeric(dp["bedrooms"], errors="coerce"),
        "bathrooms": pd.to_numeric(dp["bathrooms"], errors="coerce"),
        "geocode_source": "google_text", "geocode_precision": np.nan,
    }))

    # OnePropertee DROPPED 2026-06-14 (feature investigation, Decision 47 follow-up): its rows
    # are city-centroid geocoded AND its lots are per-sqm-priced text the parser mis-extracts —
    # OOF showed model over-predicts OP lots 3.3x (MdAPE 234%) and condos 1.43x (43%). Only 36
    # survived the spatial cap and they were demonstrable contamination. Excluded entirely.
    # (Scraper + raw CSV kept; re-enable here if a future cleaner OP extraction is built.)

    df = pd.concat(frames, ignore_index=True)
    print(f"normalised: {len(df)} rows  ({df['source'].value_counts().to_dict()})")
    return df


# --------------------------------------------------------------------------- geocode
def in_cebu(lat, lon):
    return (CEBU_BOUNDS["lat_min"] <= lat <= CEBU_BOUNDS["lat_max"]
            and CEBU_BOUNDS["lon_min"] <= lon <= CEBU_BOUNDS["lon_max"])


def geocode_text(df, api_key):
    """Forward-geocode unique loc_text for rows lacking coords (DP/OP). Cache to disk."""
    cache = json.loads(CACHE_PATH.read_text()) if CACHE_PATH.exists() else {}
    need = df["latitude"].isna() & df["loc_text"].notna()
    uniq = sorted({norm_txt(s) for s in df.loc[need, "loc_text"] if norm_txt(s)})
    todo = [s for s in uniq if s not in cache]
    print(f"geocode: {len(uniq)} unique strings, {len(todo)} not cached -> calling Google")

    for i, q in enumerate(todo, 1):
        query = q if "philippin" in q.lower() else f"{q}, Philippines"
        if "cebu" not in q.lower():
            query = f"{q}, Cebu, Philippines"
        try:
            r = requests.get("https://maps.googleapis.com/maps/api/geocode/json",
                             params={"address": query, "key": api_key}, timeout=20).json()
            st = r.get("status")
            if st == "OK":
                g = r["results"][0]["geometry"]
                lat, lon = g["location"]["lat"], g["location"]["lng"]
                if in_cebu(lat, lon):
                    cache[q] = {"lat": lat, "lon": lon, "precision": g.get("location_type", "")}
                else:
                    cache[q] = None  # out of bounds
            elif st == "OVER_QUERY_LIMIT":
                print("  !! OVER_QUERY_LIMIT — stopping; rerun later (cache preserved). "
                      "Switch to OSM if persistent.")
                break
            else:
                cache[q] = None
        except requests.RequestException as e:
            print(f"  geocode error '{q}': {e}")
        if i % 100 == 0:
            print(f"  ...{i}/{len(todo)}")
            CACHE_PATH.write_text(json.dumps(cache))
        time.sleep(0.06)
    CACHE_PATH.write_text(json.dumps(cache))

    # attach (vectorized, dtype-safe): only fill rows that currently lack coords
    key = df["loc_text"].map(norm_txt)
    glat = key.map(lambda k: cache[k]["lat"] if cache.get(k) else np.nan)
    glon = key.map(lambda k: cache[k]["lon"] if cache.get(k) else np.nan)
    gprec = key.map(lambda k: cache[k]["precision"] if cache.get(k) else np.nan)
    fillmask = df["latitude"].isna()
    df.loc[fillmask, "latitude"] = glat[fillmask]
    df.loc[fillmask, "longitude"] = glon[fillmask]
    df.loc[fillmask, "geocode_precision"] = gprec[fillmask]
    got = df["latitude"].notna().sum()
    print(f"  geocoded: {got}/{len(df)} rows now have coords")
    return df


# --------------------------------------------------------------------------- LGU assign
def assign_lgu(df):
    geo = json.loads(LGU_GEOJSON.read_text())
    geoms = {f["properties"]["lgu"]: shape(f["geometry"]) for f in geo["features"]}
    cities = []
    for lat, lon in zip(df["latitude"], df["longitude"]):
        if pd.isna(lat) or pd.isna(lon):
            cities.append(None); continue
        pt = Point(lon, lat)
        hit = next((k for k, g in geoms.items() if g.contains(pt)), None)
        cities.append(hit)
    df["city"] = cities
    return df


def main():
    load_dotenv(THESIS_DIR / ".env")
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    abt = pd.read_csv(ABT_PATH)
    log = []

    df = load_normalised()
    log.append(("normalised (FH null-island dropped)", len(df)))

    # price bounds
    df = df[df["price_php"].between(PRICE_MIN, PRICE_MAX)].copy()
    log.append((f"price in [{PRICE_MIN:,}-{PRICE_MAX:,}]", len(df)))

    # geocode text rows (DP/OP); FH already has coords
    df = geocode_text(df, api_key)
    df = df[df["latitude"].notna() & df["longitude"].notna()].copy()
    log.append(("has coords (geocoded)", len(df)))

    # LGU polygon -> city + 6-LGU filter
    df = assign_lgu(df)
    df = df[df["city"].notna()].copy()
    log.append(("inside 6 LGUs (polygon)", len(df)))

    # residential type recode
    df["property_type"] = df.apply(lambda r: infer_type(r["title"], r["category"]), axis=1)
    df = df[df["property_type"].notna()].copy()
    log.append(("residential type recode", len(df)))

    # area consolidation (floor first, lot fallback) + Vacant Lot scope
    floor = pd.to_numeric(df["floor_area_sqm"], errors="coerce")
    lot = pd.to_numeric(df["lot_area_sqm"], errors="coerce")
    df["area_sqm"] = np.where(floor.notna() & (floor > 0), floor, lot)
    df = df[df["area_sqm"].notna() & (df["area_sqm"] > 0)].copy()
    is_lot = df["property_type"] == "Vacant Lot"
    lot_ok = (~is_lot) | (df["area_sqm"].between(LOT_AREA_MIN, LOT_AREA_MAX))
    df = df[lot_ok].copy()
    log.append((f"area>0 + Lot scope [{LOT_AREA_MIN}-{LOT_AREA_MAX}]", len(df)))

    # drop distressed / mortgage-assumption listings (loan-balance prices, not market value)
    distressed = df["title"].fillna("").str.contains(DISTRESSED_TITLE)
    df = df[~distressed].copy()
    log.append((f"drop distressed/assume (-{int(distressed.sum())})", len(df)))

    df["price_per_sqm"] = df["price_php"] / df["area_sqm"]
    df = df[df["price_per_sqm"].notna() & (df["price_per_sqm"] > 0)].copy()
    log.append(("valid price_per_sqm", len(df)))

    # per-stratum price_per_sqm sanity band (area errors + extreme mispricing)
    lo = df["property_type"].map(lambda t: PPSQM_BAND.get(t, (0, 1e12))[0])
    hi = df["property_type"].map(lambda t: PPSQM_BAND.get(t, (0, 1e12))[1])
    band_ok = (df["price_per_sqm"] >= lo) & (df["price_per_sqm"] <= hi)
    df = df[band_ok].copy()
    log.append((f"price_per_sqm band by stratum (-{int((~band_ok).sum())})", len(df)))

    # ---- DEDUP (coords + price + area), within new data, precise-coords-first ----
    df["rlat"], df["rlon"] = df["latitude"].round(4), df["longitude"].round(4)
    df["pbucket"] = df["price_php"].round(-4).astype("int64")   # nearest 10k peso
    df["abucket"] = df["area_sqm"].round(0)
    df["_precise"] = df["geocode_precision"].isin(PRECISE_TYPES | {"embedded"}).astype(int)
    before = len(df)
    df = (df.sort_values(["_precise", "source"], ascending=[False, True], kind="stable")
            .drop_duplicates(subset=["rlat", "rlon", "pbucket", "abucket"], keep="first").copy())
    log.append((f"dedup coords+price+area (-{before-len(df)})", len(df)))

    # dedup vs existing ABT (same coords+price+area already in the master)
    a = abt.dropna(subset=["latitude", "longitude", "price_php", "area_sqm"]).copy()
    abt_keys = set(zip(a["latitude"].round(4), a["longitude"].round(4),
                       a["price_php"].round(-4).astype("int64"), a["area_sqm"].round(0)))
    mask = [ (rl, ro, int(pb), ab) not in abt_keys
             for rl, ro, pb, ab in zip(df["rlat"], df["rlon"], df["pbucket"], df["abucket"]) ]
    df = df[mask].copy()
    log.append(("dedup vs existing ABT", len(df)))

    # ---- spatial cap (3 per ~11m cell): keep highest-priced ----
    before = len(df)
    df = (df.sort_values(["rlat", "rlon", "price_php"], kind="stable")
            .groupby(["rlat", "rlon"], sort=False, group_keys=False).head(SPATIAL_CAP).copy())
    cap_dropped = before - len(df)
    log.append((f"spatial cap 3/cell (-{cap_dropped})", len(df)))

    # ---- build abt_clean base columns ----
    out = pd.DataFrame(index=df.index)
    next_id = int(abt["property_id"].max()) + 1
    out["property_id"] = np.arange(next_id, next_id + len(df))
    out["source"] = df["source"].map({"filipinohomes": "FilipinoHomes_2026-06",
                                       "dotproperty": "DotProperty_2026-06",
                                       "onepropertee": "OnePropertee_2026-06"}).values
    out["price_type"] = "open_market"
    out["property_name"] = df["title"].map(norm_txt).values
    out["address"] = df["loc_text"].map(norm_txt).values
    out["city"] = df["city"].values
    out["property_type"] = df["property_type"].values
    out["lot_area_sqm"] = np.nan
    out["floor_area_sqm"] = df["area_sqm"].values
    out["area_sqm"] = df["area_sqm"].values
    out["bedrooms"] = df["bedrooms"].values
    out["bathrooms"] = df["bathrooms"].values
    out["price_php"] = df["price_php"].values
    out["latitude"] = df["latitude"].values
    out["longitude"] = df["longitude"].values
    out["geocode_source"] = df["geocode_source"].values
    out["geocode_precision"] = df["geocode_precision"].values
    out["price_outlier_flag"] = False
    out["price_per_sqm"] = df["price_per_sqm"].values
    out["log_price"] = np.log(df["price_per_sqm"].values)
    out["is_mactan_island"] = (out["city"] == "Lapu-Lapu City").astype(int)
    out["is_vacant_lot"] = (out["property_type"] == "Vacant Lot").astype(int)
    out["bedrooms_imputed"] = out["bedrooms"].isna().astype(int)
    out["bathrooms_imputed"] = out["bathrooms"].isna().astype(int)
    out["floor_area_imputed"] = out["area_sqm"].isna().astype(int)
    out["market_segment"] = "open_market"

    # ---- BIR zonal join ----
    bir_summary = pd.read_csv(BIR_SUMMARY_PATH)
    out = reverse_geocode_abt(out, api_key)
    out = join_bir_to_abt(out, bir_summary)
    out["valuation_gap"] = out["price_per_sqm"] - out["bir_zonal_rr_median"]

    # align to abt_clean schema (enrichment cols left empty); keep geocode_precision as extra
    for col in abt.columns:
        if col not in out.columns:
            out[col] = np.nan
    keep = list(abt.columns) + (["geocode_precision"] if "geocode_precision" not in abt.columns else [])
    out = out.reindex(columns=keep)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_PATH, index=False)

    # ---- report ----
    print("\n=== FUNNEL ===")
    for label, n in log:
        print(f"  {label:42s} {n}")
    print(f"\n  staged rows: {len(out)}  ->  {OUT_PATH.relative_to(THESIS_DIR)}")
    print("\n=== staged by source ===\n", out["source"].value_counts().to_string())
    print("\n=== staged by property_type ===\n", out["property_type"].value_counts().to_string())
    print("\n=== staged by city ===\n", out["city"].value_counts().to_string())
    print("\n=== geocode precision ===\n", out["geocode_precision"].value_counts(dropna=False).to_string())
    print(f"\n  spatial cap dropped {cap_dropped}; enrichment cols (dist_*/mcrai_*/spatial_lag) empty.")


if __name__ == "__main__":
    main()
