# Defense Deck — Build Log

Two parallel decks exist, both grounded in the **dev/manuscript** branch (numbers from
`deployment_manifest.json`, `model_comparison_stratified.csv`, `valuation_gap_summary.csv`,
the decision log, and the compiled manuscript). Nothing in either deck is invented.

## Artifacts
| File | What it is |
|---|---|
| `defense_storyboard.md` | The slide-by-slide plan (claims audited, citations grounded). |
| `defense_mockup.html` | Early 7-archetype design proof (warm-green, low-density). |
| `build_deck.py` → `defense_deck.html` | **Angle A — lean / narrative.** ~80 slides, deep-green warm, low-density, picture-led intro. |
| `build_pptx.py` → `defense_deck.pptx` | PowerPoint export of Angle A (photo placeholders + animation notes). |
| `build_deck_v2.py` → `defense_deck_v2.html` | **Angle B — substantive / panel.** 77 slides, cool palette, dense where the manuscript is dense. |
| `generate_deck_plots.py` → `assets/deck/*.png` | All generated charts/diagrams (9). |
| `manuscript_narrative.html` | Chapter-by-chapter narrative + page refs — the content source. |

## Generated assets (`assets/deck/`)
funnel_collection · ablation_tiers · valuation_gap_lots · listings_by_lgu · mcrai_catchment ·
abt_snapshot_wide · model_comparison · mcrai_weighting · feature_selection · webapp_{market_map,price_surface,predictor}

---

## Angle B (v2) — revision history

### Round 1 — substantive rebuild (this session)
Built the panel-appropriate angle: persistent chrome (section + slide number), data tables,
takeaway callouts, figure+analysis splits, chapter-mapped dividers, references spread.

### Round 2 — revisions requested by Nico
1. **Removed speaker-note phrasing** — dropped "β and the radii are defensible baselines, not
   estimated from Cebu data (revisited in Chapter 10)." Replaced with audience-facing wording:
   the reach values "follow standard accessibility conventions — a sensible baseline."
2. **MCRAI made layman + weight story** — new slide "how the weights were chosen" with a
   two-stage diagram (`mcrai_weighting.png`): Stage 1 = fit a regression, see which categories
   raise price; Stage 2 = normalize the positive coefficients into weights (edu 0.447 /
   grocery 0.345 / recreation 0.222). "Transport measured separately as road distance;
   banking proximity dropped" reworded in plain terms.
3. **Per-stratum features now shown in full** — three dedicated slides listing every feature
   for Condo (21) / Houses (24) / Vacant Lot (22), grouped by category (replaces the abstract
   feature-group ✓/— matrix).
4. **Model comparison added** — `model_comparison.png` (grouped MdAPE bars OLS/RF/XGB per
   stratum) answers RQ2 with numbers from `model_comparison_stratified.csv`.
5. **Modeling pipeline explained** — new slides: "Preparing the data for modeling" (split →
   encode → select) and "How the three feature sets were chosen" (`feature_selection.png`:
   VIF → OLS significance → ablation → MCRAI zero rates → 21/24/22) and a "Hyperparameters
   and tuning" table (trees/max-features/min-leaf/max-depth per stratum, from the manifest).
6. **Feature-group ✓ matrix replaced** with the full per-stratum feature lists (item 3).
7. **Dröes / Usman insight stated, not just cited** — "stratified models lifted R² from 0.637
   to 0.782 (Dröes et al., 2019); segmenting improved fit ~7% and cut error >10% (Usman et al., 2020)."
8. **Data Preparation now includes modeling prep** — the feature-set derivation lives in Ch5.
9. **Introduction re-paced for story** — context (where Cebu is → 7.3% economy → 11.5% housing)
   → how a price is decided (scenario → four references → fragmentation) → the problem →
   research questions → scope. No longer a single dense dump.
