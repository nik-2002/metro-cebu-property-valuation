# **Chapter 3 | Research Methodology**

## **3.1 Research Design**

This study employs a **quantitative, non-experimental design** focused on predictive and prescriptive analytics. Specifically, we use a supervised learning approach to estimate residential property values in Metro Cebu and visualize the results through an interactive GIS platform for prescriptive decision support. The dependent variable is the property price (or price per square meter), and the independent variables encompass structural features, geospatial value drivers, administrative benchmarks, and macroeconomic indicators.

The study compares three supervised learning models to quantify the trade-off between interpretability and predictive accuracy, while testing the incremental value of GIS-derived features and administrative data:

1. **Ordinary Least Squares (OLS) / Hedonic Regression**: An interpretable baseline grounded in Hedonic Pricing Theory (Rosen, 1974). Coefficients carry direct economic meaning (e.g., "each additional bedroom adds ₱X to value").
2. **Random Forest Regressor**: A tree-based ensemble that captures non-linear relationships and feature interactions without requiring explicit specification (Breiman, 2001).
3. **XGBoost Regressor**: A gradient boosting algorithm optimized for predictive accuracy on structured tabular data (Chen & Guestrin, 2016). Empirically proven to be the best-performing model for datasets of ~1,000 observations (Nyanda et al., 2024).

This three-model comparison allows us to quantify the trade-off between interpretability (hedonic) and predictive accuracy (ML), while explicitly testing the incremental value of GIS-derived geospatial features and administrative data (BIR Zonal Values).

---

## **3.2 Data Sources: The Hybrid Strategy**

To overcome the data scarcity challenge identified in the literature (Cheloti & Mooya, 2021), we aggregate multiple data sources into a hybrid dataset. Since actual Deed of Sale transaction data is private and inaccessible, we bracket the "True Market Value" between a conservative floor and a speculative ceiling.

| Source                       | Role                      | Volume                     | Nature                    |
| ---------------------------- | ------------------------- | -------------------------- | ------------------------- |
| **Bank Foreclosures**        | Verified Floor Price      | BDO, PNB, RCBC, Union Bank | Conservative / Distressed |
| **Pag-IBIG / Gov't Assets**  | Verified Floor Price      | HDMF acquired assets       | Conservative / Distressed |
| **Online Listings** (Lamudi) | Market Ceiling Price      | Target: 500+               | Asking / Speculative      |
| **BIR Zonal Values**         | Administrative Benchmark  | Per barangay               | Static / Regulatory       |
| **BSP RPPI**                 | Time-Trend Control        | Quarterly index            | Macro / Cyclical          |
| **Google Maps API**          | Geocoding / Location Data | Per property               | Geospatial / Dynamic      |
| **OpenStreetMap (OSM)**      | Amenity & Land-Use Data   | Per property radius        | Geospatial / Open Data    |

### **3.2.1 Primary Data: Verified Floor Price (Foreclosed / Acquired Assets)**

The floor price dataset aggregates foreclosed and acquired property listings from multiple institutional sources to prevent single-source bias:

- **BDO Unibank**: 955 raw foreclosure entries nationwide (as of November 18, 2025).
- **Pag-IBIG Fund (HDMF)**: Acquired assets representing the affordable housing segment.
- **PNB, RCBC, and Union Bank**: Additional listings to broaden coverage.
- **SSS / GSIS**: Government-acquired properties within Metro Cebu.

These distressed assets, priced below standard market rates to ensure liquidity, serve as the conservative price floor. Aggregating across multiple institutions mitigates pricing strategy bias.

**Sample Data Structure: BDO Foreclosures (Raw vs. Cleaned)**

| Raw Column (BDO Excel) | Processed Feature | Description |
| :--- | :--- | :--- |
| `REGION` | `Region` | Filtered to Region VII |
| `CITY_PROVINCE` | `City` | Filtered to Metro Cebu LGUs |
| `PROPERTY_ADDRESS` | `Address` | Geocoded string |
| `LOT_AREA` | `Lot Area` | Numeric (sqm) |
| `FLOOR_AREA` | `Floor Area` | Numeric (sqm) |
| `MINIMUM_BID_PRICE` | `Actual Price` | Numeric target variable (₱) |
| `PROPERTY_DESCRIPTION` | `Bedrooms`, `Bathrooms` | Parsed via regex |

### **3.2.2 Secondary Data: Market Ceiling Price (Online Listings)**

To denote "fair market" asking prices, we collect current residential listings from public online platforms, primarily Lamudi. As validated by Sousa et al. (2024), aggregating thousands of online listings captures pricing clusters often missed by sparse official records. We target 500+ Metro Cebu residential listings.

