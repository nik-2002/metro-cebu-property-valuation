# Manuscript Task Snapshot

> Snapshot date: 2026-04-20
> Canonical tracker: `thesis_main/Manuscript/task.md`

## Current Status
- ABT cleanup is complete through Hansen recomputation
- Modeling has not started yet
- The transport accessibility update is implemented in data but still needs final manuscript write-up

## Completed Since The Earlier Snapshot
- Applied the 6-LGU scope filter to the ABT
- Standardized `property_type` across sources
- Flagged bank ROPA outliers
- Dropped legacy null columns and regenerated `valuation_gap`
- Replaced terminal-based `transport.csv` with 2,643 unique OSM road corridor midpoints after de-duplication by OSM way ID
- Re-ran `compute_hansen_scores.py` with the updated transport layer

## Immediate Remaining Blockers
1. Recode `price_type` into a defensible modeling variable
2. Decide missing-data treatment for `bedrooms`, `bathrooms`, and `lot_area_sqm`
3. Audit the CBD distance variables for redundancy before fitting models

## Next Modeling Sequence
1. Freeze the modeling-ready ABT
2. Run EDA
3. Fit OLS as baseline
4. Fit Random Forest and XGBoost
5. Compare model performance and generate SHAP outputs
6. Export prediction layers for QGIS and app integration

## Documentation Follow-up
- Add literature support for road accessibility in Chapter 2 if the feature remains in the final specification
- Add the implemented road-accessibility methodology to Chapter 3
- Keep `thesis_main/Manuscript/task.md` as the source of truth for all future updates
