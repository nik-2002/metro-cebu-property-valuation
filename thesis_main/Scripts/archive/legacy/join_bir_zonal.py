"""
join_bir_zonal.py
-----------------
Adds BIR zonal values to analytics_base_table.csv.

Steps:
1. Parse BIR zonal value Excel files for RDO 81, 82, 83
2. Load already-extracted RDO 80 data
3. Build consolidated barangay-level summary
4. Reverse-geocode lat/lon → barangay via Google Maps API (with caching)
5. Join BIR summary to ABT on (city, barangay)
6. Overwrite ABT with new columns added

New columns added to ABT:
  barangay_geocoded    — raw barangay name from Google Maps
  bir_zonal_rr_median  — median RR zonal value (PHP/sqm) for barangay
  bir_zonal_cr_median  — median CR zonal value (PHP/sqm) for barangay
  bir_zonal_rc_median  — median RC zonal value (PHP/sqm) for barangay
  bir_zonal_rr_log     — log(1 + bir_zonal_rr_median)
"""

import os
import re
import time
import json
import unicodedata
import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv

# ============================================================================
# CONFIGURATION
# ============================================================================

WORKSPACE_ROOT = os.getcwd()
ABT_PATH = os.path.join(WORKSPACE_ROOT, 'thesis_main/Data/processed/analytics_base_table.csv')
GEOCODE_CACHE_PATH = os.path.join(WORKSPACE_ROOT, 'thesis_main/Data/processed/geocode_barangay_cache.json')
BIR_SUMMARY_PATH = os.path.join(WORKSPACE_ROOT, 'thesis_main/Data/BIR Zonal Values/bir_barangay_summary.csv')

BIR_RDO_FILES = {
    80: {
        'path': os.path.join(WORKSPACE_ROOT, 'thesis_main/Data/BIR Zonal Values/extracted_v2/RDO_No__80___Mandaue_City__Cebu_extracted.csv'),
        'type': 'extracted',
    },
    81: {
        'path': os.path.join(WORKSPACE_ROOT, 'thesis_main/Data/BIR Zonal Values/RDO No. 81 - Cebu City North.xlsx'),
        'sheet': 'Sheet 6 (DO 054-2023)',
        'type': 'hierarchical',
    },
    82: {
        'path': os.path.join(WORKSPACE_ROOT, 'thesis_main/Data/BIR Zonal Values/RDO No. 82 - Cebu City, South.xls'),
        'sheet': 'Sheet 6 (DO 86-2023)',
        'type': 'hierarchical',
    },
    83: {
        'path': os.path.join(WORKSPACE_ROOT, 'thesis_main/Data/BIR Zonal Values/RDO No. 83 -Talisay City, CebuWeb.xls'),
        'sheet': 'Sheet 8(060-22)',
        'type': 'hierarchical',
    },
}

GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
GEOCODE_SLEEP_SEC = 0.15
GEOCODE_BATCH_SIZE = 10

# ============================================================================
# UTILITIES
# ============================================================================

def norm(s):
    """Normalize a string for city/barangay matching."""
    if pd.isna(s) or not str(s).strip():
        return ''
    s = str(s).upper().strip()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r'[^\w\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def slug(s):
    """Slug for barangay matching: strip all non-alphanumeric chars.
    Handles phonetic hyphens (TUNGHA-AN->TUNGHAAN) and
    separator hyphens (LAWAAN-II->LAWAANII == 'Lawaan II'->LAWAANII).
    """
    return re.sub(r'[^A-Z0-9]', '', norm(s))


def _strip_parens(s):
    """Remove parenthetical qualifiers from a geocoded barangay name.
    e.g. 'Tejero (Villa Gonzalo)' -> 'Tejero'
    """
    return re.sub(r'\s*\([^)]*\)', '', str(s)).strip()


# BIR-side renames applied before slug computation.
_BIR_BARANGAY_RENAMES = {
    'BABAG I & II': 'BABAG',   # Lapu-Lapu: combined entry in the RDO sheet
}


def _normalize_bir_barangay(name):
    """Normalize a BIR barangay name: strip parentheticals, apply known renames."""
    name = re.sub(r'\s*\([^)]*\)', '', str(name)).strip()
    return _BIR_BARANGAY_RENAMES.get(name.upper().strip(), name)


