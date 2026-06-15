"""Fetch Metro Cebu LGU administrative boundary polygons from Geoboundaries
and verify ABT point-in-polygon coverage.

Uses requests + shapely only. All coordinates are WGS84 (EPSG:4326)
lat/lon throughout.

Output:
    thesis_main/Data/GIS/lgu_boundaries.geojson  — 6 LGU boundary polygons
"""

from __future__ import annotations

import json
import os

import pandas as pd
import requests
from shapely.geometry import Point, shape

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
THESIS_DIR = os.path.dirname(SCRIPT_DIR)
ABT_PATH   = os.path.join(THESIS_DIR, "Data", "processed", "abt_clean.csv")
GIS_DIR    = os.path.join(THESIS_DIR, "Data", "GIS")

GEOBOUNDARIES_API = "https://www.geoboundaries.org/api/current/gbOpen/PHL/ADM3/"
HEADERS = {"User-Agent": "thesis-metro-cebu-valuation/1.0 (academic research)"}

SHAPE_NAME_MAP = {
    "Cebu City":      "Cebu City",
    "Mandaue City":   "Mandaue City",
    "Lapu-Lapu City": "Lapu-Lapu City",
    "City of Talisay": "Talisay City",
    "Minglanilla":    "Minglanilla",
    "Consolacion":    "Consolacion",
}

CEBU_LAT = (10.1, 10.5)
CEBU_LON = (123.70, 124.20)


def fetch_boundaries() -> list[dict]:
    print("Fetching Geoboundaries metadata...")
    meta_response = requests.get(GEOBOUNDARIES_API, headers=HEADERS, timeout=60)
    meta_response.raise_for_status()
    meta_payload = meta_response.json()

    if isinstance(meta_payload, list):
        meta = next(
            (
                item
                for item in meta_payload
                if isinstance(item, dict) and item.get("gjDownloadURL")
            ),
            None,
        )
    elif isinstance(meta_payload, dict):
        meta = meta_payload if meta_payload.get("gjDownloadURL") else None
    else:
        meta = None

    if meta is None:
        raise ValueError("Geoboundaries metadata did not include gjDownloadURL")

    url = meta["gjDownloadURL"]
    print("Downloading full-resolution PHL ADM3 boundaries from Geoboundaries...")
    response = requests.get(url, headers=HEADERS, timeout=300)
    response.raise_for_status()
    geojson = response.json()
    source_features = geojson.get("features", [])
    print(f"  Total features in PHL ADM3: {len(source_features)}")

    matched_features: list[dict] = []
    matched_lgus: set[str] = set()

    for feature in source_features:
        properties = feature.get("properties", {})
        shape_name = properties.get("shapeName")
        if shape_name not in SHAPE_NAME_MAP or shape_name in matched_lgus:
            continue

        geom = shape(feature.get("geometry"))
        centroid = geom.centroid
        if not (
            CEBU_LAT[0] <= centroid.y <= CEBU_LAT[1]
            and CEBU_LON[0] <= centroid.x <= CEBU_LON[1]
        ):
            continue

        lgu_label = SHAPE_NAME_MAP[shape_name]
        bounds = geom.bounds
        print(
            f"  {lgu_label}: {geom.geom_type}  "
            f"lat [{bounds[1]:.3f}, {bounds[3]:.3f}]  "
            f"lon [{bounds[0]:.3f}, {bounds[2]:.3f}]"
        )
        matched_features.append({
            "type": "Feature",
            "geometry": feature.get("geometry"),
            "properties": {
                "lgu": lgu_label,
                "source": "Geoboundaries ADM3 full",
            },
        })
        matched_lgus.add(shape_name)

    missing_lgus = [
        lgu_label
        for lgu_label in SHAPE_NAME_MAP.values()
        if lgu_label not in {feature["properties"]["lgu"] for feature in matched_features}
    ]
    if missing_lgus:
        print(f"  WARNING: missing expected LGUs: {', '.join(missing_lgus)}")
    else:
        print("  [all 6 LGUs matched]")

    return matched_features


def save_geojson(features: list[dict]) -> str:
    os.makedirs(GIS_DIR, exist_ok=True)
    out_path = os.path.join(GIS_DIR, "lgu_boundaries.geojson")
    geojson = {"type": "FeatureCollection", "features": features}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False)
    print(f"\nSaved: {out_path}  ({len(features)} LGU polygons)")
    return out_path


def abt_point_in_polygon_check(features: list[dict]) -> None:
    print("\n=== ABT POINT-IN-POLYGON CHECK ===")
    abt = pd.read_csv(ABT_PATH).dropna(subset=["latitude", "longitude"]).copy()
    lgu_geoms = {f["properties"]["lgu"]: shape(f["geometry"]) for f in features}

    def assign_lgu(row: pd.Series) -> str:
        pt = Point(row["longitude"], row["latitude"])
        for name, geom in lgu_geoms.items():
            if geom.contains(pt):
                return name
        return "UNMATCHED"

    print(f"Checking {len(abt):,} rows...")
    abt["lgu_polygon"] = abt.apply(assign_lgu, axis=1)

    lgu_order = list(SHAPE_NAME_MAP.values()) + ["UNMATCHED"]
    print(f"\n{'LGU':<20} {'Polygon match':>14} {'City column':>12} {'Delta':>8}")
    print("-" * 58)
    for lgu_name in lgu_order:
        poly_n = (abt["lgu_polygon"] == lgu_name).sum()
        city_n = (abt["city"] == lgu_name).sum() if lgu_name != "UNMATCHED" else "-"
        delta  = (poly_n - city_n) if lgu_name != "UNMATCHED" else "-"
        flag   = "  ⚠" if isinstance(delta, int) and delta != 0 else ""
        if lgu_name == "UNMATCHED":
            flag = "  ⚠" if poly_n > 0 else ""
        print(f"{lgu_name:<20} {poly_n:>14,} {str(city_n):>12} {str(delta):>8}{flag}")

    unmatched = abt[abt["lgu_polygon"] == "UNMATCHED"]
    if not unmatched.empty:
        print(f"\nUnmatched rows ({len(unmatched)}) — likely coastal/border edge cases:")
        print(unmatched[["property_id", "city", "latitude", "longitude"]]
              .head(20).to_string(index=False))


def main() -> None:
    features = fetch_boundaries()
    if not features:
        print("No boundaries fetched. Exiting.")
        return
    save_geojson(features)
    abt_point_in_polygon_check(features)


if __name__ == "__main__":
    main()
