# Chapter Correction Checklist — from the 2026-06-13 verification sprint

> Exact manuscript edits to make in the NEXT loop (prose rewriting was deliberately
> deferred). Every item is grounded in code or in Decision 44. Do not edit chapters
> until the RQ2/RQ3/RQ4 analysis numbers are in (`model_comparison_groupcv.csv`,
> `ablation_groupcv.csv`, `valuation_gap_summary.csv`).

## Research Re-Alignment — paste-ready RQ + contribution wording (decided 2026-06-13)

These re-worded statements match the honest findings (Decision 44f). Use them in Ch1 §Research Questions and §Significance.

**RQ1 (unchanged):** What value drivers significantly influence residential property prices in Metro Cebu?
- *Answer (deployed-RF importance):* **location dominates** — geospatial/location features are 75–84% of model importance across all strata. **Vacant Lot:** distance-to-CBP alone = **47%** (land value ≈ location; consistent with bid-rent, Alonso/Muth). **Houses:** dist-CBP 24% + size + neighbourhood (spatial lag) + road/health access. **Condo:** more balanced — size (16%), neighbourhood price level (spatial lag 14%), lifestyle amenities (recreation/tourism), airport. *Caveat:* impurity importance favours continuous features; ablation + univariate correlations agree location dominates. *Note the importance↔ablation reconciliation:* geospatial features are what the model **uses** (high importance), while city+BIR are a **redundant substitute** that cushions the ablation for houses/lots (not condos — RQ3).

**RQ2 (reframed — "most suitable for deployment," not "lowest MAPE"):** Among Hedonic Regression (OLS), Random Forest, and XGBoost, which model is most suitable for deployment, balancing out-of-sample accuracy (MdAPE/PE20), robustness on small per-stratum samples, and interpretability?
- *Answer:* the tree models clearly outperform the hedonic OLS baseline; Random Forest and XGBoost perform equivalently (within ~1.3pp, i.e. sampling noise); Random Forest is deployed for its robustness on small samples and deployment simplicity, not a decisive accuracy edge.

**RQ3 (reframed — headline YES + decomposition):** Do geospatial features — proximity to economic nodes, MCRAI accessibility, and spatial autocorrelation — improve valuation accuracy over a structural-only model, and how does that contribution differ across property types?
- *Answer:* **yes for all three strata** vs structural-only (Vacant Lot +15.7pp, Condo +3.9pp, Houses +2.8pp MdAPE). Decomposition: the **engineered geospatial features carry the gain for condominiums**, while for houses and lots most of the locational signal is already captured by **administrative location (city + BIR zonal value)**. The model therefore adds the most value where administrative benchmarks are weakest.

**RQ4 (minor):** How large is the valuation gap between the model's data-driven predictions and BIR zonal values across Metro Cebu?
- *Answer:* large and positive everywhere (95–100% of listings exceed BIR). Clean land-to-land comparison (vacant lots): market ≈ 2–4× BIR. (Caveat condo/house % — land-vs-floor unit mismatch.)

**Re-aligned contribution (for §Significance / abstract):** A Cebu-specific, property-level valuation model whose geospatial features and stratified design add the most value precisely where administrative benchmarks fail (vertical condominiums), and which quantifies a large, systematic gap between market prices and BIR zonal values — delivered as QGIS layers and a Streamlit decision-support app.

---

## Chapter 1 — Problem & Setting
- [ ] **RQ2 + RQ3 wording (§Research Questions):** replace with the re-aligned statements in the "Research Re-Alignment" section above (RQ2 → "most suitable for deployment"; RQ3 → headline-yes + decomposition). Metric is MdAPE/PE20.
- [ ] **§1.6 Model Selection:** keep OLS/RF/XGB framing, but state the **deployment verdict explicitly**: RF deployed, XGB tested-not-retained, OLS diagnostic — and give the *why* (Decision 44d), not only the metric.
- [ ] **Abstract + Ch1 "IVS 2025":** resolve the bib-key mismatch (biblio.bib has `ivs2020`; prose says "IVS 2025"). Either add the correct IVS edition entry or align the prose to the cited edition. (carried over from task.md)
- [ ] Confirm "eight polycentric CBD nodes" wording matches the 8 used in code (CBP, Mandaue, Mactan, SRP, Talisay-Tabunok, Consolacion, Naga, Airport).
- [ ] **Abstract** — the line "the baseline Random Forest was retained ... because it delivered the strongest overall held-out performance" is no longer supported (RF ≈ XGB under leak-free CV). Soften to: "Random Forest and XGBoost performed comparably; Random Forest was deployed for its robustness on small per-stratum samples and deployment simplicity." Also align the abstract to the open-market-only deployed scope and MdAPE/PE20 metrics.

