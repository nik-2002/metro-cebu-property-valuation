#!/usr/bin/env python3
"""One-off post-processing fixes for fetched MCRAI POI CSV anomalies."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

TARGET_LGUS = {"Cebu City", "Mandaue City", "Lapu-Lapu City", "Talisay City", "Minglanilla", "Consolacion"}
BRAND_KEYWORDS = ("7-eleven", "alfamart", "ministop", "familymart")
RECREATION_REJECTS = (
    "mall", "shopping", "parking", "car park", "office", "hotel",
    "resort", "restaurant", "cafe", "bar", "bank", "hospital",
    "clinic", "pharmacy", "hardware", "gasoline", "fuel",
    "school", "university", "residential", "apartment", "condo",
    "subdivision", "real estate",
)
TOURISM_RESIDENTIAL_REJECTS = (
    "apartment", "condo", "condominium", "for rent", "for sale",
    "for lease", "house and lot", "townhouse", "bungalow",
    "studio unit", "room for rent", "boarding house", "subdivision",
    "real estate", "property for", "residence",
    "to rent", "house for",
)
OUTPUT_COLUMNS = ["id", "lat", "lon", "amenity_type", "amenity", "lgu"]
BASE_DIR = Path(__file__).resolve().parents[1]
AMENITIES_DIR = BASE_DIR / "Data" / "amenities"
RECREATION_GEOJSON = BASE_DIR / "QGIS" / "data" / "mcrai_pois" / "mcrai_recreation_pois.geojson"


def normalize_frame(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    normalized = normalized.reindex(columns=OUTPUT_COLUMNS)
    normalized["id"] = normalized["id"].astype(str)
    normalized["amenity_type"] = normalized["amenity_type"].astype(str)
    normalized["amenity"] = normalized["amenity"].astype(str)
    normalized["lgu"] = normalized["lgu"].astype(str)
    normalized["lat"] = pd.to_numeric(normalized["lat"], errors="coerce")
    normalized["lon"] = pd.to_numeric(normalized["lon"], errors="coerce")
    normalized = normalized.dropna(subset=["id", "lat", "lon", "amenity", "lgu"])
    return normalized[OUTPUT_COLUMNS].copy()


def load_recreation_geojson() -> pd.DataFrame:
    payload = json.loads(RECREATION_GEOJSON.read_text())
    rows = [feature.get("properties", {}) for feature in payload.get("features", [])]
    return normalize_frame(pd.DataFrame(rows))


def merge_recreation() -> tuple[int, int, int, int]:
    path = AMENITIES_DIR / "recreation.csv"
    old_frame = load_recreation_geojson()
    new_frame = normalize_frame(pd.read_csv(path))
    merged = pd.concat([old_frame, new_frame], ignore_index=True)
    merged = merged.drop_duplicates(subset=["id"], keep="last")
    merged_before_filter = len(merged)
    name_lower = merged["amenity"].str.lower()
    reject_mask = name_lower.apply(lambda value: any(reject in value for reject in RECREATION_REJECTS))
    merged = merged.loc[~reject_mask].copy()
    merged = merged.loc[merged["lgu"].isin(TARGET_LGUS)].copy()
    merged = merged.sort_values(by=["lgu", "amenity", "id"], kind="stable").reset_index(drop=True)
    merged.to_csv(path, index=False)
    print(f"recreation: merged old ({len(old_frame)}) + new ({len(new_frame)}) -> {merged_before_filter} unique -> {len(merged)} after hard-reject filter")
    return len(new_frame), len(merged), len(old_frame), merged_before_filter


def retag_retail_density() -> tuple[int, int]:
    path = AMENITIES_DIR / "retail_density.csv"
    frame = normalize_frame(pd.read_csv(path))
    before = len(frame)

    def classify(row: pd.Series) -> str:
        name_lower = str(row["amenity"]).lower()
        current_type = str(row["amenity_type"])
        if any(keyword in name_lower for keyword in BRAND_KEYWORDS) or current_type == "convenience_store":
            return "convenience_store"
        if current_type == "cafe" or "cafe" in name_lower:
            return "cafe"
        if current_type == "bakery":
            return "bakery"
        return "restaurant"

    frame["amenity_type"] = frame.apply(classify, axis=1)
    frame = frame.sort_values(by=["lgu", "amenity", "id"], kind="stable").reset_index(drop=True)
    frame.to_csv(path, index=False)
    print("retail_density amenity_type counts:")
    print(frame["amenity_type"].value_counts().sort_index().to_string())
    return before, len(frame)


def clean_tourism() -> tuple[int, int, int, int]:
    path = AMENITIES_DIR / "tourism.csv"
    frame = normalize_frame(pd.read_csv(path))
    before = len(frame)
    name_lower = frame["amenity"].str.strip().str.lower()
    residential_mask = name_lower.apply(lambda value: any(reject in value for reject in TOURISM_RESIDENTIAL_REJECTS))
    n_residential = int(residential_mask.sum())
    filtered = frame.loc[~residential_mask].copy()
    dedup_key = pd.DataFrame({
        "name_key": filtered["amenity"].str.strip().str.lower(),
        "lat_key": filtered["lat"].round(5),
        "lon_key": filtered["lon"].round(5),
    })
    dedup_mask = dedup_key.duplicated(keep="first")
    n_dedup = int(dedup_mask.sum())
    filtered = filtered.loc[~dedup_mask].copy()
    filtered = filtered.sort_values(by=["lgu", "amenity", "id"], kind="stable").reset_index(drop=True)
    filtered.to_csv(path, index=False)
    print(f"tourism: {before} -> {len(filtered)} (dropped {n_residential} residential, {n_dedup} exact duplicates)")
    return before, len(filtered), n_residential, n_dedup


def print_summary(recreation_before: int, recreation_after: int, retail_before: int, retail_after: int, tourism_before: int, tourism_after: int) -> None:
    print("Category       | Before | After  | Change")
    print(f"recreation     | {recreation_before:<6} | {recreation_after:<6} | {recreation_after - recreation_before:+d} (merged + filtered)")
    print(f"retail_density | {retail_before:<6} | {retail_after:<6} | {retail_after - retail_before:+d} (labels fixed only)")
    print(f"tourism        | {tourism_before:<6} | {tourism_after:<6} | {tourism_after - tourism_before:+d} (residential removed)")


def main() -> None:
    recreation_before, recreation_after, _, _ = merge_recreation()
    retail_before, retail_after = retag_retail_density()
    tourism_before, tourism_after, _, _ = clean_tourism()
    print_summary(recreation_before, recreation_after, retail_before, retail_after, tourism_before, tourism_after)


if __name__ == "__main__":
    main()