# Aliases: (city_norm, geocoded_slug) -> canonical BIR barangay slug
BARANGAY_ALIASES = {
    ('CEBU CITY',    'CAMPUTHAW'):       'KAMPUTHAW',
    ('CEBU CITY',    'HIPPODROMO'):      'HIPODROMO',
    ('CEBU CITY',    'ADLAON'):          'ADLAWON',
    ('CEBU CITY',    'SANTACRUZ'):       'STACRUZ',
    ('CEBU CITY',    'PARDO'):           'POBLACIONPARDO',
    ('CEBU CITY',    'QUIOT'):           'QUIOTPARDO',
    ('CEBU CITY',    'PASIL'):           'PASILABUNO',
    ('CEBU CITY',    'LOREGA'):          'LOREGASANMIGUEL',
    ('CEBU CITY',    'TEJERO'):          'TEJERO',   # safety-net after _strip_parens
    ('TALISAY CITY', 'CADULAWAN'):       'CANDULAWAN',
    ('CONSOLACION',  'TAYUD'):           'TAYOD',
    ('MINGLANILLA',  'POBLACIONWARDIV'): 'POBLACION',  # Ward IV is part of the combined BIR entry
}

# City overrides: when geocoder assigns the wrong city relative to BIR coverage.
# (city_norm, barangay_slug) -> (lookup_city_norm, lookup_barangay_slug)
JOIN_CITY_OVERRIDES = {
    ('CONSOLACION', 'YATI'):           ('LILOAN',         'YATI'),
    ('CONSOLACION', 'JAGOBIAO'):       ('MANDAUE CITY',   'JAGOBIAO'),
    ('CEBU CITY',   'CANTAOAN'):       ('NAGA CITY',      'CANTAOAN'),
    ('CEBU CITY',   'PUNTAENGANO'):    ('LAPU LAPU CITY', 'PUNTAENGANO'),
    ('CEBU CITY',   'IBABAOESTANCIA'): ('MANDAUE CITY',   'IBABAO'),
    ('CEBU CITY',   'TIPOLO'):         ('MANDAUE CITY',   'TIPOLO'),
    ('CEBU CITY',   'SUBANGDAKU'):     ('MANDAUE CITY',   'SUBANGDAKU'),
    ('MANDAUE CITY','SACSAC'):         ('CONSOLACION',    'SACSAC'),
    ('MANDAUE CITY','BACAYAN'):        ('CEBU CITY',      'BACAYAN'),
}

# ABT city corrections: properties whose scraper-assigned city is wrong.
# (barangay_geocoded_lower, wrong_city) -> correct_city
ABT_CITY_CORRECTIONS = {
    ('tungkil', 'Talisay City'): 'Minglanilla',
}


def normalize_city(city):
    """Normalize city names, collapsing CEBU CITY districts."""
    city_norm = norm(city)
    if 'CEBU CITY' in city_norm:
        return 'CEBU CITY'
    return city_norm


def _clean_captured(val):
    """Strip trailing DO No./effectivity junk from a captured block value."""
    if not val:
        return val
    # Remove anything from 'D.O.', 'EFFECTIVITY DATE', or 'EFFECTIVE DATE' onward
    val = re.split(
        r'\s+(?:D\.?\s*O\.?\s*(?:No\.?|NO\.?)|EFFECTIVITY\s+DATE|EFFECTIVE\s+DATE)',
        val, flags=re.IGNORECASE
    )[0]
    return val.strip()



    """
    Extract value for a label from a row.
    Tries col[0] as combined "LABEL : VALUE", then falls back to col[2], col[1], col[3].
    """
    # Try col[0] first as combined "LABEL : VALUE"
    if len(row) > 0 and pd.notna(row.iloc[0]):
        m = re.search(label_pattern + r'\s*[:/]\s*(.*)', str(row.iloc[0]), re.IGNORECASE)
        if m and m.group(1).strip():
            return m.group(1).strip()
    
    # Try col[2], col[1], col[3] as separate value cells
    for col_idx in [2, 1, 3]:
        if col_idx < len(row) and pd.notna(row.iloc[col_idx]):
            val = str(row.iloc[col_idx]).strip()
            if val and val not in [':', 'nan']:
                return val
    return None


# ============================================================================
# PARSE BIR EXCEL FILES
# ============================================================================

