"""Filter the ABT and active amenity CSVs to the 6 Metro Cebu LGU scope.

Rows whose coordinates fall outside all 6 LGU polygons are dropped.
Files are overwritten in place only when at least one row is removed.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
from shapely.geometry import Point, shape

SCRIPT_DIR = Path(__file__).resolve().parent
THESIS_DIR = SCRIPT_DIR.parent
DATA_DIR = THESIS_DIR / "Data"
GIS_PATH = DATA_DIR / "GIS" / "lgu_boundaries.geojson"
ABT_PATH = DATA_DIR / "processed" / "abt_clean.csv"
AMENITY_DIR = DATA_DIR / "amenities"

AMENITY_FILES = [
    "education.csv",
    "grocery.csv",
    "health.csv",
    "hospitals.csv",
    "security.csv",
    "recreation.csv",
    "retail_density.csv",
    "tourism.csv",
    "transport.csv",
]


def load_lgu_geometries(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        geojson = json.load(handle)

    features = geojson.get("features", [])
    geoms: dict[str, object] = {}
    for feature in features:
        properties = feature.get("properties", {})
        lgu_name = properties.get("lgu")
        if not lgu_name:
            continue
        geoms[lgu_name] = shape(feature.get("geometry"))

    if len(geoms) != 6:
        raise ValueError(f"Expected 6 LGU polygons, found {len(geoms)} in {path}")

    return geoms


def write_if_changed(path: Path, frame: pd.DataFrame, changed: bool) -> str:
    if not changed:
        return "no changes"

    temp_path = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temp_path, index=False)
    os.replace(temp_path, path)
    return "overwritten"


def filter_csv(path: Path, geoms: dict[str, object], lat_col: str, lon_col: str) -> tuple[int, int, int, str]:
    frame = pd.read_csv(path)
    before = len(frame)

    lat = pd.to_numeric(frame[lat_col], errors="coerce")
    lon = pd.to_numeric(frame[lon_col], errors="coerce")
    valid_mask = lat.notna() & lon.notna()

    keep_mask = pd.Series(False, index=frame.index)
    valid_index = frame.index[valid_mask]
    if len(valid_index) > 0:
        inside_flags = []
        for x, y in zip(lon.loc[valid_index], lat.loc[valid_index]):
            point = Point(x, y)
            inside_flags.append(any(geom.contains(point) for geom in geoms.values()))
        keep_mask.loc[valid_index] = inside_flags

    filtered = frame.loc[keep_mask].copy()
    after = len(filtered)
    dropped = before - after
    status = write_if_changed(path, filtered, dropped > 0)
    return before, dropped, after, status


def main() -> None:
    print(f"Loading LGU polygons from {GIS_PATH.name}... (6 polygons)")
    geoms = load_lgu_geometries(GIS_PATH)

    print("\nFiltering ABT: abt_clean.csv")
    before, dropped, after, status = filter_csv(ABT_PATH, geoms, "latitude", "longitude")
    print(f"  Before: {before:,} rows")
    print(f"  Dropped: {dropped:,} rows outside LGU polygons")
    print(f"  After:  {after:,} rows  → {status}")

    print("\nFiltering amenities:")
    for filename in AMENITY_FILES:
        path = AMENITY_DIR / filename
        before, dropped, after, status = filter_csv(path, geoms, "lat", "lon")
        print(f"  {filename:<20} Before: {before:>5,}   Dropped: {dropped:>3,}   After: {after:>5,}  → {status}")

    print("\nDone. MCRAI scores must be recomputed (run compute_hansen_scores.py) after this step.")


if __name__ == "__main__":
    main()
