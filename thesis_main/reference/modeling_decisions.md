# Modeling Decisions Log

> Started: 2026-04-20
> Last updated: 2026-06-07
> Purpose: Record modeling, EDA, data, and deployment decisions that control the thesis workflow.
> These decisions should be reflected in Chapter 3 during the final write-up pass.

---

## Decision 18 — Naga City: CBD Node Only, Excluded from Training Scope (2026-05-04)

**Decision:** Naga City remains a CBD node in the distance feature set (`dist_naga_m`) but is excluded from the training data scope. The 4 Naga City rows collected in Phase C Lamudi scrape are dropped before merging into the ABT.

**Why:** Data scarcity is the binding constraint. The Phase C scrape produced only 4 Naga listings (original ABT had 0). Four rows cannot support LGU-level learning — the model would assign Naga prices based almost entirely on coefficients learned from the other 6 LGUs, which would be misleading. Naga City is primarily industrial in character (JICA Mega Cebu Roadmap 2050 industrial anchor designation), and open-market residential listings are sparse by nature.

**Literature basis:** Naga City's role as a sub-regional employment anchor is grounded in the JICA Mega Cebu Roadmap 2050. Its inclusion as a CBD node follows Giuliano & Small (1991) employment subcenter criteria. Exclusion from training scope is a data-driven boundary condition, not a judgment about Naga's urban significance.

**Chapter 3 flag:** State clearly that the spatial scope for model training is 6 LGUs. Naga City appears in the model only as a distance anchor (CBD node 8). Inclusion as a 7th training LGU is deferred pending sufficient listing coverage (target: 150–200 verified open-market listings).

**Phase D note:** Scraping 150–200 Naga City residential listings from Lamudi (or alternative sources) would enable Naga's inclusion in a future model version.

---

## Custom Accessibility Scoring Framework — Research Summary (2026-04-22)

> Source: Gemini Deep Research + NotebookLM 5-question synthesis
> Literature file: `thesis_main/Literature/Polycentric_Urbanism/Polycentric Urbanism_ Metro Cebu POI Analysis.md`
> Advisor direction: Build a Metro Cebu-specific accessibility scoring model rather than applying OHANA directly.

### Why OHANA Cannot Be Applied Directly

Project OHANA was designed for **nationwide equity mapping** (normative economics — where services *should* be for social justice). This thesis requires **revealed preference valuation** (positive economics — what buyers actually pay for). Five documented limitations:

1. **Normative vs. positive objective** — equity mapping ≠ valuation
2. **MAUP problem** — OHANA uses 1km × 1km grids; parcel-level valuation requires property coordinates
3. **Great-circle distance** — ignores road network friction (already fixed via Decision 7)
4. **Assumed equal weights** — violates utility theory; weights must reflect actual market behavior
5. **Fixed decay parameter** — β should be empirically calibrated, not assumed

### Custom Framework Design Principles (literature-grounded)

**Weights — Two-stage hedonic regression (validated):**
- Stage 1: Run OLS hedonic regression with individual unweighted Hansen scores per category
- Stage 2: Normalize statistically significant coefficients → use as composite weights
- This grounds weights in Metro Cebu's own revealed market preferences
- If multicollinearity between categories: use RF/XGBoost feature importance instead
- Placeholder weights used until after first OLS run — do not interpret as final

**Decay parameter β:**
- β=2.0 is within documented range for congested developing cities (1.75–2.0)
- Literature caution: β should be empirically calibrated, not assumed
- β=2.0 retained as a documented baseline; flag empirical calibration as future work
- Category-specific β (e.g., lower for walking amenities) is the ideal but deferred

**Catchment radii — category-specific (three-tier framework):**
- Micro (400m–800m): pedestrian access — convenience stores, pocket parks
- Meso (1km–3km): short vehicle/transit trips — grocery, clinics, finance
- Macro (5km+): regional pull — CBDs, hospitals, universities, transport corridors

**Cebu-specific weight guidance from literature:**
- Agosto (Cebu): transport/mobility ranked #1 driver, livability (open space + facilities) ranked #2
- Bangkok study: transport accessibility = 51.69% of total model weight in congested SE Asian city
- South Tangerang: malls and hospitals showed NO significant effect — danger of assuming all categories matter equally
- Implication: `hansen_transport` should carry highest weight in the final composite

### Transport Category — How It Actually Works

`transport.csv` contains 2,643 lat/lon **point coordinates** — the geographic center (midpoint) of each OSM highway road segment. Not a shapefile.

The Hansen formula treats each road midpoint as a POI. A property near many road segments gets a high `hansen_transport` score. This is a **corridor-based accessibility proxy** — it measures how well-connected a property is to the surrounding road grid.

**Conceptual note:** When computing network distance from a property to a road midpoint, the routing travels *through* the road network to reach *a point on the road network*. This is slightly circular but defensible as a proxy for road corridor accessibility.

**More precise alternatives (future work):**
- Shortest distance to nearest classified road using OSM line geometry
- Distance to nearest PUJ/jeepney route (requires actual route data)
- Road density within a buffer radius

**Chapter 3 framing:** Describe as "a corridor-based transport accessibility proxy using OSM highway way centers, not a direct measure of jeepney operations or ridership."

---

## Decision 1: `lot_area_sqm` — Area Variable Treatment

**Status**: Decided

**Problem**: `lot_area_sqm` has 793/1110 nulls (71%). The nulls are structural, not random — 682 are Lamudi rows, which are predominantly condominiums. Condos do not have lot area by definition. Imputing 71% of a column is not defensible.

**Decision**: Option B — merge into a unified `area_sqm` column with a property-type fallback, plus an `is_vacant_lot` flag.

**Implementation logic**:
- `area_sqm` = `floor_area_sqm` if available, else `lot_area_sqm`
- `is_vacant_lot` = 1 if `property_type == "Vacant Lot"`, else 0
- Rationale: vacant lots (249 rows) are valued primarily on land size, not floor area. Dropping `lot_area_sqm` entirely would make the model blind for that segment.
- `lot_area_sqm` and `floor_area_sqm` are retained as separate columns for reference but `area_sqm` is the modeling feature.

**Chapter 3 note**: §3.5 Pre-processing should document this merge and flag logic explicitly.

---

## Decision 2: `bedrooms` and `bathrooms` Missingness

**Status**: Decided

**Problem**: `bedrooms` has 585/1110 nulls (53%); `bathrooms` has 523/1110 nulls (47%). Nulls split across two causes: (1) bank ROPA rows (BoC: 234, PagIBIG: 96, BPI: 65) structurally omit interior details; (2) some Lamudi rows (161 bedrooms, 106 bathrooms) have blank fields — scraping gaps or studio units. Vacant lots (249 rows) will always be null — bedrooms/bathrooms are meaningless for land-only listings.

**Decision**: Option B — impute with median by `property_type` + `city`, add binary flag columns, set vacant lot rows to 0 explicitly.

**Implementation logic**:
- `bedrooms` and `bathrooms`: impute nulls using median grouped by `property_type` + `city`
- Add `bedrooms_imputed` and `bathrooms_imputed` flag columns (1 = was null, 0 = original value)
- For rows where `property_type == "Vacant Lot"`: set `bedrooms = 0`, `bathrooms = 0`, flags = 0 (these are not imputed — they are correct zero values)

**Chapter 3 note**: §3.5 should describe the two-tier treatment: explicit zero for vacant lots, median imputation with flag for all other nulls.

---

## Decision 3: `floor_area_sqm` Missingness

**Status**: Decided

**Problem**: 269/1110 nulls (24%). Mostly Bank of Commerce (231 of 234 rows) — structural absence from that source's listing format. Remaining 38 nulls are scattered (Lamudi: 32, others: 6).

**Decision**: Option A — median imputation by `property_type` + `city`, add `floor_area_imputed` flag column.

**Implementation logic**:
- Impute nulls using median grouped by `property_type` + `city`
- Add `floor_area_imputed` flag (1 = was null, 0 = original value)
- Consistent with Decision 2 imputation pattern
- Vacant lot rows: `floor_area_sqm` will be null/imputed but `area_sqm` (from Decision 1) will use `lot_area_sqm` for those rows anyway — no conflict

**Chapter 3 note**: §3.5 should note that BoC rows account for the majority of floor area nulls and that imputation is source-structural, not random missingness.

---

## Decision 4: `market_segment` Variable

**Status**: Decided (design phase)

**Problem**: `price_type` column carries labels (`ceiling`, `asking`, `floor`) that were attached by source during ABT build. These are provenance labels, not theoretically grounded economic constructs. The thesis prose was using "floor" and "ceiling" as formal valuation bounds, which is overclaiming.

**Decision**: Add a `market_segment` categorical variable with three levels:
- `open_market` → Lamudi (682 rows)
- `bank_ropa` → BPI, Metrobank, BoC, Landbank, China Bank Savings (320 rows)
- `floor_price` → BDO, PagIBIG (108 rows)

Rationale: BDO/PagIBIG floor prices and bank ROPA listings are meaningfully different from each other and from open-market listings. Collapsing them into a single `distressed_flag` loses that signal.

**Deployment note**: At prediction time (Streamlit map, price surface), the model will predict with `market_segment = "open_market"` fixed. This means the model estimates open-market residential price levels across Metro Cebu — a defensible and clearly scoped output.

**Chapter 3 note**: §3.2.5 and §3.5 should describe `market_segment` as a training-time control for mixed-origin price data, not as a deployed prediction feature.

---

## Decision 5: CBD Distance Audit — Which Nodes to Keep

**Status**: Decided — grounded by Gemini Deep Research (2026-04-22)
**Source document**: `thesis_main/Literature/CBD_node_selection/Polycentric Urbanism in Metro Cebu.md`

**Literature basis**: Giuliano & Small (1991), McMillen (2001, 2003), Anas Arnott & Small (1998), Heikkila et al. (1989), JICA Mega Cebu Roadmap 2050, Spatial Analysis of Local Competitiveness (MDPI 2023), Neoliberal Urbanization in Cebu (ResearchGate).

**Final node decisions:**

| Node | Variable | Decision | Literature basis |
|---|---|---|---|
| Cebu Business Park | `dist_cebu_business_park_m` | **Keep** | Unambiguous primary CBD; PEZA-registered 50ha financial core; global employment density peak |
| IT Park | `dist_it_park_m` | **Drop** | r=0.99 with CBP; overlapping commuting shed; treat as single Urban Core per Anas et al. agglomeration continuity principle |
| Mandaue CBD | `dist_mandaue_cbd_m` | **Keep** | Major secondary industrial/logistics node; passes McMillen nonparametric test as distinct residual peak |
| Mactan CBD / Airport | `dist_mactan_cbd_m` | **Keep** | Geometrically distinct (island); MEPZ I & II (175+ ha PEZA); aerotropolis effect; bridge friction creates independent sub-market |
| South Road Properties | `dist_srp_m` | **Keep** | 265ha master-planned waterfront zone; SM Seaside anchor; CCLEX nexus; JICA identifies as distinct urban cluster requiring separate infrastructure sub-roadmap |
| Talisay Tabunok | `dist_talisay_tabunok_m` | **Keep** | Traffic-induced commercial expansion; JICA explicitly names as key urban cluster; distinct from SRP by function and location |
| Minglanilla Poblacion | `dist_minglanilla_poblacion_m` | **Drop** | Likely fails Giuliano & Small employment density threshold; small town center, may not survive McMillen stage-2 significance test |
| Naga City | `dist_naga_city_m` | **Keep (External)** | Population 133,000+; Apo Cement, KEPCO-SPC power plants, Naga Valley Industrial Park, Naga Special Economic Zone; JICA designates as satellite subcenter; Metro Cebu Expressway origin point. NOTE: dual effect — positive employment pull for Talisay/Minglanilla workers, negative pollution externality (industrial emissions cross boundary). Single distance variable captures net effect; decomposition deferred to future work. |
| Consolacion | `dist_consolacion_m` | **Keep** | Northern industrial spillover from Mandaue; strongest price correlation of all variables (-0.162); functions as established peripheral peak |
| Airport | `dist_airport_m` | **Keep** | Aerotropolis price effect; unique signal not captured by Mactan CBD distance |
| Minglanilla Lipata | `dist_minglanilla_lipata_m` | **Drop** | r=0.997 with Minglanilla Poblacion; duplicate measurement |

**Final retained set (7 variables from 11):**
`dist_cebu_business_park_m`, `dist_mandaue_cbd_m`, `dist_mactan_cbd_m`, `dist_srp_m`, `dist_talisay_tabunok_m`, `dist_naga_city_m`, `dist_consolacion_m`, `dist_airport_m`

Wait — that is 8. Recount: CBP, Mandaue, Mactan, SRP, Talisay, Naga, Consolacion, Airport = **8 variables retained**.

**Additional finding — GWR recommendation:**
The literature (Heikkila 1989; Kuala Lumpur, Bangkok studies) recommends Geographically Weighted Regression (GWR/MGWR) to capture spatial heterogeneity in subcenter influence. This is beyond the current OLS + RF + XGBoost scope. For OLS, note in limitations that global coefficients mask sub-market variation. For RF/XGBoost, spatial heterogeneity is partially captured implicitly. Flag GWR as future work.

**Chapter 3 note**: §3.4.1 must cite JICA Mega Cebu Roadmap 2050 and the polycentric urbanism literature for each retained node. The Naga City dual-effect (employment pull vs. industrial pollution externality) should be acknowledged explicitly with a limitation note.

---

## Decision 6: Amenity Scores vs. Hansen Gravity Scores

**Status**: Decided

**Problem**: The ABT contains two parallel sets of accessibility features for the same 6 amenity categories:
- `amenity_score_*` (7 columns) — simple weighted POI count within 1km radius; treats all POIs within the radius equally regardless of distance
- `hansen_*` (7 columns) — gravity-weighted accessibility scores with distance decay (β=2.0); closer POIs contribute more than farther ones

Both measure the same underlying concept (amenity accessibility), creating 14 columns of redundant signal.

**Decision**: Drop all `amenity_score_*` columns. Retain and recompute `hansen_*` scores only.

**Rationale**:
- Hansen scores are strictly more informative — they preserve the distance gradient within the catchment radius
- Hansen is theoretically grounded (Hansen 1959) and standard in accessibility literature
- Keeping both adds redundant features that compete in the model and complicate feature importance interpretation
- Hansen scores are being recomputed with network distance anyway (see Decision 7), making amenity scores further outdated

**Implementation**: Drop 7 `amenity_score_*` columns from ABT after Hansen recomputation is complete.

**Chapter 3 note**: §3.4.1 amenity scoring subsection should reference Hansen (1959) and explain the distance decay rationale. Remove the simple weighted-count description.

---

## Decision 7: Switch CBD Distances and Hansen Scores to Network Distance

**Status**: Decided

**Problem**: All current distance computations use Haversine (straight-line) distance. This is inaccurate for Metro Cebu because:
- Mactan Island properties (Lapu-Lapu, 312 rows) are separated from the mainland by water — Haversine understates effective distance to mainland nodes
- Cebu's topography (mountains to the west) creates road detours not captured by straight-line distance
- Network distance better reflects actual accessibility, which is the theoretical basis for distance-as-value-driver

**Decision**: Full switch to network distance (osmnx road network routing) for:
1. All 6 retained CBD distance variables
2. All 7 Hansen gravity score computations (distance decay uses network distance instead of Haversine)

**Rationale**: Pipeline was originally built and run in under half a day. Recomputation is low risk given existing tooling. Network distance is theoretically superior and aligns with the polycentric urbanism literature (Giuliano & Small 1991; McMillen 2003).

**Implementation notes**:
- Check whether `compute_hansen_scores.py` uses Haversine directly or already uses osmnx — determines if this is a modification or a partial rewrite
- Cache the Metro Cebu road graph to avoid redundant downloads
- Add `is_mactan_island` binary flag (1 for Lapu-Lapu City properties) as an additional feature to capture the island premium/discount that network distance alone may not fully represent

**Chapter 3 note**: §3.4.1 should explicitly state that network distance is used instead of Euclidean distance, and cite the Mactan bridge effect as the primary motivation.

---

## Decision 8: BSP RPPI — Exclude from Model

**Status**: Decided

**Problem**: BSP Residential Real Estate Price Index (RPPI) was listed in Chapter 2 and Chapter 3 as a planned macroeconomic time-trend control. The file `Data/RPPI/RPPI.xlsx` exists with quarterly Metro Cebu index values. However, RPPI was never joined to the ABT and is not among the 50 columns in `abt_clean.csv`.

**Why it cannot be included**: RPPI is a quarterly time-series. To join it meaningfully, each property row needs a collection date to match the correct quarter's index value. The ABT has no per-row date column. Without dates, RPPI would be assigned the same constant value to all 1,110 rows — a constant adds zero explanatory power and is absorbed into the model intercept.

**Decision**: Exclude RPPI from the modeling feature set. The ABT is a cross-sectional snapshot, not a panel dataset. The cross-sectional design structurally precludes RPPI as a time-varying control.

**No implementation needed**: Nothing to add to the Copilot task list.

**Chapter 3 note**: §3.2.3 should acknowledge RPPI as a macro variable that was considered but excluded, with one sentence explaining that the cross-sectional design lacks per-property collection dates required for a quarterly index join.

**Chapter 2 note**: RPPI citations (BSP, 2025) remain valid for describing market conditions — do not remove them. Only remove any claim that RPPI is used as a model input.

---

## Decision 9: Custom Accessibility Scoring — Metro Cebu Residential Accessibility Index (MCRAI)

**Status**: Decided — framework designed; implementation pending POI fetch + Stage 1 OLS

**Advisor direction (2026-04-22)**: Do not apply OHANA framework directly. Build a custom scoring model purpose-built for Metro Cebu residential valuation.

**Source documents**:
- `thesis_main/Literature/Polycentric_Urbanism/Polycentric Urbanism_ Metro Cebu POI Analysis.md`
- `thesis_main/reference/5_Questions.md` (NotebookLM synthesis — custom accessibility scoring literature)

**Why a custom model (OHANA limitations — literature-documented):**
1. Normative vs. positive economics — equity mapping asks where services *should* be; valuation asks what the market actually prices
2. MAUP problem — OHANA's 1km grid is too coarse for parcel-level valuation
3. Euclidean distance — ignores network friction (already resolved via Decision 7)
4. Assumed equal weights — violates economic utility theory
5. Fixed decay parameter — β=2.0 may not reflect Metro Cebu's travel behavior

**Index name**: Metro Cebu Residential Accessibility Index (MCRAI). Use this name in the thesis to signal it is purpose-built, not borrowed from OHANA.

**9 Categories** (6 existing + 3 new):

| # | Category | POI types | Notes |
|---|---|---|---|
| 1–6 | Existing categories | (unchanged) | Education, Health, Finance, Grocery, Transport, Security |
| 7 | **Tourism & Hospitality** | Hotels, beach resorts, dive shops, tourist attractions | Dual effect: positive for condos/vacation properties, negative externality for family homes at close range. Standard Hansen treats all proximity as positive — flag as limitation in Chapter 3. Most relevant: Lapu-Lapu, Talisay, Minglanilla |
| 8 | **Recreation & Green Space** | Parks, plazas, nature reserves, sports facilities | Nonlinear in Southeast Asia: 0–500m often a dead zone or nuisance; premium appears at 500m–2km. Property-type interaction (condos vs. houses) matters. Flag as limitation in Chapter 3. |
| 9 | **Retail Density** | Convenience stores — 7-Eleven, Alfamart, Ministop, FamilyMart | Proxy for urban commercial maturity and walkability. Distinct from Grocery (which is food access). Reflects Metro Cebu's macroeconomic landscape. Taipei study confirms positive premium especially for mid-to-lower-tier housing. |

**Why not gasoline stations**: Standard Hansen scoring treats proximity as purely positive. Gasoline stations have a documented severe negative effect at 0–200m (−16% price discount, China study) and moderate negative at 201–600m. Including them naively in Hansen would actively misrepresent the effect. Excluded for now; flag as a future nonlinear distance-band feature.

**Category-specific radii (decided 2026-04-22, grounded in literature):**

| Category | Radius | Tier | Reasoning |
|---|---|---|---|
| Education | 5km | Macro | Universities draw regionally |
| Health | 5km | Macro | Tertiary hospitals serve wide area |
| Finance | 3km | Meso-wide | ATMs cluster near town centers in peripheral LGUs (Talisay, Minglanilla, Consolacion) — 2km too tight |
| Grocery | 2km | Meso | Neighborhood shopping trip |
| Transport | 5km | Macro | Road corridors are city-wide signal |
| Security | 2km | Meso | Local service catchment |
| Tourism & Hospitality | 5km | Macro | Resort/hotel strip serves area-wide market |
| Recreation & Green Space | 1.5km | Micro-meso | Expanded from 800m — Lapu-Lapu island road network inflates network distances vs. Haversine |
| Retail Density | 1.0km | Micro | Expanded from 500m — same reason; 500m network radius cut off Lapu-Lapu properties (96% zeros) |

**Network distance radius fix (decided 2026-04-22):**
Current `network_utils.py` applies `radius_km` as a Haversine pre-filter only — the Hansen score uses network distance, but the cutoff determining which POIs are included is still straight-line. Fix: use Haversine as a loose pre-screen (e.g., `hav_km <= radius_km * 1.5`), then apply the true radius cutoff after computing network distance. This makes the radius a genuine network distance threshold.

**Weight derivation — Two-Stage Method (key methodological contribution):**

Weights are NOT assumed — they are derived from the data after OLS fitting.

- **Stage 1**: Run OLS hedonic regression with all 9 individual unweighted MCRAI category scores as features alongside structural and locational variables. Extract statistically significant category coefficients (implicit prices).
- **Stage 2**: Normalize significant coefficients → these become the composite weights for `mcrai_composite`.
- If multicollinearity between categories is severe, use RF/XGBoost feature importance as weight proxy instead of OLS coefficients.

**Literature basis**: Two-stage hedonic regression for accessibility weight derivation — validated in Beijing POI hedonic study. Agosto (2017) Cebu-specific grounding: Mobility (transport) and Livability (open space + neighborhood facilities) are the primary residential value drivers in Cebu → expect transport and recreation to carry elevated weights.

**Placeholder weights** (for initial ABT construction before Stage 1 runs — arbitrary, do not interpret):
```
transport: 0.20 | grocery: 0.15 | education: 0.15 | health: 0.12
finance: 0.10 | security: 0.04 | tourism: 0.10 | recreation: 0.08 | retail_density: 0.06
```

**Why not gasoline stations**: Documented −16% price discount at 0–200m. Standard Hansen treats proximity as positive — would misrepresent the effect. Excluded; flag as future nonlinear distance-band feature.

**Implementation sequence for Copilot**:
1. Fetch POIs for 3 new categories (tourism, recreation, retail_density) from Google Maps Places API across 6 LGUs
2. Update `network_utils.py`: fix radius to be a true network distance threshold, not just a Haversine pre-filter
3. Update `compute_hansen_scores.py`: support per-category radii via dict; rename output columns from `hansen_*` to `mcrai_*`
4. Rerun all 9 categories with category-specific radii
5. Update composite column to `mcrai_composite` with placeholder weights (flagged as temporary)
6. **After Stage 1 OLS**: recompute `mcrai_composite` with empirically derived weights

**Chapter 3 note**: §3.4.1 must explain OHANA limitations as justification for MCRAI, describe all 9 categories with category-specific radii and tier rationale, describe the two-stage weight derivation, acknowledge β=2.0 as defensible baseline, and cite: Hansen (1959), Agosto (2017), Beijing POI hedonic study, OHANA framework limitations literature.

**Addendum — retail_density scope and zero-rate interpretation (2026-04-28):**

`mcrai_retail_density` measures access to **formal convenience stores** (7-Eleven, Lawson's, Uncle John's/former Ministop, Alfamart) as a proxy for urban commercial maturity and walkability.

**Scope limitation**: The 40.3% overall zero rate reflects **absence of formal convenience stores within 1km road network distance** — not absence of retail activity. The informal sector (sari-sari stores, unregistered micro-businesses) is not indexed in Google Maps Places API and is therefore outside the measurement scope. This is a known and accepted data limitation.

**Interpretation**: The zeros are interpretable signal. Peripheral LGUs (Consolacion, Minglanilla) and low-density barangays genuinely have lower formal convenience store density. A zero score means no indexed formal store is reachable within 1km by road — meaningful for walkability and commercial maturity as value proxies.

**Chapter 3 note**: §3.4.1 should state explicitly that `mcrai_retail_density` measures access to formal convenience stores indexed in Google Maps, and acknowledge that the informal retail sector is outside measurement scope.

---

## Decision 10: Pre-Modeling Data Integrity Row Drops

**Status**: Decided (2026-04-28)

**Problem**: Three rows were identified with physically implausible `price_per_sqm` values that indicate data quality failures, not genuine residential listings.