def parse_bir_hierarchical(filepath, sheet_name, rdo_num):
    """
    Parse hierarchical BIR zonal data (RDO 81, 82, 83).
    
    Returns DataFrame with columns:
      [Province, City, Barangay, Classification, Zonal_Value, Source]
    """
    print(f"  Parsing {filepath} (sheet '{sheet_name}')...")
    df_raw = pd.read_excel(filepath, sheet_name=sheet_name, header=None)
    print(f"    Raw shape: {df_raw.shape}")
    
    data = []
    current_province = None
    current_city = None
    current_barangay = None
    data_section = False
    
    for idx, row in df_raw.iterrows():
        row_str = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
        # Full row as single string — needed for RDO 81 where label is in col[0]
        # and value is in col[1]/col[2] separately
        row_all = ' '.join(str(v) for v in row.values if pd.notna(v))
        row_all_upper = row_all.upper()

        # Detect PROVINCE row
        if re.search(r'\bPROVINCE\s*[:/]', row_all_upper):
            m = re.search(r'\bPROVINCE\s*[:/]\s*(.+)', row_all_upper)
            current_province = _clean_captured(m.group(1)) if m else extract_label_value(row, r'PROVINCE')
            data_section = False
            continue

        # Detect CITY/MUNICIPALITY row (handles both "CITY/MUNICIPALITY" and just "MUNICIPALITY")
        if re.search(r'(?:CITY[/\s]?)?MUNICIPALITY\s*[:/]', row_all_upper):
            m = re.search(r'(?:CITY[/\s]?)?MUNICIPALITY\s*[:/]\s*(.+)', row_all_upper)
            current_city = _clean_captured(m.group(1)) if m else extract_label_value(row, r'CITY')
            data_section = False
            continue

        # Detect BARANGAY row (also "ZONE/BARANGAY", "ZONE/ BARANGAY")
        if re.search(r'(?:ZONE\s*/?\s*)?BARANGAY\s*[:/]', row_all_upper):
            m = re.search(r'(?:ZONE\s*/?\s*)?BARANGAY\s*[:/]\s*(.+)', row_all_upper)
            v = _clean_captured(m.group(1)) if m else extract_label_value(row, r'(?:ZONE\s*/?\s*)?BARANGAY')
            if v:
                current_barangay = v
            data_section = False
            continue

        # Detect header row — "CLASSIFICATION" may appear in any column
        if 'CLASSIFICATION' in row_all_upper and current_barangay:
            data_section = True
            continue
        
        # Parse data rows
        if data_section and current_province and current_city and current_barangay:
            # Check if last column is numeric (zonal value)
            try:
                if pd.notna(row.iloc[-1]):
                    zonal_value = float(row.iloc[-1])
                    if zonal_value > 0:
                        # Extract classification and vicinity
                        classification = None
                        vicinity = None
                        
                        if len(row) >= 2 and pd.notna(row.iloc[-2]):
                            classification = str(row.iloc[-2]).strip()
                        if len(row) >= 3 and pd.notna(row.iloc[-3]):
                            vicinity = str(row.iloc[-3]).strip()
                        
                        if classification and classification.strip():
                            data.append({
                                'Province': current_province,
                                'City': current_city,
                                'Barangay': current_barangay,
                                'Classification': classification,
                                'Zonal_Value': zonal_value,
                                'Source': f'RDO {rdo_num}',
                            })
            except (ValueError, TypeError):
                pass
    
    result = pd.DataFrame(data)
    print(f"    Parsed {len(result)} data rows")
    return result


def parse_bir_extracted(filepath):
    """Load already-extracted BIR CSV (RDO 80)."""
    print(f"  Loading {filepath}...")
    df = pd.read_csv(filepath)
    # Assume it has Province, City, Barangay, Classification, Zonal_Value columns
    if 'Source' not in df.columns:
        df['Source'] = 'RDO 80'
    print(f"    Loaded {len(df)} rows")
    return df


