import urllib.request
import json
import pandas as pd
import time
import os
import urllib.parse

CEBU_BBOX = (10.0, 123.7, 10.6, 124.1) # S, W, N, E
s, w, n, e = CEBU_BBOX

OVERPASS_URL = 'https://overpass-api.de/api/interpreter'

def fetch_category(category, tags):
    print(f'Fetching {category}...')
    all_elements = []
    
    for tag_key, tag_values in tags.items():
        for tag_val in tag_values:
            query = f"""
            [out:json][timeout:180];
            (
              node["{tag_key}"="{tag_val}"]({s},{w},{n},{e});
              way["{tag_key}"="{tag_val}"]({s},{w},{n},{e});
              rel["{tag_key}"="{tag_val}"]({s},{w},{n},{e});
            );
            out center;
            """
            
            try:
                data = urllib.parse.urlencode({'data': query}).encode('utf-8')
                req = urllib.request.Request(OVERPASS_URL, data=data)
                with urllib.request.urlopen(req, timeout=190) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    elements = res_data.get('elements', [])
                    print(f'  {tag_key}={tag_val}: {len(elements)}')
                    all_elements.extend(elements)
            except Exception as ex:
                print(f'  Error {tag_key}={tag_val}: {ex}')
            time.sleep(2)
            
    processed = []
    seen = set()
    for el in all_elements:
        if el['id'] in seen: continue
        seen.add(el['id'])
        
        lat = el.get('lat') or el.get('center', {}).get('lat')
        lon = el.get('lon') or el.get('center', {}).get('lon')
        if not lat: continue
            
        tags = el.get('tags', {})
        processed.append({
            'id': el['id'],
            'lat': lat,
            'lon': lon,
            'amenity_type': tags.get('amenity', tags.get('shop', 'other')),
            'amenity': tags.get('name', f'Unnamed {category}')
        })
        
    df = pd.DataFrame(processed)
    os.makedirs('Data/amenities_v2', exist_ok=True)
    df.to_csv(f'Data/amenities_v2/{category}.csv', index=False)
    print(f'Saved {len(df)} {category}.')

health_tags = {'amenity': ['hospital', 'clinic']}
fetch_category('health', health_tags)