## Chapter 3 — Methodology (largest changes)
- [ ] **Data gathering — tell the two-scraper-generation story.** §3.4 currently says only "Lamudi listings were collected through a custom web scraper" (line ~96) and lists "Requests" as a tool — it omits the real history. Document both generations using the verified funnel in `reference/data_collection_funnel.csv`: (1) the **legacy `requests` + BeautifulSoup scraper** — **4,477 raw → 1,419 unique in-scope**, the bulk that became the ~1,579 open-market pre-batch ABT; (2) the **Playwright browser scraper** added in 2026-06 after **Lamudi deployed a JS-challenge / CAPTCHA wall** the `requests` scraper couldn't pass — **665 raw → 275 net-new**. Drop the funnel table straight into §3.4. (NB: count parsed rows, not `wc -l` — the description field has embedded newlines.) Decision-log history is consolidated in **Decision 45**.
- [ ] **MCRAI radii** — replace any 5km/finance-3km text with the **code values**: education 2.5km, health 2.0km, hospitals 5.0km, grocery 2.0km, security 2.0km, tourism 3.0km, recreation 1.5km, retail 1.0km; β=2.0, 0.5km floor. (Decision 44a)
- [ ] **MCRAI composite** — state it is **3 categories**: education 0.447, grocery 0.345, recreation 0.222. Note transport moved to road-distance features and finance was retired. Remove the 4-category/transport-weight description. (Decision 44a; Decisions 28–29)
- [ ] **Transport accessibility** — describe via `dist_to_trunk_road_m` / `dist_to_primary_road_m`, NOT a transport-MCRAI category.
- [ ] **Strata counts** — Condo 687, Houses 674, Lot 255 (from abt_clean 1,849×51). Replace 654/558/204.
- [ ] **Target** — `log_price = log(price_per_sqm)`; predict per-sqm, ×area for total.
- [ ] **Evaluation protocol** — describe **GroupKFold(5) by coordinate cluster** (leak-free) and MdAPE/PE20 + COD/PRD panel; do not claim IAAO compliance.
- [ ] **Hyperparameter tuning** — document both grids (RF: n_estimators/max_features/min_samples_leaf/max_depth; XGB: n_estimators/max_depth/learning_rate/subsample), the **MdAPE-under-GroupKFold** selection, and the per-stratum best params (tables in walkthrough §4). Reference the elbow-method sweep plots in `EDA/plots/11_hyperparameter_tuning/` and the results table `EDA/tables/hpo_*` as methodology evidence. Note a wider exploratory search confirmed the deployed settings.
- [ ] **Deployment** — RF per stratum is deployed; OLS is the comparator baseline; XGB was evaluated under the same protocol (RQ2).
- [ ] **Lot scope filter** — 80–2000 sqm AND price ≥ ½ BIR zonal (Decision 41).

