from __future__ import annotations

import json
import math
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
        parsed = float(text)
    except ValueError:
        return None
    # NaN/inf are not valid JSON; emit null so the browser can always parse the file.
    if math.isnan(parsed) or math.isinf(parsed):
        return None
    return parsed


def round_or_none(value: float | None, ndigits: int = 0) -> float | None:
    return None if value is None else round(value, ndigits)


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

    # The per-stratum files define the listing set + stratum; the master ABT carries
    # the geocoded barangay and the full feature record (beds/baths, MCRAI, distances,
    # BIR, spatial lag). Pull both from abt_clean keyed by property_id.
    abt_by_id: dict[str, dict[str, str]] = {}
    for row in read_csv_rows(PROCESSED / "abt_clean.csv"):
        property_id = clean_text(row.get("property_id"))
        if property_id and property_id not in abt_by_id:
            abt_by_id[property_id] = row

    def truthy_flag(value: object) -> bool:
        return clean_text(value).lower() in ("1", "1.0", "true", "yes")

    records = []
    for row in rows:
        property_id = clean_text(row.get("property_id"))
        source = abt_by_id.get(property_id, {})
        mcrai = {
            short: round_or_none(clean_float(source.get(col)), 3)
            for col, short in MCRAI_COLS.items()
        }
        dist = {
            short: round_or_none(clean_float(source.get(col)), 0)
            for col, short in DIST_COLS.items()
        }
        records.append(
            {
                "propertyId": int(property_id),
                "latitude": clean_required_float(row.get("latitude")),
                "longitude": clean_required_float(row.get("longitude")),
                "pricePerSqm": clean_required_float(row.get("price_per_sqm")),
                "pricePhp": clean_float(row.get("price_php")),
                "city": clean_text(row.get("city")),
                "barangay": clean_text(source.get("barangay_geocoded")),
                "propertyType": clean_text(row.get("property_type")),
                "stratum": clean_text(row.get("stratum")),
                "address": clean_text(row.get("address")),
                "areaSqm": clean_float(row.get("area_sqm")),
                # Full ABT feature record for the in-depth property breakdown.
                "bedrooms": clean_float(source.get("bedrooms")),
                "bathrooms": clean_float(source.get("bathrooms")),
                "bedroomsImputed": truthy_flag(source.get("bedrooms_imputed")),
                "bathroomsImputed": truthy_flag(source.get("bathrooms_imputed")),
                "mcrai": mcrai,
                "dist": dist,
                "birZonalRr": round_or_none(clean_float(source.get("bir_zonal_rr_median")), 0),
                "spatialLag": round_or_none(clean_float(source.get("spatial_lag_price")), 0),
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


# Feature columns aggregated per barangay (averaged over the listings that fall
# inside each polygon). Short keys keep the JSON small; the frontend maps them to
# readable labels.
MCRAI_COLS = {
    "mcrai_education": "education",
    "mcrai_grocery": "grocery",
    "mcrai_health": "health",
    "mcrai_hospitals": "hospitals",
    "mcrai_recreation": "recreation",
    "mcrai_security": "security",
    "mcrai_tourism": "tourism",
    "mcrai_retail_density": "retail_density",
    "mcrai_composite": "composite",
}
DIST_COLS = {
    "dist_cebu_business_park_m": "cbp",
    "dist_mandaue_cbd_m": "mandaue",
    "dist_mactan_cbd_m": "mactan",
    "dist_srp_m": "srp",
    "dist_talisay_tabunok_m": "talisay",
    "dist_consolacion_m": "consolacion",
    "dist_naga_city_m": "naga",
    "dist_airport_m": "airport",
    "dist_to_trunk_road_m": "trunk_road",
    "dist_to_primary_road_m": "primary_road",
}


def export_barangay_features() -> None:
    """Aggregate the ABT's location features to each barangay polygon.

    The barangay surface files carry only price/confidence per polygon. To explain
    *why* a barangay sits in its price band, we average the amenity (MCRAI) scores,
    CBD/road distances, BIR zonal value, and neighbourhood price level of the
    listings inside each polygon. Listings are matched to polygons by point-in-
    polygon (robust to the barangay-name mismatch between the surface's official
    PSA names and the ABT's reverse-geocoded names). Keyed by adm4_pcode, which the
    surface geojson carries and is stable across all three archetypes.
    """
    import math

    import pandas as pd
    from shapely.geometry import Point, shape
    from shapely.strtree import STRtree

    def num(value, ndigits: int = 0):
        """Round to JSON-safe float; NaN/inf -> None (JSON null), never bare NaN."""
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            return None
        if math.isnan(parsed) or math.isinf(parsed):
            return None
        return round(parsed, ndigits)

    surface = json.loads((APP_DATA / "barangay_surface_sdh.geojson").read_text())
    polygons, pcodes = [], []
    for feature in surface["features"]:
        pcode = (feature.get("properties") or {}).get("adm4_pcode")
        geometry = feature.get("geometry")
        if pcode and geometry:
            polygons.append(shape(geometry))
            pcodes.append(pcode)
    tree = STRtree(polygons)

    abt = pd.read_csv(PROCESSED / "abt_clean.csv")
    abt = abt.dropna(subset=["latitude", "longitude", "price_per_sqm"]).reset_index(drop=True)

    matched = []
    for lat, lon in zip(abt["latitude"].to_numpy(), abt["longitude"].to_numpy()):
        point = Point(float(lon), float(lat))
        # STRtree applies the predicate as point.predicate(polygon); query by bbox
        # intersection, then confirm the polygon actually covers the point.
        pcode = None
        for idx in tree.query(point, predicate="intersects"):
            if polygons[int(idx)].covers(point):
                pcode = pcodes[int(idx)]
                break
        matched.append(pcode)
    abt["_pcode"] = matched

    barangays: dict[str, dict] = {}
    for pcode, group in abt.dropna(subset=["_pcode"]).groupby("_pcode"):
        record: dict = {"n_listings": int(len(group))}
        record["mcrai"] = {
            short: num(group[col].mean(), 3)
            for col, short in MCRAI_COLS.items()
            if col in group
        }
        record["dist"] = {
            short: num(group[col].mean(), 0)
            for col, short in DIST_COLS.items()
            if col in group
        }
        if "bir_zonal_rr_median" in group:
            record["bir_zonal_rr_median"] = num(group["bir_zonal_rr_median"].mean(), 0)
        if "spatial_lag_price" in group:
            record["spatial_lag_price"] = num(group["spatial_lag_price"].mean(), 0)
        record["listing_price_median"] = num(group["price_per_sqm"].median(), 0)
        record["listing_price_min"] = num(group["price_per_sqm"].min(), 0)
        record["listing_price_max"] = num(group["price_per_sqm"].max(), 0)
        barangays[str(pcode)] = record

    # Metro-wide max per MCRAI category so the frontend can draw comparable bars.
    mcrai_max = {
        short: num(abt[col].max(), 3)
        for col, short in MCRAI_COLS.items()
        if col in abt
    }

    payload = {"mcrai_max": mcrai_max, "barangays": barangays}
    (PUBLIC_DATA / "barangay_features.json").write_text(json.dumps(payload, separators=(",", ":")))
    print(f"Exported barangay features for {len(barangays)} barangays (point-in-polygon join)")


def main() -> None:
    PUBLIC_DATA.mkdir(parents=True, exist_ok=True)
    export_listings()
    export_pois()
    shutil.copyfile(APP_DATA / "lgu_boundaries.geojson", PUBLIC_DATA / "lgu_boundaries.geojson")
    for filename in SURFACE_FILES:
        shutil.copyfile(APP_DATA / filename, PUBLIC_DATA / filename)
    export_barangay_features()
    print("Exported listings, POIs, LGU boundaries, barangay price surfaces, and barangay features")


if __name__ == "__main__":
    main()
