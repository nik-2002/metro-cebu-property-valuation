"""
Pag-IBIG Online Public Auction (OPA) Scraper — Cebu Province
=============================================================
Verified selectors from live DOM inspection (2026-03-24):
  - CTA Button:    id="btn_supersale"  (scrolls to form)
  - Region:        id="region"
  - Province:      id="province"
  - City:          id="city"
  - Search button: id="search-button"  (anchor <a> tag, NOT <button>)
  - Tabs:          id="nav-first-tab" | "nav-second-tab" | "nav-nego-tab"
  - Cards:         div.card.mb-3
  - Field icons:   Bootstrap icons (bi-*) precede field text

Usage:
    conda run -n webscrape python scrape_pagibig_opa.py

Output:
    pagibig_cebu_properties.csv (in the same folder as this script)
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

CEBU_CITIES = [
    "BOGO CITY",
    "CARCAR CITY",
    "CEBU CITY",
    "CONSOLACION",
    "DANAO CITY",
    "LAPU-LAPU CITY (OPON)",
    "LILOAN",
    "MANDAUE CITY",
    "MINGLANILLA",
    "TALISAY CITY",
]

# Tab IDs confirmed from DOM inspection
# Format: (display_label, tab_element_id, pagination_div_id_suffix)
AUCTION_TABS = [
    ("First Auction",   "nav-first-tab",   "first"),
    ("Second Auction",  "nav-second-tab",  "second"),
    ("Negotiated Sale", "nav-nego-tab",    "nego"),
]

OUTPUT_FILE = Path(__file__).parent / "pagibig_cebu_properties.csv"
WAIT  = 12    # seconds to wait for elements
PAUSE = 2     # seconds pause after each interaction


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
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(5)
    return driver


def js_click(driver, element):
    driver.execute_script("arguments[0].click();", element)


# ---------------------------------------------------------------------------
# NAVIGATION
# ---------------------------------------------------------------------------
def open_search_section(driver):
    """Click the CTA button (id=btn_supersale) to scroll to / reveal the search form."""
    btn = WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, "btn_supersale"))
    )
    js_click(driver, btn)
    time.sleep(PAUSE)


def set_filters(driver, city: str):
    """Set Region 7 → Cebu → {city} → click Search."""
    # ---- Region ----
    region_el = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "region"))
    )
    Select(region_el).select_by_visible_text("REGION 7 (CENTRAL VISAYAS)")
    time.sleep(PAUSE)

    # ---- Province (dynamically populated after region) ----
    province_el = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "province"))
    )
    Select(province_el).select_by_visible_text("CEBU")
    time.sleep(PAUSE)

    # ---- City/Municipality (dynamically populated after province) ----
    city_el = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "city"))
    )
    # Wait until at least one real option appears (not just placeholder)
    WebDriverWait(driver, WAIT).until(
        lambda d: len(Select(d.find_element(By.ID, "city")).options) > 1
    )
    Select(city_el).select_by_visible_text(city)
    time.sleep(0.5)

    # ---- Search (anchor tag with id="search-button") ----
    search_el = WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, "search-button"))
    )
    js_click(driver, search_el)
    time.sleep(PAUSE)


def click_tab(driver, tab_id: str):
    """Click a tab by its confirmed id."""
    tab = WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, tab_id))
    )
    js_click(driver, tab)
    time.sleep(PAUSE)


# ---------------------------------------------------------------------------
# PAGINATION
# ---------------------------------------------------------------------------
def get_total_pages(driver, pagination_suffix: str) -> int:
    """
    Count page buttons inside div#paginationControls-{suffix}.
    Confirmed structure: <button class="btn btn-primary">1</button>
                         <button class="btn btn-light">2</button> ...
    Ignores 'Previous' and 'Next' buttons.
    """
    container_id = f"paginationControls-{pagination_suffix}"
    try:
        container = driver.find_element(By.ID, container_id)
        buttons = container.find_elements(By.TAG_NAME, "button")
        nums = [
            int(b.text.strip())
            for b in buttons
            if b.text.strip().isdigit()
        ]
        return max(nums) if nums else 1
    except Exception:
        pass

    # Fallback: parse 'Total Properties: N' label
    try:
        label = driver.find_element(
            By.XPATH, "//*[contains(text(),'Total Properties')]"
        ).text
        match = re.search(r"\d+", label)
        if match:
            return max(1, (int(match.group()) + 4) // 5)
    except Exception:
        pass

    return 1


def navigate_to_page(driver, page_num: int, pagination_suffix: str) -> bool:
    """Click the page button inside div#paginationControls-{suffix}."""
    if page_num == 1:
        return True
    container_id = f"paginationControls-{pagination_suffix}"
    try:
        container = WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, container_id))
        )
        buttons = container.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            if btn.text.strip() == str(page_num):
                js_click(driver, btn)
                time.sleep(PAUSE)
                return True
        return False
    except Exception as e:
        print(f"      ⚠ Pagination error: {e}")
        return False


