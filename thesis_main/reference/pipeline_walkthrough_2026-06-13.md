# Pipeline Walkthrough — End to End, in Plain Language

> Written 2026-06-13 to help me (Nico) hold the whole pipeline in my head before the
> manuscript revision. Organised the way I'll defend it: the business problem first,
> then the six CRISP-DM phases, with each phase pointing back to the research question
> it answers. Every claim names the script behind it so I can check it.

---

## 0. The business problem (why this thesis exists)

Metro Cebu has a hot housing market — residential prices rose about 11.5% in 2025, the
fastest outside Metro Manila — but there is **no single, trustworthy way to price one
property**. In practice three references are used, and all three are flawed:

- **BIR zonal values** are the government's tax benchmark. They lag the market badly —
  nationally only ~60% of LGUs have updated their schedules, some Cebu values date to 2019.
- **Bank appraisals** exist to protect the lender, so they lean conservative.
- **Listing prices** are what sellers *ask*, not what buyers actually *pay* — asking-price noise.

I call the distance between these references the **valuation gap**. The thesis builds a
data-driven, property-level model that gives a transparent, reproducible estimate of
open-market price, and delivers it two ways: a **QGIS map** and a **Streamlit web app**.

**Who it's for (two clients):**
- **Consumers (buyers/sellers):** "what's the typical open-market price for a property
  like this, in this part of Metro Cebu?"
- **Brokers (like my dad):** a professional who already knows the market and can sanity-check
  whether the model's number sits in a believable range. He's my real-world validator.

**Scope:** six LGUs — Cebu City, Mandaue, Lapu-Lapu, Talisay, Minglanilla, Consolacion.
Naga City is an economic anchor (a distance reference) but not a training area.

**The four research questions this pipeline must answer:**
1. **RQ1** — Which value drivers actually move price in Metro Cebu?
2. **RQ2** — Which model (Hedonic/OLS, Random Forest, XGBoost) is most **suitable for deployment** — balancing accuracy, robustness, and interpretability?
3. **RQ3** — Do the geospatial features improve valuation over a plain structural-only model, and how does that differ by property type?
4. **RQ4** — How big is the valuation gap between our predictions and BIR zonal values?

---

## 1. Business Understanding → answers the framing of RQ4

The valuation gap *is* the problem statement. RQ4 closes the loop by measuring it: once the
model can predict an open-market price for any point, the gap between that price and the BIR
zonal value at the same place tells us, in pesos per square metre, how far the official
benchmark sits from market reality — and where (which barangays, which LGUs).

---

## 2. Data Understanding — what data we have and whether to trust it

### The three data tiers
- **open_market (Lamudi):** online listings. **This is the only tier the deployed model
  trains on** — it matches the "market value" target.
- **bank_ropa (bank foreclosures)** and **floor_price (BDO/Pag-IBIG)**: collected and kept
  as reference, but **excluded from training**. Foreclosure and administrative floor prices
  are a *different basis of value* (liquidation / administered), not open-market value, so
  pooling them would contaminate the estimate (IVS 104 reasoning, Decision 17).

### How the data is collected
- Collection happened in **two scraper generations** (verified funnel in `reference/data_collection_funnel.csv`):
  1. **Legacy `requests` + BeautifulSoup scraper** (`Data/webscraping-lamudi/`): **4,477 raw** listings →
     3,459 with coords → 3,163 valid price → 2,826 inside the 6 LGUs → 2,638 residential → 1,470 after the
     spatial cap → **1,419 unique in-scope**. Further cleaning/geocoding/BIR steps brought this to the
     **~1,579-row pre-batch open-market ABT** — the bulk of the data.
  2. **Playwright browser scraper** (`playwright/scrape_index.py`, `scrape_properties.py`), added in 2026-06
     because **Lamudi put up a JavaScript-challenge / CAPTCHA wall** the plain `requests` scraper could no
     longer pass: **665 raw** → 654 coords → 600 valid price → 560 in-scope → 533 residential → 400 after
     spatial cap → 372 unique → **275 net-new** after de-dup against the pre-batch ABT.
- Net result: the **1,849-row ABT** (Lamudi 1,579 + 2026-06 Playwright batch 270), all open-market.
  *(Note: the raw CSVs contain multi-line description fields, so a `wc -l` line count overstates the row
  count wildly — always count parsed rows. The "665 → 275" figure is correct for Stage 2.)*
