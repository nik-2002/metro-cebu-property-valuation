# Data Workflow — Significant Findings for the Manuscript

> Plain-language record of how the data gathering, cleaning, and feature engineering
> progressed, and the findings worth stating in the manuscript. Written 2026-06-08.
> Companion to `eda_workflow_handoff_2026-06-07.md` and `modeling_decisions.md`.

---

## 1. Data Gathering

- Source: Lamudi online property listings for Metro Cebu (open-market asking prices).
- The original scraper used a normal request-style approach. Lamudi later blocked that
  with a browser/JavaScript challenge, so a Playwright browser scraper was built to behave
  like a real user (sequential, headed, persistent session; manual CAPTCHA wait).
- The new scrape did NOT add thousands of rows. The honest funnel: 665 candidates → 275
  net-new usable rows after price range, 6-LGU scope, residential recode, spatial cap, and
  dedup against the existing table.
- After merging and enriching, the master table `abt_clean.csv` reached **1,849 rows**.

**Panel sentence:** "We scraped open-market listings from Lamudi; when the site added bot
protection, we rebuilt the scraper to behave like a real browser. After cleaning and
deduplication the final dataset is 1,849 open-market residential records."

---

## 2. Data Cleaning — Significant Findings

### Finding A — Inconsistent computation of the target price (most important)
- Early on, the price figure being modeled was computed in different ways across different
  scrape batches. A model trained on an inconsistently-defined target learns noise.
- Fix: we standardized the target to **price per square meter** (`price_per_sqm`),
  computed the same way for every row, and model `log(price_per_sqm)`.
- Why price per sqm and not total price: it puts a small condo unit and a large lot on the
  same comparable scale, and it is the unit valuers actually reason in.

**Panel sentence:** "We standardized the target to price per square meter so every property
is measured on the same basis; this also fixed an earlier inconsistency in how price was
computed across scrape batches."

### Finding B — The same location appearing many times
- Many listings share the exact same coordinates — partly because some were geocoded to a
  barangay centroid, partly because the same property gets relisted.
- Risk: if identical locations sit in both training and testing, the model looks better than
  it really is (it is being "tested" on places it already memorized).
- Fix: hard duplicates dropped; and the model is evaluated with **GroupKFold by location**
  (whole locations held out at once), which is also the honest test for a price *map* that
  predicts at spots with no listing.

**Panel sentence:** "Because some listings share coordinates, we tested the model by holding
out entire locations at a time, so accuracy is measured on places the model has not seen."

### Finding C — Amenity-access gaps (MCRAI zero rates)
- Some accessibility scores are zero in certain areas. We checked whether that means
  "no amenity nearby" (real) or "no data here" (a gap).
- Current zero rates in the final ABT: security ~25.5%, retail density ~14.3%,
  health ~10.7%, recreation ~9.4%; education, grocery, tourism, hospitals near zero.
- Interpretation: the higher zero rates (security, retail) reflect genuinely thinner amenity
  coverage in outer LGUs, not a computation error. They are reported, not hidden.

**Panel sentence:** "We checked the accessibility scores for data gaps; the zeros we see are
concentrated in outer towns and reflect real differences in amenity coverage, which we
report transparently rather than imputing away."

### Other cleaning steps already logged (Decision 26)
- Removed implausible-price rows (e.g., a 14 sqm "house" at PHP 200M).
- Removed commercial lots that slipped through the residential filter.
- Reclassified mislabeled units (penthouses tagged as Single Detached).
- For vacant lots, restricted to realistic residential scope (80–2000 sqm and price at least
  half the BIR zonal floor) — this is what turned the lot model from broken to sensible.

---

## 3. Feature Engineering

- **Target:** `log(price_per_sqm)`; predictions back-transformed to pesos for the app.
- **Location features:** network road distance (not straight-line) to 8 CBD nodes plus
  airport, computed with osmnx; plus distance to trunk and primary roads for transport access.
- **Accessibility:** MCRAI (Metro Cebu Residential Accessibility Index) — per-category
  amenity access scores (education, grocery, health, hospitals, recreation, security,
  tourism, retail density) plus a composite, using category-specific search radii.
- **Spatial context:** `spatial_lag_price` (nearby price level) and BIR zonal values as the
  legal land-value reference.
- **Structural:** area, bedrooms, bathrooms, with imputation flags where listings were
  incomplete (bedrooms ~25% missing, bathrooms ~19% missing — flagged, not dropped).

**Panel sentence:** "Each property carries structural details, real road-network distances to
the city's business centers, and a custom Metro Cebu accessibility index, so the model can
learn how location and amenities move price."

---

## 4. Where We Are vs. Before the First Defense

| | Before first (re)defense | Now |
|---|---|---|
| Model design | One single model for ALL property types | Three separate models: Condo, Houses, Vacant Lot |
| Dataset | ~1,491 rows | 1,849 rows (687 / 674 / 255 in strata) |
| Target | Total price, raw | `log(price per sqm)`, standardized |
| Testing | Random held-out split (location could leak) | GroupKFold by location (honest, map-appropriate) |
| Benchmark | Informal | IAAO ratio-study panel + beats BIR-zonal and city-median |
| Scraper | Request-style (later blocked) | Playwright browser scraper |

- The pivot came from advisor feedback after the first defense: one model on mixed property
  types created variance the data could not resolve. Splitting into three strata is grounded
  in the literature (Droes, Hoesli & Bourassa 2019; Usman et al. 2020).

**Panel sentence:** "Since the first defense we split the single mixed model into three
property-type models, grew and re-cleaned the data, standardized the target to price per
square meter, and adopted a stricter location-based test — so the current results are both
better organized and more honestly measured."
