# Project Structure and Integrity Review

> Review date: 2026-06-07  
> Scope: model + repo integrity after recent Claude Opus modeling work  
> Method: targeted inspection of entrypoints, artifacts, contracts, logs, and Git state. No training, scraping, enrichment, or cleanup scripts were rerun.

---

## Executive Summary

The current modeling artifacts are mostly coherent, but the project is **not safe to continue as-is at the app and documentation layer**.

The strongest current modeling source of truth appears to be:

1. `thesis_main/Scripts/prepare_stratified_abt.py`
2. `thesis_main/Scripts/finalize_stratified_groupcv.py`
3. `thesis_main/Models/stratified/deployment_manifest.json`
4. `thesis_main/Models/stratified/{condo,houses,lot}_model.pkl`

The three stratum CSVs and model artifacts align:

| Artifact | Rows | Target check |
|---|---:|---|
| `abt_condo.csv` | 687 | `log_price = log(price_per_sqm)` within floating-point tolerance |
| `abt_houses.csv` | 674 | `log_price = log(price_per_sqm)` within floating-point tolerance |
| `abt_lot.csv` | 255 | `log_price = log(price_per_sqm)` within floating-point tolerance |

The current manifest matches these row counts and model feature names. However, the Streamlit predictor still expects the old manifest key `deployed_metrics`, while the current manifest exposes `metrics_group_cv`. This is a live app compatibility break.

The manuscript and some reference docs still describe the old global Random Forest / total-price / held-out-test workflow. They do not match the current stratified per-sqm GroupKFold/IAAO workflow.

The EDA logic exists and covers the right issues, but the saved structured EDA artifacts are stale. The latest saved EDA log used 654/558/204 rows, while the current stratum CSVs contain 687/674/255 rows. Do not use the saved EDA plots/logs as final thesis evidence until `eda_stratified_v2.py` and the data-integrity EDA are rerun on the current data.

GitHub readiness is improved but unfinished. A large staged repo-cleanup exists, but the working tree still has many unstaged and untracked thesis/modeling changes. Do not push this repo to GitHub until the app contract and source-of-truth cleanup are resolved.

---

## Project Map

### Active working areas

- `thesis_main/Scripts/`
  - Current modeling/data path appears to use `stage_lamudi_batch.py`, `enrich_cbd_and_lag.py`, `filter_to_lgu_scope.py`, `prepare_stratified_abt.py`, and `finalize_stratified_groupcv.py`.
  - `run_models_stratified.py` and `tune_models_stratified.py` are still useful historical/intermediate scripts, but Decision 42 supersedes their deployment logic.
- `thesis_main/Data/processed/`
  - Current modeling inputs are `abt_condo.csv`, `abt_houses.csv`, and `abt_lot.csv`.
  - `abt_clean.csv` is still used as an app feature-lookup pool, but not as the authoritative training target table.
- `thesis_main/Models/stratified/`
  - Current deployment manifest and per-stratum model artifacts live here.
  - Old/intermediate artifacts also live here, including held-out, k-fold, tuned RF/XGB files, and backups.
- `thesis_main/app/`
  - Current Streamlit app points to the stratified model directory.
- `thesis_main/reference/`
  - Decision logs and snapshots live here, but some are stale or internally inconsistent with Decision 42.
- `thesis_main/Manuscript/`
  - Current manuscript source exists here, but several chapters still describe the older global workflow.

### Archive or local-only areas

- `thesis_main/Scripts/archive/`
  - Contains legacy/generated/geocoding/google maps/experimental/utility subfolders. This is good separation, but older files still show up in task/docs references.
- `.venv/`, `cache/`, `thesis_main/cache/`, `.claude/worktrees/`, `.vscode/`
  - Local-only. These should not be committed.
- `thesis_main/Models/*.pkl`, `thesis_main/Models/stratified/*.pkl`, `thesis_main/app/data/*.parquet`
  - Generated binary artifacts. Useful locally, but generally should not be committed unless using Git LFS or a deliberate artifact policy.

---

## Integrity Findings

### Critical 1 - Streamlit predictor is incompatible with the current manifest

**Evidence**

- `thesis_main/app/lib/predict.py:58-59`:
  - reads `manifest["strata"][stratum_key]["deployed_family"]`
  - then reads `manifest["strata"][stratum_key]["deployed_metrics"]`
- `thesis_main/Models/stratified/deployment_manifest.json` has `metrics_group_cv`, not `deployed_metrics`.

**Impact**

Prediction can fail with `KeyError: 'deployed_metrics'` after a successful model prediction. This blocks reliable use of the Property Predictor flow until the app is updated or the manifest schema is restored.

