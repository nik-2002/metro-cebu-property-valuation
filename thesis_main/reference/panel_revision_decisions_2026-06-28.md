# Panel Revision Decision Log — 2026-06-28

**Purpose:** Track decisions made while addressing the panel/Sir Randy comments received 2026-06-28.
**Scope:** This is a SEPARATE log from `modeling_decisions.md` — it covers manuscript-revision decisions for this submission round only. Do not merge into the modeling decision log.
**Branch:** all edits land on `dev/manuscript` (`thesis-worktrees/manuscript/`).
**Companion task list:** `thesis_main/Manuscript/panel_revision_2026-06-28_tasklist.md`

Log format per entry: **Decision** — what was decided · **Why** — reason/grounding · **Affects** — files/chapters · **Status**.

---

## Settled framing (from the 2026-06-28 discussion with the author)

### D-01 — Better map is "good to have," not a blocker
- **Decision:** Treat the higher-fidelity / better-framed map (Sir Randy's comment) as a polish item, sequenced last.
- **Why:** Sir Randy framed it as good-to-have; current "Map 1" is passable, just unprofessional and white-space-heavy.
- **Affects:** webapp/QGIS map export → appendix figure `diagrams/webapp_market_map.png`.
- **Status:** Open.

### D-02 — Sensitivity analysis targets the MCRAI scoring decisions
- **Decision:** The sensitivity analysis will probe the MCRAI composite weights, the β=2 decay, and the keep-positives / drop-negatives decision.
- **Why:** Panel asked for sensitivity on "the scoring"; the keep-positives composite choice (item #8) is the most defensible thing to stress-test.
- **Affects:** Ch3/Ch6/Ch7 (new subsection + plot); links task items #2 and #8.
- **Status:** Open — method to be decided (see open questions).

### D-03 — Accuracy verdict belongs in insights/conclusion
- **Decision:** The explicit "is the accuracy acceptable" verdict goes in Results/Discussion (Ch8) or Conclusions (Ch9), framed around fitness-for-use (decision-support, not formal appraisal).
- **Why:** Panel item #8 wants a clear verdict, not just reported metrics.
- **Affects:** Ch8 / Ch9.
- **Status:** Open.

### D-04 — Slide comments are out of manuscript scope
- **Decision:** "Slides could be improved" and "texts can be bigger" are presentation-only; no manuscript action, no slide redo (already passed).
- **Why:** Advisor noted these were comment-only.
- **Affects:** none (manuscript).
- **Status:** Closed.

---

### D-05 — Distance computation: add network-vs-straight-line rationale + algorithm (item #7)
- **Decision:** Kept the existing operational description; added (a) why network distance was chosen over Haversine (Metro Cebu road network, Mactan bridge crossings, terrain routing) and (b) named the algorithm and units (shortest-path, Dijkstra, meters).
- **Why:** Panel found the distance computation unclear in the presentation; the text described *how* but not *why network distance*, and never named the algorithm.
- **Affects:** `chapter3.tex` §3.4.1 Network Distance Features. **Done.**
- **Status:** Closed.

### D-06 — Keep-positives / remove non-positives made explicit (item #8)
- **Decision:** Spelled out the two-stage weight derivation (Stage 1 OLS → normalize significant positive coefficients → Stage 2 composite weights) and stated explicitly why negative/non-significant categories are excluded from the composite (a benefit index should not net in price-reducing categories) while remaining available as standalone stratum features.
- **Why:** Panel asked for the rationale behind keeping positives and dropping non-positives in the MCRAI scoring. Grounded in `modeling_decisions.md` (two-stage method, "Weight derivation — Two-Stage Method").
- **Affects:** `chapter3.tex` §3.4.1 MCRAI composite paragraph. **Done.** Sets up item #2 (sensitivity should stress-test this exclusion).
- **Status:** Closed.

### D-07 — Stratification is already explicit; no rewrite (item #5)
- **Decision:** No edit. Stratification is explicitly motivated and cited at `chapter3.tex` line 7 (`droes2019`, `usman2020`), operationalized in §3.4 (per-stratum feature trimming), and the leak-free GroupKFold rationale is in `chapter6.tex` §Stratified Fitting.
- **Why:** Author worried it might not be explicit; review found it adequately explicit and referenced. Reopen only if the panel names a specific gap.
- **Status:** Closed (verified, no change).

### D-08 — MCRAI composite weights verified against code; keep deployed values, fix wording
- **Decision:** Keep `0.447 / 0.345 / 0.222` in the manuscript (they match the deployed model) and reword so we do NOT claim they are normalized / sum to 1. Described instead as the positive Stage~1 OLS implicit prices rescaled into the fixed deployed weights, with transport noted as retired to the road-distance features. No model re-run. (Author chose this over renormalizing in code, 2026-06-28.)
- **Verification trail:**
  - `modeling_decisions.md` Decision 20 — 4-category normalized weights: education 0.401, grocery 0.310, recreation 0.199, transport 0.102.
  - Decision 29 — retired transport; printed `0.447 / 0.345 / 0.222` and claimed "Sum = 1.000 (rounding-adjusted in implementation)" — but those print values actually sum to **1.014**.
  - `Scripts/compute_hansen_scores.py:112-117` — hard-codes exactly `0.447 / 0.345 / 0.222` with **no normalization step**. This is the deployed reality; the manuscript matches it.
- **Why the 1.014 sum is immaterial:** `mcrai_composite` is a model feature; scaling it by a constant is monotonic, so RF split-based predictions are unchanged and OLS only rescales that one coefficient. The overshoot has no effect on results.
- **Affects:** `chapter3.tex` §3.4.1 MCRAI composite paragraph. **Done** (wording fixed).
- **Status:** Closed.

### D-09 — CBD node selection grounded in the JICA Roadmap (item #4)
- **Decision:** Added `jica2015metrocebu` to the Network Distance Features paragraph, grounding the 8-node selection in the JICA Roadmap Study (the documented local planning basis from project notes / CLAUDE.md), alongside the existing `giuliano1991subcenters`.
- **Why:** Panel wanted references/ground truth for the 8 CBD nodes; only Giuliano & Small was cited. JICA is the verified local basis for treating Naga, the airport, Mactan, and SRP as anchors.
- **Did NOT use:** `mcmillen2003employment` — flagged PLACEHOLDER in `biblio.bib` ("confirm details in Zotero"). Do not cite until verified.
- **Affects:** `chapter3.tex` §3.4.1. **Done.**
- **Status:** Closed.

### D-10 — RF-vs-XGBoost justified on use, not just metrics (item #6)
- **Decision:** Kept the existing robustness/simplicity framing and added a paragraph in ch7 Best Model Selection: the model backs a decision-support tool, so stable/reproducible/retrainable estimates matter more than a marginal, non-robust accuracy gain; RF averages over independent trees (lower overfitting on the 849–1,300-row noisy per-stratum samples) vs. boosting's sequential residual fitting; flat tuning curves showed boosting's extra capacity bought no reliable gain. Citations: `grinsztajn2022` (tree models strong default on tabular data), `ramolete2023`/`viray2023` (PH ML valuation context).
- **Why:** Panel wanted a robust, business/real-world justification with reference papers, not a performance-only argument.
- **Citation caution:** claims kept to what the sources clearly support — `grinsztajn2022` for tabular tree-model strength; the PH papers cited only as "ML valuation practice in the Philippine setting," not as RF-specific endorsements.
- **Also:** changed ch6 MCRAI wording "renormalized" → "rescaled" for consistency with D-08.
- **Affects:** `chapter7.tex` §Best Model Selection, `chapter6.tex` §MCRAI. **Done.**
- **Status:** Closed.

### D-11 — Explicit accuracy verdict added (item #9)
- **Decision:** Added a dedicated Ch8 subsection "Is the Accuracy Acceptable?" giving a direct fitness-for-use verdict, and echoed a one-sentence verdict in the Ch9 summary. Framing: acceptable for explainable decision-support over the open-market segment (condo ~19%, house ~23% typical error, competitive with Ramolete's band and beating OLS + BIR zonal); vacant lots (~38%) usable only as a rough indicator; explicitly NOT IAAO assessment-grade (COD 36–56, PRD 1.20–1.48 outside ratio-study uniformity) and not a substitute for formal appraisal. Added the PRD>1 fairness caveat (over-values the cheap tail).
- **Why:** Panel item #8/#9 wanted a clear verdict on whether the accuracy is acceptable, not just reported metrics.
- **Citation note:** Matched Ch7's existing descriptive reference to "IAAO ratio-study thresholds" — no IAAO bib entry exists, so none was invented.
- **Affects:** `chapter8.tex` (new subsection), `chapter9.tex` (summary sentence). **Done.**
- **Status:** Closed.

### D-12 — Front-matter list cleanup (formatting; adviser will check)
- **Decisions (author-confirmed 2026-06-28):**
  1. **Continuous numbering** for appendix tables/figures (Tables 23–28, Figures 8–17) instead of apa7's default letter-prefixed A1/C1/D1. Matches the BSDS format guide ("numbered consecutively throughout"). Implemented in `main.tex` by overriding `\thetable`/`\thefigure` after `\appendix` and `\patchcmd`-ing out apa7's per-appendix `\setcounter` resets. Appendix SECTION letters (Appendix A–G) are preserved.
  2. **Combined short lists** to save space: List of Maps follows List of Figures on one page; List of Pictures + List of Appendices + List of Abbreviations share a page. Done by removing forced `\clearpage`s (kept one before Pictures). APA 7 does not govern front-matter list pagination, so this is permitted; the BSDS guide *implies* one-per-page (vii–xii) but does not forbid sharing — **flag for adviser/Sir Randy at the formatting check.**
  3. **List of Tables** kept all appendix tables (per guide); still ~2 pages — accepted as normal.
- **Bugs fixed along the way:**
  - The hand-typed List of Appendices was out of sync (wrong titles B–F, missing Appendix G). Rebuilt correctly (A–G) with page numbers via `\label`/`\pageref` on each appendix section.
  - `chapter3.tex` hard-coded "Appendix~F" for the web-app screenshots, which are actually **Appendix G**. Replaced with `\ref{app:webapp}` so it auto-resolves.
- **Verified:** recompiled, no undefined refs; rendered front-matter pages confirm continuous numbering and the combined layout.
- **Status:** Closed (pending adviser sign-off on the combined-page layout).

## ⚠️ Flags for author to verify
- **(Resolved — see D-08)** Composite weights `0.447/0.345/0.222` verified as the deployed values. Kept as-is with corrected wording; no model change.
- **Doc hygiene (modeling branch, future):** `modeling_decisions.md` Decision 29 prints weights that sum to 1.014 while claiming "Sum = 1.000." Consider correcting that note on `dev/modeling` so the decision log is internally consistent. Not a manuscript blocker.

## Decisions to be made (open questions)
- **#2 Sensitivity method:** weight-perturbation grid? leave-one-category-out? β sweep? Pick what is computationally cheap and panel-legible.
- **#4 CBD references:** which exact sources to cite for the 8-node selection (JICA Mega Cebu Roadmap 2050 + which polycentric papers).
- **#6 RF vs XGBoost:** which business-context / interpretability reference papers to anchor the non-performance justification.
- **#3 Ethics:** dedicated section vs. methodology subsection; how much to say on scraping terms-of-use.

---

## Change log
- 2026-06-28 — Log created; seeded with D-01..D-04 and open questions from the comment-review session.
