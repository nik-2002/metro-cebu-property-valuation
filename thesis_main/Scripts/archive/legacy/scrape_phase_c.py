from __future__ import annotations

import argparse
import json
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import Lock
from typing import Any
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

import pandas as pd
import requests

OUTPUT_CSV = Path("thesis_main/Data/raw/phase_c_listings.csv")
CHECKPOINT_JSON = Path("thesis_main/Data/raw/phase_c_listings_progress.json")
MAX_PAGES_DEFAULT = 50
CSV_WRITE_LOCK = Lock()
CHECKPOINT_LOCK = Lock()
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

OUTPUT_COLUMNS = [
    "source",
    "property_name",
    "address",
    "city",
    "property_type",
    "lot_area_sqm",
    "floor_area_sqm",
    "bedrooms",
    "bathrooms",
    "price_php",
    "listing_url",
    "market_segment",
]

TARGET_CITIES = {
    "Cebu City",
    "Mandaue City",
    "Lapu-Lapu City",
    "Talisay City",
    "Minglanilla",
    "Consolacion",
    "Naga City",
}

CITY_PATTERNS = [
    (re.compile(r"\bcebu\s+city\b", re.I), "Cebu City"),
    (re.compile(r"\bmandaue\s+city\b|\bmandaue\b", re.I), "Mandaue City"),
    (re.compile(r"\blapu[-\s]?lapu\s+city\b|\blapu[-\s]?lapu\b|\bopon\b", re.I), "Lapu-Lapu City"),
    (re.compile(r"\btalisay\s+city\b|\btalisay\b", re.I), "Talisay City"),
    (re.compile(r"\bminglanilla\b", re.I), "Minglanilla"),
    (re.compile(r"\bconsolacion\b", re.I), "Consolacion"),
    (re.compile(r"\bnaga\s+city\b|\bcity\s+of\s+naga\b|\bnaga,\s*cebu\b", re.I), "Naga City"),
]

EXCLUDED_KEYWORDS = [
    "commercial",
    "industrial",
    "farm lot",
    "farm-lot",
    "agricultural",
    "office",
    "warehouse",
    "retail space",
    "soho",
]

PROPERTY_TYPE_RULES = [
    (re.compile(r"\bcondo(?:minium)?\b|\bapartment\b|\bpenthouse\b|\bstudio\b", re.I), "Condominium"),
    (re.compile(r"\bsingle[-\s]?detached\b|\bdetached\s+house\b|\bstandalone\s+house\b", re.I), "Single Detached"),
    (re.compile(r"\btownhouse\b|\bduplex\b|\bsingle[-\s]?attached\b|\battached\s+house\b|\browhouse\b", re.I), "Townhouse"),
    (re.compile(r"\bvacant\s+lot\b|\blot\s+only\b|\bresidential\s+lot\b|\bplot\s+of\s+land\b|\bland\s+for\s+sale\b", re.I), "Vacant Lot"),
    (re.compile(r"\bhouse\s*(?:and|&)\s*lot\b|\bhouse\s+for\s+sale\b|\bvilla\b|\bhome\s+for\s+sale\b|\bhouse\b", re.I), "House and Lot"),
    (re.compile(r"\bresidential\b", re.I), "Residential"),
]

SITE_CONFIGS = {
    "property24": {"base_url": "https://www.property24.com.ph/property-for-sale-in-cebu-p270", "page_param": "page", "allowed_domains": {"www.property24.com.ph", "property24.com.ph"}},
    "dotproperty": {"base_url": "https://www.dotproperty.com.ph/properties-for-sale/cebu", "page_param": "page", "allowed_domains": {"www.dotproperty.com.ph", "dotproperty.com.ph"}},
    "olx": {"base_url": "https://www.olx.ph/real-estate/real-estate-for-sale/ph-ceb-cebu-city", "page_param": "page", "allowed_domains": {"www.olx.ph", "olx.ph"}},
    "carousell": {"base_url": "https://www.carousell.ph/property-for-sale/house-lot/cebu/", "page_param": "page", "allowed_domains": {"www.carousell.ph", "carousell.ph"}},
    "myproperty": {"base_url": "https://www.myproperty.ph/buy/cebu/", "page_param": "page", "allowed_domains": {"www.myproperty.ph", "myproperty.ph"}},
}


