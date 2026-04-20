# Manuscript Tasks

> Tracking manuscript, ABT readiness, modeling, and supporting outputs.
> Last updated: 2026-04-20

---

## Current Working Status
- [x] Build and enrich the Analytics Base Table (`analytics_base_table.csv`)
- [x] Append bank ROPA sources (BPI, Metrobank, Bank of Commerce, Landbank, China Bank Savings)
- [x] Complete geocoding, CBD distances, amenity scores, spatial lag, and BIR join
- [x] Expand ABT to 1,185 rows × 46 columns across 8 sources
- [x] Apply `clean_abt.py`: filter to 6-LGU scope, drop `dist_cbrt_nearest_m` → `abt_clean.csv` (1,120 rows × 45 cols)
- [x] Standardize property types, flag outliers, drop legacy columns, compute Hansen scores → ABT now 1,110 rows × 50 cols
- [ ] Resolve `price_type` mislabeling (recode to `is_ropa` binary) before freezing ABT
- [ ] Freeze the modeling-ready ABT after cleanup
- [ ] Start EDA on the cleaned ABT

## ABT Readiness Before Modeling

> **Immediate blockers before modeling** (in order):
> 1. `price_type` recode — banks are still mixed into `asking` / `floor` labels and should be normalized before training
> 2. Missingness strategy — `bedrooms`, `bathrooms`, and `lot_area_sqm` have structural nulls that need an explicit treatment
> 3. CBD distance audit — the 10 hub-distance variables should be checked for redundancy before model fitting

- [x] Confirm final modeling geography: 6-LGU scope (Cebu City, Mandaue City, Lapu-Lapu City, Talisay City, Minglanilla, Consolacion)
- [x] Filter rows to the 6-LGU scope — drop all records outside the Metro Cebu study area (`clean_abt.py`: dropped 65 rows from 7 out-of-scope cities)
- [x] Standardize `property_type` into a unified residential taxonomy (`standardize_property_types.py`); 10 non-residential BDO rows dropped → 1,110 rows
- [ ] Resolve `price_type` mix: ABT has ceiling (682), asking (320), floor (118) — decide whether to include `price_type` as a feature or subset to a single price concept before modeling
- [ ] Decide the missing-data strategy for `bedrooms`, `bathrooms`, and `lot_area_sqm` (structural nulls, especially in condo and bank ROPA rows)
- [x] Compute `price_outlier_flag` for bank ROPA rows (`flag_ropa_outliers.py`); used p01/p99 of full ABT; 4 rows flagged (2 BoC, 2 Metrobank); 0 nulls remaining
- [x] Drop legacy null columns (`dist_cbd_m`, `bir_zonal_value`, `valuation_gap`) and regenerate `valuation_gap = price_per_sqm − bir_zonal_rr_median` (`drop_legacy_columns.py`); ABT now 1,110 rows × 43 cols
- [x] Compute Hansen Gravity accessibility scores for 6 amenity categories (`compute_hansen_scores.py`); β=2.0, 5 km radius, Google Maps Places POIs; 7 new columns appended → ABT now 1,110 rows × 50 cols
- [x] Replace terminal-node `transport.csv` (69 rows) with OSM road corridor midpoints via Overpass API (`out center` on highway WAYs); 2,643 unique road segments retained after de-duplication by OSM way ID; re-ran `compute_hansen_scores.py` → `hansen_transport` mean=238.48, `hansen_composite` mean=88.10
  - Note: `transport.csv` `lgu` values now indicate fetch provenance from overlapping LGU bounding boxes, not strict final administrative assignment after de-duplication
- [ ] Audit the 10 CBD distance variables for redundancy or multicollinearity before training
- [x] Decide whether road accessibility will be added before modeling or deferred to a post-baseline enhancement
  - Decision: OSM road corridor midpoints (2,643 ways) implemented via Overpass API; `hansen_transport` column recomputed