def consolidate_bir_data():
    """Load the pre-extracted BIR CSV and build barangay-level summary."""
    print("\n[STEP 1] Load BIR Zonal Value Data")
    print("=" * 70)

    extracted_path = os.path.join(
        WORKSPACE_ROOT,
        'thesis_main/Data/BIR Zonal Values/bir_zonal_extracted_all.csv'
    )
    if not os.path.exists(extracted_path):
        raise FileNotFoundError(
            f"Extracted BIR CSV not found: {extracted_path}\n"
            "Run: python3 thesis_main/Scripts/extract_bir_v2.py"
        )

    bir_data = pd.read_csv(extracted_path)
    print(f"  Loaded {len(bir_data)} rows from {extracted_path}")

    # Rename to match downstream expectations
    bir_data = bir_data.rename(columns={
        'city_municipality': 'City',
        'barangay':          'Barangay',
        'classification':    'Classification',
        'zonal_value':       'Zonal_Value',
    })

    # Filter to valid numeric zonal values
    bir_data = bir_data[
        pd.notna(bir_data['Zonal_Value']) &
        (bir_data['Zonal_Value'] > 0) &
        pd.notna(bir_data['Classification']) &
        (bir_data['Classification'].str.strip() != '')
    ]
    print(f"  After filtering: {len(bir_data)} valid rows")

    # Normalize city names
    bir_data['City'] = bir_data['City'].apply(normalize_city)

    # Aggregate by barangay and classification type
    print("\nAggregating by city/barangay...")
    bir_data['city_norm']     = bir_data['City'].apply(norm)
    bir_data['Barangay']      = bir_data['Barangay'].apply(_normalize_bir_barangay)
    bir_data['barangay_slug'] = bir_data['Barangay'].apply(slug)

    summary_rows = []
    for (city_norm, barangay_slug), group in bir_data.groupby(['city_norm', 'barangay_slug']):
        city     = group['City'].iloc[0]
        barangay = group['Barangay'].iloc[0]

        rr_data = group[group['Classification'].str.startswith('RR', na=False)]['Zonal_Value']
        cr_data = group[group['Classification'].str.startswith('CR', na=False)]['Zonal_Value']
        rc_data = group[group['Classification'].str.startswith('RC', na=False)]['Zonal_Value']

        summary_rows.append({
            'city':                  city,
            'barangay':              barangay,
            'city_norm':             city_norm,
            'barangay_norm':         barangay_slug,
            'barangay_slug':         barangay_slug,
            'bir_zonal_rr_median':   rr_data.median() if len(rr_data) > 0 else np.nan,
            'bir_zonal_cr_median':   cr_data.median() if len(cr_data) > 0 else np.nan,
            'bir_zonal_rc_median':   rc_data.median() if len(rc_data) > 0 else np.nan,
        })

    bir_summary = pd.DataFrame(summary_rows)
    print(f"Summary: {len(bir_summary)} unique (city, barangay) combinations")

    bir_summary.to_csv(BIR_SUMMARY_PATH, index=False)
    print(f"Saved BIR summary to {BIR_SUMMARY_PATH}")

    return bir_summary


# ============================================================================
# REVERSE GEOCODING
# ============================================================================

def load_geocode_cache():
    """Load cached barangay geocoding results."""
    if os.path.exists(GEOCODE_CACHE_PATH):
        with open(GEOCODE_CACHE_PATH, 'r') as f:
            return json.load(f)
    return {}


def save_geocode_cache(cache):
    """Save geocoding cache."""
    os.makedirs(os.path.dirname(GEOCODE_CACHE_PATH), exist_ok=True)
    with open(GEOCODE_CACHE_PATH, 'w') as f:
        json.dump(cache, f, indent=2)


def get_barangay_from_geocode(lat, lng, api_key, cache):
    """
    Get barangay from lat/lon via Google Maps Reverse Geocoding API.
    Returns barangay name or empty string if not found.
    Uses cache to avoid repeated API calls.
    """
    cache_key = f"{lat:.6f},{lng:.6f}"
    
    if cache_key in cache:
        return cache[cache_key]
    
    try:
        params = {
            'latlng': f'{lat},{lng}',
            'key': api_key,
            'result_type': 'sublocality',
        }
        response = requests.get(GOOGLE_MAPS_API_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] != 'OK':
            cache[cache_key] = ''
            return ''
        
        # Look for sublocality_level_1, then sublocality, then neighborhood
        for result in data.get('results', []):
            for component in result.get('address_components', []):
                types = component.get('types', [])
                if any(t in types for t in ['sublocality_level_1', 'sublocality', 'neighborhood']):
                    barangay = component.get('long_name', '')
                    cache[cache_key] = barangay
                    return barangay
        
        cache[cache_key] = ''
        return ''
    except Exception as e:
        print(f"    Error geocoding ({lat}, {lng}): {e}")
        cache[cache_key] = ''
        return ''


