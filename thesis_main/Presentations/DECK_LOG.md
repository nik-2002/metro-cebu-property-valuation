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
| `build_deck_v2.py` → `defense_deck_v2.html` | **Angle B — substantive / panel.** 73 slides, cool palette, dense where the manuscript is dense. |
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

## Open / manual
- Both decks: stock photos for the lean deck's picture slides still to be dropped in.
- v2 has no .pptx export yet — generate from `build_deck_v2.py` if Angle B is chosen.
- Decide which angle (A lean vs B substantive) is the one to present.
