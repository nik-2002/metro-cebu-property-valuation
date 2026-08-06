# Final Defense — Storyboard / Slide Plan (low-density build)

**Title:** Predicting Open-Market Residential Property Values in Metro Cebu Using Machine Learning and Geospatial Features
**Presenter:** Chris Dominic Estreba · BS Data Science, UA&P · Defense June 2026
**Target:** ~80 slides, 30 minutes. Most are light/transition slides (10–20 sec); a few content slides take longer. Pacing works because the deck breathes.
**Spine:** Human problem → why it's hard here → business→data problem → what others did + gap → CRISP-DM walk-through → results → tool → mature close
**Numbers source:** `deployment_manifest.json`, decision log, EDA plot library, and the **dev/manuscript** branch (confirmed).

> Slide numbers are INDICATIVE and finalized at build time. Citations are keyed by **section + claim**, not absolute number, so content edits don't break them.

## DESIGN RULES (apply to every slide)
- **One idea per slide.** If a slide needs more than ~3 points, split it into two slides.
- **Never more than 5 lines of text.** Aim for 2–3. Many slides are a single line or a single image.
- **Picture-led wherever possible.** The image carries the point; words support it.
- **Big type, lots of whitespace.** Let slides feel empty.
- **No footers. No shaded callout boxes. No side-notes.** Detail lives in the **speaker notes**.
- **Citations:** a claim resting on a specific source gets a small, discreet author–year tag bottom-right (academic norm, not clutter). A full **References** slide closes the deck. All entries come from `biblio.bib` — none invented.
- **Section dividers** between sections — a number + the section name, nothing else.
- The slide is the headline; the **speaker notes** carry everything you actually say.

> Status: DRAFT for iteration. Nothing built yet.
> OHANA is NOT named on any slide — say "gravity / Hansen accessibility model." (MCRAI took inspiration from Project OHANA; lineage stays in speaker notes only.)

## CITATIONS — grounded in the manuscript (claim cited ONLY where the paper cites that source for that claim)
Verified against actual `\parencite`/`\textcite` usage in dev/manuscript.

| Section · claim | Tag (verified) |
|---|---|
| The Property · BIR zonal = taxation tool, not live prices; assessments not always updated | Bureau of Internal Revenue, n.d.; Otsuka et al., 2023 |
| The Market · Metro Cebu prices rose **11.5% in 2025**, highest outside NCR | Bangko Sentral ng Pilipinas, 2025 |
| The Market · Cebu **7.3% economic growth (2024)**, IT-BPM/tourism drivers | PSA Cebu, 2025 |
| The Field · OLS = interpretable hedonic baseline; RF for non-linearity | Rosen, 1974; Breiman, 2001 |
| The Field · tree models tend to outperform linear on tabular/property data (small-N caution) | Grinsztajn et al., 2022; Tanamal et al., 2023 |
| The Field · PH ML work Manila/Pangasinan-centric; Agosto only Cebu study (transport accessibility = primary driver) | Viray, 2023; Ramolete et al., 2023; Agosto, 2020 |
| The Field · open-market = closest available proxy to IVS Market Value | International Valuation Standards Council, 2025 |
| The Data · polycentric nodes shape accessibility gradients | Giuliano & Small, 1991; McMillen, 2003; JICA, 2015 |
| The Data · network distance from road graph (osmnx) | Boeing, 2017 |
| The Data · gravity/accessibility logic (nearer counts more) | Hansen, 1959 |
| The Data · spatial lag = Tobler's First Law | Tobler, 1970 |
| The Build · stratified models fit better than pooled | Dröes et al., 2019; Usman et al., 2020 |
| The Build · XGBoost strong on tabular; SHAP for explainability | Chen & Guestrin, 2016; Lundberg & Lee, 2017 |
| The Close · add macro indicators to model price drift (future work) | Udomsap & Abid, 2020 |

Notes:
- 11.5% (Metro Cebu, highest outside NCR) IS in the manuscript (Ch1 + Ch2, BSP 2025) — cleared.
- Recommendation slides are the study's own forward-looking points; citation-light except the macro reference.
- The **References** slide lists exactly the works tagged above, full APA, auto-generated from `biblio.bib`.

