# Technical Narrative
### Methodology Writeshop Activity
*APA 7th Edition | Double-spaced | 12pt font | ~560 words*

---

**Data Acquisition and Cleaning**

Data was collected from multiple sources to cover Metro Cebu's property market. Residential listings were scraped from Lamudi, returning 845 records across Cebu Province; after filtering to the six-LGU urban core (Cebu City, Mandaue, Lapu-Lapu, Talisay, Consolacion, and Minglanilla), 712 listings were kept. Floor price data was pulled from the Pag-IBIG Fund's Online Property Auction platform, giving 96 Metro Cebu records. BDO Unibank foreclosure listings were downloaded as an Excel file and filtered to the same area. BIR Zonal Values were compiled at the barangay level as the official price reference. The combined dataset covered both open-market and distressed-sale segments, and a source indicator variable was added to account for the systematic price difference between them.

Missing structural values were filled using barangay-level median imputation, and records with no price were dropped. Outliers were flagged using the interquartile range (IQR) method. Two other sources—Leechiu Property and Lifenavi—were collected but excluded due to insufficient Metro Cebu residential coverage; Leechiu listings were primarily large-scale commercial transactions, while Lifenavi returned only one usable record. One adjustment was also made to the original plan: Lamudi listings already had latitude and longitude embedded, so the planned Google Maps API geocoding step was unnecessary for the primary dataset.

**Feature Engineering and Selection**

The target variable was defined as price per square meter and log-transformed to address right-skewness. Features were grouped into structural (lot area, bedrooms, bathrooms, property type), locational (barangay, latitude, longitude), geospatial, administrative, and macroeconomic categories.

The geospatial features were the most technically involved part of the preparation. Straight-line distances were computed from each property to major urban landmarks—Ayala Center Cebu, Cebu IT Park, SM Seaside City, Mactan-Cebu International Airport, and planned CBRT station sites. Using the `osmnx` library and OpenStreetMap data, amenity scores were built for each property based on the number of schools, hospitals, commercial establishments, and transit stops within a one-kilometer network radius. The scoring approach was adapted from Project OHANA (Alvarez et al., 2021), a local open-source tool that applies Hansen's Gravity Model to OSM data; the original per-grid implementation was modified to compute per-property scores. A spatial lag variable—the average price of neighboring properties within one kilometer—was also included to capture how surrounding prices affect value. BIR Zonal Values were joined at the barangay level, and the BSP Residential Real Estate Price Index (RPPI) was included as a feature to let the model absorb time-trend variation across the collection period, rather than deflating prices to a reference date. Individual distance variables were consolidated into composite accessibility indices following Rey-Blanco et al. (2024) to reduce multicollinearity, and categorical variables were one-hot encoded.

**Model Architecture and Training**

Three models were built: Ordinary Least Squares (OLS) hedonic regression as a readable baseline, a Random Forest regressor, and an XGBoost regressor. The OLS model used a log-linear form so its coefficients could be read directly. For Random Forest and XGBoost, hyperparameters were tuned using GridSearchCV with five-fold cross-validation. The final sample size of roughly 900 records directly informed this model choice: deep learning architectures were excluded because they tend to overfit on small structured datasets and sacrifice the interpretability required under IVS 2025 standards (Wang & Li, 2020; Nyanda et al., 2024).

**Evaluation Metrics and Validation**

The primary metric was Mean Absolute Percentage Error (MAPE), chosen for comparability with similar studies (Ramolete et al., 2023; Nyanda et al., 2024). R², Mean Absolute Error in Philippine Peso, and Root Mean Square Error were used as supporting metrics. An 80/20 train-test split was used with five-fold cross-validation to assess generalization. SHAP values were applied to produce both overall feature importance rankings and individual prediction explanations, meeting IVS 2025 transparency requirements. Model outputs were then loaded into QGIS to build a valuation map, and a Streamlit web application was developed to deliver interactive, SHAP-explained predictions to end users.