**Recommended fix**

Update the app to read `metrics_group_cv` and expose current metrics such as `MdAPE`, `MAPE`, `COD`, `PRD`, `PE10`, and `PE20`. Remove or rename old output fields like `test_r2_sqm` if they no longer exist in the GroupKFold manifest.

---

### Critical 2 - Manuscript still describes the old global total-price model, not the current deployed model

**Evidence**

- `thesis_main/Manuscript/chapter3.tex:5` says the training target is total property price and `price_per_sqm` is only a diagnostic.
- `thesis_main/Manuscript/chapter7.tex:7-21` describes a 299-row held-out test set and total-price evaluation.
- `thesis_main/Manuscript/chapter7.tex:49` says the app aligns with `Models/rf_model.pkl`.
- Current app config points to `Models/stratified/{condo,houses,lot}_model.pkl`, and current manifest says target is `log_price = log(price_per_sqm)`.

**Impact**

The thesis write-up is materially inconsistent with the actual current pipeline. This is a panel-risk issue because Chapter 3, Chapter 6, Chapter 7, Chapter 8, Chapter 9, and the abstract can tell an older story than the model artifacts.

**Recommended fix**

Before manuscript editing continues, update the methodology/evaluation narrative to the Decision 42 workflow:

- stratified per-sqm target
- three per-stratum Random Forest deployments
- GroupKFold by coordinate cluster
- MdAPE/PE20 as headline operational metrics
- COD/PRD as IAAO-context diagnostics, with explicit non-compliance caveat

---

### High 1 - Current modeling source of truth is scattered across multiple generations of artifacts

**Evidence**

- `run_models_stratified.py` deploys best tree by held-out MAPE.
- `tune_models_stratified.py` deploys by repeated k-fold mean MAPE.
- `finalize_lot_model.py` resolves Lot with GroupKFold and IAAO reporting.
- `finalize_stratified_groupcv.py` generalizes GroupKFold/IAAO reporting to all three strata and rewrites `deployment_manifest.json`.
- `model_comparison_stratified.csv` still contains older held-out results.
- `kfold_cv_stratified.csv` still contains repeated-k-fold results.
- `deployment_manifest.json` now contains GroupKFold/IAAO results.

**Impact**

A future user can easily cite or deploy the wrong metric table. The artifacts are not wrong by themselves, but they belong to different evaluation generations.

**Recommended fix**

Declare Decision 42 artifacts as the current source of truth and label older files explicitly as historical/intermediate:

- Current: `deployment_manifest.json`, `finalize_stratified_groupcv.py`, deployed `{stratum}_model.pkl`
- Historical: `model_comparison_stratified.csv`, `kfold_cv_stratified.csv`, tuned XGB/RF references, backup manifests

---

### High 2 - Decision log and task-log contradictions were found, then partially refreshed

**Evidence**

- Original finding: `modeling_decisions.md` had current Decisions 40-42 but a stale `Last updated: 2026-05-25` header.
- Original finding: `task.md` still marked k-fold/tuning/IAAO follow-ups as pending and foregrounded older clean-strata results.
- Follow-up update on 2026-06-07: `modeling_decisions.md` now includes Decision 43, `task.md` has a new 2026-06-07 current-standing section, and `PROJECT_SNAPSHOT.md` points to the Decision 42/43 workflow.
- Current manifest/CSVs show Condo 687, Houses 674, Lot 255.

**Impact**

This issue is improved but not fully closed. A handoff reader now has a current Decision 43 trail, but older historical sections still contain stale row counts and should be treated as dated context.

**Recommended fix**

Use `eda_workflow_handoff_2026-06-07.md` plus Decisions 42-43 as the current reading path. Do not delete older historical sections unless doing a separate documentation cleanup pass.

---

### High 2b - Saved EDA outputs are stale relative to current stratum CSVs

**Evidence**

- `thesis_main/EDA/plots/eda_stratified_v2_run.log` was generated from Condo 654, Houses 558, and Lot 204 rows.
- Current stratum CSVs and manifest show Condo 687, Houses 674, and Lot 255 rows.
- The EDA folders and EDA scripts are untracked in Git status, so the results exist locally but are not safely integrated.

**Impact**

The EDA findings are directionally useful, but final manuscript or defense claims should not cite stale row counts, stale plots, or log-only numeric summaries. This is especially important for thin LGU cells, VIF flags, Cook's distance counts, and MCRAI zero rates.

**Recommended fix**

Rerun `eda_stratified_v2.py` and `eda_data_integrity.py` on the current data, then save key numeric outputs as CSV/JSON alongside the plots. Add a one-page defense table mapping each EDA issue to its workflow response.