**Sample Data Structure: Lamudi Listings (Raw vs. Cleaned)**

| Raw Field (Web Scrape) | Processed Feature | Description |
| :--- | :--- | :--- |
| `Location` | `Barangay`, `City` | Parsed location string |
| `Price` | `Actual Price` | Target variable (₱), cleaned of currency symbols |
| `Bedrooms` | `Bedrooms` | Numeric extract |
| `Bathrooms` | `Bathrooms` | Numeric extract |
| `Floor area` | `Floor Area` | Numeric extract (sqm) |
| `Land Size` | `Lot Area` | Numeric extract (sqm) |
| `Latitude` / `Longitude` | `Latitude`, `Longitude` | Direct coordinate mapping |

### **3.2.3 Administrative and Macroeconomic Data**

- **BIR Zonal Values**: Official zonal values per barangay, used both as a model feature and to calculate the "Valuation Gap" (Market Price − Zonal Value).
- **BSP RPPI**: Quarterly Residential Real Estate Price Index for Areas Outside NCR (AONCR), controlling for time-trend effects (inflation/market cycle).

### **3.2.4 Geospatial Data Sources**

- **Google Maps Geocoding API**: Converts property addresses into precise latitude/longitude coordinates, enabling all subsequent spatial analyses. Chosen for its superior address disambiguation in Philippine contexts.
- **OpenStreetMap (OSM)**: Provides open geospatial data for amenity density analysis. Queried via the `osmnx` Python library (Boeing, 2017) to retrieve counts of schools, hospitals, commercial establishments, restaurants, and public transport stops within defined radii of each property.

### **3.2.5 Target Variable**

Given this hybrid strategy, BDO foreclosure prices serve as the floor, and Lamudi listings serve as the ceiling. We include a source indicator variable in the model to account for systematic price-level differences between distressed and market listings. This allows the model to learn the structural relationship between property attributes and price across both market segments.

**Final Feature Matrix Schema (Pre-Modeling)**

| Feature Group | Variables | Type |
| :--- | :--- | :--- |
| **Identifiers** | `ID`, `Source` (BDO/Lamudi) | Categorical |
| **Structural** | `Lot Area`, `Floor Area`, `Bedrooms`, `Bathrooms`, `Property Type` | Numeric / Categorical |
| **Locational** | `Latitude`, `Longitude`, `Barangay` | Numeric / Categorical |
| **Geospatial** | `Dist_CBD`, `Dist_Airport`, `Dist_CBRT` | Numeric (Meters) |
| **Amenity** | `OSM_Amenity_Score` | Numeric (Count/Index) |
| **Economic** | `BIR_Zonal_Value`, `Spatial_Lag_Mean` | Numeric (₱) |
| **Target** | `Actual Price`, `Log_Price` | Numeric (₱) |

### **3.2.6 Validation Layer: Human-in-the-Loop**

To comply with IVS 2025 (IVS 105) and ground the computational model in local reality, licensed real estate brokers from the CPRE network serve as a validation layer:

1. **Sanity Check**: Reviewing SHAP-derived value driver rankings against domain knowledge.
2. **Outlier Review**: Investigating properties with high prediction error to identify data quality issues vs. genuine market anomalies.

---

## **3.3 Data Pipeline**

The data pipeline follows five stages, implemented in Python:

1. **Ingestion**: We ingest BDO Excel files via Pandas and collect Lamudi listings using web scraping logic.
2. **Filtering**: The dataset is restricted to residential properties within Metro Cebu (Cebu City, Mandaue, Lapu-Lapu, Talisay, Minglanilla, and Consolacion).
3. **Regex Parsing and Cleaning**: 
   - *BDO Data*: The `Property Description` string often bundles features (e.g., "3BR 2TB"). We apply regex patterns to extract `Bedrooms` and `Bathrooms`. Missing values in lot/floor area are imputed based on the median of similar property types in the same barangay.
   - *Lamudi Data*: Scraped fields often contain varying text formats (e.g., "₱ 5,000,000" or "Contact agent for price"). We clean currency symbols and commas, dropping rows without explicit numerical prices.
4. **Geocoding**: We batch-process addresses through the Google Maps Geocoding API, standardizing barangay names and securing precise coordinates.
5. **GIS Augmentation**: From these geocoded coordinates, we engineer geospatial features:
   - Proximity metrics (Haversine distances to key economic nodes).
   - Amenity scores (OSM-derived counts within a 1 km radius).
   - Spatial lag (mean price of neighboring properties within a 1 km radius).

**Tools**: Python (Pandas, Scikit-learn, XGBoost, osmnx), Google Maps API for geocoding, QGIS for spatial visualization.

---

