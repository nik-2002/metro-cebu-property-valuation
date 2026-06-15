#!/usr/bin/env python3
"""Fetch MCRAI tourism, recreation, and retail-density amenities from Google Maps Places."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

import googlemaps
import pandas as pd
from dotenv import load_dotenv

OUTPUT_COLUMNS = ["id", "lat", "lon", "amenity_type", "amenity", "lgu"]
SLEEP_BETWEEN_CALLS = 0.5
SLEEP_BETWEEN_PAGES = 2.0
REQUEST_TIMEOUT_SECS = 25
MIN_TOURISM_RATING = 3.5
TARGET_LGUS = {
    "Cebu City",
    "Mandaue City",
    "Lapu-Lapu City",
    "Talisay City",
    "Minglanilla",
    "Consolacion",
}
LGU_CENTROIDS = {
    "Cebu City": (10.3157, 123.8854),
    "Mandaue City": (10.3494, 123.9353),
    "Lapu-Lapu City": (10.3119, 123.9494),
    "Talisay City": (10.2443, 123.8416),
    "Minglanilla": (10.1931, 123.8011),
    "Consolacion": (10.3736, 123.9647),
}
METRO_CEBU_BBOX = {"lat_min": 10.10, "lat_max": 10.45, "lon_min": 123.70, "lon_max": 124.10}


def within_metro_cebu_bbox(lat: float, lon: float) -> bool:
    return (METRO_CEBU_BBOX["lat_min"] <= lat <= METRO_CEBU_BBOX["lat_max"] and
            METRO_CEBU_BBOX["lon_min"] <= lon <= METRO_CEBU_BBOX["lon_max"])


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
RETAIL_FALSE_POSITIVES = (
    "warehouse",
    "distribution",
    "wholesale",
    "depot",
    "hardware",
    "pharmacy",
    "drugstore",
    "clinic",
    "hospital",
    "gas",
    "gasoline",
    "fuel",
    "school",
    "university",
    "resort",
    "hotel",
    "office",
)

SEED_AREAS = [
    {"name": "cebu_city_central", "lgu": "Cebu City", "lat": 10.3180, "lon": 123.9050, "radius": 4500},
    {"name": "cebu_city_it_park", "lgu": "Cebu City", "lat": 10.3270, "lon": 123.9060, "radius": 4500},
    {"name": "cebu_city_south", "lgu": "Cebu City", "lat": 10.2720, "lon": 123.8610, "radius": 4500},
    {"name": "mandaue_city_central", "lgu": "Mandaue City", "lat": 10.3410, "lon": 123.9210, "radius": 4500},
    {"name": "lapu_lapu_city_central", "lgu": "Lapu-Lapu City", "lat": 10.3140, "lon": 123.9510, "radius": 4500},
    {"name": "talisay_city_central", "lgu": "Talisay City", "lat": 10.2720, "lon": 123.8610, "radius": 4500},
    {"name": "talisay_tabunok", "lgu": "Talisay City", "lat": 10.2390, "lon": 123.8290, "radius": 3000},
    {"name": "minglanilla_central", "lgu": "Minglanilla", "lat": 10.1830, "lon": 123.8200, "radius": 5000},
    {"name": "minglanilla_south", "lgu": "Minglanilla", "lat": 10.1650, "lon": 123.7980, "radius": 3000},
    {"name": "naga_city_boundary", "lgu": "Minglanilla", "lat": 10.2120, "lon": 123.7580, "radius": 3000},
    {"name": "consolacion_central", "lgu": "Consolacion", "lat": 10.3730, "lon": 123.9670, "radius": 4500},
]

CATEGORY_CONFIG = {
    "tourism": {
        "nearby_types": ["lodging", "tourist_attraction"],
        "text_queries": [
            "beach resort cebu", "resort mactan", "dive resort lapu-lapu",
            "boutique hotel cebu", "resort talisay", "resort minglanilla",
            "inn cebu", "pension house cebu",
            "inn lapu-lapu", "pension house lapu-lapu",
            "inn talisay", "resort consolacion",
            "inn mandaue",
            "bed and breakfast cebu",
            "guesthouse cebu",
            "transient house cebu",
            "tourist inn lapu-lapu",
        ],
        "output_name": "tourism.csv",
    },
    "recreation": {
        "nearby_types": ["park", "stadium", "sports_complex"],
        "text_queries": [
            "public park cebu", "plaza cebu", "nature park cebu", "sports center cebu",
            "park lapu-lapu", "plaza lapu-lapu", "park minglanilla", "park talisay",
            "plaza mandaue", "sports complex mandaue",
            "park consolacion", "plaza consolacion",
            "sports center lapu-lapu",
            "nature reserve cebu",
            "beach park cebu",
            "swimming pool cebu",
            "gym cebu", "fitness center cebu",
        ],
        "output_name": "recreation.csv",
    },
    "retail_density": {
        "nearby_types": ["convenience_store", "restaurant", "cafe", "bakery"],
        "text_queries": [
            "7-Eleven cebu", "Alfamart cebu", "Ministop cebu", "FamilyMart cebu",
            "7-Eleven lapu-lapu", "Alfamart lapu-lapu", "Ministop lapu-lapu",
            "7-Eleven minglanilla", "Alfamart talisay", "7-Eleven consolacion",
            "convenience store cebu",
            "restaurant cebu", "restaurant mandaue", "restaurant lapu-lapu",
            "restaurant talisay", "restaurant minglanilla", "restaurant consolacion",
            "restaurant naga cebu",
            "coffee shop cebu", "coffee shop mandaue", "coffee shop lapu-lapu",
            "coffee shop talisay", "coffee shop minglanilla", "coffee shop consolacion",
            "eatery cebu", "eatery talisay", "eatery minglanilla",
            "halo-halo talisay", "halo-halo cebu",
            "lechon cebu",
            "cafe lapu-lapu", "cafe consolacion",
        ],
        "output_name": "retail_density.csv",
    },
}


def resolve_requested_categories(category_args: Sequence[str]) -> List[str]:
    if not category_args:
        return list(CATEGORY_CONFIG)

    unknown_categories = [name for name in category_args if name not in CATEGORY_CONFIG]
    if unknown_categories:
        valid_categories = ", ".join(CATEGORY_CONFIG)
        unknown_list = ", ".join(unknown_categories)
        raise ValueError(f"Unknown category name(s): {unknown_list}. Valid categories: {valid_categories}")

    return list(category_args)


def load_client() -> googlemaps.Client:
    base_dir = Path(__file__).resolve().parents[1]
    env_path = base_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY not found in thesis_main/.env or environment")
    return googlemaps.Client(key=api_key, timeout=REQUEST_TIMEOUT_SECS)


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


def reverse_geocode_lgu(client: googlemaps.Client, lat: float, lon: float) -> Optional[str]:
    try:
        results = client.reverse_geocode((lat, lon))
    except Exception as exc:
        print(f"  reverse geocode failed for ({lat}, {lon}): {exc}")
        return None

    for result in results:
        for component in result.get("address_components", []):
            types = set(component.get("types", []))
            if not ({"locality", "administrative_area_level_2", "administrative_area_level_3"} & types):
                continue
            candidate = normalize_lgu(component.get("long_name", ""))
            if candidate in TARGET_LGUS:
                return candidate
    return None


def assign_lgu_by_nearest_centroid(lat: float, lon: float) -> str:
    return min(
        LGU_CENTROIDS,
        key=lambda lgu: (lat - LGU_CENTROIDS[lgu][0]) ** 2 + (lon - LGU_CENTROIDS[lgu][1]) ** 2,
    )


def fetch_next_page_with_retries(client: googlemaps.Client, method_name: str, next_page_token: str) -> Optional[Dict[str, object]]:
    for attempt in range(1, 4):
        time.sleep(SLEEP_BETWEEN_PAGES)
        try:
            return getattr(client, method_name)(page_token=next_page_token)
        except googlemaps.exceptions.ApiError as exc:
            if str(exc) != "INVALID_REQUEST":
                print(f"  warning: stopping pagination for {method_name} after page-token error: {exc}")
                return None
            if attempt == 3:
                print(f"  warning: stopping pagination for {method_name}; page token stayed INVALID_REQUEST")
                return None
        except Exception as exc:
            print(f"  warning: stopping pagination for {method_name} after page-token fetch failed: {exc}")
            return None
    return None


def fetch_nearby_paginated(
    client: googlemaps.Client,
    seed: Dict[str, object],
    place_type: str,
) -> List[Dict[str, object]]:
    payloads: List[Dict[str, object]] = []
    try:
        response = client.places_nearby(
            location=(seed["lat"], seed["lon"]),
            radius=seed["radius"],
            type=place_type,
        )
    except Exception as exc:
        print(f"  warning: skipping nearby search for {seed['name']} / {place_type}: {exc}")
        return []

    while True:
        for place in response.get("results", []):
            payloads.append(build_payload(place, seed, source_kind="nearby", source_value=place_type))
        next_page_token = response.get("next_page_token")
        if not next_page_token:
            break
        response = fetch_next_page_with_retries(client, "places_nearby", next_page_token)
        if response is None:
            break

    time.sleep(SLEEP_BETWEEN_CALLS)
    return payloads


def fetch_text_paginated(
    client: googlemaps.Client,
    seed: Dict[str, object],
    query: str,
) -> List[Dict[str, object]]:
    payloads: List[Dict[str, object]] = []
    try:
        response = client.places(query=query, location=(seed["lat"], seed["lon"]), radius=seed["radius"])
    except Exception as exc:
        print(f"  warning: skipping text search for {seed['name']} / {query}: {exc}")
        return []

    while True:
        for place in response.get("results", []):
            payloads.append(build_payload(place, seed, source_kind="text", source_value=query))
        next_page_token = response.get("next_page_token")
        if not next_page_token:
            break
        response = fetch_next_page_with_retries(client, "places", next_page_token)
        if response is None:
            break

    time.sleep(SLEEP_BETWEEN_CALLS)
    return payloads


def build_payload(
    place: Dict[str, object],
    seed: Dict[str, object],
    source_kind: str,
    source_value: str,
) -> Dict[str, object]:
    geometry = place.get("geometry", {})
    location = geometry.get("location", {})
    return {
        "place_id": place.get("place_id", ""),
        "name": place.get("name", "").strip(),
        "lat": location.get("lat"),
        "lon": location.get("lng"),
        "rating": place.get("rating"),
        "types": list(place.get("types", [])),
        "seed_lgu": seed["lgu"],
        "source_kind": source_kind,
        "source_value": source_value,
    }


def source_priority(row: Dict[str, object]) -> int:
    return 2 if row["source_kind"] == "nearby" else 1


def filter_tourism(row: Dict[str, object]) -> bool:
    rating = row.get("rating")
    if rating is not None and rating < MIN_TOURISM_RATING:
        return False
    name = str(row.get("name", "")).lower()
    if any(reject in name for reject in TOURISM_RESIDENTIAL_REJECTS):
        return False
    types = set(row.get("types", []))
    return bool(types & {"lodging", "tourist_attraction"}) or any(
        token in name for token in ("resort", "hotel", "beach", "dive", "inn", "pension", "guesthouse", "transient")
    )


def filter_recreation(row: Dict[str, object]) -> bool:
    types = set(row.get("types", []))
    name = str(row.get("name", "")).lower()
    if any(reject in name for reject in RECREATION_REJECTS):
        return False
    keywords = ("park", "plaza", "stadium", "sports", "nature", "gym", "fitness", "pool", "beach")
    return bool(types & {"park", "stadium", "sports_complex"}) or any(keyword in name for keyword in keywords)


def filter_retail_density(row: Dict[str, object]) -> bool:
    types = set(row.get("types", []))
    name = str(row.get("name", "")).lower()
    hard_rejects = (
        "warehouse", "distribution", "wholesale", "depot", "hardware",
        "pharmacy", "drugstore", "clinic", "hospital", "gas", "gasoline",
        "fuel", "school", "university", "resort", "hotel", "office",
    )
    if any(flag in name for flag in hard_rejects):
        return False
    food_types = {"convenience_store", "restaurant", "cafe", "bakery", "food"}
    has_brand = any(keyword in name for keyword in BRAND_KEYWORDS)
    return bool(types & food_types) or has_brand


def choose_amenity_type(category: str, row: Dict[str, object]) -> str:
    types = set(row.get("types", []))
    query = str(row.get("source_value", "")).lower()
    name = str(row.get("name", "")).lower()

    if category == "tourism":
        if "lodging" in types or any(token in query or token in name for token in ("hotel", "resort", "inn")):
            return "lodging"
        return "tourist_attraction"

    if category == "recreation":
        if "stadium" in types:
            return "stadium"
        if "sports_complex" in types or "sports center" in query or "sports" in name:
            return "sports_complex"
        return "park"

    if category == "retail_density":
        name_lower = str(row.get("name", "")).lower()
        types = set(row.get("types", []))
        if any(kw in name_lower for kw in BRAND_KEYWORDS) or "convenience_store" in types:
            return "convenience_store"
        if "cafe" in types or "cafe" in name_lower:
            return "cafe"
        if "bakery" in types:
            return "bakery"
        if "restaurant" in types or "food" in types:
            return "restaurant"
        return "convenience_store"

    return "convenience_store"


def deduplicate_rows(rows: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    deduped: Dict[str, Dict[str, object]] = {}
    for row in rows:
        place_id = str(row.get("place_id", "")).strip()
        if not place_id or row.get("lat") is None or row.get("lon") is None:
            continue
        existing = deduped.get(place_id)
        if existing is None or source_priority(row) > source_priority(existing):
            deduped[place_id] = row
    return sorted(deduped.values(), key=lambda row: (str(row["seed_lgu"]), str(row["name"]).lower(), str(row["place_id"])))


def collect_category_rows(
    client: googlemaps.Client,
    category: str,
    config: Dict[str, object],
) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for seed in SEED_AREAS:
        for place_type in config["nearby_types"]:
            print(f"[{category}] nearby {place_type} @ {seed['name']}")
            rows.extend(fetch_nearby_paginated(client, seed, place_type))
        for query in config["text_queries"]:
            print(f"[{category}] text {query} @ {seed['name']}")
            rows.extend(fetch_text_paginated(client, seed, query))

    filter_map = {
        "tourism": filter_tourism,
        "recreation": filter_recreation,
        "retail_density": filter_retail_density,
    }
    filtered = [row for row in rows if filter_map[category](row)]
    return deduplicate_rows(filtered)


def to_output_frame(
    client: googlemaps.Client,
    category: str,
    rows: Iterable[Dict[str, object]],
) -> pd.DataFrame:
    output_rows = []
    for row in rows:
        if not within_metro_cebu_bbox(float(row["lat"]), float(row["lon"])):
            continue
        lgu = assign_lgu_by_nearest_centroid(float(row["lat"]), float(row["lon"]))
        if lgu not in TARGET_LGUS:
            continue
        output_rows.append(
            {
                "id": str(row["place_id"]),
                "lat": float(row["lat"]),
                "lon": float(row["lon"]),
                "amenity_type": choose_amenity_type(category, row),
                "amenity": str(row["name"]),
                "lgu": lgu,
            }
        )

    frame = pd.DataFrame(output_rows, columns=OUTPUT_COLUMNS)
    if frame.empty:
        return frame
    frame = frame.drop_duplicates(subset=["id"]).sort_values(by=["lgu", "amenity", "id"], kind="stable")
    return frame[OUTPUT_COLUMNS].reset_index(drop=True)


def main(argv: Optional[Sequence[str]] = None) -> None:
    requested_categories = resolve_requested_categories(list(sys.argv[1:] if argv is None else argv))
    client = load_client()
    amenities_dir = Path(__file__).resolve().parents[1] / "Data" / "amenities"
    amenities_dir.mkdir(parents=True, exist_ok=True)

    for category in requested_categories:
        config = CATEGORY_CONFIG[category]
        deduped_rows = collect_category_rows(client, category, config)
        frame = to_output_frame(client, category, deduped_rows)
        output_path = amenities_dir / str(config["output_name"])
        frame.to_csv(output_path, index=False)
        print(f"Saved {len(frame)} rows to {output_path}")


if __name__ == "__main__":
    main()
