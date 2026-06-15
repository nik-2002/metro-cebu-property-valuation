"""
scrape_dotproperty.py
=====================
Source-expansion scraper #4: DotProperty.com.ph — the largest catch of the 2026-06 sprint
(~9,845 Cebu listings across houses/condos/land). Server-rendered HTML, `?page=N` pagination,
25 `.listing-snippet` cards per page. NOT previously scraped (ABT source col = Lamudi only).

WHY DOTPROPERTY OVER THE OTHERS
  - Volume: ~9.8k Cebu results vs OnePropertee ~1k / FilipinoHomes ~2.4k.
  - Geocoding: card carries BARANGAY-level location ("Catarman, Lilo-an Cebu") — far better
    than OnePropertee's city-level text, so it geocodes to a real neighbourhood, not a centroid.
  - It worked with plain requests in recon (HTTP 200, static markup).
  CAVEAT: DotProperty syndicates from brokers (Cebu Grand Realty etc.), so expect overlap with
  Lamudi — the downstream ABT dedup (street_address/price/type) will absorb it; true net-new < 9.8k.

ANTI-BOT NOTE
  OnePropertee rate-limited us (HTTP 202, empty body) after ~45 fast pages. If DotProperty does
  the same, two levers (in order): (1) raise PACING and lower the per-run page budget, run in
  several passes; (2) switch fetch() to the Playwright harness in thesis_main/playwright/browser.py
  (LamudiBrowser) — generalize its Lamudi-specific warm_up/markers. Start requests-first.

FIELD EXTRACTION (DOM is Tailwind-obfuscated, so we parse the reliable signals)
  url/slug   a[href] -> "/ads/4-bedroom-house-for-sale-in-catarman-cebu_<id>"
             slug gives: bedrooms ("4-bedroom"), type ("house"/"condo"/"land"), barangay+city.
  price      first "₱ N" in card text  (total price)
  psqm       "₱ N / m 2"               (price per sqm)
  area_sqm   total_price / psqm  (exact cross-check) ; fallback "N m 2" regex
  baths      "<bed> <bath> <area> m 2" triple in card text (best-effort)
  location   slug "...-in-<barangay>-cebu" + the "Location:" line when present

Output: Data/webscraping-dotproperty/dp_raw.csv  (raw; clean/geocode downstream).

USAGE
  python scrape_dotproperty.py --self-test          # parse pg1 of each category, no full crawl
  python scrape_dotproperty.py                       # full crawl (all categories, all pages)
  python scrape_dotproperty.py --max-pages 80        # cap pages/category (rate-limit friendly)
"""

import argparse
import os
import random
import re
import time
from datetime import datetime
from urllib.parse import unquote

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE = "https://www.dotproperty.com.ph"
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

CATEGORIES = [
    {"label": "house", "slug": "/houses-for-sale/cebu"},
    {"label": "condo", "slug": "/condos-for-sale/cebu"},
    {"label": "lot",   "slug": "/land-for-sale/cebu"},
]

PACING = (1.0, 2.2)        # gentler than OnePropertee (which throttled at ~45 fast pages)
STALL_LIMIT = 2
DEFAULT_MAX_PAGES = 400    # ~9.8k/25 ≈ 394 pages for houses; safety cap

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "Data", "webscraping-dotproperty")
OUT_CSV = os.path.join(OUT_DIR, "dp_raw.csv")


def num(s):
    if s is None:
        return None
    m = re.search(r"[\d,]+(?:\.\d+)?", str(s))
    return float(m.group(0).replace(",", "")) if m else None


def parse_slug(href):
    """'/ads/4-bedroom-house-for-sale-in-catarman-cebu_abc123' -> dict(beds,type,location,ad_id)."""
    tail = href.rstrip("/").split("/ads/")[-1]
    ad_id = tail.split("_")[-1] if "_" in tail else tail
    slug = tail.split("_")[0]
    beds = num(re.search(r"(\d+)-bedroom", slug).group(1)) if re.search(r"(\d+)-bedroom", slug) else None
    if re.search(r"\bcondo|condominium\b", slug):
        ptype = "condo"
    elif re.search(r"\bland|lot\b", slug):
        ptype = "lot"
    elif re.search(r"\bhouse|townhouse|duplex\b", slug):
        ptype = "house"
    else:
        ptype = None
    m = re.search(r"-in-(.+)$", slug)
    location = unquote(m.group(1)).replace("-", " ").strip() if m else None
    return {"ad_id": ad_id, "slug": slug, "beds_slug": beds, "type_slug": ptype, "loc_slug": location}


