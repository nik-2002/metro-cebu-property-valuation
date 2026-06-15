import pandas as pd, re, unicodedata

def norm(s):
    if pd.isna(s) or not str(s).strip(): return ''
    s = str(s).upper().strip()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r'[^\w\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def slug(s):
    return re.sub(r'[^A-Z0-9]', '', norm(s))

def normalize_city(city):
    city_norm = norm(city)
    if 'CEBU CITY' in city_norm: return 'CEBU CITY'
    return city_norm

abt = pd.read_csv('thesis_main/Data/processed/analytics_base_table.csv')
summary = pd.read_csv('thesis_main/Data/BIR Zonal Values/bir_barangay_summary.csv')

unmatched = abt[abt['bir_zonal_rr_median'].isna()].copy()
unmatched['city_norm'] = unmatched['city'].apply(normalize_city)
unmatched['barangay_slug'] = unmatched['barangay_geocoded'].apply(slug)

print('Unmatched by city and barangay:')
for city, grp in unmatched.groupby('city'):
    brgy_counts = grp['barangay_geocoded'].value_counts()
    print(f'\n  {city} ({len(grp)} rows):')
    for brgy, cnt in brgy_counts.items():
        b_slug = slug(str(brgy))
        city_n = normalize_city(city)
        in_bir = summary[(summary['city_norm'] == city_n) & (summary['barangay_slug'] == b_slug)]
        status = 'IN BIR' if len(in_bir) > 0 else 'NOT IN BIR'
        print(f'    {str(brgy):<35s}  slug={b_slug:<25s}  n={cnt}  [{status}]')
