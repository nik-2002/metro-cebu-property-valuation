# Multi-Source Scraping Expansion — Sprint State (2026-06-14)

> Goal: grow the ABT beyond Lamudi (1,849 rows) to give the stratified Random Forest more
> training data — the binding constraint, esp. Vacant Lot (n=255). Branch: `modeling`.
> Motivation (Decision 46b): more data should shrink the high-MAPE error tail; sample size,
> not the geocoding centroid issue, is judged the bigger limiter right now.

## Source recon — evidence-based verdict on all 9 candidates

| Source | Scrapeable? | Cebu volume | Geocode quality | Status tonight |
|---|---|---|---|---|
| Lamudi | already have | — | pin/address | in ABT (1,579 + 270) |
| **OnePropertee** | ✅ requests | ~1,000 (throttled after) | ⚠️ city-level | **1,039 houses scraped** (raw) |
| Filipino Homes | ⚠️ page-1 only (Next.js hidden API) | ~2,400 | ✅ subdivision (best) | 36 raw; needs Playwright for deep pages |
| **Dot Property** | ✅ requests | **~9,845** | ✅ **barangay-level** | **scraper built + self-tested; RUN NEXT** |
| Cebu Grand Realty | ✅ requests (WordPress) | ~88 | no coords | low yield — skip |
| Cebu Filipino Homes | ⚠️ thin/JS | unknown | unknown | not worth tonight |
| Facebook Marketplace | ❌ login-wall + aggressive anti-bot | high | unstructured | not feasible overnight |
| Developer sites | ❌ bespoke per-site | preselling | varies | new-build biased — skip |
| Local broker sites | ✅ tiny each | small | varies | diminishing returns |

**Takeaway:** ChatGPT's "50k–100k across 9 sources" conflates *exists* with *scrapeable tonight*.
The real wins are **Dot Property (biggest + cleanest geocoding) and OnePropertee (banked)**.

## Scrapers built this session (Scripts/)
- `scrape_onepropertee.py` — **COMPLETE. 3,804 listings** (house 1,039 / condo 1,544 / lot 1,221)
  → `Data/webscraping-onepropertee/op_raw.csv`. Server-rendered, `/page/N` pagination,
  `div.listing` cards. First run rate-limited (HTTP 202) after ~45 fast pages; resumed later with
  gentler pacing (1.4–2.8s) + 202-detection + `--categories`/resume flags — no throttle. Condo
  needed canonical slug `/condo-for-sale-cebu` first (a redirecting slug breaks `/page/N`).
  **Location is city-level only** → geocodes to city centroid (low precision) — weaker than
  DotProperty/FH. **Lots are shown per-sqm** (`price_text` "₱X.Xm ( ₱Y /sqm)"); `price_php` holds
  the TOTAL (verified: total/area ≈ displayed /sqm). ⚠ some lot areas implausible (e.g. 10 sqm) —
  staging must cross-check `price_php/area` vs the explicit `/sqm` in `price_text` and drop divergent rows.
- `scrape_filipinohomes.py` — SUPERSEDED. HTML scraper got only page 1/category (36 rows):
  FilipinoHomes is a Next.js app whose SSR only serves page 1. Kept for reference; use the API
  version below instead.
- `scrape_filipinohomes_api.py` — **COMPLETE. 3,894 listings** (house 1,727 / condo 1,038 /
  lot 1,129) → `Data/webscraping-filipinohomes/fh_api_raw.csv`. **THE HIGHEST-QUALITY SOURCE.**
  Found the backend JSON API by intercepting the browser's network calls:
  `GET api2.filipinohomes.com/api/listings?categories[]=For Sale&type_str=<House|Condominium|Land>
  &address=" Cebu"&page=N`, header `x-guest-token` (from `filipinohomes.com/api/guest-token`,
  ~1h validity, refreshed on 401 + every 60 pages). Hit directly with requests — no browser, ~4 min.
  **Every row has PRECISE embedded coordinates** (geo_coordinates.lat/lng, 7dp rooftop) + STRUCTURED
  city/barangay/province objects + separate floor_area & lot_area + bed/bath + subtype→type taxonomy.
  100% completeness (3894/3894 coords+price+city+floor+lot). **Needs NO geocoding → sidesteps the
  centroid-snap problem (Decision 46b) entirely.** City spread covers all 6 LGUs (+ Naga/Compostela/
  Danao to filter). per_page locked at 12 server-side (329 pages). This is the gold-standard data.
- `scrape_dotproperty.py` — **RAN (full crawl). 3,721 raw listings** →
  `Data/webscraping-dotproperty/dp_raw.csv`. Balanced: **lot 1,249 / condo 1,238 / house 1,234**
  (the Lot haul is ~5× the current Lot stratum of 255 — huge for the weakest model). No throttle;
  all 3 categories ended at a clean 404 page-51 (the site caps pagination at 50 pages × 25 =
  1,250/category, so the "~9,845" search hint is the unpaginated total incl. rentals). 0 internal
  duplicates. **3,469 usable** (price + area > 0); 252 lack area. Location is barangay-level
  ("tisa cebu", "cabancalan cebu") → geocodes well; 3,589/3,721 contain "cebu". Extracts from href
  slug (beds/type/barangay) + card-text regex (price/psqm/baths); area = price ÷ price_per_sqm
  (exact). URL-decodes ñ. **NOT previously scraped** (ABT source col = Lamudi only).
  ⚠ Needs the standard filters before integration: price bounds (raw p99=653M, p01=1 → junk),
  Lot scope (area p99=46,474 sqm = development parcels → cap 80–2000), residential-only,
  6-LGU, spatial-cap, ABT-dedup. Realistic usable net-new ≈ 2,500–3,000 pre-geocode.