def parse_card(card, cat_label):
    a = card.find("a", href=True)
    if not a:
        return None
    href = a["href"]
    url = href if href.startswith("http") else BASE + href
    sl = parse_slug(href)

    full = " ".join(card.get_text(" ", strip=True).split())

    prices = re.findall(r"₱\s*([\d,]+)", full)
    total_price = num(prices[0]) if prices else None
    psqm_m = re.search(r"₱\s*([\d,]+)\s*/\s*m", full)
    price_per_sqm = num(psqm_m.group(1)) if psqm_m else None

    # area: exact from price/psqm, else "<bed> <bath> <area> m 2" triple, else first "N m 2"
    area = None
    if total_price and price_per_sqm:
        area = round(total_price / price_per_sqm, 1)
    triple = re.search(r"(\d+)\s+(\d+)\s+([\d,]+)\s*m\s*2", full.split("/ m 2 )", 1)[-1])
    baths = num(triple.group(2)) if triple else None
    if area is None:
        am = re.search(r"([\d,]+)\s*m\s*2", full)
        area = num(am.group(1)) if am else (num(triple.group(3)) if triple else None)

    # location: prefer the "Location:" line (richest), else slug-derived
    loc_line = re.search(r"Location:\s*([^|]+?)(?:Project Name|Project Type|Listing|$)", full)
    location = (loc_line.group(1).strip() if loc_line else None) or sl["loc_slug"]
    if location:
        location = unquote(location)
    project = re.search(r"Project Name:\s*([^|]+?)(?:Project Type|Listing|$)", full)

    return {
        "ad_id": sl["ad_id"],
        "url": url,
        "title": a.get("title") or sl["slug"].replace("-", " "),
        "property_type_raw": sl["type_slug"] or cat_label,
        "price_php": total_price,
        "price_per_sqm_listed": price_per_sqm,
        "bedrooms": sl["beds_slug"],
        "bathrooms": baths,
        "area_sqm": area,
        "location_text": location,
        "project_name": project.group(1).strip() if project else None,
    }


def fetch(session, url):
    r = session.get(url, headers=HEADERS, timeout=30)
    # OnePropertee-style throttle signature: 202 / empty body
    if r.status_code == 202 or not r.text.strip():
        raise RuntimeError(f"throttled (status {r.status_code}, len {len(r.text)}) at {url} "
                           f"— raise PACING / lower --max-pages, or switch to Playwright")
    r.raise_for_status()
    return r.text


def scrape_category(session, cat, seen, rows, max_pages):
    print(f"[{cat['label']}] {BASE}{cat['slug']}")
    stalls = 0
    for page in range(1, max_pages + 1):
        url = f"{BASE}{cat['slug']}" + ("" if page == 1 else f"?page={page}")
        try:
            html = fetch(session, url)
        except Exception as e:
            print(f"[{cat['label']}] page {page} STOP: {e}")
            break
        cards = BeautifulSoup(html, "html.parser").select(".listing-snippet")
        if not cards:
            print(f"[{cat['label']}] page {page}: 0 cards — end")
            break
        new = 0
        for c in cards:
            rec = parse_card(c, cat["label"])
            if not rec or not rec["ad_id"] or rec["ad_id"] in seen:
                continue
            seen.add(rec["ad_id"])
            rec["category"] = cat["label"]
            rec["source"] = "dotproperty"
            rec["scraped_at"] = datetime.now().isoformat(timespec="seconds")
            rows.append(rec)
            new += 1
        print(f"[{cat['label']}] page {page}: {len(cards)} cards, {new} new (total {len(rows)})")
        stalls = stalls + 1 if new == 0 else 0
        if stalls >= STALL_LIMIT:
            print(f"[{cat['label']}] {STALL_LIMIT} stalled pages — stopping")
            break
        time.sleep(random.uniform(*PACING))


def self_test(session):
    print("SELF-TEST — page 1 of each category, no full crawl:\n")
    for cat in CATEGORIES:
        html = fetch(session, f"{BASE}{cat['slug']}")
        cards = BeautifulSoup(html, "html.parser").select(".listing-snippet")
        recs = [parse_card(c, cat["label"]) for c in cards]
        recs = [r for r in recs if r]
        ok_price = sum(r["price_php"] is not None for r in recs)
        ok_area = sum(r["area_sqm"] is not None for r in recs)
        ok_loc = sum(bool(r["location_text"]) for r in recs)
        print(f"[{cat['label']}] {len(recs)} cards | price {ok_price} | area {ok_area} | loc {ok_loc}")
        for r in recs[:2]:
            print("   ", {k: r[k] for k in ("property_type_raw", "price_php", "bedrooms",
                                            "bathrooms", "area_sqm", "location_text")})
        time.sleep(random.uniform(*PACING))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", help="parse pg1 of each category, no crawl")
    ap.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES)
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    session = requests.Session()

    if args.self_test:
        self_test(session)
        return

    seen, rows = set(), []
    print(f"DotProperty scrape -> {OUT_CSV}  (max {args.max_pages} pages/category)\n")
    for cat in CATEGORIES:
        scrape_category(session, cat, seen, rows, args.max_pages)
        pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
        print(f"  checkpoint: {len(rows)} rows\n")

    df = pd.DataFrame(rows)
    print("=" * 64)
    print(f"DONE — {len(df)} raw listings")
    if len(df):
        print("\nby category:\n", df["category"].value_counts().to_string())
        print(f"\nwith price: {df['price_php'].notna().sum()}  with area: {df['area_sqm'].notna().sum()}  "
              f"with location: {df['location_text'].notna().sum()}")
    print(f"\n-> {OUT_CSV}")


if __name__ == "__main__":
    main()