| Row idx | Property ID | City | Property Type | Price PHP | area_sqm | price_per_sqm |
|---------|-------------|------|---------------|-----------|----------|---------------|
| 431 | 468 | Cebu City | Vacant Lot | 294,000 | 80,000 | 3.68 |
| 658 | 714 | Cebu City | Vacant Lot | 280,000 | 67,725 | 4.13 |
| 705 | 769 | Mandaue City | Single Detached | 21,000 | 4,564 | 4.60 |

**Decision**: Drop all three rows before model fitting.

**Grounds** (data integrity, not outlier suppression):
- Rows 431 and 658: ₱3–4/sqm for 6–8 hectare lots. BIR residential zonal values in Metro Cebu start at ₱1,500–3,000/sqm minimum. These are almost certainly agricultural lots misclassified by a Lamudi residential category search — not residential property listings.
- Row 705: ₱21,000 total for a 4,564 sqm single detached house. The nearest plausible reading is a decimal/unit entry error (₱21,000 → should be ₱21,000,000), but the original price field cannot be verified from the data alone. Implausible as-is.

**Implementation note**: These rows are identified and reported in the EDA script. The actual drop happens in the pre-modeling data prep step — not in `abt_clean.csv` directly. The EDA script does not drop rows.

**Impact**: Reduces modeling-ready dataset from 1,110 rows (minus 32 null price_per_sqm, minus 14 null spatial_lag_price) to approximately 1,061 usable rows after all pre-modeling drops. Final count confirmed at model fitting time.

**Chapter 3 note**: §3.5 should document these three rows as removed for data integrity reasons, distinguish this from statistical outlier removal, and note that agricultural land misclassified as residential is a known risk in scraping-sourced Philippine listing data.

---

## Decision 11: CBD Distance Multicollinearity Treatment

**Status**: Decided (2026-05-01)
**Source**: EDA output — `cbd_distance_corr.png`

**Problem**: Two highly collinear pairs flagged from the CBD distance correlation matrix:
- `dist_srp_m` × `dist_talisay_tabunok_m`: r = 0.959
- `dist_talisay_tabunok_m` × `dist_naga_city_m`: r = 0.973

`dist_talisay_tabunok_m` appears in both pairs — it is the shared collinear variable. At r > 0.95, OLS coefficient estimates become unstable and standard errors inflate.

**Decision**: Differential treatment by model type.

- **OLS (baseline comparator)**: Drop `dist_talisay_tabunok_m` from the OLS feature set. This stabilizes coefficient estimates. Talisay Tabunok's effect is partially captured by SRP and Naga City distances in OLS.
- **Random Forest and XGBoost**: Keep all 8 CBD distance variables. Tree models handle multicollinearity implicitly — correlated features do not destabilize splits. Retaining `dist_talisay_tabunok_m` preserves the full spatial signal for the deployed models.

**Rationale**: OLS is a benchmark comparator only — it is not the deployed model. Dropping one variable for OLS stability is defensible and does not compromise the deployed price surface.

**Literature basis**: Multicollinearity in hedonic OLS is a documented issue when CBDs are spatially clustered (Heikkila et al. 1989). Tree-based models are robust to correlated predictors (Breiman 2001).

**Chapter 3 note**: §3.5 should note that `dist_talisay_tabunok_m` is excluded from the OLS feature set due to multicollinearity (r > 0.95 with adjacent nodes), and that all 8 CBD distance variables are retained for RF and XGBoost.

---

## Decision 12: OLS X_ols — Additional Collinearity Drops

**Status**: Decided (2026-05-01)
**Source**: run_models.py diagnostic output — near-singular matrix flags during model fitting

**Problem**: After the initial X_ols construction (X_full minus `dist_talisay_tabunok_m`), three additional near-perfect collinearities were identified in OLS:

1. **`is_mactan_island` ≡ `city_Lapu-Lapu City`** (one-hot dummy): `is_mactan_island = 1` for all Lapu-Lapu City properties by definition (Decision 7). Perfectly duplicates the city dummy. Condition number ~1e+16 before fix.
2. **`bir_zonal_rr_log` ≡ `log(bir_zonal_rr_median)`**: Near-perfect log-linear relationship with `bir_zonal_rr_median` already in the feature set. Redundant log form in OLS causes coefficient instability.
3. **`is_vacant_lot` ≡ `property_type_Vacant Lot`** (one-hot dummy): Both equal 1 iff property_type is "Vacant Lot". Identical columns confirmed by matching coefficients (1.2910) and t-stats.

**Decision**: Drop `is_mactan_island`, `bir_zonal_rr_log`, and `is_vacant_lot` from X_ols only. Keep all three in X_full for RF/XGBoost (tree models handle duplicated information without instability).

**Rationale**: These are structural collinearities arising from the data encoding pipeline — not domain-relevant features being discarded. The island flag and vacancy flag are already represented in OLS through city dummies and property_type dummies respectively.

**Chapter 3 note**: §3.5 should note that six columns are excluded from X_ols (decisions 11–13) while all 46 features are retained for RF and XGBoost.

---

## Decision 13: OLS X_ols — Log-Transform Area Variables (Log-Linear Hedonic Spec)

**Status**: Decided (2026-05-01)
**Source**: Diagnostic output — OLS producing MAPE 597%, R² −45 on test set; traced to extreme area_sqm values (max 150,000 sqm)

**Problem**: The ABT contains a small number of large-scale development listings misclassified as residential (e.g., property_id 552: 150,000 sqm floor_area, price_per_sqm = 2,000 PHP). With OLS coefficient ≈ 4.0e-05 on `area_sqm`, the contribution is +6.0 to log_price → exp(6) ≈ 400x amplification. These rows remain in the dataset as valid market observations (they are open-market Lamudi listings with genuine prices); dropping them would require an arbitrary size cutoff with no literature basis.

**Decision**: For X_ols only, replace the three raw area columns with their log1p-transformed versions:
- `lot_area_sqm` → `log_lot_area_sqm = log1p(lot_area_sqm)`
- `floor_area_sqm` → `log_floor_area_sqm = log1p(floor_area_sqm)`
- `area_sqm` → `log_area_sqm = log1p(area_sqm)`

For X_full (RF/XGBoost): retain raw area values. Tree models handle nonlinear area-price relationships through splits, so log transformation is unnecessary.

**Rationale**: Log-linear and log-log hedonic price regressions are standard in the literature (Rosen 1974; Can 1992; Sirmans et al. 2005). With log_price as the target variable, using log-transformed area variables creates a log-log model where area coefficients are directly interpretable as elasticities (e.g., 1% increase in area → X% change in price per sqm). This is the correct functional form for hedonic OLS with a right-skewed size distribution.

**Observed effect after fix**: OLS train R² improved from 0.717 to 0.890; test R² improved from −45 to 0.394. OLS remains the weakest model (expected for linear baseline), with RF (R² 0.641) and XGBoost (R² 0.616) outperforming.

**Chapter 3 note**: §3.5 should state that the OLS specification uses log-transformed size variables (log-log specification) consistent with hedonic price theory, while RF and XGBoost use raw area values since tree splits handle nonlinear area effects implicitly.


---

## Chapter 3 Flags — Limitations and Interpretive Notes (2026-05-01)

### Flag A: Tourism vs. Recreation Category Separation

**For**: §3.4.1 (MCRAI category design) and §3.5 (limitations)

In Metro Cebu's OSM data, the boundary between tourism and recreation POIs is not always clean. A beach resort near Mactan could be tagged under either category. The two were kept separate based on conceptual grounds: tourism amenities signal economic activity and destination appeal, while recreation amenities signal residential livability. However, if SHAP values from the deployed RF model show both categories ranking low and similarly, the separation may not be adding predictive signal in this local context. This should be acknowledged as a limitation — the MCRAI framework may benefit from collapsing or reweighting these two categories in future iterations with richer local POI data.

### Flag B: Negative Tourism Coefficient — Disamenity Interpretation

**For**: §3.5 (OLS findings and limitations) and §4.x (model interpretation)

The OLS Stage 1 model produced a statistically significant negative coefficient for `mcrai_tourism` (coef = −0.011, p = 0.0001). Two complementary explanations apply:

1. **City composition effect**: Tourism amenities in Metro Cebu are spatially concentrated in Lapu-Lapu City (Mactan resort corridor), which carries a significant city-level price discount (OLS city dummy coef = −1.17). The negative coefficient partially reflects this geographic overlap rather than a pure tourism effect.

2. **Disamenity effect**: Proximity to high-traffic tourism nodes generates noise, congestion, and reduced residential privacy. Residential buyers in Metro Cebu appear to price livability over tourism accessibility — a pattern consistent with the hedonic pricing literature on commercial spillover disamenities (documented for busy corridors, markets, and tourist hubs).

Both mechanisms likely operate simultaneously. The disamenity interpretation is behaviorally grounded and should be cited in the manuscript with appropriate hedonic pricing literature (e.g., Luttik 2000 on amenity/disamenity effects; verify before citing).

**Note**: Because of the sign reversal and city absorption issue, `mcrai_tourism` OLS coefficient was not used for Stage 2 MCRAI weight derivation. SHAP-based weights from the RF model were used instead (see Decision 14).


---

## Decision 14: MCRAI Stage 2 Weights — Use RF SHAP Instead of OLS Coefficients (Historical)

**Status**: Historical / superseded by Decision 20 (recorded 2026-05-01; superseded 2026-05-05)
**Source**: OLS Stage 1 output (mcrai_stage2_weights.txt) + user review

**Supersession note**: This was an interim response to the pre-Decision-20 modeling state. It is retained as project history only. The controlling composite rule is now Decision 20: positive-coefficient OLS categories only.

**Problem**: The original two-stage plan used OLS Stage 1 coefficients to derive MCRAI category weights. Two issues make this unreliable:

1. Only 2 of 9 categories reached p < 0.05 (tourism and retail_density). The other 7 are statistically indistinguishable from zero in OLS — not because they don't matter, but because city fixed-effect dummies absorbed most of the MCRAI spatial variation before the scores could explain it.
2. The tourism coefficient is negative (coef = −0.011), reflecting city composition overlap with the Lapu-Lapu discount and a residential disamenity effect from high-traffic tourism zones. Using a negative weight in an accessibility composite is not interpretable.

**Decision**: Derive Stage 2 MCRAI weights from **RF SHAP mean absolute values** for the 9 MCRAI columns in X_full.

Procedure:
- Extract SHAP values for the RF model on the test set (already computed in run_models.py Step 8)
- Isolate the 9 mcrai_* columns
- Compute mean |SHAP| per category
- Normalize to sum = 1.0
- Save as updated mcrai_stage2_weights.txt

**Rationale**:
- RF is the better-performing deployed model (test R² = 0.641 vs OLS 0.394)
- SHAP isolates each feature's marginal contribution after all other features (including city) are accounted for — no city absorption problem
- SHAP-based weights reflect what the actual deployed model learned, not a linear approximation constrained by OLS assumptions
- Both positive and negative SHAP contributors can be handled correctly (|SHAP| is used, so direction does not corrupt the weight)

**Chapter 3 note**: Keep this as a historical modeling branch only. Do not describe RF SHAP weights as the current Stage 2 composite in Chapter 3; the controlling thesis-standard composite is now Decision 20.


---

## Decision 15: Adopt RF SHAP Weights as Final MCRAI Stage 2 Weights (Historical)

**Status**: Historical / superseded by Decision 20 (recorded 2026-05-01; superseded 2026-05-05)
**Source**: extract_mcrai_shap_weights.py output — mcrai_shap_weights.txt

**Supersession note**: These SHAP-derived weights are no longer the thesis-standard `mcrai_composite` definition. They remain archived for historical comparison only. Decision 20 replaced this composite with the positive-only OLS specification.

**Historical RF SHAP weights (normalized to sum = 1.0):**

| Category | Weight |
|---|---|
| mcrai_grocery | 0.261 |
| mcrai_retail_density | 0.186 |
| mcrai_recreation | 0.144 |
| mcrai_transport | 0.109 |
| mcrai_health | 0.108 |
| mcrai_tourism | 0.058 |
| mcrai_finance | 0.057 |
| mcrai_security | 0.046 |
| mcrai_education | 0.031 |

**Interpretation**: Grocery and retail density dominate (47% combined), reflecting the primacy of daily commercial access in Metro Cebu residential preferences. Recreation and transport follow as livability and commute signals. Tourism, finance, security, and education contribute smaller but nonzero weights — no category is zeroed out.

**Action at the time**: These weights were previously used to update `compute_hansen_scores.py`, but they are now archived and should not be restored.

**Chapter 3 note**: If this branch is mentioned at all, present it strictly as a superseded intermediate weighting approach that was later replaced by Decision 20.

---

## Decision 16: Drop `floor_area_imputed` from Feature Matrix

> Date: 2026-05-03
> Audit script: `thesis_main/Scripts/audit_floor_area_imputed.py`

**Decision**: Remove `floor_area_imputed` from `EXCLUDE_COLS` in `run_models.py` (add it to exclusions) and remove it from the feature vector in `thesis_main/app/lib/features.py`.

**Evidence from audit (n=1,110)**:

| floor_area_imputed | bank_ropa | floor_price | open_market |
|---|---|---|---|
| 0 (n=841) | 10.2% | 12.5% | 77.3% |
| 1 (n=269) | **87.0%** | 1.1% | 11.9% |

- 87% of imputed rows are `bank_ropa` — well above the 60% drop threshold established in the audit plan.
- 85% of imputed rows by property type are `Vacant Lot` — consistent with bank repossession assets that have no floor area by definition.
- All 32 open_market imputed rows have `price_per_sqm = NaN` — they carry no price label and contribute nothing to model training.
- Point-biserial correlation: r = −0.531 (p < 0.001) — the flag's strong negative correlation with price is entirely explained by the bank_ropa concentration, not by floor area missingness itself.

**Why this matters**: Retaining `floor_area_imputed` allows the model to partially reconstruct the `market_segment` signal through a surrogate variable. If the market_segment treatment is later revisited (Decision 17, pending), the flag would reintroduce the segment effect through the back door.

**Chapter 3 note**: Report that missingness indicators were evaluated before model fitting. `floor_area_imputed` was found to be a bank_ropa proxy (87% concentration) and excluded. `bedrooms_imputed` and `bathrooms_imputed` were audited and retained — both are evenly distributed across market segments (≤35% bank_ropa) and show meaningful price gaps within open_market (bedrooms: PHP 130K vs 171K/sqm; bathrooms: PHP 108K vs 170K/sqm), indicating genuine listing behavior rather than segment leakage.

---

## Decision 17: Restrict Training Data to open_market Segment Only

> Date: 2026-05-03
> Literature basis: `thesis_main/Literature/Market Segment/market_segment_stratification_deep_research.md`

**Decision**: Filter `abt_clean.csv` to `market_segment == "open_market"` rows only before model fitting. Remove `market_segment` from the feature matrix entirely — no dummies, no reference category.

**Rationale**:

The thesis objective is to estimate **open-market residential price** across Metro Cebu. The International Valuation Standards (IVS 104, IVSC 2022) define Market Value as requiring an arm's-length transaction between willing parties acting without compulsion. Bank foreclosure (bank_ropa) data represents **Liquidation Value** under the IVS framework — a distinct basis of value. Administrative floor prices (floor_price) are not market transactions at all.

Pooling these segments into a single model with a market_segment dummy violates the definitional basis of what the thesis is predicting. The IVS explicitly treats forced sale prices as a different value basis, not a discounted variant of Market Value. The IMF (2023) Philippines Technical Assistance Report echoes this for the BSP's RPPI methodology.

Empirical literature further supports stratification over pooling:
- Droes, Hoesli & Bourassa (2019): stratified models improved R² from 0.637 to 0.782 vs. pooled.
- Usman et al. (2020, Malaysia): stratified models improved fit by 7% and reduced error by over 10%.
- Foreclosure discount in the Philippines documented at 28–30% (Calinao et al., 2022); Kuala Lumpur at 34% (Wong et al., 2014). These discounts are real effects that contaminate open-market coefficient estimates when pooled.

The argument for pooling (sample size in thin markets) is addressed by Phase C: expanding open_market listings via additional data sources, not by retaining non-arm's-length rows.

**Implementation**:
- In `thesis_main/Scripts/run_models.py`: add `df = df[df["market_segment"] == "open_market"].copy()` immediately after loading the ABT, before any encoding or feature construction.
- Remove `"market_segment"` from `CAT_COLS` (or confirm it is excluded after the filter makes it a constant column).
- `market_segment_open_market` and `market_segment_floor_price` dummies will no longer appear in `rf.feature_names_in_`.
- Update `thesis_main/app/lib/features.py`: remove `market_segment_floor_price` and `market_segment_open_market` from the feature vector — they are no longer model features.
- Update `thesis_main/app/pages/2_Property_Predictor.py`: remove the `FIXED_FEATURES` filter from the SHAP section — it is no longer needed.

**Training row count impact**: From 1,110 total rows → ~682 open_market rows. CI width will remain elevated until Phase C (data expansion) adds more open_market listings.

**Chapter 3 note**: §3.3 should state that the training dataset was restricted to arm's-length open-market listings (n ≈ 682) in accordance with the IVS 104 Market Value definition (IVSC, 2022). Bank foreclosure and administrative floor price records were excluded on the basis that they represent Liquidation Value and administered price floors respectively — distinct value bases incompatible with a market value prediction objective. Cite: IVSC (2022) IVS 104; IMF (2023) Philippines TA Report; Droes et al. (2019); Usman et al. (2020).

## Decision 18: Expand `mcrai_retail_density` to Food & Retail Density + Fix Bbox Contamination Bug

**Status**: Decided (2026-05-04)

Expanded the `retail_density` POI category from formal convenience stores only (7-Eleven, Alfamart, Ministop, FamilyMart) to include restaurants, cafes, and bakeries across all 6 LGUs. Motivation: peripheral LGUs (Talisay, Minglanilla) have sparse indexed convenience stores but significant food establishment density that better captures commercial maturity. The category remains a proxy for "commercial walkability" - food establishments are a valid and arguably stronger signal of commercial density in Philippine peripheral urban areas than formal convenience chains alone.

Also expanded recreation text queries (gym, swimming pool, beach park, sports complex by LGU) and tourism text queries (inn, pension house, guesthouse, transient house, bed and breakfast) to capture smaller lodging types missed by the `lodging` nearby type. Added three new seed areas: talisay_tabunok, minglanilla_south, naga_city_boundary.

**Bug fix**: `assign_lgu_by_nearest_centroid()` in `to_output_frame()` previously assigned every POI to the nearest LGU centroid regardless of actual geographic location. POIs in Bohol, Batangas, Tagaytay, and Balamban were passing the `TARGET_LGUS` filter. Fixed by adding `within_metro_cebu_bbox()` guard before LGU assignment.

**Chapter 3 note**: Update §3.4.1 to describe `mcrai_retail_density` as measuring commercial food & retail density (convenience stores, restaurants, cafes, bakeries indexed in Google Maps Places) as a proxy for walkability and urban commercial maturity. Retain the limitation note that informal retail (sari-sari stores) is outside measurement scope.

---

## Decision 19: run_models.py Fixes for open_market-Only Training

> Date: 2026-05-05

**Status**: Implemented

**Problem encountered on first retrain**: After filtering to open_market only (Decision 17), `run_models.py` crashed at two points:

1. **Imputer crash** (`ValueError: Columns must be same length as key`): `lot_area_sqm` is 100% null for open_market rows (Lamudi listings do not collect lot area). `SimpleImputer(strategy='median')` cannot compute a median with zero observed values — it silently skips the column, returning a narrower array than expected.

2. **OLS dtype error** (`ValueError: Pandas data cast to numpy dtype of object`): `market_segment` was removed from `CAT_COLS` (Decision 17) but was not added to `EXCLUDE_COLS`. It remained in the feature matrix as a string column (constant "open_market"), which statsmodels rejected.

**Fixes applied**:

1. **Imputer**: Separate fully-null columns from imputable columns before calling `fit_transform`. All-null columns are filled with 0 (principled default: `lot_area_sqm=0` means "not collected", which is the correct representation for open_market Lamudi listings). Implementation in `run_models.py` lines 100–114.

2. **Feature exclusion**: Added `market_segment` to `EXCLUDE_COLS` — it is a constant after the Decision 17 filter and adds no information.

3. **OLS collinearity fixes**:
   - Added `log_lot_area_sqm` to `OLS_EXTRA_DROPS` — it is constant (log1p(0) = 0) because `lot_area_sqm` is all-null for open_market.
   - Removed `log_area_sqm` from OLS log-area columns — it is perfectly collinear with `log_floor_area_sqm` for open_market rows where `lot_area_sqm` is null (Decision 1 fallback: `area_sqm = floor_area_sqm` when lot_area is missing).
   - OLS condition number improved from 1.04e+16 → 7.94e+06 after these fixes.

4. **App alignment**: Added `market_segment == "open_market"` filter to `TRAIN_ABT` in `app/lib/features.py` so `TRAIN_MEDIANS` (used as fallback values for user inputs) reflects the open_market training distribution rather than all three segments.

**Why lot_area_sqm = 0 is acceptable**: For the tree models (RF, XGBoost), a constant-zero feature contributes zero information gain to any split and is effectively ignored. It does not degrade model performance. The feature remains in X_full for structural completeness and in case future open_market data sources collect lot area.

**No impact on MCRAI Stage 2 weights**: The OLS collinearity fixes (removing log_lot_area_sqm and log_area_sqm) did not change the MCRAI coefficients — these area variables are orthogonal to the MCRAI scores in the design matrix.

**Chapter 3 note**: Note that `lot_area_sqm` is structurally absent from Lamudi (open_market) listings. The area variable used in the model is `floor_area_sqm` / `area_sqm` (per Decision 1 fallback). No lot area proxy was substituted.

---

## Decision 20: Positive-Only MCRAI Composite — Exclude Security, Tourism, Retail Density

> Date: 2026-05-05

**Status**: Decided — literature confirmed (partial). Security and retail: fully supported. Tourism: partially supported — Shenzhen theme park citation unverified; use Chen & Jim (2010) and Dronyk-Trosper (2017) as stand-ins. See `thesis_main/reference/lit_decision20_spatial_sorting.md`.

**Background**: Stage 2 weight derivation (run_models.py Step 9) uses |OLS coefficient| normalized to sum=1. Three of the seven significant MCRAI categories returned negative OLS coefficients: `mcrai_security` (−0.093, 59.5% weight), `mcrai_tourism` (−0.023, 14.7% weight), and `mcrai_retail_density` (−0.007, 4.7% weight). These three account for 69.9% of composite weight despite pushing price in the negative direction.

**Decision**: Restrict `mcrai_composite` to positive-coefficient categories only — education, grocery, transport, and recreation. Weights renormalized to sum=1:

| Category | OLS coef | Composite weight |
|---|---|---|
| mcrai_education | +0.013 | 0.401 |
| mcrai_grocery | +0.010 | 0.310 |
| mcrai_recreation | +0.006 | 0.199 |
| mcrai_transport | +0.003 | 0.102 |

Security, tourism, and retail_density remain as individual model features and continue to contribute to RF/XGBoost predictions through their own columns. They are excluded only from the composite index.

**Why not SHAP weights (Option B)**: SHAP mean |values| are also unsigned. `mcrai_security` has high mean |SHAP| in both the RF and XGBoost outputs, so it would still dominate the composite — the sign incoherence is not resolved by switching to SHAP. OLS implicit prices are also more interpretable in a hedonic framing than SHAP importance weights, and the open_market-only OLS now produces significant MCRAI coefficients (the city absorption problem that originally motivated SHAP weights has diminished).

**Preferred interpretation for Chapter 3/4 — SPATIAL SORTING, not disamenity**:

The negative OLS coefficients for security, tourism, and retail_density should NOT be framed as "these facilities are undesirable." The correct framing is **spatial sorting**: public security infrastructure (police substations, barangay halls) tends to be more densely deployed in lower-income, lower-price neighborhoods. The negative OLS coefficient captures reverse causality — lower prices preceded the higher security density, not the other way around. The OLS model cannot distinguish a direct disamenity effect from a sorting artifact without neighborhood income controls (which the ABT does not have). The same sorting logic may apply to tourism zones (proximity to resort strips correlates with certain neighborhood types) and commercial retail density (intrusive commercial activity in residential-zoned areas).

**Literature basis (confirmed 2026-05-07)** — see `thesis_main/reference/lit_decision20_spatial_sorting.md` for full citations and framing guidance:

- **Security (sorting):** Tiebout (1956) *JPE* + Bayer & McMillan (2012) *JPUBE* — income sorting explains security infrastructure deployment in lower-price neighborhoods.
- **Security (proximity disamenity):** Dronyk-Trosper (2017) *Real Estate Economics* — nonlinear "Goldilocks" effect: very close proximity to police/fire facilities depresses prices due to noise and institutional surroundings.
- **Security (service quality):** Brasington & Parent (2024) *RSUE* — what is capitalized is service delivery quality, not physical proximity.
- **Retail density (threshold disamenity):** Yang, Song & Choi (2016) *Sustainability* (Seoul, 25,126 parcels) — inverted-U: commercial density raises values to a threshold then depresses via noise/crowding. Song & Knaap (2004) *RSUE* — commercial proximity does not reliably produce positive hedonic coefficients.
- **Tourism (externality):** Chen & Jim (2010) *Geographical Journal* (Shenzhen) — confirms urban non-residential land uses produce disamenity capitalization. **⚠️ The "Shenzhen theme park study" cited in the POI analysis literature file (ref 20) could not be independently verified — do not cite until confirmed via Google Scholar/Scopus.**

