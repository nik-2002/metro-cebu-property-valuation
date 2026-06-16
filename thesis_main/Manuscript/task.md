# Manuscript Tasks

> Tracking manuscript, ABT readiness, modeling, and supporting outputs.
> Last updated: 2026-06-16 (repo moved off Google Drive → ~/Documents/projects-data-science/thesis; 3 worktrees set up)

---

## Session 2026-06-16 — Repo moved off Google Drive + 3 parallel worktrees

> Goal: work the three streams in parallel without stepping on each other —
> modeling (CRISP-DM), the webapp, and the manuscript.

### Done
- [x] **Repo copied off Google Drive** to a clean local path (no spaces, no Drive sync churn):
      `/Users/nicoestreba/Documents/projects-data-science/thesis`. Old Drive path kept as a
      one-time **backup** (no git remote exists — Drive + Time Machine are the only backups).
      **Work in the local copy from now on; do not edit the Drive folder.**
- [x] **`.venv` survived the move** (relative `python` symlink + everything invokes `python -m …`):
      sklearn 1.8.0 / numpy 2.4.3 / pandas 3.0.1 / shap 0.51.0 load fine at the new path.
- [x] **Three worktrees** under `~/Documents/projects-data-science/thesis-worktrees/`, all off
      `clean-baseline-2026-06-15` (05a64d71): `modeling` → `dev/modeling`, `webapp` → `dev/webapp`,
      `manuscript` → `dev/manuscript`. Removed the stale `awesome-stonebraker-06be10` agent worktree.