- Rows missing coordinates are filled with the **Google geocoding API** (`playwright/geocode_missing.py`),
  bounded to the Cebu box so nothing lands in the wrong province.

### Whether we trust it — data integrity (`Scripts/eda_data_integrity.py`)
This read-only audit checks the things that quietly break a property model:
- **Duplicate listings** (same coordinates + area + price) — relistings would fake "agreement."
- **Coordinate clusters** — many rows sharing one pin usually means a barangay-centroid geocode,
  not a real address; matters because it can leak location across train/test.
- **Implausible prices** — e.g. ₱3–4/sqm "lots" that are really mislabeled farmland.
- **MCRAI coverage by LGU** — thin amenity coverage in outer LGUs is real, not a bug.

> Current master table: `Data/processed/abt_clean.csv` — **1,849 rows × 51 columns**, open_market only.

---

## 3. Data Preparation — cleaning, then building the features

### Cleaning (a sequence of small, honest filters)
1. `stage_lamudi_batch.py` — price bounds (₱500k–₱500M), map messy city names to the 6 LGUs,
   keep only residential, cap listings per coordinate cell (kills barangay-centroid pile-ups),
   drop duplicates, and join the BIR zonal value.
2. `filter_to_lgu_scope.py` — drop anything whose pin falls outside the 6 LGU polygons.
3. `cleanup_abt_final.py` — keep open_market only, fix a few known bad IDs.

### Feature engineering — each feature in one plain line
- **CBD network distances** (`enrich_cbd_and_lag.py`): how far the property is, *by road*, from
  the 8 economic nodes (Cebu Business Park, Mandaue CBD, Mactan CBD, SRP, Talisay-Tabunok,
  Consolacion, Naga, Airport). Road distance, not straight-line, because Mactan's bridges make
  straight-line distance lie.
- **Road-corridor distances** (`compute_road_distances.py`): distance to the nearest trunk road
  and primary road — a property's basic connectivity.
- **MCRAI** (`compute_hansen_scores.py`): the *Metro Cebu Residential Accessibility Index* —
  "how easy is it to reach everyday amenities from here?" Computed per category with a gravity
  formula (closer + more amenities = higher score). 8 categories with their own radii:
  education 2.5km, health 2.0km, hospitals 5.0km, grocery 2.0km, security 2.0km, tourism 3.0km,
  recreation 1.5km, retail 1.0km (β=2.0, half-km floor). A combined **mcrai_composite** mixes the
  three categories the market actually rewards: **education 0.447, grocery 0.345, recreation 0.222**.
  *(Note: composite is 3 categories now — transport was retired to the road-distance features,
  finance was dropped entirely. Older decision notes that say 5km radii or a transport weight are
  stale; the code above is the truth.)*
- **spatial_lag_price** (`enrich_cbd_and_lag.py`): the average price of nearby listings within 1km —
  "what's the neighbourhood selling for?" Captures spatial autocorrelation (RQ3's third geospatial item).
- **BIR zonal values:** the official benchmark, carried as a feature and as the RQ4 comparison point.

### Stratification — three models, not one (`prepare_stratified_abt.py`)
A condo (~₱100k+/sqm) and a vacant lot (~₱20k/sqm) price by completely different logic, so one
mixed model would be noisy. We split into three:
- **Condo** — 687 rows
- **Houses** (Single Detached + House & Lot + Townhouse + Apartment) — 674 rows
- **Vacant Lot** — 255 rows (extra filter: 80–2000 sqm and price ≥ half the BIR floor, to drop
  bulk/farm land and data errors — Decision 41)

**Target for all three:** `log_price = log(price_per_sqm)`. We predict price *per square metre*,
then multiply by area for a total. Using the log keeps a few very expensive listings from
dominating, and per-sqm is the deliverable.

---

## 4. Modeling — the three models and how they're tuned

### The three models and their jobs
- **OLS (Hedonic regression)** — the *transparent baseline*. Gives a clear coefficient per driver.
  It's the comparator, not the deployed model. (Uses a trimmed feature set: top-2 CBD distances
  per stratum, log-area, drops the composite and the raw BIR value to avoid collinearity.)
- **Random Forest** — the *deployed* model. An average of many decision trees ("bagging"); robust,
  handles non-linear and correlated spatial features well.
- **XGBoost** — a *comparator*. Boosted trees; often wins on big tabular datasets.

