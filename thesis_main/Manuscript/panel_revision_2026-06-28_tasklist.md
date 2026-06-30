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
| 1 | ✅ **Better map** (Sir Randy — "good to have") | DONE. The in-app Leaflet capture was low-opacity, had no LGU labels, and was not presentation-grade. Instead of recapturing the app, rendered a static presentation-quality map (`webapp/scripts/render_listings_map.py`, `dev/webapp` f896edaf) from the same `public/data` GeoJSON: 3,372 modeled listings colored by stratum, UTM 51N projection, exposed LGU labels, full-opacity points, legend with counts, scale bar + north arrow. Placed as a Chapter 5 data figure (`fig:listings-distribution`) in the Stratum Split subsection — NOT in the appendix; the three web-app screenshots there are unchanged. | Ch5 §Stratum Split (`diagrams/listings_distribution_map.png`); renderer on `dev/webapp` | — |
| 2 | ✅ **Sensitivity analysis on MCRAI scoring** | DONE (weighting/keep-positives tier). Ran `sensitivity_mcrai_weights.py` on `dev/modeling` (Decision 56): ceteris-paribus sweep of the composite weights (baseline / equal / all-8 keep-positives-off / no-composite / ±25% perturbation), RF params fixed, leak-free group-CV. Result: condo/house error robust to within ~0.5pp; keep-positives mildly helpful not load-bearing. Written up in Ch7 §Sensitivity of the MCRAI Scoring (table) + Ch3 forward ref. β/radii tier (would move Lot, needs re-scoring) deferred. | — | Ch7 §MCRAI Sensitivity; modeling branch | — |
| 3 | ✅ **Ethical considerations** | DONE. Added Ch3 §Ethical Considerations: public non-personal listing data (no PII, property is the unit of analysis, no login-restricted pages); non-commercial academic use + data minimization; data-integrity-as-ethics (OnePropertee removal, asking-price disclosure); responsible use (decision-support not appraisal); PRD>1 fairness caveat; SHAP transparency. ⚠️ Author to confirm: (a) program's ethics-clearance requirement, (b) whether to add an explicit terms-of-use statement. | — | Ch3 §Ethical Considerations | — |
| 4 | ✅ **CBD nodes — ground truth & references** | DONE. Added `jica2015metrocebu` (verified bib entry) grounding the 8-node selection in the JICA Roadmap, alongside `giuliano1991subcenters`. Note: `mcmillen2003employment` is a PLACEHOLDER bib entry — not used; confirm details before citing. | — | Ch3 §3.4.1 | — |
| 5 | ✅ **Stratification — make explicit / cite** | DONE (review only). Verified explicit + cited at Ch3 line 7 (`droes2019`, `usman2020`); operationalized §3.4; leak-free GroupKFold in Ch6. No edit needed. | — | Ch3 / Ch6 | — |
| 6 | ✅ **RF vs XGBoost — robust justification** | DONE. Strengthened ch7 Best Model Selection with intended-use framing (stable/reproducible/retrainable estimates for a decision-support tool), RF's lower overfitting risk on small noisy per-stratum samples, and citations: `grinsztajn2022` (tree models on tabular data), `ramolete2023`/`viray2023` (PH ML valuation). | — | Ch7 §Best Model Selection | — |
| 7 | ✅ **Distance computation — review** | DONE. Added why network distance over straight-line (road network, Mactan crossings, terrain) + named algorithm/units (shortest-path, Dijkstra, meters). | — | Ch3 §3.4.1 | — |
| 8 | ✅ **Keep positives / remove non-positives (MCRAI composite)** | DONE. Spelled out the two-stage derivation and why negatives/non-significant are excluded but kept as standalone features. Weights `0.447/0.345/0.222` verified against `compute_hansen_scores.py` (match deployed model); wording fixed to not claim sum=1 (see decision log D-08). | — | Ch3 §3.4.1 | — |
| 9 | ✅ **Accuracy verdict / acceptance** | DONE. Added Ch8 subsection "Is the Accuracy Acceptable?" — explicit fitness-for-use verdict tied to the real numbers (MdAPE 19/23/38, PE20 51/44/26%, COD 36–56, PRD 1.20–1.48): acceptable for decision-support (condo/house), weak for vacant lots; not IAAO/assessment-grade. Brief verdict echoed in Ch9 summary. | — | Ch8 §Is the Accuracy Acceptable?, Ch9 | — |

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