- [x] **Shared-resource wiring** (`.venv` + `Models/stratified/*.pkl` are git-ignored, so worktrees
      don't get them from checkout): each worktree's `.venv` is a symlink to the main `.venv`;
      **webapp** symlinks the deployed pkls (read-only, tracks the live baseline); **modeling** has
      independent pkl **copies** (retrain-safe — can't clobber the frozen deployment); **manuscript**
      needs neither. Added `.venv` to `.git/info/exclude` so the symlink isn't flagged untracked.
- [x] **Verified runnable:** webapp worktree backend predicts 261,694/sqm condo @ CBP (5 SHAP drivers,
      MdAPE 19.3) through the symlinked venv+pkls; `npm install` done. Modeling worktree loads
      `condo_model.pkl` (RandomForestRegressor, 21 feats). All four trees git-clean.
- [x] **Claude memory carried to the new path:** memory is keyed to the folder path, so the set was
      copied to `~/.claude/projects/-Users-nicoestreba-Documents-projects-data-science-thesis/memory/`
      and each worktree namespace's `memory/` symlinks to it (unified memory wherever Claude runs).

### Notes / next
- Workflow: Codex does hands-on edits inside a worktree; Claude advises from the main hub (more context).
- Consider a **private GitHub remote** for off-machine code backup (won't cover git-ignored pkls/venv/raw data — Drive copy still needed for those).
- `MOVE_TO_LOCAL_CHECKLIST.md` at repo root is the throwaway move guide — delete whenever.

---

## Session 2026-06-15 (webapp) — JS/TS frontend + FastAPI backend; Property Predictor ported

> Direction shift: the deliverable app is moving from Streamlit to a lighter Vite + TypeScript +
> Leaflet frontend (`thesis_main/webapp/`, started by Codex) with model inference behind a small
> FastAPI service. Streamlit app (`thesis_main/app/`) is being retired (code kept in repo).

### Done this session (Claude — implemented directly, not via Codex)
- [x] **Property Predictor ported** to TS frontend + Python API. Architecture chosen with Nico:
      TS sends `{lat,lon,property_type,area,beds,baths,bir_override}` → FastAPI runs the EXACT thesis
      model code → JSON back. No modeling logic reimplemented in JS; no retrain.
- [x] **Backend** `thesis_main/webapp/api/main.py` (FastAPI): `GET /api/health`, `GET /api/resolve`
      (point-in-polygon city + auto BIR estimate on pin drop), `POST /api/predict` (full feature
      build → RF predict + CI band → SHAP top-5 drivers). Reuses `app/lib` unchanged.
- [x] **Cache shim** `app/lib/_cache.py` — the ONLY change to `app/lib`. Returns `st.cache_*` normally;
      when `WEBAPP_API=1` (set by the backend) falls back to `functools` so lib imports with no
      Streamlit runtime. Swapped the 4 decorators in features/predict/mcrai_lookup/shap_explain.
      `streamlit run` behaviour unchanged (verified: shim returns the real `st.cache_*`). Shim also
      degrades to functools if streamlit is uninstalled.
- [x] **Frontend** third "Predictor" view in `webapp/{index.html,src/main.ts,src/styles.css}`:
      pin-drop map, type/area/beds/baths inputs, auto city pill + BIR readout (+override), Predict
      button, results panel (price/sqm, total, CI range, MCRAI-fallback warning, SHAP drivers).
      `vite.config.ts` proxies `/api → :8000`; `npm run api` convenience script; README + .gitignore updated.
- [x] **Runs on the project `.venv`** (NOT conda). Installed `fastapi 0.137.0` into `./.venv`
      (already had uvicorn, **shap 0.51.0**, shapely, streamlit, sklearn 1.8.0 / numpy 2.4.3 / pandas 3.0.1
      → pickles load identically). npm scripts point at `../../.venv/bin/python`.

### Verified
- tsc `--noEmit` clean; `vite build` green (JS ~167 KB). Streamlit-path lib import still clean.
- **Faithfulness:** `/api/predict` == direct lib call, exact match. CBP condo 60 sqm → **224,665/sqm**.
- All 3 strata route (Condo 224,665 · Houses 142,577 · Lot 73,207 /sqm); BIR override flows through;
  out-of-bounds pin → HTTP 422. SHAP drivers populate (5) on the `.venv` (shap present).
- Verified through the Vite proxy (browser path) on `:5174` (5173 was occupied).

### Decisions / notes
- `get_last_mcrai_fallback()` is a module global → could race under truly concurrent requests.
  Fine for single-user demo; per-request refactor if it ever goes multi-user.
- CLAUDE.md still calls the **Streamlit app the final deliverable** — update that line once the
  webapp is confirmed as the deliverable.

### Venv lean-up (Nico's request — "shifted from streamlit")
- Finding: `streamlit`, `streamlit_folium`, `folium`, `pydeck`, `branca` are imported ONLY by
  `thesis_main/app/`. Nothing in `Scripts/`, the scrapers, EDA, or the webapp uses them → removing
  them retires only the old Streamlit app. Scientific stack (sklearn, pandas, numpy, scipy, shap,
  shapely, matplotlib, osmnx, geopandas, …) is shared by the modeling pipeline → KEEP.
- **DECIDED 2026-06-15: KEEP Streamlit for now** — do NOT uninstall. Nico wants `app/` runnable as a
  defense fallback; revisit the lean-up after the defense. `.venv` left unchanged. Safe-to-remove set
  when revisited: `streamlit`, `streamlit-folium`, `folium`, `pydeck`, `branca` (+ their orphans).

### Hugging Face Space deploy package (built 2026-06-15) — NOT YET DEPLOYED
- Goal: host the whole webapp (FastAPI + built frontend) free. Chose **Hugging Face Spaces, Docker SDK**
  (free, 16 GB RAM, port 7860). One container serves `/api/*` AND the built `dist/` at `/` via
  `StaticFiles` → **same-origin, no CORS** (production path differs from dev, which uses the Vite proxy).
- `thesis_main/webapp/deploy/` created (tracked): `Dockerfile` (python:3.12-slim, `ENV WEBAPP_API=1`,
  uvicorn on :7860), `requirements.txt` (**scikit-learn==1.8.0 pinned** so pickles load, + shap, fastapi,
  uvicorn, numpy<3, pandas, scipy, shapely — **NO streamlit**), `README.md` (HF front-matter `sdk: docker`,
  `app_port: 7860`), `.gitattributes` (`*.pkl filter=lfs`), and `build_hf_space.py`.
- `build_hf_space.py` assembles `webapp/hf_space/` mirroring the minimal subtree the backend imports —
  the 7 needed `app/lib` modules, the 3 deployed pkls + manifest, `abt_clean.csv`, `lgu_boundaries.geojson`,
  `api/main.py`, and the built `dist/` — **preserving relative paths** so lib's relative file lookups
  resolve unchanged inside the container. `hf_space/` is git-ignored (regenerate with the script).
- **Verified locally only** (ran the exact Docker CMD via `.venv` uvicorn on :7861): `/api/health` ok
  (shap true), `/` → index.html 200, `/data/*` 200, JS asset 200, predict 224,665/sqm + 5 drivers.
  Package = 28 files, ~83.5 MB. **Docker build itself NOT tested (Docker not installed locally).**
- **STATUS: nothing pushed to Hugging Face yet.** What's left is Nico's to do (I can't log into his HF):
  create a Docker Space (Blank, CPU free), make a Write token, then from the repo root:
  `! ./.venv/bin/hf auth login`  then  `! ./.venv/bin/hf upload USERNAME/SPACE "thesis_main/webapp/hf_space" . --repo-type space`.
  (`hf` CLI v1.19.0 is installed in `.venv`; `huggingface-cli` is deprecated.)
- **CAVEAT to decide before pushing:** a **Public** Space exposes the full ABT (addresses, coordinates,
  prices scraped from Lamudi / FilipinoHomes / DotProperty) and the live Predictor to anyone. Choose
  **Public vs Private**. Free Spaces also **cold-start** (sleep when idle) → for the actual defense, run
  locally via `run.command`, not the Space. Local pkls are git-ignored but DO get pushed to the Space (LFS).

### One-click launcher `run.command` (added by a separate Claude session; verified here 2026-06-16)
- `thesis_main/webapp/run.command` (untracked) — double-click in Finder (opens Terminal) or `./run.command`.
  Starts the FastAPI backend (:8000) + Vite frontend (:5173), opens the browser, **Ctrl+C stops both**
  (cleanup trap kills only the backend it started). Reuses a healthy backend already on :8000 instead of
  erroring. `--export` forces a fresh data export; otherwise skipped (data is frozen). Uses `../../.venv/bin/python`.
  `README.md` "Run" section updated to point at it (do not revert).
- **Verified 2026-06-16, true cold start** (killed all stray backend/Vite/Streamlit first): backend healthy
  ~8 s, single process (no `--reload`), shap true; resolve CBP → Cebu City, BIR ₱51,250; predict condo 80 m²
  → ₱261,694/sqm = ₱20.9M, MdAPE 19.3 + 5 drivers; Vite served on :5173. NOTE: `/api/predict` request field
  is `area_sqm` (not `floor_area_sqm`); `property_type` must be in `PROPERTY_TYPES` (e.g. "Condominium").
- For the defense: **double-click the file yourself** so Ctrl+C works in your own Terminal window.

---

## Session 2026-06-15 — Decision: LOCK IN modeling; do all manuscript work later (as one batch)

> Modeling has hit diminishing returns. Nico's call: proceed with the current models, then update
> the Streamlit app, then rewrite the manuscript. **All manuscript-related tasks are DEFERRED to a
> single later session** (do them together, not piecemeal). Sequence agreed: freeze/commit → app →
> manuscript.

### Done this session
- [x] **Decision 48** — refreshed `replicate_ramolete_randomsplit.py` on the 3,616-row ABT
      (updated RF params to manifest + applied deployed `STRATUM_DROP` so replication matches
      deployment). RF random-80/20: Condo 31.5%/MdAPE 16.2, Houses 33.8%/22.1, Lot 56.1%/36.2.
      Leakage inflation shrank (Condo +5.1 / Houses +1.3 / Lot +1.8pp). Write-up + CSV + decision
      log updated. XGB/OLS labelled comparator-only.

### DEFERRED — Manuscript (do ALL of these together in one later session)
- [ ] ⚠ Update `ch_correction_checklist_2026-06-13.md` — strata counts/metrics STALE → **1,300 / 1,223 / 849** + CURRENT metrics (Condo 19.3/21feat · Houses 22.7/24feat · **Lot 38.4/22feat** — Decision 49 superseded the 38.2/25feat figure).
- [ ] Methodology section: EDA-grounded per-stratum feature selection (RQ3 — different geospatial structure per property type; lots need individual MCRAI + CBD, condos/houses summarised by composite).
- [ ] Limitations: source heterogeneity (FH ~14% cheaper), vacant-lot data ceiling (unobserved parcel attributes), honest lot ~38% (not 25.6), centroid-geocoding noise on ~⅓ of houses/lots.
- [ ] Ch7 benchmark: fold Decision 48 numbers into the Ramolete framing (typical MdAPE at top of their band; mean-gap = sample size + market thinness + their socio-economic features, NOT evaluation rigor).
- [ ] **Positioning / spine note**: contribution = locally-grounded GEOSPATIAL feature system for Metro Cebu (MCRAI + 8 polycentric CBD nodes + osmnx network distances + BIR), NOT a generic socio-economic hedonic. Write the "why we scoped OUT socioeconomic/competitiveness features" defense (LGU-level → collinear with 6-LGU fixed effects; would dilute the geospatial focus).
- [ ] **Consistency check before writing**: confirm RQ1/RQ3 importance + ablation outputs were computed on the FULL geospatial feature set (where the contribution is proven), and that the manuscript bridges "categories matter" (analysis) vs "composite deployed for condo/houses" (lean model). The seam a panelist would poke.

### DEFERRED — App + artifact regen (before manuscript)
> Scope is SMALL — Decision 49 changed ONLY the lot model (condo/house byte-identical; ABT
> UNCHANGED today, mtime 00:53 < retrain 02:08). So most outputs are NOT stale.
- [x] **DONE — RF SHAP beeswarms for ALL 3 strata regenerated** (`Scripts/regen_shap_2026-06-15.py`, run via `./.venv/bin/python` which has shap 0.51). They were STALE since 2026-06-05 (pre-expansion, pre-47i) for every stratum, not just lot — finalize silently skips SHAP when shap is missing in the runtime. Regenerated from the deployed pkls, no retrain. Now condo 21 / houses 24 / lot 22 features, dated 2026-06-15.
- [x] **DONE — price surface rebuilt** (`build_price_surface.py`, all 3 archetypes, 2026-06-15): condo ₱57k–338k/med 169k · houses ₱32k–209k/med 57k · vacant ₱13k–97k/med 33k. Vacant reflects Decision 49 lot model.
- [x] **DONE — app integrity + UI verified** (2026-06-15): all 3 pages read current pkls/manifest/data via `feature_names_in_` auto-align; end-to-end predict+SHAP smoke test passes all 5 property types; AppTest renders all pages with 0 exceptions. **Fixed 2 bugs:** (1) `streamlit_app.py` hardcoded stale MAPE 33/32/55 → now dynamic MdAPE from manifest; (2) `lib/navbar.py` was missing the Price Surface link (page unreachable, sidebar CSS-hidden) → added.
- [ ] (low priority) XGB comparator SHAP plots (`shap_*_xgb_summary.png`) are still 2026-06-05 stale — XGB is RQ2 comparator only, not deployed; regen only if the manuscript shows them.
- [ ] (optional) refresh lot row in `model_comparison_groupcv.csv` / `rf_cv_results_lot.csv` IF a figure cites them — manifest is already the source of truth.
- [ ] Update Streamlit app to the frozen models; verify paths; capture screenshots for the deliverable chapter.
- [ ] **Do NOT regenerate:** EDA plots (ABT unchanged), `abt_clean.geojson` (raw data, no preds), condo/house SHAP, `valuation_gap` (= actual − BIR, a data diagnostic).

### DEFERRED — Future work (write as scoped, not pre-defense)
- [ ] Barangay-level socio-economic enrichment (population density is the best single candidate — barangay-resolution + not already captured by MCRAI). Income unavailable at barangay resolution (PSA limit).
- [ ] Lot parcel-attribute enrichment (zoning/flood/slope rasters) to lift the bare-land ceiling.
- [ ] k-NN spatial-lag if 500m too sparse; re-scrape FH `status` field for status-based distressed filter.

### NEXT concrete action (when resuming)
- [x] **DONE 2026-06-15** — Freeze: re-confirmed abt_clean (3,616) ↔ 3 RF pkls (300 trees; feature_names_in_ match manifest 21/24/22) ↔ manifest (1,300/1,223/849; MdAPE 19.3/22.7/38.4) ↔ barangay price surfaces (199 brgys; med ppsqm condo 165k/houses 62k/vacant 34k; app+webapp copies byte-identical). One consistent state (ABT 00:53 → models 02:08-02:10 → manifest 02:10 → surfaces 10:48). Committed on `clean-baseline-2026-06-15` as `dc9efa1c` (33 files; pkls git-ignored, manifest is tracked source of truth). NOTE: task said branch `modeling`/261 changes — stale; actual was clean-baseline, 16 changes (ABT+manifest already in HEAD from prior baseline commit).
- [ ] NEXT: app screenshots for the deliverable chapter, then the deferred manuscript batch.

---

## Session 2026-06-14 (late) — Multi-source data expansion deployed (Decision 47)

> Scraped 3 new Cebu portals, cleaned/geocoded/merged, retrained. ABT 1,849 → **3,632**.

### Done
- [x] 3 scrapers: `scrape_{filipinohomes_api,dotproperty,onepropertee}.py` (11,419 raw).
      FilipinoHomes via reverse-engineered backend JSON API (precise coords).
- [x] `clean_multisource_2026-06.py` — geocode (Google, cached) + filters + dedup + spatial cap
      → 1,783 clean net-new. Drops "For Assume"/distressed + price-band outliers.
- [x] Merge + canonical enrich chain + retrain. Strata **Condo 1,314 / Houses 1,221 / Lot 851**.
      Deployed: Condo 20.7 / Houses 22.7 (parity) / **Lot 38.7** (honest harder sample).
- [x] Lot experiment (`experiment_lot_precise.py`) — centroid hypothesis REFUTED.
- [x] spatial_lag fix: same-stratum, 1km→500m (arXiv 1902.00562 + MCRAI micro-scale).
- [x] Refreshed: manifest, SHAP, EDA plots/tables (01-09), abt_clean.geojson (3,632),
      valuation_gap.geojson. Decision 47 logged; memory updated.

### Feature investigation — DONE (Decision 47h, `feature_investigation_2026-06-14.md`)
- [x] Source effect quantified → **OnePropertee dropped** (contamination, over-predicts lots 3.34×). FH houses over-predicted ~14% = source-heterogeneity LIMITATION.
- [x] High-error lots profiled → cheap lots at normal locations = unobserved parcel attributes (data ceiling). LIMITATION.
- [x] VIF/correlation re-checked on 2× sample (top VIF dist-CBP 10.1, fine for RF).
- [x] Distressed filter broadened (`assum*`); re-shipped. **Final deployed: Condo 19.8 / Houses 22.5 / Lot 38.0; abt_clean 3,617; strata 1,301/1,223/849.**
- [ ] (deferred) k-NN spatial-lag if 500m too sparse; re-scrape FH `status` field for status-based distressed filter.

### Feature selection — DONE (Decision 47i)
- [x] Deep EDA mining (OLS sig, Cook's D, VIF, MCRAI corr, zero-rates, IQR).
- [x] Dropped condo ID 1523 (misclassified 186sqm "condo" = house).
- [x] Per-stratum feature selection: all drop bir_rr_log+bir_cr_median+ROAD; Condo+Houses MCRAI 9→1 (composite); Lot keeps individual MCRAI.
- [x] **Deployed: ABT 3,616; Condo 19.3/21feat · Houses 22.7/24feat · Lot 38.4/22feat (Decision 49).** Manifest/SHAP refreshed; price-surface geojson + RQ2/RQ3 CSVs still need rerun (see app/regen list).

### Manuscript (next)
- [ ] ⚠ `ch_correction_checklist_2026-06-13.md` strata counts/metrics STALE → use **1,300/1,223/849** + CURRENT metrics (Condo 19.3/Houses 22.7/**Lot 38.4** — Decision 49).
- [ ] New methodology section: EDA-grounded per-stratum feature selection (RQ3 sharpened — different features per property type by economics).
- [ ] New limitations to write (from `feature_investigation_2026-06-14.md`): source heterogeneity (FH ~14% cheaper), vacant-lot data ceiling (unobserved parcel attributes), honest lot difficulty ~38% (not 25.6).

---

## Session 2026-06-14 — Ramolete benchmark replication + shared-pin investigation (Decision 46)

> Stress-tested the Ramolete et al. (2023) benchmark before it enters Ch7. Diagnostic only — no
> change to data, strata, or deployed models.

### Done
- [x] **Ramolete random-split replication** — `Scripts/replicate_ramolete_randomsplit.py` (OLS/RF/XGB
      per stratum, random 80/20 × 25 seeds + seed=42). Output `Models/stratified/ramolete_randomsplit_comparison.csv`.
      **Finding:** leakage inflation modest (RF +2–5pp, largest condos); even like-for-like our MAPE
      ~30% > their 10.7–21% → gap mostly genuine (data scale, market, features), NOT just honesty.
      Lead with MdAPE (15.9% condo / 21.3% houses = top of band). Write-up `reference/ramolete_replication_2026-06-14.md`.
- [x] **Shared-pin investigation** (subagent, Sonnet 4.6) — `reference/shared_pin_investigation_2026-06-14.md`.
      45%/39% house/lot shared-pins = **centroid-snapped geocoding artifact** (~83%/80% of shared rows;
      ~31–37% of strata on a centroid). Spatial features on those rows computed from the wrong point →
      feature noise on ⅓ of houses/lots. Doesn't break GroupKFold.
- [x] Folded both into `ch_correction_checklist_2026-06-13.md` (Ch7 benchmark item + new Limitations
      section), `reference/avm_benchmarks_2026-06-13.md`, `reference/ph_comparable_studies_2026-06-13.md`,
      `modeling_decisions.md` (Decision 46), and memory.

### New manuscript items (added to checklist)
- [ ] Ch7: Ramolete like-for-like benchmark paragraph (random-split MAPE ~30%, MdAPE at top of their band; houses = fair comparison).
- [ ] Ch3/Ch9: centroid-snapped geocoding as a stated **data-quality limitation** + future re-geocode fix.
- [ ] (Author decision) whether to re-geocode incomplete-address rows before final submission — NOT done this session.

---

## Session 2026-06-13 — CRISP-DM verification sprint, re-anchored on the 4 RQs (Decision 44)

> Full pipeline verified against code before manuscript revision (adviser deadline Sun 2026-06-14).
> Found the pipeline had drifted from 3 of 4 research questions. See `reference/modeling_decisions.md` Decision 44.

### Done this session (Claude)
- [x] Plain-language end-to-end walkthrough: `reference/pipeline_walkthrough_2026-06-13.md`.
- [x] Two editable diagrams: `Manuscript/diagrams/pipeline_overview_2026-06.drawio`, `modeling_deepdive_2026-06.drawio`.
- [x] Decision 44 logged (docs↔code reconciliation + RQ gaps + remediation + why-RF reasoning).
- [x] Chapter correction checklist: `Manuscript/ch_correction_checklist_2026-06-13.md`.
- [x] Codex prompts authored: `answer_rq2_rq3.py` (RQ2 head-to-head + RQ3 ablation), `answer_rq4.py` (RQ4 gap + map), EDA rerun.

### Stale items CLOSED (verified already done in code)
- [x] ~~Fix app/manifest contract (read metrics_group_cv)~~ — already correct, `app/lib/predict.py:62`. Not a bug.
- [x] ~~Fix Price Surface Mapbox token~~ — app uses CartoDB public tiles, no token needed.

### Analyses — DONE 2026-06-13
- [x] RQ2+RQ3 (`Scripts/answer_rq2_rq3.py`, run by Claude in .venv) → `model_comparison_groupcv.csv` + `ablation_groupcv.csv`. RF matched manifest exactly. Findings: **RF ≈ XGB tie** (RQ2); geospatial helps **condos only** (RQ3). See Decision 44f.
- [x] RQ4 (`Scripts/answer_rq4.py`, run by Claude) → `valuation_gap_summary.csv` + `valuation_gap_per_property.csv` + `QGIS/data/valuation_gap.geojson`. Market ≈ 2–4× BIR on vacant lots (clean comparison); condo/house % inflated by land-vs-floor unit mismatch.
- [x] EDA rerun (Codex Prompt C) → 45 plots on 687/674/255 + full `EDA/tables/*.csv` (target, spearman, VIF, OLS coeffs, residual diagnostics w/ Breusch-Pagan+Jarque-Bera+DW, Cook's, MCRAI zero-rates, integrity passes) + `eda_defense_table.csv`. Heteroscedasticity confirmed Houses/Lot, borderline Condo; residuals non-normal all strata.
- [x] Folded honest RQ2/RQ3/RQ4 numbers into Decision 44f, walkthrough, deep-dive diagram, and correction checklist.
- [x] Data-collection funnel verified (`Scripts/data_collection_funnel.py` → `reference/data_collection_funnel.csv`): Stage 1 legacy requests+BeautifulSoup **4,477 raw → 1,419 unique in-scope**; Stage 2 Playwright **665 raw → 275 net-new** → ABT 1,849. Corrected a `wc -l` overcount (embedded newlines); "665→275" was right. Consolidated lineage in **Decision 45**. Overview diagram + walkthrough + checklist updated to real numbers.

### Pending
- [ ] NEXT LOOP: manuscript prose edits per `ch_correction_checklist_2026-06-13.md` (carries the honest framing).
- [ ] Note for Ch3/Ch7: the diagnostic OLS in EDA runs on **complete-case** subsets (Condo 546, Houses 558, Lot 216) — smaller than the modeling strata (687/674/255), which impute. State this so the differing n is not a surprise.
- [ ] DEFERRED: Streamlit Cloud deployment for broker (dad) testing.

---

## Session 2026-06-07 — EDA workflow audit and handoff (Decision 43)

### Logged + clarified
- [x] Added plain-language handoff: `thesis_main/reference/eda_workflow_handoff_2026-06-07.md`.
- [x] Logged Decision 43 in `thesis_main/reference/modeling_decisions.md`.
- [x] Updated `CLAUDE.md` so future Claude sessions start from the Decision 42 stratified RF workflow, not the stale global-model workflow.
- [x] Confirmed current source of truth:
  - `Scripts/prepare_stratified_abt.py`
  - `Scripts/finalize_stratified_groupcv.py`
  - `Models/stratified/deployment_manifest.json`
  - `Models/stratified/{condo,houses,lot}_model.pkl`

### Current modeling standing
- [x] Current target: `log_price = log(price_per_sqm)` in stratum CSVs.
- [x] Current deployed model: Random Forest per stratum.
- [x] Current evaluation: GroupKFold(5), groups = coordinate cluster.
- [x] Current rows: Condo 687, Houses 674, Lot 255.
- [x] Current headline metrics: MdAPE / PE20; COD and PRD as IAAO-context diagnostics only.
- [x] Do **not** claim IAAO compliance.

### EDA issue status
- [x] Heteroscedasticity: addressed as an OLS diagnostic issue via HC3 robust standard errors; not a deployed Random Forest blocker.
- [x] Collinearity/VIF: addressed by not relying on OLS coefficients as the final valuation model; RF keeps correlated spatial predictors where useful.
- [x] Outliers and hard duplicates: addressed in `prepare_stratified_abt.py`.
- [x] Coordinate leakage: addressed in Decision 42 via GroupKFold by coordinate cluster.
- [x] Playwright scrape: yielded 665 candidates and 275 net staged rows after filters/dedup; useful but not a huge row-count expansion.

### Still pending
- [ ] Rerun `eda_stratified_v2.py` on the current 687/674/255 stratum CSVs.
- [ ] Rerun or refresh `eda_data_integrity.py` on the current ABT.
- [ ] Save key EDA numeric outputs as CSV/JSON, not only printed logs.
- [ ] Build a one-page EDA defense table: issue, implication, workflow response, defense wording.
- [ ] Update Chapters 3, 6, 7, 8, 9, and abstract to match Decision 42/43.
- [ ] Fix app/manifest contract if still broken: app should read `metrics_group_cv`, not old `deployed_metrics`.

---

## Session 2026-06-05 — Playwright scraper subproject vs Lamudi WAF (Decision 37)

### Built + verified
- [x] Diagnosed Lamudi block as a **DataDome-class WAF (JS challenge), not an IP ban** — first ~2–3 burst requests pass, then the `window.gokuProps` wall; terminal curl check came back CLEAR.
- [x] Stood up isolated subproject **`thesis_main/playwright/`** (`browser.py`, `parse.py`, `scrape_index.py`, `scrape_properties.py`, README, requirements, `data/`, `screenshots/`). Env: `playwright==1.60.0` + `playwright-stealth==2.0.3` + chromium in `16 Thesis/.venv`.
- [x] Modules first authored by **Antigravity (Gemini)** from a Claude prompt; verified end-to-end on a 5-row sample (WAF beaten; prices/lot_area/coords/type parse clean; Talisay/Batangas fixed via `talisay-2 + ?search=Cebu`).
- [x] **Claude now edits the scraper code directly** (author runs via Antigravity). Two direct edits: (a) `browser.py` human-verification CAPTCHA handling — detect, stop reloading, ring bell, **wait up to 10 min for manual solve**, resume (headless → clear error); (b) `scrape_index.py` `--max-pages` default 5 → 10.
- [x] All four scraper files compile clean.

### Pending (next steps, in order)
- [x] **[ANTIGRAVITY run]** Full scrape — done: 665 rows, 0 WAF blocks (`playwright/data/lamudi_scraped.csv`).
- [x] **[CLAUDE]** Geocoded 55 land/house coord-less rows (`playwright/geocode_missing.py`, Google).
- [x] **[CLAUDE]** Staged 275 net-new rows w/ both filters + BIR join (`Scripts/stage_lamudi_batch.py`).
- [x] **[CLAUDE/merge]** Merged → enriched (canonical scripts + new `Scripts/enrich_cbd_and_lag.py`) → LGU polygon filter → `prepare_stratified_abt` → `run_models_stratified`. **abt_clean 1,579→1,849; Lot 204→301.** Backup: `abt_clean.backup_pre_batch_2026-06.csv`. (Decision 39)
- [x] **[CLAUDE]** Regenerated `QGIS/data/abt_clean.geojson` (1,849 features + `stratum` field) for QGIS.

### Post-scrape model-improvement plan (Decision 38, superseded by Decisions 41-42)
- [x] **k-fold CV direction superseded** by stronger GroupKFold by coordinate cluster. This is the current honest evaluation protocol.
- [x] Per-stratum RF tuning completed under GroupKFold in `finalize_stratified_groupcv.py`.
- [x] XGBoost-for-Lot deferred. Current deployment is RF for all three strata; retest XGBoost only if the environment and timeline justify it.
- [x] Lot-specific scope filter implemented in `prepare_stratified_abt.py`; richer land attributes remain a future-work limitation.
- [x] Honest reporting now led by MdAPE, PE20, COD, and PRD. IAAO thresholds verified and used as context only; current models are not IAAO-compliant.

---

## Session 2026-06-03 — log_price bug, stratified models, app rebuild (Decisions 34–35)

### Data-integrity fix (Decision 34)
- [x] Found + fixed the `log_price` target bug (Phase C merge stored log(price_per_sqm), base build stored log(total)). Target redefined to **log(price_per_sqm)** for all rows.
- [x] Retired `is_ceiling_price`/`price_type` as features (leftover from abandoned floor/ceiling design); dropped `is_mactan_island` from models (identical to city_Lapu-Lapu City).
- [x] Dropped data-error rows (condo 621/1292; apartment-buildings 1500/1928/1959); fixed house 2151 bedrooms (378→median).
- [x] `prepare_stratified_abt.py` updated + re-run → clean strata: **Condo 654, Houses 558, Lot 204**.
- [x] `eda_stratified_v2.py` re-run on corrected target (Lot DW autocorrelation concern resolved; heteroscedasticity persists → HC3 still right).

### Stratified modeling (Decision 35) — Phase 4 COMPLETE
- [x] `run_models_stratified.py` written + run on clean strata; best-per-stratum (RF deployed all 3).
  - Condo: MAPE 32.8% / median 13.9% / R²sqm 0.535
  - Houses: MAPE 31.9% / median 20.3% / R²sqm 0.589
  - Vacant Lot: MAPE 54.7% / median 33.6% / R²sqm 0.329 (weak — needs more data)
- [x] Artifacts in `Models/stratified/` + `deployment_manifest.json`; SHAP clean (no leakage).
- [x] Open: consider XGBoost for Lot + add K-fold CV → folded into the **Decision 38** post-scrape plan (k-fold adopted; XGBoost-for-Lot on the table).

### App rebuild (Decision 35d) — DONE
- [x] `app/` rebuilt to stratified per-sqm layer: stratum routing, predict log(ppsqm)→×area, neighbour-lookup for MCRAI/road/spatial-lag, per-stratum SHAP, regenerated price-surface grids, updated copy.

### App/UI dashboard (Decision 36) — DONE (2026-06-04)
- [x] New **Market Map** dashboard (`app/pages/0_Market_Map.py`): 3-panel layout (controls · map · insights) modeled on author's reference design.
  - Map shows ~1,416 **real listings colored by stratum** (Condo/Houses/Lot) + CBD nodes + LGU outline — replaces the precomputed grid (not sustainable).
  - Right panel: stat cards, stratum-composition bar, median-₱/sqm-by-LGU ranked list.
- [x] Platform decided: Streamlit restyled (not custom front-end). Navbar updated; old Price Surface page unlinked.
- [x] All pages pass headless AppTest; app verified running (localhost:8503).
- [ ] **Deferred (chat later):** drop-pin → live ₱/sqm prediction on the map (on-demand layer already exists). Decide interaction + whether to keep any coarse heat layer.
- [ ] Optional visual polish toward reference (dark control rail, top stat strip, donut element).

### Data expansion (Decision 35f) — prompts issued, execution pending
- [ ] **[COPILOT]** Extend Lamudi scraper (add Talisay; land/lot category per LGU; add `lot_area_sqm` + `property_type_raw`).
- [ ] **[COPILOT]** Merge + enrich new rows (append-only; recompute MCRAI/road via canonical scripts; log_price=log(ppsqm)); then re-run compute_road_distances → compute_hansen_scores → prepare_stratified_abt → run_models_stratified.

### Manuscript follow-ups from this session
- [ ] Ch3/Ch4: document the log_price correction + per-sqm target; report **median APE** alongside MAPE.
- [ ] Ch7: replace results table with the stratified numbers (Decision 35a).
- [ ] Ch8: per-stratum SHAP interpretation from `EDA/plots/10_stratified_models/`.

---

---

## Redefense Remediation — 2026-05-14

> Defense was May 9, 2026. Redefense required. Three issues raised by advisor:
> 1. Single global model on mixed property types creates unresolvable variance (condo PHP 175K/sqm vs lot PHP 30K/sqm — nearly 6x difference)
> 2. EDA depth insufficient — no per-stratum within-open_market analysis
> 3. CBD selection method stated weakly (IT Park dropped on r=0.99; Minglanilla "likely fails threshold")
>
> Plan: `~/.claude/plans/wise-jumping-trinket.md`
> Manuscript rewrites DEFERRED until Phases 1–4 complete.

### Phase 1 — EDA (COMPLETE 2026-05-14)
- [x] Write `thesis_main/Scripts/eda_stratified.py` — per-stratum EDA for 3 proposed strata
- [x] Produce `EDA/stratum_counts.csv`, `EDA/stratum_price_stats.csv`, `EDA/stratum_price_distributions.png`, `EDA/stratum_correlations.png`
- [x] Strata confirmed viable: Condo 706 rows, Vacant Lot 217 rows, Houses 568 rows — all 6 LGUs represented

### ABT Final Cleanup (COMPLETE 2026-05-14 — Decision 26)
- [x] Write `thesis_main/Scripts/cleanup_abt_final.py` and run it
- [x] Drop all non-open_market rows (−428 rows)
- [x] Drop property ID 1967 (PHP 14.3M/sqm data error — −1 row)
- [x] Drop 15 "Commercial Lot" entries miscategorized under Vacant Lot
- [x] Reclassify property IDs 707+386 Single Detached → Condominium (penthouse units)
- [x] ABT now: 1,603 rows × 50 cols (open_market only)
- **Note**: Property ID 769 (Single Detached, PHP 4.60/sqm, Mandaue) is still in ABT — filter it in `run_models_stratified.py`

### LGU Boundary Polygons (COMPLETE 2026-05-14)
- [x] Write `thesis_main/Scripts/fetch_lgu_boundaries.py`
- [x] Download Geoboundaries ADM3 full-resolution GeoJSON — all 6 Metro Cebu LGU polygons confirmed
- [x] Save to `thesis_main/Data/GIS/lgu_boundaries.geojson`
- [x] Point-in-polygon check against ABT run — coordinates validated

### Phase 2 — Stratification Decision (COMPLETE 2026-05-14 — Decision 27)
- [x] Log Decision 27 in `modeling_decisions.md`: 3-stratum design confirmed
  - Stratum A: Condominium (706 rows)
  - Stratum B: Vacant Lot (217 rows)
  - Stratum C: Houses — Single Detached + House and Lot + Townhouse + Apartment (568 rows)
- [x] Literature basis logged: Droes et al. (2019), Usman et al. (2020)

### Phase 3 — MCRAI Literature Research (COMPLETE 2026-05-15 — Decision 28)
- [x] Deep research: 9 MCRAI categories validated against SE Asian hedonic literature (10 studies reviewed; see `thesis_main/reference/mcrai_lit_phase3.md`)
- [x] Log Decision 28 in `modeling_decisions.md`: MCRAI category reduction
  - **Finance retired**: no SE Asian hedonic study uses banking/ATM proximity as standalone residential amenity category
  - **Hospitals added** (new, 3.0km radius): separate from primary_care (health.csv = clinics/GPs only). Basis: Peng & Chiang (2015), Li et al. (2022)
  - **Health redefined** as primary care only (2.0km radius). hospitals.csv = separate 42-row file
  - **Transport, education, recreation, grocery**: retained — all confirmed across ≥3 SE Asian studies
  - **Security, tourism, retail_density**: retained as individual model features only (already excluded from composite per Decision 20)
- [x] `compute_hansen_scores.py` updated: finance removed from category list and radii dict
- [x] `filter_to_lgu_scope.py` updated: finance.csv removed from AMENITY_FILES
- **Next decision number: 29**

### Phase 4 — Stratified Model Build (PENDING — blocked on Hansen recompute)
- [ ] **[COPILOT]** Write `thesis_main/Scripts/run_models_stratified.py`
  - Read `abt_clean.csv`, filter to open_market, split into 3 strata
  - Per stratum: OLS → RF → XGBoost → SHAP on best tree model
  - Feature set differences by stratum (floor_area drops for lots; bedrooms/bathrooms drop for lots)
  - Filter property ID 769 before modeling
  - Save per-stratum artifacts to `thesis_main/Models/stratified/`
  - Print metrics table: MAPE, MAE, RMSE, R² per stratum vs. global model baseline
- [ ] Compare within-stratum MAPE vs. global model MAPE for the same rows
- [ ] Log Decision 29 in `modeling_decisions.md`: final stratified model results

### Phase 5 — Manuscript Rewrites (DEFERRED — pending Phase 4)
- [ ] Chapter 3 §3.3 stratification method
- [ ] Chapter 3 §3.4.1 CBD selection (formal Giuliano & Small two-stage statement; remove "likely" language)
- [ ] Chapter 4 per-stratum EDA figures
- [ ] Chapter 7 stratified results table
- [ ] Chapter 8 per-stratum SHAP interpretation

---

## Manuscript Pre-Defense Pass — 2026-05-07

> Defense: May 9, 2026. Issues raised during the manuscript review against the post-Decision-22/23/24/25 reference state (RF baseline deployed, ABT = 2,047 rows, modeling-ready = 1,491 rows).
> **Status as of 2026-05-07 session**: All Critical, Moderate, and Tables/Diagrams audit items are complete EXCEPT the items marked below.

### Critical — stale numbers and content contradictions

- [x] **Chapter 4 — refresh all ABT figures to post-cleanup state** — DONE
- [x] **Chapter 7 — regenerate SHAP top-10 table from current artifacts** — DONE (table rebuilt from EDA PNGs; narrative updated)
- [x] **Chapter 8 — re-ground polycentric narrative on the cleaned-sample SHAP** — DONE (§8.1, §8.2, §8.4 updated; Consolacion #4 in both models; Naga scaled back)
- [x] **Chapter 9 — RQ1 answer updated** — DONE (Consolacion as top locational signal; Mactan CBD and Naga removed from strongest-feature list)
- [x] **Chapter 10 — all internal project references removed** — DONE (Decision N, Phase D, task log, deployment section rewritten)
- [x] **Appendix B — city distribution table refreshed** — DONE (2,047 total; per-LGU counts verified against cleaned ABT)

- [ ] **IVS citation key mismatch** — OPEN: `\parencite{ivs2020}` in biblio.bib points to "IVS 2020" but prose in chapters 1, 2, 3 says "IVS 2025". Either (a) add an `ivs2025` entry for the 2025 edition if it exists, or (b) change the "IVS 2025" prose to "IVS 2022" or "IVS 2020" to match the bib entry. **Needs author decision.**

### Moderate — internal consistency

- [x] **Chapter 3 §3.1** — target variable clarified: log_price is the training target; price_per_sqm is the substantive diagnostic. DONE.
- [x] **Chapter 3 §3.6.2** — hedonic equation LHS corrected from `ln(price_per_sqm)` to `ln(price_php)`. Clarifying note added. DONE.
- [x] **Chapter 3 §3.3** — "2,075 ABT rows" → "2,047 ABT rows". DONE.
- [x] **Chapter 1 §1.6** — XGBoost "primary candidate" softened to "strong candidate"; deferred to Ch7 for results. DONE.
- [x] **Chapter 6 §6.1** — "was expected to be the strongest" is already past tense and describes prior expectation; acceptable as-is. No fix needed.
- [x] **Chapter 5 dummy count** — Apartment IS present (2 rows) in the 1,491-row modeling set; 6 property types × drop_first = 5 dummies. Text is correct. No fix needed.
- [x] **Chapter 4 §4.3 inline "110 rows"** — fixed to "107 rows". DONE.
- [x] **Chapter 4 §4.3 "Decision 18"** — replaced with "targeted POI re-fetch". DONE.
- [x] **Chapter 6 §6.7 "Decision 20"** — replaced with natural language. DONE.

### Tables and Diagrams Pass — 2026-05-07

- [x] **Row terminator audit** — CLEAN. No single-backslash terminators in any tabular block. Appendix B `\\` terminators fixed during number refresh.
- [x] **Column-width audit** — CLEAN. All `p{}` width sums ≤ 0.96 across all tables.
- [x] **Figure path audit** — CLEAN. All 3 `\includegraphics` paths resolve correctly (`../../EDA/` from `thesis_main/Manuscript/` resolves to root `EDA/` folder).
- [x] **Caption + label audit** — CLEAN. All tables have captions and labels. Unreferenced tables are all introduced inline; no isolated orphans.
- [ ] **Compile-and-eyeball pass** — OPEN. Run `latexmk -pdf main.tex` in `thesis_main/Manuscript/` after all assets are inserted. PDF already built once; re-run after diagram additions.
- [ ] **List-of-tables and list-of-figures sync** — OPEN. Re-run LaTeX build after all figures are inserted. LOF will now show 10 figures (was 3).
- [x] **Tier 1 figures inserted** — DONE 2026-05-07. The following figures were inserted with `\begin{figure}` blocks; image files confirmed on disk:
  - `fig:study-area` — Ch1 §1.5, `diagrams/Study-Area-Map.png`
  - `fig:price-by-segment` — Ch4 §4.3, `EDA/price_by_segment.png`
  - `fig:price-by-property-type` — Ch4 §4.3, `EDA/price_by_property_type.png`
  - `fig:price-by-city` — Ch4 §4.3, `EDA/price_by_city_open_market.png`
  - `fig:missingness` — Ch4 §4.4, `EDA/missingness_top15.png`
  - `fig:mcrai-weights` — Ch6 §6.7, `EDA/mcrai_shap_weights.png`
  - `fig:xgb-actual-vs-pred` — Ch7 §7.5, `EDA/xgb_actual_vs_predicted.png`
- [x] **EmpiricalFramework.drawio updated** — DONE 2026-05-07. BSP RPPI removed; OSM fixed to road network only; geospatial IVs updated (osmnx, MCRAI, no CBRT/Haversine); admin_macro trimmed to BIR only; RF labeled DEPLOYED; XGB labeled Comparator; Bayesian/Streamlit exploratory box removed; Streamlit added to QGIS deliverable; IVS edition year dropped.
- [ ] **Pending Tier 2 assets** — OPEN. Author must create and save to `thesis_main/Manuscript/diagrams/` before Claude can insert `\begin{figure}` blocks:
  - **QGIS: Metro Cebu Study Area screenshot** (new QGIS screenshot with CBD node labels; existing Study-Area-Map.png already inserted — verify it shows CBD nodes)
  - **QGIS: Property Distribution Map** → `diagrams/property_distribution_map.png`
  - **QGIS: POI Coverage Map** (9 MCRAI categories; GeoJSONs in `thesis_main/QGIS/`) → `diagrams/poi_coverage_map.png`
  - **Streamlit: Property Predictor screenshot** → `diagrams/streamlit_predictor.png`
  - **Streamlit: Price Surface map** (or QGIS equivalent) → `diagrams/price_surface_map.png`
  - **draw.io: Data Pipeline** (export `Presentations/assets/Data-Pipeline-Updated.drawio` to PNG) → `diagrams/data_pipeline.png`
  - **Mermaid: Modeling Pipeline** (render `diagrams/Modeling-Pipeline.mermaid` to PNG) → `diagrams/modeling_pipeline.png`
  - **draw.io: Empirical Framework** (open updated `thesis_main/EmpiricalFramework.drawio`, export PNG 2× scale) → `diagrams/EmpiricalFramework.png`

---

## Manuscript Format Compliance Pass — 2026-05-05
- [x] Move LaTeX manuscript workflow fully into `thesis_main/Manuscript/`
- [x] Add BSDS prelim-page scaffold: title page, approval sheet, dedication, abstract, acknowledgment, contents, and list sections
- [x] Scaffold Chapters 4–10 and appendices in LaTeX
- [x] Write Chapters 1–3 compliance audit (`chapters_1_3_compliance_audit.md`)
- [x] Replace approval sheet placeholders with final adviser and panel names
- [ ] Replace dedication and acknowledgment placeholders with final author text
- [ ] Review the new abstract and revise for final submission tone
- [ ] Fill Chapters 4–10 with thesis content following the BSDS writing guide

## Current Working Status
- [x] Build and enrich the Analytics Base Table (`analytics_base_table.csv`)
- [x] Append bank ROPA sources (BPI, Metrobank, Bank of Commerce, Landbank, China Bank Savings)
- [x] Complete geocoding, CBD distances, amenity scores, spatial lag, and BIR join
- [x] Expand ABT to 1,185 rows × 46 columns across 8 sources
- [x] Apply `clean_abt.py`: filter to 6-LGU scope, drop `dist_cbrt_nearest_m` → `abt_clean.csv` (1,120 rows × 45 cols)
- [x] Standardize property types, flag outliers, drop legacy columns, compute Hansen scores → ABT now 1,110 rows × 50 cols
- [x] **[COPILOT — DONE]** ABT recomputation batch (5 tasks — verified 2026-04-22)
- [x] **[COPILOT — DONE]** ABT preprocessing decisions (Decisions 1–4) — verified 2026-04-22
- [x] **[COPILOT — DONE]** POI data quality fixes (finance.csv + retail_density.csv) before Hansen rerun
- [x] **[COPILOT — DONE]** MCRAI Phase 1 — scripts refactored, 9 categories, mcrai_* columns, category-specific radii. tourism.csv refreshed (440 rows). ABT: 1,110 × 50. Issues found: recreation/retail_density POIs incomplete, security radius too tight.
- [x] **[COPILOT — DONE]** MCRAI Phase 2 — security radius 1km → 2km; security Lapu-Lapu zeros fixed (80.4% → 22.4%). Recreation/retail_density Lapu-Lapu still above threshold after radius expansion.
- [x] **[COPILOT — DONE]** MCRAI Phase 3 — targeted Lapu-Lapu re-fetch for recreation + retail_density; recreation.csv +221 rows (total 905), retail_density.csv +101 rows (total 499). Final zero rates: mcrai_recreation Lapu-Lapu 1.0%, mcrai_retail_density Lapu-Lapu 20.5%. Both targets cleared. ABT: 1,110 × 50.
- [ ] **[NEXT]** Freeze the modeling-ready ABT and run EDA
- [ ] Start EDA on the cleaned ABT

## Copilot ABT Recomputation Tasks (2026-04-22) — COMPLETE
> All decisions documented in `thesis_main/reference/modeling_decisions.md`
> Final ABT state after these tasks: 1,110 rows × 41 columns

- [x] **Task 1** — Removed `it_park`, `minglanilla_poblacion`, `minglanilla_lipata` from `define_cbds.py`; `cbd_nodes.csv` now has 7 nodes
- [x] **Task 2** — CBD distances switched to osmnx network distance (Dijkstra, haversine fallback); 3 dropped columns confirmed absent; `network_utils.py` created; Metro Cebu graph cached at `metro_cebu_network.pkl` (23,501 nodes, 27,592 edges)
- [x] **Task 3** — `is_mactan_island` added; verified 312 Lapu-Lapu City rows = 1
- [x] **Task 4** — Hansen scores recomputed with network distance; `hansen_transport` mean changed 238.48 → 158.33 (expected: network distances longer than Haversine); `hansen_composite` 88.10 → 57.42
- [x] **Task 5** — All 7 `amenity_score_*` columns dropped; confirmed absent

## Copilot ABT Preprocessing Tasks (Decisions 1–4) — COMPLETE (2026-04-22)
> Final ABT state: 1,110 rows × 47 columns. All key nulls resolved.

- [x] **Decision 1** — `area_sqm` created (floor_area_sqm → lot_area_sqm fallback); `is_vacant_lot` flag added; 32 double-null rows back-filled from imputed floor_area_sqm
- [x] **Decision 2** — `bedrooms` and `bathrooms` imputed (0 for vacant lots, grouped median for all others); `bedrooms_imputed` and `bathrooms_imputed` flags added; 0 nulls remaining
- [x] **Decision 3** — `floor_area_sqm` imputed (grouped median by property_type + city); `floor_area_imputed` flag added; 0 nulls remaining
- [x] **Decision 4** — `market_segment` added: open_market=682, bank_ropa=320, floor_price=108; 0 nulls

## Custom Accessibility Scoring — Pending Literature (Advisor Suggestion)

> Raised by advisor, 2026-04-22. Do not implement until literature is found.

**The issue:** The current Hansen gravity scores follow the Project OHANA framework, which was designed for nationwide amenity accessibility equity mapping across the Philippines — a different objective from residential property valuation in Metro Cebu. Applying OHANA's framework uncritically means the thesis is borrowing a methodology designed for a different purpose.

**The advisor's direction:** Develop a custom accessibility scoring model tailored specifically to Metro Cebu residential valuation. This would make the thesis methodologically original rather than a direct application of an existing framework.

**What this might involve:**
- Custom category weights grounded in Cebu-specific literature (e.g., Agosto 2017 identified transport accessibility as the primary driver — should it carry more weight than in OHANA?)
- Custom radius selection based on Metro Cebu's urban morphology and commuting patterns
- Possibly different decay parameters (β) calibrated to local travel behavior
- Category selection and weighting justified by local valuation practice, not just general social infrastructure equity

**What's needed before designing this:**
- Literature on custom accessibility index design for hedonic price models
- Literature on how weights and radii have been calibrated in comparable studies (Southeast Asian cities preferred)
- Review of how Agosto (2017) and the JICA Roadmap describe accessibility priorities in Cebu

**Status:** Parked. Find literature first, then design the custom scoring framework before the next Hansen recomputation.

---

## POI Data Quality Audit — finance.csv and retail_density.csv (2026-04-25)

> Audit run by Copilot. Fixes must be completed BEFORE rerunning Hansen scores.
> Do NOT rerun compute_hansen_scores.py until all 9 categories are clean and ready.

### finance.csv — 3 issues found

1. **Spatial leak** — lat values up to 10.57 (Danao City), outside the 6-LGU study scope. Filter to Metro Cebu bbox: lat 10.17–10.43, lon 123.74–124.07.
2. **Missing `lgu` column** — add during the spatial filter step.
3. **105 "Unnamed finance" entries** — valid ATMs/branches with no Google Maps name. **Keep them.** Dropping these would undercount financial access in peripheral LGUs (Minglanilla, Consolacion) where named ATMs are scarce.

- [ ] Filter finance.csv to 6-LGU bbox and add lgu column

### retail_density.csv — 2 issues found

1. **~60 noise entries** — Google's `convenience_store` type returned false positives: hotels (Mabolo Royal Hotel), pharmacies (Brigada Pharmacy), gas stations (JSY Gasoline Service Station), cafes. Remove using keyword blocklist.
2. **7-Eleven text search failed** (INVALID_REQUEST — missing `location` parameter). 7-Elevens that Google natively tagged as `convenience_store` are already captured (~61 entries). Check coverage before deciding whether to re-fetch.

- [ ] Clean retail_density.csv — remove non-convenience-store entries via keyword blocklist
- [ ] Check: count existing 7-Eleven entries in retail_density.csv. If coverage looks thin across all 6 LGUs, fix the INVALID_REQUEST and re-fetch. Otherwise skip.

### Hold on Hansen rerun

- [ ] Complete all POI fixes above first
- [ ] Also complete Decision 9 (fetch tourism.csv, recreation.csv, fix network_utils.py radius)
- [ ] Only then rerun compute_hansen_scores.py once — with all 9 categories clean

---

## Pipeline Orchestrator — Build Before Adding New Data

> Must be done BEFORE scraping Dot Property or MyProperty PH.
> Current scripts are individual modules with no orchestrated sequence.

- [ ] **[COPILOT]** Build `thesis_main/Scripts/run_pipeline.py` — an orchestrated end-to-end pipeline that runs all steps in the correct order for new property data:
  1. Scrape/ingest raw listings (source-specific scripts)
  2. Clean and standardize property types
  3. Geocode new rows only (skip already-geocoded rows to save API calls)
  4. BIR zonal value join (`join_bir_zonal.py`)
  5. CBD distances via network routing (`enrich_abt.py`)
  6. MCRAI scores (`compute_hansen_scores.py` — static POI files, just rerun)
  7. ABT preprocessing (imputation, market_segment, area_sqm, flags)
  8. Merge into `abt_clean.csv` (append new rows, deduplicate by property_id)

  Key design requirements:
  - Skip geocoding for rows that already have lat/lon (cost control)
  - Skip BIR join for rows that already have bir_zonal_rr_median
  - Log how many rows were added, how many skipped, and match rates
  - Print final ABT shape after each major step

---

## Phase C — Lamudi Extended Scrape (COMPLETE 2026-05-04)

- [x] Extended Lamudi scrape: `scrape_index.py` + `scrape_properties.py` — 4,473 raw rows in `lamudi_cebu_full.csv`
- [x] Cleaned and filtered via `process_lamudi_phase_c.py` — 969 net new open_market rows in `phase_c_lamudi.csv`
  - Price bounds filter: PHP 500K–500M (dropped 245 rows)
  - Spatial cap: max 3 listings per rounded lat/lon (dropped 1,167 rows — confirmed Lapu-Lapu condo cluster issue)
  - ABT dedup: 504 rows already in existing dataset
- [x] **Decision 18** — Naga City rows (4) dropped from merge; Naga remains CBD node only (see modeling_decisions.md)
- [ ] **[NEXT — COPILOT]** Merge `phase_c_lamudi.csv` into ABT and enrich (`merge_phase_c.py`)

## Phase D — Naga City (Deferred)

> Prerequisite: 150–200 verified open-market Naga City residential listings from Lamudi or alternative source.
> Do not start until Phase C merge and retrain are complete.

- [ ] Scrape 150–200 Naga City listings specifically
- [ ] Run through geocode → enrich → merge pipeline
- [ ] Add Naga as 7th training LGU in a future model version

## Additional Data Sources — On Standby

> Only scrape if more data is needed after EDA reveals thin coverage (e.g., Consolacion, Minglanilla, specific property types).

- **Dot Property** — condos, houses, townhouses, villas, apartments, land in Cebu (Cloudflare-blocked, requires Playwright)
- **MyProperty PH** — residential for rent/sale (Cloudflare-blocked, requires Playwright)

Note: if scraped, these would be `open_market` listings — same as Lamudi. Run through the same geocoding, BIR join, and Hansen pipeline before merging into the ABT.

---

## Jeepney Transport — Resolved (2026-04-22)
- [x] Confirmed: no separate jeepney route dataset was built in prior sessions
- [x] Transport layer is fully integrated as `hansen_transport` in the ABT
- The previous session replaced terminal-node transport (69 rows, `transport_terminals_backup.csv`) with a road-corridor proxy (2,643 OSM highway WAY midpoints) because jeepney service in Cebu is corridor-based, not terminal-based
- `hansen_transport` (mean=238.48) reflects proximity to road corridors along which jeepneys operate — it is a transport accessibility proxy, not a direct jeepney route measurement
- No further data collection needed; describe accurately in Chapter 3 (see thesis-safe framing below)

**Thesis-safe Chapter 3 framing (draft):**
> Transport accessibility was initially represented using terminal-like nodes. Because jeepney service in Metro Cebu is not strictly terminal-based and is frequently accessed along road corridors, this was replaced with a corridor-based proxy. The revised transport layer uses OSM highway way centers as an approximation of corridor accessibility, computed via Hansen gravity scoring. This should be interpreted as a transport accessibility proxy rather than a direct measure of jeepney operations or ridership.

## ABT Readiness Before Modeling

> **Immediate blockers before modeling** (in order):
> 1. `price_type` recode — banks are still mixed into `asking` / `floor` labels and should be normalized before training
> 2. Missingness strategy — `bedrooms`, `bathrooms`, and `lot_area_sqm` have structural nulls that need an explicit treatment
> 3. CBD distance audit — the 10 hub-distance variables should be checked for redundancy before model fitting

- [x] Confirm final modeling geography: 6-LGU scope (Cebu City, Mandaue City, Lapu-Lapu City, Talisay City, Minglanilla, Consolacion)
- [x] Filter rows to the 6-LGU scope — drop all records outside the Metro Cebu study area (`clean_abt.py`: dropped 65 rows from 7 out-of-scope cities)
- [x] Standardize `property_type` into a unified residential taxonomy (`standardize_property_types.py`); 10 non-residential BDO rows dropped → 1,110 rows
- [x] Resolve `price_type` mix — Decision: replace with `market_segment` (open_market / bank_ropa / floor_price); predict at open_market for deployed map (see modeling_decisions.md Decision 4)
- [x] Decide missing-data strategy for `bedrooms`, `bathrooms`, `lot_area_sqm` (see modeling_decisions.md Decisions 1–3)
- [ ] Implement all ABT preprocessing decisions (Decisions 1–7) via Copilot — see Copilot task list above
- [x] Compute `price_outlier_flag` for bank ROPA rows (`flag_ropa_outliers.py`); used p01/p99 of full ABT; 4 rows flagged (2 BoC, 2 Metrobank); 0 nulls remaining
- [x] Drop legacy null columns (`dist_cbd_m`, `bir_zonal_value`, `valuation_gap`) and regenerate `valuation_gap = price_per_sqm − bir_zonal_rr_median` (`drop_legacy_columns.py`); ABT now 1,110 rows × 43 cols
- [x] Compute Hansen Gravity accessibility scores for 6 amenity categories (`compute_hansen_scores.py`); β=2.0, 5 km radius, Google Maps Places POIs; 7 new columns appended → ABT now 1,110 rows × 50 cols
- [x] Replace terminal-node `transport.csv` (69 rows) with OSM road corridor midpoints via Overpass API (`out center` on highway WAYs); 2,643 unique road segments retained after de-duplication by OSM way ID; re-ran `compute_hansen_scores.py` → `hansen_transport` mean=238.48, `hansen_composite` mean=88.10
  - Note: `transport.csv` `lgu` values now indicate fetch provenance from overlapping LGU bounding boxes, not strict final administrative assignment after de-duplication
- [ ] Audit the 10 CBD distance variables for redundancy or multicollinearity before training
- [x] Decide whether road accessibility will be added before modeling or deferred to a post-baseline enhancement
  - Decision: OSM road corridor midpoints (2,643 ways) implemented via Overpass API; `hansen_transport` column recomputed

## Modeling Roadmap

### QGIS Verification
- [ ] Export road network for QGIS verification (`export_network_for_qgis.py` — edges, nodes, transport midpoints as GeoJSON)
- [x] **[DONE]** Export one GeoJSON per MCRAI POI category — 9 files in `thesis_main/QGIS/`. All valid FeatureCollections, Point geometry, zero null coordinates. Note: education, finance, grocery, health, security are missing `lgu` property — source CSVs in `Data/amenities/` predate the lgu column. Not a blocker for QGIS verification but needs a spatial join if LGU-level filtering is required.
- [ ] Visually verify in QGIS: Mactan bridge routes present, road network covers all 6 LGUs, transport midpoints look like road corridor centers

### Pre-Modeling Data Prep
- [x] Build the final modeling table from the cleaned ABT (rows 431, 658, 705 dropped; null price_per_sqm and spatial_lag rows excluded — Decision 10)
- [x] CBD distance multicollinearity audit — `dist_talisay_tabunok_m` dropped from X_ols; retained in X_full (Decision 11)
- [x] Additional OLS collinearity drops: `is_mactan_island`, `bir_zonal_rr_log`, `is_vacant_lot` removed from X_ols only (Decision 12)
- [x] Log-transform area variables for X_ols (`log_lot_area_sqm`, `log_floor_area_sqm`, `log_area_sqm`) — log-log hedonic spec (Decision 13)
- [x] `floor_area_imputed` excluded from feature matrix — bank_ropa proxy (87% concentration), not genuine missingness signal (Decision 16)
- [x] **[DECISION 17 — COPILOT IN FLIGHT]** Restrict training data to `open_market` segment only (IVS 104 Market Value definition). In `run_models.py`: filter to open_market before encoding; remove `market_segment` from CAT_COLS. In `app/lib/features.py`: remove `market_segment_floor_price` and `market_segment_open_market`. In `app/pages/2_Property_Predictor.py`: remove `FIXED_FEATURES` filter from SHAP section.

### Modeling — Done
- [x] Run EDA — price distributions, feature correlations, CBD distance correlation matrix (`cbd_distance_corr.png`) (inferred from Decision 11 source)
- [x] Stage 1 OLS — fit with all 9 `mcrai_*` columns. Result: only `mcrai_tourism` (negative, disamenity) and `mcrai_retail_density` (positive) reached p < 0.05. City dummies absorbed most MCRAI spatial variation.
- [x] Stage 2 MCRAI weight derivation — historical RF SHAP phase recorded (Decisions 14-15). `mcrai_shap_weights.txt` retained as an archived intermediate output only; it is not the current composite definition after Decision 20.
- [x] Fit final OLS hedonic baseline — train R² 0.890, test R² 0.394 (after log-area fix) [PRE-RETRAIN]
- [x] Fit Random Forest — test R² 0.641 [PRE-RETRAIN — 682 rows]
- [x] Fit XGBoost — test R² 0.616 [PRE-RETRAIN — 682 rows]
- [x] Generate SHAP outputs for RF model (used for Stage 2 weight derivation)
- [x] **[RETRAINED 2026-05-05 — historical pre-cleanup sample]** RF and XGBoost retrained on 1,516 open_market rows (Decision 17 filter + Phase C data). Decision 19 fixes applied to `run_models.py` (lot_area_sqm imputer fix, market_segment exclusion, OLS collinearity cleanup). Historical results:
  - OLS: train R²=0.837, test R²=0.260 (MAPE 154.65% — OLS log back-transform instability, expected)
  - **RF: test R²=0.786, MAPE=59.06%, MAE=6.53M, RMSE=31.4M**
  - **XGBoost: test R²=0.808, MAPE=42.83%, MAE=5.69M, RMSE=29.7M** ← best model
  - SHAP regenerated: `EDA/shap_rf_summary.png`, `EDA/shap_xgb_summary.png`
  - MCRAI Stage 2 diagnostic report regenerated: `Models/mcrai_stage2_weights.txt` now leads with the Decision 20 final composite specification and keeps normalized OLS coefficients as diagnostics only
  - **SHAP top features (RF+XGB)**: dist_naga_city_m (#1 both), property type dummies, longitude, dist_consolacion_m, dist_mactan_cbd_m

### Modeling — Still Pending
- [x] **[DECISION 20 — 2026-05-05]** MCRAI composite restricted to positive-coefficient categories only (education, grocery, recreation, transport). Security, tourism, retail_density excluded from composite — negative OLS coefficients indicate spatial sorting artifacts, not genuine residential amenities. Weights: education 0.401, grocery 0.310, recreation 0.199, transport 0.102. See modeling_decisions.md Decision 20.
- [x] **[LITERATURE — DONE 2026-05-07, partial]** Spatial sorting literature confirmed for security and retail. Tourism partially supported. Full citations in `thesis_main/reference/lit_decision20_spatial_sorting.md`.
  - Security: Tiebout (1956), Bayer & McMillan (2012) for sorting mechanism; Dronyk-Trosper (2017) for nonlinear proximity disamenity; Brasington & Parent (2024) for service-quality framing. ✅
  - Retail: Yang et al. (2016) Seoul inverted-U; Song & Knaap (2004) mixed land use. ✅
  - Tourism: Chen & Jim (2010) Shenzhen disamenities (limited scope — covers urban villages, not resorts). ⚠️ **Still needed: verify the "Shenzhen theme park study" (ref 20 in POI analysis lit file) via Google Scholar/Scopus before citing in manuscript.**
- [x] **[COPILOT — DONE 2026-05-06]** Recompute `mcrai_composite` in `compute_hansen_scores.py` using Decision 20 positive-only OLS weights. `abt_clean.csv` refreshed: `mcrai_composite` mean=27.4098, zeros=5. Individual `mcrai_*` columns unchanged. Network rerun not required — composite recomputed from existing columns.
- [x] **[DONE 2026-05-06 — Decision 21, historical pre-cleanup sample]** Hyperparameter tuning: RF and XGBoost via `tune_models.py` (RandomizedSearchCV, 30 iter, 5-fold CV). Result: neither tuned model beat its baseline on the 1,516-row pre-cleanup sample. See Decision 21 in modeling_decisions.md.
  - RF tuned: R²=0.667, MAPE=61.40% — worse than baseline (R²=0.786, MAPE=59.06%)
  - XGBoost tuned: R²=0.800, MAPE=44.31% — slightly worse than baseline (R²=0.808, MAPE=42.83%)
  - `rf_tuned.pkl`, `xgb_tuned.pkl` saved for reference; tuned models were not rerun after Decision 22
- [x] **[DONE 2026-05-06 — Decision 22]** `property_type` cleanup: removed the generic `Residential` bucket from the canonical taxonomy.
  - Rule-based recode on Lamudi `Residential` rows: land / lot -> `Vacant Lot`, studio / condo-like -> `Condominium`, villa / house -> `Single Detached`
  - Out-of-scope office / commercial leakage dropped instead of being left inside the residential model sample
  - Post-cleanup validation: `abt_clean.csv` now has 2,047 rows total, `open_market` = 1,619, and the modeling-ready slice = 1,491 rows; `Residential` no longer appears in either the full ABT or modeling sample
  - **[RETRAINED 2026-05-06 — Decision 23]** Baseline models rerun on the cleaned taxonomy. New results: **RF R²=0.8069, MAPE=59.28%, MAE=4.95M, RMSE=27.45M**; **XGBoost R²=0.4915, MAPE=60.14%, MAE=6.32M, RMSE=44.54M**. SHAP regenerated: `EDA/shap_rf_summary.png`, `EDA/shap_xgb_summary.png`. Random Forest is now the deployed model (`Models/rf_model.pkl`).
- [x] **[DONE 2026-05-06 — Decision 24]** Revised retuning / benchmark pass completed on the post-cleanup 1,491-row sample via the rewritten `tune_models.py`.
  - Existing artifact rescoring confirmed RF baseline is still the strongest current `.pkl`: **R²=0.8069, MAPE=59.28%, MAE=4.95M, RMSE=27.45M**.
  - Repeated-CV RF tuning reproduced the earlier weak tuned RF regime (**R²=0.4569, RMSE=46.03M**), so tuning did not rescue RF beyond the baseline.
  - Repeated-CV XGBoost tuning improved over the current XGB baseline (**R²=0.5569, MAPE=58.93%, MAE=6.06M, RMSE=41.58M**) but still remained well behind the baseline RF.
  - OLS benchmark remained weak (**R²=0.0827, RMSE=59.82M**).
  - New artifacts saved: `rf_tuned.pkl`, `xgb_tuned.pkl`, `rf_cv_results.csv`, `xgb_cv_results.csv`, `model_comparison_final.csv`, plus six tuning plots in `EDA/`.
  - Deterministic deployment selection kept the app on **Random Forest baseline** (`Models/rf_model.pkl`).

- [x] **[DONE 2026-05-06 — Decision 25]** Narrow RF baseline-centered confirmation search rerun completed on the same 1,491-row post-cleanup sample.
  - RF grid was narrowed around the deployed baseline regime: `max_features` = 0.8, 0.9, 1.0; `n_estimators` = 200, 300, 400; shallow regularization only.
  - Best RF confirmation params: **max_depth=None, max_features=0.8, min_samples_leaf=1, min_samples_split=2, n_estimators=400**.
  - The confirmation-tuned RF improved over the earlier weak tuned RF regime but still lost to the deployed RF baseline on held-out performance: **R²=0.6798, MAPE=53.00%, MAE=5.08M, RMSE=35.34M** vs baseline **R²=0.8069, MAPE=59.28%, MAE=4.95M, RMSE=27.45M**.
  - XGBoost tuned remained below RF baseline (**R²=0.5569, RMSE=41.58M**); OLS remained weak (**R²=0.0827, RMSE=59.82M**).
  - Conclusion for manuscript and deployment: **baseline Random Forest remains the current production model** after both the broad repeated-CV retuning pass and the narrower baseline-centered RF confirmation pass.


- [x] **[DONE 2026-05-07 — historical pre-property-type-cleanup POI pass]** POI expansion + MCRAI recomputation pass 2 (Decision 18 follow-up):
  - `retail_density.csv`: expanded from 499 → 2,012 rows (added restaurants, cafes, bakeries across all 6 LGUs; bbox contamination fixed). Minglanilla zero rate: 40.3% → 5.6%. Talisay zero rate significantly reduced.
  - `recreation.csv`: merged old 905-row set + new 384-row fetch → 820 rows after false-positive removal (malls, parking, offices). Recreation amenity_type labels normalized (query strings → proper types).
  - `tourism.csv`: 440 → 632 rows (expanded lodge types); 86 residential contamination rows removed (Airbnb-style listings with bedroom counts, studio tower units, room rentals). Pension houses, guesthouses, transient houses retained as legitimate Philippine lodging.
  - `abt_clean.csv` MCRAI recomputed: retail_density mean=43.72, recreation mean=24.44, tourism mean=20.76, composite mean=26.84.
  - **[RETRAINED 2026-05-07 — historical pre-cleanup sample]** Models were retrained on the then-current 1,647-row open_market ABT before Decision 22 removed the generic `Residential` bucket. Those results (**RF R²=0.783 / MAPE=54.76%**, **XGBoost R²=0.803 / MAPE=43.93%**) are retained as project history only and are superseded by the 2026-05-06 post-cleanup baseline rerun under Decision 23.
- [x] **[DONE 2026-05-06 — partial]** Streamlit app verification — core predictor verified in project virtualenv (port 8502):
  - Home page, sidebar, city dropdown, BIR auto-fill: all pass
  - Default submission → PHP 176,661/sqm, PHP 17,666,137 total: pass
  - Optional fields blank → prediction succeeds: pass
  - Lapu-Lapu City edge case: pass (no crash)
  - SHAP waterfall rendered with 15 bars: pass
  - Price Surface page loads without Streamlit crash: pass
  - **Two issues remaining (see below)**
- [ ] **[FIX — Streamlit env]** `shap` not installed in global environment — `streamlit run streamlit_app.py` crashes at Property Predictor with `ModuleNotFoundError: No module named 'shap'`. Fix: always run from project virtualenv. Consider adding a `run_app.sh` wrapper or documenting the correct launch command.
- [ ] **[FIX — Price Surface map]** Price Surface map tiles fail with `access_token=no-token` in browser. `pydeck` / Mapbox requires a valid token. Either: (a) switch to an open tile provider (no token required), or (b) add a valid Mapbox token. Address before the app is shown externally.
- [ ] Final model comparison table: MAPE, MAE, RMSE, R² for OLS / RF / XGBoost — ready to write (numbers in Modeling — Done above and Decision 21)
- [ ] Export RF and XGBoost predictions for map-layer integration

## Map And App Deliverables
- [ ] Finalize the QGIS layer design for predicted price, residuals, and valuation gap
- [ ] Decide whether the map will use both RF and XGBoost outputs or only the best-performing model
- [ ] Streamlit app exists (`thesis_main/app/`) — verify it works end-to-end after Decision 17 feature changes
- [ ] Confirm Streamlit and QGIS outputs are consistent on features and model version

## Methodology Decisions Still Open
- [x] OLS as baseline comparator — decided; not the deployed model
- [ ] Finalize manuscript wording for the implemented road-accessibility feature
- [ ] Decide whether a stricter road-network distance feature should complement the corridor-based transport accessibility signal in a later iteration
- [ ] Revisit the CBD / subcenter literature to better justify malls, town centers, and polycentric nodes used in Metro Cebu

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
- [ ] Update scope language if the ABT remains broader than the 6-LGU thesis frame

## Chapter 2 — Review of Related Literature
- [x] Draft initial version (§2.1–§2.8)
- [x] **Post-panel**: Replace §2.5 (NLP) → §2.5 (Geospatial Feature Engineering)
- [x] **Post-panel**: Update §2.8 synthesis with GIS gap statement
- [x] **Post-panel**: Standardize "value drivers" terminology
- [x] **Post-panel**: Separate lit findings from thesis methodology
- [x] **Official feedback #2**: Clearer RRL structure (ensure arguments build logically)
- [x] **Official feedback #11**: Add more RRL sources (GIS+ML in SE Asia, PH-specific OSM)
- [x] **Official feedback #10**: Literature grounding for custom value driver model
- [ ] Strengthen the literature basis for polycentric CBDs, subcenters, malls, and town-center proxies in Cebu
- [ ] Add literature support for road accessibility if that feature is implemented

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
- [ ] Replace remaining OSM/osmnx amenity references with the implemented Google Maps Places workflow where applicable
- [ ] Add a clear subsection on how the final deployed map will use Random Forest / XGBoost outputs while OLS remains the benchmark model
- [x] Add the road-accessibility feature to methodology only after the implementation decision is settled
  - Implemented: OSM highway ways (`out center`) as transport accessibility nodes; describe in §3.x under Hansen scoring

## Diagrams & Assets
> Existing `.drawio` sources in `Presentations/assets/`. Output to `Manuscript/diagrams/`.

### Ch1 – Problem & Setting
- [ ] **Study Area Map** — QGIS map of Metro Cebu (Cebu City, Mandaue, Lapu-Lapu, Talisay) + CBRT route overlay

### Ch3 – Methodology
- [ ] **Data Landscape** *(revise `Data-Landscape.drawio`)* — Floor (BDO) + Ceiling (Lamudi) → True Market Value. Fix: Lamudi no longer "Future scrape"; typo "Braket" → "Bracket"
- [ ] **Data Pipeline** *(revise `Data-Pipeline.drawio`)* — update to the implemented multi-source flow and current source counts
- [ ] **Empirical Framework** *(revise `Emprerical-Framework.drawio`)* — IVS → Models → Outputs → Validation. Fix: remove outdated NLP/BERT framing if still present
- [ ] **Feature Engineering Summary Table** — LaTeX table: all features, source, type, derivation
- [ ] **Modeling Pipeline Flowchart** — New: cleanup → preprocessing → split → 3 models → evaluation → SHAP → map/app outputs

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
- [ ] Align the draft with the final ABT scope and the actual deployed-model decision

## Literature Verification — Deep Research Sources (URGENT before writing)

> All three Gemini Deep Research outputs contain citations to actual papers and articles.
> These must be verified and added to `biblio.bib` before Chapter 2 or 3 are revised.
> Do NOT cite the AI-generated summary — cite the actual source it referenced.

### Session 1 — Polycentric Urbanism in Metro Cebu
**File**: `thesis_main/Literature/CBD_node_selection/Polycentric Urbanism in Metro Cebu.md`
Key papers to verify and add to biblio.bib:
- [ ] Giuliano & Small (1991) — *Subcenters in the Los Angeles Region*, Regional Science and Urban Economics
- [ ] McMillen (2001) — *Nonparametric Employment Subcenter Identification*, Journal of Urban Economics
- [ ] McMillen (2003) — *Identifying Subcenters*, Journal of Regional Science (or similar)
- [ ] Anas, Arnott & Small (1998) — *Urban Spatial Structure*, Journal of Economic Literature
- [ ] Heikkila et al. (1989) — *What Happened to the CBD-Distance Gradient?*, Regional Science and Urban Economics
- [ ] JICA (2014?) — *Roadmap Study for Sustainable Urban Development in Metro Cebu (Mega Cebu Roadmap 2050)* — URLs in the file
- [ ] Spatial Analysis of Local Competitiveness (MDPI 2023) — Moran's I Metro Cebu study
- [ ] Neoliberal Urbanization in Cebu City — ResearchGate paper

### Session 2 — Expanded POI Analysis
**File**: `thesis_main/Literature/Polycentric_Urbanism/Polycentric Urbanism_ Metro Cebu POI Analysis.md`
Key papers to verify:
- [ ] Coastal amenity hedonic study — Zhuhai, China (sea view = 91% price variation)
- [ ] Beach peer-to-peer rental study — Balearic Islands, Spain (PMC source in file)
- [ ] Bintan Island tourism real estate study (2015–2020)
- [ ] Shenzhen theme park/resort proximity study — negative capitalization effect
- [ ] Taipei convenience store density hedonic study — quantile regression, 100m radius premium
- [ ] Jakarta green space hedonic study — 17.1% and 9.2% land price increase
- [ ] Singapore park connector discount study (2014–2018) — 6–7% discount within 400m
- [ ] Metro Manila green view index study (PSPNet / Green View Index)
- [ ] Gasoline station hedonic study — Xuancheng, China (−16% at 0–100m)

### 5_Questions — Custom Accessibility Scoring
**File**: `thesis_main/reference/5_Questions.md`
Key papers to verify:
- [ ] Beijing POI hedonic study — two-stage weight derivation from regression coefficients (MDPI source referenced)
- [ ] Tiglao & Rivera (2006) — Metro Manila land market hedonic model, accessibility as central dogma
- [ ] Jakarta LRT land value capture study — MGWR + network centrality
- [ ] South Tangerang hedonic study — malls/hospitals showed no price effect
- [ ] Bangkok condominium hedonic study — transit accessibility = 51.69% of total model weight

**Process**: For each paper above, locate the actual DOI or URL (most are linked in the source files), verify the paper exists and supports the claim, then add to `biblio.bib` using Zotero or manual entry.

---

## Literature Gaps — Pending Zotero Verification
- [ ] **CBD bid-rent theory**: Verify and complete `alonso1964location` in `biblio.bib` (Alonso 1964, *Location and Land Use*)
- [ ] **Monocentric baseline**: Verify and complete `muth1969cities` in `biblio.bib` (Muth 1969, *Cities and Housing*)
- [ ] **Polycentric urbanism**: Verify and complete `giuliano1991subcenters` in `biblio.bib` (Giuliano & Small 1991, *Regional Science and Urban Economics*)
- [ ] **Polycentric distance gradients**: Verify and complete `mcmillen2003employment` in `biblio.bib` (McMillen 2003, *Regional Science and Urban Economics*)
- [ ] **In-text**: Add Alonso (1964) citation in §2.5.2 before the Rosen/Malpezzi sentence — grounds the theoretical basis for distance-to-CBD as a value driver
- [ ] **In-text**: Add polycentric justification in §3 proximity subsection — explain why multiple CBD nodes are used instead of a single monocentric anchor

## LaTeX Sync (Deferred)
- [ ] Sync `chapter1.tex` with revised Ch1
- [ ] Sync `chapter2.tex` with revised Ch2
- [ ] Sync `chapter3.tex` with revised Ch3
- [ ] Update `biblio.bib`

## Verification
- [x] Grep: 0 NLP references remain
- [x] 10/10 initial panel feedback addressed
- [ ] Verify all 12 official feedback items addressed (pending)
- [ ] Verify the ABT cleanup decisions before committing to model training
