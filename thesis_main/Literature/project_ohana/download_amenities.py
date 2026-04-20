import fire
import requests
import json
import pandas as pd
import re
import time

OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter"
]
WHITESPACE_PATTERN = re.compile(r'\s+')

# Metro Cebu Bounding Box (South, West, North, East)
CEBU_BBOX = (10.0, 123.7, 10.6, 124.1)

AMENITY_CONFIG = {
    'health': {
        'amenity': ['hospital', 'clinic', 'pharmacy', 'doctors', 'dentist']
    },
    'finance': {
        'amenity': ['bank', 'atm']
    },
    'education': {
        'amenity': ['school', 'university', 'college', 'kindergarten']
    },
    'security': {
        'amenity': ['police', 'fire_station']
    },
    'transport': {
        'amenity': ['bus_station', 'ferry_terminal', 'taxi_terminal']
    },
    'grocery': {
        'amenity': ['marketplace'],
        'shop': ['supermarket', 'mall', 'convenience', 'grocery']
    }
}

def query_osm(tag_key, tag_value, bbox, mirrors=OVERPASS_MIRRORS):
    """Queries a single tag (node, way, rel) within a bbox, trying mirrors."""
    s, w, n, e = bbox
    query = f"""
    [out:json][timeout:120];
    (
      node["{tag_key}"="{tag_value}"]({s},{w},{n},{e});
      way["{tag_key}"="{tag_value}"]({s},{w},{n},{e});
      rel["{tag_key}"="{tag_value}"]({s},{w},{n},{e});
    );
    out center;
    """
    
    for url in mirrors:
        try:
            response = requests.get(url, params={'data': query}, timeout=130)
            if response.status_code == 429:
                time.sleep(10)
                continue
            response.raise_for_status()
            return response.json().get('elements', [])
        except Exception:
            continue
    return []

def get_amenities_data(category, bbox=CEBU_BBOX):
    """
    Fetches amenities for a category by querying each tag individually.
    """
    if category not in AMENITY_CONFIG:
        raise ValueError(f"Category {category} not found in config.")
    
    tags_dict = AMENITY_CONFIG[category]
    print(f"Downloading {category} data for Metro Cebu (tag-by-tag)...")
    
    all_elements = []
    for k, values in tags_dict.items():
        for v in values:
            print(f"  Fetching: {k}={v}...")
            elements = query_osm(k, v, bbox)
            print(f"    Found {len(elements)} elements.")
            all_elements.extend(elements)
            time.sleep(3) # Brief gap between individual tags

    return {'elements': all_elements}

def transform_json_to_list(data, category):
    elements = data.get('elements', [])
    amenities_data = []
    seen_ids = set()

    for el in elements:
        if el['id'] in seen_ids:
            continue
        
        item = {}
        item['id'] = el['id']
        tags = el.get('tags', {})
        item['amenity'] = tags.get('name', f"Unnamed {category}")
        atype = tags.get('amenity', tags.get('shop', tags.get('office', 'other')))
        item['amenity_type'] = atype
        
        # Center coordinate for ways/rels, lat/lon for nodes
        if 'center' in el:
            item['lat'] = el['center']['lat']
            item['lon'] = el['center']['lon']
        elif 'lat' in el:
            item['lat'] = el['lat']
            item['lon'] = el['lon']
        else:
            continue
            
        amenities_data.append(item)
        seen_ids.add(el['id'])
            
    return amenities_data

def run_download(category=None, filename_template=None):
    categories = [category] if category else list(AMENITY_CONFIG.keys())
    
    for cat in categories:
        data_json = get_amenities_data(cat)
        amenities_list = transform_json_to_list(data_json, cat)
        
        out_file = filename_template.format(cat=cat) if filename_template else f"./{cat}.csv"
        df = pd.DataFrame(amenities_list, columns=['id', 'lat', 'lon', 'amenity_type', 'amenity'])
        df.to_csv(out_file, index=False)
        print(f"Saved {len(amenities_list)} records for {cat} to {out_file}")
        print("Cooling down for 15 seconds between categories...")
        time.sleep(15)

if __name__ == "__main__":
    fire.Fire(run_download)
