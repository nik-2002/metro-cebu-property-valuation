import os
import random
import re
import subprocess
import time
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import pandas as pd
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
BASE_DOMAIN = "https://www.lamudi.com.ph"
CITY_SLUGS = ["cebu", "mandaue", "lapu-lapu", "talisay", "minglanilla", "consolacion"]
GENERIC_BUY_TEMPLATE = f"{BASE_DOMAIN}/{{city}}/buy/"
LAND_PATTERN_CANDIDATES = [
    f"{BASE_DOMAIN}/{{city}}/land/buy/",
    f"{BASE_DOMAIN}/{{city}}/buy/land/",
    f"{BASE_DOMAIN}/{{city}}/lot/buy/",
]
CSV_FILENAME = "lamudi_cebu_full.csv"
LINKS_FILENAME = "property_links.txt"


def fetch_html(url, session, timeout=15):
    try:
        response = session.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        if "window.gokuProps" in response.text:
            raise requests.exceptions.RequestException("Lamudi WAF challenge page returned")
        return response.text, response.url
    except requests.exceptions.RequestException:
        curl_command = [
            "curl",
            "-L",
            "--compressed",
            "-sS",
            "-A",
            HEADERS["User-Agent"],
            "-H",
            f"Accept: {HEADERS['Accept']}",
            "-H",
            f"Accept-Language: {HEADERS['Accept-Language']}",
            "--max-time",
            str(timeout),
            url,
        ]
        result = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        if "window.gokuProps" in result.stdout:
            raise requests.exceptions.RequestException("Lamudi WAF challenge page returned after curl fallback")
        return result.stdout, url


def normalize_property_url(href):
    if href.startswith("http"):
        return href
    if href.startswith("/"):
        return f"{BASE_DOMAIN}{href}"
    return f"{BASE_DOMAIN}/{href}"


def extract_property_links_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    property_links = set()

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        if "/property/" in href or href.endswith(".html"):
            property_links.add(normalize_property_url(href))

    return sorted(property_links)


def with_page_query(base_url, page):
    parts = urlsplit(base_url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["page"] = str(page)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def discover_land_category_template(session, sample_city="cebu"):
    print(f"Testing land/lot index URL patterns with sample city '{sample_city}':")
    confirmed_template = None

    for pattern in LAND_PATTERN_CANDIDATES:
        test_url = pattern.format(city=sample_city)
        property_links = []

        try:
            html, final_url = fetch_html(test_url, session=session, timeout=15)
            property_links = extract_property_links_from_html(html)
            print(
                f"  Pattern {test_url} -> {len(property_links)} /property/ links "
                f"(final URL: {final_url})"
            )
        except requests.exceptions.RequestException as exc:
            print(f"  Pattern {test_url} failed: {exc}")
            continue

        if property_links and confirmed_template is None:
            final_url = final_url.rstrip("/")
            confirmed_template = re.sub(
                rf"/{re.escape(sample_city)}(?=/|$)",
                "/{city}",
                final_url,
                count=1,
            ) + "/"

    if not confirmed_template:
        raise RuntimeError("Could not confirm a working land/lot index URL pattern.")

    print(f"Confirmed land/lot category pattern: {confirmed_template}")
    return confirmed_template


def build_index_targets(land_template):
    targets = []

    for city in CITY_SLUGS:
        targets.append(
            {
                "city": city,
                "category": "generic_buy",
                "base_url": GENERIC_BUY_TEMPLATE.format(city=city),
            }
        )
        targets.append(
            {
                "city": city,
                "category": "land_lot",
                "base_url": land_template.format(city=city),
            }
        )

    return targets


def load_existing_urls(csv_filename):
    if not os.path.exists(csv_filename):
        return set()

    df = pd.read_csv(csv_filename)
    if "url" not in df.columns:
        return set()

    return set(df["url"].dropna())


def scrape_index_pages(base_url, city, category, seen_urls, session, max_pages=100):
    new_links = []
    new_links_seen = set()
    pages_requested = 0

    for page in range(1, max_pages + 1):
        page_url = with_page_query(base_url, page)
        pages_requested += 1
        print(f"[{city} | {category}] Scraping page {page}: {page_url}")

        try:
            html, _ = fetch_html(page_url, session=session, timeout=15)
        except requests.exceptions.RequestException as exc:
            print(f"[{city} | {category}] Failed to fetch page {page}: {exc}")
            break

        page_links = extract_property_links_from_html(html)
        page_new_links = [
            link
            for link in page_links
            if link not in seen_urls and link not in new_links_seen
        ]

        print(
            f"[{city} | {category}] Page {page}: "
            f"{len(page_links)} property links, {len(page_new_links)} new"
        )

        if not page_links:
            print(f"[{city} | {category}] No property links found on page {page}; stopping early.")
            break

        new_links.extend(page_new_links)
        new_links_seen.update(page_new_links)

        sleep_time = random.uniform(0.25, 0.5)
        time.sleep(sleep_time)

    summary = {
        "city": city,
        "category": category,
        "pages_scraped": pages_requested,
        "new_links_found": len(new_links),
    }
    print(
        f"Summary -> city={city}, category={category}, pages_scraped={pages_requested}, "
        f"new_links_found={len(new_links)}"
    )

    return new_links, summary


def main():
    session = requests.Session()
    existing_urls = load_existing_urls(CSV_FILENAME)
    print(f"Loaded {len(existing_urls)} already-scraped URLs from {CSV_FILENAME}")

    land_template = discover_land_category_template(session)
    index_targets = build_index_targets(land_template)

    all_new_links = []
    run_seen_urls = set(existing_urls)
    summaries = []

    for target in index_targets:
        target_links, summary = scrape_index_pages(
            base_url=target["base_url"],
            city=target["city"],
            category=target["category"],
            seen_urls=run_seen_urls,
            session=session,
            max_pages=100,
        )
        all_new_links.extend(target_links)
        run_seen_urls.update(target_links)
        summaries.append(summary)

    deduped_new_links = list(dict.fromkeys(all_new_links))

    with open(LINKS_FILENAME, "w") as handle:
        for link in deduped_new_links:
            handle.write(f"{link}\n")

    print("\n--- Per-URL Summary ---")
    for summary in summaries:
        print(
            f"city={summary['city']}, category={summary['category']}, "
            f"pages_scraped={summary['pages_scraped']}, new_links_found={summary['new_links_found']}"
        )

    print(f"\nTotal NEW links written to {LINKS_FILENAME}: {len(deduped_new_links)}")


if __name__ == "__main__":
    main()