## PLOTS & ASSETS — every visual slide points to a real file
Paths relative to `thesis_main/`. ⚙ = no PNG yet, generate at build.

| Slide | Visual | Asset |
|---|---|---|
| 38 Collection funnel | funnel 16,561 → 3,616 | `Presentations/assets/deck/funnel_collection.png` ✔ generated |
| 39 Study area (scope) | node-free 6-LGU map | `Manuscript/diagrams/lgu_boundaries.png` |
| 40 Where listings sit | properties by stratum | `Manuscript/diagrams/properties_by_stratum.png` |
| 41 One row of data | ABT slice | `Manuscript/diagrams/abt_snapshot.png` |
| **42 CBD distance** | **8 CBD nodes on Metro Cebu** | **`Manuscript/diagrams/study_area_clean.png`** |
| 43b MCRAI categories | amenity POIs across Cebu | `Manuscript/diagrams/amenities_map.png` |
| 44 Spatial lag | property points / neighbors | `EDA/plots/09_data_integrity/Master_geocoding_clusters.png` |
| 45 EDA target | price-per-sqm skew | `EDA/plots/01_target/all_strata_price_boxplot.png` |
| 46 EDA price by LGU | faceted price | `EDA/plots/02_geographic/price_by_lgu_faceted.png` |
| 47 EDA collinearity | VIF bars | `EDA/plots/05_multicollinearity/Houses_vif.png` (or per-stratum) |
| 49 5.8× finding | strata price boxplot | `EDA/plots/01_target/all_strata_price_boxplot.png` (reuse) |
| 54 Three strata | per-stratum price dist | `EDA/plots/01_target/{Condo,Houses,Lot}_price_distribution.png` |
| 62 Ablation | 3-tier bars (Structural / +Admin / +Geospatial) | `Presentations/assets/deck/ablation_tiers.png` ✔ generated |
| 63 SHAP condo/houses | mean abs SHAP bars | `EDA/plots/10_stratified_models/shap_condo_rf_bar.png`, `shap_houses_rf_bar.png` |
| 64 SHAP lot | mean abs SHAP bars | `EDA/plots/10_stratified_models/shap_lot_rf_bar.png` |
| 65 Valuation gap | vacant-lot market÷BIR by LGU (2.1×–4.8×) | `Presentations/assets/deck/valuation_gap_lots.png` ✔ generated |
| 68–70 Web app | 3 screenshots | `Manuscript/diagrams/webapp_{market_map,price_surface,predictor}.png` — on **dev/manuscript**; gather at build |
| Appendix | beeswarm / OLS diag / tuning / MCRAI heatmaps | `EDA/plots/10_stratified_models/*_summary.png`, `06_ols_residuals/*`, `11_hyperparameter_tuning/*`, `09_data_integrity/*_mcrai_by_lgu_heatmap.png` |

~~Three visuals to generate at build.~~ ✔ All three generated (`Presentations/assets/deck/`, deep-green deck style) via `generate_deck_plots.py` — data verified against Ch4 funnel table, Ch7 ablation table, and `valuation_gap_summary.csv`. Only the 3 webapp screenshots still need gathering from dev/manuscript at build.

---

## SECTION 1 — THE PROPERTY  (the human problem, picture-led, ~15 slides)

1. **Title slide.** Title, name, BSDS Capstone, June 2026, UA&P. Nothing else.
2. **Image: a family / a home.** *"Everyone needs a place to live."*
3. **Image: Cebu homes or skyline.** *"And for most families, a home is the biggest purchase of their lives."*
4. **Image: a real listing.** *"You find one. ₱6.5M."* → *"Is that fair?"* (Illustrative hypothetical — a round, realistic Cebu price, not a data point.)
5. **Image: a broker.** *"Ask a broker — you get a number."*
6. **Image: an appraiser.** *"Ask an appraiser — you get a different one."*
7. **Three numbers, no agreement.** *"None of them agree. And none of them says why."*
8. **Image: a 'For Sale' sign.** Flip the side: *"Now you're the seller. What is it worth?"*
9. **Two short lines.** *"Price too high — it sits for months."* / *"Too low — you leave money behind."*
10. **Simple diagram: one house, five question marks** (buyer, seller, broker, bank, LGU). *"Everyone guesses — from a different corner."*
11. **Image: tax/zonal document.** *"BIR zonal values — built for taxation, not live market prices. And not always updated."* [bir_nd; Otsuka et al., 2023]
12. **Image: a bank.** *"Bank appraisals — tied to lending and collateral risk. A different question than market value."*
13. **Image: a listings website.** *"Online listings — asking prices, not verified sales. Full of seller strategy and noise."*
14. **Recap, one line.** *"Each one is useful. But they answer different questions — and they don't line up."* (Manuscript posture: useful-but-partial, NOT "broken.")
15. **The pivot (text-only, big type).** *"The references exist. Nothing connects them."* (Grounded paraphrase of Ch1 "fragmented references"; avoids the contestable "no data" claim.)

