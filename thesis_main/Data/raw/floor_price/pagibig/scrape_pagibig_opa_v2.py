"""
Pag-IBIG Online Public Auction (OPA) Scraper — Full Cebu Province
===================================================================
v3 — 2026-03-24
  Fix: Price extracted from parentElement of bi-tag icon
  New: Covers ALL cities/municipalities in Cebu Province (from dropdown)
  Output: pagibig_cebu_province_all.csv

Confirmed DOM structure:
  Price:       <div title="Minimum Bid/..."><i class="bi bi-tag"></i><strong>₱XYZ</strong></div>
  Lot area:    parent of bi-bounding-box-circles icon
  Floor area:  parent of bi-border-outer icon
  Occupancy:   parent of bi-house icon (not bi-houses)
  Auction date:parent of bi-calendar icon

Usage:
    conda run -n webscrape python scrape_pagibig_opa_v2.py
"""

import time
import csv
import re
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
BASE_URL = "https://www.pagibigfundservices.com/OnlinePublicAuction"

# Full dropdown list for Cebu Province (Region 7)
# Will be auto-read from the dropdown at runtime; this list is a fallback
CEBU_CITIES_FALLBACK = [
    "ALCANTARA",
    "ALCOY",
    "ALEGRIA",
    "ALOGUINSAN",
    "ARGAO",
    "ASTURIAS",
    "BADIAN",
    "BALAMBAN",
    "BANTAYAN",
    "BARILI",
    "BOGO CITY",
    "BORBON",
    "CARCAR CITY",
    "CARMEN",
    "CATMON",
    "CEBU CITY",
    "COMPOSTELA",
    "CONSOLACION",
    "CORDOVA",
    "DAANBANTAYAN",
    "DALAGUETE",
    "DANAO CITY",
    "DUMANJUG",
    "GINATILAN",
    "LAPU-LAPU CITY (OPON)",
    "LILOAN",
    "LUGO",
    "MADRIDEJOS",
    "MALABUYOC",
    "MANDAUE CITY",
    "MEDELLIN",
    "MINGLANILLA",
    "MOALBOAL",
    "NAGA CITY",
    "OSLOB",
    "PILAR",
    "PINAMUNGAHAN",
    "PORO",
    "RONDA",
    "SAMBOAN",
    "SAN FERNANDO",
    "SAN FRANCISCO",
    "SAN REMIGIO",
    "SANTA FE",
    "SANTANDER",
    "SIBONGA",
    "SOGOD",
    "TABOGON",
    "TABUELAN",
    "TALISAY CITY",
    "TOLEDO CITY",
    "TUBURAN",
    "TUDELA",
]

AUCTION_TABS = [
    ("First Auction",   "nav-first-tab",   "first"),
    ("Second Auction",  "nav-second-tab",  "second"),
    ("Negotiated Sale", "nav-nego-tab",    "nego"),
]

OUTPUT_FILE = Path(__file__).parent / "pagibig_cebu_province_all.csv"
WAIT  = 15
PAUSE = 2


# ---------------------------------------------------------------------------
# DRIVER
# ---------------------------------------------------------------------------
def init_driver(headless: bool = False) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1400,900")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def js_click(driver, element):
    driver.execute_script("arguments[0].click();", element)


# ---------------------------------------------------------------------------
# NAVIGATION
# ---------------------------------------------------------------------------
def open_search_section(driver):
    btn = WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, "btn_supersale"))
    )
    js_click(driver, btn)
    time.sleep(PAUSE)


def get_cebu_cities_from_dropdown(driver) -> list[str]:
    """
    Set Region 7 → Cebu Province, then read all City options from the dropdown.
    Returns a list of city names (skipping placeholder 'Select City/Municipality').
    """
    region_el = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "region"))
    )
    Select(region_el).select_by_visible_text("REGION 7 (CENTRAL VISAYAS)")
    time.sleep(PAUSE)

    province_el = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "province"))
    )
    Select(province_el).select_by_visible_text("CEBU")
    time.sleep(PAUSE)

    # Wait for city options to populate
    WebDriverWait(driver, WAIT).until(
        lambda d: len(Select(d.find_element(By.ID, "city")).options) > 2
    )
    city_el = driver.find_element(By.ID, "city")
    options = Select(city_el).options
    cities = [
        o.text.strip()
        for o in options
        if o.text.strip() and "Select" not in o.text
    ]
    print(f"📋 Found {len(cities)} cities/municipalities in Cebu Province dropdown.")
    return cities