RF and XGBoost use the **full feature set** (all 8 CBD distances, all MCRAI, road, spatial lag,
raw BIR). OLS uses the trimmed set above.

### How the models were tuned (precisely)
**Method for both RF and XGBoost:** grid search scored by **MdAPE** under **leak-free GroupKFold(5)**
(groups = coordinate cluster), `random_state=42`; lowest-MdAPE setting wins. OLS has no
hyperparameters (HC3 robust SE is for diagnostics only).

**Random Forest (deployed) — `finalize_stratified_groupcv.py`**, 24-setting grid:
n_estimators (300/400) × max_features (0.7/0.9/1.0) × min_samples_leaf (1/2) × max_depth (None/20).

| Stratum | n_estimators | max_features | min_samples_leaf | max_depth |
|---|---:|---:|---:|---:|
| Condo | 400 | 0.9 | 2 | None |
| Houses | 300 | 1.0 | 2 | 20 |
| Lot | 400 | 1.0 | 1 | None |

**XGBoost (comparator) — `answer_rq2_rq3.py`**, 8-setting grid:
n_estimators (300/500) × max_depth (3/5) × learning_rate (0.05/0.1) × subsample 0.9.

| Stratum | n_estimators | max_depth | learning_rate | subsample |
|---|---:|---:|---:|---:|
| Condo | 300 | 3 | 0.05 | 0.9 |
| Houses | 500 | 3 | 0.05 | 0.9 |
| Lot | 300 | 5 | 0.05 | 0.9 |

A wider exploratory search + elbow-style sweep plots live in `EDA/plots/11_hyperparameter_tuning/`
(`hyperparameter_tuning_sweep.py`).

### The key honesty trick — GroupKFold by coordinate cluster
Many listings share a coordinate (relistings, barangay-centroid geocodes). If a relisting of the
same address lands in *training* and its twin in *testing*, the model "cheats" and looks better than
it is. So we group every row by its exact (lat, lon) and force all rows at one location into the
**same fold** (`groupby([latitude, longitude]).ngroup()`). This is *leak-free* evaluation — slightly
worse-looking numbers, but honest ones.

### Why Random Forest over XGBoost (the honest answer — they tie)
This is the question the panel will push on, and the honest evidence (RQ2 head-to-head under the
same leak-free GroupKFold, `answer_rq2_rq3.py`) does **not** say RF is clearly more accurate:

| Stratum | OLS MdAPE | Random Forest | XGBoost |
|---|---:|---:|---:|
| Condo | 26.2% | **20.1%** | 21.4% |
| Houses | 24.3% | **22.1%** | 22.2% |
| Vacant Lot | 32.9% | 25.6% | **24.3%** |

**Tree models clearly beat OLS everywhere. RF and XGBoost are essentially tied** — RF wins condo,
ties houses, XGB edges lot on MdAPE (RF wins lot on PE20). All differences are within ~1.3pp, which
on 255–687 rows is sampling noise, not a real gap. So the deployment choice is **not** "RF is more
accurate." It's:
1. **Equivalent accuracy** — no honest reason to prefer XGB on the numbers.
2. **Small-sample robustness** — with only 255–687 rows per stratum, Random Forest's averaging is a
   safer default than boosting, which is built to shine on large data and can chase noise on small data.
3. **Parsimony** — RF has fewer sensitive knobs, so it reaches a stable optimum on a small tuning budget.
4. **Deployment simplicity** — RF is deterministic (fixed seed) and the app already runs on scikit-learn;
   shipping one model family is simpler for a tool a non-technical broker will use.

Say it plainly at defense: *"The two tree models perform the same within noise; we deploy Random Forest
because on a small sample it's the steadier, simpler, more reproducible choice — not because it's more
accurate."* That's honest and defensible.

---

## 5. Evaluation — how we judge it, in plain terms (`iaao_panel`)

We report a panel of metrics (the IAAO ratio-study set), led by two plain-language ones:
- **MdAPE** — the *typical* error. "Half the time we're within this %." This is the headline.
- **PE20** — "what share of predictions land within 20% of the true price."
- Supporting: **MAPE** (average error, pulled up by outliers), **COD** (how consistent the errors are),
  **PRD** (whether we systematically over/under-price cheap vs expensive homes).

**Current honest (leak-free) numbers:**

| Stratum | Rows | MdAPE | PE20 |
|---|---:|---:|---:|
| Condominium | 687 | 20.1% | 49.8% |
| Houses | 674 | 22.1% | 45.0% |
| Vacant Lot | 255 | 25.6% | 41.6% |

