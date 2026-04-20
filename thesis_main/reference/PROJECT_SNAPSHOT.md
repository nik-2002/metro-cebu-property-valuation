# Project Snapshot: Metro Cebu Residential Valuation Thesis

**Date**: 2026-04-20
**Author**: Chris Dominic Estreba
**Status**: ABT cleaned and enriched; modeling not yet started

## 1. Project Overview
This thesis develops a data-driven residential property valuation workflow for Metro Cebu using a hybrid dataset of listings and bank ROPA inventory. The study is now scoped to 6 LGUs: Cebu City, Mandaue City, Lapu-Lapu City, Talisay City, Minglanilla, and Consolacion. The empirical workflow positions OLS as a benchmark model and Random Forest / XGBoost as the main deployment candidates for QGIS and Streamlit decision-support outputs.

## 2. Current Data Status
- Canonical modeling table: `thesis_main/Data/processed/abt_clean.csv`
- Current ABT shape: 1,110 rows x 50 columns
- Active sources: BDO, Pag-IBIG, Lamudi, BPI, Metrobank, Bank of Commerce, Landbank, China Bank Savings
- Implemented feature families: structural fields, geocoding, 10 CBD/subcenter distances, airport distance, amenity scores, spatial lag, BIR zonal benchmarks, and Hansen gravity accessibility scores

## 3. Recent Accomplishments
- Completed ABT cleanup: 6-LGU filter, property taxonomy standardization, outlier flagging, and legacy-column removal
- Recomputed Hansen gravity scores for 6 amenity categories after replacing transport terminals with OSM road corridor midpoints
- Rebuilt `transport.csv` from Overpass API highway WAY centers: 2,643 unique road segments retained after de-duplication by OSM way ID
- Confirmed updated transport accessibility signal in the ABT:
  - `hansen_transport` mean = 238.48
  - `hansen_composite` mean = 88.10

## 4. Active Modeling Blockers
- Recode `price_type` into a defensible modeling representation, likely with an `is_ropa` flag
- Decide the missing-data strategy for `bedrooms`, `bathrooms`, and `lot_area_sqm`
- Audit the CBD distance variables for redundancy or multicollinearity before model fitting

## 5. Manuscript And Documentation State
- `thesis_main/Manuscript/task.md` is the canonical working task tracker
- Chapters 1 to 3 exist in both Markdown and LaTeX workflows
- The road-accessibility implementation is complete in data, but Chapter 2 and Chapter 3 still need the final write-up and literature support for that feature

## 6. Next Steps
- Finalize `price_type` treatment and freeze the modeling-ready ABT
- Run EDA on the cleaned ABT
- Fit OLS, Random Forest, and XGBoost in sequence
- Export model outputs for QGIS layers and the Streamlit app

---
This file is the current high-level project snapshot and supersedes earlier Cebu City-only framing.
