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

## Decisions to be made (open questions)
- **#2 Sensitivity method:** weight-perturbation grid? leave-one-category-out? β sweep? Pick what is computationally cheap and panel-legible.
- **#4 CBD references:** which exact sources to cite for the 8-node selection (JICA Mega Cebu Roadmap 2050 + which polycentric papers).
- **#6 RF vs XGBoost:** which business-context / interpretability reference papers to anchor the non-performance justification.
- **#3 Ethics:** dedicated section vs. methodology subsection; how much to say on scraping terms-of-use.

---

## Change log
- 2026-06-28 — Log created; seeded with D-01..D-04 and open questions from the comment-review session.
