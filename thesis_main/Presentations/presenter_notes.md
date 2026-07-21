# Presenter Notes — Defense (Claude Design deck)

Keyed to the 28 slides of `Defense Deck-Claude Design.html`. For each slide: **Say** (the spoken line) and, where a panelist is likely to probe, **Defend** (the justification, with the number or citation behind it). The deepest Q&A material is on the feature-set, MCRAI, cleaning, modeling, and evaluation slides.

Core figures to have memorized: ABT **3,616** rows (3 portals); modeling subset **3,372**; strata **Condo 1,300 / Houses 1,223 / Lot 849**; target **log(price per sqm)**; deployed **Random Forest**, leak-free **GroupKFold(5)** by coordinate cluster; MdAPE **19.3 / 22.7 / 38.4** (condo/houses/lot).

---

## The two questions you flagged

### Why MCRAI **composite** for condos & houses, but **individual** categories for vacant lots?

**Say:** "For built homes we use a single accessibility summary; for bare land we keep the amenity categories separate. That choice is empirical, not arbitrary."

**Defend:**
- For **condominiums and houses**, the eight MCRAI categories are **strongly inter-correlated — roughly 0.57 to 0.96** — so they move together and behave as *one* accessibility dimension. Collapsing them into the single `mcrai_composite` is the parsimonious, non-redundant representation; feeding all eight in separately would just add collinear noise without separable behavioral meaning. A buyer of a built home is responding to "is this a well-connected, well-serviced location," not to schools-versus-groceries as distinct levers.
- For **vacant lots**, the categories carry **distinct** signal — bare land responds to *specific* kinds of nearby access, so the six individual categories (education, grocery, health, hospitals, recreation, tourism) are each informative. The lot model therefore keeps them separate and **drops** three things: the **composite** (collinear with its own components), **security** (an uneven data layer with a high zero rate, ~26.6%), and **retail density** (near-zero correlation with lot price).
- The plain reading, and the line to give the panel: **"Built homes are summarized well by one accessibility index; bare land responds to particular kinds of amenity access, so we let those speak individually."** This came out of the feature-selection screens (inter-feature correlation, OLS significance, leave-one-block ablation, MCRAI zero rates) — not a hand choice.
- If pressed "isn't that inconsistent?": No — it's the *same* selection procedure applied per stratum, and it produced different answers because the strata genuinely behave differently. That difference is itself a finding.

### What are the **imputed flags** (`bedrooms_imputed`, `bathrooms_imputed`)?

**Say:** "Those are 0/1 indicator columns that tell the model which bedroom and bathroom counts were observed versus filled in."

**Defend:**
- When a listing reported beds/baths, the value is used and the flag = **0** (observed). When a listing didn't report them, we imputed the value (median by property type and city) and set the flag = **1** (imputed).
- **Why include the flag:** it lets the model distinguish a *real observed* 3-bedroom from a *guessed* 3-bedroom, so the imputed values don't silently masquerade as fact. The model can learn that imputed rows carry more uncertainty and treat them accordingly. This is the "**flag it, never silently fill it**" principle — imputation stays auditable, and it prevents filled values from quietly distorting the price signal.
- **Why lots don't have them:** for vacant lots, bedrooms and bathrooms are **structurally absent** (land has none) — not *missing*. So they're left out of the lot model entirely; there's nothing to impute and no flag. That is why the lot structural block is just `area_sqm`.

---

## Slide-by-slide

**1 · Title.** Say the title, your name, program, that it's an open-market residential valuation study for Metro Cebu using ML + geospatial features. Frame: a *decision-support* tool, not a replacement for appraisal.

**2 · Outline.** "The talk follows the CRISP-DM arc mapped to the thesis chapters — problem, literature, methodology, the data, modeling, evaluation, results, and the tool."

**3 · Where this study is set.** Six LGUs (Cebu City, Mandaue, Lapu-Lapu, Talisay, Minglanilla, Consolacion). **Defend the timing:** Cebu grew **7.3%** in 2024 (PSA) and residential prices rose **11.5%** in 2025 (BSP, highest outside NCR) — prices are moving faster than the references people use to read them.

**4 · The fragmented-references problem.** There's no single public source of "what is this worth." Price is pieced from four partial references — broker opinion, bank appraisals, BIR zonal values, online listings — each built for a *different* purpose, so they can't be compared. **Defend BIR:** zonal values are for taxation, not live market value, and are often stale (Otsuka et al., 2023) — that gap is exactly RQ4.

