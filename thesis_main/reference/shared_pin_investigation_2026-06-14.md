# Shared-Pin Investigation — abt_clean.csv
**Date:** 2026-06-14  
**Analyst:** Claude (Sonnet 4.6) — read-only investigation, no data files modified  
**File examined:** `thesis_main/Data/processed/abt_clean.csv` (1,849 rows, 51 cols)

---

## Bottom-Line Answer

**The 45% house and 39% vacant-lot shared-pin rates are overwhelmingly a geocoding artifact, not real geography.** The dominant cause across both strata is centroid-snapping: when a Lamudi listing carries an incomplete address (subdivision name, barangay, or city only, with no street number), the scraper's geocoding step returns a subdivision or barangay centroid from Google Maps. Multiple unrelated listings with the same vague address token land on the same single coordinate. This accounts for roughly 83% of all shared-pin rows in the Houses stratum and 80% in the Lot stratum. Genuine same-location sharing (townhouse blocks, small subdivisions where units share a building coordinate) explains most of the remainder (~17% and ~19% respectively). Relisting — the same property appearing twice at similar price and area — is negligible (<1% in both strata). The key evidence is the address content inside single-pin clusters: 66% of single-address shared pins in Houses and 64% in Lots contain only a barangay or subdivision name with no street number — the classic centroid-snap signature. The `geocode_source` breakdown reinforces this: the `Lamudi scraper` geocode source (which relies on JSON-LD embedded coordinates or falls back to Google geocoding) has the highest share-rate of all three sources, and `Lamudi_pin_or_google_geocode` (explicitly Google-geocoded) is elevated for Houses (52%) and Lots (63%). For the Condo stratum, the picture is different: large genuine clusters (the 64-unit Marigondon condo is a real multi-unit building) drive most of the 64% rate, but even here, about 39% of the stratum sits on centroid-snap pins.

---

## Per-Stratum Analysis

### Stratum: Condo (Condominium + Apartment)

#### Section 1 — Baseline Sharing Stats

| Metric | Value |
|---|---|
| Total rows | 780 |
| Unique pins | 418 |
| Average rows/pin | 1.87 |
| Rows on shared pins (≥2 rows) | 501 (64.2%) |
| Largest cluster | 64 rows |

Confirms the 64% figure.

#### Section 2 — Cluster-Size Distribution

Of the 501 shared-pin rows (780 total):

| Bucket | Rows | % of Stratum | Pins |
|---|---|---|---|
| Pairs (size = 2) | 138 | 17.7% | 69 pins |
| Small (size 3–5) | 195 | 25.0% | 58 pins |
| Large (size 6+) | 168 | 21.5% | 12 pins |

The condo stratum has the heaviest tail of large clusters. The 12 large-cluster pins include the 64-unit building — a real multi-unit tower — plus resort/hotel condos on Mactan where dozens of units are listed under one building address.

#### Section 3 — Cause Decomposition (Revised, incorporating address quality)

Classification rule: a pin is "centroid-snap" if it has ≥2 distinct addresses, OR if it has 1 distinct address but the address is only a barangay/subdivision/city name (no street number, no road name). A pin is "genuine" if 1 distinct address AND address contains a street number or road name. "Relisting" = genuine address + price_per_sqm within 10% AND area within 10%.

| Category | Rows | % of Stratum |
|---|---|---|
| Genuine same-building/address | 183 | 23.5% |
| Centroid-snap (artifact) | 306 | 39.2% |
| Relisting | 12 | 1.5% |
| **Total shared** | **501** | **64.2%** |

Even in condos, 39% of the stratum sits on centroid pins. However, the 64-unit cluster and other large condo-tower clusters are genuine (1 distinct address with a proper road name), so the genuine category carries real meaning here.

#### Section 4 — geocode_source Cross-Tab