**Implementation (done)**: `mcrai_composite` in `compute_hansen_scores.py` already uses only the four positive-coefficient categories per Decision 20 weights. `abt_clean.csv` recomputed. The initial pre-cleanup baseline retrain on the 1,516-row sample produced RF R²=0.783 and XGBoost R²=0.803; that comparison was superseded by Decision 23 after the property-type cleanup rerun.

---

## Decision 21: Hyperparameter Tuning — Baseline Models Retained

> Date: 2026-05-06

**Status**: Implemented — baseline models retained as production models

**Method**: `tune_models.py` — `RandomizedSearchCV`, n_iter=30, 5-fold CV, scoring=R², random_state=42, on the same open_market training split used in `run_models.py`. Final reported test metrics below were rechecked from the saved model artifacts on the current held-out split.

**Results**:

| Model | Best params | MAPE | MAE | RMSE | R² |
|---|---|---|---|---|---|
| RF (baseline, 300 trees) | n_estimators=300, max_depth=None, min_samples_split=2, min_samples_leaf=1, max_features=1.0 | 54.76% | 6,538,548 | 31,602,095 | 0.7831 |
| RF (tuned) | n_estimators=700, max_depth=None, min_samples_split=2, min_samples_leaf=1, max_features=0.5 | 64.50% | 8,967,186 | 44,976,326 | 0.5607 |
| XGBoost (baseline) | n_estimators=300, learning_rate=0.05, max_depth=6 | 43.93% | 6,242,660 | 30,106,433 | 0.8032 |
| XGBoost (tuned) | subsample=0.9, n_estimators=500, min_child_weight=3, max_depth=7, learning_rate=0.01, colsample_bytree=0.8 | 47.15% | 8,812,259 | 46,342,713 | 0.5336 |

**Decision**: Retain baseline `rf_model.pkl` and `xgb_model.pkl` as the production models. Neither tuned configuration outperformed its baseline on the held-out test set.

**Interpretation**:

- RF tuned (R²=0.5607) is materially worse than RF baseline (R²=0.7831). The search kept a very flexible tree depth while reducing `max_features` to 0.5 and increasing the forest to 700 trees. On this dataset, that configuration did not generalize well to the held-out set.
- XGBoost tuned (R²=0.5336) is also materially worse than XGBoost baseline (R²=0.8032). The tuned setup used a lower learning rate (`0.01`) with deeper trees (`max_depth=7`) and 500 estimators, but the final combination performed much worse on the test data.
- With only 1,212 training rows, random search had limited room to find a better configuration than the already strong baseline models. In this case, tuning increased complexity without improving generalization.

**Production model at the time of Decision 21**: XGBoost baseline (`Models/xgb_model.pkl`) — R²=0.8032, MAPE=43.93%. This deployment choice was superseded by Decision 23 after the property-type cleanup rerun.

**Tuned model files**: `Models/rf_tuned.pkl`, `Models/xgb_tuned.pkl` saved for reference — not deployed.


## Decision 22: Remove Generic `Residential` Bucket from `property_type`

> Date: 2026-05-06

**Status**: Implemented

**Problem**: The canonical `property_type` taxonomy still retained a generic `Residential` label inherited from Lamudi. On audit, this was not a coherent residential subtype. The open-market rows under this label mixed together vacant land listings, studio units, villas, and out-of-scope office/commercial listings. Leaving it in the feature matrix created an indefensible catch-all dummy and contaminated SHAP interpretation.

**Evidence from current ABT audit**:
- `open_market` `Residential` rows before cleanup: 106
- Pattern audit of listing titles / addresses:
  - 47 land / lot rows
  - 25 studio / condo-like rows
  - 6 villa / house rows
  - 28 office / commercial rows dropped as non-residential leakage
- `Residential` rows surviving in the 1,516-row modeling sample before cleanup: 95

**Decision**: Remove `Residential` as a final canonical property type. Replace it with rule-based recodes using the listing title / address text:
- Land / lot titles -> `Vacant Lot`
- Studio / condo-like titles -> `Condominium`
- Villa / house titles -> `Single Detached`
- Office / commercial titles -> drop as non-residential leakage from Lamudi
- If a future `Residential` row does not match one of these patterns, fail loudly and review it manually rather than silently keeping a catch-all label.

**Rationale**:
- `Residential` is not a market-recognizable subtype like condominium, townhouse, single detached, or vacant lot.
- The deployed app already assumes the final property-type list excludes `Residential`; keeping it only in training data creates train/deploy inconsistency.
- For panel defense, a mixed catch-all dummy is much harder to defend than a small set of explicit recodes plus documented drops.

**Implementation (done)**:
- `standardize_property_types.py` now resolves raw `Residential` rows before canonical mapping.
- Office / commercial leakage is dropped from the ABT.
- The script raises an error if any future `Residential` rows remain unresolved after the title-based recode.

**Chapter 3 note**: Describe `property_type` as a cleaned residential taxonomy and note that Lamudis generic `Residential` label was disaggregated into defensible subclasses, with office/commercial leakage removed from the open-market sample.

## Decision 23: Post-Cleanup Baseline Retrain and Production Model Switch

> Date: 2026-05-06

**Status**: Implemented

**Problem**: After Decision 22 removed the generic `Residential` bucket, the canonical ABT changed materially but the recorded model state still reflected the earlier 1,516-row sample and an XGBoost deployment assumption. That left the docs, SHAP interpretation, and app deployment record out of sync with the cleaned taxonomy.

**Evidence from the post-cleanup validation run**:
- `abt_clean.csv` current shape: 2,047 rows × 50 columns
- `open_market` rows after cleanup: 1,619
- Final modeling-ready sample after the standard filters in `run_models.py`: 1,491 rows
- `Residential` rows remaining in the full ABT: 0
- `Residential` rows remaining in the modeling sample: 0

**Decision**: Re-run the baseline OLS, Random Forest, and XGBoost models on the cleaned open-market sample, regenerate SHAP outputs, and treat baseline Random Forest as the current production model.

**Results from `run_models.py` (2026-05-06)**:
- OLS baseline: R²=0.0827, MAPE=201.63%, MAE=9,817,411, RMSE=59,820,880
- Random Forest baseline: R²=0.8069, MAPE=59.28%, MAE=4,950,161, RMSE=27,448,003
- XGBoost baseline: R²=0.4915, MAPE=60.14%, MAE=6,322,294, RMSE=44,538,841

**Rationale**:
- On the cleaned taxonomy, Random Forest materially outperformed XGBoost on the held-out test set.
- The refreshed SHAP outputs no longer rank `dist_naga_city_m` first; property-type dummies, bedrooms, and `dist_consolacion_m` now dominate the cleaned-sample explanations.
- Keeping RF as the deployed app model is now supported by the current validation run rather than by an ad hoc config change.

**Implementation (done)**:
- `run_models.py` rerun on the cleaned ABT
- `Models/rf_model.pkl` and `Models/xgb_model.pkl` refreshed
- `EDA/shap_rf_summary.png` and `EDA/shap_xgb_summary.png` regenerated
- Streamlit app config kept on `Models/rf_model.pkl` and the predictor page message switched to the dynamic `MODEL_LABEL` value

**Chapter 3 note**: If the deployed model is described explicitly, it should now be identified as the baseline Random Forest on the post-cleanup 1,491-row open-market sample. The earlier XGBoost deployment claim is historical only.

**Note on the XGBoost R² drop (2026-05-08)**: The pre-cleanup XGBoost baseline (May 5 JSON) showed R²=0.803. The post-cleanup result is R²=0.491 — a 31-point drop. This is disproportionate to the raw data change (28 rows dropped, 106 recoded — approximately 8% of the training sample). The most defensible explanation is that the generic "Residential" label was functioning as an implicit price-range proxy in XGBoost. In the pre-cleanup test set, Residential-labeled rows likely clustered in a narrow price band; XGBoost's split-based learning captured this efficiently, inflating the held-out R². Once that label was disaggregated and office/commercial leakage dropped, XGBoost lost this shortcut and its test R² fell to a more honest level. Random Forest, being less sensitive to individual high-confidence clusters, was not affected in the same way — its R² rose modestly from 0.783 to 0.807. The post-cleanup result is the more reliable number. If asked at panel: the pre-cleanup XGBoost figure should not be cited as a stable performance estimate.

## Decision 24: Repeated-CV Retuning Confirms Baseline Random Forest Retention

> Date: 2026-05-06

**Status**: Implemented

**Problem**: The first tuning pass recorded under Decision 21 was run on a historical pre-cleanup sample and used a simpler 5-fold / R2-first search. After Decision 22 and Decision 23 changed the canonical modeling sample and the production winner, the project still needed a manuscript-grade retuning check on the current 1,491-row open-market sample before treating the deployed Random Forest as settled.

**Decision**: Rewrite `tune_models.py` to mirror the current `run_models.py` preprocessing contract, score all four existing `.pkl` artifacts on the current split, run a repeated-CV RMSE-first retuning pass for Random Forest and XGBoost, refit OLS as a benchmark, save tuning diagnostics, and keep the deployed model on the candidate with the best held-out RMSE among models within 0.02 R2 of the best competitor.

**Results from `tune_models.py` (2026-05-06)**:
- Existing artifact check on the current split:
  - RF baseline: R2=0.8069, MAPE=59.28%, MAE=4,950,161, RMSE=27,448,003
  - RF tuned (stale): R2=0.4569, MAPE=52.34%, MAE=6,020,771, RMSE=46,028,830
  - XGBoost baseline: R2=0.4915, MAPE=60.14%, MAE=6,322,294, RMSE=44,538,841
  - XGBoost tuned (stale): R2=0.4394, MAPE=71.34%, MAE=6,613,760, RMSE=46,767,297
- Repeated-CV retuning outputs:
  - RF tuned: best params = `n_estimators=300`, `min_samples_split=2`, `min_samples_leaf=1`, `max_features=0.5`, `max_depth=None`; test R2=0.4569, MAPE=52.34%, MAE=6,020,771, RMSE=46,028,830
  - XGBoost tuned: best params = `subsample=0.9`, `n_estimators=200`, `min_child_weight=5`, `max_depth=7`, `learning_rate=0.07`, `colsample_bytree=0.8`; test R2=0.5569, MAPE=58.93%, MAE=6,064,612, RMSE=41,578,638
- OLS benchmark: R2=0.0827, MAPE=201.63%, MAE=9,817,411, RMSE=59,820,880
- Final deployment selection: RF baseline retained (`Models/rf_model.pkl`)

**Rationale**:
- The post-cleanup baseline Random Forest remains the only candidate near the top R2 band and still has by far the best held-out RMSE.
- XGBoost tuning improved materially over the current XGBoost baseline, but it still did not approach the Random Forest baseline on RMSE or R2.
- This confirms that the current app deployment on baseline RF is not an artifact of stale tuning or an incomplete search space.

**Implementation (done)**:
- `tune_models.py` rewritten around the current post-cleanup data contract
- `Models/rf_tuned.pkl`, `Models/xgb_tuned.pkl`, `Models/rf_cv_results.csv`, `Models/xgb_cv_results.csv`, and `Models/model_comparison_final.csv` regenerated
- Six regression tuning plots saved under `EDA/`
- Streamlit config/homepage rechecked by the script; deployment remained on `Models/rf_model.pkl`

**Chapter 3 note**: If tuning is discussed, present this as a confirmation pass rather than as evidence that a tuned model necessarily dominates a baseline. The defensible conclusion on the cleaned open-market sample is that baseline Random Forest remains the deployed model after repeated-CV retuning and held-out comparison.

## Decision 25: RF Baseline-Centered Confirmation Search Still Retains Baseline Random Forest

> Date: 2026-05-06

**Status**: Implemented

**Problem**: After Decision 24, the retained production model was still the untuned Random Forest from `run_models.py`, but the first RF tuning grid in `tune_models.py` had not actually searched the deployed baseline neighborhood. The deployed RF baseline uses the sklearn default `max_features=1.0`, while the earlier RF search only tested `max_features` values up to `0.5`. That left a defensibility gap: the thesis could not claim a fair RF confirmation pass if the search excluded the incumbent model regime.

**Decision**: Narrow the RF search to a true baseline-centered confirmation grid and rerun `tune_models.py` on the same post-cleanup 1,491-row open-market sample. The revised RF grid used `n_estimators = [200, 300, 400]`, `max_features = [0.8, 0.9, 1.0]`, `max_depth = [None, 20]`, `min_samples_leaf = [1, 2]`, and `min_samples_split = [2, 4]`, evaluated with 5x3 repeated CV and RMSE-first refitting. XGBoost and OLS were rerun in the same script so the final comparison artifacts remained internally consistent.

**Results from the RF confirmation rerun (2026-05-06)**:
- Existing artifact check on the current split:
  - RF baseline: R2=0.8069, MAPE=59.28%, MAE=4,950,161, RMSE=27,448,003
  - RF tuned (pre-rerun artifact): R2=0.6798, MAPE=53.00%, MAE=5,082,061, RMSE=35,343,389
  - XGBoost baseline: R2=0.4915, MAPE=60.14%, MAE=6,322,294, RMSE=44,538,841
  - XGBoost tuned: R2=0.5569, MAPE=58.93%, MAE=6,064,612, RMSE=41,578,638
- RF baseline-centered confirmation search:
  - Best params = `max_depth=None`, `max_features=0.8`, `min_samples_leaf=1`, `min_samples_split=2`, `n_estimators=400`
  - Best CV RMSE on the log target = 0.6687
  - Held-out RF tuned metrics after refit: R2=0.6798, MAPE=53.00%, MAE=5,082,061, RMSE=35,343,389
- XGBoost tuned metrics after the same rerun: R2=0.5569, MAPE=58.93%, MAE=6,064,612, RMSE=41,578,638
- OLS benchmark: R2=0.0827, MAPE=201.63%, MAE=9,817,411, RMSE=59,820,880
- Final deployment selection: RF baseline retained (`Models/rf_model.pkl`)

**Rationale**:
- The narrower RF search materially improved tuned RF over the earlier weak `max_features=0.5` regime, but it still did not beat the deployed RF baseline on the held-out test set.
- Relative to RF baseline, the best baseline-centered tuned RF remained worse by about PHP 7.90M in RMSE (35.34M vs 27.45M) and by 0.127 in R2 (0.6798 vs 0.8069).
- This closes the methodological gap identified after Decision 24: the deployed RF baseline was not retained by default or by an unfair grid omission. It remained the winner even after the search was explicitly centered on its own parameter neighborhood.

**Implementation (done)**:
- `tune_models.py` RF search switched from the earlier broad random search to a baseline-centered RF confirmation grid via `GridSearchCV`
- `Models/rf_tuned.pkl`, `Models/rf_cv_results.csv`, and `Models/model_comparison_final.csv` regenerated from the confirmation rerun
- Existing deployment config remained on `Models/rf_model.pkl`; no Streamlit model switch was triggered

**Chapter 3/4 note**: The defensible manuscript interpretation is that hyperparameter tuning was used as a confirmation exercise rather than as an assumption that a more complex model must dominate. Even when the RF search was narrowed around the incumbent baseline regime, the baseline Random Forest still delivered the strongest held-out market-value prediction on the cleaned 1,491-row open-market sample.

---

## Decision 26: ABT Final Cleanup and Restriction to Open Market

> Date: 2026-05-14
> Script: `thesis_main/Scripts/cleanup_abt_final.py`

**Status**: Implemented — `abt_clean.csv` overwritten

**Context**: Post-redefense remediation. Advisor flagged high variability in the global model driven in part by mixed market segments and residual data quality issues in the ABT. The ABT was cleaned in place and restricted to open_market only, making it the canonical single-segment training file going forward.

**Four fixes applied (in order):**

1. **Drop non-open_market rows** — Removed all bank_ropa (428 rows: BPI, Metrobank, BoC, Landbank, China Bank Savings) and floor_price rows (BDO, PagIBIG). These represent Liquidation Value and administered floor prices respectively under IVS 104, which are definitionally incompatible with the open-market valuation objective (see Decision 17 for the full literature basis). Keeping them in the ABT served no further purpose after the modeling filter was already applied in `run_models.py`. Removed: 428 rows.

2. **Drop property ID 1967** (extended from Decision 10) — "House For Sale in Banilad", Cebu City, Lamudi listing. Floor area = 14 sqm, total price = PHP 200,000,000 → price_per_sqm = PHP 14,285,714. Physically impossible for a residential property. Almost certainly a data entry error (missing zeros in area or decimal error in price). The original Decision 10 dropped three rows by row index; this row was not caught at the time. Removed: 1 row.

3. **Drop commercial lot contamination** — 15 rows where `property_type == "Vacant Lot"` AND `property_name` contains "Commercial" (case-insensitive). These are commercial-grade land listings (PHP 200K–408K/sqm) that passed the original residential scrape filter due to Lamudi's category overlap. They are not residential properties and should not be in a residential valuation model. Note: property IDs 468 and 714 from the original Decision 10 implausible-row list were also in this set and thus removed here. Removed: 15 rows.

4. **Reclassify misclassified penthouse units** — Property IDs 707 and 386, both titled "Penthouse For Sale in Punta Engaño", Lapu-Lapu City, labeled `Single Detached`. These are penthouse units in a building (Punta Engaño is a condo/resort complex on Mactan Island), not standalone houses. Reclassified to `Condominium`. Rows affected: 2.

**Final ABT state after cleanup:**

| Metric | Value |
|---|---|
| Total rows | 1,603 |
| Columns | 50 (unchanged) |
| market_segment | open_market only |
| Condominium | 753 |
| House and Lot | 363 |
| Single Detached | 219 |
| Vacant Lot | 218 |
| Townhouse | 48 |
| Apartment | 2 |

**Script is idempotent**: rerunning on the already-cleaned ABT reports zero changes for each fix.

**Chapter 3 note**: §3.5 (data preparation) should note that the ABT was restricted to open-market listings in accordance with the IVS 104 Market Value definition (Decision 17), and that a final data integrity pass removed one additional implausible-price row (14 sqm "house" at PHP 200M), 15 commercial lot listings that passed the original residential scrape filter, and reclassified 2 penthouse units mislabeled as Single Detached.

---

## Decision 27: Stratified Modeling — Three Property-Type Strata

> Date: 2026-05-14

**Status**: Design confirmed by EDA — implementation pending (next phase)

**Context**: Advisor post-redefense feedback: single global model on mixed property types creates artificial variance the 1,491-row dataset cannot resolve. EDA confirmed the core problem.

**EDA evidence (from `eda_stratified.py` — 2026-05-14):**

| Stratum | Rows | Median PHP/sqm | CV |
|---|---|---|---|
| Condominium | 706 | 175,651 | 0.44 |
| Vacant Lot | 217 | 30,450 | 1.28 |
| Houses (SD + H&L + TH + Apt) | 568 | 78,775 | 0.68* |

*After removing property 1967 (CV was 5.04 with it in). Condominium median is 5.8× the Vacant Lot median — these are structurally different markets with different price drivers. A single model treats them as one distribution, which inflates the variance the model must explain.

**Correlation structure differs by stratum (Spearman ρ with price_per_sqm):**
- Condominium: `area_sqm` and `floor_area_sqm` are top negative drivers (compact units = higher PHP/sqm). `mcrai_recreation` and `bir_zonal_rr_median` are top positive drivers.
- Vacant Lot: `bir_zonal_rr_median` dominates as the strongest positive signal. CBD distances all negative. Structural features (bedrooms, bathrooms) irrelevant.
- Houses: Similar to Lots — `bir_zonal_rr_median` leads. MCRAI accessibility features broadly positive. Structural features (bedrooms, bathrooms) present and relevant.

Condominiums have a fundamentally different feature structure from Lots and Houses, confirming they warrant a separate stratum. Lots and Houses share a similar correlation profile but differ enough in feature availability (lots lack floor_area and bedrooms) and price level to remain separate strata.

**Stratum definitions:**

| Stratum | property_type values |
|---|---|
| Condominium | `Condominium` |
| Vacant Lot | `Vacant Lot` |
| Houses | `Single Detached`, `House and Lot`, `Townhouse`, `Apartment` |

All three strata are viable for tree model fitting (>150 rows each, all 6 LGUs represented in each stratum).

**Literature basis**: Droes, Hoesli & Bourassa (2019) — stratified models improved R² from 0.637 to 0.782 vs. pooled for different property classes. Usman et al. (2020, Malaysia) — stratification improved fit by 7%, reduced error by >10%. These are already cited in Decision 17 for the market segment argument; the same logic applies here to property type.

**Implementation (pending)**: New script `thesis_main/Scripts/run_models_stratified.py` — separate OLS → RF → XGBoost → SHAP pipeline per stratum. Feature sets differ by stratum (see implementation plan in `/Users/nicoestreba/.claude/plans/wise-jumping-trinket.md`).

**Chapter 3 note**: §3.3 (scope) should add a paragraph stating that the modeling pipeline uses property-type stratification. Cite Droes et al. (2019) and Usman et al. (2020).

---

## Project Note: LGU Boundary Polygons Fetched (2026-05-14)

> Script: `thesis_main/Scripts/fetch_lgu_boundaries.py`
> Output: `thesis_main/Data/GIS/lgu_boundaries.geojson`

Administrative boundary polygons for all 6 training LGUs fetched from Geoboundaries ADM3 full-resolution GeoJSON. Source: https://www.geoboundaries.org/ — CC-BY license, Year 2024.

| LGU | Geometry | Approx. bbox |
|---|---|---|
| Cebu City | MultiPolygon | lat [10.258, 10.493] lon [123.770, 123.927] |
| Mandaue City | Polygon | lat [10.311, 10.390] lon [123.913, 123.976] |
| Lapu-Lapu City | MultiPolygon | lat [10.202, 10.334] lon [123.915, 124.179] |
| Talisay City | Polygon | lat [10.234, 10.338] lon [123.778, 123.872] |
| Minglanilla | Polygon | lat [10.230, 10.328] lon [123.734, 123.819] |
| Consolacion | Polygon | lat [10.348, 10.462] lon [123.922, 123.998] |

**Point-in-polygon check against ABT (1,603 rows):** Cebu City matched perfectly (478/478). Five other LGUs had minor discrepancies of 1–15 rows. 24 rows (1.5%) were unmatched — all are coastal/border properties with geocoding precision issues (several snap to lat=10.266182, lon=123.997295, a known Lapu-Lapu snap point). These are not geocoding errors requiring correction; they reflect polygon boundary vs. point coordinate resolution at the coast.

**Use**: Available for POI spatial validation and QGIS map layers. The simplified polygons are sufficient for spatial joins; they are not the authoritative legal boundary.

---

## Decision 28: MCRAI Category Reduction — Finance Retired, Hospitals Added, Health Split (2026-05-15)

> Literature basis: Phase 3 MCRAI literature research — `thesis_main/reference/mcrai_lit_phase3.md`
> Status: Decided — implement by rerunning `compute_hansen_scores.py` (9 active categories)

**Context**: Prior to recomputing Hansen scores (required because the spatial filter in `filter_to_lgu_scope.py` changed both the ABT and all POI files), a literature review was conducted to validate whether all 9 MCRAI categories are defensible before a new compute run. One category was retired, one new category was added, and one existing category was refined.

---

### Category-by-Category Decisions

