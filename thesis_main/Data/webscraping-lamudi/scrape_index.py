import requests
from bs4 import BeautifulSoup
import time
import random

def scrape_index_pages(base_url, max_pages=3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    all_property_links = []
    
    for page in range(1, max_pages + 1):
        url = f"{base_url}&page={page}"
        print(f"Scraping page {page}: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch page {page}: {e}")
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Method 1: Lamudi index pages hide links without the full domain
        page_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Based on testing, valid property links look like /property/some-id
            if '/property/' in href or href.endswith('.html'):
                # Ensure it's a full URL
                if href.startswith('http'):
                    full_url = href
                elif href.startswith('/'):
                    full_url = f"https://www.lamudi.com.ph{href}"
                else:
                    full_url = f"https://www.lamudi.com.ph/{href}"
                    
                page_links.append(full_url)
                
        # Deduplicate links for this page
        page_links = list(set(page_links))
        print(f"Found {len(page_links)} unique property links on page {page}.")
        
        if not page_links:
            print(f"No property links found on page {page}. We might have hit a captcha, IP block, or the end of results.")
            break
            
        all_property_links.extend(page_links)
        
        # Polite scraping delay
        sleep_time = random.uniform(2.5, 5.5)
        print(f"Sleeping for {sleep_time:.2f} seconds...\n")
        time.sleep(sleep_time)

    # Deduplicate total
    all_property_links = list(set(all_property_links))
    print(f"\n--- Scraping Summary ---")
    print(f"Total unique property links collected: {len(all_property_links)}")
    
    # Save links to a file for later use
    with open('property_links.txt', 'w') as f:
        for link in all_property_links:
            f.write(f"{link}\n")
    print("Saved links to property_links.txt")
    
    return all_property_links

if __name__ == "__main__":
    search_url = "https://www.lamudi.com.ph/buy/?search=Cebu"
    scrape_index_pages(search_url, max_pages=50)