## NEXT SESSION — exact steps
1. **Run Dot Property:** `python thesis_main/Scripts/scrape_dotproperty.py --max-pages 80` first
   (tests rate-limit cheaply); if clean, full run (drop `--max-pages`). If HTTP 202 throttle like
   OnePropertee → raise `PACING`, run in passes, or switch `fetch()` to the Playwright harness
   (`thesis_main/playwright/browser.py` `LamudiBrowser`).
2. **(Optional) Playwright pass** for FilipinoHomes deep pages + OnePropertee condo/lot.
3. **Clean + geocode + stage** (Task #2): mirror `Scripts/stage_lamudi_batch.py` but geocode from
   `location_text` FIRST (these sources have no coords). Quality-gate: keep Google
   ROOFTOP/RANGE_INTERPOLATED precise; flag GEOMETRIC_CENTER/APPROXIMATE (city-centroid). Reject
   out-of-Cebu-bounds. Reuse `archive/legacy/join_bir_zonal.py` reverse_geocode + BIR join.
   Apply the 6-LGU + residential + price + spatial-cap(3/cell) + ABT-dedup filters. Note the
   spatial cap will drop most city-centroid OnePropertee rows — expected.
4. **Enrich + merge + retrain** (Task #3): canonical enrichment (CBD/road dist, MCRAI, spatial
   lag) on net-new → append to abt_clean → `prepare_stratified_abt.py` →
   `finalize_stratified_groupcv.py`; report new strata counts + leak-free metrics vs current
   (Condo MdAPE 20.1 / Houses 22.1 / Lot 25.6).

## Google Maps API — status
Key live in `thesis_main/.env` (`GOOGLE_MAPS_API_KEY`), verified working (test geocode OK, not
over quota). Geocoding API ~$5/1k calls, ~10k free/month (verify in Cloud Console → Quotas).
Re-geocoding the whole expanded set sits inside the free tier — budget is not the constraint.

## FINAL OUTCOME — integrated + deployed (Decision 47 + 47h)
Raw 11,419 → clean/geocode/dedup/spatial-cap (89%→62% pin-sharing). **47h dropped OnePropertee**
(contamination) → merged **abt_clean 1,849 → 3,617** (Lamudi 1,579 + FilipinoHomes 1,203 +
DotProperty 565 + Lamudi_pw 270). Strata **Condo 1,301 / Houses 1,223 / Lot 849**. Deployed
(leak-free GroupKFold):

| Stratum | n | MdAPE | (was) | COD | PRD |
|---|---|---|---|---|---|
| Condo | 1,301 | **19.8** | 20.1 | 38.2 | 1.22 |
| Houses | 1,223 | 22.5 | 22.1 | 35.8 | 1.21 |
| Vacant Lot | 849 | 38.0 | 25.6 | 56.2 | 1.49 |

Condo now BEATS the validated baseline. See `feature_investigation_2026-06-14.md` for the OOF
source-effect + lot data-ceiling findings that drove the OnePropertee drop.

- **Condo/Houses: parity at ~2× data.** **Lot 38.7 = honest harder-sample finding**, not a bug
  (experiment refuted the centroid hypothesis: precise-only lots = 40.7, no better; original 255
  Lamudi lots still = 24.3 → the old 25.6 was small-sample optimism). EDA confirms lot price
  CV 0.88 < Lamudi-only 1.02 → difficulty is spatial, not price-dispersion.
- **Contamination filter added:** dropped 299 "For Assume"/distressed (loan-balance prices) + 100
  price-band outliers (mostly FilipinoHomes). FilipinoHomes also runs ~26% cheaper than Lamudi
  even when clean (genuine cheaper stock) — a residual source-heterogeneity limitation.
- **spatial_lag_price fixed:** same-stratum neighbours, radius 1km→500m (arXiv 1902.00562 + MCRAI
  micro-scale). Minor metric effect; for defensibility.
- Refreshed: deployment_manifest, SHAP (10_), EDA plots/tables (01-09), abt_clean.geojson (3,632),
  valuation_gap.geojson, decision log (Decision 47).

## Still open (next-phase feature investigation — user flagged "didn't investigate enough features")
1. Quantify a `source` effect (FilipinoHomes vs Lamudi feature/residual differences).
2. Profile the high-error lots — which missing features (frontage/zoning/slope/flood) drive the
   wide lot IQR [16k-57k].
3. Re-check VIF/correlation on the 2× sample (refreshed 04_/05_ plots ready to read).
4. Consider k-NN spatial-lag neighbour definition if 500m leaves lots too sparse.