| Category | Decision | Literature basis |
|---|---|---|
| transport | **Retain** | Agosto (2017) Cebu: #1 of 31 determinants. Moosavi et al. (2021) Bangkok: strongest driver. South Tangerang (2024): KRL commuter rail significant. Hangzhou (2022): becomes more prominent over time. Universally the top signal in SE Asian residential hedonic studies. |
| education | **Retain** | Yao et al. (2017) Beijing: positive and significant. Hangzhou (2022): second-strongest signal over time. South Tangerang (2024): secondary schools significant (universities not). Agosto (2017) Cebu: in top determinant cluster. |
| recreation | **Retain** | Agosto (2017) Cebu: livability group #2. Moosavi et al. (2021) Bangkok: strong for condos. Yao et al. (2017) Beijing: positive and significant. South Tangerang (2024): public parks significant. Rey-Blanco et al. (2023): recreation category retained in optimal accessibility composite. |
| grocery | **Retain** | Standard essential-goods access proxy in residential accessibility literature. Positive in Bangkok (Moosavi 2021). Alvarez et al. (2021) OHANA Philippines framework uses food access. Not individually tested in every study, but no study reviewed excludes daily-goods access from a residential amenity composite. |
| health (primary_care) | **Retain — redefined as primary care only** | `health.csv` (143 rows after spatial filter) now contains only clinics, dentists, and GP doctors — no hospitals. Peng & Chiang (2015) Taipei: hospital proximity has a Goldilocks non-linear effect (0–500m disamenity, 500m+ amenity). FLOOR_KM=0.5 in the Hansen formula partially handles the disamenity band by preventing division-by-zero and downweighting extreme proximity. Retaining primary care as a separate category allows the model to capture local daily-care access distinct from tertiary hospital accessibility. |
| hospitals | **Add (new category, 3.0km radius)** | New POI file `hospitals.csv` (42 rows, all LGU-filtered) fetched from OSM Overpass API. Li et al. (2022) Fuzhou: Grade-A tertiary hospitals within 1,000m show +10.7% price premium; effect depends on grade and interaction with transit. Wang & Gao (2014, cited in Li et al.): +7.5% premium for high-grade hospital within 1,000m. Peng & Chiang (2015): Goldilocks effect — FLOOR_KM=0.5 handles the 0–500m disamenity band. 3.0km radius appropriate for regional hospital catchment. |
| finance | **Retire entirely** | No SE Asian hedonic study reviewed uses banking/ATM proximity as a standalone residential amenity category. Yao et al. (2017) Beijing, Moosavi et al. (2021) Bangkok, South Tangerang (2024), Agosto (2017) Cebu, and OHANA Philippines (Alvarez et al. 2021) — none include finance/banking as a distinct POI category. Finance POIs (bank branches, ATMs) proxy urban commercial density and economic activity, a signal already partially captured by CBD distance features (`dist_cebu_business_park_m`, `dist_mandaue_cbd_m`, etc.) in the model. Including it adds collinear noise without a defensible behavioral interpretation (the access utility a residential buyer derives from bank proximity is not separable from general commercial proximity). **`finance.csv` (457 rows) and the `mcrai_finance` column are retired from all further modeling.** |
| security | **Retain as individual model feature only** | Already excluded from `mcrai_composite` (Decision 20) — negative OLS coefficient explained by spatial sorting (Tiebout 1956; Bayer & McMillan 2012: security infrastructure is deployed more densely in lower-income neighborhoods, creating reverse causality). No SE Asian study reviewed uses security as a positive standalone amenity category. Retained in the Hansen compute and feature matrix because the directional signal (even if negative) is real and informative for the tree models in the stratified pipeline. Not included in composite. |
| tourism | **Retain as individual model feature only** | Already excluded from `mcrai_composite` (Decision 20) — negative OLS coefficient reflects Lapu-Lapu city composition effect + disamenity spillover from high-traffic tourist zones. Not a standard residential amenity category in any study reviewed. Retained in the compute script and feature matrix for the same reason as security — directional signal captured by RF/XGBoost. Not included in composite. |
| retail_density | **Retain as individual model feature only** | Already excluded from `mcrai_composite` (Decision 20) — South Tangerang (2024): shopping malls insignificant. Yang et al. (2016) Seoul: inverted-U threshold effect (commercial density raises values then depresses them via noise/crowding). Retained in the compute script and feature matrix. Not included in composite. |

---

### Net Change to MCRAI Category Set

| | Old (9 categories) | New (9 categories) |
|---|---|---|
| Composite-eligible | education, grocery, recreation, transport | education, grocery, recreation, transport (unchanged, Decision 20) |
| Individual-only | health, finance, security, tourism, retail_density | health (primary_care), hospitals (new), security, tourism, retail_density |
| Retired | — | finance |

Finance is the only category removed. Hospitals is the only category added. Health is redefined (primary care only — no hospitals in the file). Net count stays at 9.

---

### Implementation

1. **`compute_hansen_scores.py`** — already updated (hospitals at 3.0km added, finance still present). Remove `finance` from `amenity_categories` list and from `CATEGORY_RADII_KM`. The `mcrai_composite` weights (Decision 20: education 0.401, grocery 0.310, recreation 0.199, transport 0.102) are unchanged.
2. **`filter_to_lgu_scope.py`** — remove `finance.csv` from `AMENITY_FILES`.
3. After these edits, run `compute_hansen_scores.py` to recompute all 9 `mcrai_*` columns in `abt_clean.csv`.
4. After recompute, recheck strata row counts (Condo, Lot, Houses) — stale since spatial filter dropped 24 rows.

---

### Chapter 3 note

§3.4.1 (MCRAI categories) should document the final 9-category set with the literature basis for each retained category. State explicitly that finance was excluded because no SE Asian revealed-preference property valuation study uses banking/ATM proximity as a standalone residential amenity category, and that the signal overlaps with CBD distance features already in the model. Note the health split into primary_care (2.0km) and hospitals (3.0km) and cite Peng & Chiang (2015) for the non-linearity rationale and the FLOOR_KM=0.5 disamenity handling.

**Key citations for §3.4.1:** Agosto (2017) Cebu; Moosavi et al. (2021) Bangkok; Yao et al. (2017) Beijing; South Tangerang HPM (2024); Hangzhou (2022); Peng & Chiang (2015) Taipei; Li et al. (2022) Fuzhou; Alvarez et al. (2021) OHANA Philippines; Rey-Blanco et al. (2023).


---

## Decision 29: Replace MCRAI Transport with Network Distance to Trunk and Primary Roads (2026-05-22)

> Literature basis: Wang et al. (2022) transportation network centrality + housing price; Lieske et al. (2021) hedonic transport infrastructure; standard urban hedonic practice on distance-to-classified-road.
> Status: Decided — implementation pending (`compute_road_distances.py` to be written; `compute_hansen_scores.py` to be updated)

**Context**: `transport.csv` contains 2,610 OSM highway WAY midpoints (`out center`) drawn from `highway in {trunk, primary, secondary, tertiary}`. The current `mcrai_transport` Hansen score computes 1/d² accessibility against this point set. Three problems with this operationalization:

1. **Equal weighting across road tiers.** A tertiary residential street midpoint counts the same as a trunk-road midpoint. Jeepney corridors in Metro Cebu run on primary and secondary roads — not tertiary residential streets. Hansen-of-midpoints over-counts tertiary density and dilutes the actual corridor signal.
2. **Methodological circularity.** Network distance is computed *to a point that already lies on the network*. The Hansen denominator becomes a function of how finely OSM segmented the road, not of how far the property is from a usable transport corridor.
3. **Discrete artifact in the output.** Because midpoints are dense and roughly equally spaced along each road, the resulting `mcrai_transport` values cluster around a small number of discrete levels — visible in the ABT.

**Decision**: Retire `mcrai_transport` Hansen-of-midpoints. Replace with two direct distance features:

- `dist_to_trunk_road_m` — Dijkstra shortest-path network distance from each property's snapped origin node to the nearest node lying on a `highway in {trunk, trunk_link}` edge.
- `dist_to_primary_road_m` — same, against `highway in {primary, primary_link}` edges.

Computed on the osmnx drivable road graph for the 6-LGU bbox, using `networkx.shortest_path_length(G, orig, dest, weight='length')` (Dijkstra over edge length in meters). Haversine fallback flag retained for unreachable nodes, consistent with the CBD distance script.

**Why trunk + primary specifically:**
- Trunk roads in Metro Cebu = Cebu South Coastal Road, Cebu North Road, Mactan-Cebu bridges. Regional arterials.
- Primary roads = Osmeña Boulevard, Colon Street, A.S. Fortuna, M.J. Cuenco — the main jeepney spine routes.
- Together they capture the actual transit-bearing corridor structure. Secondary and tertiary roads are captured indirectly through CBD network distance, which already passes through the same graph.

**Literature basis:**
- Wang et al. (2022) "Does transportation network centrality determine housing price?" — closeness centrality on the road graph outperforms simple CBD distance; XGBoost + SHAP framework. We adopt the simpler classified-road-distance variant as the panel-defensible operationalization. Closeness centrality is retained as a future enhancement if model gains plateau.
- Lieske et al. (2021) — hedonic studies should represent transport infrastructure via direct proximity-to-corridor measures, not POI midpoint density.
- Agosto (2017) Cebu — accessibility to public transportation is the #1 determinant of land value across 31 factors; the operationalization must match how Cebu residents actually access transit (via jeepney corridors on primary/secondary roads).

**Composite weight handling**: Renormalize the remaining three composite-eligible categories (Decision 20 weights, transport removed and dropped):

| Category | Old weight | New weight (renormalized) |
|---|---|---|
| education | 0.401 | 0.447 |
| grocery | 0.310 | 0.345 |
| recreation | 0.199 | 0.222 |
| transport | 0.102 | retired |

New `mcrai_composite = 0.447·education + 0.345·grocery + 0.222·recreation`. Sum = 1.000 (rounding-adjusted to exactly 1.0 in implementation).

**Security, tourism, retail_density** — remain retained as individual model features outside the composite (Decision 20 + Decision 28 reaffirmed). The model determines whether their directional signal is informative; we do not pre-judge by dropping them.

**Implementation**:
1. Write `thesis_main/Scripts/compute_road_distances.py` — loads cached osmnx drivable graph for the 6-LGU bbox, filters edges by `highway` tag, computes Dijkstra network distance from each ABT row's snapped origin node to nearest trunk/primary node, writes `dist_to_trunk_road_m` and `dist_to_primary_road_m` to `abt_clean.csv`.
2. Update `compute_hansen_scores.py`: remove `transport` from `CATEGORY_RADII_KM` and `amenity_categories`. Drop `mcrai_transport` column on next compute. Renormalize composite weights (education 0.447, grocery 0.345, recreation 0.222).
3. Update `filter_to_lgu_scope.py`: keep `transport.csv` in `AMENITY_FILES` (still used to populate the road graph if needed, or retire it from the spatial filter once the road graph is fully sourced from osmnx — TBD on first run).
4. After both scripts run, ABT will have: 8 `mcrai_*` columns (transport removed), 2 new `dist_to_*_road_m` columns, renormalized `mcrai_composite`.

**Chapter 3 note**: §3.4.1 — replace the paragraph describing transport-as-Hansen with a paragraph stating that transport accessibility is operationalized as two separate network distance features (`dist_to_trunk_road_m`, `dist_to_primary_road_m`) computed via Dijkstra shortest path on the osmnx drivable road graph. Cite Wang et al. (2022), Lieske et al. (2021), and Agosto (2017). Note that this replaces an earlier midpoint-based Hansen formulation which was retired due to road-tier conflation and methodological circularity.

**Next decision number: 30.**


---

## Decision 30: MCRAI Radii Recalibration — Education and Hospitals Widened (2026-05-22)

> Literature basis: OHANA Philippine framework (Alvarez et al. 2021); Philippine learner-distance survey (Cabanog & Esteves 2024, scimatic.org); Hospital catchment area methodology (Hu et al. 2022, PMC); Li et al. (2022) Fuzhou hospital-grade hedonic; Yao et al. (2017) Beijing POI hedonic.
> Status: Decided — radii updated in `compute_hansen_scores.py`; rerun pending.

**Context**: The category-specific radii in MCRAI (Decision 18, refined in Decision 28) were originally set on local-daily-access assumptions — implicitly importing a walkability planning standard (school = 800m, hospital = 3.0km). In a Metro Cebu transit context, where jeepneys are the dominant mode of school and hospital travel and walking shares are below typical Western/Chinese-dense-city baselines, two of these radii were misaligned with how Cebu households actually access these amenities.

**Trigger**: User raised the question during 2026-05-22 review: "I don't think the people in Cebu walk to school. They usually have carpools or most of them ride the jeepney from across towns so I'm not sure if 800 meters is — I think it's too narrow." Literature review followed before any change.

---

### What the Literature Shows

**OHANA (Alvarez et al. 2021) — the only published Philippine accessibility framework using Hansen gravity over OSM data:**
- β = 2.0 (matches MCRAI implementation)
- Self-distance floor = 0.5 km (matches MCRAI FLOOR_KM)
- **Single 14.2 km maximum study radius applied uniformly across all categories** — no per-category radii at all.
- Explicitly notes great-circle distance and constant travel mode as limitations.
- Implication: our category-specific radii (0.8–3.0 km) are *narrower* than the Philippine published benchmark, not wider. Where we tightened on local-access reasoning, that tightening must be defensible against the broader Philippine reference radius.

**Philippine learner-distance evidence:**
- Cabanog & Esteves (2024) — large Philippine learner survey: median home-to-school distance is **3–5 km**, with walking as modal share but jeepney/tricycle as the realistic mode for >800m commutes. The 800 m walking radius captures only the immediate neighborhood, not how Cebu families actually choose schools.

**Comparable Chinese POI hedonic studies:**
- Yao et al. (2017) Beijing — kindergarten/primary school proximity at 500 m walking radius, in a city with substantially higher walkability infrastructure than Metro Cebu.
- Wen et al. (2022) Hangzhou — education accessibility at 1–2 km.
- These ranges import a walkability standard that does not transfer cleanly to a jeepney-dependent city.

**Hospital catchment standards:**
- Hu et al. (2022, PMC9235278) and standard hospital catchment methodology: 5 km, 10 km, and 15 km are the documented tiers for general hospital catchment analysis.
- Li et al. (2022) Fuzhou: Grade-A tertiary hospital premium peaks within 1 km but persists out to ~2 km. Not a hard outer cutoff — the analysis extends several km.
- Peng & Chiang (2015) Taipei: disamenity-to-amenity transition at 500m–1 km, with positive accessibility well beyond.
- Metro Cebu reality: 42 hospitals across the 6 LGUs. A 3 km radius leaves 22% of properties (345 of 1,579) with zero hospital accessibility — partly real, partly a radius artifact.

---

### Decision

| Category | Old radius | New radius | Basis |
|---|---|---|---|
| education | 0.8 km | **2.5 km** | Jeepney-mode-corrected school catchment. Midway between Beijing 500 m walking standard and OHANA's blanket 14.2 km. Aligns with Philippine survey-median home-to-school distance (3–5 km) while preserving local-access interpretation (a school still has to be reachable, not just exist in the region). |
| hospitals | 3.0 km | **5.0 km** | Standard hospital catchment-area first tier. Tertiary-care amenity, regional draw. Reduces zero-rate artifact (currently 22%) without inflating to a citywide composite. Preserves the Peng & Chiang (2015) disamenity-band logic via FLOOR_KM=0.5. |

**All other radii unchanged.**

| Category | Radius | Reason for no change |
|---|---|---|
| health (primary care) | 2.0 km | Clinics, dentists, pharmacies — local jeepney/walk amenity. Matches Yao Beijing primary-care range. |
| grocery | 2.0 km | Daily essentials. Standard SE Asian range. |
| recreation | 1.5 km | Neighborhood parks. Matches Yao 2017 + Hangzhou 2022. |
| security | 2.0 km | Individual feature only — not in composite. No literature reason to recalibrate. |
| tourism | 3.0 km | Individual feature only — not in composite. Lapu-Lapu composition driver. |
| retail_density | 1.0 km | Walkable retail clusters. Yang et al. (2016) inverted-U threshold is at 500m–1 km. |

---

### Implementation

1. `CATEGORY_RADII_KM` updated in `compute_hansen_scores.py` (education 2.5, hospitals 5.0; inline comment cites Decision 30).
2. Rerun `compute_hansen_scores.py` to refresh all `mcrai_*` columns. Expected effects:
   - `mcrai_education` zero rate drops materially from 33% (514 rows) toward typical 5–10%.
   - `mcrai_hospitals` zero rate drops from 22% (345 rows) toward 5–10%.
   - Composite mean shifts upward (education term is renormalized at 0.447 weight).

### Chapter 3 note

§3.4.1 — when documenting MCRAI radii, the table should list (category, radius, literature basis) and explicitly state that radii are calibrated to a Metro Cebu jeepney-dominated transit context, not a Western/Chinese walkability standard. Cite OHANA (Alvarez et al. 2021) as the Philippine framework precedent. Cite Cabanog & Esteves (2024) for the home-to-school distance basis. Cite Hu et al. (2022) for hospital catchment methodology. Cite Li et al. (2022) and Peng & Chiang (2015) for the hospital-specific non-linearity / radius logic.

### Sources

- Alvarez, F.D., Madridejos, J.M., Sarmiento, J.A., Valdez, E., & Lecaros, L.L. (2021). *A Framework for Measuring Geospatial Amenity Accessibility in the Philippines.* ISPRS Archives, XLVI-4/W6-2021, 19–26. https://isprs-archives.copernicus.org/articles/XLVI-4-W6-2021/19/2021/
- Cabanog, M. & Esteves, R. (2024). *School Distance: Its Impact to Learners' Academic Performance.* Philippine EJournals / scimatic.org. https://scimatic.org/storage/journals/11/pdfs/4879.pdf  |  https://ejournals.ph/article.php?id=32789
- Hu, Y. et al. (2022). *Algorithmic hospital catchment area estimation using label propagation.* PMC9235278. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9235278/
- Li, et al. (2022). *Do hospital and rail accessibility have a consistent influence on housing prices?* Frontiers in Environmental Science 10:1044600.
- Peng, C.W. & Chiang, Y.H. (2015). *The non-linearity of hospitals' proximity on property prices: Taipei.* Journal of Property Research 32(4): 341–361.
- Yao, Y., Zhang, J., & Li, X. (2017). *Exploring Determinants of Housing Prices in Beijing: An Enhanced Hedonic Regression with Open Access POI Data.* ISPRS International Journal of Geo-Information 6(11): 358. https://www.mdpi.com/2220-9964/6/11/358
- Wen, H. et al. (2022). *Influence of POI Accessibility on Temporal–Spatial Differentiation of Housing Prices: Hangzhou.* Journal of Urban Planning and Development 148(4). https://ascelibrary.org/doi/10.1061/%28ASCE%29UP.1943-5444.0000878

**Next decision number: 31.**


---

## Decision 31: Stratified ABT Cleanup, Unified `area_sqm`, and Per-Stratum Feature Sets (2026-05-22)

> Status: Decided — `prepare_stratified_abt.py` to be written by Copilot.
> Related decisions: Decision 1 (area_sqm fallback created), Decision 3 (floor_area imputation — now reversed), Decision 16 (floor_area_imputed excluded from feature matrix), Decision 17 (open_market filter), Decision 19 (lot_area_sqm 100% null audit), Decision 27 (stratum design), Decisions 28–30 (MCRAI restructuring).

**Context**: Before the stratified modeling pipeline (Decision 27) can be implemented, the ABT physical-feature layer needs three cleanup actions and an explicit per-stratum feature set. A 2026-05-22 audit revealed: `area_sqm` and `floor_area_sqm` are exact duplicates (identical values everywhere); `lot_area_sqm` is 100% null (Lamudi listings do not separate floor and lot area — confirmed in Decision 19 audit); `bir_zonal_rc_median` is 11–47% null per stratum; for Vacant Lots, `bedrooms` and `bathrooms` are imputed zeros (209 of 215 lots) and carry no signal; and property_id 769 (PHP 5/sqm Single Detached anomaly) is still in the ABT awaiting filter.

A separate concern raised in advisor consultation: floor area should not be imputed — instead, rows with no listed area should be dropped, because imputation distorts price-per-sqm distributions and inflates feature reliability artificially. This guidance was not previously logged in `modeling_decisions.md` and is captured here as a formal decision rule.

---

### Decision 31a — Unified `area_sqm` (no separate floor/lot columns)

Retire both `lot_area_sqm` (100% null) and `floor_area_sqm` (duplicate of `area_sqm`). Keep one column: `area_sqm`. Its meaning is stratum-dependent:

| Stratum | `area_sqm` interpretation |
|---|---|
| Condominium | Unit floor area (sqm) |
| Houses (Single Detached, House and Lot, Townhouse, Apartment) | Floor area (sqm) — primary listing area |
| Vacant Lot | Lot area (sqm) |

Chapter 3 §3.3 (variable definitions) must document this stratum-specific meaning explicitly. The `price_per_sqm` target inherits the same stratum-specific denominator interpretation.

### Decision 31b — Do not impute `area_sqm`

Rows with null `area_sqm` (77 rows: Condo 28, Houses 49 wait — actually verify: Condo 28, Lot 5, Houses 44) are dropped, not imputed. Median imputation by `property_type` + `city` (the prior Decision 3 approach) is reversed because it inflates the apparent precision of `price_per_sqm`, masks listing-quality differences across LGUs, and contributes to the same kind of segment leakage that Decision 16 found in `floor_area_imputed`. Drop is cleaner and panel-defensible.

The `floor_area_imputed` column (previously excluded from features, Decision 16) is now physically dropped from the ABT.

### Decision 31c — Drop sparse and known-bad columns

- `lot_area_sqm` — 100% null, drop.
- `floor_area_sqm` — duplicate of `area_sqm`, drop.
- `floor_area_imputed` — drop (Decision 16 excluded it from features; now retire the column).
- `bir_zonal_rc_median` — 11–47% null per stratum, drop.
- `property_id == 769` row — drop (PHP 5/sqm anomaly, flagged in project state).
- Rows with null `price_per_sqm` — drop (no model target).

### Decision 31d — Per-stratum feature sets

**Common features (all 3 strata) — 19 features:**

CBD distances (8): `dist_cebu_business_park_m`, `dist_mandaue_cbd_m`, `dist_mactan_cbd_m`, `dist_srp_m`, `dist_talisay_tabunok_m`, `dist_consolacion_m`, `dist_naga_city_m`, `dist_airport_m`.

Road corridor distances (2): `dist_to_trunk_road_m`, `dist_to_primary_road_m`.

MCRAI individual scores (8): `mcrai_education`, `mcrai_grocery`, `mcrai_health`, `mcrai_hospitals`, `mcrai_recreation`, `mcrai_security`, `mcrai_tourism`, `mcrai_retail_density`.

MCRAI composite (1): `mcrai_composite`.

BIR zonal (2): `bir_zonal_rr_median`, `bir_zonal_rr_log`, `bir_zonal_cr_median`. (3 — corrected count to 3.)

Geography flag (1): `is_mactan_island`.

Spatial lag (1, with caveat): `spatial_lag_price` — usable with the 15 null rows dropped or imputed at the stratum level.

**Stratum-specific physical features:**

| Stratum | Physical features | Total feature count |
|---|---|---|
| Condominium | `area_sqm`, `bedrooms`, `bathrooms`, `bedrooms_imputed`, `bathrooms_imputed` | 24 |
| Houses | `area_sqm`, `bedrooms`, `bathrooms`, `bedrooms_imputed`, `bathrooms_imputed` | 24 |
| Vacant Lot | `area_sqm` only (no bedrooms/bathrooms — imputed zeros, no signal) | 20 |

### Decision 31e — Output of cleanup script

`prepare_stratified_abt.py` writes three CSVs:

- `thesis_main/Data/processed/abt_condo.csv` — Condominium only, with the Condo feature set.
- `thesis_main/Data/processed/abt_houses.csv` — Single Detached + House and Lot + Townhouse + Apartment.
- `thesis_main/Data/processed/abt_lot.csv` — Vacant Lot only.

The master `abt_clean.csv` is retained as the canonical hybrid dataset (still useful for EDA, QGIS layers, and any future global-model comparator), but is not consumed directly by the modeling script.

Expected row counts post-cleanup (estimates pending script run):

| Stratum | Pre-cleanup rows | Estimated post-cleanup rows |
|---|---|---|
| Condominium | 739 | ~669 (drop 28 null-area + ~42 null-price_per_sqm) |
| Houses | 625 | ~525 (drop 44 null-area + ~56 null-price + property_id 769 if Houses) |
| Vacant Lot | 215 | ~202 (drop 5 null-area + ~8 null-price) |
| **Total** | 1,579 | **~1,396** |

### Chapter 3 note

§3.3 must document: (1) the unified `area_sqm` and its stratum-specific meaning, (2) the drop-not-impute treatment of null area, (3) the retired columns (`floor_area_sqm`, `lot_area_sqm`, `floor_area_imputed`, `bir_zonal_rc_median`), and (4) the per-stratum feature sets in tabular form.

**Next decision number: 32.**


---

## Decision 32: Stratified EDA Findings — Modeling Spec Adjustments (2026-05-23)

> Status: Decided — `eda_stratified_v2.py` re-run pending; outlier drops already applied in `prepare_stratified_abt.py`; modeling-spec changes apply to `run_models_stratified.py` (to be written next).
> Source: 2026-05-23 EDA run on `abt_condo.csv` (698 rows), `abt_houses.csv` (568 rows), `abt_lot.csv` (207 rows) — full plots in `thesis_main/EDA/plots/`.

This decision logs all seven data-integrity and modeling-spec concerns surfaced by the stratified EDA (Sections 1–8 of `eda_stratified_v2.py`). Each flag includes the finding, the action taken, and the rationale.

---

### Flag 1 — `mcrai_composite` perfect collinearity in OLS (VIF ~10^11)

**Finding:** VIF for `mcrai_composite` is 951 billion (Condo), 283 billion (Houses), 370 billion (Lot). The cause is structural: `mcrai_composite = 0.447·mcrai_education + 0.345·mcrai_grocery + 0.222·mcrai_recreation` — a deterministic linear combination of three features that are also individually in the feature set. The OLS design matrix is near-singular.

