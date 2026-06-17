# Thesis Workspace Guidelines

## Project Focus
- Residential real estate valuation thesis, Metro Cebu, Philippines — data science and geospatial features.
- Treat the author as the primary writer. AI supports planning, critique, consistency checks, and targeted revision — not authorship.
- The thesis is a predictive and prescriptive decision support tool for property valuation practice in Metro Cebu.
- Keep Metro Cebu, valuation practice, geospatial features, and decision support central. Do not generalize away local specificity.
- Final deliverable: a Streamlit web app showing a predicted open-market residential price surface across Metro Cebu.

## Project Context (Durable Design Decisions)
- **Spatial scope**: 6 LGUs — Cebu City, Mandaue City, Lapu-Lapu City, Talisay City, Minglanilla, Consolacion.
- **Naga City**: CBD node only (industrial anchor, JICA Roadmap 2050 basis). Not in the training data scope.
- **Data scope (Decision 54, 2026-06-17)**: open_market only. The ABT is open-market residential listings from three online portals (Lamudi, FilipinoHomes, DotProperty). The earlier bank_ropa (bank foreclosures) and floor_price (BDO / Pag-IBIG) tiers were **dropped from the research** — they were never merged into any ABT and are not modeled. Do not reintroduce them into the narrative.
- **CBD nodes**: 8 — CBP, Mandaue, Mactan, SRP, Talisay Tabunok, Consolacion, Naga City, Airport. Grounded in Giuliano & Small (1991) and JICA Mega Cebu Roadmap 2050.
- **Current MCRAI model features**: education, grocery, health, hospitals, recreation, security, tourism, retail_density, plus `mcrai_composite`. Finance is retired; transport is represented by road-distance features, not as an MCRAI category in the deployed models.
- **Target variable**: `price_per_sqm`. `valuation_gap = price_per_sqm − bir_zonal_rr_median` is a derived diagnostic column, not a model feature.
- **Lapu-Lapu**: `is_mactan_island` flag on all Lapu-Lapu City rows. Road network distances inflate on the island — expected behavior, not an error.
- **Current source of truth**: read `thesis_main/reference/eda_workflow_handoff_2026-06-07.md`, `thesis_main/reference/modeling_decisions.md` Decision 42/43, and `thesis_main/Models/stratified/deployment_manifest.json` before making modeling or manuscript claims.

## Collaboration Model
- Claude is the second agent: research design judgment, modeling decisions, literature synthesis, defensibility review, and Codex prompt authoring.
- The hands-on implementer is **OpenAI Codex** (as of 2026-06-08). This replaces the earlier GitHub Copilot, then Antigravity, workflows — do not write prompts targeting Copilot or Antigravity. Codex implements code. Do not write code inline unless the change is trivial (single-line fix or minor edit to an existing snippet), or the user has explicitly asked Claude to do the modeling directly.
- Before writing any Codex implementation prompt, read the target script first. Prompts that don't match the actual file structure produce confused output.
- A good Codex prompt names the target script, describes the exact change, lists expected outputs (columns, row counts, printed summaries), and specifies what must not change.
- Every modeling decision must be logged to `thesis_main/reference/modeling_decisions.md` immediately — with both what was decided and why.
- When the user says "save this" or "note this," write it to the appropriate file in `thesis_main/reference/` or `task.md` — not just in conversation.
- When producing any output the user will clearly copy and paste — Codex prompts, session handoff briefs, scraping prompts, LaTeX snippets, or any block of text meant to be transferred elsewhere — wrap it in a fenced markdown code block (` ```markdown ... ``` ` or the appropriate language fence) so it renders cleanly and can be copied without formatting loss.

## Decision-Making Standards
- Always ground node selection, variable design, and feature inclusion in the literature or defensible research design reasoning — not just statistical correlations or convenience.
- When a decision could be challenged at a panel review, lead with the literature basis, then add the statistical rationale.
- Do not apply OHANA (Project OHANA nationwide equity framework). OHANA was designed for nationwide equity mapping — a different objective from property valuation. The MCRAI custom framework replaces it.
- If a decision involves dropping variables or nodes, require a literature-grounded reason — not just "r=0.99 so we dropped it."
- Placeholder MCRAI weights are temporary. Stage 2 weights will be derived from Stage 1 OLS coefficients — do not treat placeholders as final.

## Methodology Standing Rules
- **Spatial distances**: osmnx network distance (Dijkstra, Haversine fallback) is the standard for all CBD and accessibility computations. Do not revert to Haversine-only.
- **Market segment at prediction time**: `market_segment` is fixed to `open_market` for the deployed Streamlit map. The model estimates open-market residential price levels across Metro Cebu.
- **MCRAI radii**: category-specific (micro: 500–800m, meso: 1–2km, meso-wide: 3km). Do not apply a single global radius across all categories.
- **MCRAI weights**: the current deployed models retain individual MCRAI features plus `mcrai_composite`; do not revive historical finance/transport MCRAI features without logging a new decision.
- **Transport accessibility**: represented by `dist_to_trunk_road_m` and `dist_to_primary_road_m`, not the retired transport-Hansen midpoint feature. Describe accurately in Chapter 3.
- **Current modeling pipeline**: stratified per-sqm models for Condo, Houses, and Vacant Lot. OLS is a diagnostic comparator only. Current deployment is Random Forest per stratum, evaluated with GroupKFold by coordinate cluster.

