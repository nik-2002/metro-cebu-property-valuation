# Modeling Decisions & Rationale — Q&A Defense Pack

Every decision below is grounded in `reference/modeling_decisions.md` (the **manuscript branch** is the authoritative, most complete log — Decisions 1–58; the modeling branch is identical through Decision 53). Cross-referenced with how Chapters 3, 5, 6 actually write it up. For each: **Decision → Why → If challenged.**

> **One number caveat to know cold:** earlier internal reports (Decision 42, n≈255 lot) showed Lot MdAPE ~25%. The **final deployed** numbers are on the expanded **3,616-row** ABT (Decision 47): **Condo 19.3 / Houses 22.7 / Lot 38.4**. The lot number rose because the multi-portal expansion added many cheap, attribute-thin lots — the data ceiling, not a regression. Use the final numbers.

---

## 1. Target variable = log(price per sqm)

**Decision (34).** The target is `log(price_per_sqm)`, back-transformed for the surface.

**Why.** (a) Price per sqm is right-skewed, so logging stabilizes variance and is the standard hedonic functional form (Rosen 1974; log-log gives interpretable elasticities). (b) **The integrity story** — an earlier `log_price` was computed inconsistently across scrape batches, so the target quietly meant *two different things*; one suspicious feature was dominating SHAP as a hidden scale-selector. Tracing and redefining the target to log price per sqm is why the final metrics are trustworthy.

**If challenged ("why per sqm, not total price?"):** per-sqm normalizes for size so the model learns *value density* (location/quality), not just "bigger = pricier"; total price is recovered as `pred × area`.

---

## 2. Stratification — three property-type models

**Decision (27).** Separate Condominium / Houses / Vacant Lot models (Houses = Single Detached + House & Lot + Townhouse + Apartment).

**Why — EDA evidence, not preference.** Condo median price/sqm is **5.8×** the lot median; coefficient of variation differs sharply (Condo 0.44, Houses 0.68, **Lot 1.28**); and the **correlation structure differs by stratum** — condos are driven by compact-unit area + recreation/zonal; houses & lots by BIR zonal and CBD distance, with structural features irrelevant for lots. A single pooled model treats these as one distribution and inflates the variance it must explain on a small sample.

**Manuscript:** Ch3 scope + Ch6. **Literature:** Dröes, Hoesli & Bourassa (2019) — stratified R² 0.637→0.782; Usman et al. (2020) — fit +7%, error −10%.

**If challenged ("isn't that just slicing a small dataset thinner?"):** each stratum still has ≥849 rows and all six LGUs; the variance *reduction* from removing cross-type noise outweighs the smaller n — and the literature shows the same.

---

## 3. Per-stratum feature sets (21 / 24 / 22)

**Decision (31d, 49).** A shared core for all three, plus principled per-stratum differences.

- **Shared core:** 8 road-network CBD distances; BIR zonal benchmark; 500 m spatial lag; city indicators (Cebu City = reference).
- **Condo & Houses:** structural (area, beds, baths + **imputed flags**) + the single **MCRAI composite**. Houses also carry property-type indicators (the sub-types).
- **Vacant Lot:** land area only (no beds/baths) + **six individual MCRAI** categories.

### 3a. MCRAI composite (condo/house) vs individual categories (lot) — *the question you'll get*

**The tested rationale (Decision 49 — this is the strong version):**
- For **condo/house**, the composite (1 feature) **empirically beats** its three raw constituents (education + grocery + recreation): Condo **19.32 vs 19.82**, Houses **22.67 vs 22.91** — *lower error with fewer features*. The Stage-1-OLS-derived weights act as **regularization** (one stable accessibility signal vs three correlated raw scores the RF must re-weight on limited data), and the composite **is** the MCRAI index — the thesis construct. Condo/house deploy the **index**.
- For **vacant lots**, the model originally carried *both* the composite and the individuals → the composite is an **exact linear blend** of education/grocery/recreation (regress it on the 8 individuals: **R² = 1.0000**), i.e. perfect collinearity. Harmless to RF *prediction* but it **corrupts SHAP/importance** (splits the accessibility signal between the composite and its own parts) — indefensible at a panel. So the composite is **dropped from lot**, and lots keep the **individuals** because bare land reads *specific* amenity access. Lots also drop **security** (36.9% zero-rate OSM coverage gap, LGU-uneven, lowest RF importance 2.14%) and **retail density** (≈ noise correlation +0.047).
- **Manuscript framing (Ch3 §3.4.x):** for built homes the categories are strongly inter-correlated (~0.57–0.96) and behave as one accessibility summary; bare land responds to specific kinds of access. Same conclusion, written gently.

**One-line answer:** *"Built homes deploy the MCRAI index because it empirically beats the raw categories and regularizes a noisy signal; bare land deploys the individual categories because it responds to specific access — and keeping both in the lot model was exact collinearity that corrupts the SHAP story, so the composite was dropped there."*

