# Chapter Correction Checklist — manuscript rewrite map

> Origin: 2026-06-13 verification sprint. **REFRESHED 2026-06-15** with current deployed numbers
> (Decisions 47–49) and the RQ2/RQ3 rerun. Every number below is from the live
> `Models/stratified/deployment_manifest.json` + `model_comparison_groupcv.csv` /
> `ablation_groupcv.csv` (re-run 2026-06-15 on the 3,616-row ABT). **The manuscript chapters are
> stale (they describe the retired global model); do NOT copy from them — rewrite from this map +
> the reference docs.**

## CURRENT DEPLOYED STATE (the source of truth — use these everywhere)
- **ABT = 3,616 rows** (open-market). Sources: Lamudi 1,579 + FilipinoHomes 1,203 + DotProperty 565 + Lamudi_pw 270.
- **Strata:** Condo **1,300** / Houses **1,223** / Vacant Lot **849**.
- **Deployed RF (leak-free GroupKFold), MdAPE / PE20 / MAPE / COD / PRD:**
  - Condo **19.3 / 51 / 36.5 / 37.7 / 1.21** (21 features)
  - Houses **22.7 / 44 / 35.1 / 35.8 / 1.20** (24 features)
  - Vacant Lot **38.4 / 26 / 58.3 / 55.9 / 1.48** (22 features)
- **Per-stratum features (Decision 47i/49):** all strata drop `bir_zonal_rr_log`, `bir_zonal_cr_median`,
  both road-distance features. Condo + Houses collapse MCRAI to `mcrai_composite` only. Vacant Lot keeps
  6 individual MCRAI (education, grocery, health, hospitals, recreation, tourism) — composite, security,
  retail_density dropped. spatial_lag = same-stratum within 500 m.

---

## Research Re-Alignment — paste-ready RQ answers (current numbers)

**RQ1 — value drivers (unchanged question).**
- *Answer (deployed-RF importance):* **location dominates.** **Vacant Lot:** distance-to-CBP is the
  single biggest driver (~**31%** RF importance) — land value ≈ location (bid-rent, Alonso/Muth), with
  area and individual amenity access (grocery/education) next. **Condo:** **neighbourhood price level
  (spatial lag ~29%)** leads, then unit size (area ~17%, bedrooms ~8%), airport, composite accessibility.
  **Houses:** distance-to-CBP (~19%) + neighbourhood (spatial lag ~16%) + size (~15%). *Caveat:* impurity
  importance favours continuous features; the RQ3 ablation + correlations agree location dominates.
  ⚠ If a single "geospatial = X% of importance" figure is wanted, recompute it from the current models;
  the per-feature values above are from the 2026-06-15 deployed RF.

**RQ2 — most suitable model for deployment (not "lowest MAPE").**
- *Answer (current, leak-free GroupKFold, MdAPE):*
  | Stratum | OLS | Random Forest | XGBoost |
  |---|---|---|---|
  | Condo | 24.5 | **19.3** | 19.8 |
  | Houses | 25.1 | **22.7** | 23.6 |
  | Vacant Lot | 44.8 | **38.4** | 40.2 |
  Tree models clearly beat OLS (5–6pp). **RF edges XGB on all three by 0.5–1.9pp** — close enough to call
  comparable, but RF is the modest winner; deployed for robustness on small samples + simplicity
  (scikit-learn only). Frame as "RF best / tied, deployed for robustness," NOT a decisive accuracy gulf.

**RQ3 — do geospatial features help, and how does it differ by type? (headline YES + decomposition).**
- *Answer (ablation, RF, same folds, ΔMdAPE):* **yes for all three vs structural-only** — Condo
  **+5.65pp**, Houses **+4.18pp**, Vacant Lot **+12.95pp**. **Decomposition (engineered geospatial ON TOP
  of administrative location city+BIR):** Condo **+3.70pp**, Vacant Lot **+3.77pp** (engineered geospatial
  carries BOTH), Houses **−0.66pp** (administrative location alone carries houses; engineered geospatial
  adds nothing beyond it). The model adds the most value where administrative benchmarks are weakest
  (condos, lots).  *(Updates the old "admin carries houses AND lots" — lots are now carried by geospatial too.)*