---

## SECTION 2 — THE MARKET  (why Cebu, why now, ~5 slides)

16. **Divider:** *"The Market."*
17. **One stat, big.** *"One of the country's most dynamic economies — 7.3% growth in 2024."* — cite **PSA Cebu, 2025**.
18. **Image: BPO / tourism.** *"Driven by IT-BPM, call centers, and the rebound in tourism."* — same PSA source (notes).
19. **One stat, big.** *"And home prices rose 11.5% in 2025 — the highest rate outside Metro Manila."* — cite **BSP, 2025**.
20. **Image: CBRT / Expressway / SRP.** *"New infrastructure keeps redrawing what counts as 'near'."* → leads into the question.

---

## SECTION 3 — THE QUESTION  (business→data problem, objectives, RQs, ~7 slides)

21. **Divider:** *"The Question."*
22. **The business problem (one line).** *"No defensible, market-facing price reference for Metro Cebu homes."*
23. **The data problem (one line).** *"Turn a property — and where it sits — into a defensible price per square meter."*
24. **Objectives (2 points).** Predictive: estimate open-market price. Prescriptive: show where estimates and benchmarks diverge.
25. **Research Questions (the 4, short form).** Drivers · best model · do geospatial features help · how big is the BIR gap. (Full wording in notes.)
26. **The solution (one line).** *"A stratified, explainable ML model — delivered as a prototype for triangulation."*
27. **Roadmap (one visual).** CRISP-DM: Business → Data → Prep → Modeling → Evaluation → Deployment.

---

## SECTION 4 — THE FIELD  (prior research + the gap, ~9 slides)

28. **Divider:** *"The Field."*
29. **Two traditions (2 points).** Hedonic regression (interpretable) vs machine learning (flexible, accurate). [Rosen, 1974; Breiman, 2001]
30. **The features that drive price (4 short labels).** Structural · economic/benchmark · geospatial/accessibility · amenity/POI.
31. **International / regional evidence (1–2 points).** Tree-based models tend to outperform linear models on tabular/property data — with small-N caution. [Grinsztajn et al., 2022; Tanamal et al., 2023]
32. **Philippine & Cebu evidence (1–2 points).** ML work is mostly Manila/Pangasinan-centric (Viray, 2023; Ramolete et al., 2023). **Agosto (2020) is the only Cebu-specific study — transport accessibility is the primary driver of Cebu land value.** Sets up the gap and "why geospatial."
33. **The gap (one line).** *"Nothing property-level, geospatial, and explainable — for Metro Cebu."*
34. **Our bridge (one line).** *"This study builds exactly that."*
35. **Why open-market listings (one point).** The *closest available proxy* to IVS *Market Value* — arm's-length asking evidence. [IVSC, 2025]
36. **Why geospatial features (one point).** Location is price — and we *construct* the location signal, not ingest it.

---

## SECTION 5 — THE DATA  (data understanding, ~12 slides)

