# Project Handoff: Metro Cebu Residential Valuation Thesis
**Author:** Chris Dominic Estreba (UA&P, BSDS)
**As of:** 2026-06-07
**Status note:** This snapshot was refreshed after the EDA workflow audit. For detailed modeling standing, read `eda_workflow_handoff_2026-06-07.md` and `modeling_decisions.md` Decisions 42-43.

---

## What This Thesis Is

A data-driven residential property valuation workflow for Metro Cebu, Philippines. The core deliverable is a **Streamlit web app** showing a predicted open-market residential price surface across Metro Cebu — not individual property lookup, but a spatial price approximation layer. Secondary deliverable: QGIS map layers for valuation practice use.

**Study area:** 6 LGUs — Cebu City, Mandaue City, Lapu-Lapu City, Talisay City, Minglanilla, Consolacion.

**Target variable:** `price_per_sqm`. The model predicts this. `valuation_gap = price_per_sqm − bir_zonal_rr_median` is a diagnostic output, not a feature.

---

## Data Sources and Market Segments

The current modeling ABT is open-market only after the latest Lamudi/Playwright merge and cleanup:

- `open_market` (1,849 rows in `abt_clean.csv`) — Lamudi-derived asking-price listings after residential scope, geocoding, deduplication, and enrichment.
- `bank_ropa` and `floor_price` are historical/reference data tiers only. They are not used by the current deployed model because they represent different value bases.

At **prediction time**, `market_segment` is fixed to `open_market`. The deployed price surface estimates open-market residential levels only.

---

## ABT Current State

- **File:** `thesis_main/Data/processed/abt_clean.csv`
- **Shape:** 1,849 rows × 51 columns
- **Status:** Current enriched open-market master table. It is not the authoritative training target table; `prepare_stratified_abt.py` writes the current stratum CSVs and recomputes `log_price = log(price_per_sqm)`.
- **Current stratum CSVs:** `abt_condo.csv` (687 rows), `abt_houses.csv` (674 rows), `abt_lot.csv` (255 rows after residential-lot scope filter).

### What's in the ABT

- Structural fields: `area_sqm`, `floor_area_sqm`, `lot_area_sqm`, `bedrooms`, `bathrooms`, `property_type`, `market_segment`, imputation flags
- Location: lat/lon, city, barangay, `is_mactan_island` (all Lapu-Lapu City rows)
- CBD/subcenter distances (10 nodes, osmnx network distance): CBP, Mandaue, Mactan, SRP, Talisay Tabunok, Consolacion, Naga City, Airport
- BIR zonal benchmarks: `bir_zonal_rr_median`, `valuation_gap`
- Spatial lag: `spatial_lag_price` recomputed over the current open-market pool.
- Current MCRAI model features: `mcrai_education`, `mcrai_grocery`, `mcrai_health`, `mcrai_hospitals`, `mcrai_recreation`, `mcrai_security`, `mcrai_tourism`, `mcrai_retail_density`, plus `mcrai_composite`.
- Road accessibility: `dist_to_trunk_road_m` and `dist_to_primary_road_m`.

---

## Key Design Decisions (All Implemented)

| # | Decision | Outcome |
|---|---|---|
| 1 | Area variable | `area_sqm` = floor_area first, lot_area fallback; `is_vacant_lot` flag |
| 2 | bedrooms/bathrooms nulls | 0 for vacant lots; grouped median for others; imputation flags |
| 3 | floor_area_sqm nulls | Grouped median imputation; `floor_area_imputed` flag |
| 4 | price_type → market_segment | open_market / bank_ropa / floor_price |
| 5 | CBD nodes | 8 nodes kept; IT Park, Minglanilla Poblacion, Minglanilla Lipata dropped. Grounded in JICA Mega Cebu Roadmap 2050 + Giuliano & Small (1991) |
| 6 | amenity_score_* columns | All 7 dropped — redundant with MCRAI Hansen scores |
| 7 | Spatial distances | osmnx Dijkstra (Haversine fallback) — standard for all CBD and MCRAI computations |
| 8 | RPPI | Excluded — cross-sectional ABT has no per-row dates; RPPI would be a constant |
| 9 | MCRAI | Custom framework replacing OHANA. Current deployed features exclude finance and represent transport through road-distance features. |
| 42 | Current deployment | Stratified Random Forest per stratum, target `log(price_per_sqm)`, evaluated with GroupKFold by coordinate cluster. |
| 43 | EDA handoff | Heteroscedasticity and collinearity are handled as OLS diagnostic issues; rerun EDA on current 687/674/255 stratum rows before final thesis use. |

