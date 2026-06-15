"""
define_cbds.py
--------------
Empirically defines Central Business District (CBD) anchor points for Metro Cebu
by querying Google Maps Places API (Nearby Search) for major commercial and
civic POIs around each candidate hub.

For each hub, the script:
  1. Issues a Nearby Search for place types configured per hub within SEARCH_RADIUS_M.
     Core hubs use [shopping_mall, local_government_office].
     Peripheral hubs additionally use [supermarket, park, city_hall] to catch
     markets, plazas, and civic buildings that Google does not tag as shopping_mall.
  2. For peripheral hubs, a Text Search using the hub's query string is also run
     as a fallback, capturing landmarks with no formal type classification.
  3. Saves the raw results to Data/processed/cbd_pois_raw.csv
  4. Computes a POI-weighted centroid per hub (= empirical CBD anchor)
  5. Saves the final anchor coordinates to Data/processed/cbd_nodes.csv

These anchors replace hardcoded NODES in enrich_abt.py.

Justification for thesis:
  The CBD is operationalised as the geometric centroid of major commercial and
  civic POIs returned by the Google Maps Places API within 1.5 km of each
  candidate hub nucleus. This provides a data-driven, replicable definition
  rather than an arbitrary single-building pin.

Usage:
    python3 thesis_main/Scripts/define_cbds.py
"""

import os
import time
import json
import pandas as pd
import numpy as np
import googlemaps
from dotenv import load_dotenv

# ── Config ────────────────────────────────────────────────────────────────────
load_dotenv("thesis_main/.env")
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=API_KEY)

SEARCH_RADIUS_M      = 1_500   # metres around seed coordinate
CORE_PLACE_TYPES     = ["shopping_mall", "local_government_office"]
PERIPH_PLACE_TYPES   = ["shopping_mall", "local_government_office", "supermarket", "park", "city_hall"]

RAW_OUT   = "thesis_main/Data/processed/cbd_pois_raw.csv"
NODES_OUT = "thesis_main/Data/processed/cbd_nodes.csv"

# ── Candidate hub seeds ────────────────────────────────────────────────────────
# These are rough nucleus coordinates for each candidate CBD.
# The final centroid will be determined by the Places results, not by these seeds.
CANDIDATE_HUBS = [
    # peripheral=False → uses CORE_PLACE_TYPES only, no text search fallback
    # peripheral=True  → uses PERIPH_PLACE_TYPES + text search using query field
    {
        "hub_id":   "cebu_business_park",
        "label":    "Cebu Business Park (Cebu City primary CBD)",
        "seed_lat": 10.3184,
        "seed_lon": 123.9054,
        "query":    "Cebu Business Park",
        "peripheral": False,
    },
    {
        "hub_id":   "mandaue_cbd",
        "label":    "Mandaue commercial corridor (A.C. Cortes / SM City Cebu)",
        "seed_lat": 10.3430,
        "seed_lon": 123.9230,
        "query":    "SM City Cebu Mandaue",
        "peripheral": False,
    },
    {
        "hub_id":   "mactan_cbd",
        "label":    "Lapu-Lapu / Mactan commercial core (Robinsons Galleria)",
        "seed_lat": 10.3133,
        "seed_lon": 123.9488,
        "query":    "Robinsons Galleria Cebu Mactan",
        "peripheral": False,
    },
    {
        "hub_id":   "srp",
        "label":    "South Road Properties (SM Seaside / emerging CBD)",
        "seed_lat": 10.2716,
        "seed_lon": 123.8613,
        "query":    "SM Seaside City Cebu SRP",
        "peripheral": False,
    },
    # ── Peripheral / peri-urban sub-centers (added 2026-04-17) ────────────────
    {
        "hub_id":   "talisay_tabunok",
        "label":    "Talisay Tabunok commercial hub (highway strip)",
        "seed_lat": 10.2380,
        "seed_lon": 123.8420,
        "query":    "Tabunok Public Market Talisay City",
        "peripheral": True,
    },
    {
        "hub_id":   "consolacion",
        "label":    "Consolacion commercial center (SM + CityMall corridor)",
        "seed_lat": 10.3730,
        "seed_lon": 123.9670,
        "query":    "SM City Consolacion CityMall Consolacion",
        "peripheral": True,
    },
    {
        "hub_id":   "naga_city",
        "label":    "City of Naga poblacion and civic center",
        "seed_lat": 10.2120,
        "seed_lon": 123.7580,
        "query":    "City of Naga Plaza Cebu People's Market Naga",
        "peripheral": True,
    },
]