**Action:** Drop `mcrai_composite` from the **OLS feature set only**. Retain it in the RF and XGBoost feature sets — VIF is irrelevant for tree models, and the composite is a useful summary feature for SHAP interpretation.

**Rationale:** Including a deterministic linear combination of other features in OLS is a textbook violation; coefficients are not identified. Tree models do not require feature independence.

---

### Flag 2 — All 8 CBD distances mutually collinear (VIF > 5)

**Finding:** Every CBD distance feature shows VIF > 5 across all three strata. CBD nodes are spatially clustered in Metro Cebu (Giuliano & Small 1991 polycentric framework), so inter-node distances correlate strongly.

**Action:** Trim the CBD feature set to the **top 2 CBD distances per stratum (by |Spearman ρ| with `price_per_sqm`)**:

| Stratum | CBD #1 | CBD #2 |
|---|---|---|
| Condo | `dist_cebu_business_park_m` (ρ=−0.161) | `dist_talisay_tabunok_m` (ρ=−0.133) |
| Houses | `dist_cebu_business_park_m` (ρ=−0.390) | `dist_mandaue_cbd_m` (ρ=−0.265) |
| Lot | `dist_cebu_business_park_m` (ρ=−0.708) | `dist_mandaue_cbd_m` (ρ=−0.664) |

The other 6 CBD distances are dropped from the modeling feature set for that stratum. They remain in the underlying stratum CSVs (data preserved); only the `FEATURE_COLS` used by the modeling script changes.

**Rationale:** Trimming is more defensible at panel than keeping all 8 with HC3 robust errors — selection is grounded in observed stratum-specific ranking, not blanket inclusion. Cebu Business Park is the dominant anchor across all three strata, consistent with its role as the primary economic node (CLAUDE.md). The secondary node differs by stratum and reflects the stratum's locational structure: Condos respond to Talisay Tabunok (southern condo development corridor); Houses and Lot respond to Mandaue (industrial-adjacent residential expansion). Note that Condo CBD correlations are weak overall (max |ρ| = 0.161) — Condos are primarily driven by structural and accessibility features, not CBD distance per se.

**Re-evaluation required:** After trimming, re-run Spearman rankings and VIF on the trimmed feature set in the next EDA pass. If multicollinearity persists (e.g. CBP and Mandaue still correlate strongly for Houses), consider further reduction or PCA.

---

### Flag 3 — `bir_zonal_rr_median` and `bir_zonal_rr_log` are the same variable

**Finding:** Both columns have VIF > 5 because one is the log of the other.

**Action:** Drop `bir_zonal_rr_median` from the **OLS feature set**. Keep `bir_zonal_rr_log` (log-log hedonic spec is the standard form, per Decision 13). Retain both in RF/XGBoost — tree models can use either or both without harm.

**Rationale:** Log-log specification is the canonical hedonic regression form (Rosen 1974; standard urban economics practice). Carrying both raw and log is double-counting in OLS.

---

### Flag 4 — Heteroscedasticity confirmed (Breusch-Pagan significant) across all 3 strata

**Finding:** Breusch-Pagan p-value < 0.05 for Condo, Houses, and Lot. Residual variance grows with fitted values — visible in scale-location plots.

**Action:** Use **HC3 robust standard errors** for OLS inference (`statsmodels.OLS(...).fit(cov_type='HC3')`). Do not transform further (log transformation already applied to target).

**Rationale:** HC3 is the standard remedy for heteroscedasticity-consistent inference in cross-sectional hedonic models. Does not affect point estimates, only standard errors. RF and XGBoost are robust to heteroscedasticity by construction. Note as a known property of open-market listing data in Chapter 4.

---

### Flag 5 — Non-normal OLS residuals (Jarque-Bera fails for Condo + Houses)

**Finding:** Jarque-Bera p-value < 0.05 for Condo (JB stat = 154.8) and Houses (JB stat = 177.7) even after log-transform. Lot passes at α=0.05 (p=0.07).

**Action:** Accept and document. HC3 robust standard errors (Flag 4) provide valid inference under non-normality. No further transformation.

**Rationale:** Non-normal residuals are typical in hedonic models on listing data due to seller-driven asking-price noise and the heavy right tail of luxury listings. Robust inference is the accepted treatment in the literature.

---

### Flag 6 — High-influence observations (Cook's D > 4/n)

