"""
data_collection_funnel.py
=========================
Reconstructs the honest data-collection funnel for the manuscript (replaces the
stale "665 candidates" figure). Applies the CANONICAL staging filters from
stage_lamudi_batch.py to each raw Lamudi scrape file and reports how many rows
survive each stage.

Two scraper generations (Decisions 18/22/26/37/39):
  Stage 1 — legacy requests + BeautifulSoup : Data/webscraping-lamudi/lamudi_cebu_full.csv
  Stage 2 — Playwright (post-CAPTCHA, 2026-06): playwright/data/lamudi_scraped_geocoded.csv

Stage 2's dedup runs against the PRE-batch ABT (abt_clean.backup_pre_batch_2026-06.csv,
1,579 rows) to reproduce the real net-new contribution. Stage 1 is the source of that
pre-batch ABT, so it ends at unique in-scope residential listings (no vs-ABT dedup).

Read-only. Writes reference/data_collection_funnel.csv + prints the table.
"""

import re
from pathlib import Path

import numpy as np
import pandas as pd

THESIS_DIR = Path(__file__).resolve().parent.parent
LEGACY_RAW = THESIS_DIR / "Data" / "webscraping-lamudi" / "lamudi_cebu_full.csv"
PLAYWRIGHT_RAW = THESIS_DIR / "playwright" / "data" / "lamudi_scraped_geocoded.csv"
PREBATCH_ABT = THESIS_DIR / "Data" / "processed" / "abt_clean.backup_pre_batch_2026-06.csv"
OUT = THESIS_DIR / "reference" / "data_collection_funnel.csv"

PRICE_MIN, PRICE_MAX = 500_000, 500_000_000
SPATIAL_CAP = 3

CITY_MAP = {
    "Cebu": "Cebu City", "Cebu City": "Cebu City",
    "Lapu-Lapu": "Lapu-Lapu City", "Lapu-Lapu City": "Lapu-Lapu City",
    "Mandaue": "Mandaue City", "Mandaue City": "Mandaue City",
    "Talisay": "Talisay City", "Talisay City": "Talisay City",
    "Minglanilla": "Minglanilla", "Consolacion": "Consolacion",
}
TYPE_RULES = [
    (r"\bcondo(?:minium)?\b|\bapartment\b|\bpenthouse\b|\bstudio\b", "Condominium"),
    (r"\bsingle[-\s]?detached\b|\bdetached\s+house\b", "Single Detached"),
    (r"\btownhouse\b|\bduplex\b|\browhouse\b|\bsingle[-\s]?attached\b", "Townhouse"),
    (r"\bvacant\s+lot\b|\blot\s+only\b|\bresidential\s+lot\b|\bland\s+for\s+sale\b", "Vacant Lot"),
    (r"\bhouse\s*(?:and|&)\s*lot\b|\bvilla\b|\bhouse\b", "House and Lot"),
]
EXCLUDED_TITLE = re.compile(r"commercial|office|warehouse|farm|industrial|beach house", re.IGNORECASE)
CAT_FALLBACK = {"land": "Vacant Lot", "condo": "Condominium", "apartment": "Condominium",
                "house": "House and Lot"}


def norm_txt(v):
    return "" if pd.isna(v) else re.sub(r"\s+", " ", str(v)).strip()


def cat_token(raw):
    parts = [p.strip() for p in str(raw).split("|")]
    return parts[1].lower().split("/")[0] if len(parts) > 1 else ""


def infer_type(title, raw):
    t = norm_txt(title)
    if t and EXCLUDED_TITLE.search(t):
        return None
    for pat, label in TYPE_RULES:
        if t and re.search(pat, t, re.IGNORECASE):
            return label
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


def funnel(path, label, dedup_ref=None):
    df = pd.read_csv(path)
    rows = [(label, "raw scrape", len(df))]

    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"]).copy()
    rows.append((label, "has coordinates", len(df)))

    df["price_php"] = df["price"].map(parse_price)
    df = df[df["price_php"].notna() & df["price_php"].between(PRICE_MIN, PRICE_MAX)].copy()
    rows.append((label, "valid price 500k-500M", len(df)))

    df["city"] = df["city"].map(CITY_MAP)
    df = df[df["city"].notna()].copy()
    rows.append((label, "inside 6 LGUs", len(df)))

    df["property_type"] = df.apply(lambda r: infer_type(r.get("title"), r.get("property_type_raw")), axis=1)
    df = df[df["property_type"].notna()].copy()
    rows.append((label, "residential recode", len(df)))

    df["rlat"], df["rlon"] = df["latitude"].round(4), df["longitude"].round(4)
    df = (df.sort_values(["rlat", "rlon", "price_php"], kind="stable")
            .groupby(["rlat", "rlon"], sort=False, group_keys=False).head(SPATIAL_CAP).copy())
    rows.append((label, f"after spatial cap (<= {SPATIAL_CAP}/pin)", len(df)))

    # self-dedup on (address, price, type) — removes page-level repeats
    df = df.drop_duplicates(subset=["street_address", "price_php", "property_type"], keep="first").copy()
    rows.append((label, "unique in-scope listings", len(df)))

    if dedup_ref is not None:
        abt = pd.read_csv(dedup_ref)
        existing = {combo_key(r.property_name, r.address) for r in abt.itertuples(index=False)}
        df = df[~df.apply(lambda r: combo_key(r["title"], r["street_address"]) in existing, axis=1)].copy()
        rows.append((label, "NET-NEW vs pre-batch ABT", len(df)))

    return rows


def main():
    all_rows = []
    print("=" * 70)
    print("DATA COLLECTION FUNNEL")
    print("=" * 70)

    all_rows += funnel(LEGACY_RAW, "Stage 1: legacy requests+BeautifulSoup")
    all_rows += funnel(PLAYWRIGHT_RAW, "Stage 2: Playwright (post-CAPTCHA)", dedup_ref=PREBATCH_ABT)

    out = pd.DataFrame(all_rows, columns=["stage", "filter", "rows_surviving"])
    out.to_csv(OUT, index=False)

    cur = None
    for _, r in out.iterrows():
        if r["stage"] != cur:
            cur = r["stage"]; print(f"\n{cur}")
        print(f"   {r['filter']:34s} {r['rows_surviving']:>8,}")
    print(f"\nWrote {OUT.relative_to(THESIS_DIR)}")
    print("\nNote: Stage 1 is the source of the 1,579-row pre-batch ABT, so it ends at unique")
    print("in-scope listings (further cleaning/geocoding/BIR steps brought it to the 1,579).")
    print("Stage 2's NET-NEW is dedup'd against that 1,579-row pre-batch ABT.")


if __name__ == "__main__":
    main()