37. **Divider:** *"The Data."*
38. **Collection funnel (one visual).** 16,561 raw listings → 3,616 clean open-market records. (3 portals; OnePropertee excluded — notes.)
39. **Study area (one map).** The six LGUs in scope. Node-free map (`lgu_boundaries.png`), matching the manuscript.
40. **Where the listings sit (one map/bar).** Cebu City 37.8% down to Minglanilla 6.0%.
41. **One row of the data (one visual).** The ABT snapshot. *"51 columns. Here's a slice."*
42. **Engineered location — CBD distance.** → **MAP: `diagrams/study_area_clean.png`** — the 8 polycentric/regional nodes labeled on Metro Cebu (Cebu Business Park, Mandaue CBD, Mactan CBD, SRP, Talisay Tabunok, Consolacion, Airport, Naga City anchor), so the audience sees exactly which CBDs we mean. Line: shortest-path *road* distance to each (osmnx). [Giuliano & Small, 1991; McMillen, 2003; JICA, 2015; Boeing, 2017]
43. **MCRAI — what it is (one slide).** First use spells it out: the **Metro Cebu Residential Accessibility Index (MCRAI)** — a gravity-based accessibility score where nearer amenities count more, decaying with the *square* of road-distance (β = 2). One clean formula on the slide. [Hansen, 1959]
43b. **MCRAI — how it's built (one slide).** Eight amenity categories (education, grocery, health, hospitals, recreation, security, tourism, retail density), each with its own search radius; individual scores **plus a composite that keeps only the positive-signal categories.** (This two-stage rule is the methodological contribution — say "gravity/Hansen," never OHANA.)
44. **Engineered location — spatial lag (one image).** Mean price of nearby *same-type* listings within **500 m**. *"Tobler's Law: near things are alike."* [Tobler, 1970]
45. **EDA — the target (one plot).** Price per sqm is right-skewed → log-transform. `01_target` boxplot.
46. **EDA — price across the map (one plot).** Strong variation by LGU. `02_geographic/price_by_lgu_faceted.png`.
47. **EDA — do we trust the features? (one plot).** VIF / correlation check. `05_multicollinearity/*_vif.png`.

---

## SECTION 6 — GROUNDWORK  (data preparation, ~4 slides)

48. **Divider:** *"Groundwork."*
49. **The finding that changed everything (one plot + one line).** Condo median ≈ **5.8× the vacant-lot median**. *"These are different markets."*
50. **Cleaning, honestly (2 points).** Imputation kept visible (flags); structurally-absent fields left unimputed, not faked.
51. **A data-integrity war story (1–2 lines).** One bad feature was secretly hijacking the target; finding and fixing it is why the results are trustworthy.

---

## SECTION 7 — THE BUILD  (modeling, ~7 slides)

52. **Divider:** *"The Build."*
53. **One model isn't enough (one line).** *"A single model would treat condos, houses, and lots as one market — and they differ 5.8×."* (Grounded framing; the explicit "it flopped" anecdote dropped — no manuscript metric backs it.)
54. **The pivot (one visual).** So we built three: Condo (1,300) · Houses (1,223) · Vacant Lot (849). [Dröes et al., 2019; Usman et al., 2020]
55. **Features per stratum (2 points).** Lots drop beds/baths, use individual amenities; condos/houses use the composite.
56. **The model lineup (one visual).** OLS → Random Forest → XGBoost, with SHAP for the "why." [Chen & Guestrin, 2016; Lundberg & Lee, 2017]
57. **Honest evaluation (one line).** GroupKFold by location — the same spot can't be in train and test.
58. **Random Forest deployed (RQ2, 2 points).** RF beat OLS everywhere; RF edged XGBoost (19.3 vs 19.8 / 22.7 vs 23.6 / 38.4 vs 40.2). Deployed for robustness + simplicity.

---

## SECTION 8 — THE APPRAISAL  (results, ~8 slides)

59. **Divider:** *"The Appraisal."*
60. **Headline accuracy (the one table slide).** MdAPE / PE20: Condo 19.3% / 51% · Houses 22.7% / 44% · Lot 38.4% / 26%.
61. **What that means (2 points).** MdAPE = typical error; PE20 = share within 20%. (Not claiming IAAO compliance — notes.)
62. **Do geospatial features help? (RQ3, 2 points).** Yes — every stratum improves (condo +5.7, houses +4.2, lot +13.0). They help most where benchmarks are weakest.
63. **What drives price — condo & houses (RQ1, one plot).** Spatial lag leads for condos; CBP distance leads for houses. `shap_condo/houses_rf_bar.png`.
64. **What drives price — vacant lot (RQ1, one plot + one line).** CBP distance + amenities lead; but lot is the weakest stratum — a parcel-data ceiling, owned honestly.
65. **The valuation gap (RQ4, one visual + headline).** Vacant-lot market price ≈ **3× the BIR benchmark** (2.2× Cebu City → 4.8× Mandaue). A research signal, not a correction factor.
66. **So — is it good enough? (2–3 lines).** A triangulation reference, not a replacement — held-out error stays substantial even in the best strata. Strongest for condos and houses; only indicative for vacant lots and thin areas. It complements professional judgment; it does not replace it. (Manuscript posture, not "solid.")

