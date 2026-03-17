import requests
from bs4 import BeautifulSoup
import json
import re

def test_scrape():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    test_url = "https://www.lamudi.com.ph/property/41032-73-786b2dbc79d-84fe-197f957-9572-71b0"
    print(f"\nFetching property URL: {test_url}")
    
    try:
        prop_response = requests.get(test_url, headers=headers, timeout=10)
        prop_response.raise_for_status()
    except Exception as e:
        print(f"Property request failed: {e}")
        return
        
    prop_soup = BeautifulSoup(prop_response.text, 'html.parser')
    
    print("\n--- Extracted Data ---")

    # The most reliable way to get real estate data is from the Schema.org JSON-LD scripts
    json_scripts = prop_soup.find_all('script', type='application/ld+json')
    
    property_data = {}
    
    for script in json_scripts:
        try:
            data = json.loads(script.string)
            # JSON-LD can be a single object or a '@graph' array
            items = data.get('@graph', [data])
            
            for item in items:
                if item.get('@type') == 'Accommodation' or item.get('@type') == 'SingleFamilyResidence':
                    property_data['title'] = item.get('name', 'Not found')
                    property_data['description'] = item.get('description', 'Not found')
                    property_data['bedrooms'] = item.get('numberOfBedrooms', 'Not found')
                    property_data['bathrooms'] = item.get('numberOfBathroomsTotal', 'Not found')
                    
                    if 'floorSize' in item:
                        property_data['floor_area'] = item['floorSize'].get('value', 'Not found')
                    
                    if 'address' in item:
                        address_obj = item['address']
                        property_data['street_address'] = address_obj.get('streetAddress', 'Not found')
                        property_data['city'] = address_obj.get('addressLocality', 'Not found')
                        property_data['region'] = address_obj.get('addressRegion', 'Not found')
                        
                    if 'geo' in item:
                        geo_obj = item['geo']
                        property_data['latitude'] = geo_obj.get('latitude', 'Not found')
                        property_data['longitude'] = geo_obj.get('longitude', 'Not found')
                        
                    # Amenities
                    if 'amenityFeature' in item:
                        amenities = [a.get('name') for a in item['amenityFeature'] if 'name' in a]
                        property_data['amenities'] = ', '.join(amenities)

        except json.JSONDecodeError:
            continue
            
    # Fallback to HTML parsing if JSON-LD parsing failed for some fields
    
    # Try to find Price
    price_element = prop_soup.find(attrs={"data-name": "property-price"}) or prop_soup.select_one('.ListingPrice')
    price = price_element.text.strip() if price_element else "Not found"
    property_data['price'] = price
    
    # Print the final dictionary
    for k, v in property_data.items():
        # Truncate description for readability in terminal
        if k == 'description' and len(str(v)) > 100:
            print(f"{k.capitalize()}: {str(v)[:100]}...")
        else:
            print(f"{k.capitalize()}: {v}")

if __name__ == "__main__":
    test_scrape()