# ---------------------------------------------------------------------------
# PROPERTY EXTRACTION  (uses confirmed Bootstrap icon structure)
# ---------------------------------------------------------------------------
def icon_sibling_text(card, icon_class: str) -> str:
    """
    Return text of the element immediately following the Bootstrap icon
    whose class contains icon_class.
    e.g. <i class="bi bi-tag"></i><strong>₱2,795,500</strong>
    """
    try:
        icon = card.find_element(By.XPATH, f".//*[contains(@class,'{icon_class}')]")
        # Try next sibling text via JS
        txt = card.parent.execute_script(
            "return arguments[0].nextSibling ? arguments[0].nextSibling.textContent : "
            "(arguments[0].nextElementSibling ? arguments[0].nextElementSibling.textContent : '');",
            icon
        )
        return txt.strip() if txt else ""
    except Exception:
        return ""


def extract_properties(driver, city: str, category: str) -> list[dict]:
    records = []
    time.sleep(1)

    cards = driver.find_elements(By.CSS_SELECTOR, "div.card.mb-3")
    if not cards:
        print(f"      ⚠ No cards found (0 properties for this filter).")
        return []

    for card in cards:
        try:
            # Property name — h3 > strong
            name = ""
            try:
                name = card.find_element(By.CSS_SELECTOR, "h3 strong, h3").text.strip()
            except Exception:
                pass

            # Property type — near bi-houses icon
            prop_type = icon_sibling_text(card, "bi-houses")
            if not prop_type:
                # Fallback: search card text for property type keywords
                for kw in ["Condominium", "House and Lot", "Lot Only", "Townhouse", "Apartment"]:
                    if kw.lower() in card.text.lower():
                        prop_type = kw
                        break

            # Price — after bi-tag icon
            price_raw = icon_sibling_text(card, "bi-tag")
            price_clean = re.sub(r"[₱,\s]", "", price_raw)

            # Lot area — after bi-bounding-box-circles icon
            lot_raw = icon_sibling_text(card, "bi-bounding-box-circles")
            lot_clean = re.sub(r"[^\d.]", "", lot_raw)

            # Floor area — after bi-border-outer icon
            floor_raw = icon_sibling_text(card, "bi-border-outer")
            floor_clean = re.sub(r"[^\d.]", "", floor_raw)

            # Occupancy — after bi-house icon
            occupancy = icon_sibling_text(card, "bi-house")
            if not occupancy:
                for kw in ["Unoccupied", "Occupied/Closed", "Occupied", "Vacant"]:
                    if kw.lower() in card.text.lower():
                        occupancy = kw
                        break

            # Auction date — look for "Mar. 30, 2026 – Apr. 3, 2026" pattern
            date_match = re.search(
                r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\.?\s+\d{1,2},\s*\d{4}"
                r"\s*[–\-]\s*"
                r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\.?\s+\d{1,2},\s*\d{4}",
                card.text
            )
            auction_date = date_match.group(0) if date_match else ""

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
            print(f"      ⚠ Card parse error: {e}")

    return records


# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------
def scrape_all(headless: bool = False) -> list[dict]:
    all_records = []
    driver = init_driver(headless=headless)

    try:
        print(f"\n📡 Opening: {BASE_URL}\n{'=' * 55}")
        driver.get(BASE_URL)
        time.sleep(2)

        open_search_section(driver)
        print("✅ Search section opened.\n")

        for city in CEBU_CITIES:
            print(f"📍 {city}")
            set_filters(driver, city)

            for label, tab_id, pag_suffix in AUCTION_TABS:
                print(f"  🏷  {label}")
                try:
                    click_tab(driver, tab_id)
                except Exception:
                    print(f"      ↳ Tab '{tab_id}' not found. Skipping.")
                    continue

                total_pages = get_total_pages(driver, pag_suffix)
                print(f"      📄 Pages: {total_pages}")

                for page in range(1, total_pages + 1):
                    if page > 1:
                        ok = navigate_to_page(driver, page, pag_suffix)
                        if not ok:
                            print(f"      ⚠ Could not load page {page}. Stopping.")
                            break

                    recs = extract_properties(driver, city, label)
                    print(f"      ✅ Page {page}: {len(recs)} properties")
                    all_records.extend(recs)

            print()

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback; traceback.print_exc()
    finally:
        driver.quit()

    return all_records


# ---------------------------------------------------------------------------
# SAVE CSV
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
# ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 55)
    print("  Pag-IBIG OPA Scraper — Cebu Province")
    print("  Confirmed selectors: 2026-03-24")
    print("=" * 55)

    records = scrape_all(headless=False)  # set True for silent mode
    save_csv(records)

    print("\n🎉 Done!")
    if records:
        print(f"   Total: {len(records)} properties")
        cities = {r["City"] for r in records if r["Price_PHP"]}
        print(f"   Cities with data: {', '.join(sorted(cities))}")