## EDA and Modeling Standards
- Before model fitting: verify price_per_sqm distributions by market_segment and property_type, feature correlations, and geographic spread across all 6 LGUs.
- Check MCRAI zero rates before model fitting — high zero rates in a single LGU indicate data gaps, not true absence of amenities.
- Log-transform `price_per_sqm` for modeling if skew justifies it; back-transform predictions for the price surface.
- Use MdAPE and PE20 as the plain-language headline performance metrics. Use MAPE, COD, and PRD as supporting diagnostics. Do not claim IAAO compliance for the current models.
- Heteroscedasticity and residual non-normality are handled as OLS diagnostic issues via HC3 robust standard errors; they are not blockers for the deployed Random Forest models.
- Collinearity/VIF matters for OLS interpretation. For the deployed Random Forest models, correlated spatial features may remain if the decision log justifies them.
- SHAP or RF importance outputs are needed for interpretation, but do not let interpretation overwrite the simpler defense narrative.

## Canonical Files
- Decision log: `thesis_main/reference/modeling_decisions.md`
- Task tracker: `thesis_main/Manuscript/task.md`
- Reference notes: `thesis_main/reference/` (5_Questions.md, literature_research_nodes_poi.md)
- Literature: `thesis_main/Literature/` (Polycentric_Urbanism/, CBD_node_selection/, Main-Literatures/)
- Manuscript drafts: `thesis_main/Manuscript/`
- LaTeX + bibliography: `thesis_main/TeX/`

## Writing Priorities
- Prefer review-first behavior over draft-first behavior.
- When reviewing prose, diagnose the section before rewriting it.
- Preserve the author's voice and argument. Do not flatten the prose into generic academic language.
- Avoid making the writing sound overly structured, too polished, or mechanically balanced.
- Keep technical content precise, but allow sentence rhythm and paragraph transitions to feel natural.
- When updating a methodology section, check modeling_decisions.md first to ensure the description matches the implemented decision — not the originally planned one.

## Review Workflow
- For Markdown draft review, prioritize paragraph purpose, flow, repetition, and argument clarity.
- For humanization, flag robotic or templated phrasing and propose minimal revisions.
- For technical review, prioritize defensibility, operational clarity, and overclaim risk.
- For citation review, flag unsupported claims conservatively and never invent evidence.
- Prefer paragraph-level or section-level feedback over full-chapter rewrites.

## Citation And Evidence Rules
- Never invent citations, references, author names, publication years, or empirical findings.
- Never claim a source supports a statement unless the source text or bibliography context clearly supports that claim.
- Separate verified support from likely-but-unverified support when reviewing literature.
- If evidence is missing, explicitly say the claim needs a citation or stronger grounding.
- Gemini Deep Research outputs are starting points, not citable sources. Verify each paper before citing — find the actual DOI or source file.

## Thesis Style Conventions
- Favor clear, direct academic prose over inflated formal wording.
- Avoid repetitive transitions: "moreover," "furthermore," "thus," and similar filler unless genuinely needed.
- Avoid stock AI phrasing: "underscores," "leverages," "highlights," "demonstrates," and similar.
- Do not make every sentence equally dense or equally formal.
- Keep local specificity: Metro Cebu, barangays, CBRT, zonal values, amenity access, and valuation practice should not be generalized away.
- When referring to the custom accessibility index, use the full name "Metro Cebu Residential Accessibility Index (MCRAI)" on first reference, then "MCRAI" thereafter. Do not use "Hansen scores" when referring to MCRAI outputs.

## Technical Writing Conventions
- For methodology, ensure variables, features, assumptions, and procedures are operationally clear.
- Prefer defensible phrasing over ambitious phrasing when discussing model performance or implications.
- Distinguish predictive claims, prescriptive claims, and policy implications carefully.
- Keep terminology consistent across Markdown, LaTeX, and bibliography-backed sections.

## What To Avoid
- Do not perform full rewrites unless explicitly requested.
- Do not convert nuanced paragraphs into bullet-heavy summaries unless the user asks.
- Do not make unsupported methodological defenses on behalf of the thesis.
- Do not prioritize elegance over accuracy in methods, results, or literature sections.
- Do not reintroduce the retired bank_ropa / floor_price tiers into the manuscript or data narrative (Decision 54). The dataset is open_market only.
- Do not save project state (ABT row counts, decision outcomes, task progress) to CLAUDE.md — those belong in `task.md` and memory files.
