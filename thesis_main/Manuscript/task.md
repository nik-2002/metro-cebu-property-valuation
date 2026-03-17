# Manuscript Tasks

> Tracking Chapters 1–3 drafting, revisions, and LaTeX sync.
> Last updated: 2026-03-05

---

## Chapter 1 — The Problem and Its Setting
- [x] Draft initial version
- [x] Add §1.5 Scope and Limitations
- [x] **Post-panel**: Remove NLP research question
- [x] **Post-panel**: Add GIS-focused RQ3 (geospatial features)
- [x] **Post-panel**: Define Metro Cebu (6 LGUs)
- [x] **Official feedback #3**: Define property, Metro Cebu (formalized in Ch1)
- [x] **Post-panel**: Emphasize Philippine-context novelty in §1.4
- [x] **Post-panel**: Frame thesis as predictive + prescriptive (QGIS map)
- [x] **Official feedback #4**: Expand justification for choice of problem (§1.1.3 — Why Metro Cebu, and Why Now?)
- [x] **Official feedback #4**: Expand model selection rationale (new §1.6 — OLS/RF/XGBoost with 'Why Not Other Models?' table)

## Chapter 2 — Review of Related Literature
- [x] Draft initial version (§2.1–§2.8)
- [x] **Post-panel**: Replace §2.5 (NLP) → §2.5 (Geospatial Feature Engineering)
- [x] **Post-panel**: Update §2.8 synthesis with GIS gap statement
- [x] **Post-panel**: Standardize "value drivers" terminology
- [x] **Post-panel**: Separate lit findings from thesis methodology
- [x] **Official feedback #2**: Clearer RRL structure (ensure arguments build logically)
- [x] **Official feedback #11**: Add more RRL sources (GIS+ML in SE Asia, PH-specific OSM)
- [x] **Official feedback #10**: Literature grounding for custom value driver model

## Chapter 3 — Research Methodology
- [x] Draft initial version
- [x] **Post-panel**: Remove all NLP references
- [x] **Post-panel**: GIS data sources, target variable, geospatial feature engineering
- [x] **Post-panel**: Diversify floor prices (BDO + Pag-IBIG + other banks)
- [x] **Post-panel**: QGIS Interactive Map as primary deliverable
- [ ] **Official feedback #5**: Add sample data structure tables (raw BDO, raw Lamudi, cleaned schema, final feature matrix)
- [ ] **Official feedback #6**: Acknowledge data processing complexity per source
- [ ] **Official feedback #7**: Add per-source preprocessing details (what needs to be done for each data structure)
- [ ] **Official feedback #8**: Make web map + dashboard description more tangible/concrete (mock screenshots, layer descriptions)
- [ ] **Official feedback #9**: Deeper methodology for adding value drivers (scoring methodology, radius selection, weighting)
- [ ] **Official feedback #10**: Develop custom value driver scoring model (not just standard features)

## Diagrams & Assets
> Existing `.drawio` sources in `Presentations/assets/`. Output to `Manuscript/diagrams/`.

### Ch1 – Problem & Setting
- [ ] **Study Area Map** — QGIS map of Metro Cebu (Cebu City, Mandaue, Lapu-Lapu, Talisay) + CBRT route overlay

### Ch3 – Methodology
- [ ] **Data Landscape** *(revise `Data-Landscape.drawio`)* — Floor (BDO) + Ceiling (Lamudi) → True Market Value. Fix: Lamudi no longer "Future scrape"; typo "Braket" → "Bracket"
- [ ] **Data Pipeline** *(revise `Data-Pipeline.drawio`)* — 5-stage flow. Fix: update source names/counts (remove LeeChiu/LifeNavi if not final)
- [ ] **Empirical Framework** *(revise `Emprerical-Framework.drawio`)* — IVs → Models → Outputs → Validation. Fix: remove "Exploratory" sidebar if out of scope; confirm NLP/BERT inclusion
- [ ] **Feature Engineering Summary Table** — LaTeX table: all features, source, type, derivation
- [ ] **Modeling Pipeline Flowchart** — New: Preprocessing → Split → 3 Models → Evaluation → SHAP

### Ch4 – Results (plan ahead)
- [ ] **Property Distribution Map** — QGIS choropleth/dot map of sample across barangays
- [ ] **Model Comparison Table** — LaTeX table: MAE / MAPE / RMSE / R² per model
- [ ] **Feature Importance Bar Chart** — Top-N from RF/XGBoost *(matplotlib)*
- [ ] **SHAP Summary Plot** — Beeswarm *(SHAP library)*
- [ ] **Actual vs Predicted Scatter** — Per-model with 45° line *(matplotlib)*
- [ ] **Residual Distribution** — Error histograms per model *(matplotlib)*

## Full Draft
- [x] Rebuild `Full_Thesis_Draft.md` with revised Ch1 + Ch2 + Ch3
- [ ] Final proofread pass for consistency
- [ ] Incorporate all official feedback edits (after implementation)

## LaTeX Sync (Deferred)
- [ ] Sync `chapter1.tex` with revised Ch1
- [ ] Sync `chapter2.tex` with revised Ch2
- [ ] Sync `chapter3.tex` with revised Ch3
- [ ] Update `biblio.bib`

## Verification
- [x] Grep: 0 NLP references remain
- [x] 10/10 initial panel feedback addressed
- [ ] Verify all 12 official feedback items addressed (pending)