def reverse_geocode_abt(abt, api_key):
    """Add barangay_geocoded column via reverse geocoding."""
    print("\n[STEP 2] Reverse Geocode Properties to Barangay")
    print("=" * 70)
    
    # Load cache
    cache = load_geocode_cache()
    initial_cache_size = len(cache)
    
    # Get unique lat/lon pairs
    abt['lat_lng'] = abt.apply(lambda r: (r['latitude'], r['longitude']), axis=1)
    unique_coords = abt['lat_lng'].unique()
    print(f"Total unique (lat, lng) pairs: {len(unique_coords)}")
    
    cached_count = sum(1 for lat, lng in unique_coords if f"{lat:.6f},{lng:.6f}" in cache)
    print(f"Already cached: {cached_count}")
    
    # Geocode new coordinates
    to_geocode = [c for c in unique_coords if f"{c[0]:.6f},{c[1]:.6f}" not in cache]
    print(f"Need to geocode: {len(to_geocode)}")
    
    if len(to_geocode) > 0 and not api_key:
        print("WARNING: No GOOGLE_MAPS_API_KEY found. Skipping geocoding.")
        print("Barangay_geocoded will be empty for uncached coordinates.")
    
    for i, (lat, lng) in enumerate(to_geocode):
        if api_key:
            get_barangay_from_geocode(lat, lng, api_key, cache)
            if (i + 1) % GEOCODE_BATCH_SIZE == 0:
                print(f"  Geocoded {i + 1}/{len(to_geocode)} unique coordinates")
                save_geocode_cache(cache)
            time.sleep(GEOCODE_SLEEP_SEC)
    
    # Save cache at end
    if len(to_geocode) > 0:
        save_geocode_cache(cache)
        print(f"  Geocoded {len(to_geocode)}/{len(to_geocode)} unique coordinates")
    
    # Apply barangay lookup to ABT
    abt['barangay_geocoded'] = abt['lat_lng'].apply(
        lambda c: cache.get(f"{c[0]:.6f},{c[1]:.6f}", '')
    )
    abt.drop(columns=['lat_lng'], inplace=True)
    
    print(f"Geocoding complete. Cache size: {len(cache)} (was {initial_cache_size})")
    return abt


# ============================================================================
# JOIN BIR TO ABT
# ============================================================================