**RQ4 — valuation gap vs BIR (minor).**
- *Answer:* large and positive everywhere (95–100% of listings exceed BIR). Clean land-to-land (vacant
  lots): market ≈ **2–4× BIR**. Caveat condo/house % (land-vs-floor unit mismatch).
  ⚠ **Rerun `answer_rq4.py`** to refresh `valuation_gap_summary.csv` on the 3,616-row ABT before quoting
  per-LGU figures (current geojson/summary predate Decision 49).

**Re-aligned contribution (§Significance / abstract):** A Cebu-specific, property-level valuation model
whose geospatial features + stratified, per-type feature design add the most value precisely where
administrative benchmarks fail (vertical condominiums and bare lots), quantifying a large systematic gap
between market prices and BIR zonal values — delivered as QGIS layers + a Streamlit decision-support app.

---

## Chapter 1 — Problem & Setting
- [ ] **RQ2 + RQ3 wording (§Research Questions):** use the re-aligned statements above.
- [ ] **§1.6 Model Selection:** state the deployment verdict (RF deployed, XGB tested-not-retained, OLS diagnostic) + the *why*.
- [ ] **Abstract overclaim:** "baseline Random Forest … strongest overall held-out performance" is unsupported. Soften to "RF and XGBoost performed comparably (RF marginally ahead); RF deployed for robustness on small per-stratum samples + simplicity." Align abstract to open-market-only scope + MdAPE/PE20.
- [ ] **IVS edition** — resolve bib-key mismatch (biblio.bib `ivs2020` vs prose "IVS 2025").
- [ ] Confirm "eight polycentric CBD nodes" matches code (CBP, Mandaue, Mactan, SRP, Talisay-Tabunok, Consolacion, Naga, Airport).

## Chapter 3 — Methodology (largest changes)
- [ ] **Data gathering — tell the FULL multi-source story (Decisions 45 + 47).** Two phases:
  - *Phase 1 — Lamudi, two scraper generations (Decision 45):* legacy `requests`+BeautifulSoup (bulk),
    then a **Playwright browser scraper** added after Lamudi deployed a JS-challenge/CAPTCHA wall →
    **Lamudi total 1,579 + 270 (anti-bot batch)**.
  - *Phase 2 — multi-portal expansion (Decision 47):* added **FilipinoHomes (1,203**, via its backend
    JSON API → precise coords) and **DotProperty (565**, barangay-text geocoded). **OnePropertee was
    scraped but dropped** (contamination: mis-extracted per-sqm prices + city-centroid geocoding, OOF
    over-prediction). Net ABT **1,849 → 3,616**. Use the funnel from `reference/source_expansion_2026-06-14.md`.
