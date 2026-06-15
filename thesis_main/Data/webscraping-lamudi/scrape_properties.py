import concurrent.futures
import json
import os
import random
import re
import subprocess
import threading
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}
CSV_FILENAME = "lamudi_cebu_full.csv"
LINKS_FILENAME = "property_links.txt"
MAX_WORKERS = 5
CSV_COLUMNS = [
    "url",
    "title",
    "description",
    "bedrooms",
    "bathrooms",
    "floor_area_sqm",
    "street_address",
    "city",
    "region",
    "latitude",
    "longitude",
    "amenities",
    "price",
    "lot_area_sqm",
    "property_type_raw",
]
PROPERTY_TYPE_SEGMENTS = {
    "apartment",
    "beach-house",
    "commercial",
    "condo",
    "condominium",
    "farm",
    "house",
    "land",
    "lot",
    "office",
    "residential",
    "retail",
    "room",
    "studio",
    "townhouse",
    "warehouse",
}
INVALID_PAGE_MARKERS = [
    "we haven't found what you are looking for",
    "human verification",
]


def fetch_html(url, headers, timeout=15):
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        if "window.gokuProps" in response.text:
            raise requests.exceptions.RequestException("Lamudi WAF challenge page returned")
        return response.text
    except requests.exceptions.RequestException:
        curl_command = [
            "curl",
            "-L",
            "--compressed",
            "-sS",
            "-A",
            headers["User-Agent"],
            "-H",
            f"Accept: {headers['Accept']}",
            "-H",
            f"Accept-Language: {headers['Accept-Language']}",
            "--max-time",
            str(timeout),
            url,
        ]
        result = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        if "window.gokuProps" in result.stdout:
            raise requests.exceptions.RequestException("Lamudi WAF challenge page returned after curl fallback")
        return result.stdout


def normalize_number(value):
    if value is None:
        return None

    if isinstance(value, dict):
        value = value.get("value")

    if isinstance(value, (int, float)):
        return str(value)

    text = str(value).strip()
    match = re.search(r"(\d[\d,]*(?:\.\d+)?)", text)
    if not match:
        return None

    return match.group(1).replace(",", "")


def extract_json_ld_items(soup):
    items = []

    for script in soup.find_all("script", type="application/ld+json"):
        script_text = script.string or script.get_text()
        if not script_text:
            continue

        try:
            data = json.loads(script_text)
        except json.JSONDecodeError:
            continue

        graph_items = data.get("@graph", [data]) if isinstance(data, dict) else data
        if not isinstance(graph_items, list):
            graph_items = [graph_items]

        items.extend(item for item in graph_items if isinstance(item, dict))

    return items


def is_property_item(item):
    property_types = {
        "Accommodation",
        "Apartment",
        "House",
        "Product",
        "Residence",
        "SingleFamilyResidence",
    }
    return (
        item.get("@type") in property_types
        or any(
            key in item
            for key in [
                "address",
                "amenityFeature",
                "floorSize",
                "geo",
                "numberOfBathroomsTotal",
                "numberOfBedrooms",
                "size",
            ]
        )
    )


def extract_area_candidates(item):
    candidates = {"general": None, "floor": None, "lot": None}

    if "floorSize" in item:
        floor_size = normalize_number(item["floorSize"])
        candidates["floor"] = floor_size
        candidates["general"] = candidates["general"] or floor_size

    if "size" in item:
        size_value = normalize_number(item["size"])
        candidates["general"] = candidates["general"] or size_value

    additional_properties = item.get("additionalProperty", [])
    if isinstance(additional_properties, dict):
        additional_properties = [additional_properties]

    for prop in additional_properties:
        if not isinstance(prop, dict):
            continue

        label = " ".join(
            str(prop.get(key, ""))
            for key in ["name", "propertyID", "description"]
            if prop.get(key)
        ).lower()
        value = normalize_number(prop.get("value") or prop.get("valueReference") or prop.get("description"))

        if not value:
            continue

        if "land" in label or "lot" in label:
            candidates["lot"] = candidates["lot"] or value
        elif "floor" in label:
            candidates["floor"] = candidates["floor"] or value
        elif "area" in label:
            candidates["general"] = candidates["general"] or value

    return candidates


def extract_type_candidates_from_breadcrumbs(json_items):
    candidates = []

    for item in json_items:
        if item.get("@type") != "BreadcrumbList":
            continue

        for crumb in item.get("itemListElement", []):
            if not isinstance(crumb, dict):
                continue

            crumb_url = crumb.get("item") or ""
            segments = [segment for segment in crumb_url.split("/") if segment]
            type_segments = [segment for segment in segments if segment.lower() in PROPERTY_TYPE_SEGMENTS]
            if type_segments:
                candidates.append("/".join(type_segments))

            crumb_name = str(crumb.get("name", "")).strip()
            if re.search(r"\b(land|lot|townhouse|house|condo|apartment|commercial|office|warehouse)\b", crumb_name, re.I):
                candidates.append(crumb_name)

    return candidates