## Chapter 7 — Results
- [ ] Insert the **RQ2 head-to-head table** from `model_comparison_groupcv.csv`: OLS vs RF vs XGB per stratum, all under the same GroupKFold. **Honest finding:** tree models beat OLS; **RF ≈ XGB (tied within ~1.3pp = noise)**. Frame RF deployment as parsimony/robustness, NOT a decisive accuracy win. Do not claim RF is "the most accurate."
- [ ] Insert the **RQ3 ablation table** from `ablation_groupcv.csv` (Structural → +Admin → +Geospatial). **Headline:** geospatial+location features improve **all three strata** vs structural-only (Lot +15.7pp, Condo +3.9pp, Houses +2.8pp MdAPE) → RQ3 = YES. **Decomposition:** engineered geospatial carries condos; administrative location (city+BIR) carries houses/lots. Present both — headline yes, then the nuance.
- [ ] Replace any single-split / MAPE-only results with the leak-free MdAPE/PE20 numbers (Condo 20.1/49.8, Houses 22.1/45.0, Lot 25.6/41.6).
- [ ] **Benchmarking note** — add a short subsection positioning the models against external AVM benchmarks (see `reference/avm_benchmarks_2026-06-13.md`): IAAO ratio-study COD 5–15/PRD 0.98–1.03, IAAO AVM acceptance (⚠ verify), Zillow median error 1.74% on-market/7.20% off-market, academic ML MAPE ~7–10%. Be explicit: we are NOT assessment-grade or transaction-AVM-grade; we beat the **local** baselines (OLS + BIR) under honest CV. Use the apples-to-oranges caveats (listings not sales, small n, no quality features, sparse market). Verify the ⚠ primary sources before final citation.
- [ ] **Ramolete et al. like-for-like benchmark (NEW, `reference/ramolete_replication_2026-06-14.md`)** — we re-ran our models under their random 80/20 protocol. **Honest finding, do not overclaim "we're just more honest":** the protocol switch lifts RF MAPE only **2–5pp** (Condo +5.1, Houses +1.9, Lot +3.4 — largest for condos, as their coordinate clustering is densest). Even under their split our MAPE is **~30%**, still above their **10.7–21%**; the rest of the gap is genuine (their 3,212 Cavite houses vs our 674, thinner Cebu market, their PSA/DTI features + AdaBoost/segmentation). **Lead with MdAPE:** our RF typical error under the random split is **15.9% (condo) / 21.3% (houses)** — at the top of their band — so the median property is competitive; a tail of hard properties inflates the mean. Use the **houses stratum** (house-dominated data) as the fair comparison, not the aggregate. Table in the replication doc §4; paste-ready prose §6.
- [ ] **Hyperparameter tuning evidence** — drop the elbow-method plots (`EDA/plots/11_hyperparameter_tuning/`) and note the wider search confirmed deployed params are at the optimum; curves are flat (models insensitive to settings).

## Chapter 8 — Interpretation
- [ ] Refresh per-stratum **SHAP** narrative (RQ1) from the regenerated plots in `EDA/plots/10_stratified_models/` (current rows). Keep the simpler defense narrative on top of SHAP.

## Chapter 9 — Conclusions
- [ ] **RQ4 valuation gap** — report the quantified gap by LGU×stratum from `valuation_gap_summary.csv`; reference `valuation_gap.geojson` as the prescriptive map. **Lead with vacant lots (clean land-to-land): market ≈ 2–4× BIR.** **Caveat condo/house percentages** (>1000%) as inflated by a unit mismatch (BIR = land/sqm vs price = floor/sqm). 95–100% of listings exceed BIR in every LGU.
- [ ] Re-answer RQ1–RQ4 directly, each pointing to its artifact. Keep RQ2 (RF≈XGB) and RQ3 (condo-only geospatial gain) honest, not overclaimed.

## Limitations (Ch3 data section + Ch9/limitations) — NEW from 2026-06-14
- [ ] **Centroid-snapped geocoding** (`reference/shared_pin_investigation_2026-06-14.md`) — disclose honestly: a large share of rows share an exact coordinate, but for **houses/lots this is mostly a geocoding artifact, not real geography**. Listings with incomplete addresses (subdivision/barangay/city, no street number) were snapped to a barangay/subdivision **centroid**: ~**83% of shared house rows** and ~**80% of shared lot rows** are centroid-snaps; net ~**31–37% of the Houses and Lot strata** sit on a centroid. Condos are mostly genuine multi-unit buildings (the 64-unit Marigondon tower) but ~39% are still centroid-snaps. **Implication:** the spatial features (CBD distances, MCRAI, road distances, spatial lag) of centroid rows were computed from the centroid, not the true parcel → spatial-feature noise on ~⅓ of houses/lots, a plausible contributor to the high-MAPE error tail. **Note it does NOT break the leak-free CV** (GroupKFold groups by exact lat/lon → a centroid's listings all fall in one fold; no train/test leakage). Frame as a data-quality limitation + future-work fix (re-geocode incomplete addresses), not an evaluation flaw.

## Cross-cutting
- [ ] Remove any remaining "Mapbox token" or "manifest contract bug" caveats — both resolved (Decision 44a).
- [ ] Ensure terminology consistency: "MCRAI" (full name on first use), MdAPE/PE20 as headline metrics.