**5 · The problem, research questions & scope.** The claim: *Metro Cebu lacks a transparent, property-level, spatially detailed reference for interpreting residential price evidence.* Then RQ1–RQ4. **Scope discipline:** open-market segment only for the deployed model; a cross-sectional snapshot, late 2025; a prototype tool — say these proactively so the panel doesn't have to ask.

**6 · The core obstacle — and the gap it leaves.** The literature says the binding constraint in developing markets is **data scarcity, not valuer misconduct**: Kenya, 427 valuers ranked "limited information" #1 (Cheloti, 2021); Nigeria, **92.7%** of 300 valuers cited insufficient market evidence (Ajibola, 2010). **The gap:** no published, reproducible, property-level Metro Cebu model integrates open-market listings, geospatial accessibility, and explainable ML. That's the hole this fills.

**7 · Two modeling traditions — and why we stratify.** Hedonic regression (interpretable, one coefficient per attribute; Rosen 1974) vs. machine learning (non-linear, interacting; Breiman 2001; tree ensembles win on tabular data, Grinsztajn 2022). **Defend stratification with evidence:** modeling submarkets separately lifted R² from **0.637 → 0.782** (Dröes et al., 2019); segmenting before fitting improved fit ~7% and cut error >10% (Usman et al., 2020). Different property types are priced by different logic — pooling averages those into a worse fit for all.

**8 · Research design and the data pipeline.** Quantitative, non-experimental; predictive (estimate price) + prescriptive (surface the benchmark gap). Walk the pipeline: **Ingest → Clean → Geocode → BIR join → Geospatial features → ABT.** **Numbers:** 16,561 raw across Lamudi / FilipinoHomes / DotProperty; OnePropertee excluded for contamination (bad geocoding + mis-extracted per-sqm prices); **3,616** clean rows, 51 columns. **Defend "why only cleaning prunes":** geocoding/BIR/geospatial steps *add columns*, they don't drop rows — so the 16,561→3,616 attrition is the cleaning + scope filters, not the feature engineering.

