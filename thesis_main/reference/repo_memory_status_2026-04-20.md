# Repo Status — 2026-04-20

## Confirmed current state
- Canonical ABT: `thesis_main/Data/processed/abt_clean.csv`
- Current ABT shape: 1,110 rows x 50 columns
- Sources: BDO, Pag-IBIG, Lamudi, BPI, Metrobank, Bank of Commerce, Landbank, China Bank Savings
- Completed cleanup steps: 6-LGU scope filter, property-type standardization, bank ROPA outlier flagging, legacy-column removal, Hansen gravity scoring
- Local task snapshot saved in `thesis_main/reference/task_snapshot_2026-04-20.md`

## Transport accessibility update
- `thesis_main/Data/amenities/transport.csv` no longer uses the earlier 69 transport terminal rows
- Transport was rebuilt from OSM highway WAY centers fetched through Overpass API
- Final retained dataset: 2,643 unique road segments after de-duplication by OSM way ID
- `transport.csv` `lgu` labels should be treated as fetch provenance from overlapping LGU bounding boxes, not strict final administrative assignment
- `compute_hansen_scores.py` was re-run successfully on the rebuilt transport dataset

## Current Hansen state
- `hansen_transport`: mean 238.48, std 288.92, zero-score rows 0
- `hansen_composite`: mean 88.10, std 99.93, zero-score rows 0
- Other amenity Hansen columns remain in place and the ABT width stays at 50 columns

## Sanity-check findings to carry forward
- Modeling has not started yet
- OLS remains the benchmark / comparison model
- Random Forest and XGBoost remain the intended deployment candidates for the map and app outputs
- The next modeling blockers are now `price_type`, structural missingness, and CBD-distance redundancy

## Next sequence
1. Recode `price_type` into a defensible modeling representation, likely with `is_ropa`
2. Finalize missing-data treatment for structural variables
3. Audit CBD distance variables for redundancy / multicollinearity
4. Run EDA on the frozen ABT
5. Fit OLS, Random Forest, and XGBoost
6. Export RF / XGBoost predictions for QGIS and Streamlit

## Documentation follow-through still needed
- Chapter 2 needs literature support for the implemented road-accessibility feature
- Chapter 3 needs the final methodology write-up for the corridor-based transport accessibility input
