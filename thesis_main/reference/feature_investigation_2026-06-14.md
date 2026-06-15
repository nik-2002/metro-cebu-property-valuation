# Feature Investigation — post-expansion (2026-06-14, Decision 47h)

> Leak-free OOF residual analysis on the expanded ABT (`Scripts/investigate_features_2026-06.py`).
> Feeds the manuscript Limitations section. Final deployed model: Condo 19.8 / Houses 22.5 /
> Lot 38.0 MdAPE (abt_clean 3,617, OnePropertee dropped).

## 1. OnePropertee was contamination → dropped
OOF model-vs-actual ratio (>1 = over-predicts): OP **lots 3.34× (MdAPE 234%)**, OP condos 1.43×
(43%). Cause: OP lots are per-sqm-priced text the parser mis-handled + city-centroid geocoding.
Only 36 rows survived the spatial cap; all contamination. Dropped in the clean step. Removing
them lifted **Condo 20.7→19.8** (now beats the validated 20.1) and trimmed **Lot COD 59.3→56.2**.

## 2. FilipinoHomes price effect (real source heterogeneity — LIMITATION)
The model **over-predicts FilipinoHomes houses by ~14%** (OOF ratio 1.135; FH house MdAPE 26.2%
vs Lamudi 21.8%). FH lists genuinely cheaper stock (affordable / RFO / pre-selling units) that
the structural + location features don't fully explain. A `source` dummy barely helps
(lot −1.0pp, houses +0.3pp) and is unavailable when valuing a new property, so it is NOT a
feature. **Disclose:** combining listing portals introduces source-level price heterogeneity;
FilipinoHomes skews ~14–26% cheaper than Lamudi at comparable features.

## 3. The vacant-lot data ceiling (quantified — LIMITATION)
Worst-decile-error lots (APE ≥ 124%, n=86) vs the rest:

| feature | high-error lots | rest | 
|---|---|---|
| median price_per_sqm | **11,085** | 35,000 |
| area_sqm | 220 | 271 |
| dist_cebu_business_park_m | 10,099 | 9,893 |
| bir_zonal_rr_median | 9,105 | 10,000 |

Same location, area, and BIR — but priced **⅓** as much, and the model over-predicts **100%** of
them. Their cheapness is driven by **unobserved parcel attributes** — frontage, road access,
zoning, title status, slope, flood exposure, irregular shape — none of which are in the listing
data. 65% are FilipinoHomes (FH surfaces more atypical cheap lots than Lamudi did). EDA
corroborates: lot price CV 0.88 < Lamudi-only 1.02, so the difficulty is spatial/attribute, not
price-dispersion. **Defense:** Vacant Lot is the weakest stratum because land value depends on
parcel-specific attributes absent from portal listings — a data ceiling, not a modeling failure.
The honest out-of-sample lot error on a broad, representative sample is ~38% (the prior 25.6% was
a small, geographically concentrated, optimistic sample — `experiment_lot_precise.py`, Decision 47f).

## 4. Distressed-listing filtering (honest status)
Dropped mortgage-assumption (pasalo) listings by title keyword (`assum*|pasalo|foreclos|
repossess|bank-owned|take-over|distress`). FH's distressed inventory is assumption-type, not bank
foreclosures (no ROPA keyword survivors). **Caveat:** the FH API `status` field was not captured,
so a distressed listing that doesn't name itself in the title could still slip through — a
residual data-quality limitation, not fully closable by keyword filtering.

## 5. Feature ablations (`experiment_no_cbd.py`, `experiment_ablation_blocks.py`)
**Drop the 8 CBD-node distances** (re-tuned RF, leak-free GroupKFold):

| Stratum | with-CBD | no-CBD | Δ |
|---|---|---|---|
| Condo | 19.8 | 19.9 | +0.1 (no change) |
| Houses | 22.5 | 22.6 | +0.1 (no change) |
| Vacant Lot | 38.0 | 41.5 | **+3.5** |

**Finding:** CBD distances are **redundant for condos/houses** (the proximity signal is already
carried by MCRAI + BIR + spatial-lag + city dummies — consistent with their VIF ~10-12 and the
MCRAI block VIF 30+ for condos), but **essential for vacant lots** (bid-rent; lots lack structural
substitutes). NOT a deployment change — CBD distances don't hurt condos/houses and help lots.
Sharpens RQ3: geospatial-feature contribution differs by property type via feature *redundancy*,
not location irrelevance.