## **3.4 Feature Engineering**

| Category           | Features                                                                          | Source             |
| ------------------ | --------------------------------------------------------------------------------- | ------------------ |
| **Structural**     | Lot Area, Floor Area, Bedrooms, Bathrooms, Parking, Property Type                 | BDO / Lamudi       |
| **Locational**     | Barangay, Latitude/Longitude                                                      | Google Maps API    |
| **Geospatial** ⭐   | Proximity to Ayala, IT Park, SM Seaside, Airport, **CBRT stations** (Haversine)   | Geocoding + GIS    |
| **Amenity Score**  | Count of schools, hospitals, commercial centers, transit stops within 1 km radius | OSM / osmnx        |
| **Spatial Lag**    | Mean price of neighboring properties within defined radius                        | Computed from data |
| **Administrative** | BIR Zonal Value (per barangay)                                                    | BIR schedules      |
| **Macro**          | BSP RPPI quarterly index                                                          | BSP data           |
| **Data Source**    | Source indicator (BDO vs. Lamudi)                                                 | Engineered         |

**Engineered variables**: Price per sqm, Valuation Gap (Price − Zonal Value), Log(Price).

### **3.4.1 Geospatial Feature Engineering**

This is the core methodological contribution of this study. Geospatial features are extracted through the following pipeline:

1. **Geocoding (Google Maps API)**: Each property address is geocoded to obtain precise latitude/longitude coordinates. The Google Maps Geocoding API is chosen for its superior handling of Philippine address formats, which often include barangay names, landmarks, or informal location descriptors.

2. **Proximity Features (Haversine Formula)**: For each geocoded property, the Haversine formula computes great-circle distances to key economic and infrastructure nodes:
- Ayala Center Cebu (primary CBD)
   - Cebu IT Park (employment hub)
   - SM Seaside City (commercial center)
   - Mactan-Cebu International Airport
   - Planned Cebu Bus Rapid Transit (CBRT) station locations

3. **Custom Value Driver Scoring Model (OSM via osmnx)**: 
   Rather than relying solely on arbitrary distances, we develop a custom amenity scoring model using OpenStreetMap data. Utilizing the `osmnx` library, we query points of interest (POI) within a 1 kilometer network radius of each property. We select a 1 km radius as it generally corresponds to a 10-15 minute walkable catchment area. The amenity score is computed not just as a raw count, but as a weighted index reflecting urban density:
   - Educational institutions (schools, universities): Standard weight
   - Healthcare facilities (hospitals, clinics): High weight
   - Commercial establishments (malls, markets): Medium weight
   - Public transport stops (jeepney routes, bus stops): High weight

   *Note: Specific weight allocations will be finalized during initial exploratory data analysis to ensure they reflect local variance correctly.*

4. **Spatial Lag Variable**: To capture neighborhood price effects (spatial autocorrelation), we compute the mean actual price of all other properties within a 1 kilometer radius of the target property. This operationalizes Tobler's First Law—that near things are more related than distant things—directly into our non-spatial ML algorithms.

---

## **3.5 Pre-processing**

| Step                   | Method                                     | Rationale                                      |
| ---------------------- | ------------------------------------------ | ---------------------------------------------- |
| **Outlier Detection**  | IQR (Interquartile Range) method           | Statistically principled; no arbitrary cutoffs |
| **Log Transformation** | ln(Price) as target variable               | Normalizes the right-skewed price distribution |
| **Missing Values**     | Barangay-level median imputation           | Preserves local spatial context                |
| **Encoding**           | One-Hot Encoding (Property Type, Barangay) | Required for regression and tree-based models  |

---

## **3.6 Modeling Strategy**

### **3.6.1 The Three Models**

| #   | Model                        | Strength                                          | Weakness                 |
| --- | ---------------------------- | ------------------------------------------------- | ------------------------ |
| 1   | **Hedonic Regression (OLS)** | Interpretable; coefficients have economic meaning | Assumes linearity        |
| 2   | **Random Forest**            | Handles non-linearities; robust to overfitting    | Less interpretable       |
| 3   | **XGBoost**                  | Best predictive performance on tabular data       | Hyperparameter-sensitive |

### **3.6.2 Hedonic Equation**

The hedonic regression takes the following log-linear form:

$$\ln(Price) = \alpha + \beta_1 \ln(Area) + \beta_2(BR) + \beta_3(Dist_{CBD}) + \beta_4(ZonalValue) + \beta_5(AmenityScore) + \beta_6(SpatialLag) + \epsilon$$

Where $AmenityScore$ represents the OSM-derived neighborhood quality index, $SpatialLag$ captures neighboring property price effects, and $ZonalValue$ is the BIR benchmark. This specification extends the traditional hedonic model by explicitly incorporating GIS-derived geospatial features and administrative data.