def nearby_search_all(lat: float, lon: float, radius: int, types: list[str]) -> list[dict]:
    """Fetch all Nearby Search results (with pagination) for given place types."""
    results = []
    for ptype in types:
        resp = gmaps.places_nearby(
            location=(lat, lon),
            radius=radius,
            type=ptype,
        )
        results.extend(resp.get("results", []))
        # Follow next_page_token (up to 2 additional pages)
        for _ in range(2):
            next_token = resp.get("next_page_token")
            if not next_token:
                break
            time.sleep(2)  # Google requires a short delay before using the token
            resp = gmaps.places_nearby(page_token=next_token)
            results.extend(resp.get("results", []))
        time.sleep(0.5)
    return results


def text_search_all(query: str, lat: float, lon: float, radius: int) -> list[dict]:
    """Text Search fallback for peripheral hubs whose landmarks lack formal type tags."""
    results = []
    try:
        resp = gmaps.places(query=query, location=(lat, lon), radius=radius)
        results.extend(resp.get("results", []))
        for _ in range(2):
            next_token = resp.get("next_page_token")
            if not next_token:
                break
            time.sleep(2)
            resp = gmaps.places(page_token=next_token)
            results.extend(resp.get("results", []))
    except Exception as e:
        print(f"   WARNING: text search failed — {e}")
    return results


def deduplicate(records: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for r in records:
        pid = r.get("place_id")
        if pid and pid not in seen:
            seen.add(pid)
            out.append(r)
    return out


def centroid(lats: list[float], lons: list[float]) -> tuple[float, float]:
    return float(np.mean(lats)), float(np.mean(lons))


def main():
    all_pois = []
    node_rows = []

    for hub in CANDIDATE_HUBS:
        radius = hub.get("radius", SEARCH_RADIUS_M)  # per-hub override or global default
        print(f"\n── {hub['label']}")
        print(f"   Seed: ({hub['seed_lat']}, {hub['seed_lon']})  |  radius: {radius} m")

        place_types = PERIPH_PLACE_TYPES if hub.get("peripheral") else CORE_PLACE_TYPES
        raw = nearby_search_all(hub["seed_lat"], hub["seed_lon"], radius, place_types)

        # For peripheral hubs, supplement with a text search using the query string
        if hub.get("peripheral"):
            text_results = text_search_all(
                hub["query"], hub["seed_lat"], hub["seed_lon"], radius
            )
            raw.extend(text_results)
            print(f"   Text search ('{hub['query']}') returned {len(text_results)} additional results")

        raw = deduplicate(raw)
        print(f"   Returned {len(raw)} unique POIs total")

        if not raw:
            print("   WARNING: no results — seed centroid will be used as fallback")
            node_rows.append({
                "hub_id":      hub["hub_id"],
                "label":       hub["label"],
                "centroid_lat": hub["seed_lat"],
                "centroid_lon": hub["seed_lon"],
                "poi_count":   0,
                "fallback":    True,
            })
            continue

        lats, lons = [], []
        for place in raw:
            loc = place["geometry"]["location"]
            lats.append(loc["lat"])
            lons.append(loc["lng"])
            all_pois.append({
                "hub_id":     hub["hub_id"],
                "place_id":   place.get("place_id"),
                "name":       place.get("name"),
                "types":      json.dumps(place.get("types", [])),
                "lat":        loc["lat"],
                "lon":        loc["lng"],
                "rating":     place.get("rating"),
                "vicinity":   place.get("vicinity"),
            })

        clat, clon = centroid(lats, lons)
        print(f"   Empirical centroid: ({clat:.6f}, {clon:.6f})")

        node_rows.append({
            "hub_id":       hub["hub_id"],
            "label":        hub["label"],
            "centroid_lat": round(clat, 6),
            "centroid_lon": round(clon, 6),
            "poi_count":    len(raw),
            "fallback":     False,
        })

    # ── Save raw POIs ──────────────────────────────────────────────────────────
    if all_pois:
        pd.DataFrame(all_pois).to_csv(RAW_OUT, index=False)
        print(f"\n✅ Raw POIs saved → {RAW_OUT}  ({len(all_pois)} rows)")

    # ── Save CBD anchor nodes ──────────────────────────────────────────────────
    nodes_df = pd.DataFrame(node_rows)
    nodes_df.to_csv(NODES_OUT, index=False)
    print(f"✅ CBD nodes saved → {NODES_OUT}")
    print()
    print(nodes_df[["hub_id", "centroid_lat", "centroid_lon", "poi_count"]].to_string(index=False))


if __name__ == "__main__":
    main()