**Finding:** Condo 39 high-influence rows (after dropping the worst, property 843, Cook's D = 18.3); Houses 33; Lot 27.

**Three rows investigated by data forensics:**

| ID | Stratum | Issue | Action |
|---|---|---|---|
| 843 | Condo | 3,949 sqm "single condo unit" with 1 bed/1 bath (both imputed), PHP 50,645/sqm — bulk listing or whole-floor lot mis-categorized as a single Condominium | **Drop** (logged in `prepare_stratified_abt.py` OUTLIER_IDS) |
| 1989 | Houses | `bedrooms` field = 40 for a 40-sqm House and Lot — scraper field-shift error (area value written into bedrooms field) | **Drop** (logged in OUTLIER_IDS) |
| 1710 | Lot | 785 sqm at PHP 80,000/sqm in Talisay City — high but defensible premium subdivision (Manipis); BIR zonal is PHP 8,000/sqm (10x zonal, not impossible) | **Keep** — high Cook's D reflects feature-space sparsity at the Talisay premium tier, not a data error |

The remaining 30–35 high-influence rows per stratum are not individually inspected. Robust inference (HC3) absorbs their effect on standard errors. The Cook's D plot is retained as Chapter 4 supporting evidence.

**Rationale:** Outlier drops require row-level data forensics (bulk-listing identification, field-shift detection). Drops are applied only where the source data is demonstrably wrong, not where the row is merely unusual. Premium-tail observations are kept — they contain real signal.

---

### Flag 7 — Possible positive spatial autocorrelation in Lot stratum (Durbin-Watson = 1.42)

**Finding:** DW statistic 1.42 for Lot is below the 1.5 conventional threshold for "possible positive autocorrelation." Houses DW = 1.59 and Condo DW = 1.62 are closer to 2.0 (no strong signal).

**Action:** Retain `spatial_lag_price` in all stratum feature sets — it already absorbs some neighbor-effect signal. No additional spatial econometric model (SAR/SEM) introduced at this stage.

**Rationale:** RF and XGBoost capture non-linear spatial effects through CBD distances + spatial lag interactions without an explicit spatial autoregressive structure. SHAP outputs will reveal whether spatial features dominate. If panel review requires formal spatial econometrics, that becomes a follow-up decision.

---

### Net effect on OLS feature sets per stratum

Common OLS features (per-stratum top-2 CBDs):

| Feature group | Condo | Houses | Lot |
|---|---|---|---|
| CBD distances | CBP, Talisay Tabunok | CBP, Mandaue | CBP, Mandaue |
| Road distances | trunk, primary | trunk, primary | trunk, primary |
| MCRAI individual (8) | all 8 | all 8 | all 8 |
| `mcrai_composite` | dropped (OLS) | dropped (OLS) | dropped (OLS) |
| BIR | `bir_zonal_rr_log`, `bir_zonal_cr_median` | same | same |
| `bir_zonal_rr_median` | dropped (OLS) | dropped (OLS) | dropped (OLS) |
| Geography | `is_mactan_island` | `is_mactan_island` | `is_mactan_island` |
| Spatial lag | `spatial_lag_price` | `spatial_lag_price` | `spatial_lag_price` |
| Physical | area_sqm, bedrooms, bathrooms (+imputed flags) | same | area_sqm |

OLS feature count: Condo ~19, Houses ~19, Lot ~15.

For **RF and XGBoost**, the full feature set is retained (including `mcrai_composite`, `bir_zonal_rr_median`, and all 8 CBD distances) since tree models do not require collinearity treatment. SHAP will reveal which features carry independent information.

---

### Plot legibility — to be addressed in next EDA pass

`eda_stratified_v2.py` will be updated to add legends/annotations explaining:
- "Fitted Values" = OLS-predicted log_price on the x-axis of residuals-vs-fitted and scale-location plots
- "Theoretical Quantiles" = standard normal quantiles on the x-axis of Q-Q plots
- The dashed red line in Cook's distance plots = 4/n threshold for high-influence observation flagging
- Scale-location plot interpretation (horizontal lowess = homoscedastic; sloped = heteroscedastic)

**Next decision number: 33.**


---

## Project Note: Deferred Feature Engineering — Exploration Backlog (2026-05-23)

> Status: Deferred. To be revisited after baseline stratified models are fitted and residuals reviewed.
> Triggered by: 2026-05-23 EDA conversation — user prioritized dimensionality control over additional features before modeling. Goal is to model first with a defensible minimal feature set, then revisit additions only if residuals indicate missing signal.

**Held for later (not in current modeling spec):**

1. **Elevation per property** — SRTM 30m DEM sampled at each (lat, lon). Captures hillside premium (Busay, Maria Luisa) and low-flat penalty (coastal Mandaue). Low effort; high panel-defensibility.
2. **Flood-prone barangay flag** — PHIVOLCS HazardHunter / Project NOAH spatial join. Cebu's documented flood vulnerability is a well-known regional risk; absence of this feature is a known panel-question target.
3. **Distance to coastline** — OSM coastline geometry; haversine or osmnx network distance. Captures Mactan beachfront premium.
4. **Property age / year built** — would require re-scraping Lamudi detail pages; uncertain whether the field is reliably populated on the source.
5. **Travel time to CBD nodes** — Google Maps Distance Matrix API; captures Cebu rush-hour traffic effects not visible in straight-line or network distance.
6. **Lamudi listing-quality signals** — photo count, description length, "featured" badge; re-scrape required.
7. **Engineered transforms from existing features** — log-transformed CBD distances, nearest-CBD distance, multi-CBD Hansen-style centrality, area-per-room, distance × area interactions.

**Rule:** Add a feature only if (a) baseline residuals show missing signal in the relevant dimension, (b) the feature is supported by hedonic literature, and (c) the marginal cost (data + dimensionality + risk of overfitting) is justified for the Lot stratum where n ≈ 175.

**Currently approved for addition** (after EDA passes 2–5):
- **Full city one-hot encoding** (6 LGUs → 5 dummies + reference) — replaces `is_mactan_island`. Lets the model learn LGU-level price levels without smuggling them through proxy features.

**Currently rejected:**
- None outright; everything else is deferred pending baseline model results.

---

## Decision 33 — Drop Hard Duplicate Listings Before Writing Stratified ABTs (2026-05-25)

**Decision:** In `prepare_stratified_abt.py`, drop hard duplicate listings immediately after the existing outlier-ID removal step and before the stratum split. A hard duplicate is any set of rows with identical `latitude`, `longitude`, `area_sqm`, and `price_per_sqm`.

**Retention rule:** Sort by `property_id` ascending and keep the smallest `property_id` within each hard-duplicate group. Drop the remaining rows.

**Why:** These rows are functionally identical listings and inflate sample size, duplicate spatial signal, and overstate repeated support for the same price-location observation. This is a data-integrity correction, not a statistical outlier treatment.

**Observed scope from the integrity audit:** The hard-duplicate audit identified approximately 33 duplicate groups across the modeling-ready strata (`Condo ≈ 19`, `Houses ≈ 10`, `Lot ≈ 4`). These duplicates were concentrated in repeated Lamudi-style listings with the same size, price, and coordinates.

**Implementation note:** This decision is applied only in the stratified ABT preparation step. `abt_clean.csv` remains unchanged as the upstream master ABT; the deduplication is part of model-ready export logic.

**Chapter 3 note:** §3.5 should document that exact duplicate listings were removed using a deterministic retention rule (lowest `property_id`) based on identical coordinates, area, and `price_per_sqm`, and distinguish this from anomaly/outlier removal.

---

## Decision 34 — `log_price` Target Bug Fix, Target Redefinition, and Stratum Cleanup (2026-06-03)

> Status: Decided and implemented in `prepare_stratified_abt.py`; strata regenerated; `eda_stratified_v2.py` re-run on the corrected target. `abt_clean.csv` master left unchanged (cleanup lives in the prep step, consistent with Decision 33).
> Trigger: building `run_models_stratified.py` (Phase 4) exposed `is_ceiling_price` as the #1 SHAP feature, which led to a full data-integrity audit.

### 34a — Critical bug: inconsistent `log_price` target across scrape batches
The `log_price` target column was computed differently by the two Lamudi scrape pipelines:
- Original build (`build_abt.py`, `price_type == "ceiling"`, 625 rows): `log_price = log(total price_php)`.
- Phase C merge (`merge_phase_c.py`, `price_type == "open_market"`, 877 rows): `log_price = log(price_per_sqm)`.

The split is exact (verified ceiling↔log-total, open_market↔log-per-sqm in all strata). `price_php = price_per_sqm × area_sqm` holds for every row, so both are recoverable. This single bug explained the stratified MAPE blow-up: `is_ceiling_price` was acting as a scale-selector (mean |SHAP| ≈ 2.2), and removing it broke prediction because the target meant two different things.

### 34b — Target redefined to `log_price = log(price_per_sqm)` for all rows
Recomputed deterministically from the clean `price_per_sqm` column. Rationale: matches the CLAUDE.md target variable and the price-per-sqm deliverable; the price surface becomes a direct model output; avoids the area back-transform amplification that affected the log(total) spec. Total price in the app = prediction × `area_sqm`.

### 34c — `is_ceiling_price` / `price_type` retired as model inputs
Confirmed by the author as a leftover from the abandoned two-basis design (floor = bank/ROPA, ceiling = Lamudi). After the pivot to open-market-only (bank/ROPA dropped), every row is one basis (Lamudi asking price), so the flag is dead. Consistent with Decision 4 (provenance label, not a feature). `is_ceiling_price` column removed from the strata; `price_type` retained only as metadata (never a feature).

### 34d — `is_mactan_island` dropped from all models
Within the 6-LGU scope it is byte-for-byte identical to the `city_Lapu-Lapu City` dummy (verified 291/291, 126/126, 44/44 — perfectly collinear). Lapu-Lapu location is carried by the city dummy. Amends the Decision 32 net-effect table, which listed `is_mactan_island`. (Note: the stratified EDA VIF tables excluded binary/categorical features, so this redundancy was definitional, not VIF-detected.)

### 34e — Additional data-error rows dropped (added to `OUTLIER_IDS`)
- `621` (Condo, total ₱25k → 714/sqm; junk price field), `1292` (Condo, 2898 sqm → 966/sqm; impossible area).
- `1500`, `1928`, `1959` (Condominium-typed but whole apartment *buildings*; "bedrooms" = unit count; non-comparable to single units) — dropped per author.
- `2151` (House) — `bedrooms = 378` scraper field-shift error; row otherwise valid → bedrooms imputed to the house-stratum median and `bedrooms_imputed = 1` (row kept).

### 34f — Cleaned stratum counts
Condo **654**, Houses **558**, Lot **204** (cols 41/41/37 after `is_ceiling_price` removal).

### 34g — Refreshed OLS diagnostics on the corrected target (supersede Decision 32 Flags 5 & 7)
Re-run of `eda_stratified_v2.py`:
- Heteroscedasticity persists in all three strata (Breusch-Pagan p < 0.05) → **HC3 robust SE remains the chosen treatment** (Flag 4 stands).
- Residuals non-normal in all three (Jarque-Bera p < 0.05), including **Lot** (Decision 32 said Lot passed at p=0.07; now p=0.0005) — HC3 covers this.
- **Durbin-Watson now near 2 for all strata (Condo 1.84, Houses 1.98, Lot 1.79).** The Lot autocorrelation concern (Decision 32 Flag 7, DW=1.42) was an artifact of the corrupted target and no longer holds. `spatial_lag_price` is retained on predictive grounds (strong Spearman ρ), not as an autocorrelation remedy.
- OLS comparator R²: Condo 0.212, Houses 0.351, Lot 0.558.

### Pending
- `run_models_stratified.py` must be re-run on the cleaned strata with the corrected target (not yet done; models from the pre-fix run are invalid).
- App feature layer rebuild (Stage B+) must use `log(price_per_sqm)` target and a neighbor-lookup for `spatial_lag_price`.

**Next decision number: 35.**

---

## Decision 35 — Stratified Model Results (clean target), Best-Per-Stratum Deployment, App Rebuild, Data Expansion (2026-06-03)

> Status: Implemented. `run_models_stratified.py` written and run on the cleaned strata; app rebuilt to the stratified per-sqm layer; scraping + merge expansion prompts issued (execution pending).

### 35a — Stratified model results (held-out 80/20, random_state=42), target = log(price_per_sqm)
| Stratum | n_test | Deployed | MAPE | Median APE | R²(per-sqm) | R²(total) |
|---|---|---|---|---|---|---|
| Condominium | 131 | Random Forest | 32.8% | 13.9% | 0.535 | 0.767 |
| Houses | 112 | Random Forest | 31.9% | 20.3% | 0.589 | 0.771 |
| Vacant Lot | 41 | Random Forest | 54.7% | 33.6% | 0.329 | 0.486 |

OLS comparator stayed weak (Condo R²(total) −0.35, Houses 0.65, Lot 0.04), confirming the tree models. Full table in `Models/stratified/model_comparison_stratified.csv`; manifest in `deployment_manifest.json`. SHAP clean (no leakage): Condo → area/spatial_lag/recreation; Houses → distance-to-CBP #1; Lot → Mandaue/CBP distance.

### 35b — Best-per-stratum deployment rule
Deploy the best of RF/XGBoost per stratum by **lowest test MAPE** (OLS comparator only, never deployed). Result: RF for all three strata. **Open item:** for Vacant Lot, XGBoost has better R²(per-sqm) (0.41 vs 0.33) and lower MAE/RMSE but higher MAPE (58% vs 55%) — deploying XGBoost for Lot is a defensible alternative; held RF for a consistent selection rule.

### 35c — Reporting: report median APE alongside MAPE
MAPE (a mean) overstates typical error because a few large misses dominate. Median APE is far lower (Condo 14%, Houses 20%, Lot 34%) and is the honest "typical error". Within-30% rates: Condo 74%, Houses 70%, Lot 41%. Thesis/app should lead with median error. Vacant Lot remains genuinely weak (small n=204, heterogeneous land, missing land-specific features) — do not oversell at panel.

### 35d — App rebuilt to the stratified per-sqm layer
`thesis_main/app/` rewritten: routes by property_type → stratum model (`config.STRATUM_MAP`); predicts log(price_per_sqm) → exp → ×area for total. `mcrai_lookup.py` generalized to nearest-neighbour lookup of all location-derived features (9 MCRAI + 2 road distances + spatial_lag + bir_zonal_cr_median) — no osmnx graph needed at runtime. Retired from the app: `is_ceiling_price`, `is_mactan_island`, lat/lon-as-features, `mcrai_finance`, `mcrai_transport`, separate area columns. Price-surface grids regenerated from the stratum models. Verified end-to-end.

### 35e — Standing rule: never re-implement enrichment in the merge step
The log_price bug (Decision 34) originated in `merge_phase_c.py`, which re-implemented enrichment inline with stale definitions (old MCRAI categories/weights, log(price_per_sqm) vs the base build's log(total)). **Rule going forward:** the merge step appends cleaned rows only; MCRAI and road distances are always recomputed for the whole ABT via the canonical scripts (`compute_hansen_scores.py`, `compute_road_distances.py`), and `log_price = log(price_per_sqm)` everywhere. `prepare_stratified_abt.py` recomputes log_price defensively as a final safety net.

### 35f — Data expansion (pending execution)
Models are data-starved in the Vacant Lot stratum (204 rows) and Talisay City (currently unscraped). Two Copilot prompts issued: (1) extend the Lamudi scraper (add Talisay; scrape the land/lot category per LGU; add `lot_area_sqm` + `property_type_raw`); (2) merge + enrich the new rows following the 35e rule, then re-run compute_road_distances → compute_hansen_scores → prepare_stratified_abt → run_models_stratified. Goal: more lots + Talisay coverage to lift the weak stratum.

**Next decision number: 36.**

---

## Decision 36 — App/UI Direction: Dashboard Layout + Retire Precomputed Price Surface (2026-06-04)

> Status: Partially implemented. New Market Map dashboard built and running; drop-pin live-prediction interaction deferred (to be designed).

### 36a — Retire the precomputed price-surface grid as the primary map
Generating a dense grid of predicted points is not sustainable. The map now shows the **~1,416 real listings as pins**, not a synthetic surface. On-demand prediction (predict a single dropped point live) will replace the surface — the on-demand layer already exists (`build_feature_vector` + `predict` for any lat/lon). The old `1_Price_Surface.py` page is unlinked from nav (file retained); regenerated grids kept but no longer the headline view.

### 36b — Platform: Streamlit, restyled (not a custom front-end)
Keep Streamlit; reshape into a 3-panel dashboard (controls · map · insights) with custom CSS. Reuses the rebuilt model/feature layer; fastest path for the deadline. (Considered a custom HTML/React front-end — rejected as too much new stack for the thesis timeline.)

### 36c — New Market Map dashboard (`app/pages/0_Market_Map.py`)
Modeled on a bank competitor-intelligence reference layout (provided by author): left control rail (Target LGU, stratum multiselect, layer toggles, legend), center pydeck map of **real listings colored by stratum** (Condo blue / Houses green / Lot gold) + CBD nodes + LGU outline, right "Market Intelligence" panel (stat cards, stratum-composition bar, median-₱/sqm-by-LGU ranked list). Navbar updated (Home · Market Map · Property Predictor); all pages pass headless AppTest; app verified running.

### 36d — Deferred (chat later): drop-pin live prediction interaction
The map is currently a market explorer. The "click/drop-pin anywhere → predict ₱/sqm here" flow, and whether to keep any coarse heat layer, are deferred pending an explicit design discussion.

**Next decision number: 37.**

---

## Decision 37 — Playwright Scraper Subproject to Beat the Lamudi WAF (2026-06-05)

> Status: Implemented and verified end-to-end on a small sample. Full-size scrape + post-scrape filters + merge pending.

### 37a — Diagnosis: Lamudi runs a DataDome-class WAF, not an IP ban
The legacy `requests`+`curl` scrapers (`Data/webscraping-lamudi/`) cannot pass Lamudi's protection. Live evidence (2026-06-04): the first ~2–3 requests in a burst succeed, then every page returns the `window.gokuProps` JS-challenge wall — including the land/lot category, which *does* return ~30 listings on the first hit. A WAF curl-from-terminal check returned ✅ CLEAR, confirming the IP is **not** banned; the block is **rate/behavior-based and requires executing JavaScript**, which plain HTTP clients cannot do. Conclusion: a real browser (Playwright) that solves the challenge once and reuses the cookie is the fix.

### 37b — Isolated Playwright subproject: `thesis_main/playwright/`
All browser automation lives in its own folder so it also serves interactive use (open a page, screenshot) — not just batch scraping. Files: `browser.py` (`LamudiBrowser`: persistent context + `playwright-stealth`, `warm_up`, `fetch`, `screenshot`), `parse.py` (parsing ported verbatim from the legacy `scrape_properties.py`), `scrape_index.py`, `scrape_properties.py`, plus `README.md`, `requirements.txt`, `data/` (staging), `screenshots/`. Env: `playwright==1.60.0`, `playwright-stealth==2.0.3`, chromium, in the `16 Thesis/.venv`.

### 37c — Anti-WAF non-negotiables (do not regress)
One persistent browser context per run; **sequential only** (no threads — the legacy `ThreadPoolExecutor(max_workers=5)` is what tripped the burst WAF); **headed by default** (`--headless` opt-in; headless is easier for DataDome to fingerprint); human pacing 4–8s between navigations (`DELAY_RANGE`); warm up on the homepage first so the challenge resolves before scraping.

### 37d — Two distinct blocks, handled differently
The DataDome **JS challenge** (`window.gokuProps`) auto-resolves in a real browser, so `_handle_waf` reloads up to 3×. The interactive **human-verification CAPTCHA** does NOT auto-resolve — reloading only resets it into an infinite loop (hit live during the first run). `browser.py` now detects CAPTCHA markers (`captcha-delivery`, "verify you are a human", "human verification", …), stops reloading, rings the terminal bell, and **waits up to 10 min (polling every 5s) for the author to solve it by hand**, then resumes. Under `--headless` a CAPTCHA raises a clear "re-run headed" error instead of hanging.

### 37e — Implementation-agent change: Antigravity runs, Claude edits the scraper code
The 4 modules were first authored by **Google Antigravity (Gemini)** from a Claude-written prompt (a shift from the usual Copilot path). Going forward for this subproject, **Claude edits the scraper scripts directly** and the author runs them via Antigravity — removing the extra agent layer for code changes. (Scoped to the scraper; the broader Copilot-implements rule still holds elsewhere.)

### 37f — Verification on a 5-row sample
WAF beaten; 5 land listings scraped cleanly with prices, `lot_area_sqm`, coordinates (4/5), and `property_type_raw`. Talisay/Batangas ambiguity solved by targeting `https://www.lamudi.com.ph/buy/cebu/talisay-2/?search=Cebu`. Output writes to `playwright/data/lamudi_scraped.csv` only; canonical `lamudi_cebu_full.csv` untouched. `--max-pages` default raised 5 → 10 for the real run.

### 37g — Two scope filters applied AFTER scraping (not in the scraper)
The 5-row sample already surfaced scope leaks the index pages introduce: **commercial lots** (e.g., a ₱990M / 198,000 sqm commercial parcel in Liloan) and **out-of-scope municipalities** (Liloan is not one of the 6 LGUs). Decision: keep the scraper **unfiltered** (capturing everything) and apply two filters — **residential-only** and **city ∈ 6 LGUs** — downstream at the prep/merge stage, so genuinely-residential rows mislabeled "commercial" by the scraper's heuristic are not prematurely dropped. Supersedes the 35f plan that would have filtered at scrape time. Filters + merge to be built when the full land batch exists (per the 35e enrichment rule).

**Next decision number: 38.**

---

## Decision 38 — Post-Scrape Model-Improvement Plan (2026-06-05)

> Status: Plan agreed; executes after the scrape → filter → merge → re-enrichment cycle. Targets the weak Vacant Lot stratum (n=204, MAPE 54.7%).

### 38a — k-fold cross-validation for accuracy reporting: ADOPTED (reversal)
Author's initial instinct was to skip k-fold ("too few rows to chop up further"). After walking through how it works, this was **reversed — k-fold is in**. Rationale: each fold trains on k−1 folds (≈80% of the stratum) and tests on the held-out fold, so the model never trains on a tiny slice; across folds every row is tested exactly once and used for training in the rest. With the Lot stratum at n=204 a single 80/20 split rests the reported error on ~41 rows — too thin and luck-sensitive to defend at the redefense. k-fold (or repeated k-fold) averages over all rows and gives a stabler, more honest error. Final deployed model is still refit on the full stratum; k-fold is for *estimating* accuracy only. Reporting plan: keep the single held-out score and report the k-fold average alongside it — agreement is reassuring, divergence is itself worth surfacing. (Note: differs from Decisions 21/24's earlier repeated-CV *tuning* runs, which were pre-cleanup and pre-stratification; this is k-fold for honest per-stratum accuracy reporting.)

### 38b — Per-stratum hyperparameter tuning: YES
Tune RF (and XGBoost where relevant) separately within each stratum rather than with one global grid — the strata have different sizes and correlation structures (Condo area-driven; Lot/Houses BIR-zonal-dominant, per Decision 27).

### 38c — XGBoost for the Lot stratum: ON THE TABLE
Decided by the post-scrape numbers. XGBoost already showed better R²/MAE signal for Lot; revisit once the expanded land batch is merged. Best-per-stratum-by-lowest-test-MAPE deployment rule (Decision 35) still governs.

### 38d — Lot-specific features: pending new data
Hope the expanded land listings carry richer lot attributes; assess feasibility after the merge.

### 38e — Honest reporting led by median APE + AVM benchmark
**Median APE** remains the headline accuracy figure (MAPE overstates typical error). The model class is an **AVM (Automated Valuation Model)**; report against AVM/mass-appraisal conventions — candidate metrics: median APE (MdAPE), PE10/PE20 ("within-X%" hit rates), and IAAO ratio-study stats (COD, PRD/PRB) from the IAAO *Standard on AVMs* and *Standard on Ratio Studies*. **To do:** verify exact IAAO thresholds and find 2–3 comparable ML-AVM studies (ideally Philippine / SE-Asian / emerging-market) for a fair benchmark — figures must be cited from verified sources, not asserted from memory (per the citation rules).

**Next decision number: 39.**

---

## Decision 39 — 2026-06 Lamudi Batch Merge Executed + Stratified Retrain (2026-06-05)

> Status: Executed end-to-end. Master `abt_clean.csv` rebuilt 1,579 → 1,849 rows; all three stratified models retrained. Backup at `abt_clean.backup_pre_batch_2026-06.csv`.

### 39a — Geocoding the coord-less land + house rows
55 land/house scrape rows lacked coordinates; geocoded via Google Maps (`playwright/geocode_missing.py`, canonical Google geocoder, Cebu-bounds reject, address cache). All 55 filled (9 ROOFTOP, 21 GEOMETRIC_CENTER, **25 barangay-centroid APPROXIMATE**). Condos left coord-less (plentiful). Caveat for defensibility: the 25 barangay-centroid rows share coordinates within a barangay → identical road/MCRAI features; acceptable for rows that would otherwise be dropped, but note it when discussing spatial precision.

### 39b — Staging (Step A): `Scripts/stage_lamudi_batch.py`
Builds cleaned base rows from the geocoded scrape into the abt_clean schema (BIR join via canonical reverse-geocode + `join_bir_to_abt`; enrichment cols left empty). Filter funnel: 665 → coords 654 → price ∈[₱500k,₱500M] 600 → **6-LGU (city map) 560** → **residential recode 533** → **spatial cap (≤3/≈11m cell) 400** → **dedup vs ABT 275**. The spatial cap (−133) and ABT dedup (−≈125) are both legitimate: the cap mostly removed House&Lot pin-pileups (only 4/133 were coarse geocodes, 1 a lot), and the dedup removed relistings already in the ABT (URL-new ≠ property-new). Net **275** staged: House&Lot 112, Vacant Lot 104, Condo 40, Townhouse 19. BIR join 100% matched (8 nearest-neighbour imputed).

### 39c — Area-convention fix (reusable lesson)
First staging used Decision-1 fallback into a *separate* `lot_area_sqm`, which broke `prepare_stratified_abt.py`'s audit (`area_sqm == floor_area_sqm`, `lot_area_sqm` 100% null). Corrected: consolidate usable area into **`floor_area_sqm`** (floor first, lot fallback so vacant lots get lot area), keep `lot_area_sqm` null, set `area_sqm = floor_area_sqm`. Restored from backup and re-ran clean. **Future merges must follow this convention.**

### 39d — Enrichment (Step B): canonical scripts (Decision 35e)
Append → `compute_road_distances.py` (trunk/primary road) → **new `Scripts/enrich_cbd_and_lag.py`** (7 CBD-node Dijkstra distances + airport haversine for new rows; `spatial_lag_price` recomputed for **all** rows for a consistent neighbour pool — there was no standalone current script for these) → `compute_hansen_scores.py` (MCRAI) → `filter_to_lgu_scope.py` (polygon LGU filter, **dropped 5** edge rows). Final master: **1,849 rows × 51 cols**.

### 39e — Strata + retrain results (deployed = RF, best-per-stratum by lowest MAPE)
Strata: **Condo 654→687, Houses 558→674, Vacant Lot 204→301** (+48%). Added **MdAPE (median APE)** to `run_models_stratified.py` outputs + manifest (Decision 38e).

| Stratum | Old MAPE / MdAPE / R²sqm | New MAPE / MdAPE / R²sqm |
|---|---|---|
| Condominium | 32.8% / 13.9% / 0.535 | 30.67% / 15.92% / 0.599 |
| Houses | 31.9% / 20.3% / 0.589 | 30.69% / 24.27% / 0.487 |
| **Vacant Lot** | 54.7% / 33.6% / 0.329 | **58.56% / 23.34% / 0.573** |

**Lot read:** the target stratum's *typical* error (MdAPE) fell 33.6%→**23.3%** and fit R²sqm jumped 0.329→**0.573**; MAPE rose slightly because the mean is dragged by a few low-priced lots (small denominators) — exactly why MdAPE is the honest headline (Decision 38e). XGBoost-for-Lot now has the best fit (R²sqm 0.637, MAE ₱16,959/sqm) but worse MdAPE/MAPE (29.4%/60.4%), so **RF stays deployed** by the lowest-MAPE rule. Houses metrics softened slightly (more heterogeneous data); Condo improved on MAPE/R².

**Next decision number: 40.**

---

## Decision 40 — Per-Stratum Hyperparameter Tuning + k-fold CV Reporting (2026-06-05)

> Status: Plan agreed; executes the Decision 38a/38b work on the post-batch strata (Condo 687, Houses 674, Lot 301). New script `Scripts/tune_models_stratified.py`; baseline `run_models_stratified.py` and legacy global `tune_models.py` left untouched.

### 40a — New script, not a reuse of legacy `tune_models.py`
`tune_models.py` is the pre-stratification *global* tuner (total-price target, edits the old single-model app config) and conflicts with the stratified per-sqm design. It is **deprecated, not reused**. Tuning is implemented in a new `tune_models_stratified.py` that imports the feature build (`build_features`), `evaluate`, stratum config, paths, and `run_shap` from `run_models_stratified.py` so the feature matrices and metrics stay a single source of truth. Held-out split kept identical (RANDOM_STATE=42, TEST_SIZE=0.20) so tuned-vs-baseline is apples-to-apples.

### 40b — Tuning CV scorer = RMSE on the log target
Hyperparameter search optimizes `neg_root_mean_squared_error` on `log(price_per_sqm)` (numerically stable on the thin Lot stratum), **not** a custom MAPE/MdAPE scorer (noisier, overfit-prone on small n). Per-sqm MAPE/MdAPE/R² are computed *after* fitting for selection and reporting. RF tuned via `GridSearchCV` (grid reused from `tune_models.py` RF_CONFIRMATION_GRID), XGB via `RandomizedSearchCV` (n_iter=40, XGB_PARAM_DIST), both with `RepeatedKFold(5×3)` on the training split only.

### 40c — Deployment basis = k-fold mean MAPE (best of {baseline, tuned} × {RF, XGB})
Decision 38a adopted k-fold for honest reporting; selection now uses it. For each stratum, k-fold CV (RepeatedKFold 5×3 over the **full** stratum; back-transformed per-sqm metrics per fold) is run for four configs — baseline RF, tuned RF, baseline XGB, tuned XGB — and the config with the **lowest k-fold mean MAPE** deploys. Tuning therefore can only replace the baseline if it actually wins ("keep best of both"); a marginal/negative tuning gain leaves the baseline deployed. The single held-out score is still reported alongside the k-fold mean ± std (agreement reassuring, divergence flagged).

### 40d — Final deployed model refit on the full stratum
Consistent with 38a: k-fold is for *estimating* accuracy only; the winning config is refit on the entire stratum and saved to `{stratum}_model.pkl` (drop-in for the app — feature columns unchanged). Tuned references saved to `{stratum}_rf_tuned.pkl` / `{stratum}_xgb_tuned.pkl`; best params to `tuning_results_{stratum}.json`; per-config held-out + k-fold table to `kfold_cv_stratified.csv`; `deployment_manifest.json` rewritten (old one backed up) to carry tuned params, k-fold metrics, and the selection basis. SHAP regenerated on the refit deployed model.

### 40e — Known limitation logged
`build_features` median-imputes over the whole stratum before the fold split (inherited from the baseline), so k-fold carries mild impute leakage. Kept for consistency with the deployed pipeline; noted as a limitation rather than re-engineered.

**Next decision number: 41.**

---

## Decision 41 — Vacant Lot Re-solved: Artifact Diagnosis, Scope Filter, Leak-free Eval, IAAO Benchmark (2026-06-05)

> Status: Executed by Claude directly (no Antigravity — author asked Claude to do the modeling for this). Triggered by alarm over the Decision 40 Lot k-fold MAPE of 75% (±44). Scripts: `Scripts/prepare_stratified_abt.py` (filter added), `Scripts/finalize_lot_model.py` (new, authoritative Lot model). Deployed `lot_model.pkl` retrained on filtered data.

### 41a — The 75% MAPE was an artifact, not a broken model
Three stacked causes, none of which is model quality:
1. **MAPE on cheap denominators.** The raw Lot stratum spanned a **241× price/sqm range** (₱1,300–₱313,500). When a genuine cheap row (₱1,300–2,300/sqm) is predicted at a sensible area value, APE hits 1,000–1,400% and drags the mean; the ±44 std came from a few such rows landing in different folds.
2. **Non-residential / data-error rows.** The cheapest rows were development/agri parcels (e.g., 50,000 sqm @ ₱1,600; 11,000 sqm @ ₱1,300) and data errors (price < ½ the BIR zonal floor, e.g. ₱2,300/sqm where zonal = ₱29,375).
3. **Coordinate-leaky CV.** 109/301 rows shared coordinates (barangay-centroid geocodes from Decision 39a + relistings) → near-identical-feature neighbours straddled train/test folds, making ordinary k-fold both optimistic and unstable.

### 41b — Residential-scope + data-quality filter (in `prepare_stratified_abt.py`)
Applied to the Lot stratum only, each cut independently defensible (not metric-fishing): **area_sqm ∈ [80, 2000]** (residential-lot scope — PH subdivision lots are ~100–500 sqm, estate to ~1.5k; above ~2,000 sqm parcels are subdivision-scale raw/development land on a bulk-discount regime: median price/sqm collapses from ~₱51k at 600–1,000 sqm to ~₱16.5k above 5,000 sqm) **AND price_per_sqm ≥ 0.5 × bir_zonal_rr_median** (the BIR zonal is the legal valuation floor; arm's-length residential land transacts at/above it). Funnel: **301 → 255** (−44 out-of-scope by area, −2 below the zonal floor). Backup: `Data/processed/abt_lot.backup_pre_clean_2026-06.csv`. **Note:** the filter lives in the prep step so it survives data refreshes.

### 41c — Leak-free evaluation = GroupKFold on coordinate clusters
Honest accuracy uses **GroupKFold (5 folds, groups = coordinate cluster)** so shared-location rows never split across folds; metrics are pooled out-of-fold (every row predicted once). This is now the honest protocol; ordinary k-fold/held-out splits on this data are optimistic. **Cross-check (same protocol, all strata):** Condo MdAPE 20.2 / COD 36.2 / PRD 1.21; Houses 23.2 / 33.7 / 1.18; Lot 25.7 / 36.9 / 1.28 — **Lot is only modestly worse than the others, not a uniquely broken stratum.** (Earlier held-out numbers, e.g. Condo MdAPE 15.9%, were optimistic from coordinate leakage.)

### 41d — Benchmark = IAAO Standard on Ratio Studies (2013), verified
Reported against mass-appraisal/AVM convention, **not MAPE**: MdAPE, **COD**, **PRD**, PE10/PE20. Verified IAAO bands: **COD vacant land ≤ 25** (residential improved 5–15); **PRD 0.98–1.03** (>1.03 regressive). Caveat stated in the report: IAAO COD/PRD are *in-sample assessment-roll* standards on large samples; our values are *stricter out-of-sample* CV estimates on n=255. (Sources: IAAO Standard on Ratio Studies PDF; comparable predictive ML-AVM studies report MdAPE 4–10% but on large developed-market datasets with richer features — aspirational, not like-for-like.)

### 41e — Deployed Lot model + honest result
RF tuned by group-CV **MdAPE** (small grid; best = n_estimators 400, max_features 1.0, min_samples_leaf 1, max_depth None), refit on the full 255-row filtered stratum → `lot_model.pkl` + `lot_rf.pkl`. **Honest group-CV: MdAPE 25.7%, MAPE 37.8%, COD 36.9, PRD 1.28, PE10 24%, PE20 42%.** Tested and rejected as not worth the added defensibility burden: zonal-premium target (worse — Cebu BIR zonal too poorly calibrated, ratio 0.08–37×), HistGradientBoosting (worse on n=255), fold-wise linear bias calibration (MdAPE 24.7 but COD 38.3 — within noise). **Value check vs naive baselines (same group-CV):** BIR-zonal predictor MdAPE 66.7 / COD 55; city-median MdAPE 26.9 / COD 43.5; **RF MdAPE 25.7 / COD 36.9** — RF decisively beats both on uniformity and the expensive tail. Top driver: dist_to_Cebu_Business_Park (47% importance).

### 41f — Honest standing & limitation
The Lot AVM does **not** meet the strict IAAO in-sample vacant-land COD band (≤25) under honest out-of-sample CV (COD ~37, PRD ~1.28 regressive). This is a **feature/data ceiling, not a modeling failure**: vacant-land price/sqm is driven by lot-level attributes absent from the data (frontage, zoning/land classification, titled status, corner, slope, flood) and n=255 is thin. The model is defensible as the **weakest of the three strata**, reported transparently with MdAPE ~26% and PE20 ~42%, beating naive baselines. Do not claim IAAO compliance. Artifacts: `Models/stratified/lot_iaao_report.json`, manifest `strata.lot` updated with `metrics_group_cv` + `iaao_benchmark`.

### 41g — Follow-ups surfaced (not yet done)
1. Adopt GroupKFold honest reporting for Condo + Houses too (current manifest still carries optimistic ungrouped/held-out numbers for them).
2. Revisit the Decision 40 Houses switch to XGB-tuned — it won on a 0.22pp k-fold MAPE edge (noise); group-CV supports reverting to RF baseline for consistency.
3. Manuscript Ch7: report the IAAO panel + GroupKFold protocol; state the Lot feature-ceiling limitation explicitly.

**Next decision number after this point was 42.**

---

## Decision 42 — Leak-free GroupKFold Reporting + RF Deployment Across All Strata (2026-06-05)

> Status: Executed by Claude directly. Generalizes Decision 41's honest protocol from Lot to Condo + Houses. Script: `Scripts/finalize_stratified_groupcv.py` (authoritative). Rewrote `deployment_manifest.json` (backup `deployment_manifest.backup_pre_groupcv.json`); redeployed all three `{stratum}_model.pkl` as RF.

### 42a — GroupKFold is the appropriate honest test for a price surface
All strata now evaluated with **GroupKFold (5 folds, groups = coordinate cluster)**, pooled out-of-fold. Rationale beyond leakage: the deliverable is a **price surface predicting at arbitrary Metro Cebu locations** (incl. pixels with no nearby listing), so testing on held-out *locations* is the realistic test — not random holdout, which lets a near-identical same-coordinate comp sit in training. Earlier held-out numbers (e.g. Condo MdAPE 15.9%) were optimistic from coordinate leakage.

### 42b — Deploy RF for all three; Houses reverted off XGB-tuned
RF tuned per stratum by group-CV MdAPE, refit on full stratum. This **reverts the Decision 40 Houses→XGB-tuned switch** (it had won on a 0.22pp k-fold MAPE edge = noise). All three deployed = Random Forest, consistent. (XGBoost not evaluated here — env lacks xgboost; RF won/tied under honest CV in Decision 41. Re-add xgboost to retest if desired.)

### 42c — Honest leak-free results (deployed RF, GroupKFold, IAAO panel)
| Stratum | n | MdAPE | MAPE | COD | PRD | PE10 | PE20 | IAAO COD band |
|---|---|---|---|---|---|---|---|---|
| Condominium | 687 | 20.1% | 35.2% | 36.3 | 1.21 | 27% | 50% | ≤15 (improved) — above |
| Houses | 674 | 22.1% | 32.4% | 33.0 | 1.18 | 24% | 45% | ≤15 (improved) — above |
| Vacant Lot | 255 | 25.6% | 37.8% | 36.9 | 1.28 | 24% | 42% | ≤25 (vacant) — above |

### 42d — Honest standing for the whole model (not just Lot)
Under leak-free location-based CV, **all three strata sit at COD ~33–37 and PRD ~1.2 (mildly regressive) — above the strict IAAO in-sample bands**, with MdAPE 20–26% and PE20 42–50%. This is a property of the data/features + the harder (correct) test, not a Lot-specific defect; Lot is only modestly worse than Condo/Houses. Report honestly: MdAPE/PE20 as headline, COD/PRD with the in-sample-vs-out-of-sample caveat, and state that the location-based CV matches how the surface is used. Do not claim IAAO compliance. Deployed pkls: condo/houses/lot `_model.pkl` (= `_rf.pkl`), all RandomForest.

### 42e — Follow-ups
1. Reinstall `shap` + `xgboost` in the active conda env to regenerate per-stratum SHAP (beeswarms skipped this run; RF importances captured) and optionally retest XGBoost under group-CV.
2. App QA: confirm the Streamlit app still loads the redeployed RF pkls (feature counts: condo 33, houses 36, lot 29 — unchanged column sets, so drop-in).
3. Manuscript Ch7: report the GroupKFold protocol + IAAO panel table above; frame location-based CV as the surface-appropriate test.

---

## Decision 43 — EDA Workflow Audit And Plain-Language Handoff (2026-06-07)

> Status: Logged after Codex review of the EDA artifacts, current stratum CSVs, scrape logs, and Decision 42 manifest. Detailed handoff: `thesis_main/reference/eda_workflow_handoff_2026-06-07.md`.

### 43a — Current workflow is Decision 42, not the older global-model workflow
The active model source of truth is the Decision 42 workflow:

1. `prepare_stratified_abt.py`
2. `finalize_stratified_groupcv.py`
3. `Models/stratified/deployment_manifest.json`
4. deployed per-stratum Random Forest models

Older global Random Forest / total-price / random held-out split references in manuscript files, snapshots, and task logs are historical and must not be used as the current methodology.

### 43b — EDA issues have mostly been addressed, but the saved EDA run is stale
The structured EDA logic exists and covers price skew, geographic spread, feature distributions, Spearman correlations, VIF, OLS residual diagnostics, Cook's distance, MCRAI zero rates, geocoding clusters, and duplicate checks.

However, the saved structured EDA log was run on older stratum counts:

| EDA log count | Rows |
|---|---:|
| Condo | 654 |
| Houses | 558 |
| Lot | 204 |

The current stratum CSVs are:

| Current stratum CSV | Rows |
|---|---:|
| `abt_condo.csv` | 687 |
| `abt_houses.csv` | 674 |
| `abt_lot.csv` | 255 |

Therefore, the EDA should be rerun before final defense or manuscript use. The existing EDA artifacts are useful for diagnosis, but not final evidence.

### 43c — Heteroscedasticity is addressed as an OLS diagnostic issue
EDA found heteroscedasticity in OLS residuals. This is not "fixed" in the sense of making the data homoscedastic. It is accounted for by using HC3 robust standard errors in the OLS diagnostic model.

Defense framing:

> Heteroscedasticity was detected in the OLS baseline, so OLS inference uses HC3 robust standard errors. The deployed valuation model is Random Forest, not OLS; OLS is retained as a transparent diagnostic comparator.

### 43d — Collinearity is handled by separating OLS diagnostics from the deployed model
EDA found high VIF / collinearity among MCRAI, CBD distance, and related spatial features. This affects OLS coefficient stability, so OLS is not used as the final valuation engine.

Decision:

- For OLS: use a trimmed diagnostic specification and interpret cautiously.
- For Random Forest: keep correlated spatial predictors when they carry useful predictive signal, because RF is less sensitive to collinearity than OLS.
- For thesis defense: do not make coefficient-level causal claims from OLS.

Defense framing:

> Collinearity was a reason not to rely on OLS coefficients as the final model. The final workflow uses stratified Random Forest models and treats OLS as a diagnostic baseline.

### 43e — Duplicates, outliers, and coordinate leakage are addressed in the workflow
The workflow currently addresses the major data-integrity issues:

- bad/outlier property rows are dropped or repaired in `prepare_stratified_abt.py`;
- hard duplicates are dropped using identical coordinates, area, and price per sqm;
- the target is recomputed as `log(price_per_sqm)` in the stratum prep step;
- vacant lots are filtered to residential-scope lots;
- final evaluation uses GroupKFold by coordinate cluster, so same-coordinate listings do not leak across train/test folds.

This is the strongest defensibility improvement after the EDA: the current evaluation tests held-out locations rather than random rows.

### 43f — Playwright scrape added useful but limited data
The Playwright scrape was introduced because normal HTML/requests-style scraping was blocked by Lamudi's browser/JavaScript protection. The full scrape did not yield thousands of usable new model rows. The logged funnel was:

| Stage | Rows |
|---|---:|
| Scraped/listed candidates | 665 |
| With coordinates | 654 |
| Valid price range | 600 |
| Inside six target LGUs | 560 |
| Residential recode retained | 533 |
| After spatial cap | 400 |
| Net staged rows after dedup against ABT | 275 |

The main value of the batch was not just row count. It forced the workflow to fix target consistency, geocoding precision, duplicate handling, Lot filtering, and leak-free evaluation.

### 43g — Required next documentation and EDA actions
Before manuscript or defense use:

1. Rerun `eda_stratified_v2.py` on the current stratum CSVs.
2. Rerun or refresh `eda_data_integrity.py` outputs on the current ABT.
3. Save key EDA numeric outputs as CSV/JSON instead of only printed logs.
4. Add a one-page EDA defense table: issue, implication, workflow response, defense wording.
5. Update Chapters 3, 6, 7, 8, 9, and the abstract to match Decision 42 and this handoff.

---

## Decision 44 — CRISP-DM Verification Sprint: Re-anchor on the 4 RQs, Reconcile Docs↔Code, Close RQ2/RQ3/RQ4 Gaps (2026-06-13)

**Context:** Before the manuscript revision (adviser deadline Sun 2026-06-14), a full-loop CRISP-DM verification was run against the actual code. Reading Chapter 1 first revealed the pipeline had drifted from its own research questions. This decision records the verification findings and the agreed remediation.

### 44a — Docs↔code discrepancies found (and the code is the truth)

| Item | Stale doc says | Code actually does | Source |
|---|---|---|---|
| MCRAI composite weights | 4 cats incl. transport (edu 0.401 / grocery 0.310 / rec 0.199 / transport 0.102) | **3 cats: edu 0.447 / grocery 0.345 / rec 0.222** | `compute_hansen_scores.py:112-117` |
| MCRAI radii | edu 5km, health 5km, finance 3km (Decision 9) | edu **2.5km** (Dec 30), health **2.0**, hospitals **5.0** (new), grocery 2.0, security 2.0, tourism 3.0, recreation 1.5, retail 1.0; β=2.0, floor 0.5km | `compute_hansen_scores.py` |
| App manifest contract | "bug: reads old deployed_metrics" | **Reads `metrics_group_cv` correctly** (legacy fallback) — not a bug | `app/lib/predict.py:62` |
| Map tiles | "Mapbox token issue" | **CartoDB public tiles, no token** — not an issue | app pages |
| EDA artifacts | 654/558/204 | **687/674/255** (abt_clean 1,849×51) | live check |

Action: the manuscript and earlier decision text must use the **code values above**. The Decision 9 radii table and the Decision 20 4-category composite are superseded for description purposes (the staged composite is now 3 categories per Decisions 28–29 renormalisation).

### 44b — The pipeline had drifted from 3 of 4 research questions

- **RQ1 (value drivers):** served (SHAP / RF importance + EDA). OK.
- **RQ2 (best model, "lowest MAPE"):** drifted. Headline metric is now MdAPE/PE20, and `finalize_stratified_groupcv.py` only evaluates RF under GroupKFold — OLS/XGB were never run under the same leak-free protocol. `run_models_stratified.py` does run all three but only under a single random 80/20 split (leaky on shared-coordinate rows).
- **RQ3 (geospatial vs structural-only):** **gap** — no ablation existed anywhere in the code.
- **RQ4 (valuation gap size):** **gap** — `valuation_gap` is computed in staging then placed in `EXCLUDE_COLS` and dropped before modeling; never quantified, summarised, or mapped.

### 44c — Agreed remediation (rigorous options chosen by author)

- **RQ2:** fair head-to-head — OLS, RF, XGB all under the SAME GroupKFold(5) by coordinate cluster; report MdAPE/PE20/MAPE/COD/PRD. New `Scripts/answer_rq2_rq3.py` → `Models/stratified/model_comparison_groupcv.csv`. Update RQ2 wording to MdAPE. Requires `pip install xgboost` (env currently lacks it).
- **RQ3:** clean ablation — same RF, same folds, 3 nested tiers (Structural → +Admin location[city,BIR] → +Engineered geospatial[CBD,MCRAI,road,spatial_lag]). Same script → `ablation_groupcv.csv`. Uplift Tier2→Tier3 = the pure engineered-geospatial contribution.
- **RQ4:** quantify + map — `Scripts/answer_rq4.py` uses the deployed RF's leak-free out-of-fold predictions; `model_gap = pred_price_per_sqm − bir_zonal_rr_median` and `listing_gap` summarised by LGU×stratum → `valuation_gap_summary.csv` + `QGIS/data/valuation_gap.geojson`.

### 44d — "Why RF over XGBoost" (the defensible reasoning, beyond the metric)

1. Small per-stratum samples (255–687) favour bagging; boosting overfits noisy listing data without heavy regularisation.
2. XGB's only edge (Houses, 0.22pp MAPE, Decision 40) vanished under leak-free GroupKFold → noise, not signal. The RQ2 head-to-head documents this directly.
3. Fewer sensitive hyperparameters → stable optimum on a small tuning budget.
4. Deterministic, scikit-learn-only → simpler to deploy and defend (deployment env has no xgboost).

### 44e — Artifacts produced this session
- `reference/pipeline_walkthrough_2026-06-13.md` (plain-language end-to-end teach-me, RQ-mapped).
- `Manuscript/diagrams/pipeline_overview_2026-06.drawio` and `modeling_deepdive_2026-06.drawio`.
- Codex prompts for `answer_rq2_rq3.py`, `answer_rq4.py`, and the EDA rerun.
- `Manuscript/ch_correction_checklist_2026-06-13.md` (exact manuscript edits for the next loop).

**Out of scope (next sprint):** Streamlit Cloud deployment for broker testing; manuscript prose rewriting.

### 44f — RESULTS (ran 2026-06-13 in the project .venv, which DOES have xgboost/shap)

RF out-of-fold MdAPE matched the manifest exactly on all three strata (replication PASS).

**RQ2 — model head-to-head (leak-free GroupKFold, MdAPE / PE20, lower MdAPE better):**

| Stratum | OLS | Random Forest | XGBoost | Verdict |
|---|---|---|---|---|
| Condominium | 26.2% / 39% | **20.1% / 50%** | 21.4% / 47% | RF best |
| Houses | 24.3% / 42% | **22.1% / 45%** | 22.2% / 45% | RF ≈ XGB (tie) |
| Vacant Lot | 32.9% / 33% | 25.6% / 42% | **24.3% / 41%** | XGB edges MdAPE, RF wins PE20 |

**Honest reading:** tree models clearly beat OLS everywhere. **RF and XGBoost are statistically
indistinguishable** (all within ~1.3pp; differences are within sampling noise for 255–687 rows).
So RQ2's answer is NOT "RF is the most accurate" — it is "tree models beat hedonic OLS; RF and
XGB tie; **RF is deployed for parsimony, small-sample robustness, and deployment simplicity**,
not a decisive accuracy edge." Drop the earlier "env lacks xgboost" reason — the .venv has it.

**RQ3 — geospatial ablation (RF, same folds, MdAPE by tier):**

| Stratum | Structural | +Admin (city+BIR) | +Geospatial (full) | Pure geospatial uplift (Δ from +Admin) |
|---|---|---|---|---|
| Condominium | 24.3% | 24.9% | **20.4%** | **+4.5pp (clear gain)** |
| Houses | 24.8% | 21.2% | 22.0% | −0.8pp (no gain) |
| Vacant Lot | 41.8% | 25.1% | 26.2% | −1.1pp (no gain) |

**Honest reading (re-aligned 2026-06-13 — corrects an earlier too-harsh version):** RQ3 asks whether geospatial features improve over a **structural-only** model. On that test the answer is **YES for all three strata** — Structural → Full MdAPE gain: **Condo +3.9pp, Houses +2.8pp, Vacant Lot +15.7pp**. The +Admin column adds only a *decomposition* nuance: the **engineered geospatial features carry the gain for condos** (the +Admin→+Geospatial step), while for **houses and lots most of the locational signal is already in administrative location (city + BIR zonal)**. Report RQ3 as **headline yes (all strata) + decomposition**, NOT as "geospatial adds nothing for houses/lots." Coherent story: BIR zonal is a
**land**-value-per-sqm benchmark, so it is least informative for condos (vertical, many units per land
parcel) — exactly where the geospatial ML adds the most.

**RQ4 — valuation gap (market & model price_per_sqm vs BIR zonal RR, leak-free RF predictions, n=1,616):**
Market and model prices sit **far above** BIR zonal everywhere; 95–100% of listings exceed BIR in every
LGU. The model gap tracks the listing gap closely (model agrees BIR is low). **Caveat (must state):**
`bir_zonal_rr_median` is a **land** value per sqm, while condo/house `price_per_sqm` is per sqm of
**floor** area — so the condo/house percentage gaps (often >1000%) overstate the true market lag from a
unit mismatch. The **clean land-to-land comparison is vacant lots**: median market price still runs
roughly **2–4× BIR** (e.g. Cebu City lots +93%, Mandaue +401%, Lapu-Lapu +170%). RQ4's defensible
headline should lead with the vacant-lot gap and caveat the condo/house magnitudes.

Artifacts written: `Models/stratified/model_comparison_groupcv.csv`, `ablation_groupcv.csv`,
`valuation_gap_summary.csv`, `Data/processed/valuation_gap_per_property.csv`,
`QGIS/data/valuation_gap.geojson`. Scripts: `Scripts/answer_rq2_rq3.py`, `Scripts/answer_rq4.py`.

---

## Decision 45 — Consolidated Data-Collection Lineage (two scraper generations) + verified funnel (2026-06-13)

**Context:** The Lamudi collection history was scattered across Decisions 18/22/26/37/39 and was vague in the manuscript (Ch3 §3.4 just says "a custom web scraper"). This consolidates it and pins the **verified** funnel so the manuscript can state accurate numbers. Funnel reproduced by `Scripts/data_collection_funnel.py` → `reference/data_collection_funnel.csv`.

**Measurement caveat (important):** the raw scrape CSVs have multi-line `description` fields, so `wc -l` line counts wildly overstate the row count (e.g. `wc -l` reported 122,549 / 20,988; the actual **parsed** rows are 4,477 / 665). Always count parsed rows. An earlier "tens of thousands of raw listings" claim from a line-count is **retracted** — the documented "665 candidates → 275 net" figure was correct.

### Stage 1 — legacy `requests` + BeautifulSoup scraper (`Data/webscraping-lamudi/`)
The original collection generation. Verified funnel on `lamudi_cebu_full.csv`:

| Filter | Rows |
|---|---:|
| raw scrape | 4,477 |
| has coordinates | 3,459 |
| valid price 500k–500M | 3,163 |
| inside 6 LGUs | 2,826 |
| residential recode | 2,638 |
| after spatial cap (≤3/pin) | 1,470 |
| unique in-scope listings | **1,419** |

After further cleaning, geocoding, BIR join, and the segment/cleanup passes (ABT moved 2,047 → 1,603 → ... per Decisions 22/26), this generation is the **bulk of the ~1,579-row pre-batch open-market ABT**.

### Stage 2 — Playwright browser scraper (`playwright/`, Decision 37, 2026-06)
Introduced because **Lamudi deployed a JavaScript-challenge / CAPTCHA (DataDome-class WAF)** that the `requests` scraper could no longer pass (the IP was not banned; the block was JS-execution-based). Verified funnel on `lamudi_scraped_geocoded.csv`, dedup'd against the 1,579-row pre-batch ABT (`abt_clean.backup_pre_batch_2026-06.csv`):

| Filter | Rows |
|---|---:|
| raw scrape | 665 |
| has coordinates | 654 |
| valid price 500k–500M | 600 |
| inside 6 LGUs | 560 |
| residential recode | 533 |
| after spatial cap (≤3/pin) | 400 |
| unique in-scope listings | 372 |
| **NET-NEW vs pre-batch ABT** | **275** |

Merged + enriched (Decision 39) → **abt_clean.csv 1,849 rows** (5 of the 275 dropped at the polygon-LGU/enrichment step; final source tags: **Lamudi 1,579 + Lamudi_playwright_2026-06 270**).

### Net
- Final ABT = **1,849 open-market rows** from two Lamudi scraper generations.
- Supersedes scattered references; Decisions 18/22/26/37/39 remain valid for their specific steps.
- Ch3 §3.4 should carry this two-stage story + the funnel table (see `ch_correction_checklist_2026-06-13.md`).

---

## Decision 46 — Ramolete benchmark replication + centroid-snap geocoding finding (2026-06-14)

Two linked diagnostics run to stress-test the Ramolete et al. (2023) benchmark before it enters
Chapter 7. **No change to data, strata, or deployed models** — diagnostic only.

### 46a — Ramolete random-split replication (`Scripts/replicate_ramolete_randomsplit.py`)
Re-ran OLS/RF/XGB per stratum under Ramolete's protocol (plain random 80/20 split, no coordinate
grouping; 25 seeds + literal seed=42), to test the prior assumption that our higher headline MAPE
was "mostly evaluation honesty." **It is not.** RF MAPE under random split vs leak-free GroupKFold:

| Stratum | random-80/20 MAPE (mean) | leak-free MAPE | inflation | random-split MdAPE |
|---|---:|---:|---:|---:|
| Condo | 30.0% | 35.2% | +5.1pp | 15.9% |
| Houses | 30.6% | 32.5% | +1.9pp | 21.3% |
| Vacant Lot | 34.4% | 37.8% | +3.4pp | 21.2% |

Findings: (1) coordinate-leakage inflation is **real but modest (2–5pp, largest for condos)** —
consistent with condos having the densest pin-sharing; (2) **even under their split our MAPE
stays ~30%, still above Ramolete's 10.7–21%** → the gap is mostly genuine (their 3,212 houses vs
our 674, thinner Cebu market, their PSA/DTI features + AdaBoost/segmentation), NOT just protocol;
(3) **lead with MdAPE** — RF typical error under the random split (15.9% condo / 21.3% houses)
sits at the top of their band, so the median property is competitive while a tail of hard
properties inflates the mean. Houses = fairest like-for-like (their data is house-dominated).
Write-up: `reference/ramolete_replication_2026-06-14.md`; CSV:
`Models/stratified/ramolete_randomsplit_comparison.csv`.

