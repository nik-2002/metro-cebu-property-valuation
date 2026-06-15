# Session Handoff — App-Contract Fix (2026-06-10)

> Audience: Claude Code CLI (or any agent) resuming cold.
> Repo root: `/Users/nicoestreba/Library/CloudStorage/GoogleDrive-nico.estreba@gmail.com/My Drive/UA&P/classes/Data Science/16 Thesis`
> Source of truth for the project: read `CLAUDE.md` at repo root first, then
> `thesis_main/reference/eda_workflow_handoff_2026-06-07.md`,
> `thesis_main/reference/project_integrity_review_2026-06-07.md`,
> `thesis_main/reference/modeling_decisions.md` (Decisions 42/43),
> `thesis_main/Models/stratified/deployment_manifest.json`.

---

## 1. What this session did

Fixed the **immediate app blocker** flagged as "Critical 1" in
`project_integrity_review_2026-06-07.md`: the Streamlit predictor read a manifest
key that no longer exists, so the Property Predictor could fail with
`KeyError: 'deployed_metrics'` after a successful prediction.

Scope was deliberately narrow: **app compatibility only.** No training, scraping,
enrichment, manuscript edits, or Git operations were performed.

---

## 2. Root cause

- Decision 42 finalization (`finalize_stratified_groupcv.py`) rewrote
  `deployment_manifest.json` to store GroupKFold metrics under
  `strata.<key>.metrics_group_cv`.
- The app (`app/lib/predict.py`) still read the old key
  `strata.<key>.deployed_metrics`, and also pulled `R2_sqm`, which the
  Decision 42 manifest does not contain.
- Only one UI consumer existed: `app/pages/2_Property_Predictor.py` used
  `result['test_mape']` and `result['test_r2_sqm']`.

Manifest metric keys that DO exist per stratum (condo/houses/lot):
`MdAPE, MAPE, COD, PRD, PE10, PE20, median_ratio, n`. There is **no `R2_sqm`** —
do not invent one.

---

## 3. Files changed (2 app files)

### `thesis_main/app/lib/predict.py`
- Read `strata.<key>.metrics_group_cv`, with a fallback to legacy
  `deployed_metrics` only if an old manifest is loaded:
  ```python
  stratum_manifest = manifest["strata"][stratum_key]
  metrics = stratum_manifest.get("metrics_group_cv") or stratum_manifest.get("deployed_metrics") or {}
  ```
- Return dict: kept `test_mape` → `MAPE` (UI back-compat). Added
  `mdape, mape, cod, prd, pe10, pe20, median_ratio`, plus full `metrics` block.
- **Removed** `test_r2_sqm` (R2_sqm not in Decision 42 manifest).

### `thesis_main/app/pages/2_Property_Predictor.py`
- Caption no longer references `test_r2_sqm`. Now shows Decision 42 headline
  metrics with a `None`-safe `_pct()` helper:
  `group-CV MdAPE ≈ 20%, MAPE ≈ 35%, PE20 ≈ 50%`.

No other files touched. `build_price_surface.py` and `shap_explain.py` only use
`get_model` (no metric fields), so they were unaffected.

---

## 4. Verification status

**Static (done this session):** Confirmed all three strata in
`deployment_manifest.json` expose `metrics_group_cv` with the six metric keys;
confirmed `2_Property_Predictor.py` was the only consumer of the metric fields
(via repo-wide grep for `test_mape|test_r2_sqm|deployed_metrics|metrics_group_cv|R2_sqm`).

**Runtime (NOT done — blocked):** The isolated sandbox in the prior session would
not start (`ERR_QUIC_PROTOCOL_ERROR`), so the smoke test was never executed
against the `.pkl` models. **This is the one open item to close.**

### Run the smoke test
A standalone end-to-end test was written to the session outputs folder:
`smoke_test_predict.py`. It exercises all three real prediction paths
(`build_feature_vector()` → `predict()`): Condominium (Cebu City),
Single Detached (Talisay), Vacant Lot (Consolacion, bedrooms/bathrooms omitted to
test imputation). It asserts no `KeyError`, finite positive prices, all six metric
fields resolve, and `test_r2_sqm` is gone.

