import fire
import requests
import time
import pandas as pd

# ---------------------------------------------------------------------------
# Overpass mirrors — same as download_amenities.py
# ---------------------------------------------------------------------------
OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter"
]

# ---------------------------------------------------------------------------
# LGU configuration
# Bounding boxes: (south, west, north, east)
# Road types: reflect actual jeepney/bus penetration per LGU
#   - Cebu City + Mandaue: tertiary included (dense informal routes)
#   - Lapu-Lapu, Talisay, Consolacion: secondary only
#   - Minglanilla: primary/trunk only (highway corridor)
# ---------------------------------------------------------------------------
LGU_CONFIG = {
    'cebu_city': {
        'bbox': (10.28, 123.84, 10.42, 123.93),
        'road_types': ['primary', 'secondary', 'tertiary', 'trunk'],
        'label': 'Cebu City',
    },
    'mandaue_city': {
        'bbox': (10.33, 123.92, 10.40, 123.97),
        'road_types': ['primary', 'secondary', 'tertiary', 'trunk'],
        'label': 'Mandaue City',
    },
    'lapu_lapu_city': {
        'bbox': (10.27, 123.93, 10.35, 124.02),
        'road_types': ['primary', 'secondary', 'trunk'],
        'label': 'Lapu-Lapu City',
    },
    'talisay_city': {
        'bbox': (10.22, 123.83, 10.30, 123.90),
        'road_types': ['primary', 'secondary', 'trunk'],
        'label': 'Talisay City',
    },
    'consolacion': {
        'bbox': (10.37, 123.92, 10.44, 123.98),
        'road_types': ['primary', 'secondary', 'trunk'],
        'label': 'Consolacion',
    },
    'minglanilla': {
        'bbox': (10.17, 123.78, 10.24, 123.87),
        'road_types': ['primary', 'trunk'],
        'label': 'Minglanilla',
    },
}


def query_road_ways(road_type, bbox, mirrors=OVERPASS_MIRRORS):
    """
    Query OSM for road ways of a given type within a bounding box.
    Returns center point of each way segment.
    Using 'out center' avoids pulling all individual OSM nodes
    (which would be tens of thousands and too dense for Hansen scoring).
    """
    s, w, n, e = bbox
    query = f"""
    [out:json][timeout:120];
    (
      way["highway"="{road_type}"]({s},{w},{n},{e});
    );
    out center;
    """

    for url in mirrors:
        try:
            response = requests.get(url, params={'data': query}, timeout=130)
            if response.status_code == 429:
                print(f"    Rate limited by {url}, waiting 15s...")
                time.sleep(15)
                continue
            response.raise_for_status()
            return response.json().get('elements', [])
        except Exception as ex:
            print(f"    Mirror {url} failed: {ex}")
            continue

    print(f"    All mirrors failed for highway={road_type}.")
    return []


def fetch_lgu(lgu_key, config):
    """Fetch all road corridor nodes for one LGU."""
    label = config['label']
    bbox = config['bbox']
    road_types = config['road_types']

    print(f"\n[{label}] Fetching road types: {road_types}")
    print(f"  Bounding box: {bbox}")

    all_rows = []
    seen_ids = set()

    for road_type in road_types:
        print(f"  Querying highway={road_type}...")
        elements = query_road_ways(road_type, bbox)
        print(f"    Found {len(elements)} way segments.")

        for el in elements:
            if el['id'] in seen_ids:
                continue

            # 'out center' returns a 'center' key with lat/lon for ways
            if 'center' in el:
                lat = el['center']['lat']
                lon = el['center']['lon']
            elif 'lat' in el:
                lat = el['lat']
                lon = el['lon']
            else:
                continue

            tags = el.get('tags', {})
            road_name = tags.get('name', tags.get('ref', f"Unnamed {road_type}"))

            all_rows.append({
                'id': el['id'],
                'lat': lat,
                'lon': lon,
                'amenity_type': road_type,       # e.g. 'primary', 'secondary'
                'amenity': road_name,             # road name from OSM tags
                'lgu': label,
            })
            seen_ids.add(el['id'])

        # Brief pause between road type queries
        time.sleep(3)

    print(f"  [{label}] Total road corridor nodes: {len(all_rows)}")
    return all_rows


def run_fetch(output_file='transport_road_corridors.csv'):
    """
    Fetch road corridor nodes for all 6 Metro Cebu LGUs with
    LGU-differentiated road type filters.

    Output CSV columns:
        id, lat, lon, amenity_type, amenity, lgu

    This file replaces transport.csv as input to compute_accessibility_score.py.
    The Hansen gravity score is computed over these road corridor midpoints,
    reflecting the flag-down paratransit nature of jeepney/bus service
    in Metro Cebu (no fixed stops; service runs along named road corridors).

    Usage:
        python fetch_road_corridor_nodes.py
        python fetch_road_corridor_nodes.py --output_file=my_transport.csv
    """
    all_rows = []

    for lgu_key, config in LGU_CONFIG.items():
        lgu_rows = fetch_lgu(lgu_key, config)
        all_rows.extend(lgu_rows)
        # Cooldown between LGUs to avoid hammering Overpass
        print(f"  Cooling down 15s before next LGU...")
        time.sleep(15)

    df = pd.DataFrame(all_rows, columns=['id', 'lat', 'lon', 'amenity_type', 'amenity', 'lgu'])
    df = df.drop_duplicates(subset='id')

    df.to_csv(output_file, index=False)
    print(f"\nDone. Saved {len(df)} road corridor nodes to '{output_file}'.")
    print(f"Breakdown by LGU:\n{df['lgu'].value_counts().to_string()}")
    print(f"Breakdown by road type:\n{df['amenity_type'].value_counts().to_string()}")


if __name__ == "__main__":
    fire.Fire(run_fetch)