- [ ] **MCRAI radii** — code values: education 2.5 / health 2.0 / hospitals 5.0 / grocery 2.0 / security 2.0 / tourism 3.0 / recreation 1.5 / retail 1.0 km; β=2.0; 0.5 km floor.
- [ ] **MCRAI composite** — **3 categories**: education 0.447, grocery 0.345, recreation 0.222. Transport moved to road-distance features; finance retired. Remove any 4-category/transport-weight text.
- [ ] **Transport accessibility** — via `dist_to_trunk_road_m` / `dist_to_primary_road_m`, not a transport-MCRAI category. (Note: both road features were later dropped from the deployed models — Decision 47i — keep this nuance.)
- [ ] **Strata counts** — **Condo 1,300, Houses 1,223, Lot 849** (ABT 3,616). *(was 687/674/255 — STALE)*
- [ ] **Target** — `log_price = log(price_per_sqm)`; predict per-sqm, ×area for total.
- [ ] **Evaluation protocol** — GroupKFold(5) by coordinate cluster (leak-free); MdAPE/PE20 headline + COD/PRD panel; do not claim IAAO compliance.
- [ ] **NEW — Per-stratum feature selection (Decisions 47i/49).** Document as a methodology contribution:
  evidence-grounded trimming (VIF, OLS significance, leave-one-block ablation, MCRAI zero-rates) →
  all strata drop redundant BIR-log/BIR-commercial + road distances; condo/houses collapse the 9 MCRAI
  categories to the composite (0.57–0.96 inter-correlated → redundant); **vacant lot keeps 6 individual
  MCRAI** (grocery/hospitals OLS-significant) but drops composite (exact collinearity, R²=1.0), security
  (36.9% LGU-uneven data gap), retail_density (≈0 correlation). Net: condo 33→21, houses 36→24, lot 29→22
  features at parity accuracy. *Story:* different property types are priced by different geospatial
  structure (built homes → one accessibility summary; bare land → specific amenity access).
- [ ] **Hyperparameter tuning** — document RF grid (n_estimators/max_features/min_samples_leaf/max_depth) + XGB grid, selection by **MdAPE under GroupKFold**, per-stratum best params (manifest). Reference `EDA/plots/11_hyperparameter_tuning/` sweep plots. Note tuned ≈ defaults (models insensitive at this data size).
- [ ] **Deployment** — RF per stratum deployed; OLS comparator baseline; XGB evaluated under same protocol.
- [ ] **Lot scope filter** — area 80–2000 sqm AND price ≥ ½ BIR zonal (Decision 41).

## Chapter 7 — Results
- [ ] **RQ2 head-to-head table** from `model_comparison_groupcv.csv` (rerun 2026-06-15): OLS / RF / XGB per
  stratum (numbers in the RQ2 table above). **Honest finding:** trees beat OLS; **RF best/tied with XGB**
  (within ~2pp). Frame RF deployment as robustness/parsimony, not a decisive accuracy win.
- [ ] **RQ3 ablation table** from `ablation_groupcv.csv` (rerun 2026-06-15): Structural → +Admin →
  +Geospatial. Headline: geospatial improves all three (Condo +5.65, Houses +4.18, Lot +12.95 pp).
  Decomposition: engineered geospatial carries **condos AND lots** (+3.70 / +3.77 pp pure geospatial);
  administrative location carries **houses** (−0.66 pp pure geospatial).
- [ ] **Replace stale single-split / MAPE-only results** with the leak-free MdAPE/PE20 numbers:
  **Condo 19.3/51, Houses 22.7/44, Lot 38.4/26.** *(was 20.1/49.8, 22.1/45.0, 25.6/41.6 — STALE)*
- [ ] **External AVM benchmark subsection** (`reference/avm_benchmarks_2026-06-13.md`): IAAO ratio-study
  COD 5–15/PRD 0.98–1.03, IAAO AVM acceptance (⚠ verify), Zillow 1.74% on-/7.20% off-market, academic ML
  ~7–10% MAPE. Be explicit: NOT assessment- or transaction-AVM-grade; we beat the LOCAL baselines (OLS + BIR)
  under honest CV. Apples-to-oranges caveats (listings not sales, small n, no quality features, sparse market).
- [ ] **Ramolete et al. like-for-like (Decision 48, refreshed; `reference/ramolete_replication_2026-06-14.md`).**
  Under their random 80/20 protocol, RF random-split MdAPE = **Condo 16.2 / Houses 22.1 / Lot 36.2**; the
  protocol switch lifts MAPE only **Condo +5.1 / Houses +1.3 / Lot +1.8 pp** (leakage is small). Even their
  way, our MAPE stays above their 10.7–21% band — the rest of the gap is genuine (their **3,212** Cavite
  houses vs our **1,223**, thinner Cebu market, their PSA/DTI features). **Lead with MdAPE:** our typical
  condo (~16%) / houses (~22%) sits at the top of their band → median property competitive; a hard-case tail
  inflates the mean. Use the **houses stratum** as the fair comparison (their data is house-dominated).