### 3b. Imputed flags (`bedrooms_imputed`, `bathrooms_imputed`)

**Decision.** 0/1 columns: **0 = observed**, **1 = the value was filled** (median by property type + city). They sit in the condo/house structural block.

**Why.** They let the model distinguish a *real* 3-bedroom from a *guessed* one, so imputed values don't masquerade as fact — the "**flag it, never silently fill it**" principle, keeping imputation auditable. Vacant lots have no such flags because beds/baths are **structurally absent** (nothing to impute).

### 3c. Area treatment — drop, don't impute

**Decision (31).** `area_sqm` is unified (floor area for condo/house, lot area for lots — stratum-specific meaning). Rows with **null area are dropped, not imputed**.

**Why.** Imputing area distorts the per-sqm target and inflates apparent precision (advisor guidance; consistent with Decision 16 finding that an imputed-area flag leaked segment information). Dropping is cleaner and panel-defensible.

---

## 4. Multicollinearity — handled differently for OLS vs trees

**Decision (11, 12, 32).** Correlated spatial features are **kept in the deployed trees** but **trimmed in the OLS baseline**.

**Why.** CBD nodes are spatially clustered (Giuliano & Small 1991), so the 8 distances correlate (VIF > 5). Trees split fine on correlated predictors (Breiman 2001) and dropping them throws away real location signal — so all 8 stay in RF/XGBoost. For the **interpretable OLS** baseline, collinearity destabilizes coefficients, so it trims per stratum: the redundant CBD terms, `mcrai_composite` (a deterministic blend → near-singular design, VIF ~10¹¹), and the raw `bir_zonal_rr_median` (kept the log form — log-log spec).

**If challenged ("you have VIF > 5, isn't that a problem?"):** only for coefficient interpretation in OLS — which is exactly why we trim it there and report HC3 errors. For the deployed Random Forest, correlated features are fine and the decision is logged.

---

## 5. MCRAI design

**Decision (18, 20, 30, 56).** A gravity-based accessibility index per category, with a two-stage empirical weighting.

- **Form:** `MCRAI_ic = Σ 1/max(d_ij, 0.5)²` — inverse-**square** decay (β = 2), distance floored at 0.5 km, on osmnx road-network distance. Hansen (1959).
- **Category radii (km):** education 2.5, grocery 2.0, health 2.0, hospitals 5.0, recreation 1.5, security 2.0, tourism 3.0, retail 1.0 — category-specific catchment scales (Decision 30 widened education from a Philippine learner home-to-school survey; hospitals from tertiary-care catchment methodology).
- **Two-stage weights (Decision 20):** Stage 1 — OLS hedonic gives each category's *implicit price* (sign + significance); Stage 2 — normalize the positive, significant coefficients to sum to one → **education 0.447, grocery 0.345, recreation 0.222**. Security/tourism/retail were **never** in the composite (negative/insignificant).
- **Finance retired:** no SE-Asian residential hedonic study reviewed (Yao 2017, Moosavi 2021, Agosto 2017, OHANA 2021) treats banking as a distinct amenity; it proxies commercial density already captured by CBD distances.

**Honest ownership (Decision 56):** β = 2 and the radii are **judgment-based baselines** (conventional inverse-square gravity; standard catchment scales), **not locally estimated** — only the *weights* are data-derived. This is stated in Ch3 after the radii table and is the lead item in Future Research. **OHANA note:** MCRAI *replaced* OHANA; it is not "based on" it — frame any critique as MCRAI's own parameterization.

**If challenged ("the parameters look arbitrary"):** agree partially and own it — the decay/radii are defensible conventions, the weights are estimated from Cebu's market, and making the whole feature computation empirical is explicitly future work. Don't defend β=2 as estimated; it isn't.

---

## 6. OLS diagnostics (the baseline only)

**Decision (32).** Breusch-Pagan confirmed **heteroscedasticity** in all three strata; Jarque-Bera fails **normality** for condo + houses even after logging. Remedy: report OLS with **HC3 robust standard errors**; accept non-normality under robust inference.

**Why it doesn't threaten the deployed model:** these are OLS-inference issues. Random Forest makes no constant-variance or normality assumption, so they don't apply to the deployed predictor — they're documented as a known property of listing data, not a blocker.

---

## 7. Model selection & deployment

**Decision (40, 42).** OLS (interpretable baseline + MCRAI-sign diagnostic), Random Forest, XGBoost. **Random Forest deployed for all three strata.**

**Why these three / why not others:** they span interpretability→accuracy. SVR (costly to tune, weak interpretability), LASSO/Ridge (linear, subsumed by OLS), deep nets (need >10,000 samples; we have far fewer, and lose global interpretability) were set aside.

**Why RF over XGBoost:** under leak-free group-CV the two tree models are within noise (19.3 vs 19.8 / 22.7 vs 23.6 / 38.4 vs 40.2); RF is **best-or-tied**, robust on small samples, and simpler to maintain. (Decision 42 explicitly *reverted* an earlier Houses→XGBoost switch that had won on a 0.22 pp k-fold edge = noise.)