class WorkerSession:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept-Language": "en-PH,en-US;q=0.9,en;q=0.8",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }
        )
        self._request_count = 0

    def get(self, url: str, *, timeout: tuple[int, int] = (15, 30)) -> str | None:
        if self._request_count:
            time.sleep(random.uniform(1.0, 2.0))
        self._request_count += 1
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            if not response.text or len(response.text) < 200:
                return None
            return response.text
        except requests.RequestException:
            return None


def update_query(url: str, key: str, value: Any) -> str:
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query[key] = str(value)
    return urlunparse(parsed._replace(query=urlencode(query)))


def page_url(source: str, page: int) -> str:
    base_url = SITE_CONFIGS[source]["base_url"]
    if page <= 1:
        return base_url
    return update_query(base_url, SITE_CONFIGS[source]["page_param"], page)


def normalize_space(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def strip_tags(html: str) -> str:
    without_scripts = re.sub(r"<script\b.*?</script>", " ", html, flags=re.I | re.S)
    without_styles = re.sub(r"<style\b.*?</style>", " ", without_scripts, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", without_styles)
    text = text.replace("&nbsp;", " ")
    text = text.replace("&amp;", "&")
    return normalize_space(text)


def extract_title(html: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.I | re.S)
    return normalize_space(match.group(1)) if match else ""


def extract_meta(html: str, *keys: str) -> str:
    for key in keys:
        pattern = re.compile(
            rf"<meta[^>]+(?:property|name)=[\"']{re.escape(key)}[\"'][^>]+content=[\"'](.*?)[\"'][^>]*>",
            flags=re.I | re.S,
        )
        match = pattern.search(html)
        if match:
            return normalize_space(match.group(1))
    return ""


def extract_json_ld_objects(html: str) -> list[Any]:
    objects: list[Any] = []
    for payload in re.findall(
        r"<script[^>]+type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
        html,
        flags=re.I | re.S,
    ):
        candidate = payload.strip()
        if not candidate:
            continue
        try:
            objects.append(json.loads(candidate))
        except json.JSONDecodeError:
            continue
    return objects


def walk_json(data: Any) -> list[Any]:
    items: list[Any] = []
    if isinstance(data, dict):
        items.append(data)
        for value in data.values():
            items.extend(walk_json(value))
    elif isinstance(data, list):
        for value in data:
            items.extend(walk_json(value))
    return items


def first_json_value(objects: list[Any], *keys: str) -> str:
    for obj in objects:
        for item in walk_json(obj):
            if not isinstance(item, dict):
                continue
            for key in keys:
                value = item.get(key)
                if isinstance(value, str) and normalize_space(value):
                    return normalize_space(value)
    return ""


def parse_php_number(value: str) -> float | None:
    if not value:
        return None
    if re.search(r"\bUSD\b|US\$|\$", value, flags=re.I):
        return None
    cleaned = re.sub(r"[^\d.,]", "", value)
    if not cleaned:
        return None
    if cleaned.count(",") and cleaned.count("."):
        cleaned = cleaned.replace(",", "")
    elif cleaned.count(",") > 1:
        cleaned = cleaned.replace(",", "")
    elif cleaned.count(",") == 1 and cleaned.count(".") == 0:
        cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def json_price(objects: list[Any]) -> float | None:
    for obj in objects:
        for item in walk_json(obj):
            if not isinstance(item, dict):
                continue
            for key in ("price", "lowPrice", "highPrice"):
                value = item.get(key)
                if value is None:
                    continue
                parsed = parse_php_number(str(value))
                if parsed is None:
                    continue
                currency = normalize_space(str(item.get("priceCurrency", "PHP")))
                if currency.upper() == "PHP":
                    return parsed
    return None


def extract_price(text: str, objects: list[Any]) -> float | None:
    price = json_price(objects)
    if price is not None:
        return price
    match = re.search(r"(?:₱|PHP|Php)\s*([\d,]+(?:\.\d+)?)", text)
    return parse_php_number(match.group(1)) if match else None


def extract_float(patterns: list[str], text: str) -> float | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            try:
                return float(match.group(1).replace(",", ""))
            except ValueError:
                continue
    return None


def extract_lot_area(text: str) -> float | None:
    return extract_float(
        [
            r"lot\s*area[^\d]{0,20}([\d,]+(?:\.\d+)?)\s*(?:sqm|sq\.?m|m2)",
            r"land\s*area[^\d]{0,20}([\d,]+(?:\.\d+)?)\s*(?:sqm|sq\.?m|m2)",
        ],
        text,
    )


def extract_floor_area(text: str) -> float | None:
    return extract_float(
        [
            r"floor\s*area[^\d]{0,20}([\d,]+(?:\.\d+)?)\s*(?:sqm|sq\.?m|m2)",
            r"building\s*area[^\d]{0,20}([\d,]+(?:\.\d+)?)\s*(?:sqm|sq\.?m|m2)",
            r"interior[^\d]{0,20}([\d,]+(?:\.\d+)?)\s*(?:sqm|sq\.?m|m2)",
        ],
        text,
    )


def extract_bedrooms(text: str) -> float | None:
    return extract_float(
        [
            r"([\d.]+)\s*(?:beds?|bedrooms?)\b",
            r"bedrooms?[^\d]{0,10}([\d.]+)\b",
        ],
        text,
    )


def extract_bathrooms(text: str) -> float | None:
    return extract_float(
        [
            r"([\d.]+)\s*(?:baths?|bathrooms?)\b",
            r"bathrooms?[^\d]{0,10}([\d.]+)\b",
            r"toilets?\s*and\s*baths?[^\d]{0,10}([\d.]+)\b",
        ],
        text,
    )


def resolve_city(*values: str) -> str | None:
    haystack = " | ".join(value for value in values if value)
    for pattern, canonical in CITY_PATTERNS:
        if pattern.search(haystack):
            return canonical
    return None


def is_excluded(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in EXCLUDED_KEYWORDS)


def map_property_type(*values: str) -> str | None:
    haystack = " | ".join(value for value in values if value)
    if is_excluded(haystack):
        return None
    for pattern, mapped in PROPERTY_TYPE_RULES:
        if pattern.search(haystack):
            return mapped
    return None


def clean_listing_url(source: str, href: str) -> str | None:
    if not href:
        return None
    absolute = urljoin(SITE_CONFIGS[source]["base_url"], href)
    parsed = urlparse(absolute)
    if parsed.netloc not in SITE_CONFIGS[source]["allowed_domains"]:
        return None
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    for key in list(query):
        lowered = key.lower()
        if lowered.startswith("utm_") or lowered.startswith("t-"):
            query.pop(key, None)
    return urlunparse(parsed._replace(query=urlencode(query)))


def extract_listing_links(source: str, html: str) -> list[str]:
    patterns = {
        "property24": [
            r'href=["\']([^"\']*property24\.com\.ph[^"\']+)["\']',
            r'href=["\'](/[^"\']+)["\']',
        ],
        "dotproperty": [
            r'href=["\']([^"\']*dotproperty\.com\.ph/ads/[^"\']+)["\']',
            r'href=["\'](/ads/[^"\']+)["\']',
            r'href=["\'](/(?:condo|house|townhouse|land)/[^"\']+)["\']',
        ],
        "olx": [
            r'href=["\']([^"\']*/item/[^"\']+)["\']',
            r'href=["\'](/d/[^"\']+)["\']',
        ],
        "carousell": [r'href=["\'](/p/[^"\']+-\d+[^"\']*)["\']'],
        "myproperty": [r'href=["\'](/property/[^"\']+)["\']'],
    }
    links: list[str] = []
    seen: set[str] = set()
    for pattern in patterns[source]:
        for match in re.findall(pattern, html, flags=re.I):
            cleaned = clean_listing_url(source, match)
            if not cleaned or cleaned in seen:
                continue
            if source == "dotproperty" and "/properties-for-sale/" in cleaned:
                continue
            if source == "myproperty" and "/projects/" in cleaned:
                continue
            links.append(cleaned)
            seen.add(cleaned)
    return links


def derive_address(title: str, description: str, text_blob: str) -> str:
    match = re.search(r"(?:address|location)\s*[:\-]\s*([^|]{10,180})", text_blob, flags=re.I)
    if match:
        return normalize_space(match.group(1))
    for candidate in (description, title, text_blob[:180]):
        candidate = normalize_space(candidate)
        if candidate:
            return candidate
    return ""


def parse_detail_page(source: str, url: str, html: str) -> dict[str, Any] | None:
    objects = extract_json_ld_objects(html)
    title = first_json_value(objects, "name", "headline")
    if not title:
        title = extract_meta(html, "og:title", "twitter:title") or extract_title(html)
    description = first_json_value(objects, "description") or extract_meta(html, "description", "og:description")
    text_blob = strip_tags(html)

    json_address = ""
    for obj in objects:
        for item in walk_json(obj):
            if not isinstance(item, dict):
                continue
            address = item.get("address")
            if isinstance(address, dict):
                parts = []
                for key in ("streetAddress", "addressLocality", "addressRegion"):
                    value = address.get(key)
                    if value:
                        parts.append(str(value))
                json_address = normalize_space(", ".join(parts))
                if json_address:
                    break
            if isinstance(address, str) and normalize_space(address):
                json_address = normalize_space(address)
                break
        if json_address:
            break

    combined = " | ".join(value for value in [title, description, json_address, text_blob, url] if value)
    property_type = map_property_type(title, description, text_blob, url)
    if not property_type:
        return None

    price_php = extract_price(combined, objects)
    if price_php is None:
        return None

    city = resolve_city(json_address, title, description, text_blob, url)
    if city is None or city not in TARGET_CITIES:
        return None

    address = json_address or derive_address(title, description, text_blob)
    if not address:
        return None

    row = {
        "source": source,
        "property_name": normalize_space(re.sub(r"\s*[|\-]\s*(Property24|Dot Property|MyProperty|Carousell|OLX).*", "", title, flags=re.I)),
        "address": address,
        "city": city,
        "property_type": property_type,
        "lot_area_sqm": extract_lot_area(combined),
        "floor_area_sqm": extract_floor_area(combined),
        "bedrooms": extract_bedrooms(combined),
        "bathrooms": extract_bathrooms(combined),
        "price_php": price_php,
        "listing_url": url,
        "market_segment": "open_market",
    }

    generic_area = extract_float([r"([\d,]+(?:\.\d+)?)\s*(?:sqm|sq\.?m|m2)"], combined)
    if row["property_type"] == "Vacant Lot" and row["lot_area_sqm"] is None:
        row["lot_area_sqm"] = generic_area
    if row["property_type"] == "Condominium" and row["floor_area_sqm"] is None:
        row["floor_area_sqm"] = generic_area
    return row


def load_existing_rows() -> list[dict[str, Any]]:
    if not OUTPUT_CSV.exists():
        return []
    try:
        frame = pd.read_csv(OUTPUT_CSV)
    except Exception:
        return []
    if frame.empty:
        return []
    for column in OUTPUT_COLUMNS:
        if column not in frame.columns:
            frame[column] = pd.NA
    frame = frame[OUTPUT_COLUMNS].copy()
    return frame.where(pd.notna(frame), None).to_dict("records")


def load_checkpoint() -> dict[str, Any]:
    if not CHECKPOINT_JSON.exists():
        return {}
    try:
        return json.loads(CHECKPOINT_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_checkpoint(checkpoint: dict[str, Any]) -> None:
    CHECKPOINT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", dir=str(CHECKPOINT_JSON.parent), delete=False, encoding="utf-8") as handle:
        json.dump(checkpoint, handle, indent=2, sort_keys=True)
        temp_path = Path(handle.name)
    temp_path.replace(CHECKPOINT_JSON)


def update_checkpoint(checkpoint: dict[str, Any], source: str, *, page: int, last_listing_url: str | None, completed: bool = False) -> None:
    with CHECKPOINT_LOCK:
        checkpoint[source] = {
            "page": page,
            "last_listing_url": last_listing_url,
            "completed": completed,
        }
        save_checkpoint(checkpoint)


def scrape_source(source: str, max_pages: int, max_listings_per_site: int | None = None, checkpoint: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    worker = WorkerSession()
    rows: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    previous_fingerprint: set[str] | None = None
    source_checkpoint = checkpoint.get(source, {}) if checkpoint else {}
    if source_checkpoint.get("completed"):
        return rows
    resume_page = int(source_checkpoint.get("page", 1))
    resume_after_url = source_checkpoint.get("last_listing_url")
    if resume_page > 1 or resume_after_url:
        print(f"[{source}] resuming from page {resume_page}" + (f" after {resume_after_url}" if resume_after_url else ""))

    for page in range(1, max_pages + 1):
        if page < resume_page:
            continue
        html = worker.get(page_url(source, page))
        if not html:
            break
        listing_urls = extract_listing_links(source, html)
        if not listing_urls:
            update_checkpoint(checkpoint, source, page=page, last_listing_url=None, completed=True)
            break
        fingerprint = set(listing_urls)
        if previous_fingerprint is not None and fingerprint == previous_fingerprint:
            update_checkpoint(checkpoint, source, page=page, last_listing_url=None, completed=True)
            break
        previous_fingerprint = fingerprint
        new_urls = [url for url in listing_urls if url not in seen_urls]
        if page == resume_page and resume_after_url:
            if resume_after_url in new_urls:
                resume_index = new_urls.index(resume_after_url)
                new_urls = new_urls[resume_index + 1 :]
            resume_after_url = None
        if not new_urls:
            update_checkpoint(checkpoint, source, page=page + 1, last_listing_url=None)
            continue
        for listing_url in new_urls:
            seen_urls.add(listing_url)
            detail_html = worker.get(listing_url)
            if detail_html:
                parsed = parse_detail_page(source, listing_url, detail_html)
                if parsed is not None:
                    rows.append(parsed)
                    append_row_to_csv(parsed)
                    if max_listings_per_site is not None and len(rows) >= max_listings_per_site:
                        update_checkpoint(checkpoint, source, page=page, last_listing_url=listing_url)
                        return rows
            update_checkpoint(checkpoint, source, page=page, last_listing_url=listing_url)
        print(f"[{source}] page {page} - {len(rows)} rows collected so far")
        update_checkpoint(checkpoint, source, page=page + 1, last_listing_url=None)
    return rows


def finalize_rows(rows: list[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    if frame.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    for column in OUTPUT_COLUMNS:
        if column not in frame.columns:
            frame[column] = pd.NA
    frame = frame[OUTPUT_COLUMNS].copy()
    for column in ["lot_area_sqm", "floor_area_sqm", "bedrooms", "bathrooms", "price_php"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["address"] = frame["address"].astype(str).str.strip()
    frame = frame[frame["price_php"].notna()].copy()
    frame = frame[frame["address"].ne("")].copy()
    frame = frame[frame["city"].isin(TARGET_CITIES)].copy()
    return frame.drop_duplicates(subset=["address", "price_php", "property_type"], keep="first")


def append_row_to_csv(row: dict[str, Any]) -> None:
    with CSV_WRITE_LOCK:
        file_exists = OUTPUT_CSV.exists()
        pd.DataFrame([row], columns=OUTPUT_COLUMNS).to_csv(
            OUTPUT_CSV,
            mode="a",
            header=not file_exists,
            index=False,
        )


def print_summary(raw_frame: pd.DataFrame, deduped_frame: pd.DataFrame) -> None:
    rows_per_source = deduped_frame["source"].value_counts().sort_index().to_dict() if not deduped_frame.empty else {}
    rows_per_city = deduped_frame["city"].value_counts().sort_index().to_dict() if not deduped_frame.empty else {}
    print(f"Total rows scraped: {len(raw_frame)}")
    print(f"After deduplication: {len(deduped_frame)}")
    print(f"Rows per source: {rows_per_source}")
    print(f"Rows per city: {rows_per_city}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape Phase C Metro Cebu listings.")
    parser.add_argument("--max-pages", type=int, default=MAX_PAGES_DEFAULT)
    parser.add_argument("--sources", nargs="*", choices=sorted(SITE_CONFIGS), default=sorted(SITE_CONFIGS))
    parser.add_argument("--max-listings-per-site", type=int, default=None)
    args = parser.parse_args()

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = load_checkpoint()
    all_rows: list[dict[str, Any]] = load_existing_rows()

    with ThreadPoolExecutor(max_workers=len(args.sources)) as executor:
        future_map = {
            executor.submit(scrape_source, source, args.max_pages, args.max_listings_per_site, checkpoint): source
            for source in args.sources
        }
        for future in as_completed(future_map):
            source = future_map[future]
            try:
                all_rows.extend(future.result())
            except Exception as exc:
                print(f"Warning: {source} failed: {exc}")

    raw_frame = pd.DataFrame(all_rows, columns=OUTPUT_COLUMNS)
    deduped_frame = finalize_rows(all_rows)
    deduped_frame.to_csv(OUTPUT_CSV, index=False)
    print_summary(raw_frame, deduped_frame)


if __name__ == "__main__":
    main()
