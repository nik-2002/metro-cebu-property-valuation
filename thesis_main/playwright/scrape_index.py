import os
import re
import argparse
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import pandas as pd
from bs4 import BeautifulSoup

from browser import LamudiBrowser

BASE_DOMAIN = "https://www.lamudi.com.ph"
CITY_SLUGS = ["cebu", "mandaue", "lapu-lapu", "talisay", "minglanilla", "consolacion"]
GENERIC_BUY_TEMPLATE = f"{BASE_DOMAIN}/{{city}}/buy/"
LAND_PATTERN_CANDIDATES = [
    f"{BASE_DOMAIN}/buy/{{city}}/land/",
    f"{BASE_DOMAIN}/{{city}}/land/buy/",
    f"{BASE_DOMAIN}/{{city}}/buy/land/",
    f"{BASE_DOMAIN}/{{city}}/lot/buy/",
]

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


def discover_land_category_template(browser, sample_city="cebu"):
    print(f"Testing land/lot index URL patterns with sample city '{sample_city}':")
    
    # Try the default confirmed pattern first
    confirmed_template = "https://www.lamudi.com.ph/buy/{city}/land/"
    test_url = confirmed_template.format(city=sample_city)
    try:
        html = browser.fetch(test_url)
        property_links = extract_property_links_from_html(html)
        print(f"  Default Pattern {test_url} -> {len(property_links)} /property/ links")
        if property_links:
            print(f"Confirmed land/lot category pattern: {confirmed_template}")
            return confirmed_template
    except Exception as exc:
        print(f"  Default Pattern {test_url} failed: {exc}. Trying candidates...")

    # Fallback to candidates
    for pattern in LAND_PATTERN_CANDIDATES:
        test_url = pattern.format(city=sample_city)
        try:
            html = browser.fetch(test_url)
            property_links = extract_property_links_from_html(html)
            print(f"  Pattern {test_url} -> {len(property_links)} /property/ links")
            if property_links:
                # Standardize pattern back to {city}
                confirmed_template = pattern
                print(f"Confirmed land/lot category pattern: {confirmed_template}")
                return confirmed_template
        except Exception as exc:
            print(f"  Pattern {test_url} failed: {exc}")
            continue

    raise RuntimeError("Could not confirm a working land/lot index URL pattern.")


def build_index_targets(land_template):
    targets = []
    for city in CITY_SLUGS:
        if city == "cebu":
            generic_url = "https://www.lamudi.com.ph/cebu/buy/"
            land_url = land_template.format(city="cebu")
        elif city == "talisay":
            # Talisay, Cebu requires the talisay-2 path with search parameter to avoid Batangas
            generic_url = "https://www.lamudi.com.ph/buy/cebu/talisay-2/?search=Cebu"
            land_url = "https://www.lamudi.com.ph/buy/cebu/talisay-2/land/?search=Cebu"
        else:
            generic_url = f"https://www.lamudi.com.ph/cebu/{city}/buy/"
            # Adapt the land template to inject the cebu/ prefix for specific sub-locations
            if "{city}" in land_template:
                land_url = land_template.replace("{city}", f"cebu/{city}")
            else:
                land_url = f"https://www.lamudi.com.ph/buy/cebu/{city}/land/"
            
        targets.append(
            {
                "city": city,
                "category": "generic_buy",
                "base_url": generic_url,
            }
        )
        targets.append(
            {
                "city": city,
                "category": "land_lot",
                "base_url": land_url,
            }
        )
    return targets


def load_existing_urls(canonical_csv, scraped_csv):
    urls = set()
    
    # Load canonical CSV
    if os.path.exists(canonical_csv):
        try:
            df = pd.read_csv(canonical_csv)
            if "url" in df.columns:
                urls.update(df["url"].dropna())
            print(f"Loaded {len(urls)} existing URLs from canonical CSV: {canonical_csv}")
        except Exception as exc:
            print(f"Error loading canonical CSV: {exc}")
            
    # Load scraped CSV (local output)
    if os.path.exists(scraped_csv):
        try:
            df = pd.read_csv(scraped_csv)
            if "url" in df.columns:
                scraped_urls = set(df["url"].dropna())
                urls.update(scraped_urls)
                print(f"Loaded {len(scraped_urls)} existing URLs from local scraped CSV: {scraped_csv}")
        except Exception as exc:
            print(f"Error loading scraped CSV: {exc}")

    return urls


def scrape_index_pages(base_url, city, category, seen_urls, browser, max_pages=100):
    new_links = []
    new_links_seen = set()
    pages_requested = 0

    for page in range(1, max_pages + 1):
        page_url = with_page_query(base_url, page)
        pages_requested += 1
        print(f"[{city} | {category}] Scraping page {page}: {page_url}")

        try:
            html = browser.fetch(page_url)
        except Exception as exc:
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
    parser = argparse.ArgumentParser(description="Lamudi Playwright Index Scraper")
    parser.add_argument("--max-pages", type=int, default=10, help="Maximum index pages to scrape per target")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    args = parser.parse_args()

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    canonical_csv_path = os.path.join(SCRIPT_DIR, "../Data/webscraping-lamudi/lamudi_cebu_full.csv")
    scraped_csv_path = os.path.join(SCRIPT_DIR, "data/lamudi_scraped.csv")
    links_filename = os.path.join(SCRIPT_DIR, "property_links.txt")

    existing_urls = load_existing_urls(canonical_csv_path, scraped_csv_path)
    print(f"Total seen URLs across environments: {len(existing_urls)}")

    with LamudiBrowser(headless=args.headless) as browser:
        browser.warm_up()
        
        land_template = discover_land_category_template(browser)
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
                browser=browser,
                max_pages=args.max_pages,
            )
            all_new_links.extend(target_links)
            run_seen_urls.update(target_links)
            summaries.append(summary)

        deduped_new_links = list(dict.fromkeys(all_new_links))

        # Ensure directory exists for links
        os.makedirs(os.path.dirname(links_filename), exist_ok=True)
        with open(links_filename, "w") as handle:
            for link in deduped_new_links:
                handle.write(f"{link}\n")

        print("\n--- Per-URL Summary ---")
        for summary in summaries:
            print(
                f"city={summary['city']}, category={summary['category']}, "
                f"pages_scraped={summary['pages_scraped']}, new_links_found={summary['new_links_found']}"
            )

        print(f"\nTotal NEW links written to {links_filename}: {len(deduped_new_links)}")


if __name__ == "__main__":
    main()
