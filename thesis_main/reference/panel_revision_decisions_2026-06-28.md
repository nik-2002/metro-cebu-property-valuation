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

## ⚠️ Flags for author to verify
- **MCRAI composite weights sum:** text states education 0.447 + grocery 0.345 + recreation 0.222 = **1.014**, not 1.000. If these are normalized weights they should sum to 1; likely a rounding/typo. Verify against the Stage 1 OLS output / `modeling_decisions.md` and correct the three numbers. (Not changed by Claude — would require inventing values.)

## Decisions to be made (open questions)
- **#2 Sensitivity method:** weight-perturbation grid? leave-one-category-out? β sweep? Pick what is computationally cheap and panel-legible.
- **#4 CBD references:** which exact sources to cite for the 8-node selection (JICA Mega Cebu Roadmap 2050 + which polycentric papers).
- **#6 RF vs XGBoost:** which business-context / interpretability reference papers to anchor the non-performance justification.
- **#3 Ethics:** dedicated section vs. methodology subsection; how much to say on scraping terms-of-use.

---

## Change log
- 2026-06-28 — Log created; seeded with D-01..D-04 and open questions from the comment-review session.
