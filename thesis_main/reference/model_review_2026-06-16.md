# Model Review Notes — 2026-06-16 (for the manuscript write-up)

Findings from reviewing the deployed stratified Random Forest models (Decision 50/52).
These are notes to fold into the Chapter on results/interpretation later — NOT yet written into prose.

## Clarification: lot stratum has no structural features except lot size
The vacant-lot model uses **only `area_sqm` (lot size)** as a non-location feature — there are
**no bedrooms/bathrooms** in the lot data (`abt_lot.csv` has no such columns; nothing was imputed).
When describing SHAP/importance for lots, call this "lot size," not "structural features."

## Flag 1 — Houses gain almost nothing from the engineered geospatial features
- The features we built ourselves (CBD distances, MCRAI amenity access, neighbour-price) barely
  improve **house** predictions. Adding them changes the typical house error from ~22.3% to ~23.0% —
  essentially no gain (slightly worse on the median metric).
- For houses, the **city name + the BIR zonal value already capture most of the location signal**;
  the custom geospatial features mostly duplicate what those two already say.
- Manuscript implication: do **not** overclaim the value of engineered geospatial features for houses.
  The geospatial story is strong for condos and especially lots, but for houses it is marginal — say so
  honestly. (Matches Decision 50 decomposition: houses geospatial contribution ≈ −0.66 pp.)

## Flag 2 — The price surface is least reliable in thin LGU×property-type cells
- Where a city has very few listings of a type, the model is systematically off:
  Minglanilla condos (n=9) over-predict ~+20%, Talisay condos (n=16) ~+15%, Mandaue lots (n=106) ~−15%.
- These small samples can't pin down a local price level, so predictions there carry more bias.
- Manuscript implication: state as a limitation — the predicted surface is most trustworthy in
  data-rich cells (e.g. Cebu City condos/houses) and should be read with caution in thin cells.

## Supporting evidence: the worst errors are atypically CHEAP properties the model over-predicts
- In every stratum the worst ~10% of errors are properties priced far below their location's norm,
  and the model predicts the location-implied (higher) price. Concrete worst cases:
  - Condo: 31 sqm Cebu City listed ₱16k/sqm, model ₱180k/sqm (likely data error / mislabeled / raw unit).
  - House: 118 sqm Minglanilla listed ₱8.5k/sqm, model ₱74k/sqm.
  - Lot: 1,455 sqm Cebu City listed ₱3k/sqm, model ₱36k/sqm (likely far-flung / no access / steep).
- These reflect things the listings don't tell us: condition, title issues, distressed sale, parcel
  shape/access. This is the **data-ceiling limitation** (Decision 47h) and is worst for bare lots.
- It also explains the PRD > 1 (the model over-values cheap properties, under-values expensive ones)
  and the gap between the typical error (good) and the average error (inflated by these few bad misses).
- Possible follow-up: check whether a few of the cheapest condos (e.g. ₱16k/sqm in Cebu City) are data
  errors that should have been filtered in cleaning.

## Flag 3 (NEW, strong) — The model cannot see terrain/elevation within a city
- The clearest cause of the worst **lot** misses: cheap highland/mountain barangays inside Cebu City.
  The 3 most extreme lots were all real, not errors — "land in Sirao" (mountain flower-garden area,
  ₱3k/sqm), "Lot in Babag" (upland barangay, ₱3.3k/sqm), "Lot near Tabor Hill/Talamban" (hilly, ₱7k/sqm).
- The model only knows "Cebu City + distance to the business districts," so it applies city-wide land
  values to mountain parcels and over-predicts them heavily. Sirao land at ₱3k/sqm vs a city-norm of
  ₱50k/sqm is a real 6%-of-norm bargain explained entirely by elevation/terrain, which is not a feature.
- Manuscript implication: state plainly as a limitation — **intra-city terrain (mountain vs flat,
  elevation, slope, road access) is not captured.** This, not data error, drives the largest lot
  errors. Honest and defensible. A future feature could be elevation/slope from a DEM, but it is out of
  current scope. Keep these listings; they are genuine market observations.

## Flag 4 — A few listings carry the wrong city (geocoding error)
- Concrete example among the worst house misses: "Grand Terrace Heights, **Casili Consolacion**" was
  tagged as **Cebu City** and compared to Cebu City prices. The address clearly places it in
  Consolacion. This is a location-assignment error, not a price error.
- Connects to the existing shared-pin / centroid-snap geocoding finding (Decision 46b). Worth a
  targeted re-check of rows whose address text names a different LGU than the assigned `city`.

## Distressed/partial-price condos slip past the keyword filter
- The cheapest condos are mostly NOT errors of measurement but listing-quality issues the filter misses:
  "Rush Sale" wording (urgent/forced sale — the distressed filter only catches assum/pasalo/foreclos),
  and small round totals (~₱500k–600k) that look like pre-selling down-payments or reservation amounts
  mislabeled as the full unit price (e.g. two near-identical 36 sqm Lapu-Lapu condos at exactly ₱600k).
- Action taken / TODO: targeted removal/correction of the confirmed bad condos rather than bulk deletion
  (bulk-dropping cheap, hard cases to improve error metrics is indefensible at panel). See widened
  "rush sale" search results below.

### Widened condo scan (2026-06-16, all 1,300 condos)
- "Rush/distress" wording in the listing NAME: only **17** condos (Cebu City 14, Mandaue 2, Talisay 1,
  Lapu-Lapu 0). Undercount — listing descriptions were NOT retained in the ABT, so keyword detection of
  distress is unreliable. (Data limitation worth stating: distressed-listing detection rests on short
  titles only.)
- Total price ≤ ₱1.0M: **27** condos (Mandaue 11, Cebu City 9, Lapu-Lapu 6, Talisay 1) — a ₱1M "condo"
  in Mandaue/Mactan is almost never a full unit price.
- **Key finding:** of the **35** condos priced under 25% of their city norm, **24 (≈two-thirds) have a
  total ≤ ₱1M but only 1 says "rush."** The dominant contamination is NOT distress wording — it is
  **pre-selling down-payments / reservation fees scraped as the full unit price**, concentrated in the
  new-development LGUs (Mandaue, Lapu-Lapu, Cebu City). This is a **measurement error in the target
  (price)**, which is a defensible reason to drop/correct those specific rows — distinct from the
  highland lots, which are genuinely cheap and must be kept.
- Scale: 35 / 1,300 ≈ 2.7% of condos — a thin tail, targeted cleanup not a redo.
- The 24 low-total suspects are listed in full (name, address, city, area, price, % of city norm) in:
  **`reference/condo_partial_price_suspects_2026-06-16.csv`**. Most are named real pre-selling projects
  (MIVELA Garden Residences, Grand Residences, One Astra Place, Northwoods Place), 22–37 sqm studios/1BR
  at round ₱500k–950k totals — consistent with DP/reservation prices, not full unit prices.

### DECISION: Option A — document only, models stay frozen (2026-06-16)
- We are **NOT** dropping these rows or retraining. The deployed condo model and the app price surface
  stay frozen; the gain from removing ~1.8% of condos is small (median error barely moves; only the
  average error tightens) and we are close to defense.
- **Manuscript rewrite MUST cover this** as a stated data limitation: condo cheap-tail is contaminated
  by pre-selling down-payments scraped as full prices; distressed-listing detection is weak because
  listing descriptions were not retained in the ABT (only short titles). Cite the 24-row evidence file
  `reference/condo_partial_price_suspects_2026-06-16.csv`. Logged as Decision 53.