def extract_type_candidates_from_html(soup):
    candidates = []

    h1 = soup.find("h1")
    if h1:
        h1_text = " ".join(h1.stripped_strings)
        if h1_text:
            match = re.match(r"(.+?)\s+for sale\b", h1_text, flags=re.I)
            candidates.append(match.group(1).strip() if match else h1_text)

    if soup.title and soup.title.text.strip():
        title_text = soup.title.text.strip()
        match = re.match(r"(.+?)\s+for sale\b", title_text, flags=re.I)
        if match:
            candidates.append(match.group(1).strip())

    return candidates


def unique_non_empty(values):
    seen = set()
    ordered = []

    for value in values:
        if not value:
            continue

        normalized = value.strip()
        if not normalized or normalized.lower() in seen:
            continue

        seen.add(normalized.lower())
        ordered.append(normalized)

    return ordered


def is_lot_listing(property_data):
    property_type_raw = property_data.get("property_type_raw") or ""
    title = property_data.get("title") or ""

    if re.search(r"\b(house|townhouse|condo|condominium|apartment|residence)\b", property_type_raw, re.I):
        return False
    if re.search(r"\b(land|lot)\b", property_type_raw, re.I):
        return True
    if re.search(r"\bhouse\s+and\s+lot\b", title, re.I):
        return False

    return bool(re.search(r"\b(land|lot)\b", title, re.I))


