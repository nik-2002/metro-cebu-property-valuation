"""
scrape_filipinohomes_api.py
===========================
Source-expansion scraper #2b — FilipinoHomes via its BACKEND JSON API (efficient rewrite).

WHY THIS REPLACES scrape_filipinohomes.py
  The HTML scraper only ever got page 1 (12 rows/category) because FilipinoHomes is a Next.js app
  whose server renders only page 1; pages 2..N load client-side from a backend API. We found that
  API by intercepting the browser's network calls:
      GET https://api2.filipinohomes.com/api/listings
          ?categories[]=For Sale & type_str=<House|Condominium|Land> & address=" Cebu" & page=N
      header: x-guest-token: <token from https://filipinohomes.com/api/guest-token>
  Hitting the JSON API directly with requests is far faster than driving Playwright through 329
  pages — no browser needed at all.

WHY THIS IS THE HIGHEST-QUALITY SOURCE
  Each listing carries PRECISE embedded coordinates (geo_coordinates.lat/lng, ~7 dp / rooftop) and
  a STRUCTURED address (barangay + city + province objects). So FH rows need NO geocoding — they
  sidestep the centroid-snapping problem entirely (Decision 46b). Plus bedroom/bathroom/floor_area/
  lot_area and a subtype→type taxonomy. This is the cleanest residential data of the 2026-06 sprint.

VOLUME (Cebu province, "For Sale"): House 1,740 / Condominium 1,049 / Land 1,144 = ~3,933.
per_page is fixed at 12 server-side (329 pages total); JSON is light so the run is ~3-5 min.

Output: Data/webscraping-filipinohomes/fh_api_raw.csv  (richer schema than the old fh_raw.csv).
Token validity ~1h; we refresh on 401 and proactively every TOKEN_REFRESH_PAGES pages.
"""

import os
import random
import time
from datetime import datetime

import pandas as pd
import requests

GUEST_TOKEN_URL = "https://filipinohomes.com/api/guest-token"
API = "https://api2.filipinohomes.com/api/listings"
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
    "Accept": "application/json",
    "Referer": "https://filipinohomes.com/",
    "Origin": "https://filipinohomes.com",
}

# type_str -> our stratum label
TYPES = [
    {"type_str": "House",       "label": "house"},
    {"type_str": "Condominium", "label": "condo"},
    {"type_str": "Land",        "label": "lot"},
]

PACING = (0.3, 0.7)
TOKEN_REFRESH_PAGES = 60
MAX_PAGES = 400

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "Data", "webscraping-filipinohomes")
OUT_CSV = os.path.join(OUT_DIR, "fh_api_raw.csv")


def get_token(session):
    r = session.get(GUEST_TOKEN_URL, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()["token"]


def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def parse_listing(item, label):
    prop = item.get("property") or {}
    inner = prop.get("property") or {}
    geo = prop.get("geo_coordinates") or {}
    addr_id = prop.get("address_id") or {}
    city = (addr_id.get("city") or {}).get("name")
    province = (addr_id.get("province") or {}).get("name")
    subtype = (inner.get("subtype") or {})
    type_name = (subtype.get("type") or {}).get("name")
    return {
        "fh_id": item.get("id"),
        "code": item.get("code"),
        "url": "https://filipinohomes.com/" + (item.get("slug") or ""),
        "title": item.get("name"),
        "price_php": fnum(item.get("price")),
        "latitude": fnum(geo.get("lat")),
        "longitude": fnum(geo.get("lng")),
        "address": prop.get("address"),
        "barangay": addr_id.get("name"),
        "city": city,
        "province": province,
        "property_type_raw": subtype.get("name"),     # e.g. "House and Lot", "Condominium"
        "type_group": type_name,                       # e.g. "House", "Condominium", "Land"
        "bedrooms": fnum(inner.get("bedroom_count")),
        "bathrooms": fnum(inner.get("bathroom_count")),
        "floor_area_sqm": fnum(inner.get("floor_area")),
        "lot_area_sqm": fnum(inner.get("lot_area")),
        "furnishing": prop.get("furnishing") if isinstance(prop.get("furnishing"), str)
                      else (prop.get("furnishing") or {}).get("name") if isinstance(prop.get("furnishing"), dict) else None,
        "category": label,
        "source": "filipinohomes",
        "scraped_at": datetime.now().isoformat(timespec="seconds"),
    }


def fetch_page(session, token, type_str, page):
    """Returns (json, token) — refreshes token once on 401."""
    params = {"categories[]": "For Sale", "type_str": type_str, "address": " Cebu", "page": page}
    h = dict(HEADERS); h["x-guest-token"] = token
    r = session.get(API, params=params, headers=h, timeout=25)
    if r.status_code == 401:
        token = get_token(session)
        h["x-guest-token"] = token
        r = session.get(API, params=params, headers=h, timeout=25)
    r.raise_for_status()
    return r.json(), token


def scrape_type(session, token, cat, seen, rows):
    j, token = fetch_page(session, token, cat["type_str"], 1)
    last = j.get("meta", {}).get("last_page", 1)
    print(f"[{cat['label']}] type_str={cat['type_str']}  total={j.get('meta',{}).get('total')}  pages={last}")
    page = 1
    while page <= min(last, MAX_PAGES):
        if page > 1:
            j, token = fetch_page(session, token, cat["type_str"], page)
        new = 0
        for item in j.get("data", []):
            rec = parse_listing(item, cat["label"])
            if rec["fh_id"] in seen:
                continue
            seen.add(rec["fh_id"])
            rows.append(rec)
            new += 1
        if page == 1 or page % 20 == 0 or page == last:
            print(f"[{cat['label']}] page {page}/{last}: +{new} (total {len(rows)})")
        if page % TOKEN_REFRESH_PAGES == 0:
            token = get_token(session)
        page += 1
        time.sleep(random.uniform(*PACING))
    return token


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    session = requests.Session()
    token = get_token(session)
    seen, rows = set(), []
    print(f"FilipinoHomes API scrape -> {OUT_CSV}\n")
    for cat in TYPES:
        token = scrape_type(session, token, cat, seen, rows)
        pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
        print(f"  checkpoint: {len(rows)} rows\n")

    df = pd.DataFrame(rows)
    print("=" * 64)
    print(f"DONE — {len(df)} listings")
    if len(df):
        print("\nby category:\n", df["category"].value_counts().to_string())
        print(f"\nwith coords: {df['latitude'].notna().sum()}  with price: {df['price_php'].notna().sum()}  "
              f"with city: {df['city'].notna().sum()}  with floor: {df['floor_area_sqm'].notna().sum()}  "
              f"with lot: {df['lot_area_sqm'].notna().sum()}")
        print("\ncity spread:\n", df["city"].value_counts().head(10).to_string())
    print(f"\n-> {OUT_CSV}")


if __name__ == "__main__":
    main()