**How to say it:** "Typically off by about 20–26%. Vacant lots are weakest because land value depends
on parcel details (frontage, title, zoning, slope, flood risk) that online listings don't carry." The
model does **not** meet strict IAAO assessment-grade bands — so it's framed as a **decision-support AVM
prototype**, not an official mass-appraisal system. That's an honest, defensible position.

- **RQ1 (value drivers)** is read off SHAP / RF importance plus the EDA correlations.
- **RQ3 (geospatial uplift) — headline YES, with a decomposition nuance.** The ablation
  (`answer_rq2_rq3.py`) runs the same RF on three nested tiers. Versus a **structural-only** model,
  geospatial+location features improve **every** stratum:

  | Stratum | Structural | +Admin (city+BIR) | +Geospatial (full) | gain vs structural |
  |---|---:|---:|---:|---:|
  | Condo | 24.3% | 24.9% | **20.4%** | **+3.9pp** |
  | Houses | 24.8% | 21.2% | **22.0%** | **+2.8pp** |
  | Vacant Lot | 41.8% | 25.1% | **26.2%** | **+15.7pp** |

  So RQ3 is a **clear yes for all three strata** (vacant lots gain the most). The decomposition adds the
  nuance: the **engineered geospatial features** (CBD/MCRAI/spatial-lag) carry the gain for **condos**
  (the +Admin→+Geospatial step), while for **houses and lots** most of the locational signal is already
  captured by **administrative location** (city + BIR zonal). Coherent reason: BIR zonal is a *land*-value
  benchmark, least useful for vertical condos — exactly where the geospatial model earns its keep.
  Defensible claim: *"Geospatial features improve valuation across all property types; the engineered
  geospatial layer matters most for condominiums, where administrative benchmarks are weakest."*

- **RQ4 (valuation gap)** — `answer_rq4.py` confirms the thesis premise strongly: market and model
  prices sit **far above** BIR zonal in every LGU (95–100% of listings exceed BIR), and the model agrees
  the benchmark is low. **Caveat to state:** BIR zonal is a *land* per-sqm value while condo/house
  price/sqm is per *floor* sqm, so those percentage gaps (often >1000%) overstate the true lag. The clean
  land-to-land comparison is **vacant lots**, where market still runs roughly **2–4× BIR** — lead with that.

---

## 6. Deployment — the Streamlit app

**Tech stack:** Streamlit (UI) + scikit-learn (the RF models) + SHAP (explanations) +
pydeck and folium (maps, on free CartoDB tiles — no Mapbox key) + pandas/numpy/shapely.

**Four pages:**
- **Home** — overview + headline metrics.
- **Market Map** — every real listing, coloured by stratum, with amenity (POI) overlays.
- **Price Surface** — a predicted price grid across Metro Cebu for three property archetypes;
  far-from-data cells greyed out as low-confidence.
- **Property Predictor** — drop a pin → it auto-fills the city and BIR value, you add area/beds/baths →
  it returns a price/sqm with a 95% range and the top SHAP drivers.

**How a prediction works (`app/lib/`):** property type picks the stratum model; for the dropped pin,
the app looks up the **5 nearest training listings** and borrows their MCRAI/CBD/road/spatial-lag values
(falls back to city medians if you're >5km from any data); it builds the feature row, predicts log-price,
and exponentiates back to pesos/sqm. The 95% range comes from the spread across the forest's trees.

**The app reads the manifest correctly** (`metrics_group_cv`) — the old "contract bug" note is stale.

**Cloud deployment (deferred to next sprint):** to put this on Streamlit Cloud for my dad to test, we
need to commit the model pickles (~27MB), the grid parquets, the LGU GeoJSON, and decide how the app loads
`abt_clean.csv` (the paths are currently local-relative). No API secrets are required.

---

## One-line map of which artifact answers which RQ

| RQ | Answered by |
|---|---|
| RQ1 value drivers | SHAP/RF importance + EDA feature-relationships (battery c) |
| RQ2 best model | `model_comparison_groupcv.csv` (OLS vs RF vs XGB, same GroupKFold) |
| RQ3 geospatial uplift | `ablation_groupcv.csv` (structural → +admin → +geospatial) |
| RQ4 valuation gap | `valuation_gap_summary.csv` + `QGIS/data/valuation_gap.geojson` |
```
