# Defense Q&A Booklet — slide by slide

Merges the **presenter notes** (what to say) with the **modeling rationale pack** (the deep "why," grounded in the decision log × manuscript). Keyed to the 28 slides of `Defense Deck-Claude Design.html`.

For each slide: **Say** (the spoken line), **Defend** (likely questions), and **▸ Deep defense** where a panelist will push on a modeling decision.

> **Figures to know cold:** ABT **3,616** rows (3 portals); modeling subset **3,372**; strata **Condo 1,300 / Houses 1,223 / Lot 849**; target **log(price/sqm)**; deployed **Random Forest**; leak-free **GroupKFold(5)** by coordinate cluster. **MdAPE 19.3 / 22.7 / 38.4** · **PE20 51 / 44 / 26** (condo/houses/lot). 3-model MdAPE: OLS 24.5/25.1/44.8 · **RF 19.3/22.7/38.4** · XGB 19.8/23.6/40.2.
>
> **Number-provenance trap:** older reports show Lot ~25% / Condo 15.9% — those predate the data expansion or used a leaky split. The **final, leak-free, post-expansion** numbers are above. If a panelist quotes an old figure, point to the deployment manifest.

---

## 1 · Title
**Say:** Title, your name, program. Frame it: an open-market residential valuation study for Metro Cebu using ML + geospatial features — a **decision-support prototype**, not a replacement for appraisal.

## 2 · Outline
**Say:** "The talk follows the CRISP-DM arc mapped to the thesis chapters — problem, literature, methodology, the data, modeling, evaluation, results, the tool."

## 3 · Where this study is set
**Say:** Six LGUs (Cebu City, Mandaue, Lapu-Lapu, Talisay, Minglanilla, Consolacion). The timing matters: Cebu grew **7.3%** in 2024 (PSA); residential prices rose **11.5%** in 2025 (BSP, highest outside NCR) — prices move faster than the references people use to read them.

## 4 · The fragmented-references problem
**Say:** No single public source answers "what is this worth." Price is pieced from four partial references — broker opinion, bank appraisals, BIR zonal values, online listings — each built for a *different* purpose, so they can't be compared.
**Defend (BIR):** zonal values are for taxation, not live market value, and are often stale (Otsuka et al., 2023) — that gap is exactly RQ4.

## 5 · The problem, research questions & scope
**Say:** *Metro Cebu lacks a transparent, property-level, spatially detailed reference for interpreting residential price evidence.* Then RQ1–RQ4. State scope proactively: **open-market segment only** for the deployed model; cross-sectional snapshot, late 2025; a prototype tool.
**▸ Deep defense (scope, Decision 54/56):** bank-ROPA and floor-price tiers were dropped from the research — the deployed surface is open-market only. The web app is a **prototype for triangulation, not a stand-alone valuation tool**; institutional-use claims (BIR/LGU/lenders *using* it) were removed.

## 6 · The core obstacle — and the gap it leaves
**Say:** The binding constraint in developing markets is **data scarcity, not valuer misconduct**: Kenya, 427 valuers ranked "limited information" #1 (Cheloti, 2021); Nigeria, **92.7%** of 300 valuers cited insufficient market evidence (Ajibola, 2010). The gap: no published, reproducible, property-level Metro Cebu model integrates open-market listings, geospatial accessibility, and explainable ML.

## 7 · Two modeling traditions — and why we stratify
**Say:** Hedonic regression (interpretable, one coefficient per attribute; Rosen 1974) vs. ML (non-linear, interacting; Breiman 2001; tree ensembles win on tabular data, Grinsztajn 2022).
**▸ Deep defense (stratification, Decision 27):** the decision to split by property type is **EDA-driven, not preference**. Condo median price/sqm is **5.8×** the lot median; CV differs sharply (Condo 0.44, Houses 0.68, **Lot 1.28**); and the *correlation structure differs by stratum* — condos driven by compact-unit area + recreation; houses & lots by BIR zonal + CBD distance, structural features irrelevant for lots. Literature: Dröes et al. (2019) R² 0.637→0.782; Usman et al. (2020) fit +7%, error −10%.
*If challenged ("just slicing a small dataset thinner?"):* each stratum has ≥849 rows and all six LGUs; removing cross-type noise outweighs the smaller n, and the literature shows it.

