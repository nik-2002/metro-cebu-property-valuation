"""
Data Cleaning Script — Pag-IBIG OPA Floor Price Dataset
========================================================
Input:  Data/raw/floor_price/pagibig/pagibig_cebu_province_all.csv
Output: Data/processed/floor_price/pagibig_clean.csv

Cleaning steps:
  1. Profile data quality
  2. Remove strict duplicates (same property + price + area)
  3. Normalize Price_PHP → float
  4. Standardize occupancy status
  5. Standardize property type
  6. Convert area fields to float (0 → NaN for condos where lot area = 0)
  7. Parse auction date
  8. Add Price_per_sqm derived column (floor area preferred, lot area fallback)
  9. Add Discount_Category label
 10. Save to processed folder

Usage:
    conda run -n webscrape python clean_pagibig.py
"""

import csv
import re
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
RAW_FILE  = Path(__file__).parent.parent.parent / "raw/floor_price/pagibig/pagibig_cebu_province_all.csv"
OUT_DIR   = Path(__file__).parent
OUT_FILE  = OUT_DIR / "pagibig_clean.csv"

OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def to_float(val: str) -> float | None:
    if not val or val.strip() == "":
        return None
    try:
        return float(re.sub(r"[^\d.]", "", val))
    except ValueError:
        return None


# Standardize property type labels
PROP_TYPE_MAP = {
    "condominium":                 "Condominium",
    "row house - end with firewall":"Row House (End/Firewall)",
    "row house":                   "Row House",
    "townhouse - end with firewall":"Townhouse (End/Firewall)",
    "townhouse":                   "Townhouse",
    "town house":                  "Townhouse",
    "single attached":             "Single Attached",
    "single detached":             "Single Detached",
    "lot only":                    "Lot Only",
    "house and lot":               "House and Lot",
    "apartment":                   "Apartment",
}

def normalize_prop_type(raw: str) -> str:
    normalized = raw.strip().lower()
    for key, label in PROP_TYPE_MAP.items():
        if key in normalized:
            return label
    return raw.strip().title()  # fallback: title-case it


# Standardize occupancy status
OCCUPANCY_MAP = {
    "unoccupied":      "Unoccupied",
    "vacant":          "Unoccupied",
    "occupied/closed": "Occupied/Closed",
    "occupied":        "Occupied",
}

def normalize_occupancy(raw: str) -> str:
    lower = raw.strip().lower()
    for key, label in OCCUPANCY_MAP.items():
        if key in lower:
            return label
    return raw.strip().title() if raw.strip() else ""


# Parse auction date to ISO range string
MONTH_MAP = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04",
    "may": "05", "jun": "06", "jul": "07", "aug": "08",
    "sep": "09", "oct": "10", "nov": "11", "dec": "12",
}

def parse_date_range(raw: str) -> tuple[str, str]:
    """
    Parse 'Mar. 30, 2026 - Apr. 3, 2026' → ('2026-03-30', '2026-04-03')
    Returns ('', '') on failure.
    """
    pattern = (
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\.?\s+(\d{1,2}),\s*(\d{4})"
    )
    matches = re.findall(pattern, raw, re.IGNORECASE)
    if len(matches) >= 2:
        m1, d1, y1 = matches[0]
        m2, d2, y2 = matches[1]
        start = f"{y1}-{MONTH_MAP[m1[:3].lower()]}-{int(d1):02d}"
        end   = f"{y2}-{MONTH_MAP[m2[:3].lower()]}-{int(d2):02d}"
        return start, end
    elif len(matches) == 1:
        m1, d1, y1 = matches[0]
        start = f"{y1}-{MONTH_MAP[m1[:3].lower()]}-{int(d1):02d}"
        return start, ""
    return "", ""


# ---------------------------------------------------------------------------
# LOAD
# ---------------------------------------------------------------------------
print("=" * 55)
print("  Pag-IBIG OPA Data Cleaner")
print("=" * 55)

