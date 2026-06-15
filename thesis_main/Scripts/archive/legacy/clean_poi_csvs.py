#!/usr/bin/env python3
"""One-off cleanup for existing POI amenity CSVs before re-fetching."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

METRO_CEBU_BBOX = {"lat_min": 10.10, "lat_max": 10.45, "lon_min": 123.70, "lon_max": 124.10}
TARGET_LGUS = {"Cebu City", "Mandaue City", "Lapu-Lapu City", "Talisay City", "Minglanilla", "Consolacion"}
AMENITIES_DIR = Path(__file__).resolve().parents[1] / "Data" / "amenities"
BBOX_ONLY_FILES = ("education", "finance", "grocery", "health", "security")
LGU_FILES = ("recreation", "retail_density", "tourism")


def within_metro_cebu_bbox(lat: float, lon: float) -> bool:
    return (METRO_CEBU_BBOX["lat_min"] <= lat <= METRO_CEBU_BBOX["lat_max"] and
            METRO_CEBU_BBOX["lon_min"] <= lon <= METRO_CEBU_BBOX["lon_max"])


def normalize_lgu(value: str) -> str:
    cleaned = value.strip().lower().replace("city of ", "")
    alias_map = {
        "cebu": "Cebu City",
        "cebu city": "Cebu City",
        "mandaue": "Mandaue City",
        "mandaue city": "Mandaue City",
        "lapu lapu city": "Lapu-Lapu City",
        "lapu-lapu": "Lapu-Lapu City",
        "lapu-lapu city": "Lapu-Lapu City",
        "opu": "Lapu-Lapu City",
        "talisay": "Talisay City",
        "talisay city": "Talisay City",
        "minglanilla": "Minglanilla",
        "consolacion": "Consolacion",
    }
    return alias_map.get(cleaned, value.strip())


def apply_bbox_filter(frame: pd.DataFrame) -> pd.DataFrame:
    filtered = frame.dropna(subset=["lat", "lon"]).copy()
    filtered["lat"] = pd.to_numeric(filtered["lat"], errors="coerce")
    filtered["lon"] = pd.to_numeric(filtered["lon"], errors="coerce")
    filtered = filtered.dropna(subset=["lat", "lon"])
    mask = filtered.apply(lambda row: within_metro_cebu_bbox(float(row["lat"]), float(row["lon"])), axis=1)
    return filtered.loc[mask].copy()


def summarize_and_write(name: str, original_count: int, cleaned: pd.DataFrame, path: Path) -> int:
    retained = len(cleaned)
    dropped = original_count - retained
    percent = (dropped / original_count * 100) if original_count else 0.0
    cleaned.to_csv(path, index=False)
    print(f"  {name}: {dropped} rows dropped ({percent:.1f}%), {retained} retained")
    return dropped


def cleanup_bbox_only_files(names: Iterable[str]) -> int:
    total_dropped = 0
    for name in names:
        path = AMENITIES_DIR / f"{name}.csv"
        frame = pd.read_csv(path)
        cleaned = apply_bbox_filter(frame)
        total_dropped += summarize_and_write(name, len(frame), cleaned, path)
    return total_dropped


def cleanup_lgu_files(names: Iterable[str]) -> int:
    total_dropped = 0
    for name in names:
        path = AMENITIES_DIR / f"{name}.csv"
        frame = pd.read_csv(path)
        cleaned = apply_bbox_filter(frame)
        cleaned["lgu"] = cleaned["lgu"].fillna("").map(lambda value: normalize_lgu(str(value)))
        cleaned = cleaned.loc[cleaned["lgu"].isin(TARGET_LGUS)].copy()
        total_dropped += summarize_and_write(name, len(frame), cleaned, path)
    return total_dropped


def main() -> None:
    total_dropped = 0
    total_dropped += cleanup_bbox_only_files(BBOX_ONLY_FILES)
    total_dropped += cleanup_lgu_files(LGU_FILES)
    print(f"Total rows dropped across 9 files: {total_dropped}")


if __name__ == "__main__":
    main()