---

## SECTION 9 — THE WALKTHROUGH  (the web app, ~4 slides)

67. **Divider:** *"The Walkthrough."*
68. **Market Map (one screenshot).** Open-market listings with filters.
69. **Price Surface (one screenshot).** Predicted ₱/sqm by barangay.
70. **Property Predictor (one screenshot).** A live estimate + its SHAP breakdown. *"It always shows its reasoning."*

---

## SECTION 10 — THE CLOSE  (conclusions & recommendations, ~9 slides)

71. **Divider:** *"The Close."*
72. **Answers to the four questions (one slide, 4 short lines).** Drivers / RF deployed / geospatial helps where benchmarks are weak / gap is large and systematic.
73. **Contribution (2 points).** Methodological: per-type modeling, a polycentric distance set, the two-stage MCRAI, and leak-free CV. Practical: a reproducible, explainable web prototype.
74. **Limitations (2–3 points).** Asking-price ceiling · cross-sectional snapshot · vacant-lot data ceiling.
75. **Recommendations — practice & policy (2 points).** Use as triangulation, not a final number. Keep recognizing secondary subcenters; MCRAI as a template, not a finished index.
76. **Recommendations — future research (2 points).** Estimate MCRAI parameters from data; enrich parcel attributes + add a time dimension. [Udomsap & Abid, 2020]
77. **Close (one line, back to slide 2).** *"A clearer starting point for the family deciding what a home is worth — not the last word."*
78. **References.** Full APA list of exactly the works cited on the slides, auto-generated from `biblio.bib`. (May spill to a 2nd slide.) Key works: BIR (n.d.); Otsuka et al. (2023); BSP (2025); PSA Cebu (2025); Rosen (1974); Breiman (2001); Grinsztajn et al. (2022); Tanamal et al. (2023); Viray (2023); Ramolete et al. (2023); Agosto (2020); Dröes et al. (2019); Usman et al. (2020); IVSC (2025); Giuliano & Small (1991); McMillen (2003); JICA (2015); Boeing (2017); Hansen (1959); Tobler (1970); Chen & Guestrin (2016); Lundberg & Lee (2017); Udomsap & Abid (2020).
79. **Thank you / Questions.** Title + name, one line of thanks, clean. Deep-green divider style for a strong final frame.

---

## Appendix slides (reserve, for Q&A only)
- Full metric table (MdAPE, PE20, PE10, MAPE, COD, PRD, median ratio per stratum)
- SHAP beeswarm (directional) per stratum
- OLS diagnostics (residuals-vs-fitted, QQ, scale-location, Cook's distance)
- Hyperparameter tuning curves
- Geocoding cluster / MCRAI-by-LGU maps
- Per-portal collection funnel detail

## Open items
**Settled ✔**
1. OHANA — not named; "gravity/Hansen model."
2. 11.5% figure — confirmed in manuscript (Ch1+Ch2, BSP 2025).
3. Study-area map — node-free (`lgu_boundaries.png`).
4. "The Market" too thin — expanded to 5 slides (PSA Cebu 7.3% growth + drivers + infrastructure).
5. "First model failed" beat — dropped; grounded "5.8× different markets" framing.
6. Methodology audit — MCRAI to 2 slides (formula/β=2/Hansen + 8 categories/radii/positive-only composite); CBD-distance + spatial-lag (same-type, 500 m) sharpened to Ch3.
7. Claims audit (all sections) — every number traces to manifest/manuscript; "broken"/"solid"/"only tier"/"no data" overclaims corrected.
8. Images — stock/placeholder for now.

**Open for build time**
9. Valuation-gap visual — pull exact numbers from `valuation_gap_summary.csv`.
10. References slide — auto-generate full APA from `biblio.bib`.
11. Renumber `43b` sequentially when generating the PPTX (numbers are indicative until build).
