# Project Staleness + Cleanup Audit — 2026-06-15

> Full-project audit after the multi-source expansion (Decision 47), feature selection (47i),
> and the lot MCRAI cleanup (Decision 49). Source of truth = `Models/stratified/deployment_manifest.json`.
> Run via 2 subagents + filesystem timestamp scan. **Nothing was deleted** — this is the checklist.

## CURRENT TRUTH (everything below is measured against this)
- ABT `abt_clean.csv` = **3,616** rows (Lamudi 1,579 + FilipinoHomes 1,203 + DotProperty 565 + Lamudi_pw 270).
- Condo n=1,300, **21 feat**, MdAPE **19.3** · Houses n=1,223, **24 feat**, MdAPE **22.7** · Lot n=849, **22 feat**, MdAPE **38.4**.
- Lot MCRAI (Decision 49) = 6 individual: education, grocery, health, hospitals, recreation, tourism. **No composite, no security, no retail_density.**
- Condo/Houses MCRAI = `mcrai_composite` only. Composite = education 0.447 + grocery 0.345 + recreation 0.222 (3 cats; finance + transport retired).
- spatial_lag radius = **500 m** (Decision 47g).

---

## A. STALE NUMBERS IN DOCS  (fix during the MANUSCRIPT session — deferred)
Severity ranked. The manuscript `.tex` chapters are in worse shape than expected.

### A1 — BLOCKERS (an author following these would write wrong numbers)
- **`Manuscript/ch_correction_checklist_2026-06-13.md`** lines ~40, ~50 — *prescribes inserting* the OLD numbers (687/674/255; 20.1/22.1/25.6). Must be rewritten to 1,300/1,223/849 and 19.3/22.7/38.4 (PE20 51/44/26) BEFORE any chapter is drafted from it.
- **`Manuscript/chapter7.tex`** + **`chapter9.tex`** — describe the OLD pre-stratification GLOBAL model (R²=0.807, MAPE 59.28%, MAE 4.95M PHP, `Models/rf_model.pkl`, 1,192/299 rows). Entire results/conclusions need replacing with the stratified GroupKFold story.
- **`Manuscript/chapter3.tex`** methodology errors: (a) spatial lag described as **1 km** → 500 m; (b) MCRAI radii table still lists **Finance + Transport** as deployed; (c) composite described as **4 categories** w/ transport weight 0.102 → should be 3 cats (0.447/0.345/0.222); (d) "nine categories" narrative incl. finance/transport.
- **`Manuscript/abstract.tex`** — model-selection claim "strongest overall held-out performance" overclaims; per Decision 44f it's RF≈XGB tie, RF chosen for robustness/parsimony.

### A2 — Reference docs that read as "current/deployed" (fix before manuscript drafting)
- **`reference/feature_investigation_2026-06-14.md`** line 4 + §6 "DEPLOYED" table — shows 19.8/22.5/38.0 and Lot 25 feat. → 19.3/22.7/38.4, Lot 22 feat (Decision 49).
- **`reference/source_expansion_2026-06-14.md`** "FINAL OUTCOME" (lines ~87–99) — 3,617/1,301/19.8/38.0 → 3,616/1,300/19.3/38.4.
- **`reference/avm_benchmarks_2026-06-13.md`** "Our models (recap)" table (lines ~12–14) — pre-expansion (25.6 lot, 255 rows). Refresh from manifest.
- **`reference/ph_comparable_studies_2026-06-13.md`** line ~19 — random-split MdAPE 15.9/21.3 → Decision 48 values 16.2/22.1.
- **`reference/data_workflow_findings_for_manuscript.md`** lines 18/22/97 — "1,849 rows", 687/674/255 (manuscript-facing sentences).

### A3 — Historical snapshots (DO NOT rewrite — but don't read as current). Add a 1-line "superseded" banner if exposed.
- `reference/PROJECT_SNAPSHOT.md`, `reference/pipeline_walkthrough_2026-06-13.md` (⚠ named in CLAUDE.md as a key read — worth a banner + 1km→500m fix), `reference/eda_workflow_handoff_2026-06-07.md`, `reference/project_integrity_review_2026-06-07.md`.
- `reference/modeling_decisions.md` — correctly historical; NO change needed (latest entries/"deployed" line are current).

