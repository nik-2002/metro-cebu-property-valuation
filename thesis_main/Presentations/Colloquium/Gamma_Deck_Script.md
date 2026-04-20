# Gamma Deck Script

Deck style:
- Academic and data-driven
- Clean, minimal, map-centric visuals
- Emphasize Metro Cebu, GIS, and progress since proposal
- Avoid sounding like a second proposal defense

---

Metro Cebu Property Valuation Thesis
- Colloquium progress update on the current state of the thesis
- Focus: what has been accomplished since proposal, what improved in the methodology, and what remains to be done
- Core direction: from approved concept toward a working GIS-supported valuation pipeline

---

Study Recap and Approved Direction
- The thesis aims to estimate residential property values in Metro Cebu using structural, administrative, and geospatial value drivers
- The approved direction combined hybrid pricing data, Hedonic OLS, Random Forest, and XGBoost, together with GIS augmentation
- The intended output is both a valuation model and a QGIS-based spatial decision-support tool

---

Progress Overview Since Proposal
- Expanded floor-price acquisition beyond the earlier source base
- Geocoded the current listing batches and started plotting property layers in QGIS
- Extracted BIR zonal values, started building the consolidated analytic base table, and began amenity mapping

---

Data Acquisition and Geocoding Progress
- Pag-IBIG acquired-asset data was added to strengthen the floor-price side of the dataset
- The current cleaned Pag-IBIG file contains 108 Cebu records, with 96 records falling within the Metro Cebu LGUs in scope
- The current listing geocoding batches contain 5,233 records, with 5,198 already carrying usable coordinates, or about 99.3% completion

---

BIR Extraction and ABT Build
- A dedicated extraction workflow was built to convert messy BIR zonal schedules into machine-readable tables
- The current consolidated BIR extract contains 67,072 structured rows covering 4 cities and 65 barangays
- The current major task is assembling the analytic base table from floor prices, listings, zonal values, and geocoded locations

---

QGIS Exploration and Spatial Validation
- Property layers are already being explored in QGIS to validate spatial coverage and support map-based outputs
- The current IT Park amenity test layer already contains 310 mapped OSM amenity features
- QGIS is now serving both as a validation environment and as the foundation for the final decision-support output

---

Methodology Refinements Since Proposal
- The floor-price strategy became more robust by moving toward a more diversified institutional dataset, beginning with Pag-IBIG and other verified acquired-asset sources
- Location is now operationalized more rigorously through geocoding, distance-based features, and spatial context variables
- The amenity component became more defensible through Project OHANA and related literature, shifting the framing from simple counts toward accessibility-based scoring
- The thesis is now framed more clearly as a QGIS-based spatial decision-support tool, not only as a predictive pricing model

---

Current Remaining Work
- Finalize the consolidated analytic base table and resolve remaining source-level standardization issues
- Compute the full feature set, including proximity variables, amenity or accessibility variables, spatial lag, and zonal alignment
- Run and compare the first full OLS, Random Forest, and XGBoost model iterations

---

Immediate Next Steps and Timeline
- March 29 to early April: complete ABT assembly and finalize geospatial feature engineering
- April 1 to April 18: model training, SHAP analysis, and QGIS output refinement
- April 18 to May 2: final paper drafting and revisions, with final presentation on May 9 and submission on May 23

---

Closing and Q&A
- Since the proposal, the strongest progress has been in data acquisition, geocoding, BIR extraction, and GIS integration
- The thesis is no longer only a concept; it now has an active spatial data foundation and a clear implementation path
- The next milestone is to convert that foundation into the first full valuation results and final map-based outputs