## 8 · Research design and the data pipeline
**Say:** Quantitative, non-experimental; predictive (estimate price) + prescriptive (surface the gap). Pipeline: **Ingest → Clean → Geocode → BIR join → Geospatial features → ABT**. 16,561 raw across Lamudi / FilipinoHomes / DotProperty; **3,616** clean, 51 columns.
**Defend (why only cleaning prunes):** geocoding/BIR/geospatial steps *add columns*, not drop rows — the 16,561→3,616 attrition is cleaning + scope filters.
**▸ Deep defense (cleaning, Decision 33/41b/47):** OnePropertee excluded entirely (mis-extracted per-sqm prices + city-centroid geocoding = contamination); distressed/"For Assume" removed (loan balances, not market value); hard duplicates dropped; a **spatial cap** prevents dense clusters dominating a stratum; a per-stratum price-per-sqm **sanity band** removes area-entry errors.

## 9 · Geospatial features — distance to economic centers
**Say:** Shortest-path **road-network distance** (osmnx, Dijkstra; Haversine fallback only when a point won't snap) to **eight** nodes — CBP, Mandaue, Mactan, SRP, Talisay Tabunok, Consolacion, Naga, airport.
**Defend (node choice):** polycentric urban economics (Giuliano & Small 1991), grounded locally in the JICA Mega Cebu roadmap (2015).
**Defend (road vs straight-line):** road distance captures real travel cost incl. the Mactan bridge — that's why Mactan-island distances inflate (expected, not an error). Transport accessibility is carried by these node distances, which is why transport isn't a separate amenity category.

## 10 · MCRAI — measuring access to amenities
**Say:** Gravity idea: for each property, sum nearby amenities in a category, weighted by 1/distance² (decay β=2), floored at 0.5 km; each category has its own reach. Show the formula image.
**▸ Deep defense (MCRAI form, Decision 18/30/56):** Hansen (1959). Category radii (km): education 2.5, grocery 2.0, health 2.0, hospitals 5.0, recreation 1.5, security 2.0, tourism 3.0, retail 1.0 — catchment scales (education widened from a PH learner home-to-school survey; hospitals from tertiary-care catchment). **Own the limitation:** β=2 and the radii are **judgment-based baselines** (conventional inverse-square gravity; standard catchment scales), **not** estimated from Cebu data — only the weights are. This is in Ch3 after the radii table and leads Future Research. *Don't defend β=2 as derived — concede it.* **OHANA:** MCRAI *replaced* OHANA; it is not "based on" it.

## 11 · MCRAI weights — and the evaluation protocol
**Say (weights):** Two-stage, not assumed. **Stage 1** — hedonic OLS gives each category's *implicit price* (sign = premium/penalty, significance = reliable). **Stage 2** — keep the positive, significant categories, normalize coefficients to sum to one → **education 0.447, grocery 0.345, recreation 0.222**. Security/tourism/retail stay standalone, not in the composite.
**Say (protocol):** **GroupKFold(5)** grouped by **coordinate cluster** — same location never in both train and test folds; every headline number is out-of-fold.
**▸ Deep defense (eval, Decision 41c/42a):** two reasons for grouped CV. (1) ~109/301 lot rows shared coordinates (centroid geocodes + relistings), so a plain split leaks near-identical neighbors and **flatters** the model — the old Condo 15.9% was optimistic from exactly this. (2) The deliverable is a **price surface predicting at arbitrary locations**, so testing on held-out *locations* is the realistic test.

## 12 · From collection to a clean ABT
**Say:** Funnel 16,561 → 3,616, ~1 in 5 kept; per-portal retention (Lamudi 1,578 + 270 browser; FilipinoHomes 1,203; DotProperty 565). OnePropertee excluded.
**Defend (small N):** that small-N reality *is* the data-scarcity problem the literature names — and why small-sample-robust methods (RF) and leak-free grouped CV matter.

## 13 · The price signal — and can we trust the features?
**Say:** Price/sqm is right-skewed → modeled in **log**. Geographic spread: Cebu City ~₱113,600/sqm, Mandaue ~₱96,100, Lapu-Lapu ~₱92,100; lower band ~₱47,100–56,800 (Talisay, Minglanilla, Consolacion). Some southern CBD distances move together — a **collinearity** warning. MCRAI zero rates checked *before* modeling (education/grocery near-complete; security sparsest).
**▸ Deep defense (target = log price/sqm, Decision 34):** per-sqm normalizes for size so the model learns *value density*, not "bigger = pricier" (total price = pred × area); logging stabilizes the skew (Rosen 1974). **The integrity catch:** an earlier `log_price` was computed inconsistently across scrape batches — the target quietly meant two things and one feature dominated SHAP as a hidden scale-selector. Redefining it to log price/sqm is why the metrics are dependable.
**▸ Deep defense (collinearity, Decision 11/12/32):** matters for the OLS baseline (trimmed per stratum via VIF; `mcrai_composite` had VIF ~10¹¹ as a deterministic blend; raw vs log BIR de-duplicated). The **trees tolerate** correlated predictors, so all 8 CBD nodes are kept — dropping them throws away real location signal.

## 14 · Cleaning kept every decision visible
**Say:** Imputed values **flagged, never silently filled**; structurally-absent fields (lot beds/baths) left **unimputed**; duplicates dropped; price-per-sqm sanity band; distressed/"For Assume" removed.
**▸ Deep defense (imputed flags):** `bedrooms_imputed`/`bathrooms_imputed` are 0/1 columns — **0 = observed, 1 = filled** (median by property type + city). They let the model tell a *real* 3-bedroom from a *guessed* one, so imputed values don't masquerade as fact. Lots have no flags because beds/baths are **structurally absent** (nothing to impute) — that's why the lot structural block is just `area_sqm`.
**▸ Deep defense (area, Decision 31):** `area_sqm` is unified (floor area for condo/house, lot area for lots) and rows with **null area are dropped, not imputed** — imputing area distorts the per-sqm target and inflates apparent precision.

## 15 · Preparing the data for modeling
**Say:** Split by type → three datasets; encode cities as indicators; assemble structural + distance + MCRAI + benchmark + spatial-lag features. Four screens: **VIF** (drop duplicates), **OLS significance** (keep what moves price), **leave-one-block ablation**, **MCRAI zero rates**. Result: **21 / 24 / 22**.

## 16 · One model cannot price three markets
**Say:** Condo median price/sqm ~**5.8×** the lot median; built area and land-only follow different price logic; a pooled model blurs them. Three separate models — an evidence-based finding (Dröes 2019; Usman 2020), not a convenience. *(Stratification deep dive is on slide 7.)*

## 17 · Feature sets differ by property type — *your priority slide*
**Say:** **Shared core (all three):** 8 road-network CBD distances, BIR zonal benchmark, 500 m spatial lag, city indicators (Cebu City = reference). **Differences:** condos & houses get structural attributes (area, beds, baths + **imputed flags**) and the single **MCRAI composite**; houses add property-type indicators; vacant lots get land area only + **six individual MCRAI** categories. Counts 21 / 24 / 22.
**▸ Deep defense — MCRAI composite (condo/house) vs individuals (lot), Decision 49 (the strong, tested version):**
- For **condo/house**, the composite (1 feature) **empirically beats** its three raw constituents: Condo **19.32 vs 19.82**, Houses **22.67 vs 22.91** — lower error, fewer features. The Stage-1-OLS weights act as **regularization** (one stable accessibility signal vs three correlated raw scores), and the composite **is** the MCRAI index — the thesis construct. Condo/house deploy the **index**.
- For **vacant lots**, carrying both composite + individuals is **exact collinearity** (regress composite on the 8 individuals → **R² = 1.0000**). Harmless to RF prediction but it **corrupts SHAP** (splits accessibility between the composite and its own parts), so the composite is **dropped from lot**; lots keep the **individuals** because bare land reads *specific* amenity access. Lots also drop **security** (36.9% zero-rate OSM coverage gap, lowest RF importance 2.14%) and **retail density** (≈ noise correlation).
- **Manuscript framing (Ch3):** for built homes the categories are inter-correlated (~0.57–0.96) and behave as one accessibility summary; bare land responds to specific access. Same conclusion.
- **One-liner:** *"Built homes deploy the MCRAI index because it empirically beats the raw categories and regularizes a noisy signal; bare land deploys the individual categories — and keeping both in the lot model was exact collinearity that corrupts the SHAP story, so the composite was dropped there."*

## 18 · The model lineup — and tuning
**Say:** OLS hedonic (HC3; the MCRAI-sign diagnostic), Random Forest (deployed), XGBoost, SHAP (Lundberg & Lee 2017). **Why these three:** span interpretability→accuracy; SVR (hard to tune, weak interpretability), LASSO/Ridge (subsumed by OLS), deep nets (need >10,000 samples) set aside.
**▸ Deep defense (deployment, Decision 40/42):** RF deployed for all three. Under leak-free group-CV the tree models are within noise (19.3 vs 19.8 / 22.7 vs 23.6 / 38.4 vs 40.2); RF is **best-or-tied**, robust on small samples, simpler — Decision 42 explicitly *reverted* an earlier Houses→XGBoost switch that won on a 0.22pp k-fold edge (noise). **Tuning:** RF tuned per stratum by group-CV MdAPE — 300 trees; max-features 0.7/1.0/1.0; min-leaf 1/2/1; max-depth none; random_state 42. Comparators at standard settings for a fair head-to-head.
**▸ Deep defense (OLS diagnostics, Decision 32):** Breusch-Pagan confirms heteroscedasticity, Jarque-Bera fails normality (condo/houses) → OLS reported with **HC3 robust errors**. These are *OLS-inference* issues; the deployed Random Forest assumes neither constant variance nor normality, so they don't threaten the deployed model.

## 19 · Headline accuracy — all three models
**Say:** Under identical leak-free folds. **MdAPE** — OLS 24.5/25.1/44.8, **RF 19.3/22.7/38.4**, XGB 19.8/23.6/40.2. **PE20** — RF 51/44/26. MdAPE = median % error (robust); PE20 = share within 20%. **We do not claim IAAO assessment-grade compliance.**
**▸ Deep defense (COD/PRD vs IAAO, Decision 42d):** under honest out-of-sample CV all strata sit at COD ~33–56 and PRD ~1.2–1.5, above the strict in-sample bands — a data/feature + harder-test property, not a defect. IAAO bands are *in-sample assessment-roll* standards on large samples; ours are *stricter out-of-sample* estimates for a prototype.

## 20 · Which model performed best? (RQ2)
**Say:** Both tree models beat OLS in every stratum; RF edges XGBoost on grouped CV; "RF best-or-tied." Deployed RF for robustness + simplicity, not a meaningful accuracy gap. *(Deployment deep dive on slide 18.)*

## 21 · Do geospatial features earn their place? (RQ3)
**Say:** Three-tier ablation under identical folds: Structural → +Administrative → +Geospatial. Geospatial improves **every** stratum vs structural-only (condo +5.7, houses +4.2, **lot +13.0**); on top of admin location it still adds for condo (+3.7) and lot (+3.8), houses roughly flat (≈ −0.7). The headline: geospatial features add the most **where benchmarks are weakest** — vertical condos and bare land.

## 22 · What drives price — three findings
**Say:** (1) **Location dominates** in every stratum — geospatial block carries most SHAP attribution. (2) **Drivers differ by type:** condos track neighborhood price (spatial lag); houses & lots driven by distance to **CBP** (bid-rent); bare land also responds to individual amenity access. (3) **MCRAI is selective** — education, grocery, recreation positive; security, tourism, retail are diagnostics.
**Defend (negative signs):** **spatial sorting** — these uses cluster where congestion/commercial intensity deters some buyers (Tiebout 1956; Bayer & McMillan 2012) — not "amenities lower value."

## 23 · A polycentric price surface
**Say:** SHAP shows a **polycentric**, not monocentric, structure: CBP anchors land and housing, but condo weight spreads across the Mactan/airport corridor and the Mandaue–Consolacion nodes — consistent with the JICA roadmap.
**Defend (Mactan):** a submarket bundle (airport access, bridge connectivity, tourism-adjacent demand), not a raw island premium.

## 24 · The valuation gap (RQ4)
**Say:** On the clean land-to-land comparison, vacant-lot market price runs **~3× the BIR benchmark** overall — ~**2.2× in Cebu City to ~4.8× in Mandaue**; listings exceed the benchmark in nearly every LGU.
**Framing discipline:** a **research signal that benchmarks are stale**, **not** a correction factor to apply — say this clearly (policy-sensitive).

## 25 · The decision-support tool
**Say:** Three views — **Market Map** (listings + filters + market intelligence), **Price Surface** (predicted price/sqm by barangay), **Property Predictor** (a prediction with its SHAP breakdown). The backend runs the **exact deployed Random Forest models**; market_segment fixed to open_market.
**Defend (practical use):** a prototype/triangulation layer that complements professional appraisal — validate against recorded transactions before any operational use.

## 26 · Answers, contributions, limits
**Say:** RQ1–4 in one line each. Contributions: per-type modeling with evidence-based feature selection; a polycentric distance set; a two-stage MCRAI; all results under leak-free grouped CV; a reproducible, explainable web prototype.
**▸ Deep defense (vacant-lot ceiling, Decision 41):** Lot is the weakest stratum (MdAPE 38.4, COD 55.9) — a **data/feature ceiling, not a modeling failure**. It was scope-filtered (area ∈ [80, 2000] sqm; price ≥ 0.5× BIR zonal) to remove development land and data errors; residual error is driven by lot attributes **absent from listings** (frontage, zoning, titling, corner, slope). Crucially RF still **beats naive baselines** on the same CV (BIR-zonal MdAPE 66.7 / city-median 26.9 / RF far better). **Volunteer the limits:** asking-price ceiling (listings, not deeds); cross-sectional snapshot; vacant-lot data ceiling; thin LGU×type cells.

## 27 · For practice and policy
**Say:** Practice — read the surface as a **triangulation tool** alongside zonal values and comparables, not a final appraisal; weight polycentric distance and property type ahead of the amenity composite. Policy — keep recognizing secondary/corridor subcenters (Mactan, Consolacion, Naga); treat the valuation gap as a research signal and validate against transactions before operational use.

## 28 · For future research
**Say:** Put MCRAI on an **empirical footing** (estimate β, radii, weights from data rather than fixing them) — this leads the list; test spatial heterogeneity directly with GWR/MGWR; enrich inputs (parcel attributes, a time dimension, macro indicators; Udomsap & Abid 2020); triangulate against complementary reference prices, not a single market-facing target.

---

## Appendix — Likely panel questions (rapid answers)

- **"Why listings, not actual sale prices?"** Deed-of-sale data isn't publicly accessible at scale in the Philippines; listings are the only property-level open-market source. We name the asking-price ceiling as a limitation, and RQ4 measures how listings sit vs the official benchmark.
- **"Isn't 3,616 too small?"** That small-N reality *is* the problem the literature names; we chose small-sample-robust methods (RF), leak-free grouped CV (no optimistic leakage), and report MdAPE/PE20 honestly rather than claiming assessment-grade accuracy.
- **"Why is the vacant-lot model so much worse?"** A data ceiling — the attributes that drive land value (frontage, corner, zoning, slope, titling) aren't in listings; n is thin. Reported transparently; still beats the BIR benchmark and a city-median heuristic.
- **"Why not deep learning?"** Needs >10,000 labeled samples and sacrifices the SHAP-level explainability the use case requires; with this sample size, tree ensembles are the defensible choice.
- **"Is this IAAO compliant?"** No, and we don't claim it. IAAO bands are in-sample assessment-roll standards on large samples; ours are stricter out-of-sample grouped-CV estimates for a decision-support prototype.
- **"Why composite for condos/houses but individual MCRAI for lots?"** → slide 17 deep defense (composite empirically beats raw categories + regularizes; lots had exact R²=1.0 collinearity that corrupts SHAP, so the composite was dropped there).
- **"Your MCRAI parameters look arbitrary."** Partly true and owned — the decay (β=2) and radii are defensible conventions, the *weights* are estimated from Cebu's market, and making the whole feature computation empirical is the lead future-research item. (Don't defend β=2 as derived.)
- **"VIF > 5 — isn't that a problem?"** Only for OLS coefficient interpretation, which is why we trim it there and report HC3 errors; the deployed Random Forest handles correlated features and the decision is logged.
- **"Your COD/PRD fail IAAO."** Correct, stated openly — different (harder, out-of-sample) test than the in-sample roll standard; the model is a prototype, not an assessment roll.
- **"If a panelist quotes Lot ~25% or Condo 15.9%."** Those predate the 3-portal data expansion or used a leaky split; the final leak-free numbers are 19.3 / 22.7 / 38.4 (deployment manifest).
