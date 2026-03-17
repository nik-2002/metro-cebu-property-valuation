# Project Snapshot: Data-Driven Property Valuation (Cebu City)

**Date**: January 24, 2026
**Author**: Chris Dominic Estreba
**Status**: Chapters 1-3 Refined & LaTeX Conversion Complete

## 1. Project Overview
This project develops a data-driven property valuation model for Cebu City, comparing Hedonic Regression with Machine Learning (Random Forest, XGBoost). It utilizes a hybrid dataset of BDO foreclosures (Floor Price) and online house listings (Ceiling Price).

## 2. Key Accomplishments
- **Manuscript Refinement**:
    - Integrated "Future Factors" (Cebu Bus Rapid Transit stations) as a geospatial feature.
    - Added "Amenity Scores" (counts of schools/hospitals within 1km).
    - Defined "Human-in-the-Loop" validation strategy using real estate brokers.
    - Implemented Log Transformation for price normalization and IQR for outlier detection.
- **LaTeX Conversion**:
    - Created a modular LaTeX project in the `TeX/` directory.
    - Setup `main.tex` with APA-style formatting (using `natbib` for compatibility).
    - Split Chapters 1, 2, and 3 into individual `.tex` files.
    - Managed references via `biblio.bib`.
- **Alternative Formats**:
    - Generated a consolidated Microsoft Word document (`DS_Thesis_Combined.docx`) via Pandoc.

## 3. Directory Structure (Current)
- `Manuscript/`: Contains the Markdown draft, references, and the Word document.
- `TeX/`: Contains the modular LaTeX files and bibliography.
- `Scripts/`: Contains data inspection and processing scripts (e.g., `inspect_excel.py`).

## 4. LaTeX Build Notes
> [!IMPORTANT]
> The build was adjusted to use `natbib` and `apalike` because the `biblatex` package was missing in the local environment. If compiling elsewhere, ensure `natbib` is installed.

## 5. Next Steps
- [ ] Complete data cleaning for the full 955-property dataset.
- [ ] Run the first iteration of the Hedonic Regression vs. Machine Learning models.
- [ ] Generate SHAP value visualizations for "Human-in-the-Loop" validation.
- [ ] Draft Chapter 4 (Results) and Chapter 5 (Conclusion).

---
*This file was generated to preserve conversation context and project state.*