---

## MCRAI — What It Is

The **Metro Cebu Residential Accessibility Index (MCRAI)** is a custom Hansen gravity-based accessibility scoring model built specifically for this thesis. It replaces Project OHANA (designed for nationwide equity mapping — a different objective).

- **Current model features:** education, grocery, health, hospitals, recreation, security, tourism, retail_density, plus `mcrai_composite`
- **POI source:** Google Maps Places API (except transport)
- **Transport layer:** road-distance features to trunk and primary roads, not a current MCRAI category
- **Radii:** category-specific (micro 400–800m, meso 1–3km, macro 5km+)
- **Decay:** β = 2.0 (documented baseline for congested developing cities; empirical calibration is future work)
- **Current warning:** Do not revive historical finance/transport MCRAI features or old composite-weight claims without a new logged decision.

---

## Modeling Pipeline (Current State)

Current sequence status:
1. Playwright scrape defeated Lamudi's browser/JavaScript protection and produced 665 candidates.
2. Filtering, geocoding, residential recode, spatial cap, and ABT deduplication produced 275 net staged rows.
3. Canonical enrichment recomputed CBD distances, road distances, MCRAI, and spatial lag.
4. `prepare_stratified_abt.py` writes the current stratum CSVs and recomputes `log_price = log(price_per_sqm)`.
5. `finalize_stratified_groupcv.py` deploys Random Forest models for Condo, Houses, and Vacant Lot.
6. Evaluation uses GroupKFold(5), groups = coordinate cluster.
7. Headline metrics are MdAPE and PE20; COD and PRD are IAAO-context diagnostics. Do not claim IAAO compliance.

Current model metrics:

| Stratum | Rows | MdAPE | PE20 | COD | PRD |
|---|---:|---:|---:|---:|---:|
| Condominium | 687 | 20.1% | 49.8% | 36.3 | 1.21 |
| Houses | 674 | 22.1% | 45.0% | 33.0 | 1.18 |
| Vacant Lot | 255 | 25.6% | 41.6% | 36.9 | 1.28 |

EDA caveat: the saved structured EDA log is stale because it used 654/558/204 rows. Rerun EDA before using plots or diagnostics as final thesis evidence.

---

## Manuscript State

- **Chapter 1** — complete, post-panel revisions done
- **Chapter 2** — drafted; literature verification (Zotero) still pending for ~15 papers
- **Chapter 3** — drafted; several official feedback items still open (sample data tables, per-source preprocessing details, MCRAI scoring methodology section, dashboard mockups)
- **LaTeX sync** — deferred until chapters are finalized in Markdown
- **Full thesis draft** — exists as `thesis_main/Manuscript/Full_Thesis_Draft.md`

---

## Collaboration Model

- **Nico** is the author. Claude handles research design judgment, defensibility review, methodology decisions, and literature synthesis. **GitHub Copilot** implements code.
- Every modeling decision is logged to `thesis_main/reference/modeling_decisions.md`.
- Task tracker: `thesis_main/Manuscript/task.md`
- Do not apply OHANA to this thesis. Do not use "Hansen scores" when referring to MCRAI outputs — they are MCRAI scores.
