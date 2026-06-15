import os
import argparse
import pandas as pd

import parse
from browser import LamudiBrowser

def ensure_csv_columns(df):
    for column in parse.CSV_COLUMNS:
        if column not in df.columns:
            df[column] = None
    return df.reindex(columns=parse.CSV_COLUMNS)


def main():
    parser = argparse.ArgumentParser(description="Lamudi Playwright Property Details Scraper")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    args = parser.parse_args()

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    links_filename = os.path.join(SCRIPT_DIR, "property_links.txt")
    canonical_csv_path = os.path.join(SCRIPT_DIR, "../Data/webscraping-lamudi/lamudi_cebu_full.csv")
    scraped_csv_path = os.path.join(SCRIPT_DIR, "data/lamudi_scraped.csv")

    if not os.path.exists(links_filename):
        print(f"Error: {links_filename} not found. Run scrape_index.py first.")
        return

    with open(links_filename, "r") as handle:
        links = [line.strip() for line in handle if line.strip()]

    links = list(dict.fromkeys(links))
    print(f"Loaded {len(links)} properties to scrape.")

    scraped_data = []
    existing_urls = set()

    # Load local scraped CSV if it exists
    if os.path.exists(scraped_csv_path):
        try:
            existing_df = ensure_csv_columns(pd.read_csv(scraped_csv_path))
            scraped_data = existing_df.to_dict("records")
            local_urls = set(existing_df["url"].dropna().tolist())
            existing_urls.update(local_urls)
            print(f"Loaded {len(scraped_data)} existing records from local output {scraped_csv_path}")
        except Exception as exc:
            print(f"Error loading local scraped CSV: {exc}")

    # Load canonical CSV URLs to skip them as well
    if os.path.exists(canonical_csv_path):
        try:
            canonical_df = pd.read_csv(canonical_csv_path)
            if "url" in canonical_df.columns:
                canonical_urls = set(canonical_df["url"].dropna().tolist())
                existing_urls.update(canonical_urls)
                print(f"Loaded {len(canonical_urls)} URLs from canonical CSV to skip")
        except Exception as exc:
            print(f"Error loading canonical CSV: {exc}")

    pending_links = [link for link in links if link not in existing_urls]
    print(f"Remaining URLs to scrape: {len(pending_links)}")

    new_scraped_data = []
    progress_counter = 0
    valid_results_count = 0
    new_vacant_lot_count = 0
    total_to_scrape = len(pending_links)

    def save_rows(rows):
        os.makedirs(os.path.dirname(scraped_csv_path), exist_ok=True)
        df = ensure_csv_columns(pd.DataFrame(rows))
        df.to_csv(scraped_csv_path, index=False)

    if pending_links:
        print("Starting sequential Playwright scraping...")
        with LamudiBrowser(headless=args.headless) as b:
            b.warm_up()
            
            for link in pending_links:
                progress_counter += 1
                print(f"\n[{progress_counter}/{total_to_scrape}] Fetching: {link}")
                
                try:
                    html = b.fetch(link)
                    data = parse.parse_property_html(link, html)
                    if data:
                        new_scraped_data.append(data)
                        valid_results_count += 1
                        if parse.is_lot_listing(data):
                            new_vacant_lot_count += 1
                        print(f"  [+] Success: {data.get('title', 'No Title')[:50]}")
                    else:
                        print("  [-] Skipped or invalid listing page")
                except Exception as exc:
                    print(f"  [!] Failed to fetch/parse property {link}: {exc}")

                # Save intermediate progress every 25 successful rows
                if valid_results_count > 0 and valid_results_count % 25 == 0:
                    temp_rows = scraped_data + new_scraped_data
                    save_rows(temp_rows)
                    print(f"--- Saved intermediate progress ({len(temp_rows)} rows) ---")

        final_rows = scraped_data + new_scraped_data
        save_rows(final_rows)
        rows_before = len(scraped_data)
        rows_after = len(final_rows)
        new_rows_added = len(new_scraped_data)

        print(f"\nSuccessfully exported {rows_after} total records to {scraped_csv_path}")
        print(f"Rows before scrape: {rows_before}")
        print(f"Rows after scrape: {rows_after}")
        print(f"New rows added: {new_rows_added}")
        print(f"New vacant-lot listings added: {new_vacant_lot_count}")
    else:
        print("\nNo new data scraped.")
        rows_before = len(scraped_data)
        rows_after = len(scraped_data)
        new_rows_added = 0
        print(f"Rows before scrape: {rows_before}")
        print(f"Rows after scrape: {rows_after}")
        print(f"New rows added: {new_rows_added}")
        print(f"New vacant-lot listings added: {new_vacant_lot_count}")


if __name__ == "__main__":
    main()