with open(RAW_FILE, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print(f"\n📂 Loaded {len(rows)} raw rows from {RAW_FILE.name}")


# ---------------------------------------------------------------------------
# PROFILE
# ---------------------------------------------------------------------------
prices = [float(r["Price_PHP"]) for r in rows if r["Price_PHP"]]
with_price = len(prices)
dup_keys = [(r["Property_Name"], r["City"], r["Price_PHP"], r["Floor_Area_sqm"]) for r in rows]
n_dups = len(dup_keys) - len(set(dup_keys))

print(f"\n📊 Raw Data Profile:")
print(f"   Rows:              {len(rows)}")
print(f"   With Price:        {with_price}")
print(f"   Strict duplicates: {n_dups}")
if prices:
    print(f"   Price range:       ₱{min(prices):,.0f} – ₱{max(prices):,.0f}")
    sp = sorted(prices)
    print(f"   Median price:      ₱{sp[len(sp)//2]:,.0f}")


# ---------------------------------------------------------------------------
# STEP 1 — Deduplicate
# ---------------------------------------------------------------------------
seen = set()
deduped = []
for r in rows:
    key = (r["Property_Name"], r["City"], r["Price_PHP"], r["Floor_Area_sqm"], r["Auction_Category"])
    if key not in seen:
        seen.add(key)
        deduped.append(r)

print(f"\n🔁 After dedup: {len(deduped)} rows (removed {len(rows) - len(deduped)})")


# ---------------------------------------------------------------------------
# STEPS 2–9 — Clean each row
# ---------------------------------------------------------------------------
cleaned = []
skipped = 0

for r in deduped:
    # --- Price ---
    price = to_float(r["Price_PHP"])
    if price is None or price <= 0:
        skipped += 1
        continue  # skip rows without a valid price

    # --- Areas ---
    lot_area   = to_float(r["Lot_Area_sqm"])
    floor_area = to_float(r["Floor_Area_sqm"])

    # 0 is valid for condos (no lot), but None-ify true zeros for lot-based
    lot_area   = lot_area   if (lot_area   is not None and lot_area   > 0) else None
    floor_area = floor_area if (floor_area is not None and floor_area > 0) else None

    # --- Price per sqm ---
    area_for_psm = floor_area or lot_area
    price_per_sqm = round(price / area_for_psm, 2) if area_for_psm else None

    # --- Property type ---
    prop_type = normalize_prop_type(r["Property_Type"])

    # --- Occupancy ---
    occupancy = normalize_occupancy(r["Occupancy_Status"])

    # --- Dates ---
    date_start, date_end = parse_date_range(r["Auction_Date"])

    # --- Auction discount label ---
    cat = r["Auction_Category"]
    if "First" in cat:
        discount_label = "No Discount (First Auction)"
        discount_pct   = 0
    elif "Second" in cat:
        discount_label = "Up to 30% Discount (Second Auction)"
        discount_pct   = 30
    else:  # Negotiated Sale
        discount_label = "Up to 45% Discount (Negotiated Sale)"
        discount_pct   = 45

    cleaned.append({
        "City":               r["City"],
        "Auction_Category":   cat,
        "Discount_Pct_Max":   discount_pct,
        "Property_Name":      r["Property_Name"].strip().upper(),
        "Property_Type":      prop_type,
        "Lot_Area_sqm":       lot_area,
        "Floor_Area_sqm":     floor_area,
        "Price_PHP":          price,
        "Price_per_sqm":      price_per_sqm,
        "Occupancy_Status":   occupancy,
        "Auction_Date_Start": date_start,
        "Auction_Date_End":   date_end,
        "Source":             "Pag-IBIG OPA",
        "Scraped_Date":       "2026-03-24",
    })

print(f"🧹 Cleaned: {len(cleaned)} valid rows (skipped {skipped} without price)")


# ---------------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------------
FIELDNAMES = [
    "City", "Auction_Category", "Discount_Pct_Max",
    "Property_Name", "Property_Type",
    "Lot_Area_sqm", "Floor_Area_sqm",
    "Price_PHP", "Price_per_sqm",
    "Occupancy_Status",
    "Auction_Date_Start", "Auction_Date_End",
    "Source", "Scraped_Date",
]

with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(cleaned)

print(f"\n💾 Saved → {OUT_FILE}")


# ---------------------------------------------------------------------------
# FINAL SUMMARY
# ---------------------------------------------------------------------------
prices_clean = [r["Price_PHP"] for r in cleaned]
psm_vals = [r["Price_per_sqm"] for r in cleaned if r["Price_per_sqm"]]

print(f"\n✅ Final Summary:")
print(f"   Rows:              {len(cleaned)}")
print(f"   Price range:       ₱{min(prices_clean):,.0f} – ₱{max(prices_clean):,.0f}")
if psm_vals:
    print(f"   Price/sqm range:   ₱{min(psm_vals):,.0f} – ₱{max(psm_vals):,.0f}")
    sp = sorted(psm_vals)
    print(f"   Median price/sqm:  ₱{sp[len(sp)//2]:,.0f}")

print(f"\n   By City:")
from collections import Counter
city_counts = Counter(r["City"] for r in cleaned)
for city, n in sorted(city_counts.items(), key=lambda x: -x[1]):
    sub = [r for r in cleaned if r["City"] == city]
    avg_p = sum(r["Price_PHP"] for r in sub) / len(sub)
    print(f"   {city:<30} {n:>4} listings  avg ₱{avg_p:>12,.0f}")

print(f"\n   By Auction Category:")
cat_counts = Counter(r["Auction_Category"] for r in cleaned)
for cat, n in cat_counts.most_common():
    print(f"   {cat:<35} {n}")

print(f"\n   By Property Type:")
type_counts = Counter(r["Property_Type"] for r in cleaned)
for t, n in type_counts.most_common():
    print(f"   {str(t):<35} {n}")

print("\n🎉 Done!")