If the script isn't in the repo, regenerate it or run an equivalent. Command:
```bash
cd "/Users/nicoestreba/Library/CloudStorage/GoogleDrive-nico.estreba@gmail.com/My Drive/UA&P/classes/Data Science/16 Thesis/thesis_main"
../.venv/bin/python /path/to/smoke_test_predict.py --app-dir "$(pwd)/app"
```
Expected: `OVERALL: ALL PASS`. The `shap`/Streamlit ScriptRunContext warnings on a
bare run are harmless.

Alternative manual check: launch the app from the project venv and submit one
prediction per stratum.
```bash
cd "<repo>/thesis_main" && ../.venv/bin/streamlit run app/streamlit_app.py
```

---

## 5. Git guidance (do not deviate without discussion)

The repo has a large staged cleanup from prior GitHub prep
(staged ~`4 A / 8883 D`; unstaged ~`21 M / 59 D`; ~106 untracked). Per the integrity
review, **do not reset, unstage, or revert unrelated changes.** Keep this fix as its
own narrowly scoped commit (app contract only), separate from repo hygiene, modeling,
and manuscript changes. Prefer a private repo for first push.

---

## 6. Project state recap (current source of truth = Decision 42/43)

- Stratified **Random Forest** per property type; target `log(price_per_sqm)`;
  total = price/sqm × area_sqm.
- Evaluation: **GroupKFold(5)** by coordinate cluster (leak-free).
- Master ABT `abt_clean.csv` = 1,849 rows (lookup pool only — its `log_price`
  column is known-stale; the app does not use it).
- Stratum training CSVs: `abt_condo.csv` 687, `abt_houses.csv` 674, `abt_lot.csv` 255.
- Headline metrics MdAPE/PE20; COD/PRD are IAAO context only — **not IAAO-compliant.**

| Stratum | Rows | Groups | MdAPE | MAPE | PE20 | COD | PRD |
|---|---:|---:|---:|---:|---:|---:|---:|
| Condominium | 687 | 388 | 20.1% | 35.2% | 49.8% | 36.3 | 1.21 |
| Houses | 674 | 509 | 22.1% | 32.4% | 45.0% | 33.0 | 1.18 |
| Vacant Lot | 255 | 203 | 25.6% | 37.8% | 41.6% | 36.9 | 1.28 |

---

## 7. Remaining blockers / open items (out of scope this session)

1. **Run the smoke test** (Section 4) — only runtime confirmation still missing.
2. **Medium 1 (integrity review):** dropped-pin predictions use Haversine CBD
   distances (`app/lib/features.py:76`, `haversine_to_cbds`) while training used
   network distances. Decide: route through network distance, or document the app
   as a Haversine approximation. Affects Mactan/Lapu-Lapu bridge-friction cases.
3. **Medium 2:** app imputation medians load from `abt_clean.csv`
   (`features.py:15-18`), not the per-stratum training CSVs. Conceptually
   inconsistent with stratified design; low risk for manual inputs.
4. **Manuscript lag (Critical 2):** Chapters 3, 6, 7, 8, 9 and abstract still
   describe the old global total-price / held-out workflow. Update to Decision 42.
5. **Stale EDA artifacts (High 2b):** `eda_stratified_v2.py` and
   `eda_data_integrity.py` need rerunning on 687/674/255 rows; saved log used
   654/558/204.
6. **abt_clean.csv stale `log_price` (High 3):** recompute to `log(price_per_sqm)`
   or add a loud data-contract warning so no future script trains from it.
7. **Decision log not updated** for this app-contract fix — pending the user's call
   on whether to log it to `modeling_decisions.md` / `task.md`.

---

## 8. Collaboration rules (from CLAUDE.md — important)

- Author is the writer; the agent supports planning/critique/review, not authorship.
- Hands-on implementer is **OpenAI Codex** (not Copilot/Antigravity). Write Codex
  prompts that name the target script, the exact change, expected outputs, and what
  must not change. Read the target script before writing a prompt.
- Log every modeling decision to `modeling_decisions.md` immediately (what + why).
- Wrap any copy-paste blocks (Codex prompts, handoffs, LaTeX) in fenced code blocks.
- Ground node/feature/variable decisions in literature first, statistics second.