**9 · Geospatial features — distance to economic centers.** Shortest-path **road-network distance** (osmnx, Dijkstra; Haversine fallback only when a point won't snap) to **eight** nodes — CBP, Mandaue, Mactan, SRP, Talisay Tabunok, Consolacion, Naga, airport. **Defend node choice:** polycentric urban economics (Giuliano & Small 1991), grounded locally in the JICA Mega Cebu roadmap (2015) — not arbitrary. **Defend road vs straight-line:** road distance captures real travel cost, including the Mactan bridge; that's why Mactan-island distances inflate — expected, not an error. Transport accessibility is carried by these node distances, which is why transport isn't a separate amenity category.

**10 · MCRAI — measuring access to amenities.** The gravity idea: for each property, sum nearby amenities in a category, weighted by 1/distance² (decay β=2), floored at 0.5 km; each category has its own reach. Show the formula (it's an image so it renders cleanly). **Defend the formula:** Hansen (1959) accessibility; the square-of-distance decay and 0.5 km floor are a standard, defensible baseline (the floor prevents singular values for immediately adjacent points). **Honest line:** β and the radii are sensible conventions, not estimated from Cebu data — that's flagged as future work.

**11 · MCRAI weights — and the evaluation protocol.** Weights come from a **two-stage** procedure, not assumption: **Stage 1** — fit a hedonic OLS with the individual categories; each coefficient is its *implicit price* (sign = premium/penalty, significance = reliable). **Stage 2** — keep the positive, significant categories and normalize their coefficients to sum to one → **education 0.447, grocery 0.345, recreation 0.222**. Security, tourism, retail stay as standalone features, not in the composite. **Evaluation protocol:** **GroupKFold(5)** grouped by **coordinate cluster** — the same location never appears in both train and test folds, so the model can't memorize a neighborhood; every headline number is out-of-fold. **Defend "why grouped CV":** a plain random split leaks co-located listings across folds and flatters the model — grouped CV is the honest estimate (our earlier random-split numbers were optimistic by ~3–4 points on lots).

**12 · From collection to a clean ABT.** The funnel: 16,561 → 3,616, ~1 in 5 kept; per-portal retention (Lamudi 1,578 + 270 browser; FilipinoHomes 1,203; DotProperty 565). Reiterate OnePropertee exclusion. **Defend the small N:** that's exactly the data-scarcity reality the literature names — and why small-sample-robust models (RF) and grouped CV matter.

**13 · The price signal — and can we trust the features?** Price per sqm is right-skewed (a few premium units) → modeled in **log**. Sharp geographic spread: Cebu City ~₱113,600/sqm, Mandaue ~₱96,100, Lapu-Lapu ~₱92,100; lower band ~₱47,100–56,800 (Talisay, Minglanilla, Consolacion). Some southern CBD distances move together — an early **collinearity** warning. MCRAI zero rates were checked *before* modeling (education/grocery near-complete; security sparsest) to separate true absence from data gaps. **Defend collinearity:** it matters for the OLS baseline (handled via VIF + per-stratum trimming); the trees tolerate correlated predictors, so we keep the substantively meaningful nodes.

**14 · Cleaning kept every decision visible.** Imputed values **flagged, never silently filled** (see the imputed-flags answer above); structurally-absent fields (lot beds/baths) left **unimputed**; hard duplicates dropped; a price-per-sqm **sanity band** removed area-entry errors; distressed / "For Assume" listings dropped (they quote loan balances, not market value). **The integrity story:** early models were dominated by one suspicious SHAP feature — the target had quietly come to mean *two different things* across scrape batches; tracing and redefining it to **log price per sqm** is why the final metrics are dependable. (This is a strength to volunteer, not hide.)

**15 · Preparing the data for modeling.** Split by property type → three datasets; encode cities as indicators; assemble structural + distance + MCRAI + benchmark + spatial-lag features. Four selection screens: **VIF** (drop duplicates), **OLS significance** (keep what moves price), **leave-one-block ablation**, **MCRAI zero rates**. Result: tailored sets of **21 / 24 / 22**. **Defend "why not one feature set":** because the screens gave different answers per stratum (next slide).

**16 · One model cannot price three markets.** The condo median price per sqm is ~**5.8×** the vacant-lot median; built area and land-only follow different price logic; a pooled model blurs them. So three separate models — and that's an evidence-based finding (Dröes 2019; Usman 2020), not a convenience.

**17 · Feature sets differ by property type.** *(Your priority slide — use the two detailed answers at the top.)* **Shared core (all three):** 8 road-network CBD distances, BIR zonal benchmark, 500 m spatial lag, city indicators (Cebu City = reference). **Differences:** condos & houses get structural attributes (area, beds, baths + **imputed flags**) and the single **MCRAI composite**; houses add property-type indicators (single-detached, house-and-lot, townhouse); vacant lots get land area only + **six individual MCRAI** categories. Final counts 21 / 24 / 22. **The defense:** collinearity shaped the OLS baseline; the deployed trees tolerate it; the strata differ mainly by *what each property type actually has*.

**18 · The model lineup — and tuning.** OLS hedonic (HC3 robust errors; Rosen 1974) as interpretable baseline + the diagnostic that screens MCRAI signs; Random Forest (Breiman 2001, deployed); XGBoost (Chen & Guestrin 2016); SHAP for explanation (Lundberg & Lee 2017). **Why these three:** they span interpretability→accuracy; SVR (hard to tune, weak interpretability), LASSO/Ridge (subsumed by OLS), and deep nets (need >10,000 samples — we have far fewer) were set aside for clear reasons. **Tuning:** the deployed RF was tuned per stratum (300 trees; max-features 0.7/1.0/1.0; min-leaf 1/2/1; random_state 42); comparators ran at standard settings so the head-to-head was fair.

**19 · Headline accuracy — all three models.** Under identical leak-free folds. **MdAPE** — OLS 24.5/25.1/44.8, **RF 19.3/22.7/38.4**, XGB 19.8/23.6/40.2 (condo/houses/lot). **PE20** — RF 51/44/26. **Defend the metrics:** MdAPE = median absolute % error (robust to a few extreme listings); PE20 = share within 20% (the practical hit-rate); MAPE/COD/PRD are supporting diagnostics. **We do not claim IAAO assessment-grade compliance** — say this before they ask. Vacant lots are weakest; that's the data ceiling, reported honestly.

**20 · Which model performed best? (RQ2).** Both tree models beat OLS in every stratum; RF edges XGBoost on grouped CV (19.3 vs 19.8 / 22.7 vs 23.6 / 38.4 vs 40.2). Because the trees are so close, the fair reading is "RF best-or-tied." **Why deploy RF over XGBoost:** robust on small samples and simpler to maintain — not a meaningful accuracy gap.

**21 · Do geospatial features earn their place? (RQ3).** Three-tier ablation under identical folds: Structural → +Administrative → +Geospatial. Geospatial improves **every** stratum vs structural-only (condo +5.7, houses +4.2, **lot +13.0**); on top of administrative location (city + BIR zonal) it still adds for condo (+3.7) and lot (+3.8), with houses roughly flat (≈ −0.7). **The headline:** geospatial features add the most where benchmarks are weakest — vertical condos and bare land. That answers "do they earn their place" with a number.

**22 · What drives price — three findings.** (1) **Location dominates** in every stratum — the geospatial block carries most of the SHAP attribution. (2) **Drivers differ by type:** condos track neighborhood price (spatial lag); houses & lots are driven by distance to **CBP** (classic bid-rent); bare land also responds to individual amenity access. (3) **MCRAI is selective** — education, grocery, recreation carry positive weight; security, tourism, retail behave as diagnostics. **Defend negative signs:** they reflect **spatial sorting** (these uses cluster where congestion/commercial intensity deters some buyers; Tiebout 1956; Bayer & McMillan 2012) — not "amenities lower value."

**23 · A polycentric price surface.** The SHAP results show the model learned a **polycentric**, not monocentric, structure: CBP anchors land and detached housing, but condo weight spreads across the Mactan/airport corridor and the Mandaue–Consolacion nodes — consistent with the JICA roadmap. **Defend Mactan:** read it as a submarket bundle (airport access, bridge connectivity, tourism-adjacent demand), not a raw island premium.

**24 · The valuation gap (RQ4).** On the clean land-to-land comparison, vacant-lot market price runs **~3× the BIR benchmark** overall — from ~**2.2× in Cebu City to ~4.8× in Mandaue**; listings exceed the benchmark in nearly every LGU. **Framing discipline:** this is a *research signal that benchmarks are stale*, **not** a correction factor to apply — say this clearly, since it's a policy-sensitive claim.

**25 · The decision-support tool.** Three views: **Market Map** (listings + filters + market intelligence), **Price Surface** (predicted price-per-sqm by barangay), **Property Predictor** (a property-level prediction with its SHAP breakdown). The backend runs the **exact deployed Random Forest models** — the tool always shows its reasoning. **Defend scope:** market_segment is fixed to open_market for the deployed surface.

**26 · Answers, contributions, limits.** RQ1–4 in one line each. Contributions: per-type modeling with evidence-based feature selection; a polycentric distance set; a two-stage MCRAI; all results under leak-free grouped CV; a reproducible, explainable web prototype. **Volunteer the limits:** asking-price ceiling (listings, not deeds-of-sale); cross-sectional snapshot; vacant-lot data ceiling (parcel attributes like frontage/zoning/slope/titling aren't in listings); thin LGU×type cells. Owning the limits is the strongest defensive posture.

**27 · For practice and policy.** Practice: read the surface as a **triangulation tool** alongside zonal values and comparables — not a final appraisal; weight polycentric distance and property type ahead of the amenity composite. Policy: keep recognizing secondary/corridor subcenters (Mactan, Consolacion, Naga), not just CBP; treat the valuation gap as a research signal and validate against transactions before any operational use.

**28 · For future research.** Put MCRAI on an empirical footing (estimate the decay rate, radii, weights from data rather than fixing them); test spatial heterogeneity directly with GWR/MGWR; enrich inputs (parcel attributes, a time dimension, macro indicators; Udomsap & Abid 2020); triangulate against complementary reference prices instead of a single market-facing target.

---

## Likely panel questions — quick answers

- **"Why listings, not actual sale prices?"** Deed-of-sale data isn't publicly accessible at scale in the Philippines; listings are the only property-level open-market source. We treat the asking-price ceiling as a named limitation, and RQ4 actually measures how listings sit relative to the official benchmark.
- **"Isn't 3,616 too small?"** That small-N reality *is* the problem the literature names; we chose small-sample-robust methods (Random Forest), leak-free grouped CV (no optimistic leakage), and report MdAPE/PE20 honestly rather than claiming assessment-grade accuracy.
- **"Why is the vacant-lot model so much worse?"** A data ceiling: the parcel attributes that actually drive land value (frontage, corner-lot, zoning, slope, titling) aren't recorded in listings. The model can't price what it can't see — so it over-predicts atypically cheap lots. Reported transparently, not hidden.
- **"Why not deep learning?"** It needs >10,000 labeled samples and sacrifices the explainability the use case requires; with this sample size and the need for SHAP-level transparency, tree ensembles are the defensible choice.
- **"Is this IAAO compliant?"** No, and we don't claim it. IAAO ratio-study bands are in-sample assessment-roll standards; our numbers are stricter out-of-sample grouped-CV estimates for a decision-support prototype.