def join_bir_to_abt(abt, bir_summary):
    """Join BIR summary to ABT on (city, barangay)."""
    print("\n[STEP 3] Join BIR Summary to ABT")
    print("=" * 70)
    
    # Remove old BIR metric columns if they exist (keep barangay_geocoded — just added)
    old_cols = ['bir_zonal_rr_median', 'bir_zonal_cr_median', 'bir_zonal_rc_median', 'bir_zonal_rr_log']
    for col in old_cols:
        if col in abt.columns:
            abt.drop(columns=[col], inplace=True)
    
    # Apply ABT city corrections (scraper misclassifications)
    for (brgy_lower, wrong_city), correct_city in ABT_CITY_CORRECTIONS.items():
        mask = (abt['barangay_geocoded'].str.lower() == brgy_lower) & (abt['city'] == wrong_city)
        if mask.any():
            abt.loc[mask, 'city'] = correct_city
            print(f"  Corrected city: {wrong_city} -> {correct_city} for {mask.sum()} row(s) (barangay={brgy_lower})")

    # Create normalized join keys
    abt['city_norm'] = abt['city'].apply(normalize_city)
    # Strip parens from geocoded names (e.g. 'Tejero (Villa Gonzalo)' -> 'Tejero')
    abt['barangay_slug'] = abt['barangay_geocoded'].apply(lambda x: slug(_strip_parens(x)))

    # Apply barangay aliases (spelling/naming variants)
    abt['barangay_slug'] = abt.apply(
        lambda r: BARANGAY_ALIASES.get((r['city_norm'], r['barangay_slug']), r['barangay_slug']),
        axis=1
    )

    # Apply city overrides (geocoder city != BIR coverage city)
    def _apply_overrides(row):
        key = (row['city_norm'], row['barangay_slug'])
        if key in JOIN_CITY_OVERRIDES:
            new_city, new_brgy = JOIN_CITY_OVERRIDES[key]
            return new_city, new_brgy
        return row['city_norm'], row['barangay_slug']

    override_results = abt.apply(_apply_overrides, axis=1, result_type='expand')
    abt['city_norm']     = override_results[0]
    abt['barangay_slug'] = override_results[1]

    # Join
    merged = abt.merge(
        bir_summary[['city_norm', 'barangay_slug', 'bir_zonal_rr_median', 'bir_zonal_cr_median', 'bir_zonal_rc_median']],
        on=['city_norm', 'barangay_slug'],
        how='left'
    )
    
    # Nearest-neighbour imputation for still-unmatched rows
    unmatched_mask = merged['bir_zonal_rr_median'].isna()
    if unmatched_mask.any():
        matched = merged[~unmatched_mask].dropna(subset=['latitude', 'longitude'])
        for idx in merged[unmatched_mask].index:
            lat = merged.at[idx, 'latitude']
            lon = merged.at[idx, 'longitude']
            if pd.isna(lat) or pd.isna(lon) or len(matched) == 0:
                continue
            dlat = matched['latitude'] - lat
            dlon = (matched['longitude'] - lon) * np.cos(np.radians(lat))
            nearest_idx = (dlat**2 + dlon**2).idxmin()
            for col in ['bir_zonal_rr_median', 'bir_zonal_cr_median', 'bir_zonal_rc_median']:
                merged.at[idx, col] = matched.at[nearest_idx, col]
        n_imputed = unmatched_mask.sum() - merged['bir_zonal_rr_median'].isna().sum()
        print(f"  Nearest-neighbour imputed: {n_imputed} row(s)")

    # Compute log transform
    merged['bir_zonal_rr_log'] = np.log1p(merged['bir_zonal_rr_median'])
    
    # Drop normalization columns
    merged.drop(columns=['city_norm', 'barangay_slug'], inplace=True)
    
    # Report
    n_with_bir = merged['bir_zonal_rr_median'].notna().sum()
    n_without_bir = merged['bir_zonal_rr_median'].isna().sum()
    
    print(f"Rows with BIR match: {n_with_bir} ({100*n_with_bir/len(merged):.1f}%)")
    print(f"Rows without BIR match: {n_without_bir} ({100*n_without_bir/len(merged):.1f}%)")
    
    # Breakdown by city
    print("\nBreakdown by city:")
    for city, grp in merged.groupby('city'):
        total = len(grp)
        with_bir = grp['bir_zonal_rr_median'].notna().sum()
        pct = 100 * with_bir / total if total > 0 else 0
        print(f"  {city}: {with_bir}/{total} ({pct:.1f}%)")
    
    return merged


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "=" * 70)
    print("JOIN_BIR_ZONAL.PY - Add BIR Zonal Values to ABT")
    print("=" * 70)
    
    # Load environment and API key
    dotenv_path = os.path.join(WORKSPACE_ROOT, 'thesis_main', '.env')
    load_dotenv(dotenv_path)
    api_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
    
    if not api_key:
        print("WARNING: GOOGLE_MAPS_API_KEY not found in .env")
    
    # Step 1: Parse BIR files and consolidate
    bir_summary = consolidate_bir_data()
    
    # Step 2: Load ABT
    print("\n[STEP 2a] Load ABT")
    print("=" * 70)
    abt = pd.read_csv(ABT_PATH)
    print(f"Loaded ABT: {len(abt)} rows, {len(abt.columns)} columns")
    print(f"Columns: {list(abt.columns)}")
    
    # Step 2b: Reverse geocode
    abt = reverse_geocode_abt(abt, api_key)
    
    # Step 3: Join BIR to ABT
    abt = join_bir_to_abt(abt, bir_summary)
    
    # Step 4: Save updated ABT
    print("\n[STEP 4] Save Updated ABT")
    print("=" * 70)
    abt.to_csv(ABT_PATH, index=False)
    print(f"Saved updated ABT to {ABT_PATH}")
    print(f"  Rows: {len(abt)}")
    print(f"  Columns: {len(abt.columns)}")
    
    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
