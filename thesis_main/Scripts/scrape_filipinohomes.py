"""
scrape_filipinohomes.py
=======================
Source-expansion scraper #2 (after Lamudi): FilipinoHomes.com, the largest Cebu-HQ'd
broker portal. Server-rendered HTML, no anti-bot — plain requests + BeautifulSoup.

Goal (2026-06-14 sprint): significantly grow the ABT beyond Lamudi to give the stratified
Random Forest more training rows (the binding constraint, esp. Vacant Lot n=255).

Each listing card carries every structural field we need:
  price (₱), location text (incl. city → LGU filter), bedrooms, bathrooms,
  Floor Area, Land Size, property type, listing id (CEB-xxxxx), detail URL.
Cards: `a.MuiCard-root[href]`, 12 per page; pagination `?page=N`.

Output: Data/webscraping-filipinohomes/fh_raw.csv  (raw; cleaning/geocoding is a later stage).
No coordinates on the page → geocoded downstream from the (rich) location text.

Politeness: single sequential session, randomized 0.5–1.2s pacing, desktop UA.
"""

import os
import random
import re
import sys
import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE = "https://filipinohomes.com"
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Province-wide sweeps (in-cebu) capture all 6 LGUs in one pass per type; we filter to the
# 6 LGUs downstream by parsing the city out of the location text.
CATEGORIES = [
    {"label": "house", "slugs": ["/for-sale/house/in-cebu"]},
    {"label": "condo", "slugs": ["/for-sale/condo/in-cebu", "/for-sale/condominium/in-cebu"]},
    {"label": "lot",   "slugs": ["/for-sale/lot/in-cebu", "/for-sale/land/in-cebu"]},
]

MAX_PAGES = 250          # safety cap; real depth is ~145 (house)
PACING = (0.5, 1.2)
STALL_LIMIT = 2          # stop a category after N consecutive pages with 0 new listings

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "Data", "webscraping-filipinohomes")
OUT_CSV = os.path.join(OUT_DIR, "fh_raw.csv")


def num(text):
    """First number in a string -> float, or None. Handles '122sqm', '₱6,500,000', '3'."""
    if not text:
        return None
    m = re.search(r"[\d,]+(?:\.\d+)?", text.replace("\xa0", " "))
    return float(m.group(0).replace(",", "")) if m else None


def stat(card, label):
    """Value text inside the icon-stat block with aria-label=label (e.g. 'Bedrooms')."""
    node = card.find(attrs={"aria-label": label})
    return node.get_text(" ", strip=True) if node else None


def parse_card(card):
    href = card.get("href", "")
    url = href if href.startswith("http") else BASE + href

    # price: the one <p> carrying the ₱ glyph
    price = None
    for p in card.find_all("p"):
        t = p.get_text(" ", strip=True)
        if "₱" in t:
            price = num(t)
            break

    # property type + furnishing: the '•' line, e.g. "House and Lot • Unfurnished"
    type_raw, furnishing = None, None
    for p in card.find_all("p"):
        t = p.get_text(" ", strip=True)
        if "•" in t:
            parts = [x.strip() for x in t.split("•")]
            type_raw = parts[0] or None
            furnishing = parts[1] if len(parts) > 1 else None
            break

    # location: the aria-label string that ends in 'Philippines' (richest text)
    location = None
    for el in card.find_all(attrs={"aria-label": True}):
        al = el.get("aria-label", "")
        if al.strip().endswith("Philippines") or ", Cebu" in al:
            if location is None or len(al) > len(location):
                location = al.strip()

    # listing id
    m = re.search(r"CEB-\w+", card.get_text(" ", strip=True))
    listing_id = m.group(0) if m else None

    img = card.find("img")
    title = (img.get("alt") if img and img.get("alt") else None)

    return {
        "listing_id": listing_id,
        "url": url,
        "title": title,
        "property_type_raw": type_raw,
        "furnishing": furnishing,
        "price_php": price,
        "bedrooms": num(stat(card, "Bedrooms")),
        "bathrooms": num(stat(card, "Bathrooms")),
        "floor_area_sqm": num(stat(card, "Floor Area")),
        "lot_area_sqm": num(stat(card, "Land Size")),
        "location_text": location,
    }


def scrape_category(session, cat, seen_ids, rows):
    # pick the first slug variant that returns cards on page 1
    base_slug = None
    for slug in cat["slugs"]:
        r = session.get(BASE + slug, headers=HEADERS, timeout=20)
        if r.status_code == 200 and BeautifulSoup(r.text, "html.parser").select("a.MuiCard-root[href]"):
            base_slug = slug
            break
    if not base_slug:
        print(f"[{cat['label']}] no working slug among {cat['slugs']} — skipping")
        return
    print(f"[{cat['label']}] using {base_slug}")

    stalls = 0
    for page in range(1, MAX_PAGES + 1):
        url = f"{BASE}{base_slug}?page={page}"
        try:
            r = session.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"[{cat['label']}] page {page} fetch failed: {e}; stopping")
            break
        cards = BeautifulSoup(r.text, "html.parser").select("a.MuiCard-root[href]")
        if not cards:
            print(f"[{cat['label']}] page {page}: 0 cards — end of category")
            break
        new = 0
        for c in cards:
            rec = parse_card(c)
            key = rec["listing_id"] or rec["url"].rstrip("/").split("/")[-1]
            if not key or key in seen_ids:
                continue
            seen_ids.add(key)
            rec["category"] = cat["label"]
            rec["source"] = "filipinohomes"
            rec["scraped_at"] = datetime.now().isoformat(timespec="seconds")
            rows.append(rec)
            new += 1
        print(f"[{cat['label']}] page {page}: {len(cards)} cards, {new} new (total {len(rows)})")
        stalls = stalls + 1 if new == 0 else 0
        if stalls >= STALL_LIMIT:
            print(f"[{cat['label']}] {STALL_LIMIT} stalled pages — stopping")
            break
        time.sleep(random.uniform(*PACING))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    session = requests.Session()
    seen_ids, rows = set(), []
    print(f"FilipinoHomes scrape -> {OUT_CSV}\n")
    for cat in CATEGORIES:
        scrape_category(session, cat, seen_ids, rows)
        df = pd.DataFrame(rows)
        df.to_csv(OUT_CSV, index=False)  # checkpoint after each category
        print(f"  checkpoint: {len(rows)} rows written\n")

    df = pd.DataFrame(rows)
    print("=" * 64)
    print(f"DONE — {len(df)} raw listings")
    if len(df):
        print("\nby category:\n", df["category"].value_counts().to_string())
        print(f"\nwith price: {df['price_php'].notna().sum()}  "
              f"with location: {df['location_text'].notna().sum()}  "
              f"with floor: {df['floor_area_sqm'].notna().sum()}  "
              f"with lot: {df['lot_area_sqm'].notna().sum()}")
    print(f"\n-> {OUT_CSV}")


if __name__ == "__main__":
    main()
