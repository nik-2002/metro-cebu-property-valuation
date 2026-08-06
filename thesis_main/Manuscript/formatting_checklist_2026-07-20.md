# Formatting checklist — Ms. Kim's printing-phase comments (2026-07-20)

Source of truth: this worktree (`dev/manuscript`), which is byte-identical to the
Prism-bundle PDF Ms. Kim reviewed. Number→page map taken from the July 14 build
(`main.lot` / `main.lof`). Callout/bold/spacing states below are from a scripted
audit of the source.

Decisions locked with Nico:
- **Chapter labels:** re-add "Chapter N" to titles + fix Contents.
- **Printing:** black & white → recolor boxplot medians (Fig 3, Fig 5).
- Do plan first (this file), then execute.

Legend: `[ ]` todo · `[~]` needs author judgment · file:line references are current.

---

## A. Global / document-wide (`main.tex`)

- [ ] **A1 — Letter page setup.** Documentclass already `letterpaper`; pin it in
  `\geometry{...}` (`papersize`/`letterpaper`) and verify output page = 8.5×11 in
  after compile. *(Ms. Kim: "Page set-up should be letter")*
- [ ] **A2 — Remove running headers.** apa7 `man` mode prints a running head from
  `\shorttitle`. Suppress it (e.g. `\pagestyle{plain}` / apa7 running-head off, keep
  page numbers). *(Ms. Kim: "Should not have running headers")*
- [ ] **A3 — Unbold headings → fixes Contents + heading-level confusion.** All
  headings are written `\section{\texorpdfstring{\textbf{X}}{X}}`. The manual
  `\textbf` (a) leaks into the TOC (bold sub-headers) and (b) flattens Level-2 vs
  Level-3 so they look identical (the p.33 issue). Strip the `\texorpdfstring{\textbf{}}`
  wrapper globally; apa7 then bolds body headings itself (L1 centered-bold,
  L2 flush-bold, L3 flush-bold-italic). *Covers: Contents sub-headers, and p.33.*
- [ ] **A4 — Re-add "Chapter N" to titles.** Add `Chapter 1 … Chapter 10` to the ten
  chapter `\section` titles; confirm Contents reflects it. In-text "Chapter X"
  references then stay valid as-is.
- [ ] **A5 — Float placement policy.** Several "callout should appear before" items are
  float drift (ref exists but figure floated above it). Tighten placement
  (`[t]`/`[!t]`, `\FloatBarrier` where needed) so floats never precede their callout.

---

## B. Front matter

