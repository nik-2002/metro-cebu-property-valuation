# Philippine-Grounded Comparable Studies (2026-06-13)

> Feeds Chapter 2 (RRL) and Chapter 7 (a fair *local* benchmark — more apt than Zillow/global AVMs).
> ⚠ = verify the primary source (title/authors/metrics) before citing. Never cite from these search
> summaries directly — confirm DOI/PDF. (CLAUDE.md citation rule.)

## The closest comparables

**1. Ramolete, Bramaskara, Reyes & Heinrich (2023) — "Utilization of Machine Learning, Government-Based and Non-Conventional Indicators for Property Value Prediction in the Philippines."** *The Philippine Statistician*, Vol. 72, No. 1. **The near-perfect comparable** — verified from the full PDF (text-extracted):
- **Data:** **Lamudi property listings** (scraped via **BeautifulSoup** — same source AND scraper family as this thesis) for **Cavite + Metro Manila** (3,212 houses in Cavite), overlaid with **OSM amenities/buildings**, plus **PSA socio-economic data** and the **DTI 2021 National Competitiveness Index** (government indicators).
- **Models:** Decision Tree, Gradient Boosting Machine, Random Forest, Extremely Randomized Trees, **XGBoost**, LightGBM, AdaBoost. AdaBoost "performed most reliably" in the non-segmented setup.
- **Evaluation:** **80/20 random train-test split** (NOT leak-free / not coordinate-grouped — important for fair comparison).
- **Headline metric: MAPE 10.7–21%** (also reports Mean AE). Metric is a range across areas/segments.
- **Two findings that validate this thesis's design:** (a) **government indicators substantially improve performance** → this thesis's **BIR zonal feature**; (b) a **segmented approach** (K-Means / BIRCH clustering) lowers error → this thesis's **property-type stratification** (Decision 27).
- https://www.psai.ph/docs/publications/tps/tps_2023_72_1_1.pdf · https://www.psai.ph/tps_details.php?p=1&id=157

**Parallel + differentiation (use this in Ch2/Ch7):** Ramolete et al. is the same recipe — Lamudi + OSM + tree-based ML + segmentation, Philippines — but in **Cavite/Metro Manila** with a **random split** and **socio-economic/competitiveness** features. This thesis differentiates by: **Cebu**, **network-distance + MCRAI + spatial-lag** geospatial engineering, **BIR-zonal** anchoring, and **leak-free GroupKFold** evaluation.

**⚠ Quantified 2026-06-14 (`ramolete_replication_2026-06-14.md`) — do not overclaim "we're just more honest."** We re-ran our models under their random 80/20 protocol. The protocol switch improves RF MAPE by only **2–5pp** (Condo +5.1, Houses +1.9, Lot +3.4), so evaluation honesty explains only a *small* slice of the gap. Even under their split our MAPE is **~30%**, still above their 10.7–21%; the rest is a genuine difference (their 3,212 houses vs our 674, thinner Cebu market, their PSA/DTI features, AdaBoost/segmentation). The fair, defensible point: our RF **MdAPE** (typical error) under the random split is **15.9% (condo) / 21.3% (houses)** — at the top of their MAPE band — so the *median* property is competitive; a tail of hard properties inflates the mean.

**2. "Determinants of Land Values in Cebu City, Philippines" (2017).** Presented at the International Conference on Business and Economy, University of San Carlos, Cebu City, Feb 17–18, 2017. **Same city as this thesis.** 31 land-value determinants; survey of 52 practitioners/valuers/assessors (5-pt Likert); factor analysis + PCA + multiple regression (SPSS); GIS factor maps + MCA. **Ranks mobility (transport access) #1 and livability (open space/parks/neighborhood) #2.** The project already cites this as "Agosto (2017)" — ⚠ confirm the author name on Zenodo.
- https://zenodo.org/records/7018951 · https://www.researchgate.net/publication/345343910

**3. Manila City House Prices: A Machine Learning Analysis of the Current Market Value for Improvements (Springer, 2023).** Models: Linear Regression, Bayesian Ridge, Gradient Boost, Lasso (+ feature selection + Genetic Algorithm optimization). **Best = Gradient Boost: R² = 0.7508, EVS = 0.7640** (no MAPE/RMSE reported in the abstract). Note: predicts **value of improvements (structure)** from **structural attributes** (floor area, storeys, structure type) — **no geospatial features** — so it's a *structural-only* PH ML reference, narrower than this thesis. ⚠ verify authors/year from primary (Springer paywalled; metrics triangulated across Springer + ResearchGate summaries).
- https://link.springer.com/chapter/10.1007/978-3-031-36246-0_29 · https://www.researchgate.net/publication/375568226

**4. Hedonic Modeling for Predicting House Prices during COVID-19 in the Philippines (ACM, 2021).** Hedonic/regression approach; PH context. ⚠ verify.
- https://dl.acm.org/doi/10.1145/3460824.3460828

## Institutional / policy grounding
- **BSP Residential Property Price Index** — from Q1 2025 uses a **hedonic regression** methodology incorporating location, size, type. (Validates hedonic features as the PH standard.)
- **Real Property Valuation and Assessment Reform Act (RPVARA)** + the "60% of LGUs updated zonal values" gap — the policy backdrop for the thesis problem (modernizing PH valuation). PwC 2024 overview: https://www.pwc.com/ph/en/tax/tax-publications/taxwise-or-otherwise/2024/modernizing-property-valuation.html
- BIR zonal value system: adjusted every 3 years, minimum taxable value/sqm; ~60% LGU update rate (already in Ch1).

## Why this matters for the thesis (two payoffs)

**A. It confirms the novelty gap (supports your RQ/contribution).** No existing PH study combines all of: **Cebu** + **property-level** prediction + **GIS-engineered geospatial features (network distance, MCRAI, spatial lag)** + **ML (RF/XGB)** + a **deployable decision-support tool**. The Cebu 2017 study is survey/SPSS-based (not property-level ML, not deployable); the ML studies are Manila-centric and not GIS-rich. Your "first Cebu-specific, GIS-augmented, property-level ML valuation + decision support" claim holds against the PH literature.

**B. It gives a fair LOCAL benchmark (better than Zillow).** Against comparable PH ML work (e.g., Manila Gradient Boost R² ≈ 0.75 on total price, random split), a Cebu per-sqm stratified RF under **leak-free** CV in a thinner market is a reasonable result — and is more rigorously evaluated. This is the apt comparison to make in Chapter 7, not Zillow's 1.74%/7.2% (transaction data, millions of rows).

**Convergent validity bonus:** the Cebu 2017 study independently ranks **transport/mobility #1** and **livability/amenities #2** — which matches this thesis's RQ1 finding that **location (CBD/road access) dominates** and amenity (MCRAI) access matters. Two independent methods, same Cebu conclusion → strengthens RQ1.

## Action items
- [ ] Verify + add to `biblio.bib`: Ramolete et al. (2023); Cebu 2017 land-values (confirm author); Manila ML (2023); ACM hedonic COVID (2021).
- [ ] Ch2 RRL: add a "PH/Cebu valuation studies" paragraph using #1–#4 + the gap statement (A).
- [ ] Ch7: benchmark against the PH ML studies (B), not just global AVMs.