---

### High 3 - Master `abt_clean.csv` still has stale/mixed `log_price`

**Evidence**

Read-only audit:

- `abt_clean.csv`: 1,849 rows, 51 columns.
- Max absolute difference between `log_price` and `log(price_per_sqm)` is about `10.82`.
- Stratum CSVs are clean: max difference is approximately `1.78e-15`.
- `thesis_main/app/lib/config.py:6-8` states the app does not use `abt_clean.csv`'s `log_price`.

**Impact**

This is not a current model-training break if `prepare_stratified_abt.py` always recomputes `log_price` before writing stratum CSVs. It is still a data-integrity trap because a future script can accidentally train from `abt_clean.csv` and reintroduce the old bug.

**Recommended fix**

Either recompute `abt_clean.csv.log_price` to match `log(price_per_sqm)` or add a very visible warning in the current data contract. Prefer recomputation after confirming no historical reason to preserve mixed target values.

---

### Medium 1 - App uses Haversine CBD distances for dropped-pin predictions while training used network-distance features

**Evidence**

- `thesis_main/app/lib/features.py:76` calls `haversine_to_cbds(lat, lon)`.
- The methodology decisions and training feature names are built around distance variables that were intended as network distances.
- The app uses nearest-neighbor lookup for local MCRAI/road/spatial lag features, but CBD distances are recomputed from raw coordinates.

**Impact**

If the model was trained on network distances, but live predictions use Haversine CBD distances, dropped-pin predictions are off-contract. This matters especially for Mactan/Lapu-Lapu and bridge-friction cases.

**Recommended fix**

Either route CBD distances through the same network-distance method used in training, or explicitly document the dropped-pin app as using Haversine approximations for CBD distances. This should be tested before presenting the app as methodologically aligned.

---

### Medium 2 - Feature medians for app imputation come from `abt_clean.csv`, not stratum-specific training CSVs

**Evidence**

- `thesis_main/app/lib/features.py:15-18` loads numeric medians from `ABT_PATH`, which is `abt_clean.csv`.
- Models were trained from `abt_condo.csv`, `abt_houses.csv`, and `abt_lot.csv`.

**Impact**

For missing bedrooms/bathrooms, the app can impute from the broader master table rather than the matching stratum. This is lower risk for manual inputs, but it is conceptually inconsistent with the stratified modeling design.

**Recommended fix**

Load medians from the relevant stratum CSV or store deployment-time imputation defaults in the manifest.

---

### Medium 3 - GitHub readiness is improved but not complete

**Evidence**

- Current Git status summary:
  - staged: `4 A`, `8883 D`
  - unstaged: `21 M`, `59 D`
  - untracked: `106`
- Staged cleanup is mostly repo-prep: `.gitignore`, `.env.example`, `README.md`, `docs/GITHUB_SETUP.md`, and index-only removal of `.venv`, caches, `.DS_Store`, pycache, LaTeX build outputs, local scraper HTML, and local binaries.
- `git check-ignore` confirms ignore coverage for `.env`, `.mcp.json`, `.venv`, cache files, `.pkl`, app parquet data, LaTeX aux files, and scraper HTML.
- There is no tracked `.pkl`, `.parquet`, `.env`, `.mcp.json`, `.venv`, or cache file currently reported by `git ls-files` after the staged cleanup.

**Impact**

The repo can be made GitHub-ready, but not from the current mixed staging state. Committing now would combine repo hygiene with unrelated modeling/data/manuscript state unless staged carefully.

**Recommended fix**

Use separate commits:

1. Repo hygiene cleanup only.
2. Modeling/data pipeline changes.
3. App contract fix.
4. Documentation/manuscript sync.

For first GitHub upload, strongly prefer a private repo. If preserving old history, remember previous commits may still contain `.venv` and cache files.

---

### Medium 4 - Active scripts and old scripts are separated but still easy to confuse

**Evidence**

- `thesis_main/Scripts/archive/` contains `experimental`, `generated`, `geocoding`, `google_maps`, `legacy`, and `utility`.
- Top-level active `Scripts/` still contains both old global scripts (`run_models.py`, `tune_models.py`) and current stratified scripts.
- Decision 40 explicitly says old `tune_models.py` is deprecated, but manuscript Chapter 6 still cites it as current.

**Impact**

The folder structure is better than before, but script naming still invites accidental reuse of old global total-price scripts.

**Recommended fix**

Add a small `thesis_main/Scripts/README.md` declaring:

- current pipeline order
- deprecated global scripts
- generated/archive status
- scripts that mutate data/artifacts

