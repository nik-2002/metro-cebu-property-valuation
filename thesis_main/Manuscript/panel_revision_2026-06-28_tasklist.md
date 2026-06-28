# Panel Revision Task List — Pre-Final Submission

**Comments received:** 2026-06-28 (from advisor, on behalf of the panel + Sir Randy)
**Branch:** `dev/manuscript` (worktree: `thesis-worktrees/manuscript/`) — source of truth for all manuscript edits
**Decision log for this round:** `thesis_main/reference/panel_revision_decisions_2026-06-28.md`

## Submission chain (per advisor's email — do these in order)
1. Address the comments below.
2. **→ Send final paper to Sir Randy** (advisor; give him enough lead time). *Do not delay contacting him.*
3. **→ Back to advisor** (email thread) for **formatting check** before printing.
4. **→ Print.**

> Action now, in parallel with revising: **reach out to Sir Randy early** so his review clock starts.

---

## A. Panel "Good" (no action — context only)
- Adjusted the 3-category categorization.
- Tangible output via the web app.
- Improved overall data mining, modeling, and results.

## B. Presentation-only (NO manuscript action — already passed defense)
- Slides could be improved.
- Texts can be bigger. *(Author's read: these are slide comments, not manuscript. Confirm before ignoring; do not redo slides.)*

---

## C. Manuscript work items

| # | Item | Current state in `dev/manuscript` | What to do | Where | Effort |
|---|------|-----------------------------------|------------|-------|--------|
| 1 | **Better map** (Sir Randy — "good to have") | App map figure exists (`diagrams/webapp_market_map.png`, "Map 1") but it's a plain screenshot: passable, not professional, too much white space. | Produce a higher-fidelity capture of the in-app **Leaflet** map and reframe to cut white space. (Note: QGIS is dropped per Decision 55 — the map is the Leaflet view in the Vite/FastAPI web app.) Polish item, not a blocker. | webapp Leaflet screenshot → replace figure in appendix (and results if referenced) | Med |
| 2 | **Sensitivity analysis on MCRAI scoring** | ❌ Absent (0 hits for "sensitivity"). | New analysis: vary the composite weights (currently education 0.447 / grocery 0.345 / recreation 0.222) and/or the β=2 distance decay, and the keep-positives decision; show how model results / price surface move. Tie to item #8. | new subsection (Ch3 or Ch6/Ch7) + supporting plot | **High** |
| 3 | **Ethical considerations** | ❌ Absent (0 hits "ethic"/"consent"). | New section: web-scraping ethics for public listings (Lamudi/FilipinoHomes/DotProperty), data privacy (listing-level, no PII), responsible use & limitations of valuation outputs. | new methodology subsection or dedicated short section | **High** |
| 4 | **CBD nodes — ground truth & references** | 8 nodes listed; only `giuliano1991subcenters` cited. JICA Roadmap 2050 basis is in project notes but not cited in text. | Add references grounding the 8-node selection (JICA Mega Cebu 2050 + polycentric lit). Strengthen the "why these nodes" justification. | Ch3 §3.4.1 + `biblio.bib` | Med |
| 5 | ✅ **Stratification — make explicit / cite** | DONE (review only). Verified explicit + cited at Ch3 line 7 (`droes2019`, `usman2020`); operationalized §3.4; leak-free GroupKFold in Ch6. No edit needed. | — | Ch3 / Ch6 | — |
| 6 | **RF vs XGBoost — robust justification** | Comparison present (22 hits) but largely performance-based. | Reframe the choice beyond raw metrics: business context, real-world/operational use, interpretability/deployment, plus reference papers. Not merely "RF scored better." | Ch6/Ch7 + Ch8 + citations | Med |
| 7 | ✅ **Distance computation — review** | DONE. Added why network distance over straight-line (road network, Mactan crossings, terrain) + named algorithm/units (shortest-path, Dijkstra, meters). | — | Ch3 §3.4.1 | — |
| 8 | ✅ **Keep positives / remove non-positives (MCRAI composite)** | DONE. Spelled out the two-stage derivation (Stage 1 OLS → normalize significant positive coefficients → Stage 2 weights) and why negatives/non-significant are excluded from the composite but kept as standalone features. ⚠️ Weights as written sum to 1.014 — author to verify. | — | Ch3 §3.4.1 | — |
| 9 | **Accuracy verdict / acceptance** | Metrics reported (MdAPE/PE20, MAPE/COD/PRD) but no explicit "is this acceptable?" statement (0 hits "acceptable"). | Add a clear verdict: is the accuracy acceptable, and acceptable *for what use* (decision-support, not formal appraisal). | Ch8 Results/Discussion or Ch9 Conclusions | Low–Med |

---

## D. Already resolved — verify only (panel "make sure" items)
- **App screenshots in paper** — ✅ present: Appendix "Web Application Screenshots" (Market Map, Price Surface, Property Predictor views).
- **OnePropertee removal** — ✅ explained in Appendix: scraped but excluded due to mis-extracted per-sqm prices and centroid-level geocoding.

---

## Suggested order of attack
1. **Contact Sir Randy now** (workflow gate).
2. Knock out the writing/review items: #7 (distance), #5 (stratification), #8 (keep-positives), #4 (CBD refs), #6 (RF vs XGBoost framing).
3. Add the two new sections: #3 (ethics), #9 (accuracy verdict).
4. Do the heavier analysis: #2 (sensitivity).
5. Polish: #1 (better map).
6. Recompile, then route to Sir Randy → advisor (formatting) → print.