### 46b — Shared-pin cause = centroid-snapped geocoding (`reference/shared_pin_investigation_2026-06-14.md`)
Investigated why 64% condo / 45% house / 39% lot rows share an exact coordinate. **For houses/lots
it is overwhelmingly a geocoding artifact, not real geography:** incomplete addresses
(subdivision/barangay/city, no street number) snap to a barangay/subdivision **centroid**.
~83% of shared house rows and ~80% of shared lot rows are centroid-snaps → **~31–37% of the
Houses/Lot strata sit on a centroid**. Condos are mostly genuine multi-unit buildings (64-unit
Marigondon tower) but ~39% are still centroid-snaps. **Consequence:** spatial features (CBD
distances, MCRAI, road distances, spatial lag) on centroid rows were computed from the centroid,
not the true parcel → spatial-feature noise on ~⅓ of houses/lots (a plausible source of the
high-MAPE error tail in 46a). **Does NOT break leak-free CV** (GroupKFold groups by exact lat/lon →
one fold). Logged as a **data-quality limitation** + future-work fix (re-geocode incomplete
addresses); no re-geocoding done this session (author to decide).

---

## Decision 47 — Multi-source data expansion: 3 new portals merged + deployed (2026-06-14)

Expanded the ABT beyond Lamudi by scraping three additional Cebu portals to grow training data
(binding constraint, esp. Vacant Lot n=255). **Deployed the expanded model** (author decision):
condo/houses held accuracy at ~2× data; the Vacant Lot increase is an honest harder-sample
finding, not a regression.

### 47a — Sources + scrapers (Scripts/scrape_{filipinohomes_api,dotproperty,onepropertee}.py)
Reconned the full Cebu portal ecosystem; built/ran three scrapers. **Raw 11,419 listings:**
- **FilipinoHomes 3,894** via its backend JSON API (`api2.filipinohomes.com/api/listings`,
  `x-guest-token`) — found by intercepting browser calls; the HTML site is a Next.js app serving
  only page 1. Returns **precise embedded coords** (~90%; 107 null-island) + structured
  city/barangay + separate floor/lot area. Highest quality.
- **DotProperty 3,721** (`?page=N`, `.listing-snippet`); barangay-level location text.
- **OnePropertee 3,804** (`/page/N`, `div.listing`); city-level text only (worst geocoding).
FilipinoHomes HTML scraper (`scrape_filipinohomes.py`) superseded by the API version.

### 47b — Clean + geocode + dedup (Scripts/clean_multisource_2026-06.py)
Funnel 11,312 → **1,783 staged net-new**. Forward-geocoded **991 unique** location strings (DP/OP)
via Google (cache `Data/processed/geocode_cache_multisource.json`; ~$5, well within free tier;
verified no OVER_QUERY_LIMIT). Google chosen over OSM (has `location_type` precision flag, no
mismatch, no 1 req/s cap) — but precision ceiling is the INPUT text: all DP/OP strings →
APPROXIMATE centroids regardless of geocoder. Filters: price 500k-500M, 6-LGU polygon
(`QGIS/data/lgu_boundaries.geojson`), residential recode, Lot scope 80-2000, **drop
distressed/"For Assume" (loan-balance prices, not market value — same class as bank_ropa
Decision 17; -299)**, per-stratum price_per_sqm band (-100), dedup coords+price+area (user
choice; -733 internal/-93 vs ABT), **spatial cap 3/cell (-4,402)**. Cap collapsed the worst
clustering (one "Cebu City" centroid held 1,087 rows → 3). Pre-clean 89% pin-sharing → post 62%.

### 47c — Merge + enrich + retrain (abt_clean 1,849 → 3,632; backups `*pre_multisource*`)
Canonical chain (Decision 35e): append → compute_road_distances → enrich_cbd_and_lag →
compute_hansen_scores → filter_to_lgu_scope → prepare_stratified_abt → finalize_stratified_groupcv.
**Strata: Condo 687→1,314, Houses 674→1,221, Lot 255→851.** Sources: Lamudi 1,579 +
FilipinoHomes 1,199 + DotProperty 548 + Lamudi_pw 270 + OnePropertee 36 (OP gutted by the cap —
city centroids, as predicted).

### 47d — First retrain was contaminated; re-cleaned (the "For Assume" + outlier filters above)
Initial merge (no distressed filter) degraded all strata (Lot 41.7, COD 63). Diagnosis: ~14%
contamination (264 assumption listings + 42 area errors), mostly FilipinoHomes, + a residual
FilipinoHomes price level ~26% below Lamudi. Added the 47b filters → re-ran.

### 47e — Deployed metrics (leak-free GroupKFold, clean single retrain)
| Stratum | n | MdAPE | (was) | COD | PRD | PE20 |
|---|---|---|---|---|---|---|
| Condo | 1,314 | **20.7** | 20.1 | 39.3 | 1.23 | 49 |
| Houses | 1,221 | **22.7** | 22.1 | 36.0 | 1.21 | 45 |
| Vacant Lot | 851 | **38.7** | 25.6 | 59.3 | 1.51 | 27 |
Condo/Houses parity at ~2× data. **Lot up to 38.7 — verified an honest harder-sample effect, not
a bug** (see 47f). Manifest rewritten; SHAP + EDA (plots 01-09) refreshed; geojson regenerated.

### 47f — Lot investigation (Scripts/experiment_lot_precise.py): centroid hypothesis REFUTED
Hypothesis: centroid-geocoded lots corrupt the location signal. Test: retrain lot on precise-coord
lots only. Result: (A) all 851 = 38.0, (B) precise-only 746 = **40.7 (no better)**, (C) original
255 Lamudi lots = 24.3. So centroids are NOT the cause; the original 255-lot 25.6 was a small,
geographically concentrated (easy) sample. The 851-lot sample reveals the true ~38% difficulty of
bare-land valuation in a thin market (consistent with RQ1 bid-rent: lots depend on exact location
more than any stratum, and lack fallback structural features). EDA confirms: lot price CV 0.88
(LOWER than Lamudi-only 1.02) — difficulty is spatial, not price-dispersion.

