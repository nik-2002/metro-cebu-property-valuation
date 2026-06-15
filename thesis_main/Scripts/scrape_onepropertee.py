"""
scrape_onepropertee.py
======================
Source-expansion scraper #3: OnePropertee.com — large PH marketplace, strong Cebu coverage
(~1,950 house-and-lot + lots + condos). Server-rendered HTML (Bootstrap-class markup), no
active anti-bot on listing pages — plain requests + BeautifulSoup. Path-based pagination
`/<category>/page/N` (NOT ?page=, which the server ignores).

Card grammar (`div.listing`):
  url/title  div.listing-photo a[href][title]
  price      div.listing-price            "₱ 11.6 million" | "₱ 850,000" | "₱ 25,000 /sqm"
  type       div.-property-type span.-text  "For Sale New Single Detached House"
  bed/bath   div.-bed-bath span.-text       "3 Bedrooms 3 Bathrooms 80 sqm."
  location   div.listing-location

Output: Data/webscraping-onepropertee/op_raw.csv (raw; clean/geocode downstream).
Politeness: sequential session, 0.6–1.4s pacing, desktop UA.
"""

import argparse
import os
import random
import re
import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE = "https://onepropertee.com"
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

CATEGORIES = [
    {"label": "house", "slugs": ["/house-and-lot-for-sale-cebu"]},
    # NB: list the CANONICAL (non-redirecting) slug first — a redirecting slug breaks /page/N
    # pagination (the server drops the page and re-serves page 1).
    {"label": "condo", "slugs": ["/condo-for-sale-cebu", "/condominium-for-sale-cebu"]},
    {"label": "lot",   "slugs": ["/lot-for-sale-cebu", "/residential-lot-for-sale-cebu"]},
]

MAX_PAGES = 200
PACING = (1.4, 2.8)   # gentler than the first run (which hit a 202 throttle after ~43 pages)
STALL_LIMIT = 2

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "Data", "webscraping-onepropertee")
OUT_CSV = os.path.join(OUT_DIR, "op_raw.csv")


def parse_price(text):
    """'₱ 11.6 million' -> 11600000 ; '₱ 850,000' -> 850000. Returns (value, is_per_sqm)."""
    if not text:
        return None, False
    t = text.replace("₱", "").replace(",", "").strip().lower()
    per_sqm = "/sqm" in t or "per sqm" in t
    m = re.search(r"([\d.]+)\s*(million|billion|m|b)?", t)
    if not m:
        return None, per_sqm
    val = float(m.group(1))
    unit = m.group(2)
    if unit in ("million", "m"):
        val *= 1e6
    elif unit in ("billion", "b"):
        val *= 1e9
    return val, per_sqm


def first_num(pattern, text):
    m = re.search(pattern, text or "", re.I)
    return float(m.group(1).replace(",", "")) if m else None


def parse_card(card):
    a = card.select_one("div.listing-photo a[href]")
    href = a.get("href") if a else None
    if not href:
        return None
    url = href if href.startswith("http") else BASE + href
    title = a.get("title") if a else None

    price_el = card.select_one("div.listing-price")
    price_text = price_el.get_text(" ", strip=True) if price_el else None
    price, per_sqm = parse_price(price_text)

    type_el = card.select_one("div.-property-type span.-text")
    type_text = type_el.get_text(" ", strip=True) if type_el else None  # "For Sale New Single Detached House"

    bb_el = card.select_one("div.-bed-bath span.-text")
    bb = bb_el.get_text(" ", strip=True) if bb_el else ""  # "3 Bedrooms 3 Bathrooms 80 sqm."

    loc_el = card.select_one("div.listing-location")
    location = loc_el.get_text(" ", strip=True) if loc_el else None

    return {
        "url": url,
        "title": title,
        "property_type_raw": type_text,
        "price_php": price,
        "price_text": price_text,
        "price_is_per_sqm": per_sqm,
        "bedrooms": first_num(r"(\d+)\s*Bedroom", bb),
        "bathrooms": first_num(r"(\d+)\s*Bathroom", bb),
        "area_sqm": first_num(r"([\d,.]+)\s*sqm", bb),
        "location_text": location,
    }


def page_url(slug, page):
    return f"{BASE}{slug}" if page == 1 else f"{BASE}{slug}/page/{page}"


def scrape_category(session, cat, seen, rows):
    base_slug = None
    for slug in cat["slugs"]:
        r = session.get(BASE + slug, headers=HEADERS, timeout=25)
        if r.status_code == 200 and BeautifulSoup(r.text, "html.parser").select("div.listing"):
            base_slug = slug
            break
    if not base_slug:
        print(f"[{cat['label']}] no working slug among {cat['slugs']} — skipping")
        return
    print(f"[{cat['label']}] using {base_slug}")

    stalls = 0
    for page in range(1, MAX_PAGES + 1):
        try:
            r = session.get(page_url(base_slug, page), headers=HEADERS, timeout=25)
            # 202 / empty body = throttle signature seen on the first OnePropertee run
            if r.status_code == 202 or not r.text.strip():
                print(f"[{cat['label']}] page {page} THROTTLED (status {r.status_code}, "
                      f"len {len(r.text)}) — stopping category; rerun later to resume")
                break
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"[{cat['label']}] page {page} failed: {e}; stopping")
            break
        cards = BeautifulSoup(r.text, "html.parser").select("div.listing")
        if not cards:
            print(f"[{cat['label']}] page {page}: 0 cards — end")
            break
        new = 0
        for c in cards:
            rec = parse_card(c)
            if not rec:
                continue
            key = rec["url"].rstrip("/").split("/")[-1]
            if key in seen:
                continue
            seen.add(key)
            rec["category"] = cat["label"]
            rec["source"] = "onepropertee"
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--categories", default="house,condo,lot",
                    help="comma list of categories to scrape (default all)")
    args = ap.parse_args()
    want = {c.strip() for c in args.categories.split(",")}

    os.makedirs(OUT_DIR, exist_ok=True)
    session = requests.Session()

    # Resume: load any prior rows, keep them, and seed `seen` so we don't re-scrape.
    rows, seen = [], set()
    if os.path.exists(OUT_CSV):
        prior = pd.read_csv(OUT_CSV)
        rows = prior.to_dict("records")
        seen = {str(u).rstrip("/").split("/")[-1] for u in prior["url"]}
        print(f"resume: loaded {len(rows)} prior rows "
              f"({prior['category'].value_counts().to_dict()})")

    print(f"OnePropertee scrape -> {OUT_CSV}  (categories: {sorted(want)})\n")
    for cat in CATEGORIES:
        if cat["label"] not in want:
            continue
        scrape_category(session, cat, seen, rows)
        pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
        print(f"  checkpoint: {len(rows)} rows\n")

    df = pd.DataFrame(rows)
    print("=" * 64)
    print(f"DONE — {len(df)} raw listings")
    if len(df):
        print("\nby category:\n", df["category"].value_counts().to_string())
        print(f"\nwith price: {df['price_php'].notna().sum()}  per-sqm-priced: {df['price_is_per_sqm'].sum()}  "
              f"with area: {df['area_sqm'].notna().sum()}  with location: {df['location_text'].notna().sum()}")
    print(f"\n-> {OUT_CSV}")


if __name__ == "__main__":
    main()