### **3.6.3 Hyperparameter Tuning**

For the ML models (Random Forest and XGBoost), hyperparameters are optimized via **GridSearchCV** with **K-Fold Cross Validation** (K = 5 or 10, depending on final sample size). This avoids overfitting while maximizing generalization performance.

---

## **3.7 Evaluation and Explainability**

### **3.7.1 Performance Metrics**

| Metric   | Description                    | Purpose                                        |
| -------- | ------------------------------ | ---------------------------------------------- |
| **MAPE** | Mean Absolute Percentage Error | Primary metric; enables cross-study comparison |
| **R²**   | Coefficient of Determination   | Proportion of variance explained               |
| **MAE**  | Mean Absolute Error (in ₱)     | Business-interpretable error                   |
| **RMSE** | Root Mean Square Error         | Penalizes large errors                         |

### **3.7.2 Benchmark Targets**

| Study                  | Context                     | MAPE   | Our Target                                           |
| ---------------------- | --------------------------- | ------ | ---------------------------------------------------- |
| Ramolete et al. (2023) | Philippines, larger dataset | 10–21% | < 25% (they had larger, cleaner data)                |
| Nyanda et al. (2024)   | Tanzania, n ≈ 954           | 48%    | Beat 48% (same sample size, but we add GIS features) |

### **3.7.3 SHAP Explainability**

To satisfy IVS 2025 transparency requirements (IVS 104) and provide actionable insights, we employ **SHAP (SHapley Additive exPlanations)**:

- **Global SHAP (Summary Plots)**: Identifies which value drivers affect Metro Cebu property prices most across the entire dataset. This answers RQ1 ("What value drivers significantly influence property prices in Metro Cebu?").
- **Local SHAP (Force Plots)**: Explains individual predictions. For example: *"This Lahug condo is valued at ₱X: +₱1.2M due to IT Park proximity, −₱300K due to small floor area, +₱200K due to high amenity score."*

This dual-level explainability makes the model transparent and auditable, positioning it as a **decision-support tool** rather than a black box.

---

## **3.8 Deliverables**

### **3.8.1 QGIS Interactive Map (Primary Deliverable)**

The core prescriptive output is a QGIS interactive project map. This is not a static image, but an exploratory environment designed for decision support consisting of the following key layers:

1. **Property Valuations**: Point vectors representing individual geocoded properties. They are color-coded based on the model's prediction error (actual vs. predicted), allowing users to visually identify undervalued anomalies or overvalued clusters.
2. **Valuation Gap Heatmap**: A raster heatmap visualizing the divergence between the ML model predictions and the official BIR Zonal Values. Hotspots indicate areas where official valuations significantly lag market realities.
3. **CBRT & Infrastructure Overlays**: Line segments denoting the planned CBRT route with 500m and 1km buffer zones. This allows users to visualize how upcoming public transit infrastructure intersects with current market valuations.
4. **Value Driver Contours**: ISO-chrones or distance contours measuring proximity to the CBD (Ayala Center) or IT Park. 

This deliverable transforms the ML model from a theoretical exercise into an actionable system, equipping brokers, investors, and local government units with spatial intelligence.

### **3.8.2 Streamlit Web Application (Exploratory)**

Complementing the QGIS map, we provide an interactive Streamlit web dashboard. Users can input specific property structural features (e.g., floor area, bedrooms) and select a location on a map. The application then queries the underlying trained XGBoost/Random Forest model and outputs a predicted price along with a SHAP Waterfall plot. This dynamically explains *why* the property received that specific valuation, detailing the exact peso contribution of each feature.

---

## **3.9 Timeline and Milestones**

| Phase             | Activity                                               | Timeline        |
| ----------------- | ------------------------------------------------------ | --------------- |
| **1. Data**       | Lamudi scraping + BDO cleaning                         | Feb 18 – Feb 28 |
| **2. Proposal**   | Panel Presentation                                     | Feb 21          |
| **3. Build**      | Geocoding + GIS feature engineering (Google Maps, OSM) | Mar 1 – Mar 14  |
|                   | Model training + Hyperparameter tuning                 | Mar 15 – Mar 28 |
| **4. Colloquium** | Research updates presentation                          | Mar 28          |
| **5. Evaluate**   | SHAP analysis + QGIS map + Broker validation           | Apr 1 – Apr 18  |
| **6. Write**      | Draft final paper (Chapters 4–10)                      | Apr 18 – May 2  |
| **7. Defend**     | Final Research Paper presentation                      | May 9           |
|                   | Final Submission                                       | May 23          |