---

## B. STALE ARTIFACTS  (regenerate at the APP/FREEZE step — deferred)
- ✅ **DONE today:** RF SHAP beeswarms (condo/houses/lot) — `regen_shap_2026-06-15.py`.
- [ ] **Price surface** — rerun `app/precompute/build_price_surface.py` (lot archetype changed).
- [ ] **RQ2/RQ3 outputs STALE (pre-expansion, 06-13):** `Models/stratified/model_comparison_groupcv.csv` + `ablation_groupcv.csv` were built on the OLD ABT. Rerun `answer_rq2_rq3.py` for the manuscript RQ2/RQ3 tables.
- [ ] **Per-stratum CV CSVs (06-05):** `rf_cv_results_{condo,houses,lot}.csv`, `xgb_cv_results_*.csv` — pre-expansion; regen if cited.
- [ ] **Verify `QGIS/data/valuation_gap.geojson`** — 3,372 features vs ABT 3,616 (all 3,616 have BIR). Either a stale subset or an intentional filter — confirm, regen if stale.
- [ ] (low) XGB comparator SHAP `shap_*_xgb_summary.png` (06-03/05) — comparator only.
- KEEP (current): EDA `04_correlation` heatmaps + `11_hyperparameter_tuning` plots; `abt_clean.geojson` (app+QGIS, 3,616, in sync).

---

## C. JUNK — SAFE TO DELETE (~4 MB, no dependencies)
- 6 root stub CSVs: `thesis_main/{education,finance,grocery,health,security,transport}.csv` (32 B each, from `download_test.py`).
- `thesis_main/download_test.py` (scratch Overpass test, writes to nonexistent dir).
- `EDA/Screenshot 2026-05-09 at 9.48.29 AM.png` (2.1 MB ad-hoc capture).
- Old data backups: `abt_clean.backup_pre_multisource_*` (864 K), `abt_lot.backup_pre_clean_2026-06.csv` (116 K), `Data/amenities/transport_terminals_backup.csv` (8 K).
- Old manifest backups: `deployment_manifest.backup_pre_tuning.json`, `..._pre_multisource_*.json`.
- 18× `.DS_Store`, 9× `__pycache__` (52 `.pyc`). Add both to `.gitignore`.

## D. NEEDS-USER-DECISION (bigger / dependency-bound)
- **Old GLOBAL model pkls** `Models/{rf_model,rf_tuned,xgb_model,xgb_tuned}.pkl` (~66 MB) — ⚠ STILL referenced by chapter7/9.tex. Delete only AFTER those chapters are rewritten off the old model.
- **Stratified tuning-reference pkls** `*_rf_tuned.pkl`, `*_xgb*.pkl` (9 files, ~33 MB) — nothing loads them at predict time (`answer_rq2_rq3.py` refits XGB live). Keep for tuning trace or delete (CSVs retain the record).
- Recent safety backups `abt_clean.backup_pre_featsel_0052.csv` (1.7 M), `deployment_manifest.backup_pre_groupcv.json` — keep 1–2 weeks, then delete.
- `abt_clean.backup_pre_batch_2026-06.csv` — `data_collection_funnel.py` loads it by name; keep until the funnel table is finalized for Ch4.
- Superseded scripts in `Scripts/` root: `run_models.py`, `tune_models.py`, `eda_stratified.py` (v1) — move to `Scripts/archive/legacy/` to de-clutter (not junk; reproducibility).
- Old EDA root PNGs (~2.2 MB, pre-stratification) — some cited in task.md as manuscript figs; keep until manuscript figure list is finalized. `EDA/cbd_distance_corr.png` is ACTIVE — keep.
- `app/data/lgu_boundaries.geojson` vs `QGIS/data/lgu_boundaries.geojson` — mtimes 3 weeks apart; confirm same content (md5) and unify.
- Early scrape notebooks `Data/web_scraping/*.ipynb` (lifenavi, leechiu) — superseded by Playwright; keep for lineage or delete.

## E. GIT
Branch `modeling`, uncommitted: 21 modified, 4 added, 101 deleted (the `.venv` removal), **149 untracked** (mostly `.venv`). The freeze commit should `.gitignore` `.venv/`, `__pycache__/`, `.DS_Store` first.