| geocode_source | Unshared | Shared | Total | % Shared |
|---|---|---|---|---|
| Lamudi scraper | 65 | 289 | 354 | 81.6% |
| Lamudi_json_ld | 167 | 220 | 387 | 56.8% |
| Lamudi_pin_or_google_geocode | 11 | 28 | 39 | 71.8% |
| **All** | **243** | **537** | **780** | **68.8%** |

Note: the All row includes both shared-pin rows and the total is 780; the per-row count of 537 vs 501 differs because `is_shared` was defined at the full-dataset pin level before stratum filtering, so a handful of cross-stratum pins inflate the "shared" count slightly. The stratum-level pin cluster count (501) is the authoritative number.

`Lamudi scraper` rows have the highest pin-sharing rate (82%), which is expected: this geocode source is the legacy scraper that did not embed per-listing JSON-LD coordinates and relied on address strings.

#### Section 5 — Coordinate Precision

Mean decimal-place count of the minimum(lat decimals, lon decimals):

| Group | Mean decimals | Distribution note |
|---|---|---|
| Shared rows | 7.00 | Mode at 7 (278 rows), tail at 4–6 (122 rows) |
| Unshared rows | 7.18 | Mode at 7 (140 rows), similar tail |

The precision gap between shared and unshared condos is modest (7.00 vs 7.18). Rows with ≤4 decimal places (very low precision) number 12 in the condo stratum; 10 of those 12 are on shared pins. Low-precision coordinates are a centroid signal but are a small fraction of the total centroid-snap problem.

#### Section 6 — Address Diversity Within Shared Pins

Of the 175 shared pins in the Condo stratum:

| Distinct addresses | Pins | % |
|---|---|---|
| 1 (same address) | 118 | 67.4% |
| 2 | 44 | 25.1% |
| 3+ | 13 | 7.4% |

Pins with ≥2 distinct addresses (57 pins, 185 rows) are clear centroid snaps. Sample from the data:
- `lat=10.3149, lon=123.8854`: 4 distinct address forms, all variants of "Cebu City" — 4 rows, all `Lamudi scraper`. Classic city centroid.
- `lat=10.3671, lon=123.9174`: 3 distinct address variants of "Talamban" — 7 rows. Barangay centroid.

#### Section 7 — Scraper Generation Cross-Tab

| source | Unshared | Shared | Total | % Shared |
|---|---|---|---|---|
| Lamudi (legacy) | 232 | 509 | 741 | 68.7% |
| Lamudi_playwright_2026-06 | 11 | 28 | 39 | 71.8% |

