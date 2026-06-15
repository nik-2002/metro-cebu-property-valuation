# Implementation Plan

## Goal
Bring the LaTeX manuscript into closer alignment with the BSDS Capstone Manuscript Format and Capstone Project Writing Guide by adding prelim pages, scaffolding Chapters 4 to 10, and documenting a compliance audit for Chapters 1 to 3.

## Proposed Changes

### Modify
- `thesis_main/Manuscript/main.tex`
  - Add BSDS-style prelim pages and front matter flow
  - Add lists and abbreviations section
  - Add chapter inputs for Chapters 4 to 10 and appendices
  - Set manuscript margins explicitly to the BSDS guide requirement
- `thesis_main/Manuscript/task.md`
  - Record this compliance pass and remaining manuscript work

### Create
- `thesis_main/Manuscript/title_page.tex`
- `thesis_main/Manuscript/approval_sheet.tex`
- `thesis_main/Manuscript/dedication.tex`
- `thesis_main/Manuscript/abstract.tex`
- `thesis_main/Manuscript/acknowledgment.tex`
- `thesis_main/Manuscript/maps_list.tex`
- `thesis_main/Manuscript/pictures_list.tex`
- `thesis_main/Manuscript/appendices_list.tex`
- `thesis_main/Manuscript/abbreviations.tex`
- `thesis_main/Manuscript/chapter4.tex`
- `thesis_main/Manuscript/chapter5.tex`
- `thesis_main/Manuscript/chapter6.tex`
- `thesis_main/Manuscript/chapter7.tex`
- `thesis_main/Manuscript/chapter8.tex`
- `thesis_main/Manuscript/chapter9.tex`
- `thesis_main/Manuscript/chapter10.tex`
- `thesis_main/Manuscript/appendices.tex`
- `thesis_main/Manuscript/chapters_1_3_compliance_audit.md`

## Verification Plan
- Build the manuscript from `thesis_main/Manuscript` using `latexmk -pdf -interaction=nonstopmode main.tex`
- Confirm prelim pages, chapter scaffold, and references compile from the new structure
- Review the audit file for chapter-specific compliance findings
