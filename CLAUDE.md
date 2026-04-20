# Thesis Workspace Guidelines

## Project Focus
- This workspace is for a technical thesis on residential real estate valuation in Metro Cebu using data science and geospatial features.
- Treat the author as the primary writer. AI should support planning, critique, consistency checks, and targeted revision, not replace authorship.
- Preserve the thesis as a locally grounded research project. Keep Metro Cebu, valuation practice, geospatial features, and decision support central to the writing.

## Writing Priorities
- Prefer review-first behavior over draft-first behavior.
- When reviewing prose, diagnose the section before rewriting it.
- Preserve the author's voice and argument. Do not flatten the prose into generic academic language.
- Avoid making the writing sound overly structured, too polished, or mechanically balanced.
- Keep technical content precise, but allow sentence rhythm and paragraph transitions to feel natural.

## Review Workflow
- For Markdown draft review, prioritize paragraph purpose, flow, repetition, and argument clarity.
- For humanization, flag robotic or templated phrasing and propose minimal revisions.
- For technical review, prioritize defensibility, operational clarity, and overclaim risk.
- For citation review, flag unsupported claims conservatively and never invent evidence.
- Prefer paragraph-level or section-level feedback over full-chapter rewrites.

## Citation And Evidence Rules
- Never invent citations, references, author names, publication years, or empirical findings.
- Never claim a source supports a statement unless the source text or bibliography context clearly supports that claim.
- When asked to review literature or claims, separate verified support from likely-but-unverified support.
- If evidence is missing, explicitly say the claim needs a citation or stronger grounding.

## Thesis Style Conventions
- Favor clear, direct academic prose over inflated formal wording.
- Avoid repetitive transitions such as "moreover," "furthermore," "thus," and similar filler unless genuinely needed.
- Avoid overusing abstract verbs like "underscores," "leverages," "highlights," and similar stock AI phrasing.
- Keep local specificity when relevant: Metro Cebu, barangays, CBRT, zonal values, amenity access, geospatial context, and valuation practice should not be generalized away.
- Do not make every sentence equally dense or equally formal.

## Technical Writing Conventions
- For methodology, ensure variables, features, assumptions, and procedures are operationally clear.
- Prefer defensible phrasing over ambitious phrasing when discussing model performance or implications.
- Distinguish predictive claims, prescriptive claims, and policy implications carefully.
- Keep terminology consistent across Markdown, LaTeX, and bibliography-backed sections.

## Workspace Conventions
- Main manuscript drafts are under `thesis_main/Manuscript/`.
- LaTeX chapters and bibliography are under `thesis_main/TeX/`.
- Review-oriented custom agents are under `.claude/agents/`.
- When editing prose, prefer the smallest targeted changes that improve clarity or rigor.
- When a review task involves citations or terminology consistency, check related files in both the manuscript and bibliography when practical.

## Code Delegation
- For all coding and scripting tasks (Python scripts, data pipelines, QGIS automation, LaTeX generation, etc.), delegate implementation to a Claude Haiku subagent using `model: "Claude Haiku (copilot)"`.
- Claude Sonnet acts as manager: planning, reviewing output, making judgment calls, and integrating results.
- Only handle code inline if the change is trivial (single-line fix, minor edit to an existing snippet).

## What To Avoid
- Do not perform full rewrites unless explicitly requested.
- Do not convert nuanced paragraphs into bullet-heavy summaries unless the user asks.
- Do not make unsupported methodological defenses on behalf of the thesis.
- Do not prioritize elegance over accuracy in methods, results, or literature sections.