def set_filters(driver, city: str):
    """Select Region 7 → Cebu → {city} → click Search."""
    region_el = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "region"))
    )
    Select(region_el).select_by_visible_text("REGION 7 (CENTRAL VISAYAS)")
    time.sleep(PAUSE)

    province_el = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "province"))
    )
    Select(province_el).select_by_visible_text("CEBU")
    time.sleep(PAUSE)

    WebDriverWait(driver, WAIT).until(
        lambda d: len(Select(d.find_element(By.ID, "city")).options) > 2
    )
    city_el = driver.find_element(By.ID, "city")
    Select(city_el).select_by_visible_text(city)
    time.sleep(0.5)

    search_el = WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, "search-button"))
    )
    js_click(driver, search_el)
    time.sleep(PAUSE)


def click_tab(driver, tab_id: str):
    tab = WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, tab_id))
    )
    js_click(driver, tab)
    time.sleep(PAUSE)


# ---------------------------------------------------------------------------
# PAGINATION
# ---------------------------------------------------------------------------
def get_total_pages(driver, pag_suffix: str) -> int:
    container_id = f"paginationControls-{pag_suffix}"
    try:
        container = driver.find_element(By.ID, container_id)
        buttons = container.find_elements(By.TAG_NAME, "button")
        nums = [int(b.text.strip()) for b in buttons if b.text.strip().isdigit()]
        return max(nums) if nums else 1
    except Exception:
        return 1


def navigate_to_page(driver, page_num: int, pag_suffix: str) -> bool:
    if page_num == 1:
        return True
    container_id = f"paginationControls-{pag_suffix}"
    try:
        container = WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, container_id))
        )
        for btn in container.find_elements(By.TAG_NAME, "button"):
            if btn.text.strip() == str(page_num):
                js_click(driver, btn)
                time.sleep(PAUSE)
                return True
        return False
    except Exception as e:
        print(f"      ⚠ Pagination error: {e}")
        return False


# ---------------------------------------------------------------------------
# PROPERTY EXTRACTION  — v3 fix
# ---------------------------------------------------------------------------
def icon_parent_text(card, icon_class: str) -> str:
    """
    Get the text of the PARENT element of the Bootstrap icon.
    Confirmed structure: <div><i class="bi {icon_class}"></i> <strong>VALUE</strong></div>
    So parentElement.innerText gives us the full text incl. the value.
    We strip the icon character (it's invisible) and return cleaned text.
    """
    try:
        icon = card.find_element(
            By.XPATH, f".//*[contains(@class,'{icon_class}')]"
        )
        # Get parent element text
        parent_text = icon.find_element(By.XPATH, "..").text.strip()
        return parent_text
    except Exception:
        return ""


def extract_properties(driver, city: str, category: str) -> list[dict]:
    records = []
    time.sleep(1)

    cards = driver.find_elements(By.CSS_SELECTOR, "div.card.mb-3")
    if not cards:
        return []

    for card in cards:
        try:
            # --- Property name ---
            name = ""
            try:
                name = card.find_element(By.CSS_SELECTOR, "h3 strong, h3").text.strip()
            except Exception:
                pass

            # --- Property type (bi-houses icon parent) ---
            prop_type_raw = icon_parent_text(card, "bi-houses")
            # Strip the card header which may bleed through
            prop_type = prop_type_raw.split("\n")[0].strip() if prop_type_raw else ""

            # --- Price (bi-tag icon parent) ---
            price_raw = icon_parent_text(card, "bi-tag")
            price_match = re.search(r"₱[\d,]+", price_raw)
            price_clean = re.sub(r"[₱,\s]", "", price_match.group(0)) if price_match else ""

            # --- Lot area (bi-bounding-box-circles icon parent) ---
            lot_raw = icon_parent_text(card, "bi-bounding-box-circles")
            lot_match = re.search(r"[\d.]+", lot_raw)
            lot_clean = lot_match.group(0) if lot_match else ""

            # --- Floor area (bi-border-outer icon parent) ---
            floor_raw = icon_parent_text(card, "bi-border-outer")
            floor_match = re.search(r"[\d.]+", floor_raw)
            floor_clean = floor_match.group(0) if floor_match else ""

            # --- Occupancy (bi-house icon parent — note: NOT bi-houses) ---
            # bi-house is used for occupancy, bi-houses for type
            occupancy_raw = icon_parent_text(card, "bi-house ")  # trailing space disambiguates
            if not occupancy_raw:
                # fallback: scan card text
                for kw in ["Unoccupied", "Occupied/Closed", "Occupied", "Vacant"]:
                    if kw.lower() in card.text.lower():
                        occupancy_raw = kw
                        break
            occupancy = occupancy_raw.split("\n")[0].strip()

            # --- Auction date (bi-calendar icon parent) ---
            date_raw = icon_parent_text(card, "bi-calendar")
            date_match = re.search(
                r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\.?\s+\d{1,2},\s*\d{4}"
                r"\s*[\-–]\s*"
                r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\.?\s+\d{1,2},\s*\d{4}",
                date_raw
            )
            auction_date = date_match.group(0) if date_match else date_raw.strip()[:60]

            if name or price_clean:
                records.append({
                    "City":             city,
                    "Auction_Category": category,
                    "Property_Name":    name,
                    "Property_Type":    prop_type,
                    "Lot_Area_sqm":     lot_clean,
                    "Floor_Area_sqm":   floor_clean,
                    "Price_PHP":        price_clean,
                    "Occupancy_Status": occupancy,
                    "Auction_Date":     auction_date,
                    "Source":           "Pag-IBIG OPA",
                })

        except Exception as e:
            print(f"      ⚠ Card error: {e}")

    return records


# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------
def scrape_all(headless: bool = False) -> list[dict]:
    all_records = []
    driver = init_driver(headless=headless)

    try:
        print(f"\n📡 Opening: {BASE_URL}\n{'=' * 60}")
        driver.get(BASE_URL)
        time.sleep(2)

        open_search_section(driver)
        print("✅ Search section opened.\n")

        # Read full city list from the live dropdown
        cities = get_cebu_cities_from_dropdown(driver)
        if not cities:
            print("⚠ Could not read city list from dropdown. Using fallback.")
            cities = CEBU_CITIES_FALLBACK

        for i, city in enumerate(cities, 1):
            print(f"[{i}/{len(cities)}] 📍 {city}")
            try:
                set_filters(driver, city)
            except Exception as e:
                print(f"   ⚠ Could not set filters for {city}: {e}")
                continue

            city_total = 0
            for label, tab_id, pag_suffix in AUCTION_TABS:
                print(f"  🏷  {label}")
                try:
                    click_tab(driver, tab_id)
                except Exception:
                    print(f"      ↳ Tab not found. Skipping.")
                    continue

                total_pages = get_total_pages(driver, pag_suffix)
                if total_pages > 1:
                    print(f"      📄 Pages: {total_pages}")

                for page in range(1, total_pages + 1):
                    if page > 1:
                        ok = navigate_to_page(driver, page, pag_suffix)
                        if not ok:
                            print(f"      ⚠ Lost pagination on page {page}. Stopping.")
                            break

                    recs = extract_properties(driver, city, label)
                    city_total += len(recs)
                    if recs:
                        print(f"      ✅ Page {page}: {len(recs)} properties")
                    all_records.extend(recs)

            if city_total == 0:
                print(f"   → No listings.")
            print()

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback; traceback.print_exc()
    finally:
        driver.quit()

    return all_records


# ---------------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------------
FIELDNAMES = [
    "City", "Auction_Category", "Property_Name", "Property_Type",
    "Lot_Area_sqm", "Floor_Area_sqm", "Price_PHP",
    "Occupancy_Status", "Auction_Date", "Source",
]

def save_csv(records: list[dict]):
    if not records:
        print("\n⚠ No records to save.")
        return
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)
    print(f"\n💾 Saved {len(records)} records → {OUTPUT_FILE}")


# ---------------------------------------------------------------------------
# ENTRY
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("  Pag-IBIG OPA Scraper — Full Cebu Province (v3)")
    print("  Price fix + all cities from dropdown")
    print("=" * 60)

    records = scrape_all(headless=False)
    save_csv(records)

    print("\n🎉 Done!")
    if records:
        cities_with_data = {r["City"] for r in records if r["Price_PHP"]}
        print(f"   Total: {len(records)} properties")
        print(f"   Cities with prices: {len(cities_with_data)}")
        print(f"   → {', '.join(sorted(cities_with_data))}")