## Modeling Roadmap
- [ ] Build the final modeling table from the cleaned ABT
- [ ] Run EDA — price distributions, missingness heatmap, feature correlations, and geographic spread across the 6 LGUs
- [ ] Fit the OLS hedonic baseline (benchmark/comparator only, not the deployed model)
- [ ] Fit the Random Forest model
- [ ] Fit the XGBoost model
- [ ] Tune Random Forest and XGBoost with cross-validation
- [ ] Compare OLS, Random Forest, and XGBoost using MAPE, MAE, RMSE, and R²
- [ ] Generate SHAP outputs for the selected tree model(s)
- [ ] Export Random Forest and XGBoost predictions for map-layer integration

## Map And App Deliverables
- [ ] Finalize the QGIS layer design for predicted price, residuals, and valuation gap
- [ ] Decide whether the map will use both Random Forest and XGBoost outputs or only the best-performing tree model
- [ ] Build the Streamlit app for property-level prediction and SHAP explanation
- [ ] Confirm how the Streamlit app and QGIS outputs will stay consistent on features and model version

## Methodology Decisions Still Open
- [ ] Finalize the treatment of OLS as a baseline comparator rather than a deployed map model
- [ ] Finalize the manuscript wording for the implemented road-accessibility feature
- [ ] Decide whether a stricter road-network distance feature should complement the current corridor-based transport accessibility signal in a later iteration
- [ ] Revisit the CBD / subcenter literature to better justify malls, town centers, and polycentric nodes used in Metro Cebu

## Chapter 1 — The Problem and Its Setting
- [x] Draft initial version
- [x] Add §1.5 Scope and Limitations
- [x] **Post-panel**: Remove NLP research question
- [x] **Post-panel**: Add GIS-focused RQ3 (geospatial features)
- [x] **Post-panel**: Define Metro Cebu (6 LGUs)
- [x] **Official feedback #3**: Define property, Metro Cebu (formalized in Ch1)
- [x] **Post-panel**: Emphasize Philippine-context novelty in §1.4
- [x] **Post-panel**: Frame thesis as predictive + prescriptive (QGIS map)
- [x] **Official feedback #4**: Expand justification for choice of problem (§1.1.3 — Why Metro Cebu, and Why Now?)
- [x] **Official feedback #4**: Expand model selection rationale (new §1.6 — OLS/RF/XGBoost with 'Why Not Other Models?' table)
- [ ] Update scope language if the ABT remains broader than the 6-LGU thesis frame

## Chapter 2 — Review of Related Literature
- [x] Draft initial version (§2.1–§2.8)
- [x] **Post-panel**: Replace §2.5 (NLP) → §2.5 (Geospatial Feature Engineering)
- [x] **Post-panel**: Update §2.8 synthesis with GIS gap statement
- [x] **Post-panel**: Standardize "value drivers" terminology
- [x] **Post-panel**: Separate lit findings from thesis methodology
- [x] **Official feedback #2**: Clearer RRL structure (ensure arguments build logically)
- [x] **Official feedback #11**: Add more RRL sources (GIS+ML in SE Asia, PH-specific OSM)
- [x] **Official feedback #10**: Literature grounding for custom value driver model
- [ ] Strengthen the literature basis for polycentric CBDs, subcenters, malls, and town-center proxies in Cebu
- [ ] Add literature support for road accessibility if that feature is implemented

## Chapter 3 — Research Methodology
- [x] Draft initial version
- [x] **Post-panel**: Remove all NLP references
- [x] **Post-panel**: GIS data sources, target variable, geospatial feature engineering
- [x] **Post-panel**: Diversify floor prices (BDO + Pag-IBIG + other banks)
- [x] **Post-panel**: QGIS Interactive Map as primary deliverable
- [ ] **Official feedback #5**: Add sample data structure tables (raw BDO, raw Lamudi, cleaned schema, final feature matrix)
- [ ] **Official feedback #6**: Acknowledge data processing complexity per source
- [ ] **Official feedback #7**: Add per-source preprocessing details (what needs to be done for each data structure)
- [ ] **Official feedback #8**: Make web map + dashboard description more tangible/concrete (mock screenshots, layer descriptions)
- [ ] **Official feedback #9**: Deeper methodology for adding value drivers (scoring methodology, radius selection, weighting)
- [ ] **Official feedback #10**: Develop custom value driver scoring model (not just standard features)
- [ ] Replace remaining OSM/osmnx amenity references with the implemented Google Maps Places workflow where applicable
- [ ] Add a clear subsection on how the final deployed map will use Random Forest / XGBoost outputs while OLS remains the benchmark model
- [x] Add the road-accessibility feature to methodology only after the implementation decision is settled
  - Implemented: OSM highway ways (`out center`) as transport accessibility nodes; describe in §3.x under Hansen scoring

