#!/usr/bin/env python3
"""Fetch nearby places for Mahayag (Zamboanga Peninsula) using Google Maps APIs,
convert coordinates to EPSG:3857 and save output as JSON in the `cache/` folder.

Usage:
  export GOOGLE_MAPS_API_KEY=your_key_here
  python "Scripts/gmaps_fetch_mahayag.py" --radius 5000 --output "cache/gmaps_mahayag.json"

Notes:
- Requires `requests` and `pyproj`.
- The script first geocodes the place name, then runs a Places Nearby Search.
"""
import os
import sys
import time
import json
import argparse
from urllib.parse import urlencode

import requests
from pyproj import Transformer
try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

# Try to load a thesis_main/.env file (project-relative). If not present, fallback to default .env lookup.
if load_dotenv:
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        # loads .env from current working directory if available
        load_dotenv()


GMAPS_GEOCODE = "https://maps.googleapis.com/maps/api/geocode/json"
GMAPS_PLACES_NEARBY = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"


def geocode(place_name: str, api_key: str):
    params = {"address": place_name, "key": api_key}
    r = requests.get(GMAPS_GEOCODE, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "OK":
        raise RuntimeError(f"Geocode failed: {data.get('status')} - {data.get('error_message')}")
    loc = data["results"][0]["geometry"]["location"]
    return loc["lat"], loc["lng"]


def fetch_places_nearby(lat: float, lng: float, radius: int, api_key: str, max_requests: int = 5000):
    results = []
    params = {"location": f"{lat},{lng}", "radius": radius, "key": api_key}
    url = GMAPS_PLACES_NEARBY
    requests_left = max_requests

    while requests_left > 0:
        r = requests.get(url, params=params, timeout=30)
        requests_left -= 1
        r.raise_for_status()
        data = r.json()
        status = data.get("status")
        if status not in ("OK", "ZERO_RESULTS"):
            raise RuntimeError(f"Places API error: {status} - {data.get('error_message')}")
        results.extend(data.get("results", []))
        next_token = data.get("next_page_token")
        if not next_token:
            break
        if requests_left <= 0:
            print("Reached max request budget while fetching pages. Stopping early.")
            break
        # next_page_token needs a short delay before it becomes valid
        time.sleep(2)
        params = {"pagetoken": next_token, "key": api_key}

    return results


def to_epsg3857(lon: float, lat: float):
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
    x, y = transformer.transform(lon, lat)
    return x, y


def normalize_places(gmaps_results: list):
    norm = []
    for r in gmaps_results:
        loc = r.get("geometry", {}).get("location")
        if not loc:
            continue
        lat = loc.get("lat")
        lng = loc.get("lng")
        x, y = to_epsg3857(lng, lat)
        item = {
            "place_id": r.get("place_id"),
            "name": r.get("name"),
            "types": r.get("types"),
            "vicinity": r.get("vicinity"),
            "lat": lat,
            "lon": lng,
            "epsg3857": {"x": x, "y": y},
            "geojson": {"type": "Point", "coordinates": [x, y]},
            "raw": r,
        }
        norm.append(item)
    return norm


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--place", default="Mahayag, Zamboanga Peninsula, Philippines")
    p.add_argument("--radius", type=int, default=5000, help="Search radius in meters")
    p.add_argument("--output", default="cache/gmaps_mahayag.json")
    p.add_argument("--max-requests", type=int, default=5000, help="Maximum total Google Maps API requests (including geocode + place pages)")
    args = p.parse_args()

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("Set the GOOGLE_MAPS_API_KEY environment variable with your API key.")
        sys.exit(1)

    if args.max_requests < 2:
        print("Need at least 2 requests (1 geocode + 1 places query). Adjust --max-requests.")
        sys.exit(1)

    print(f"Geocoding '{args.place}'...")
    lat, lng = geocode(args.place, api_key)
    remaining_requests = args.max_requests - 1
    print(f"Geocode used 1 request; {remaining_requests} request(s) remain for places pages.")
    print(f"Center: {lat}, {lng} - fetching nearby places (radius={args.radius}m)")

    places = fetch_places_nearby(lat, lng, args.radius, api_key, max_requests=remaining_requests)
    print(f"Fetched {len(places)} raw results (with max {args.max_requests} requests)")

    normalized = normalize_places(places)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(normalized, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(normalized)} places to {args.output}")


if __name__ == "__main__":
    main()
