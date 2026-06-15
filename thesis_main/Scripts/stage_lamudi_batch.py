"""Step A of the 2026-06 Lamudi batch merge: build cleaned base rows.

Reads the geocoded Playwright scrape, applies the canonical cleaning + the two
scope filters (residential-only, 6-LGU), builds the abt_clean base columns,
joins BIR zonal values (canonical reverse-geocode + join), and writes a STAGED
file. It does NOT touch the master abt_clean.csv — enrichment (road/MCRAI),
the polygon LGU filter, append, and modeling happen in later steps.

Output: thesis_main/Data/raw/lamudi_batch_2026-06_staged.csv  (abt_clean schema;
dist_*/mcrai_*/spatial_lag_price left empty for the canonical enrichment scripts).

Run from the "16 Thesis" workspace root so the legacy BIR paths resolve.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
THESIS_DIR = SCRIPT_DIR.parent
LEGACY_DIR = SCRIPT_DIR / "archive" / "legacy"
sys.path.insert(0, str(LEGACY_DIR))

from join_bir_zonal import reverse_geocode_abt, join_bir_to_abt  # noqa: E402

import os  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

SCRAPE_CSV = THESIS_DIR / "playwright" / "data" / "lamudi_scraped_geocoded.csv"
ABT_PATH = THESIS_DIR / "Data" / "processed" / "abt_clean.csv"
BIR_SUMMARY_PATH = THESIS_DIR / "Data" / "BIR Zonal Values" / "bir_barangay_summary.csv"
OUT_PATH = THESIS_DIR / "Data" / "raw" / "lamudi_batch_2026-06_staged.csv"

PRICE_MIN, PRICE_MAX = 500_000, 500_000_000
SPATIAL_CAP = 3  # max listings per rounded (lat, lon) cell

# Canonical city map (process_lamudi_phase_c). Cities not here -> dropped (= 6-LGU filter).
CITY_MAP = {
    "Cebu": "Cebu City", "Cebu City": "Cebu City",
    "Lapu-Lapu": "Lapu-Lapu City", "Lapu-Lapu City": "Lapu-Lapu City",
    "Mandaue": "Mandaue City", "Mandaue City": "Mandaue City",
    "Talisay": "Talisay City", "Talisay City": "Talisay City",
    "Minglanilla": "Minglanilla", "Consolacion": "Consolacion",
}

# Canonical title-based recode (process_lamudi_phase_c TYPE_RULES).
TYPE_RULES = [
    (r"\bcondo(?:minium)?\b|\bapartment\b|\bpenthouse\b|\bstudio\b", "Condominium"),
    (r"\bsingle[-\s]?detached\b|\bdetached\s+house\b", "Single Detached"),
    (r"\btownhouse\b|\bduplex\b|\browhouse\b|\bsingle[-\s]?attached\b", "Townhouse"),
    (r"\bvacant\s+lot\b|\blot\s+only\b|\bresidential\s+lot\b|\bland\s+for\s+sale\b", "Vacant Lot"),
    (r"\bhouse\s*(?:and|&)\s*lot\b|\bvilla\b|\bhouse\b", "House and Lot"),
]
EXCLUDED_TITLE = re.compile(r"commercial|office|warehouse|farm|industrial|beach house", re.IGNORECASE)

# Fallback recode from the scraped category token (Accommodation | <cat> | <title>).
CAT_FALLBACK = {"land": "Vacant Lot", "condo": "Condominium", "apartment": "Condominium",
                "house": "House and Lot"}


def norm_txt(v):
    return "" if pd.isna(v) else re.sub(r"\s+", " ", str(v)).strip()


def cat_token(raw):
    parts = [p.strip() for p in str(raw).split("|")]
    return (parts[1].lower().split("/")[0] if len(parts) > 1 else "")


def infer_type(title, raw):
    t = norm_txt(title)
    if t and EXCLUDED_TITLE.search(t):
        return None  # residential-only filter
    for pat, label in TYPE_RULES:
        if t and re.search(pat, t, re.IGNORECASE):
            return label
    # fallback to category token if title was uninformative
    return CAT_FALLBACK.get(cat_token(raw))


def parse_price(v):
    if pd.isna(v):
        return np.nan
    c = re.sub(r"[^0-9.]", "", str(v))
    try:
        p = float(c)
    except ValueError:
        return np.nan
    return p if p > 0 else np.nan


def combo_key(a, b):
    return (norm_txt(a).casefold(), norm_txt(b).casefold())


def main():
    load_dotenv(THESIS_DIR / ".env")
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    abt = pd.read_csv(ABT_PATH)
    df = pd.read_csv(SCRAPE_CSV)
    n0 = len(df)
    log = []

    # coords required (for enrichment) — drop coordless (the leftover 9 condo + 2 commercial)
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"]).copy()
    log.append(("have coords", len(df)))

    # price parse + bounds
    df["price_php"] = df["price"].map(parse_price)
    df = df[df["price_php"].notna()].copy()
    df = df[df["price_php"].between(PRICE_MIN, PRICE_MAX)].copy()
    log.append((f"price in [{PRICE_MIN:,}-{PRICE_MAX:,}]", len(df)))

    # 6-LGU filter via city map
    df["city"] = df["city"].map(CITY_MAP)
    df = df[df["city"].notna()].copy()
    log.append(("6-LGU (city map)", len(df)))

    # residential-only + type recode
    df["property_type"] = df.apply(lambda r: infer_type(r["title"], r["property_type_raw"]), axis=1)
    df = df[df["property_type"].notna()].copy()
    log.append(("residential type recode", len(df)))

    # spatial cap (max 3 per ~11m cell) — flags barangay-centroid pile-ups
    df["rlat"], df["rlon"] = df["latitude"].round(4), df["longitude"].round(4)
    before_cap = len(df)
    df = (df.sort_values(["rlat", "rlon", "price_php"], kind="stable")
            .groupby(["rlat", "rlon"], sort=False, group_keys=False).head(SPATIAL_CAP).copy())
    cap_dropped = before_cap - len(df)
    log.append((f"spatial cap (-{cap_dropped})", len(df)))

    # dedup vs existing ABT by (property_name, address)
    existing = {combo_key(r.property_name, r.address) for r in abt.itertuples(index=False)}
    df = df[~df.apply(lambda r: combo_key(r["title"], r["street_address"]) in existing, axis=1)].copy()
    df = df.drop_duplicates(subset=["street_address", "price_php", "property_type"], keep="first").copy()
    log.append(("dedup vs ABT", len(df)))

    # ---- build base columns ----
    out = pd.DataFrame(index=df.index)
    next_id = int(abt["property_id"].max()) + 1
    out["property_id"] = np.arange(next_id, next_id + len(df))
    out["source"] = "Lamudi_playwright_2026-06"
    out["price_type"] = "open_market"
    out["property_name"] = df["title"].map(norm_txt)
    out["address"] = df["street_address"].map(norm_txt)
    out["city"] = df["city"].values
    out["property_type"] = df["property_type"].values
    # Canonical area convention (Decision 1 + abt_clean audit): consolidate the
    # usable area into floor_area_sqm (floor area first, lot-area fallback so
    # vacant lots get their lot area), keep lot_area_sqm 100% null, and set
    # area_sqm == floor_area_sqm.
    raw_floor = pd.to_numeric(df["floor_area_sqm"], errors="coerce").values
    raw_lot = pd.to_numeric(df["lot_area_sqm"], errors="coerce").values
    consolidated = pd.Series(np.where(pd.isna(raw_floor), raw_lot, raw_floor), index=out.index)
    out["lot_area_sqm"] = np.nan
    out["floor_area_sqm"] = consolidated
    out["area_sqm"] = consolidated
    out["bedrooms"] = pd.to_numeric(df["bedrooms"], errors="coerce").values
    out["bathrooms"] = pd.to_numeric(df["bathrooms"], errors="coerce").values
    out["price_php"] = df["price_php"].values
    out["latitude"] = df["latitude"].values
    out["longitude"] = df["longitude"].values
    out["geocode_source"] = "Lamudi_pin_or_google_geocode"
    out["price_outlier_flag"] = False
    valid_area = out["area_sqm"].notna() & (out["area_sqm"] > 0)
    out["price_per_sqm"] = np.where(valid_area, out["price_php"] / out["area_sqm"], np.nan)
    out["log_price"] = np.where(out["price_per_sqm"] > 0, np.log(out["price_per_sqm"]), np.nan)
    out["is_mactan_island"] = (out["city"] == "Lapu-Lapu City").astype(int)
    out["is_vacant_lot"] = (out["property_type"] == "Vacant Lot").astype(int)
    out["bedrooms_imputed"] = out["bedrooms"].isna().astype(int)
    out["bathrooms_imputed"] = out["bathrooms"].isna().astype(int)
    out["floor_area_imputed"] = out["area_sqm"].isna().astype(int)
    out["market_segment"] = "open_market"

    # ---- BIR zonal join (canonical reverse-geocode + join) ----
    bir_summary = pd.read_csv(BIR_SUMMARY_PATH)
    out = reverse_geocode_abt(out, api_key)            # adds barangay_geocoded
    out = join_bir_to_abt(out, bir_summary)            # adds bir_zonal_* (+ rr_log)
    out["valuation_gap"] = out["price_per_sqm"] - out["bir_zonal_rr_median"]

    # ---- align to abt_clean schema; enrichment cols left empty ----
    for col in abt.columns:
        if col not in out.columns:
            out[col] = np.nan
    out = out.reindex(columns=abt.columns)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_PATH, index=False)

    # ---- report ----
    print("\n=== FILTER FUNNEL ===")
    print(f"  raw scrape: {n0}")
    for label, n in log:
        print(f"  {label:32s} {n}")
    print(f"\n  staged rows: {len(out)}  ->  {OUT_PATH.relative_to(THESIS_DIR)}")
    print("\n=== staged property_type ===")
    print(out["property_type"].value_counts())
    print("\n=== staged city ===")
    print(out["city"].value_counts())
    print("\n=== price_per_sqm fill by type ===")
    for pt, g in out.groupby("property_type"):
        print(f"  {pt:16s} ppsqm {g['price_per_sqm'].notna().sum()}/{len(g)} | "
              f"bir {g['bir_zonal_rr_median'].notna().sum()}/{len(g)}")
    print(f"\n  spatial cap dropped: {cap_dropped} (barangay-centroid / duplicate-pin rows)")
    print(f"  enrichment cols (dist_*/mcrai_*/spatial_lag) left empty for canonical scripts.")


if __name__ == "__main__":
    main()