def extract_labeled_area_from_body(soup, labels):
    text = soup.get_text(" ", strip=True)
    label_pattern = "|".join(re.escape(label) for label in labels)
    patterns = [
        rf"(?:{label_pattern})\s*[:\-]?\s*([0-9][0-9,]*(?:\.\d+)?)\s*(?:sqm|sq\.?\s*m|m²|square meters?)?",
        rf"(?:{label_pattern}).{{0,60}}?([0-9][0-9,]*(?:\.\d+)?)\s*(?:sqm|sq\.?\s*m|m²|square meters?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            return normalize_number(match.group(1))

    return None


def extract_price_from_body(soup):
    price_selectors = [
        ".prices-and-fees__price",
        {"data-name": "property-price"},
        ".ListingPrice",
        ".FirstPrice",
        ".price",
    ]

    for selector in price_selectors:
        if isinstance(selector, dict):
            price_element = soup.find(attrs=selector)
        else:
            price_element = soup.select_one(selector)

        if price_element and price_element.text.strip():
            return price_element.text.strip().replace("₱", "").replace(",", "").strip()

    return None


def parse_property_html(url, html):
    soup = BeautifulSoup(html, "html.parser")
    page_title = soup.title.text.strip().lower() if soup.title and soup.title.text else ""
    page_text = soup.get_text(" ", strip=True).lower()
    if any(marker in page_title or marker in page_text for marker in INVALID_PAGE_MARKERS):
        return None

    json_items = extract_json_ld_items(soup)
    property_data = {"url": url}
    combined_area_candidates = {"general": None, "floor": None, "lot": None}
    type_candidates = []

    for item in json_items:
        if not is_property_item(item):
            continue

        if "name" in item and not property_data.get("title"):
            property_data["title"] = item["name"]
        if "description" in item and not property_data.get("description"):
            property_data["description"] = item["description"]
        if "numberOfBedrooms" in item and property_data.get("bedrooms") is None:
            property_data["bedrooms"] = item["numberOfBedrooms"]
        if "numberOfBathroomsTotal" in item and property_data.get("bathrooms") is None:
            property_data["bathrooms"] = item["numberOfBathroomsTotal"]

        if "address" in item:
            address = item["address"]
            property_data["street_address"] = property_data.get("street_address") or address.get("streetAddress")
            property_data["city"] = property_data.get("city") or address.get("addressLocality")
            property_data["region"] = property_data.get("region") or address.get("addressRegion")

        if "geo" in item:
            geo = item["geo"]
            property_data["latitude"] = property_data.get("latitude") or geo.get("latitude")
            property_data["longitude"] = property_data.get("longitude") or geo.get("longitude")

        if "amenityFeature" in item and not property_data.get("amenities"):
            amenities = [feature.get("name") for feature in item["amenityFeature"] if isinstance(feature, dict) and feature.get("name")]
            if amenities:
                property_data["amenities"] = ", ".join(amenities)

        item_type = item.get("@type")
        if item_type:
            type_candidates.append(str(item_type))

        category = item.get("category")
        if isinstance(category, str):
            type_candidates.append(category)
        elif isinstance(category, list):
            type_candidates.extend(str(value) for value in category if value)

        area_candidates = extract_area_candidates(item)
        for key, value in area_candidates.items():
            combined_area_candidates[key] = combined_area_candidates[key] or value

    type_candidates.extend(extract_type_candidates_from_breadcrumbs(json_items))
    type_candidates.extend(extract_type_candidates_from_html(soup))
    unique_types = unique_non_empty(type_candidates)
    if unique_types:
        property_data["property_type_raw"] = " | ".join(unique_types)

    lot_area_from_body = extract_labeled_area_from_body(soup, ["Land Area", "Lot Area"])
    is_lot = is_lot_listing(property_data)

    if combined_area_candidates["lot"]:
        property_data["lot_area_sqm"] = combined_area_candidates["lot"]
    elif is_lot:
        property_data["lot_area_sqm"] = combined_area_candidates["general"] or lot_area_from_body
    elif lot_area_from_body:
        property_data["lot_area_sqm"] = lot_area_from_body

    if combined_area_candidates["floor"] and not is_lot:
        property_data["floor_area_sqm"] = combined_area_candidates["floor"]
    elif combined_area_candidates["general"] and not is_lot:
        property_data["floor_area_sqm"] = combined_area_candidates["general"]

    property_data["price"] = extract_price_from_body(soup)

    has_core_listing_data = any(
        property_data.get(field)
        for field in ["title", "description", "street_address", "city", "price", "property_type_raw"]
    )
    if not has_core_listing_data:
        return None

    return property_data


def extract_property_details(url, headers):
    try:
        html = fetch_html(url, headers=headers, timeout=15)
    except requests.exceptions.RequestException as exc:
        print(f"  [!] Failed to fetch property {url}: {exc}")
        return None

    return parse_property_html(url, html)


def ensure_csv_columns(df):
    for column in CSV_COLUMNS:
        if column not in df.columns:
            df[column] = None

    return df.reindex(columns=CSV_COLUMNS)


def main():
    if not os.path.exists(LINKS_FILENAME):
        print("Error: property_links.txt not found. Run scrape_index.py first.")
        return

    with open(LINKS_FILENAME, "r") as handle:
        links = [line.strip() for line in handle if line.strip()]

    links = list(dict.fromkeys(links))
    print(f"Loaded {len(links)} properties to scrape.")

    scraped_data = []
    existing_row_count = 0
    pending_links = links

    if os.path.exists(CSV_FILENAME):
        try:
            existing_df = ensure_csv_columns(pd.read_csv(CSV_FILENAME))
            scraped_data = existing_df.to_dict("records")
            existing_row_count = len(existing_df)
            print(f"Loaded {existing_row_count} existing records from {CSV_FILENAME}")
            scraped_urls = set(existing_df["url"].dropna().tolist())
            pending_links = [link for link in links if link not in scraped_urls]
            print(f"Remaining URLs to scrape: {len(pending_links)}")
        except Exception as exc:
            print(f"Error loading existing CSV: {exc}")

    print(f"Starting concurrent scraping with {MAX_WORKERS} workers...")

    progress_lock = threading.Lock()
    progress_counter = 0
    total_to_scrape = len(pending_links)
    new_scraped_data = []

    def save_rows(rows):
        df = ensure_csv_columns(pd.DataFrame(rows))
        df.to_csv(CSV_FILENAME, index=False)

    def process_link(link):
        nonlocal progress_counter
        data = extract_property_details(link, HEADERS)

        sleep_time = random.uniform(1.5, 3.5)
        time.sleep(sleep_time)

        with progress_lock:
            progress_counter += 1
            if data:
                new_scraped_data.append(data)

            if progress_counter % 10 == 0:
                print(f"Scraping progress: [{progress_counter}/{total_to_scrape}]")

            if progress_counter % 50 == 0 and new_scraped_data:
                temp_rows = scraped_data + list(new_scraped_data)
                save_rows(temp_rows)
                print(f"--- Saved intermediate progress ({len(temp_rows)} rows) ---")

        return data

    if pending_links:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            results = list(executor.map(process_link, pending_links))
        valid_results = [result for result in results if result]
        scraped_data.extend(valid_results)
    else:
        valid_results = []

    if scraped_data:
        save_rows(scraped_data)
        final_row_count = len(scraped_data)
        new_row_count = final_row_count - existing_row_count
        new_vacant_lot_count = sum(1 for row in valid_results if is_lot_listing(row))

        print(f"\nSuccessfully exported {final_row_count} total records to {CSV_FILENAME}")
        print(f"Rows before scrape: {existing_row_count}")
        print(f"Rows after scrape: {final_row_count}")
        print(f"New rows added: {new_row_count}")
        print(f"New vacant-lot listings added: {new_vacant_lot_count}")
    else:
        print("\nNo new data scraped.")


if __name__ == "__main__":
    main()