10. **Cool / neutral palette** — slate-blue (#33455E) + steel (#5B7A99) + cool light
    (#C5D2DF) on cool near-white (#FAFBFC), replacing the warm green. All generated charts
    recolored to match; catchment rings use a cool monochrome ramp.
11. **This log.**

### Round 3 — coverage gaps + per-stratum collinearity
- **Three gap slides** added after the manuscript coverage audit: Ch2 "the core obstacle: data
  scarcity" (Cheloti 2021; Ajibola 2010), Ch6 "why these three models?" (SVR / LASSO-Ridge /
  DNN exclusion table), Ch7 "where the model errs" (residual analysis).
- **Deployment line** folded into the Ch10 "for practice and policy" slide (open-market-only
  scope; refresh as data drifts).
- **"Why the three feature sets differ"** (Ch6, new) — answers how multicollinearity and the
  other OLS diagnostics were handled per stratum. Table of statistical checks → what was done
  (CBD-distance collinearity VIF>5 kept in trees / trimmed in OLS; MCRAI composite is a
  deterministic blend, dropped from OLS; raw-vs-log zonal double-count; heteroscedasticity →
  HC3) paired with what actually differentiates the sets (lots = land only + individual MCRAI;
  houses = sub-type indicators; condos = composite). Honest framing: collinearity shaped the
  OLS baseline, the deployed trees tolerate it, and the strata differ mainly by data structure.
  Grounded in Decisions 31d / 32 (Flags 1–4) and Chapters 5–6. Deck now 77 slides.

### Round 4 — all three models shown in modeling + evaluation
- **"Hyperparameters and tuning"** (Ch6) expanded from RF-only to all three: deployed RF tuned
  per stratum (table unchanged) + a comparators table — XGBoost at standard settings (300 / lr
  0.05 / depth 6, held constant) and OLS as a fixed log-log + HC3 specification (no tuning grid).
  Did **not** use `tuning_results_*.json` (stale: marks XGB-tuned for houses, pre-Decision-42).
- **"Headline accuracy"** (Ch7) expanded from deployed-RF-only to all three models, MdAPE **and**
  PE20, all on the leak-free `model_comparison_groupcv.csv` basis (RF = 19.3 / 22.7 / 38.4, exactly
  matching the manifest). OLS 24.5 / 25.1 / 44.8; XGB 19.8 / 23.6 / 40.2.
- **Bug fix:** `model_comparison.png` was built from the *optimistic held-out* CSV (RF lot 23.3%),
  contradicting the headline (38.4%). Repointed `generate_deck_plots.py model_comparison()` to the
  leak-free GroupKFold numbers so the RQ2 chart, its bullets, and the headline now agree. ylim 36→50.

### Round 5 — sequencing fixes (CRISP-DM section hygiene)
- **Slide 41 "One model cannot price three markets"** (Modeling) no longer re-shows the
  `all_strata_price_boxplot` that already appears on slide 31 (Data Understanding). Reframed
  decision-led: a `5.8×` stat callout + the stratification argument, referencing the earlier
  distribution. Removes a duplicate image; keeps descriptive content in DU, decision in Modeling.
- **Slide 21 "The data pipeline"** (Methodology) replaced the bullet chain (which duplicated the
  16,561→3,616 funnel count already on slide 29) with a new `pipeline_flow.png` diagram: six
  stage cards (Ingest → Clean & filter → Geocode → BIR join → Geospatial features → ABT) split
  into a row-filtering phase (16,561 → 3,616) and a feature-enrichment phase (→ 51 columns, no
  rows dropped). "GIS features" renamed "Geospatial features" (GIS = the software category, wrong
  term). No fabricated per-stage counts — only the verified anchors (16,561 in, 3,616 × 51 out).

### Round 6 — wording, footer, MCRAI depth
- **Footer removed** from all content slides (was repeating the thesis title + "C. D. Estreba").
  Title-slide author credit and "Thank you" slide kept.
- **Professionalism pass:** "Evaluation protocol — an honest test" → "Evaluation protocol";
  "flattering itself" → "overstating its accuracy"; "clean, honest table" → "clean, defensible
  table"; "the honest reading" → "the fair reading".
- **Banking wording softened** (slide "MCRAI — categories and reach"): dropped the absolute
  "no comparable study treats it as a residential amenity"; now "none of the residential studies
  reviewed treat it as a distinct amenity, and it overlaps with the commercial access the CBD
  distances already carry" — matches the finance-retirement decision rationale.
- **Catchment radii bullet** tightened to reflect the real basis (category catchment + Metro Cebu
  refinement). Deck radii verified against `compute_hansen_scores.py` CATEGORY_RADII_KM (exact match).
- **New slide "The two stages, in depth"** added after the MCRAI weighting diagram: Stage 1 =
  hedonic regression → implicit prices (sign + significance, Rosen 1974); Stage 2 = normalize the
  positive significant coefficients into weights (edu 0.447 / grocery 0.345 / recreation 0.222),
  negatives kept as standalone features. Deck now 78 slides.

### Manuscript (dev/manuscript) — appendix
- New appendix section **"Data Source Portals"** scaffolded with three captioned `ccpic` slots
  (Lamudi / FilipinoHomes / DotProperty) pointing to `diagrams/portal_*.png`. Screenshots to be
  captured and dropped in by the author; OnePropertee noted as scraped-but-excluded.

## Open / manual
- Both decks: stock photos for the lean deck's picture slides still to be dropped in.
- v2 has no .pptx export yet — generate from `build_deck_v2.py` if Angle B is chosen.
- Decide which angle (A lean vs B substantive) is the one to present.
