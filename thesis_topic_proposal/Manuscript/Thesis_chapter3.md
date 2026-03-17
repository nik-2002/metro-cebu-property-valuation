# **Chapter 3 | Research Methodology**

## **3.1 Research Design**

This study employs a **quantitative research design** focused on predictive modeling. Specifically, we use a supervised learning approach to estimate residential property values in Cebu City. The "dependent variable" is the market price (or price per square meter), and the "independent variables" are the property structural features, location attributes, and macroeconomic indicators.

The study compares a baseline **Hedonic Price Model** (Multiple Linear Regression) against non-linear **Machine Learning approaches** (Random Forest and Gradient Boosting/XGBoost). This design allows us to quantifying the trade-off between interpretability (hedonic) and predictive accuracy (ML), while explicitly testing the value of government administrative data (BIR Zonal Values) as a feature.

## **3.2 Research Population and Data Sources**

The "population" for this study consists of residential properties (House & Lot, Condominium, Vacant Lot) in the **Metro Cebu** area, with a specific focus on Cebu City.

### **3.2.1 Primary Data: Foreclosed Properties**

The primary dataset is a snapshot of foreclosed property listings from **BDO Unibank**, dated November 18, 2025 (`BDO-Properties-as-of-11.18.25`).

- **Volume**: The raw file contains **955** property entries.
- **Coverage**: Includes properties across multiple regions, from which we will filter for **Cebu** (Region VII / Central Visayas).
- **Key Variables**:
  - **Location**: Region, City, Property Address (approximated for geocoding).
  - **Physical**: Lot Area (sqm), Floor Area (sqm), Property Type (e.g., "House and Lot", "Condominium").
  - **Financial**: Advertised Price (Php), which serves as our proxy for "Market Price" (specifically, distressed market value).
  - **Descriptive**: A text field (`Property Description`) containing details like bedrooms and bathrooms, which will be parsed.

### **3.2.2 Secondary Data: Online Listings**

To supplement the distressed asset data and represent "fair market value" listings, we will collect current property listings from public online platforms (e.g., Lamudi, Facebook Marketplace). This dataset will help validate if foreclosed properties transact at a significant discount compared to the broader market. _(Note: This data collection is ongoing)._

### **3.2.3 Macroeconomic and Administrative Data**

- **BIR Zonal Values**: Official zonal values for the specific barangays in Cebu City, used to calculate the "valuation gap."
- **BSP Residential Property Price Index (RPPI)**: Quarterly index values for Areas Outside NCR (AONCR) to control for time-trend effects (inflation/market cycle).

## **3.3 Data Instrument**

The research does not use a survey questionnaire. Instead, the "instrument" is a **computational data pipeline** built using the Python programming language.

- **Data Processing**: `Pandas` for cleaning, merging, and variable transformation.
- **Geocoding**: Google Maps API or OpenStreetMap (Nominatim) to convert text addresses into Latitude/Longitude coordinates.
- **Modeling**: `Scikit-learn` for Linear Regression and Random Forest; `XGBoost` or `LightGBM` for gradient boosting models.
- **Deployment**: `Streamlit` to create the interactive valuation dashboard for the end-user (CPRE).

## **3.4 Data Gathering Procedures**

1.  **Ingestion**: The BDO Excel file is ingested into the Python environment.
2.  **Filtering**: The dataset is filtered to include only "Residential" properties located in "Cebu City" or key Metro Cebu cities (Mandaue, Lapu-Lapu, Talisay, Minglanilla, Consolacion).
3.  **Parsing**: The `Property Description` field is parsed using Regular Expressions (Regex) to extract structured features:
    - Number of Bedrooms (BR)
    - Number of Bathrooms (TB/T&B)
    - Parking/Garage availability
4.  **Geocoding**: Property addresses are batch-processed to obtain spatial coordinates (Lat/Lon) and specific Barangay names.
5.  **Augmentation**:
    - **Proximity Features**: Distances to key landmarks (Ayala Center Cebu, IT Park, SM Seaside, Mactan Airport) are calculated using the Haversine formula.
    - **Zonal Value Mapping**: Each property is matched to its corresponding BIR Zonal Value based on its Barangay and Street/Subdivision.

## **3.5 Data Treatment and Analysis**

The data analysis proceeds in three stages:

### **3.5.1 Pre-processing**

- **Outlier Detection**: Properties with extreme prices (e.g., top 1%) or unrealistic dimensions (e.g., Lot Area < 20 sqm) are flagged or removed.
- **Imputation**: Missing values for `Floor Area` (if minor) may be imputed using median values per Property Type.
- **Feature Engineering**: Creation of new variables such as `Price per Square Meter` and `Valuation Gap` (Advertised Price - Zonal Value).

### **3.5.2 Modeling Strategy**

We train three distinct model architectures to estimate price:

1.  **Multiple Linear Regression (Hedonic)**: Interpretable baseline.
    $$ \ln(Price) = \alpha + \beta*1 \ln(Area) + \beta_2 (Bedrooms) + \beta_3 (Distance*{CBD}) + \epsilon $$
2.  **Random Forest Regressor**: Captures non-linearities (e.g., price plateaus) and interactions (e.g., location value depending on lot size).
3.  **XGBoost Regressor**: High-performance gradient boosting to minimize prediction error.

### **3.5.3 Validation and Metrics**

To ensure the model generalizes well to unseen data:

- **Validation Scheme**: We use a **Time-Aware Train-Test Split** (training on older listings, testing on newer ones) or standard **K-Fold Cross Validation**.
- **Performance Metrics**:
  - **MAE (Mean Absolute Error)**: Average error in Pesos (interpretable for business).
  - **MAPE (Mean Absolute Percentage Error)**: Average % error (e.g., "off by 10%").
  - **RMSE (Root Mean Square Error)**: Penalizes large errors.
  - **R-squared ($R^2$)**: Percentage of price variation explained by the model.

Finally, we assess the **Feature Importance** scores from the Tree-based models to confirm which factors (e.g., Location vs. Floor Area vs. Zonal Value) are the strongest drivers of property value in Cebu.
