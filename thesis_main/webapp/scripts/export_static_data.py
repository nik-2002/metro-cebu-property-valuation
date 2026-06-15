from __future__ import annotations

import json
import shutil
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEBAPP = Path(__file__).resolve().parents[1]
PUBLIC_DATA = WEBAPP / "public" / "data"
PROCESSED = ROOT / "Data" / "processed"
POI_DIR = ROOT / "QGIS" / "data" / "mcrai_pois"
APP_DATA = ROOT / "app" / "data"

STRATA_FILES = {
    "Condominium": "abt_condo.csv",
    "Houses": "abt_houses.csv",
    "Vacant Lot": "abt_lot.csv",
}

POI_FILES = {
    "Grocery": "mcrai_grocery_pois.geojson",
    "Retail": "mcrai_retail_density_pois.geojson",
    "Health": "mcrai_health_pois.geojson",
    "Hospitals": "mcrai_hospitals_pois.geojson",
    "Education": "mcrai_education_pois.geojson",
    "Security": "mcrai_security_pois.geojson",
    "Recreation": "mcrai_recreation_pois.geojson",
    "Tourism": "mcrai_tourism_pois.geojson",
}

SURFACE_FILES = [
    "barangay_surface_sdh.geojson",
    "barangay_surface_condo.geojson",
    "barangay_surface_vacant.geojson",
]


def clean_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def clean_float(value: object) -> float | None:
    text = clean_text(value)
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def clean_required_float(value: object) -> float:
    parsed = clean_float(value)
    if parsed is None:
        raise ValueError(f"Expected numeric value, got {value!r}")
    return parsed


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def export_listings() -> None:
    rows: list[dict[str, str]] = []
    for stratum, filename in STRATA_FILES.items():
        for row in read_csv_rows(PROCESSED / filename):
            if not clean_text(row.get("latitude")) or not clean_text(row.get("longitude")):
                continue
            if not clean_text(row.get("price_per_sqm")):
                continue
            row["stratum"] = stratum
            rows.append(row)

    barangays: dict[str, str] = {}
    for row in read_csv_rows(PROCESSED / "abt_clean.csv"):
        property_id = clean_text(row.get("property_id"))
        barangay = clean_text(row.get("barangay_geocoded"))
        if property_id and barangay and property_id not in barangays:
            barangays[property_id] = barangay

    records = []
    for row in rows:
        property_id = clean_text(row.get("property_id"))
        records.append(
            {
                "propertyId": int(property_id),
                "latitude": clean_required_float(row.get("latitude")),
                "longitude": clean_required_float(row.get("longitude")),
                "pricePerSqm": clean_required_float(row.get("price_per_sqm")),
                "pricePhp": clean_float(row.get("price_php")),
                "city": clean_text(row.get("city")),
                "barangay": barangays.get(property_id, ""),
                "propertyType": clean_text(row.get("property_type")),
                "stratum": clean_text(row.get("stratum")),
                "address": clean_text(row.get("address")),
                "areaSqm": clean_float(row.get("area_sqm")),
            }
        )

    (PUBLIC_DATA / "listings.json").write_text(json.dumps(records, separators=(",", ":")))


def export_pois() -> None:
    records = []
    for category, filename in POI_FILES.items():
        path = POI_DIR / filename
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        for feature in data.get("features", []):
            geometry = feature.get("geometry") or {}
            coords = geometry.get("coordinates") or []
            if geometry.get("type") != "Point" or len(coords) < 2:
                continue
            props = feature.get("properties") or {}
            records.append(
                {
                    "category": category,
                    "longitude": float(coords[0]),
                    "latitude": float(coords[1]),
                    "amenity": clean_text(props.get("amenity", category)),
                    "amenityType": clean_text(props.get("amenity_type", "POI")),
                }
            )

    (PUBLIC_DATA / "pois.json").write_text(json.dumps(records, separators=(",", ":")))


def main() -> None:
    PUBLIC_DATA.mkdir(parents=True, exist_ok=True)
    export_listings()
    export_pois()
    shutil.copyfile(APP_DATA / "lgu_boundaries.geojson", PUBLIC_DATA / "lgu_boundaries.geojson")
    for filename in SURFACE_FILES:
        shutil.copyfile(APP_DATA / filename, PUBLIC_DATA / filename)
    print("Exported listings, POIs, LGU boundaries, and barangay price surfaces")


if __name__ == "__main__":
    main()