- [ ] **B1 — Approval sheet: remove all bold + center the names.**
  `approval_sheet.tex`. Body paragraph already unbolded; still bold: the four names
  (`\textbf{Ms. Kimberly…}`, `\textbf{Mr. Randy…}`, `\textbf{Ms. Kimberly…}`,
  `\textbf{Mr. Elmer…}`) and they are `\noindent` left-aligned. Remove `\textbf`,
  center-align each name block. *(Ms. Kim: "No bold font in the paragraph"; "Names
  … should be center aligned")*
- [ ] **B2 — Contents: sub-headers not bold.** Resolved by **A3** (verify in PDF).
- [ ] **B3 — List of Figures / Tables / Appendices not bold.** `.lot`/`.lof` table
  entries carry no `\textbf` in source; verify they render non-bold in the PDF and
  strip any bold that appears (incl. `appendices_list.tex`). *(Ms. Kim)*

---

## C. Tables — callouts / spacing / bold row headers / notes

Audit result per table (callout = a `\ref` exists before it in source):

| # | file | callout | bold row hdr | Ms. Kim's ask |
|---|------|---------|--------------|----------------|
| 1 | chapter1 | NO | – | add callout before it |
| 2 | chapter2 | NO | **bold** | add callout; add space before; unbold row header |
| 3 | chapter3 | yes | – | — (she noted it *has* callout) |
| 4 | chapter3 | yes | **bold** | extra space before; unbold row header |
| 5 | chapter3 | NO | **bold** | add callout; fix "too many spaces" before; unbold row header |
| 6 | chapter3 | NO | – | callout before; add a space before |
| 7 | chapter3 | NO | **bold** | callout; "too many spaces"→put at top of page; unbold row hdr; add space after table |
| 8 | chapter3 | NO | **bold** | add callout; unbold row header |
| 9 | chapter3 | NO | – | add callout |
| 11 | chapter4 | NO | – | add callout; **font too small** (enlarge body) |
| 12 | chapter4 | yes | – | note missing "Note." (uses `\footnotesize{}`) |
| 13 | chapter4 | NO | – | add callout; put at top of page (solo → APA flush-left top) |
| 14 | chapter4 | NO | – | add callout; **text too small** (enlarge) |
| 15 | chapter5 | yes | – | [~] note too long — incorporate into text? |
| 16 | chapter5 | yes | – | add space before |
| 17 | chapter6 | NO | – | add callout; add space before |
| 18 | chapter6 | yes | – | note missing "Note." |
| 19 | chapter6 | NO | – | add callout; add space before |
| 20 | chapter7 | yes | **bold** | add space before; note missing "Note."; (unbold row hdr) |
| 21 | chapter7 | yes | **bold** | add space before; note missing "Note."; (unbold row hdr) |
| 22 | chapter7 | NO | – | add callout **before**; add space before; note missing "Note." |
| 23 | appendices | NO | – | add callout (see D-note) |
| 24 | appendices | NO | **bold** | add callout; unbold row header |

Planned fixes:
- [ ] **C1 — Missing callouts.** Add a sentence referencing the table *before* it
  appears (Tables 1, 2, 5, 6, 7, 8, 9, 11, 13, 14, 17, 19, 22 + appendix 23, 24).
- [ ] **C2 — Unbold row/column headers.** Tables 2, 4, 5, 7, 8, 20, 21, 24 — remove
  `\textbf` from the header row.
- [ ] **C3 — Add space before.** Tables 2, 16, 17, 19, 20, 21, 22 (`\vspace` /
  blank line before float). Tables 5, 7, 29-region: "too many spaces" → reduce /
  anchor at top of page.
- [ ] **C4 — Note "Note." label.** Tables 12, 18, 20, 21, 22 use `\footnotesize{...}`
  which prints no label. Add proper "Note." (define `\tablenote` or prepend
  `\textit{Note.} `). *(Also audit all other `\footnotesize{}` table notes.)*
- [ ] **C5 — Table body font too small.** Tables 11 and 14 — enlarge (drop
  `\footnotesize`/`\small` on the tabular, or widen columns / rotate).
- [ ] **C6 — Table 7 on p.34.** Put at top of page; continue text after with a
  space below the table.
- [ ] **C7 — Table 13 solo-on-page.** APA 7: solo float → top of page, flush-left.
- [~] **C8 — Table 15 long note.** Decide: shorten, or move into body text.

---

## D. Figures — callouts / ordering / notes / B&W

| # | file | callout | Ms. Kim's ask |
|---|------|---------|----------------|
| 2 | chapter3 | yes | callout should appear **before** figure (float drift → A5) |
| 3 | chapter4 | NO | add callout; **B&W: recolor boxplot median** |
| 4 | chapter4 | yes | callout should appear **before** figure (float drift → A5) |
| 5 | chapter4 | NO | add callout; **B&W: recolor boxplot median** (see Fig 3) |
| 6 | chapter4 | yes | [~] note seems unnecessary — remove? |
| 7 | chapter4 | NO | add callout |
| 9 | chapter7 | yes | — |
| 10 | chapter7 | NO | add callout; [~] clarify "Deployed House Random Forest" — move explanation to text |
| 11 | chapter7 | NO | add callout; [~] clarify "vacant lot" note — move to text |

- [ ] **D1 — Missing figure callouts.** Figures 3, 5, 7, 10, 11 (+ appendix figs, see E).
- [ ] **D2 — Callout-before ordering.** Figures 2, 4 (via A5 float placement).
- [ ] **D3 — B&W boxplot medians.** Recolor the median line in Fig 3 and Fig 5 to a
  dark/high-contrast tone (regenerate the plot PNGs → update `diagrams/`).
- [~] **D4 — Figure 6 note.** Remove if unnecessary (author call).
- [~] **D5 — Figures 10 & 11 notes.** Clarify or move the "Deployed … Random Forest"
  explanation into the introducing text.

---

## E. Appendices A–F (`appendices.tex`, `feature_snapshots.tex`)

Audit: appendix tables 23, 24, 25, 26, 27, 28 and figures 12–27 — **none** carry a
callout except Figs 12, 25, 27.

- [ ] **E1 — Callouts for appendix tables/figures.** Reference each in the main body
  (or in the appendix intro text) before it appears — Tables 23, 24, 25, 26–28;
  Figures 13–24, 26. *(Ms. Kim: even in the appendix, callouts are expected.)*
- [~] **E2 — Appendix B.** Same callout treatment as Tables 23/24.
- [~] **E3 — Appendix C.** One table under "Supplemental Tables" title; note too long
  → move to intro text + add callout.
- [~] **E4 — Appendix D.** No callouts for all figures; notes don't clearly explain
  contents → move explanation into text + add callouts.
- [ ] **E5 — Appendix E wording.** Replace "the tables below" with explicit table
  numbers (they aren't physically below). *(Ms. Kim 😊)*
- [~] **E6 — Appendix F.** Same callout treatment; review whether notes are necessary.

---

## F. Specific page issues

- [ ] **F1 — p.9→p.10 gap.** Big whitespace end of p.9 / top of p.10 (around Table 1).
  Fix via float placement / text flow. *(Depends on A5 + C1 for Table 1.)*
- [~] **F2 — p.22 "(alone)" small font.** A `\footnotesize{}` table note whose scope
  leaks onto the following word "alone." Fix grouping so body text returns to normal
  size. *(Locate the table note on p.22 during execution.)*
- [ ] **F3 — p.29 Table 5.** Too many spaces before it + no callout → covered by C1/C3.
- [ ] **F4 — p.33 heading levels.** Pre-processing (L2) / Modeling Strategy (L2) /
  Stratified Models (L3). Confirm intended hierarchy; visual distinction restored by
  **A3** (L2 bold vs L3 bold-italic).

---

## Judgment calls to confirm with Nico before/after drafting (the `[~]` items)
1. Table 15 note — shorten vs move to text (C8).
2. Figure 6 note — remove vs keep (D4).
3. Figures 10/11 notes — reword vs move to text (D5).
4. Appendix C/D/F notes — move into text (E3/E4/E6).

## STATUS — executed 2026-07-21 (build: 140 pp, 0 undefined refs, letter)

DONE (mechanical):
- A1 letter (verified 612×792pt) · A2 running head removed (page nos kept, top-right)
  · A3 headings unbolded (fixes Contents + p.33 levels: L2 bold vs L3 bold-italic)
  · A4 "Chapter N" added to all 10 titles + Contents · A5 float placement.
- B1 approval sheet: all bold removed (incl. body), names centered · B2/B3 verified
  (TOC sub-headers + LOF/LOT entries not bold).
- C1 callouts added for Tables 1,2,5,6,7,8,9,11,13,14,17,19,22,23,24 · C2 stub bold
  removed (Tables 4,5,7,8,24) · C3/C6/C7 spacing — solved structurally by converting
  body floats to `[H]` (see note) · C4 "Note." now on Tables 12,18,20,21,22 · C5
  Tables 11 & 14 enlarged (scriptsize→footnotesize).
- D1 figure callouts (Figs 3,5,7,10,11) · D2 Figs 2 & 4 callout-before (fixed by `[H]`)
  · D3 boxplot medians recolored solid black (Figs 3 & 5 regenerated).
- E1 appendix callouts (Tables 23,24,25,26–28; Figs 13–24,26) · E5 "tables below"→numbers.
- F1 p.9/10 gap resolved · F2 verified non-issue (Table 3 note already normal size)
  · F3 Table 5 spacing fixed · F4 p.33 heading levels fixed.

KEY DECISION — body floats `[htbp]/[tbp]` → `[H]`: the `\floatplacement{...}{tbp}`
overrides in main.tex were defeating apa7 `floatsintext`, scattering floats to their
own pages and above their callouts (root cause of most spacing/ordering comments).
Converting body floats to `[H]` (matching the appendices) places each float in-line
right after its callout. Cost: +6 pages (134→140). Verified on Tables 1,5,18; Figs 2,4.

STILL OPEN — judgment calls (need Nico) + discovered issues:
- [~] C8 Table 15 long note · D4 Fig 6 note (remove?) · D5 Figs 10/11 note wording
  · E3 Appendix C long note · E4 Appendix D note clarity · E6 Appendix F notes.
- DISCOVERED (not in Kim's list): 3 `Section~\ref{}` to unnumbered apa7 headings render
  as empty "(Section )" — chapter3:210, chapter7:75 & 110. Fix by naming the section.
- biber could not run locally (arm64 lipo error); reused existing main.bbl (citations
  unchanged). A final build on Nico's machine should run biber once to be safe.

## Execution order (proposed)
1. Global: A1 A2 A3 A4 A5 (compile, eyeball).
2. Front matter: B1–B3.
3. Callouts + spacing + row-header bold + note labels: C1–C7, D1–D2, E1/E5.
4. B&W figure recolor: D3.
5. Judgment items once confirmed: C8, D4, D5, E3, E4, E6.
6. Full compile ×3 + biber, verify page count / 0 undefined refs, spot-check the
   specific pages (9–10, 22, 29, 33), commit to `dev/manuscript`.
