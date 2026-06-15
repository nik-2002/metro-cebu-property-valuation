#!/usr/bin/env python3
"""Fetch pharmacy POIs for Metro Cebu from Google Maps Places API."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import googlemaps
import pandas as pd
from dotenv import load_dotenv

OUTPUT_COLUMNS = ["id", "lat", "lon", "amenity_type", "amenity", "lgu"]
SLEEP_BETWEEN_CALLS = 0.5
SLEEP_BETWEEN_PAGES = 2.0
REQUEST_TIMEOUT_SECS = 25
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

TEXT_QUERIES = [
    "Mercury Drug cebu",
    "Mercury Drug mandaue",
    "Mercury Drug lapu-lapu",
    "Mercury Drug talisay",
    "Mercury Drug minglanilla",
    "Mercury Drug consolacion",
    "Watsons cebu",
    "Watsons mandaue",
    "Watsons lapu-lapu",
    "Generika cebu",
    "Generika lapu-lapu",
    "Generika talisay",
    "Rose Pharmacy cebu",
    "South Star Drug cebu",
]

REJECT_NAME_TOKENS = (
    "hospital",
    "clinic",
    "medical center",
    "veterinary",
    "vet",
    "dental",
    "doctor",
    "hardware",
    "grocery",
    "supermarket",
)
KEEP_NAME_TOKENS = (
    "pharmacy",
    "drug",
    "mercury",
    "watsons",
    "generika",
    "rose pharmacy",
    "south star",
)
KEEP_TYPES = {"pharmacy", "drugstore"}


def within_metro_cebu_bbox(lat: float, lon: float) -> bool:
    return (
        METRO_CEBU_BBOX["lat_min"] <= lat <= METRO_CEBU_BBOX["lat_max"]
        and METRO_CEBU_BBOX["lon_min"] <= lon <= METRO_CEBU_BBOX["lon_max"]
    )


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


def assign_lgu_by_nearest_centroid(lat: float, lon: float) -> str:
    return min(
        LGU_CENTROIDS,
        key=lambda lgu: (lat - LGU_CENTROIDS[lgu][0]) ** 2 + (lon - LGU_CENTROIDS[lgu][1]) ** 2,
    )


def fetch_next_page_with_retries(
    client: googlemaps.Client,
    method_name: str,
    next_page_token: str,
) -> Optional[Dict[str, object]]:
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


def build_payload(
    place: Dict[str, object],
    seed: Dict[str, object],
    source_kind: str,
    source_value: str,
) -> Dict[str, object]:
    geometry = place.get("geometry", {})
    location = geometry.get("location", {})
    return {
        "place_id": str(place.get("place_id", "")).strip(),
        "name": str(place.get("name", "")).strip(),
        "lat": location.get("lat"),
        "lon": location.get("lng"),
        "types": list(place.get("types", [])),
        "seed_lgu": seed["lgu"],
        "source_kind": source_kind,
        "source_value": source_value,
    }


def fetch_nearby_paginated(client: googlemaps.Client, seed: Dict[str, object]) -> List[Dict[str, object]]:
    payloads: List[Dict[str, object]] = []
    try:
        response = client.places_nearby(
            location=(seed["lat"], seed["lon"]),
            radius=seed["radius"],
            type="pharmacy",
        )
    except Exception as exc:
        print(f"  warning: skipping nearby search for {seed['name']}: {exc}")
        return []

    while True:
        for place in response.get("results", []):
            payloads.append(build_payload(place, seed, source_kind="nearby", source_value="pharmacy"))
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


def source_priority(row: Dict[str, object]) -> int:
    return 2 if row["source_kind"] == "nearby" else 1


def passes_pharmacy_filter(row: Dict[str, object]) -> bool:
    name = str(row.get("name", "")).lower()
    if any(token in name for token in REJECT_NAME_TOKENS):
        return False
    types = {str(place_type).lower() for place_type in row.get("types", [])}
    return bool(types & KEEP_TYPES) or any(token in name for token in KEEP_NAME_TOKENS)


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


def collect_rows(client: googlemaps.Client) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for seed in SEED_AREAS:
        print(f"[pharmacy] nearby pharmacy @ {seed['name']}")
        rows.extend(fetch_nearby_paginated(client, seed))
        for query in TEXT_QUERIES:
            print(f"[pharmacy] text {query} @ {seed['name']}")
            rows.extend(fetch_text_paginated(client, seed, query))
    return rows


def to_output_frame(rows: Sequence[Dict[str, object]]) -> tuple[pd.DataFrame, Dict[str, int]]:
    summary = {
        "total_fetched": len(rows),
        "after_dedup": 0,
        "after_filter": 0,
        "after_bbox": 0,
    }

    deduped_rows = deduplicate_rows(rows)
    summary["after_dedup"] = len(deduped_rows)

    filtered_rows = [row for row in deduped_rows if passes_pharmacy_filter(row)]
    summary["after_filter"] = len(filtered_rows)

    output_rows = []
    for row in filtered_rows:
        lat = float(row["lat"])
        lon = float(row["lon"])
        if not within_metro_cebu_bbox(lat, lon):
            continue
        summary["after_bbox"] += 1
        lgu = assign_lgu_by_nearest_centroid(lat, lon)
        if lgu not in TARGET_LGUS:
            continue
        output_rows.append(
            {
                "id": str(row["place_id"]),
                "lat": lat,
                "lon": lon,
                "amenity_type": "pharmacy",
                "amenity": str(row["name"]),
                "lgu": lgu,
            }
        )

    frame = pd.DataFrame(output_rows, columns=OUTPUT_COLUMNS)
    if frame.empty:
        return frame, summary
    frame = frame.drop_duplicates(subset=["id"]).sort_values(by=["lgu", "amenity", "id"], kind="stable")
    return frame[OUTPUT_COLUMNS].reset_index(drop=True), summary


def print_summary(summary: Dict[str, int], frame: pd.DataFrame) -> None:
    print(f"Total fetched: {summary['total_fetched']}")
    print(f"After dedup: {summary['after_dedup']}")
    print(f"After filter: {summary['after_filter']}")
    print(f"After bbox: {summary['after_bbox']}")
    print(f"Final rows: {len(frame)}")
    print("Final count per LGU:")
    counts = frame["lgu"].value_counts().reindex(sorted(TARGET_LGUS), fill_value=0) if not frame.empty else None
    for lgu in sorted(TARGET_LGUS):
        count = 0 if counts is None else int(counts[lgu])
        print(f"  {lgu}: {count}")


def main() -> None:
    client = load_client()
    amenities_dir = Path(__file__).resolve().parents[1] / "Data" / "amenities"
    amenities_dir.mkdir(parents=True, exist_ok=True)

    rows = collect_rows(client)
    frame, summary = to_output_frame(rows)
    output_path = amenities_dir / "pharmacy.csv"
    frame.to_csv(output_path, index=False)
    print(f"Saved {len(frame)} rows to {output_path}")
    print_summary(summary, frame)


if __name__ == "__main__":
    main()