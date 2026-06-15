#!/usr/bin/env python3
"""
Catalogue Metro Cebu POIs using Google Maps Places API

Purpose:
    Query the Google Maps Places API to build a comprehensive catalogue of 
    significant Points of Interest (POIs) across Metro Cebu municipalities 
    (core and peripheral). Used to identify town centers and sub-centers 
    significant enough to add as additional CBD nodes in residential valuation models.

Output:
    - thesis_main/Data/processed/poi_catalogue.csv (full results)
    - thesis_main/Data/processed/poi_catalogue_deduped.csv (deduplicated)

Author: Thesis Research
Date: 2026
"""

import os
import time
import json
import googlemaps
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================

# Load API key
load_dotenv("thesis_main/.env")
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY not found in thesis_main/.env")

# Initialize client
gmaps = googlemaps.Client(key=API_KEY)

# Seed points for POI search across Metro Cebu
SEED_POINTS = {
    "talisay_tabunok": {"lat": 10.238, "lon": 123.842, "city": "Talisay", "radius": 1500},
    "talisay_poblacion": {"lat": 10.213, "lon": 123.849, "city": "Talisay", "radius": 800},
    "minglanilla_poblacion": {"lat": 10.183, "lon": 123.820, "city": "Minglanilla", "radius": 800},
    "naga_city_poblacion": {"lat": 10.212, "lon": 123.758, "city": "Naga", "radius": 800},
    "consolacion": {"lat": 10.373, "lon": 123.967, "city": "Consolacion", "radius": 800},
    "liloan": {"lat": 10.399, "lon": 123.991, "city": "Liloan", "radius": 800},
    "danao_city": {"lat": 10.523, "lon": 124.021, "city": "Danao", "radius": 800},
    "cebu_business_park": {"lat": 10.318, "lon": 123.905, "city": "Cebu City", "radius": 1500},
    "it_park": {"lat": 10.327, "lon": 123.906, "city": "Cebu City", "radius": 1500},
    "mandaue_cbd": {"lat": 10.341, "lon": 123.921, "city": "Mandaue", "radius": 1500},
    "mactan_cbd": {"lat": 10.314, "lon": 123.951, "city": "Mactan", "radius": 1500},
    "srp": {"lat": 10.272, "lon": 123.861, "city": "Cebu City", "radius": 1500},
}

# Place types for nearby search
NEARBY_TYPES = [
    "shopping_mall",
    "local_government_office",
    "park",
]

# Text search queries (parameterized by city name)
TEXT_SEARCH_QUERIES = [
    "public market {city}",
    "town plaza {city}",
    "poblacion {city}",
]

# Rate limiting (seconds)
SLEEP_BETWEEN_PAGINATED = 2.0
SLEEP_BETWEEN_CALLS = 0.5

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def deduplicate_by_place_id(results: List[Dict]) -> List[Dict]:
    """
    Deduplicate by place_id, keeping the row with highest priority search_type.
    
    Priority order (highest to lowest):
        nearby_shopping_mall > nearby_government > text_market > 
        nearby_park > text_plaza > text_poblacion
    
    Args:
        results: List of result dictionaries with 'place_id' and 'search_type'
        
    Returns:
        List of deduplicated dictionaries
    """
    priority = {
        "nearby_shopping_mall": 6,
        "nearby_government": 5,
        "text_market": 4,
        "nearby_park": 3,
        "text_plaza": 2,
        "text_poblacion": 1,
    }
    
    seen = {}
    for row in results:
        place_id = row["place_id"]
        current_priority = priority.get(row["search_type"], 0)
        
        if place_id not in seen or current_priority > priority.get(seen[place_id]["search_type"], 0):
            seen[place_id] = row
    
    return list(seen.values())


def nearby_search_paginated(
    location: Tuple[float, float],
    place_type: str,
    radius: int,
    area_id: str,
    search_type_prefix: str = "nearby",
) -> List[Dict]:
    """
    Perform paginated nearby search, collecting all results.
    
    Args:
        location: (lat, lon) tuple
        place_type: Google Places type (e.g., "shopping_mall")
        radius: Search radius in meters
        area_id: Identifier for the seed area
        search_type_prefix: Prefix for search_type field
        
    Returns:
        List of result dictionaries
    """
    results = []
    seen_ids = set()
    
    try:
        response = gmaps.places_nearby(location=location, radius=radius, type=place_type)
        
        while True:
            for place in response.get("results", []):
                if place["place_id"] not in seen_ids:
                    seen_ids.add(place["place_id"])
                    results.append({
                        "area_id": area_id,
                        "place_id": place["place_id"],
                        "name": place.get("name", ""),
                        "types": json.dumps(place.get("types", [])),
                        "lat": place["geometry"]["location"]["lat"],
                        "lon": place["geometry"]["location"]["lng"],
                        "rating": place.get("rating", ""),
                        "vicinity": place.get("vicinity", ""),
                        "search_type": f"{search_type_prefix}_{place_type}",
                    })
            
            # Check for next page
            next_page_token = response.get("next_page_token")
            if not next_page_token:
                break
            
            time.sleep(SLEEP_BETWEEN_PAGINATED)
            response = gmaps.places_nearby(page_token=next_page_token)
    
    except Exception as e:
        print(f"  ERROR in nearby search ({area_id}, {place_type}): {e}")
    
    return results


