import requests
from bs4 import BeautifulSoup
import json
import time
import random
import pandas as pd
import os

def extract_property_details(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"  [!] Failed to fetch property {url}: {e}")
        return None
        
    soup = BeautifulSoup(response.text, 'html.parser')
    json_scripts = soup.find_all('script', type='application/ld+json')
    
    property_data = {'url': url}
    
    for script in json_scripts:
        try:
            data = json.loads(script.string)
            items = data.get('@graph', [data])
            
            for item in items:
                if item.get('@type') in ['Accommodation', 'SingleFamilyResidence', 'House', 'Apartment', 'RealEstateAgent']:
                    if 'name' in item: property_data['title'] = item['name']
                    if 'description' in item: property_data['description'] = item['description']
                    if 'numberOfBedrooms' in item: property_data['bedrooms'] = item['numberOfBedrooms']
                    if 'numberOfBathroomsTotal' in item: property_data['bathrooms'] = item['numberOfBathroomsTotal']
                    
                    if 'floorSize' in item:
                        property_data['floor_area_sqm'] = item['floorSize'].get('value')
                    
                    if 'address' in item:
                        addr = item['address']
                        property_data['street_address'] = addr.get('streetAddress')
                        property_data['city'] = addr.get('addressLocality')
                        property_data['region'] = addr.get('addressRegion')
                        
                    if 'geo' in item:
                        geo = item['geo']
                        property_data['latitude'] = geo.get('latitude')
                        property_data['longitude'] = geo.get('longitude')
                        
                    if 'amenityFeature' in item:
                        amenities = [a.get('name') for a in item['amenityFeature'] if 'name' in a]
                        property_data['amenities'] = ', '.join(amenities)
                        
        except json.JSONDecodeError:
            continue

    # Fallback to get price if missing from JSON-LD
    price = None
    
    # Try multiple common Lamudi price selectors
    price_selectors = [
        ".prices-and-fees__price",
        {"data-name": "property-price"},
        ".ListingPrice", 
        ".FirstPrice",
        ".price"
    ]
    
    for selector in price_selectors:
        if isinstance(selector, dict):
            price_element = soup.find(attrs=selector)
        else:
            price_element = soup.select_one(selector)
            
        if price_element and price_element.text.strip():
            price = price_element.text.strip()
            # Clean up the price string (e.g., "₱ 4,500,000" -> "4500000")
            price = price.replace('₱', '').replace(',', '').strip()
            break
            
    property_data['price'] = price
    
    return property_data

def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    # Read links from our previous run
    if not os.path.exists('property_links.txt'):
        print("Error: property_links.txt not found. Run scrape_index.py first.")
        return
        
    with open('property_links.txt', 'r') as f:
        links = [line.strip() for line in f if line.strip()]
        
    print(f"Loaded {len(links)} properties to scrape.")
    
    # Read all links
    test_links = links
    
    # Optional: save partial progress to avoid losing data if it crashes halfway
    csv_filename = 'lamudi_cebu_full.csv'
    
    # Use thread pool for concurrent scraping
    max_workers = 5
    
    # Try to load existing progress if any
    scraped_data = []
    if os.path.exists(csv_filename):
        try:
            existing_df = pd.read_csv(csv_filename)
            scraped_data = existing_df.to_dict('records')
            print(f"Loaded {len(scraped_data)} existing records from {csv_filename}")
            # Filter out already scraped links
            scraped_urls = set(existing_df['url'].tolist())
            test_links = [l for l in test_links if l not in scraped_urls]
            print(f"Remaining URLs to scrape: {len(test_links)}")
        except Exception as e:
            print(f"Error loading existing CSV: {e}")
            
    print(f"Starting concurrent scraping with {max_workers} workers...")
    
    # Create thread locks and counters
    import threading
    progress_lock = threading.Lock()
    progress_counter = 0
    total_to_scrape = len(test_links)
    
    def process_link(link):
        nonlocal progress_counter
        data = extract_property_details(link, headers)
        
        # Polite delay per thread
        sleep_time = random.uniform(1.5, 3.5)
        time.sleep(sleep_time)
        
        with progress_lock:
            progress_counter += 1
            if progress_counter % 10 == 0:
                print(f"Scraping progress: [{progress_counter}/{total_to_scrape}]")
                # Save intermediate progress every 50 properties
            if progress_counter % 50 == 0 and data:
                 temp_data = scraped_data + [data] # Add current to existing just for saving
                 pd.DataFrame(temp_data).to_csv(csv_filename, index=False)
                 print(f"--- Saved intermediate progress ({len(temp_data)} rows) ---")
                 
        return data

    import concurrent.futures
    
    # Execute with thread pool
    if test_links:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(process_link, test_links))
            
        # Filter None results
        valid_results = [r for r in results if r]
        scraped_data.extend(valid_results)
    
    # Export final CSV
    if scraped_data:
        df = pd.DataFrame(scraped_data)
        df.to_csv(csv_filename, index=False)
        print(f"\nSuccessfully exported {len(scraped_data)} total records to {csv_filename}")
    else:
        print("\nNo new data scraped.")

if __name__ == "__main__":
    main()