## Diagrams & Assets
> Existing `.drawio` sources in `Presentations/assets/`. Output to `Manuscript/diagrams/`.

### Ch1 – Problem & Setting
- [ ] **Study Area Map** — QGIS map of Metro Cebu (Cebu City, Mandaue, Lapu-Lapu, Talisay) + CBRT route overlay

### Ch3 – Methodology
- [ ] **Data Landscape** *(revise `Data-Landscape.drawio`)* — Floor (BDO) + Ceiling (Lamudi) → True Market Value. Fix: Lamudi no longer "Future scrape"; typo "Braket" → "Bracket"
- [ ] **Data Pipeline** *(revise `Data-Pipeline.drawio`)* — update to the implemented multi-source flow and current source counts
- [ ] **Empirical Framework** *(revise `Emprerical-Framework.drawio`)* — IVS → Models → Outputs → Validation. Fix: remove outdated NLP/BERT framing if still present
- [ ] **Feature Engineering Summary Table** — LaTeX table: all features, source, type, derivation
- [ ] **Modeling Pipeline Flowchart** — New: cleanup → preprocessing → split → 3 models → evaluation → SHAP → map/app outputs

### Ch4 – Results (plan ahead)
- [ ] **Property Distribution Map** — QGIS choropleth/dot map of sample across barangays
- [ ] **Model Comparison Table** — LaTeX table: MAE / MAPE / RMSE / R² per model
- [ ] **Feature Importance Bar Chart** — Top-N from RF/XGBoost *(matplotlib)*
- [ ] **SHAP Summary Plot** — Beeswarm *(SHAP library)*
- [ ] **Actual vs Predicted Scatter** — Per-model with 45° line *(matplotlib)*
- [ ] **Residual Distribution** — Error histograms per model *(matplotlib)*

## Full Draft
- [x] Rebuild `Full_Thesis_Draft.md` with revised Ch1 + Ch2 + Ch3
- [ ] Final proofread pass for consistency
- [ ] Incorporate all official feedback edits (after implementation)
- [ ] Align the draft with the final ABT scope and the actual deployed-model decision

## Literature Gaps — Pending Zotero Verification
- [ ] **CBD bid-rent theory**: Verify and complete `alonso1964location` in `biblio.bib` (Alonso 1964, *Location and Land Use*)
- [ ] **Monocentric baseline**: Verify and complete `muth1969cities` in `biblio.bib` (Muth 1969, *Cities and Housing*)
- [ ] **Polycentric urbanism**: Verify and complete `giuliano1991subcenters` in `biblio.bib` (Giuliano & Small 1991, *Regional Science and Urban Economics*)
- [ ] **Polycentric distance gradients**: Verify and complete `mcmillen2003employment` in `biblio.bib` (McMillen 2003, *Regional Science and Urban Economics*)
- [ ] **In-text**: Add Alonso (1964) citation in §2.5.2 before the Rosen/Malpezzi sentence — grounds the theoretical basis for distance-to-CBD as a value driver
- [ ] **In-text**: Add polycentric justification in §3 proximity subsection — explain why multiple CBD nodes are used instead of a single monocentric anchor

## LaTeX Sync (Deferred)
- [ ] Sync `chapter1.tex` with revised Ch1
- [ ] Sync `chapter2.tex` with revised Ch2
- [ ] Sync `chapter3.tex` with revised Ch3
- [ ] Update `biblio.bib`

## Verification
- [x] Grep: 0 NLP references remain
- [x] 10/10 initial panel feedback addressed
- [ ] Verify all 12 official feedback items addressed (pending)
- [ ] Verify the ABT cleanup decisions before committing to model training
