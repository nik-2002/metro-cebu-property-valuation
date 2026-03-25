# Thesis Review Agents

These custom agents are designed for the thesis-writing workflow in this workspace.

## Available Agents
- `Markdown Thesis Review`: first-pass editorial review after drafting in Markdown.
- `Human Narrative Pass`: removes robotic phrasing and restores a more natural academic voice.
- `Technical Integrity Pass`: checks whether technical claims and methods are defensible.
- `Citation and Claim Scan`: flags unsupported claims, citation gaps, and terminology drift.

## Recommended Order
1. Run `Markdown Thesis Review` after you finish a draft section.
2. Run `Technical Integrity Pass` on methodology-heavy or results-heavy sections.
3. Run `Citation and Claim Scan` before advisor review or LaTeX sync.
4. Run `Human Narrative Pass` last so the section sounds human without losing rigor.

## Suggested Targets
- `thesis_main/Manuscript/Full_Thesis_Draft.md`
- chapter-specific files under `thesis_main/Manuscript/`
- LaTeX chapters under `thesis_main/TeX/`
- bibliography files such as `thesis_main/TeX/biblio.bib`

## Notes
- These agents are review-oriented by design. They do not default to full rewrites.
- Keep reviews paragraph-scoped when possible to preserve your voice.
- For the best results, ask each agent to review a specific section with a clear objective.