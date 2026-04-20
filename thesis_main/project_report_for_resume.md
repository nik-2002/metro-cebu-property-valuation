# Residential Real Estate Valuation — Metro Cebu (Thesis)

**Short summary:** End-to-end data and modeling project to estimate residential property values in Metro Cebu using a hybrid dataset (institutional foreclosures + online listings) and GIS-derived locational features. Designed and implemented the data pipeline, engineered geospatial features, and benchmarked interpretable and high-performance models (Hedonic OLS, Random Forest, XGBoost).

**Role / Contributions:**
- **Lead implementer:** Designed the ingestion, cleaning, geocoding, GIS-augmentation, modeling, and explainability pipeline.
- **Data engineering:** Built parsers and cleaning steps to turn raw BDO Excel and scraped listings into analysis-ready rows.
- **Feature engineering:** Created proximity, amenity, and spatial-lag features from geocoded coordinates.
- **Modeling & validation:** Implemented and tuned OLS, Random Forest, and XGBoost; used cross-validation and SHAP for explainability.
- **Deliverables:** Cleaned dataset(s), geocoded outputs, QGIS layers, model artifacts, and explainability charts for stakeholder review.

**Key data & pipeline specifics**
- Primary raw data: BDO foreclosure file (raw entries: 955) — filtered to Metro Cebu.
- Secondary data: Target 500+ market listings (Lamudi / public portals) to represent market "ceiling" prices.
- Administrative controls: BIR zonal values (barangay-level) and BSP RPPI for time trend adjustments.
- Main scripts:
  - `thesis_main/Scripts/data_pipeline.py` — ingestion, CSV export to `Data/processed_properties_cebu.csv`, regex parsing for `Bedrooms`/`Bathrooms`, numeric casting and Cebu filtering.
  - `thesis_main/Scripts/Geocoding/geocode_properties.py` — batch geocoding via Google Maps API with checkpointing (checkpoint frequency = 50), outputs geocoded CSV(s) used for mapping.
  - QGIS automation: `thesis_main/Scripts/Geocoding/setup_qgis_layers.py` to register CSV layers in the project.
- Processed dataset saved at: `Data/processed_properties_cebu.csv` (canonical cleaned file).

**Feature engineering (concrete features created)**
- Structural: `LotArea`, `FloorArea`, `Bedrooms`, `Bathrooms`, `PropertyType`.
- Locational & geospatial:
  - Haversine distances: `Dist_CBD`, `Dist_Airport`, `Dist_CBRT` (meters).
  - Amenity index: `OSM_Amenity_Score` computed from OpenStreetMap via `osmnx` (counts within 1 km, weighted by category: healthcare > transport > education > commerce).
  - Spatial lag: mean price of neighboring properties within 1 km (captures neighborhood spillovers).
- Administrative / derived: `BIR_Zonal_Value`, `Valuation_Gap` = Price − ZonalValue, `Price_per_sqm`, `Log_Price` (model target).

**Preprocessing choices**
- Outlier handling: IQR-based filtering for extreme anomalies.
- Missing values: Barangay-level median imputation for area fields.
- Target transform: natural log of Price to stabilize right skew.
- Encoding: One-hot for categorical fields (PropertyType, Barangay) where needed for models.

**Modeling details (exact, reproducible choices)**
- Models compared:
  - Hedonic baseline: OLS / log-linear regression for interpretability.
  - Random Forest Regressor (scikit-learn) — captures non-linearities and interactions.
  - XGBoost Regressor — gradient boosting for best predictive performance.
- Target: `Log_Price` (natural log of Price); reporting back-transformed MAE/RMSE where useful.
- Cross-validation: K-Fold CV (K = 5 or 10 depending on final sample size) for robust generalization estimates.
- Hyperparameter tuning: GridSearchCV (example grids used):
  - Random Forest: `n_estimators` ∈ {100, 200, 500}, `max_depth` ∈ {10, 20, None}, `max_features` ∈ {"sqrt", "log2"}.
  - XGBoost: `learning_rate` ∈ {0.01, 0.05, 0.1}, `n_estimators` ∈ {100, 300, 500}, `max_depth` ∈ {3, 6, 10}, `subsample` ∈ {0.6, 0.8, 1.0}.
- Evaluation metrics: **MAE**, **RMSE**, and **R²** (report both log-space and back-transformed errors). Thesis target: R² > 0.80 (benchmark/goal used in evaluation).
- Explainability: SHAP (Shapley) for global and local feature attribution; partial dependence plots for key non-linear effects.

**Validation & stakeholder review**
- Human-in-the-loop: Licensed CPRE brokers reviewed SHAP-based rankings and outliers (sanity checks and domain validation).
- Error analysis: Cases with high absolute errors reviewed for data-quality issues vs. genuine market anomalies.

**Software & environment**
- Stack: Python 3.x, Pandas, Scikit-learn, XGBoost, osmnx (OSM), googlemaps, SHAP, QGIS (for visualization), Streamlit (planned dashboard).
- Reproducibility: `requirements.txt` present in repo; main scripts and processed CSVs are under `thesis_main/Scripts` and `thesis_main/Data` respectively.

**Project artifacts (where to find them)**
- Canonical pipeline: `thesis_main/Scripts/data_pipeline.py` (ingest → clean → `Data/processed_properties_cebu.csv`).
- Geocoding: `thesis_main/Scripts/Geocoding/geocode_properties.py` (checkpointing, outputs used by QGIS).
- GIS project and outputs: `thesis_main/QGIS/Metro_Cebu_Valuation.qgz` and `thesis_main/Scripts/Geocoding/*geocoded*.csv`.
- Method writeup: `thesis_main/Manuscript/Thesis_chapter3.md` and `thesis_main/TeX/chapter3.tex` (detailed method and evaluation plan).

**Short resume-ready bullets (pick 1–2 for CV)**
- Built an end-to-end valuation pipeline for Metro Cebu: ingested institutional foreclosure data (955 entries) and scraped market listings, geocoded addresses via Google Maps API, engineered GIS-derived features (proximity, amenity scores, spatial lag), and produced a cleaned dataset for modeling (`Data/processed_properties_cebu.csv`).
- Trained and benchmarked OLS, Random Forest, and XGBoost regressors with GridSearchCV and K-Fold CV (MAE/RMSE/R²), using SHAP for model explainability to support professional appraisal review.

**Next steps (optional enhancements)**
- Add text embeddings from listing descriptions (Word2Vec/BERT) to boost predictive power.
- Incorporate satellite-derived building footprints to improve structural feature coverage.
- Build a Streamlit dashboard to allow brokers to query predicted values and view SHAP explanations interactively.

---

If you want, I can (a) convert this to 1–2 resume bullets tailored for specific roles, (b) produce a short LinkedIn summary, or (c) add exact GridSearchCV code snippets and the final model evaluation table to this file.