### 47g — spatial_lag_price feature fix (enrich_cbd_and_lag.py)
Two flaws fixed: (1) now averages **same-stratum** neighbours only (a lot's neighbourhood price no
longer mixes in condo towers); (2) radius **1,000 m → 500 m**, grounded in arXiv 1902.00562 ("The
Spatially-Conscious Machine Learning Model", which uses 500 m spatial-lag aggregation) + internal
consistency with the MCRAI "micro" amenity scale (500-800 m). Effect on metrics is minor
(spatial_lag is ~7% RF importance) — the fix is for defensibility/correctness, not accuracy. At
500 m, 136/3,632 rows (3.7%) have no same-stratum neighbour → median-imputed. If lots get too
sparse, the k-NN neighbour definition (also in 1902.00562) is the documented alternative.

### Process note
A chained-job overlap briefly ran two `finalize` processes writing the same manifest (race);
caught, killed, regenerated cleanly. Lesson: never launch a new finalize before confirming the
prior one exited. Reference doc: `reference/source_expansion_2026-06-14.md`.

### 47h — Feature investigation + OnePropertee dropped + distressed filter broadened (2026-06-14)
Post-deploy feature investigation (`Scripts/investigate_features_2026-06.py`, leak-free OOF
residuals by source + high-error-lot profiling). Findings:
- **OnePropertee = contamination.** OOF: model over-predicts OP lots **3.34× (MdAPE 234%)**, OP
  condos 1.43× (43%) — its per-sqm-priced lot text was mis-extracted + city-centroid geocoding.
  Only 36 rows survived the cap, all bad. **Dropped entirely** in `clean_multisource_2026-06.py`
  (scraper + raw CSV retained).
- **Distressed filter broadened** to `assum*` (caught 3 "assumption/assumed" pasalo listings the
  exact-word `\bassume\b` missed). Confirmed: FH distressed inventory is mortgage-ASSUMPTION
  (pasalo, loan-balance pricing), not bank foreclosures — no ROPA keyword survivors. Caveat: FH
  API `status` field was NOT captured, so a keyword-less distressed listing could still slip
  through (documented data limitation).
- **FilipinoHomes source effect (real):** model over-predicts FH houses **~14%** (ratio 1.135) —
  FH lists genuinely cheaper stock the features don't explain. Adding a `source` dummy barely
  helps (lot −1.0pp, houses +0.3) and isn't available at prediction → NOT used; disclosed as a
  source-heterogeneity limitation.
- **Lot data ceiling, quantified:** worst-decile-error lots (APE≥124%, n=86) are CHEAP lots
  (median 11k/sqm vs 35k rest) at the SAME location/area/BIR — model over-predicts 100% of them.
  Cheapness comes from unobserved parcel attributes (frontage/zoning/title/slope/flood). 65% are
  FilipinoHomes. This is the bare-land data ceiling, now evidence-backed.

**Re-ship (no OnePropertee): abt_clean 3,617; strata Condo 1,301 / Houses 1,223 / Lot 849.**
Deployed: **Condo MdAPE 19.8** (now BEATS validated 20.1), Houses 22.5 (parity), Lot 38.0
(COD 56.2, down from 59.3). Manifest/geojson/EDA/RQ4 refreshed. Sources: Lamudi 1,579 +
FilipinoHomes 1,203 + DotProperty 565 + Lamudi_pw 270.

### 47i — EDA-grounded per-stratum feature selection + ID 1523 cleanup (2026-06-15)
Deep EDA mining (OLS coefficients eda_06, Cook's distance eda_07, VIF eda_05, MCRAI internal
corr, IQR, MCRAI zero-rates) drove a principled feature trim + one data fix. Scripts:
`experiment_no_cbd.py`, `experiment_ablation_blocks.py` (parallel leave-one-block-out),
`experiment_simplified_features.py`.

- **Data fix — dropped condo ID 1523** (Cook's D=6.08, 1st-pctile): "Apartment in Mactan", 186 sqm
  (vs condo median 36), ₱23,656/sqm — a misclassified house-sized unit, not a real condo. ABT
  3,617→3,616; condo stratum cleaned. (Backup `abt_clean.backup_pre_featsel_*`.)
- **Per-stratum feature selection (in `finalize_stratified_groupcv.py STRATUM_DROP`):**
  ALL strata drop `bir_zonal_rr_log` (=log of rr_median), `bir_zonal_cr_median` (commercial, not
  OLS-sig, corr 0.59), both ROAD distances (not OLS-sig, ~0 ablation). Condo+Houses additionally
  collapse MCRAI 9→1 (keep only `mcrai_composite`; the 9 are 0.57-0.96 inter-correlated, composite
  carries 0.79-0.96 of each). **Lots keep individual MCRAI** (grocery/hospitals OLS-significant
  land-value drivers; collapsing cost +1.1pp).
- **Evidence convergence:** VIF (MCRAI 30+ for condos, bir_rr_log ~6), OLS significance (roads
  p 0.27-0.997, mcrai_security/tourism significant NEGATIVE = spatial-sorting artifacts already
  flagged in Decision 20), leave-one-block-out (ROAD ≤0.3, bir_rr_log/mcrai_composite ≈0), MCRAI
  zero-rates (security 27-37% empty). Not arbitrary — finishes the Decision-20 artifact cleanup.

**Deployed (leaner, ID 1523 removed): abt_clean 3,616; strata Condo 1,300 / Houses 1,223 / Lot 849.**
| Stratum | feat | MdAPE | (was) | COD | PRD |
|---|---|---|---|---|---|
| Condo | 33→**21** | **19.3** | 19.8 | 37.7 | 1.21 |
| Houses | 36→**24** | 22.7 | 22.5 | 35.8 | 1.20 |
| Vacant Lot | 29→**25** | 38.2 | 38.0 | 56.3 | 1.48 |
Condo improved + much simpler; houses/lots parity at far fewer features. Methodology win:
EDA-grounded feature selection, simpler where economics allow (vertical units → one accessibility
summary), fuller where bare-land valuation demands it. Manifest/geojson/EDA/RQ4 refreshed.
Detail: `feature_investigation_2026-06-14.md`.

## Decision 48 — Ramolete random-split replication refreshed on the 3,616-row ABT (2026-06-15)
Re-ran `Scripts/replicate_ramolete_randomsplit.py` after the multi-source expansion (Decision 47)
and per-stratum feature selection (Decision 47i). **Script changes:** refreshed RF best-params to
the current manifest, and applied the deployed `STRATUM_DROP` to the tree feature matrix so the
replicated models match what is actually deployed (the prior run used the full, pre-47i feature set
and stale params). OLS/XGB and the protocol (random 80/20, 25 seeds + literal seed=42, leak-free
MAPE read from the manifest) unchanged.

**Refreshed RF results (mean of 25 random 80/20 splits):**
| Stratum | n | random-80/20 MAPE | random MdAPE | leak-free MAPE | leakage inflation |
|---|---|---|---|---|---|
| Condo | 1,300 | 31.5% | 16.2% | 36.5% | +5.1pp |
| Houses | 1,223 | 33.8% | 22.1% | 35.1% | +1.3pp |
| Vacant Lot | 849 | 56.1% | 36.2% | 58.0% | +1.8pp |

**Findings (all hold, some sharper):** (1) coordinate-leakage inflation stays small (1–5pp, largest
condos) and on the expanded data **shrank** for houses/lots — more data leaves less room for a
naive split to flatter the model; XGB now barely inflates (Condo +1.7, Houses −0.1, Lot −1.0pp).
(2) Even under their own random-split protocol our houses MAPE ≈34% > their 10.7–21% → the gap is
**genuine** (their 3,212 houses vs our 1,223, thinner Cebu market, their PSA+DTI features), not an
artifact of evaluation rigor. (3) Lead with **MdAPE**: condo 16.2% (inside band) / houses 22.1%
(top of band) under their protocol. (4) **Vacant Lot random MdAPE rose 21%→36%** vs the prior run
— reconciles with Decision 47f: the earlier low lot error was small-sample optimism; the honest
broad-sample error is ~36–38% (bare-land data ceiling). Houses remain the only fair like-for-like.
Outputs: `Models/stratified/ramolete_randomsplit_comparison.csv`, write-up refreshed
`reference/ramolete_replication_2026-06-14.md`.

## Decision 49 — Lot MCRAI cleanup: drop mcrai_composite (exact collinearity) + mcrai_security (data gap) (2026-06-15)
EDA on the 8 individual MCRAI features for the lot stratum (`investigate_mcrai_lot_2026-06-15.py`)
prompted by the question "why include both the individual MCRAI scores AND the composite in the
lot model?"

- **Dropped `mcrai_composite` from lot.** The composite is an EXACT linear blend of
  education/grocery/recreation (`compute_hansen_scores.py`: weights 0.447/0.345/0.222). Regressing
  it on the 8 individuals gives **R²=1.0000** → perfect multicollinearity with features already in
  the lot model. Harmless to RF *prediction* (ablation ~0) but corrupts SHAP/importance (splits the
  accessibility signal arbitrarily between composite and its own constituents) and is indefensible
  at a panel. Condo/houses are unaffected — they use the composite *instead of* individuals (no
  collinearity there).
- **Dropped `mcrai_security` from lot.** 36.9% zero-rate, wildly LGU-uneven (Consolacion 62%,
  Minglanilla 61%, Lapu-Lapu 19%) = OSM POI **data-coverage gap**, not true absence (CLAUDE.md EDA
  rule); OLS-insignificant (p=0.14, negative sign); **lowest RF importance of the 8** (2.14%).
- **Clarification (corrects an in-session error):** `security`, `tourism`, `retail_density`,
  `health`, `hospitals` were NEVER in the composite (Decision 20 kept only positive-coefficient
  education/grocery/recreation). So condo/houses (composite-only) already exclude security — no
  composite recompute was ever needed; security lived ONLY in the lot model.

- **Also dropped `mcrai_retail_density` from lot (user-approved).** Univariate corr with lot price
  **+0.047 (≈ noise)**, OLS significant-NEGATIVE (suppression artifact), free to drop (ablation
  −0.1pp). `tourism` (+0.2pp) and `health` (+0.8pp) earn their place and are kept.

**Result (leak-free GroupKFold RF):** Lot **25→22 features**, MdAPE 38.2→**38.4** (parity, within
run-to-run noise), **COD 56.3→55.9**, PRD 1.48, PE20 26. Condo (19.3/21) and Houses (22.7/24)
**byte-identical** (change isolated to lot). Lot top feature now `dist_cebu_business_park_m`
~31% importance (bid-rent); remaining MCRAI = education/grocery/health/hospitals/recreation/tourism.

**Why keep a composite at all? (tested, `mcrai_composite` vs its 3 constituents for condo/house):**
the composite (1 feat) BEATS using education+grocery+recreation as 3 raw features — Condo 19.32 vs
19.82, Houses 22.67 vs 22.91, both at FEWER features. The grounded Stage-1-OLS weights act as
regularization (one stable accessibility signal vs three correlated raw scores the RF must
re-weight on limited data), and the composite IS the MCRAI index — the thesis construct. So:
condo/house deploy the **index** (composite); lot deploys the **individuals** (bare land reads
specific amenity access). Coherent with RQ3 (property types priced by different geospatial
structure).

Files: `Scripts/investigate_mcrai_lot_2026-06-15.py`, `finalize_stratified_groupcv.py STRATUM_DROP`,
`Models/stratified/deployment_manifest.json`.

## Decision 50 — RQ2/RQ3 rerun on the 3,616-row ABT + manuscript checklist refresh (2026-06-15)
Re-ran `answer_rq2_rq3.py` to refresh the RQ2 (model head-to-head) and RQ3 (geospatial ablation)
outputs, which were stale (pre-expansion, 06-13). **Script change:** applied the deployed `STRATUM_DROP`
(Decision 47i/49) to the tree feature matrix so RQ2's RF and the RQ3 ablation tiers use the SAME lean
feature sets as deployment — giving ONE coherent RF number per stratum. Verified: RF MdAPE now matches
the manifest exactly (19.32 / 22.67 / 38.36 → PASS for all three). OLS keeps its hedonic baseline set.

**RQ2 (leak-free GroupKFold, MdAPE):** Condo OLS 24.5 / RF 19.3 / XGB 19.8; Houses 25.1 / 22.7 / 23.6;
Lot 44.8 / 38.4 / 40.2. Trees beat OLS 5–6pp; **RF edges XGB on all three** (0.5–1.9pp) — comparable, RF
the modest winner, deployed for robustness/simplicity.

**RQ3 ablation (Structural → +Admin → +Geospatial, ΔMdAPE):** geospatial helps all three vs
structural-only (Condo +5.65, Houses +4.18, Lot +12.95 pp). **Decomposition (pure engineered geospatial
on top of city+BIR):** Condo +3.70, Lot +3.77 (geospatial carries BOTH), Houses −0.66 (admin location
carries houses). **Updates the prior finding** — lots are carried by engineered geospatial too, not just
administrative location.

**Checklist refresh:** rewrote `Manuscript/ch_correction_checklist_2026-06-13.md` with current numbers +
the missing Decision 47–49 items (multi-source data story, per-stratum feature selection, lot MCRAI
cleanup, source-heterogeneity + lot-ceiling limitations). The checklist is now the trustworthy rewrite map.
Outputs: `model_comparison_groupcv.csv`, `ablation_groupcv.csv` (both rerun). RQ4 (`answer_rq4.py`) still
pending. Manuscript prose remains the next phase.

**Next decision number: 51.**

## Decision 51 — RQ4 valuation gap refreshed on the 3,616-row ABT (2026-06-16)
Re-ran `answer_rq4.py` on the current 3,616-row open-market ABT. The output files
(`Models/stratified/valuation_gap_summary.csv`, `Data/processed/valuation_gap_per_property.csv`,
`QGIS/data/valuation_gap.geojson`) now reflect the expanded data and **supersede the n=1,616 figures
in the Decision 44 narrative** (which were never updated in place — left as historical record). No
script or model change: same leak-free out-of-fold RF predictions, manifest `best_params`,
GroupKFold(5) by coordinate cluster, target `log_price` back-transformed via `exp`.

**Coverage:** 3,372 valid properties (3,616 minus 244 rows with missing/zero `bir_zonal_rr_median`).
Strata: Condo 1,300 / Houses 1,223 / Lot 849.

**Headline finding (vacant lots, clean land-to-land vs land-area BIR):** market `price_per_sqm` runs
**~3× the BIR zonal benchmark overall**, ranging **2.2× (Cebu City) → 4.8× (Mandaue)** by LGU
(Consolacion 4.5×, Lapu-Lapu 3.0×, Minglanilla 2.7×, Talisay 2.5×). Model-predicted lot prices track
the same band (2.1×–5.8×). BIR lags the market almost everywhere: `pct_market_above_bir` ≈ 100% in
every LGU except Cebu City lots (88%) — i.e. BIR zonal values are systematically below open-market
levels across Metro Cebu.

**Caveat — condo/house gaps are NOT directly comparable and must not be headlined.** Their median
listing gaps (~736% condo, ~634% houses) are inflated because the numerator is a floor-area
`price_per_sqm` while the BIR denominator is a land-area benchmark — a unit mismatch, not a true
overvaluation. The defensible RQ4 claim is the **vacant-lot** comparison (land-to-land); condo/house
figures are reported only as directional context with the mismatch flagged.

**Next decision number: 52.**

## Decision 52 — SHAP interpretation artifacts refreshed + EDA moved inside thesis_main (2026-06-16)
**Integrity fix, no model change.** The committed SHAP artifacts were stale and misrepresented the
deployed models: the beeswarm PNGs showed individual MCRAI + road-distance features (retired/dropped
per Decisions 47i/49), and `Models/shap_block_summary_rf.txt` still listed `mcrai_finance`/
`mcrai_transport`. Regenerated all three beeswarms + a deployment-matched block summary directly from
the saved pkls (new `Scripts/regen_shap_2026-06-16.py`; one TreeExplainer pass per stratum; asserts
`n_features_in_` match). Cross-checked: deployed pkl feature lists == `deployment_manifest.json`
exactly (condo 21 / houses 24 / lot 22).

**SHAP block aggregation (mean|SHAP|, deployed RF):**
- **Condo:** spatial_lag_price 33.5% · CBD distances 30.2% · structural 28.6% · MCRAI 4.9% · BIR 2.2%
  · city/type 0.6%. Local comps + size dominate; land-based BIR nearly irrelevant for vertical units.
- **Houses:** CBD distances 38.5% · structural 35.2% · spatial_lag 13.5% · city/type 6.4% · MCRAI 3.9%
  · BIR 2.6%. `dist_cebu_business_park_m` is the single top feature (bid-rent to primary CBD).
- **Lot:** CBD distances 56.8% · MCRAI 22.4% · structural 12.4% · spatial_lag 4.7% · BIR 2.7% ·
  city/type 1.1%. Purest land-value gradient; `dist_cebu_business_park_m` alone ≈ 45% of lot mean|SHAP|.
  Highest MCRAI share of any stratum — empirically supports Decision 49 keeping individual MCRAI for
  lots while condo/houses use `mcrai_composite`.

Geospatial share (CBD + MCRAI + spatial_lag): Condo ~68.6%, Houses ~55.9% (~62% incl. admin location),
Lot ~83.9% — consistent with the RQ1 location-dominance finding.

**Repo hygiene:** all thesis content now lives under `thesis_main/`. The SHAP plots had been writing to
a stray workspace-root `EDA/` (scripts computed `SHAP_DIR` from `ROOT_DIR`, a leftover from the old
Drive layout where `EDA/` sat beside `thesis_main/`). Pointed `SHAP_DIR` at `THESIS_DIR/EDA/...` in
`finalize_stratified_groupcv.py`, `finalize_lot_model.py`, `run_models_stratified.py`; merged the fresh
plots into `thesis_main/EDA/` and deleted the root `EDA/`. Workspace root now holds only non-thesis
metadata (presentations, checklists, README, config). **NOTE: applied on `dev/modeling` only — must be
merged to `main` + other worktrees to remove the duplicate EDA everywhere.**

**Next decision number: 53.**

## Decision 53 — Condo pre-selling down-payment contamination: documented, models left frozen (Option A) (2026-06-16)
**Data-quality finding during model review (no model change).** The worst condo prediction errors are
atypically cheap listings the model over-predicts. Investigation of the cheapest condos relative to
their own city+type norm found the dominant cause is **pre-selling down-payments / reservation fees
scraped as if they were the full unit price**, not distress. Of the 35 condos priced under 25% of their
city norm, **24 carry a total ≤ ₱1M** (Mandaue 9 / Cebu City 9 / Lapu-Lapu 6), and most are named real
pre-selling projects (MIVELA Garden Residences, Grand Residences, One Astra Place, Northwoods Place) —
22–37 sqm studios/1BR at round ₱500k–950k totals. Only 1 of the 24 carries "rush"/distress wording;
distressed-listing detection is unreliable here because listing **descriptions were not retained** in
the ABT (only short titles). The 24 rows are saved with full detail in
**`reference/condo_partial_price_suspects_2026-06-16.csv`**; the fuller review write-up (including the
intra-city terrain limitation for lots and the geocoding-LGU-mismatch finding) is in
**`reference/model_review_2026-06-16.md`**.

**Decision (Option A):** document as a limitation, do **not** drop the rows or retrain. Rationale: the
deployed condo model + app price surface are frozen; removing ~1.8% of condos barely moves the median
error (the headline MdAPE) and mainly tightens the mean — a cosmetic gain not worth re-running the
frozen pipeline this close to defense, and bulk-dropping hard cheap cases to improve metrics is
indefensible at panel. A principled location-relative price floor in cleaning + retrain (Option B) is
recorded as a possible future improvement only. **The manuscript rewrite must state this limitation and
cite the 24-row evidence CSV.**

**Next decision number: 54.**

---

## Decision 54 — Bank ROPA / floor-price tiers dropped from the research; manuscript de-scoped to open-market only (2026-06-17)

**Context.** While reviewing the abstract, Nico flagged that it still described a three-tier "hybrid
dataset" (open-market listings + bank foreclosure/acquired-asset records + administrative floor-price
references). Verification against the data confirmed his recollection: **every ABT file
(`abt_clean.csv` and all backups/staged files) is 100% `market_segment = open_market`** — sources are
the three online portals (Lamudi 1,578, FilipinoHomes 1,203, DotProperty 565, Lamudi_playwright 270).
The bank ROPA and Pag-IBIG/BDO floor-price data exist only as **separate standalone files**
(`Data/processed/bank_ropa_geocoded.csv`, `Data/processed/floor_price/pagibig_clean.csv`, the BDO xlsx)
that were collected and geocoded under an earlier design but **never merged into any ABT and never
modeled**. The manuscript chapters still framed them as "reference layers retained in the canonical ABT"
and even claimed "the canonical ABT retained three market tiers" — none of which is backed by data.

**Decision.** The bank ROPA / foreclosure / acquired-asset / floor-price tiers are **dropped from the
research entirely.** The study is, and is described as, an **open-market online-listings** study across
three portals for the six LGUs. This supersedes the earlier CLAUDE.md "Data tiers" durable design
decision (open_market / bank_ropa / floor_price) and the "full ABT contains all three market segments"
note — both were updated to reflect open-market-only scope.

**Rationale.** The tiers play no role in any deployed output. They were never pooled into a training
target, contributed no features, and were used (at most) for one exploratory ordering check. Carrying
them in the narrative as "conservative benchmark layers" overstated the dataset and created a
defensibility liability (a panel could ask to see a three-tier ABT that does not exist). Removing them
makes the data story match the data.

**Manuscript edits (7 files, on `dev/manuscript`).** abstract: three-tier hybrid framing → open-market
listings from three portals. Ch1: "six data sources" list + "canonical ABT" sentence → open-market only.
Ch3: removed the "Multi-Source" subsection intro, the two distressed rows in the data-sources table, the
entire "Bank Foreclosure and Floor-Price Records" subsubsection, the "three market tiers" target-variable
claim, and the bank/Pag-IBIG ingestion + "filtered to open_market" pipeline steps. Ch4: removed
"reference layers" + the open-market-vs-ROPA comparison. Ch5: removed three "reference layer" mentions +
trimmed the market-segment subsection. Ch9: removed ROPA/floor-price from the sources list and dropped
the now-invalid "didn't pool tiers" methodological-contribution claim (renumbered First/Second/Finally).
Ch10: scope disclaimer reworded so it no longer implies the ABT held other segments. Legitimate uses of
similar words were kept (cleaning out distressed *open-market* "pasalo" listings; "three-tier *ablation*"
= feature tiers; the thesis itself as a "reference layer"). Compiles clean: 108 pages (was 112; the
4-page drop is the removed subsection + table rows), 0 undefined citations.

**Appendix also de-scoped.** The appendix (`appendices.tex`, included via `main.tex`) was itself stale:
Appendix A led with a "Sample Structure of Cleaned BDO Foreclosure Records" table (removed; the
open-market listing-structure table was retitled to represent the dataset), and Appendix B's "Geographic
Distribution... by Market Segment" table used `open_market / bank_ropa / floor_price` columns with an
old **2,047-row** total (1,619/320/108). That table was rebuilt from `abt_clean.csv` as the current
**3,616-row open-market** distribution by LGU and modeling stratum (Condo 1,391 / House 1,301 / Lot 924;
Cebu City 1,368 / Lapu-Lapu 870 / Mandaue 548 / Talisay 372 / Consolacion 242 / Minglanilla 216), with a
note that "House" aggregates house-and-lot, single-detached, townhouse, and apartment. Per-cell counts
verified against the data (first hand-estimate was wrong and corrected). Final build: 107 pages, 0
undefined references.

**Figure-and-paraphrase sweep (2026-06-17, follow-up).** A keyword grep only catches the exact tier
words, so a second sweep checked figures and paraphrases. Findings: (1) the embedded pipeline diagram
`diagrams/Data-Pipeline-Updated.png` was **stale** — it pictured `bank_ropa 320` + `floor_price 108`
ingestion and an old `abt_clean.csv 2,075 rows / 1,647 open_market`. Per Nico's choice it was **replaced
with a native TikZ figure** (added `\usepackage{tikz}` + libraries; 6-node Ingest→Clean→Geocode/BIR→GIS→
ABT 3,616→Stratify flow) so it is version-controlled and always matches the text. The old PNG and the
stale `.drawio`/`.mermaid`/`Feature-Engineering-Table.tex` sources remain on disk but are no longer
referenced. (2) Ch2 paraphrase "combines multi-source property evidence" → "open-market listings from
multiple online portals." (3) **Non-tier number bug caught while reading:** Ch5's first strata table
listed membership 1,300/1,223/849 but a "Total **3,616**" (those sum to **3,372**). Fixed the total to
3,372 and added a note explaining the 244-row gap (≈91 condo / 78 house / 75 lot), driven by
null-target / null spatial-lag rows plus the lot scope filter — verified against `abt_clean.csv` (a first
draft of the note wrongly said "mostly vacant lots" and was corrected). Remaining "liquidation /
forced-sale / conservative-filtering / three-tier-ablation" hits were confirmed legitimate, not tier
references. Build after the sweep: 108 pages, 0 undefined. Not visually rendered (poppler not installed),
but the TikZ compiles and its 90 mm width fits the text block.

**Next decision number: 55.**

---

## Decision 55 — QGIS de-scoped from a deliverable to an exploration tool; web app is the sole applied output (2026-06-17)

**Context.** During the Chapter 1 voice pass, Nico questioned the "GIS-derived" framing, noting he did
not use QGIS for feature engineering (the features come from the Google Maps Geocoding/Places APIs and
the OpenStreetMap road network via osmnx/Overpass, with Nominatim-style reverse geocoding). Two separate
points fell out of this: (1) the **title** and the generic "GIS-derived / GIS-based" terminology are
defensible and stay — GIS is the field, not the QGIS application; (2) but the manuscript still presented
**QGIS as a delivered output** in ~11 places, and Nico confirmed the price-surface map is now **only the
Vite/Leaflet + FastAPI web application** (QGIS was used during exploration, not as a final deliverable).

**Decision.** De-scope QGIS from a deliverable everywhere; the **web application is the single applied
deliverable**. Keep the thesis title ("…Machine Learning with GIS-Derived Spatial Features") and the
generic GIS terminology unchanged.

**Edits (abstract + Ch1 + Ch3 + Ch9 + Ch10).** Abstract: "delivered through a QGIS map and a web-based…"
→ web app only. Ch1: removed "QGIS-ready spatial layers/layers/map layers" from the deliverable sentence
(1.1 ideal-scenario), the broker-significance bullet, the significance closer, and changed "two applied
deliverables" → one (the web app). Ch3: dropped "through GIS" from the design intro; removed "QGIS for
spatial visualization" from the Tools line; **merged the "QGIS Interactive Map" + "Web Decision-Support
Application" subsubsections into a single "Web Decision-Support Application" deliverable** (kept the three
output layers — predicted price, valuation-gap, locational context — now presented in the app). Ch9:
"produced QGIS-ready layers" → "organized the model outputs spatially through the web application." Ch10:
fifth recommendation reworded from "keep the web application and QGIS outputs consistent" to keeping the
web application consistent with the saved model artifacts. Build clean: 107 pages, 0 undefined references.

**Next decision number: 56.**

## Decision 56 — Web app reframed as a prototype; institutional-use claims dropped; recommendations recalibrated to industry standards; MCRAI baseline parameters owned (2026-06-18)

**Context.** During the chapter-by-chapter voice pass (Chapters 1–10 reviewed and built clean), Nico
raised three connected scope concerns about how the deliverable and the recommendations were positioned:
(1) the web application was framed as an operational decision-support tool, but the model's error
(MdAPE 19/23/38; COD 37.7/35.8/55.9; PRD 1.20–1.48 — well outside IAAO ratio norms) does not support
confident stand-alone use; (2) the manuscript claimed **public institutions (BIR, LGU assessors,
lenders) would use** the tool; (3) the recommendations were too many (14) and some overclaimed. He also
asked whether the MCRAI formula/parameters are covered in the methodology and flagged that they feel
arbitrary (the gravity decay especially) — a candidate reason for the limited gains.

**Decisions.**
1. **Prototype framing.** The web application is a **prototype for triangulation, not a stand-alone
   valuation tool**, with the reasoning made explicit (substantial model error, especially vacant lots).
   Applied across abstract, Ch1 (deliverable + significance), Ch3 (deliverable subsection), Ch9
   (practical contribution). "valuation tool" → "valuation prototype."
2. **Institutional-use dropped.** Removed the Ch10 Policy recommendation that BIR / LGU assessors /
   lending institutions use the surface + valuation-gap as a monitoring layer; "screening for
   institutional review" → "screening during appraisal review"; softened the Ch1 Banks/Lending
   beneficiary (complements, does not feed, their valuation) and dropped "lenders" from the Ch9 user list.
3. **Recommendations recalibrated (~13 → 8 + a deployment note).** Dropped the Naga-City
   training-extension rec (not substantial). Softened the **valuation-gap** rec to a *research signal,
   not an appraisal input* — the gap comes from asking prices through a non-assessment-grade model and
   needs validation against recorded transactions before operational use. **Future Research now leads
   with making the geospatial/MCRAI feature computation more objective** (β, radii, weights estimated
   from data), absorbing the old decay-calibration and externality recs. Collapsed the 3 Deployment recs
   into a 3-sentence "A Note on Deployment" side note (deployment was not a primary aim). Added
   assessment-grade caveats so claims sit between over- and under-claiming.
4. **MCRAI baseline parameters owned (Ch3).** Confirmed the formula/parameters ARE in the methodology —
   Ch3 §3.4.1 (gravity formula, β=2, 0.5 km floor, the radii table) plus the Ch6 "MCRAI Composite Weight
   Derivation" subsection — but the **values** (β=2, radii) were asserted without justification (only the
   weights are OLS-derived). Added a sentence after the Ch3 radii table that both justifies (β=2 is the
   conventional inverse-square gravity setting; radii are baseline catchment scales) and **owns** the
   limitation (judgment-based baselines, not locally estimated), forward-referencing the Ch10
   future-research item.

**OHANA framing note.** The critique was written as **MCRAI's own parameterization being arbitrary**, NOT
as "based on Project OHANA" — consistent with the standing decision that MCRAI *replaced* OHANA (OHANA was
not applied). If the lineage itself is later judged a weakness, that is a separate Ch2/Ch3 revision.

**Also in this pass (logged for completeness; numeric/citation fixes, not scope decisions).** Fixed the
"five-to-six points" OLS-vs-tree overstatement in Ch7 and Ch9 (houses gained only 2.4 pts); resolved the
assembled-ABT (3,616) vs modeling-subset (3,372) terminology and a Ch5 self-contradiction + Appendix B
note; fixed the Stage 1/Stage 2 mislabel in Ch10; APA author-doubling in Ch8; the Ch2 macroeconomic
de-scope (cut the Macroeconomic Determinants subsection, Wibowo→Tanamal correction, dropped Becsky-Nagy);
the Ch4 collection-funnel table (16,561 raw → 3,616 retained, OnePropertee shown excluded). Verified RQ4
multipliers (2.2× Cebu City → 4.8× Mandaue, lots) against valuation_gap_summary.csv. All builds clean.

**Next decision number: 57.**