def text_search_paginated(
    query: str,
    location: Tuple[float, float],
    radius: int,
    area_id: str,
    search_category: str,
) -> List[Dict]:
    """
    Perform paginated text search, collecting all results.
    
    Args:
        query: Search query string
        location: (lat, lon) tuple for bias
        radius: Search radius in meters
        area_id: Identifier for the seed area
        search_category: Category label for search_type (e.g., "text_market")
        
    Returns:
        List of result dictionaries
    """
    results = []
    seen_ids = set()
    
    try:
        response = gmaps.places(query=query, location=location, radius=radius)
        
        while True:
            for place in response.get("results", []):
                if place["place_id"] not in seen_ids:
                    seen_ids.add(place["place_id"])
                    results.append({
                        "area_id": area_id,
                        "place_id": place["place_id"],
                        "name": place.get("name", ""),
                        "types": json.dumps(place.get("types", [])),
                        "lat": place["geometry"]["location"]["lat"],
                        "lon": place["geometry"]["location"]["lng"],
                        "rating": place.get("rating", ""),
                        "vicinity": place.get("vicinity", ""),
                        "search_type": search_category,
                    })
            
            # Check for next page
            next_page_token = response.get("next_page_token")
            if not next_page_token:
                break
            
            time.sleep(SLEEP_BETWEEN_PAGINATED)
            response = gmaps.places(page_token=next_page_token)
    
    except Exception as e:
        print(f"  ERROR in text search ({area_id}, {query}): {e}")
    
    return results


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 80)
    print("METRO CEBU POI CATALOGUE BUILDER")
    print("=" * 80)
    print()
    
    all_results = []
    area_summaries = {}
    
    # Iterate through seed points
    for area_id, area_config in SEED_POINTS.items():
        lat = area_config["lat"]
        lon = area_config["lon"]
        city = area_config["city"]
        radius = area_config["radius"]
        location = (lat, lon)
        
        print(f"[{area_id.upper()}] ({lat}, {lon})")
        area_results = []
        
        # Nearby searches for place types
        for place_type in NEARBY_TYPES:
            time.sleep(SLEEP_BETWEEN_CALLS)
            
            search_type_label = {
                "shopping_mall": "nearby_shopping_mall",
                "local_government_office": "nearby_government",
                "park": "nearby_park",
            }.get(place_type, f"nearby_{place_type}")
            
            nearby_results = nearby_search_paginated(
                location=location,
                place_type=place_type,
                radius=radius,
                area_id=area_id,
                search_type_prefix="nearby",
            )
            
            print(f"  [{place_type}] {len(nearby_results)} results")
            area_results.extend(nearby_results)
            all_results.extend(nearby_results)
        
        # Text searches for keywords
        for query_template in TEXT_SEARCH_QUERIES:
            time.sleep(SLEEP_BETWEEN_CALLS)
            
            query = query_template.format(city=city)
            category_map = {
                "public market": "text_market",
                "town plaza": "text_plaza",
                "poblacion": "text_poblacion",
            }
            search_category = next(
                (v for k, v in category_map.items() if k in query_template),
                "text_other"
            )
            
            text_results = text_search_paginated(
                query=query,
                location=location,
                radius=2000,
                area_id=area_id,
                search_category=search_category,
            )
            
            print(f"  [{query}] {len(text_results)} results")
            area_results.extend(text_results)
            all_results.extend(text_results)
        
        # Summary for this area
        area_summaries[area_id] = {
            "total": len(area_results),
            "names": [r["name"] for r in area_results[:5]],
        }
        print()
    
    print("=" * 80)
    print("SAVING RESULTS")
    print("=" * 80)
    print()
    
    # Output directory
    output_dir = Path("thesis_main/Data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save full results
    full_path = output_dir / "poi_catalogue.csv"
    df_full = pd.DataFrame(all_results)
    df_full.to_csv(full_path, index=False)
    print(f"✓ Full catalogue: {full_path}")
    print(f"  Total rows: {len(df_full)}")
    print()
    
    # Save deduplicated results
    dedup_results = deduplicate_by_place_id(all_results)
    dedup_path = output_dir / "poi_catalogue_deduped.csv"
    df_dedup = pd.DataFrame(dedup_results)
    df_dedup.to_csv(dedup_path, index=False)
    print(f"✓ Deduplicated catalogue: {dedup_path}")
    print(f"  Total unique place_ids: {len(df_dedup)}")
    print()
    
    # Print summary table
    print("=" * 80)
    print("SUMMARY BY AREA")
    print("=" * 80)
    print()
    print(f"{'Area ID':<25} | {'Total POIs':<12} | {'Notable Names'}")
    print("-" * 80)
    
    for area_id in sorted(area_summaries.keys()):
        summary = area_summaries[area_id]
        total = summary["total"]
        names = ", ".join(summary["names"][:3]) if summary["names"] else "(no results)"
        print(f"{area_id:<25} | {total:<12} | {names}")
    
    print()
    print("=" * 80)
    print("COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