---

### Low 1 - Some generated and binary outputs are still present locally, even if ignored

**Evidence**

Large local artifacts include:

- model binaries in `thesis_main/Models/` and `thesis_main/Models/stratified/`
- large CSV/GeoJSON files under `thesis_main/Data/`, `thesis_main/QGIS/data/`, and `thesis_main/app/data/`
- presentation files at repo root and under `thesis_main/Presentations/`

**Impact**

This is fine for a local thesis workspace, but GitHub needs a deliberate artifact policy.

**Recommended fix**

For GitHub:

- keep code, docs, scripts, and manuscript source
- keep small summary CSVs only if they are non-sensitive and useful
- keep large/private/scraped data local or in a separate data store
- use Git LFS only if you intentionally want model/data binaries versioned

---

## Modeling Source Of Truth

Treat the current model standing as:

| Layer | Current source |
|---|---|
| Master data pool | `thesis_main/Data/processed/abt_clean.csv` for lookup only |
| Training datasets | `abt_condo.csv`, `abt_houses.csv`, `abt_lot.csv` |
| Target | `log_price = log(price_per_sqm)` in stratum CSVs |
| Current finalization script | `thesis_main/Scripts/finalize_stratified_groupcv.py` |
| Current deployment manifest | `thesis_main/Models/stratified/deployment_manifest.json` |
| Current deployed models | `condo_model.pkl`, `houses_model.pkl`, `lot_model.pkl` |
| Current evaluation protocol | GroupKFold(5), groups = coordinate cluster |
| Current headline metrics | MdAPE, PE20, COD, PRD; do not claim IAAO compliance |

Current GroupKFold metrics from the manifest:

| Stratum | n | Groups | MdAPE | MAPE | COD | PRD | PE20 | IAAO COD |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Condo | 687 | 388 | 20.1% | 35.2% | 36.3 | 1.21 | 49.8% | Above band |
| Houses | 674 | 509 | 22.1% | 32.4% | 33.0 | 1.18 | 45.0% | Above band |
| Lot | 255 | 203 | 25.6% | 37.8% | 36.9 | 1.28 | 41.6% | Above band |

The model feature contracts are coherent:

| Stratum | Model type | Feature count | Manifest feature match |
|---|---|---:|---|
| Condo | RandomForestRegressor | 33 | Yes |
| Houses | RandomForestRegressor | 36 | Yes |
| Lot | RandomForestRegressor | 29 | Yes |

---

## GitHub Readiness Notes

### Safe to commit after review

- `.gitignore`
- `.env.example`
- `README.md`
- `docs/GITHUB_SETUP.md`
- this report

### Keep local or handle deliberately

- `.env`
- `.mcp.json`
- `.venv/`
- `.claude/worktrees/`
- `.vscode/`
- `cache/`, `thesis_main/cache/`
- `.DS_Store`, `__pycache__/`
- `.pkl`, `.parquet`
- scraper HTML dumps
- generated LaTeX build outputs
- large/scraped/private data unless you explicitly want it in a private repo

### Main repo risk

The staged cleanup removes many bad tracked files from the current index, but old commits may still contain them. If GitHub history cleanliness matters, create a fresh first commit from the cleaned working tree instead of pushing the old local history.

---

## Recommended Next Actions

### Fix before app demo or continued app work

1. Update `app/lib/predict.py` to read `metrics_group_cv` instead of `deployed_metrics`.
2. Smoke-test all three prediction routes: Condominium, Houses, Vacant Lot.
3. Decide whether dropped-pin CBD distances must be network-distance aligned or documented as Haversine approximations.

### Fix before manuscript work resumes

1. Update Chapter 3, Chapter 6, Chapter 7, Chapter 8, Chapter 9, and abstract to match Decision 42.
2. Replace old global model claims with stratified per-sqm GroupKFold/IAAO framing.
3. Update `PROJECT_SNAPSHOT.md`, `task.md`, and the `modeling_decisions.md` header.

### Fix before GitHub push

1. Commit repo hygiene separately from modeling changes.
2. Keep the repo private by default.
3. Decide whether model binaries and scraped datasets are excluded, Git-LFS-managed, or placed in an external data/artifact store.
4. Avoid pushing old local history if it contains `.venv`, cache files, or local generated artifacts.

---

## Bottom Line

The modeling state is recoverable and the latest artifacts are internally consistent. The immediate blocker is not the model; it is the **app-manifest contract mismatch** and the **documentation lag**. Treat Decision 42 as the current model standing, fix the app schema issue, then synchronize the manuscript and project logs before doing any GitHub push or further modeling claims.