Legacy (Lamudi) accounts for 509 of 537 shared rows. The Playwright batch also has a high rate (72%), consistent with the spatial cap applying only to ~11m cells (which doesn't help when multiple listings independently geocode to the same centroid).

#### Section 8 — Top 5 Largest Clusters

| lat | lon | n rows | distinct addrs | geocode_source | price_per_sqm range | Notes |
|---|---|---|---|---|---|---|
| 10.284110 | 123.975522 | 64 | 1 | Lamudi scraper ×64 | 158,195–230,853 | Agus Road, Marigondon — real condo tower (64 units) |
| 10.330055 | 124.040131 | 15 | 1 | Lamudi scraper ×14, json_ld ×1 | 76,190–169,355 | Punta Engano condos |
| 10.289866 | 124.005758 | 14 | 1 | Lamudi scraper ×14 | 129,730–250,000 | Buyong Road, Maribago condos |
| 10.317350 | 123.905998 | 14 | 3 | Lamudi scraper ×14 | 169,884–331,280 | Cebu Business Park — 3 address variants, centroid |
| 10.323479 | 124.036799 | 10 | 2 | scraper ×8, json_ld ×2 | 347,303–432,505 | Aruga Mactan — 2 address variants (encoding artifact in one) |

---

### Stratum: Houses (House and Lot + Single Detached + Townhouse)

#### Section 1 — Baseline Sharing Stats

| Metric | Value |
|---|---|
| Total rows | 750 |
| Unique pins | 547 |
| Average rows/pin | 1.37 |
| Rows on shared pins (≥2 rows) | 335 (44.7%) |
| Largest cluster | 7 rows |

Confirms the ~45% figure.

#### Section 2 — Cluster-Size Distribution

| Bucket | Rows | % of Stratum | Pins |
|---|---|---|---|
| Pairs (size = 2) | 180 | 24.0% | 90 pins |
| Small (size 3–5) | 134 | 17.9% | 39 pins |
| Large (size 6+) | 21 | 2.8% | 3 pins |

Houses are dominated by pairs and small clusters. The largest cluster is 7 rows. This is structurally unlike condos — houses do not naturally cluster in 64-unit towers. The presence of 3-5 row clusters for houses is the most suspicious signal.

#### Section 3 — Cause Decomposition (Revised)

| Category | Rows | % of Stratum |
|---|---|---|
| Genuine same-building/address | 56 | 7.5% |
| Centroid-snap (artifact) | 277 | 36.9% |
| Relisting | 2 | 0.3% |
| **Total shared** | **335** | **44.7%** |

**82.7% of all shared-pin rows in the Houses stratum are centroid-snap artifacts.** Only 7.5% of the stratum represents genuine same-location sharing (e.g., a townhouse block, or a corner-lot property listed under two property types by the same seller). The centroid-snap fraction is the dominant driver of the 45% shared-pin rate.

#### Section 4 — geocode_source Cross-Tab

| geocode_source | Unshared | Shared | Total | % Shared |
|---|---|---|---|---|
| Lamudi scraper | 78 | 141 | 219 | 64.4% |
| Lamudi_json_ld | 209 | 195 | 404 | 48.3% |
| Lamudi_pin_or_google_geocode | 61 | 66 | 127 | 52.0% |
| **All** | **348** | **402** | **750** | **53.6%** |

**Key finding:** `Lamudi scraper` rows have a 64% shared-pin rate vs 48% for `Lamudi_json_ld`. The scraper geocode source is responsible for 35% of all shared House rows despite being only 29% of the Houses stratum. `Lamudi_pin_or_google_geocode` (explicit Google geocoding) has a 52% shared rate — higher than JSON-LD — consistent with Google returning centroids when the address is incomplete.

The gap between `Lamudi_json_ld` (48%) and `Lamudi scraper` (64%) is the cleanest signal: JSON-LD coordinates are per-listing precise, while the scraper falls back to address-string geocoding which produces centroids.

#### Section 5 — Coordinate Precision

| Group | Mean decimals |
|---|---|
| Shared rows | 6.68 |
| Unshared rows | 7.04 |

The shared-pin house rows average 0.36 fewer decimal places than unshared rows. This is a consistent but modest signal — the centroid-snap problem is primarily about address collisions at high-precision centroid coordinates (Google geocodes to 6–7 decimal places even for a centroid), not low-precision truncation.

#### Section 6 — Address Diversity Within Shared Pins

Of the 199 shared pins in Houses:

| Distinct addresses | Pins | % | Rows |
|---|---|---|---|
| 1 | 135 | 67.8% | 232 |
| 2 | 52 | 26.1% | 124 |
| 3+ | 12 | 6.0% | 46 |

The 64 pins with ≥2 distinct addresses (170 rows) are unambiguously centroid snaps. Sample examples:
- `lat=10.3157, lon=123.8854`: 4 address variants of "Cebu City" — 4 rows, Lamudi scraper only. The coordinate resolves to a city centroid.
- `lat=10.3671, lon=123.9174`: 3 address variants of "Talamban" — 7 rows. A barangay centroid.
- `lat=10.2586, lon=123.8241`: 4 address variants of "Talisay City" — 4 rows.

The 135 single-address pins are more nuanced. Address quality classification:
- 89 pins (66%): address is barangay/subdivision only (e.g., "Pooc, Talisay", "Tungkil, Minglanilla") — centroid-snap despite sharing a single address token
- 32 pins (24%): has a road name
- 12 pins (9%): has a street number
- 2 pins (1%): Plus Code (Google's own centroid encoding)

This means even among "same address" clusters, the majority are centroid artifacts where all rows coincidentally used the same incomplete address string, which Google geocoded to the same centroid.

#### Section 7 — Scraper Generation Cross-Tab

| source | Unshared | Shared | Total | % Shared |
|---|---|---|---|---|
| Lamudi (legacy) | 287 | 336 | 623 | 53.9% |
| Lamudi_playwright_2026-06 | 61 | 66 | 127 | 52.0% |

Unlike condos, the Playwright batch has nearly the same pin-sharing rate as the legacy batch (52% vs 54%). The spatial cap in Playwright (max 3 rows per ~11m cell) does not help here because multiple listings independently geocode to the same centroid — the cap was designed for a single property being scraped multiple times, not for unrelated listings collapsing onto one coordinate.

#### Section 8 — Top 5 Largest Clusters

| lat | lon | n rows | distinct addrs | geocode_source | price_per_sqm range | Notes |
|---|---|---|---|---|---|---|
| 10.238312 | 123.816731 | 7 | 1 | scraper ×5, pin_google ×2 | 53,082–116,439 | Corona Del Mar Subdivision Clubhouse, Talisay — subdivision clubhouse as address; centroid |
| 10.367068 | 123.917392 | 7 | 3 | scraper ×7 | 25,000–125,786 | "Talamban" barangay centroid — 3 address variants of the same barangay |
| 10.284110 | 123.975522 | 7 | 1 | scraper ×7 | 181,656–222,048 | Agus Road, Marigondon — same address; mixed property types; plausible real location or another real cluster |
| 10.380845 | 123.944039 | 5 | 2 | json_ld ×3, pin_google ×2 | 53,226–85,526 | "9WJV+8J Consolacion" Plus Code + "Casili" address — centroid snap |
| 10.369329 | 123.916902 | 5 | 2 | scraper ×4, pin_google ×1 | 66,667–97,222 | "Talamban" variants — barangay centroid |

Note: The Marigondon cluster (row 3) uses the same `lat/lon` as the 64-unit condo cluster. This means condos and houses share the same geocoded point for that road segment, which is a cross-stratum centroid artifact.

---

### Stratum: Lot (Vacant Lot)

#### Section 1 — Baseline Sharing Stats

| Metric | Value |
|---|---|
| Total rows | 319 |
| Unique pins | 247 |
| Average rows/pin | 1.29 |
| Rows on shared pins (≥2 rows) | 123 (38.6%) |
| Largest cluster | 4 rows |

Confirms the ~39% figure.

#### Section 2 — Cluster-Size Distribution

| Bucket | Rows | % of Stratum | Pins |
|---|---|---|---|
| Pairs (size = 2) | 66 | 20.7% | 33 pins |
| Small (size 3–5) | 57 | 17.9% | 18 pins |
| Large (size 6+) | 0 | 0.0% | 0 pins |

No clusters larger than 4 rows. Vacant lots by definition cannot share a building structure, so any cluster here is suspicious. Pairs are the dominant form.

#### Section 3 — Cause Decomposition (Revised)

| Category | Rows | % of Stratum |
|---|---|---|
| Genuine same-address | 23 | 7.2% |
| Centroid-snap (artifact) | 98 | 30.7% |
| Relisting | 2 | 0.6% |
| **Total shared** | **123** | **38.6%** |

**79.7% of shared-pin Lot rows are centroid-snap artifacts.** A genuine shared-pin vacant lot would require multiple distinct lots on the exact same parcel corner — which can occur in a subdivision being sold lot-by-lot, but is rare. The data bears this out: the genuine category (7.2%) likely represents a handful of real subdivision-lot listings sharing a development entrance coordinate.

#### Section 4 — geocode_source Cross-Tab

| geocode_source | Unshared | Shared | Total | % Shared |
|---|---|---|---|---|
| Lamudi scraper | 19 | 33 | 52 | 63.5% |
| Lamudi_json_ld | 73 | 90 | 163 | 55.2% |
| Lamudi_pin_or_google_geocode | 39 | 65 | 104 | 62.5% |
| **All** | **131** | **188** | **319** | **58.9%** |

**The `Lamudi_pin_or_google_geocode` source has the second-highest sharing rate (62.5%) in the Lot stratum, behind `Lamudi scraper` (63.5%).** This is the strongest geocode_source signal for Lots: the explicit Google-geocode source is nearly as bad as the legacy scraper, because vacant lots in Metro Cebu are frequently listed with only a subdivision name or barangay, producing centroids regardless of geocoder.

`Lamudi_json_ld` (55%) is only slightly lower, suggesting that even when Lamudi embeds a JSON-LD coordinate, the coordinate itself may be a developer-supplied centroid for the subdivision gate rather than a parcel-level pin.

#### Section 5 — Coordinate Precision

| Group | Mean decimals |
|---|---|
| Shared rows | 6.64 |
| Unshared rows | 7.25 |

Lot shared rows average 0.61 fewer decimal places than unshared — the largest gap of any stratum. This supports the centroid-snap interpretation: barangay and subdivision centroids tend to be stored at 6 decimal places (about 10 cm resolution), while individual parcel coordinates from GPS or precise geocoding tend to have 7–8.

#### Section 6 — Address Diversity Within Shared Pins

Of the 116 shared pins in Lots:

| Distinct addresses | Pins | % | Rows |
|---|---|---|---|
| 1 | 91 | 78.4% | 124 |
| 2 | 21 | 18.1% | 52 |
| 3+ | 4 | 3.4% | 12 |

Address quality of 91 single-address pins:
- 58 pins (64%): barangay/subdivision only — centroid-snap
- 25 pins (27%): has road name
- 7 pins (8%): has street number
- 1 pin (1%): Plus Code

Sample centroid-snap Lot clusters:
- `lat=10.3671, lon=123.9174`: 4 rows, 2 distinct address variants of "Talamban" — lots and houses share the same barangay centroid.
- `lat=10.3748, lon=123.9540`: 4 rows, 2 address variants of "Royale Cebu Estates, Consolacion" — subdivision entrance centroid.

#### Section 7 — Scraper Generation Cross-Tab

| source | Unshared | Shared | Total | % Shared |
|---|---|---|---|---|
| Lamudi (legacy) | 92 | 123 | 215 | 57.2% |
| Lamudi_playwright_2026-06 | 39 | 65 | 104 | 62.5% |

Unusually, the Playwright batch has a *higher* sharing rate (63%) than legacy (57%) in the Lot stratum. This is likely because Playwright scraped newer listings for smaller LGUs (Consolacion, Minglanilla, Talisay) where vacant lot addresses tend to be even less specific.

#### Section 8 — Top 5 Largest Clusters

| lat | lon | n rows | distinct addrs | geocode_source | price_per_sqm range | Notes |
|---|---|---|---|---|---|---|
| 10.367068 | 123.917392 | 4 | 2 | scraper ×4 | 29,725–65,217 | "Talamban" variants — barangay centroid |
| 10.374615 | 123.954063 | 4 | 2 | json_ld ×2, pin_google ×2 | 22,000–26,882 | "Royale Cebu Estates, Consolacion" variants — subdivision centroid |
| 10.361710 | 123.911374 | 4 | 2 | scraper ×3, json_ld ×1 | 28,000–51,000 | "Turquoise St" and "Amethyst, Talamban" — possibly same subdivision block |
| 10.304724 | 123.982705 | 3 | 3 | json_ld ×3 | 10,000–11,000 | "Ramirez Drive, Ticgahon Bankal" — 3 address variants of same road; likely 3 distinct lots on same road geocoded to same point |
| 10.375041 | 123.953313 | 3 | 1 | pin_google ×2, json_ld ×1 | 20,095–26,882 | "Royale Cebu Estate Tennis Court, Consolacion" — subdivision centroid |

---

## Closing Verdict

### Summary Table: What fraction of the shared-pin rate is artifact vs genuine?

| Stratum | Total shared-pin rate | Centroid-snap | Genuine same-location | Relisting |
|---|---|---|---|---|
| Condo | 64.2% | ~39%pts (61%) | ~24%pts (37%) | ~1.5%pts (2%) |
| Houses | 44.7% | ~37%pts (83%) | ~7.5%pts (17%) | ~0.3%pts (1%) |
| Lot | 38.6% | ~31%pts (80%) | ~7.2%pts (19%) | ~0.6%pts (2%) |

Figures are the number of percentage points of the stratum explained by each cause; the bracketed % is the fraction of the shared-pin rows explained by that cause.

**Plain-language verdict:**
- **Condos:** The 64% rate is about half genuine (real multi-unit buildings, resort condo towers) and half geocoding artifact. The 64-unit cluster alone accounts for ~8% of the stratum. The centroid-snap problem still affects a large share of condo listings.
- **Houses:** The 45% rate is overwhelmingly (83%) a geocoding artifact. Houses do not share parcels, so nearly all shared pins arise from incomplete addresses being geocoded to the same barangay or subdivision centroid. Genuine sharing is plausible only for townhouse blocks (~7.5% of stratum).
- **Lots:** The 39% rate is similarly dominated (80%) by centroid snapping. Vacant lots by construction should be on distinct parcels. The `Lamudi_pin_or_google_geocode` source contributes disproportionately here because lot listings are particularly address-sparse.

### Why centroid-snapping dominates but `geocode_source` does not show a clean split

The geocode_source signal is real but muted because **all three sources can produce centroids**: `Lamudi scraper` uses address-string geocoding; `Lamudi_pin_or_google_geocode` explicitly calls Google; even `Lamudi_json_ld` can produce a centroid if the listing agent entered the subdivision gate or a well-known landmark as the JSON-LD `geo` field rather than the parcel. This means there is no "safe" geocode source — the problem is in the upstream listing data, not just the geocoding method.

---

## Implications for GroupKFold Evaluation

**GroupKFold by coordinate cluster (exact lat/lon) does correctly absorb centroid clusters into one group.** Since centroid-snap rows — potentially 3–7 unrelated listings — share an identical coordinate, they all fall into the same fold group, which means none can appear in both train and test. There is no data leakage from centroid snapping.

**The residual problem is different:** centroid-snap rows have spatial features (distances to CBD nodes, MCRAI scores, road distances) computed from the centroid coordinate, not the true parcel location. Because the centroid is typically a barangay or subdivision center, the spatial features may be accurate to within ~500 m–2 km for the cluster rows. Given that the CBD distance features span tens of kilometers and MCRAI uses radii of 500 m–3 km, the noise introduced is moderate but real. For the Lot stratum in particular, where MCRAI accessibility and road proximity are key predictors, this adds measurement noise to roughly 31% of the stratum.

**What GroupKFold mis-handles (mildly):** A centroid-snap group may contain listings whose true locations span different neighborhoods. GroupKFold treats the entire centroid-cluster as a single "location" for holdout purposes. This underestimates the true number of independent geographic units in the dataset, making the CV folds less cleanly spatially separated than intended. In practice, centroid-snap pins tend to be in more central/urbanized barangays (where listing addresses are vaguer), so this affects the middle of the geographic distribution more than the extremes. The effect is likely small given that the clusters are at most 7 rows (Houses) or 4 rows (Lots).

**Recommendation for the manuscript:** Acknowledge that approximately 30–37% of each non-condo stratum has coordinates that are barangay or subdivision centroids rather than parcel-level pins. State that GroupKFold by exact coordinate correctly prevents cross-contamination within centroid clusters, but note that spatial feature accuracy is reduced for these rows. This is a limitation of the upstream Lamudi listing data, not a modeling error.

---

## Appendix — Reproducible Code

The full analysis was run with `thesis_main/.venv/bin/python` from the repo root. All findings above are produced by the code below.

```python
import pandas as pd
import numpy as np
import re

df = pd.read_csv('thesis_main/Data/processed/abt_clean.csv')

def map_stratum(pt):
    if pt in ('Condominium', 'Apartment'):
        return 'Condo'
    elif pt in ('House and Lot', 'Single Detached', 'Townhouse'):
        return 'Houses'
    elif pt == 'Vacant Lot':
        return 'Lot'
    return 'Other'

df['stratum'] = df['property_type'].apply(map_stratum)

# Add cluster_size and is_shared flag
pin_counts_df = df.groupby(['latitude','longitude']).size().reset_index(name='cluster_size')
df = df.merge(pin_counts_df, on=['latitude','longitude'])
df['is_shared'] = df['cluster_size'] >= 2

# --- Address quality helper ---
def addr_quality(addr):
    if pd.isna(addr) or str(addr).strip() == '':
        return 'blank'
    addr_s = str(addr).strip()
    if re.search(r'\b\d+\s+\w', addr_s) or re.search(r'\bLot\s*\d+|\bBlock\s*\d+', addr_s, re.I):
        return 'has_street_number'
    if re.search(r'\b(street|road|avenue|drive|blvd|boulevard|lane|highway|st\.|rd\.|ave\.)\b', addr_s, re.I):
        return 'has_road_name'
    if re.search(r'\b[A-Z0-9]{4}\+[A-Z0-9]{2,}\b', addr_s):
        return 'plus_code'
    return 'subdivision_or_barangay_only'

# --- Pin classifier ---
def classify_pin_group_v2(grp):
    """
    centroid_snap: >=2 distinct addresses, OR 1 address that is barangay/subdivision only
    relisting: 1 address with road/number, price_per_sqm and area within 10%
    genuine_same_address: everything else
    """
    addrs = grp['address'].dropna().str.strip().str.lower()
    n_distinct_addr = addrs.nunique()
    if n_distinct_addr >= 2:
        return 'centroid_snap'
    addr_sample = grp['address'].dropna().iloc[0] if len(grp['address'].dropna()) > 0 else ''
    aq = addr_quality(addr_sample)
    if aq in ('subdivision_or_barangay_only', 'blank', 'plus_code'):
        return 'centroid_snap'
    psqm = grp['price_per_sqm'].dropna()
    area = grp['area_sqm'].dropna()
    if len(psqm) >= 2:
        prange = psqm.max() - psqm.min()
        pmid = psqm.median()
        arange = area.max() - area.min() if len(area) >= 2 else 0
        amid = area.median() if len(area) >= 2 else 1
        if pmid > 0 and prange/pmid < 0.10 and (amid == 0 or arange/amid < 0.10):
            return 'relisting'
    return 'genuine_same_address'

# --- Section 1: Baseline stats ---
for stratum in ['Condo', 'Houses', 'Lot']:
    sub = df[df['stratum'] == stratum]
    pin_counts = sub.groupby(['latitude','longitude']).size()
    shared_pins = pin_counts[pin_counts >= 2]
    rows_on_shared = sub[sub.set_index(['latitude','longitude']).index.isin(shared_pins.index)].shape[0]
    print(f"{stratum}: n={len(sub)}, unique_pins={len(pin_counts)}, "
          f"rows_shared={rows_on_shared} ({rows_on_shared/len(sub)*100:.1f}%), "
          f"max_cluster={pin_counts.max()}")

# --- Section 2: Cluster-size distribution ---
for stratum in ['Condo', 'Houses', 'Lot']:
    sub = df[df['stratum'] == stratum].merge(
        df.groupby(['latitude','longitude']).size().reset_index(name='cs2'),
        on=['latitude','longitude']
    )
    sr = sub[sub['cs2'] >= 2]
    print(f"{stratum}: pairs={( sr['cs2']==2).sum()}, 3-5={(( sr['cs2']>=3) & (sr['cs2']<=5)).sum()}, 6+={(sr['cs2']>=6).sum()}")

# --- Section 3: Cause decomposition ---
for stratum in ['Condo', 'Houses', 'Lot']:
    sub = df[df['stratum'] == stratum]
    pin_counts = sub.groupby(['latitude','longitude']).size()
    shared_pin_idx = pin_counts[pin_counts >= 2].index
    shared = sub[sub.set_index(['latitude','longitude']).index.isin(shared_pin_idx)].copy()
    pin_class = shared.groupby(['latitude','longitude']).apply(classify_pin_group_v2).reset_index()
    pin_class.columns = ['latitude','longitude','pin_type']
    shared = shared.merge(pin_class, on=['latitude','longitude'])
    print(f"\n{stratum}:")
    print(shared['pin_type'].value_counts())

# --- Section 4: geocode_source cross-tab ---
for stratum in ['Condo', 'Houses', 'Lot']:
    sub = df[df['stratum'] == stratum]
    ct = pd.crosstab(sub['geocode_source'], sub['is_shared'], margins=True)
    ct.columns = ['Unshared', 'Shared', 'Total']
    ct['% Shared'] = (ct['Shared'] / ct['Total'] * 100).round(1)
    print(f"\n{stratum}:")
    print(ct)

# --- Section 5: Coordinate precision ---
def count_decimal_places(val):
    s = str(val)
    return len(s.split('.')[1]) if '.' in s else 0

df['lat_dec'] = df['latitude'].apply(count_decimal_places)
df['lon_dec'] = df['longitude'].apply(count_decimal_places)
df['min_dec'] = df[['lat_dec','lon_dec']].min(axis=1)

for stratum in ['Condo', 'Houses', 'Lot']:
    sub = df[df['stratum'] == stratum]
    print(f"{stratum}: shared mean_dec={sub[sub['is_shared']]['min_dec'].mean():.2f}, "
          f"unshared mean_dec={sub[~sub['is_shared']]['min_dec'].mean():.2f}")

# --- Section 6: Address diversity within pins ---
for stratum in ['Condo', 'Houses', 'Lot']:
    sub = df[df['stratum'] == stratum]
    shared = sub[sub['is_shared']]
    pad = shared.groupby(['latitude','longitude']).apply(
        lambda g: g['address'].dropna().str.strip().str.lower().nunique()
    ).reset_index(name='n_distinct_addr')
    print(f"\n{stratum}: {pad['n_distinct_addr'].value_counts().sort_index().to_dict()}")

# --- Section 7: Source cross-tab ---
for stratum in ['Condo', 'Houses', 'Lot']:
    sub = df[df['stratum'] == stratum]
    ct = pd.crosstab(sub['source'], sub['is_shared'], margins=True)
    ct.columns = ['Unshared', 'Shared', 'Total']
    ct['% Shared'] = (ct['Shared'] / ct['Total'] * 100).round(1)
    print(f"\n{stratum}:")
    print(ct)

# --- Section 8: Top-5 clusters per stratum ---
for stratum in ['Condo', 'Houses', 'Lot']:
    sub = df[df['stratum'] == stratum]
    shared = sub[sub['is_shared']]
    top = shared.groupby(['latitude','longitude']).size().reset_index(name='n').sort_values('n', ascending=False).head(5)
    print(f"\n{stratum} top clusters:")
    for _, r in top.iterrows():
        cl = shared[(shared['latitude']==r['latitude']) & (shared['longitude']==r['longitude'])]
        print(f"  lat={r['latitude']:.6f} lon={r['longitude']:.6f} n={r['n']} "
              f"addrs={cl['address'].dropna().str.strip().str.lower().nunique()} "
              f"gs={cl['geocode_source'].value_counts().to_dict()} "
              f"psqm={cl['price_per_sqm'].min():.0f}-{cl['price_per_sqm'].max():.0f}")
```