- [ ] **HP-tuning evidence** — drop the `EDA/plots/11_hyperparameter_tuning/` curves; note the wider search confirmed deployed params (curves flat → models insensitive).

## Chapter 8 — Interpretation
- [ ] Refresh per-stratum **SHAP** narrative (RQ1). ⚠ The on-disk SHAP PNGs in
  `EDA/plots/10_stratified_models/` keep reverting (Google Drive sync) — regenerate fresh
  (`Scripts/regen_shap_2026-06-15.py` / `build_overview_html.py`) right before use, or take the
  base64-embedded copies from `study_overview_2026-06-15.html`. Keep the simpler defense narrative on top.

## Chapter 9 — Conclusions
- [ ] **RQ4 valuation gap** — report by LGU×stratum from `valuation_gap_summary.csv` (⚠ rerun `answer_rq4.py`
  first). Lead with vacant lots (clean land-to-land): market ≈ **2–4× BIR**. Caveat condo/house % (unit mismatch).
- [ ] Re-answer RQ1–RQ4 directly, each pointing to its artifact. Keep RQ2 (RF best/tied) + RQ3 (condo+lot geospatial gain) honest.

## Limitations (Ch3 data section + Ch9)
- [ ] **Centroid-snapped geocoding** (`reference/shared_pin_investigation_2026-06-14.md`): ~31–37% of
  houses/lots sit on a barangay/subdivision centroid (vague addresses) → spatial-feature noise on ~⅓ of
  those strata, a plausible high-MAPE-tail contributor. Does NOT break leak-free CV (GroupKFold groups by
  exact lat/lon). Frame as data-quality limitation + future re-geocode.
- [ ] **NEW — Source heterogeneity (Decision 47h):** combining portals introduces source-level price
  effects — FilipinoHomes lists ~14% cheaper stock at equal features; no source feature is available at
  prediction time. Disclose.
- [ ] **NEW — Vacant-lot data ceiling (Decision 47f/47h):** lot is the weakest stratum (~38%) because
  bare-land value depends on unobserved parcel attributes (frontage, zoning, title, slope, flood) absent
  from listings. The honest ~38% (not the earlier optimistic 25.6% on a small concentrated sample) is a
  data ceiling, not a modeling failure.
- [ ] **NEW — Condo pre-selling down-payment contamination (Decision 53):** the cheap tail of condo
  listings is contaminated by pre-selling **down-payments / reservation fees scraped as full unit
  prices** (24 condos ≤ ₱1M and <25% of city norm, mostly named pre-selling projects in Mandaue /
  Lapu-Lapu / Cebu City). A target-variable measurement error. We documented it rather than dropping
  the rows or retraining (frozen models, near defense). Distress detection is weak because listing
  descriptions were not retained (only short titles). Evidence:
  `reference/condo_partial_price_suspects_2026-06-16.csv`; review: `reference/model_review_2026-06-16.md`.
- [ ] **NEW — Intra-city terrain not captured (Decision 53 / model_review):** the largest vacant-lot
  errors are genuinely cheap **mountain/highland barangays within a city** (e.g. Sirao, Babag in Cebu
  City) that the model over-values because it only sees "city + distance to CBD," not elevation/slope/
  access. Honest limitation, not data error — keep those listings. Possible future feature: DEM-based
  elevation/slope. Review: `reference/model_review_2026-06-16.md`.

## Cross-cutting
- [ ] Remove any "Mapbox token" / "manifest contract bug" caveats (resolved).
- [ ] Terminology: "MCRAI" full name on first use; MdAPE/PE20 as headline metrics.
- [ ] ⚠ **Do not reintroduce manuscript chapter numbers** — the chapters themselves are being rewritten
  from this map; numbers come from the manifest + reference docs, never the old chapter prose.