### Leave-one-block-out (`experiment_ablation_blocks.py`, parallel; Δ MdAPE vs full)
| Block dropped | Condo | Houses | Lot |
|---|---|---|---|
| STRUCT (area/beds/baths) | +1.3 | **+2.4** | +0.1 |
| CBD distances | +0.3 | +0.3 | **+3.8** |
| MCRAI | +0.1 | **−0.4** | +1.7 |
| BIR zonal | +0.1 | +0.8 | +1.4 |
| spatial_lag | +0.7 | +0.5 | +1.0 |
| ROAD | +0.3 | +0.1 | −0.4 |
| bir_zonal_rr_log (dup) | +0.1 | +0.3 | +0.1 |
| mcrai_composite (dup) | −0.1 | +0.1 | +0.1 |

**Each stratum is priced by different economics:**
- **Condos** = structure + neighbourhood (STRUCT +1.3, LAG +0.7); CBD/MCRAI/BIR redundant (raw
  location double-encoded by MCRAI/spatial-lag/city — VIF 30+ for MCRAI).
- **Houses** = structure + land anchor (STRUCT +2.4, BIR +0.8); **MCRAI is noise (−0.4)**.
- **Lots** = pure location / bid-rent (CBD +3.8, MCRAI +1.7, BIR +1.4); STRUCT irrelevant (+0.1).

**Confirmed safe to drop (~0 cost, EDA-flagged redundancy):** `bir_zonal_rr_log` (=log of rr_median),
`mcrai_composite` (blend of components), ROAD distances. **Per-stratum:** MCRAI removable for houses.
Only the >1pp hits (STRUCT cond/house, CBD/MCRAI/BIR for lots) are firmly real; ±0.1-0.4 = noise.
Output `Models/stratified/ablation_blocks.csv`.

### Simplified feature set re-tuned (`experiment_simplified_features.py`)
Drop global redundant (`bir_zonal_rr_log`, `mcrai_composite`, both ROAD) everywhere; drop the whole
MCRAI block for HOUSES; keep full set for LOTS. RF grid re-tuned, leak-free GroupKFold:

| Stratum | features full→lean | FULL | LEAN | Δ |
|---|---|---|---|---|
| Condo | 33→29 | 19.8 | 19.7 | −0.1 |
| **Houses** | **36→24** | 22.5 | **22.0** | **−0.5 (better)** |
| Vacant Lot | 29→25 | 38.0 | 38.5 | +0.5 |

**Verdict:** Houses simplified by a THIRD with improved accuracy (MCRAI block was noise); Condo same
at 4 fewer features; **Lots keep the full set** (marginally worse without it — they use all location
signal). Defensible per-stratum feature selection grounded in VIF + leave-one-out. Deployment of the
leaner per-stratum sets is an option (requires a per-stratum DROP list in the harness); the win is
mainly Houses 22.5→22.0 + parsimony/defensibility, not a large accuracy gain.

## 6. DEPLOYED — per-stratum feature selection + ID 1523 cleanup (Decision 47i)
Final EDA-grounded trim (OLS sig + Cook's + VIF + MCRAI corr 0.57-0.96 + zero-rates):
- **Dropped condo ID 1523** (Cook's 6.08; 186 sqm "Apartment" at ₱23,656/sqm = misclassified house).
- **All strata:** drop `bir_zonal_rr_log`, `bir_zonal_cr_median`, both ROAD distances.
- **Condo + Houses:** MCRAI 9→1 (composite only). **Lot:** keep individual MCRAI.

| Stratum | feat | MdAPE | (was) |
|---|---|---|---|
| Condo | 33→21 | **19.3** | 19.8 (better) |
| Houses | 36→24 | 22.7 | 22.5 (parity) |
| Vacant Lot | 29→25 | 38.2 | 38.0 (parity) |

Cleaner, simpler, defensible model — no accuracy lost, condo improved. Implemented in
`finalize_stratified_groupcv.py STRATUM_DROP`.

## Open / future work
- Re-scrape FH capturing the `status`/`ats_status` field → status-based distressed filter.
- Source-harmonization (e.g., per-source calibration) if pooling more portals later.
- Parcel-attribute enrichment for lots (zoning maps, flood/slope rasters) to lift the ceiling.
- k-NN spatial-lag neighbour definition (arXiv 1902.00562) if 500 m leaves lots too sparse.