**Hyperparameters:** deployed RF tuned **per stratum** by group-CV MdAPE — 300 trees; max-features 0.7 / 1.0 / 1.0; min-leaf 1 / 2 / 1; max-depth none; random_state 42. Comparators run at standard settings so the head-to-head is fair.

---

## 8. Evaluation protocol — leak-free GroupKFold

**Decision (41c, 42a).** Accuracy is estimated with **GroupKFold(5), groups = coordinate cluster**, pooled out-of-fold (every row predicted once).

**Why (two reasons):** (1) ~109/301 lot rows shared coordinates (centroid geocodes + relistings), so a plain k-fold leaks near-identical neighbors across folds and **flatters** the model — earlier held-out Condo MdAPE 15.9% was optimistic from exactly this. (2) The deliverable is a **price surface that predicts at arbitrary locations**, so testing on held-out *locations* is the realistic test. Honest grouped-CV is stricter and correct.

**Metrics:** **MdAPE** and **PE20** as plain-language headline (median % error; share within 20%); **MAPE, COD, PRD** as supporting IAAO-style diagnostics. **No IAAO compliance claim** — under honest out-of-sample CV all strata sit at COD ~33–56 and PRD ~1.2–1.5, above the strict in-sample bands; that's a data/feature + harder-test property, stated openly (Decision 42d).

**If challenged ("your COD/PRD fail IAAO"):** correct, and we say so — IAAO bands are *in-sample assessment-roll* standards on large samples; ours are *stricter out-of-sample* estimates for a decision-support prototype, not an assessment roll.

---

## 9. The vacant-lot weakness — diagnosed, not hidden

**Decision (41).** Lot is the weakest stratum (MdAPE 38.4, COD 55.9, PRD 1.48) — and that's a **data/feature ceiling, not a modeling failure**.

**Why / what was done:** the lot stratum was first cleaned with two independently defensible filters — **area ∈ [80, 2000] sqm** (residential-lot scope; above ~2,000 sqm is bulk-discount development land where price/sqm collapses) and **price ≥ 0.5 × BIR zonal** (the legal valuation floor) — to remove non-residential parcels and data errors. The residual error is driven by lot-level attributes **absent from listings** (frontage, zoning, titled status, corner, slope, flood) and thin n. Crucially, RF still **beats naive baselines** on the same group-CV: BIR-zonal predictor MdAPE 66.7 / city-median 26.9 / **RF 25.6** (pre-expansion); top driver `dist_cebu_business_park_m` (bid-rent).

**If challenged ("the lot model is bad"):** it's the *weakest*, reported transparently with the data-ceiling reason, and it still decisively outperforms the BIR benchmark and a city-median heuristic — which is the relevant bar for a triangulation tool.

---

## 10. Data cleaning & collection

**Decision (33, 41b, 45, 47).** From 16,561 raw across three portals to a 3,616-row ABT.

- **OnePropertee excluded entirely (47):** mis-extracted per-sqm prices + city-centroid geocoding would have contaminated the model — a contamination decision, not convenience.
- **Distressed / "For Assume" removed:** they quote loan balances, not market value.
- **Hard duplicates dropped; a spatial cap** limits listings per location cell so dense clusters can't dominate a stratum.
- **Per-stratum price-per-sqm sanity band** removes area-entry errors and extreme mispricing.

**Manuscript:** Ch5 narrates each filter; Ch4 reports composition by source.

---

## 11. Scope & deployment framing

**Decision (54, 56).** **Open-market segment only** for the deployed surface (bank-ROPA / floor-price tiers dropped from the research). The web app is a **prototype for triangulation, not a stand-alone valuation tool** — justified by the substantial error (especially lots). Institutional-use claims (BIR/LGU/lenders *using* it) were removed; the valuation gap is framed as a **research signal**, not an appraisal input.

**If challenged ("can this be used in practice?"):** it's a prototype/triangulation layer that complements professional appraisal and must be validated against recorded transactions before any operational use — deployment was not a primary aim.

---

## Where the decision log and the manuscript agree / to watch

- **Aligned:** stratification rationale, per-stratum feature logic, MCRAI two-stage weights, GroupKFold protocol, the no-IAAO-compliance posture, and the lot data-ceiling framing are all written into Chapters 3/5/6 consistently with the log.
- **Watch (number provenance):** the manuscript reports the **final 3,616-row** numbers (19.3/22.7/38.4). If a panelist quotes an older figure (e.g. lot ~25%, or condo 15.9%), it predates the data expansion / used a leaky split — point them to the leak-free, post-expansion deployment manifest.
- **Owned limitation (don't over-defend):** MCRAI's β=2 and radii are baseline conventions, not estimated from Cebu data — concede this and cite it as future work (Decision 56). Only the weights are empirical.
