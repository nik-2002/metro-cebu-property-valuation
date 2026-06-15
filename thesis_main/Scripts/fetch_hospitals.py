"""Fetch Metro Cebu hospitals from OSM and export CSV + GeoJSON outputs."""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path

import requests
from shapely.geometry import Point, shape

SCRIPT_DIR = Path(__file__).resolve().parent
THESIS_DIR = SCRIPT_DIR.parent
DATA_DIR = THESIS_DIR / "Data"
GIS_PATH = DATA_DIR / "GIS" / "lgu_boundaries.geojson"
CSV_PATH = DATA_DIR / "amenities" / "hospitals.csv"
GEOJSON_PATH = THESIS_DIR / "QGIS" / "data" / "mcrai_pois" / "mcrai_hospitals_pois.geojson"

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "thesis-metro-cebu-valuation/1.0 (academic research)"}
OVERPASS_QUERY = """[out:json][timeout:60];
(
  node["amenity"="hospital"](10.1,123.7,10.5,124.2);
  way["amenity"="hospital"](10.1,123.7,10.5,124.2);
  relation["amenity"="hospital"](10.1,123.7,10.5,124.2);
);
out center;"""


def load_lgu_geometries(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        geojson = json.load(handle)

    geoms: dict[str, object] = {}
    for feature in geojson.get("features", []):
        properties = feature.get("properties", {})
        lgu_name = properties.get("lgu")
        geometry = feature.get("geometry")
        if not lgu_name or not geometry:
            continue
        geoms[lgu_name] = shape(geometry)

    if len(geoms) != 6:
        raise ValueError(f"Expected 6 LGU polygons, found {len(geoms)} in {path}")

    return geoms


def fetch_hospital_elements() -> list[dict[str, object]]:
    time.sleep(1)
    response = requests.post(
        OVERPASS_URL,
        data={"data": OVERPASS_QUERY},
        headers=HEADERS,
        timeout=120,
    )
    response.raise_for_status()
    payload = response.json()

    hospitals: list[dict[str, object]] = []
    for element in payload.get("elements", []):
        tags = element.get("tags", {})
        if element.get("type") == "node":
            lat = element.get("lat")
            lon = element.get("lon")
        else:
            center = element.get("center", {})
            lat = center.get("lat")
            lon = center.get("lon")

        if lat is None or lon is None:
            continue

        hospitals.append(
            {
                "id": element.get("id"),
                "lat": float(lat),
                "lon": float(lon),
                "amenity_type": "hospital",
                "amenity": tags.get("name") or "Unnamed hospital",
            }
        )

    return hospitals


def filter_to_lgu_scope(rows: list[dict[str, object]], geoms: dict[str, object]) -> list[dict[str, object]]:
    filtered_rows: list[dict[str, object]] = []
    for row in rows:
        point = Point(float(row["lon"]), float(row["lat"]))
        if any(geom.contains(point) for geom in geoms.values()):
            filtered_rows.append(row)
    return filtered_rows


def save_csv(rows: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "lat", "lon", "amenity_type", "amenity"])
        writer.writeheader()
        writer.writerows(rows)


def save_geojson(rows: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    features = []
    for row in rows:
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [row["lon"], row["lat"]],
                },
                "properties": dict(row),
            }
        )

    geojson = {"type": "FeatureCollection", "features": features}
    with path.open("w", encoding="utf-8") as handle:
        json.dump(geojson, handle, ensure_ascii=False)


def main() -> None:
    hospitals = fetch_hospital_elements()
    print(f"Fetched {len(hospitals)} hospitals from OSM")

    geoms = load_lgu_geometries(GIS_PATH)
    retained = filter_to_lgu_scope(hospitals, geoms)
    dropped = len(hospitals) - len(retained)
    print(f"After LGU polygon filter: {len(retained)} hospitals retained, {dropped} dropped")

    save_csv(retained, CSV_PATH)
    print("Saved: thesis_main/Data/amenities/hospitals.csv")

    save_geojson(retained, GEOJSON_PATH)
    print("Saved: thesis_main/QGIS/data/mcrai_pois/mcrai_hospitals_pois.geojson")


if __name__ == "__main__":
    main()
