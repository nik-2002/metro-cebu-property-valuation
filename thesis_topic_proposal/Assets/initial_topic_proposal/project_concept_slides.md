# Project Concept Presentation (10 Slides)

**Topic:** Data-Driven Property Valuation Factors and Model for Cebu City
**Format:** 10 Slides (Strict Requirement)

---

## Slide 1: Background
**Visual:** Cebu Economic Growth Chart / Map of Cebu City
**Content:**
*   Cebu is the fastest-growing regional economy (7.3% growth in 2024).
*   Real estate contributes ~6% to GDP, driven by IT-BPM and Tourism.
*   **The Problem:** The valuation landscape is fragmented.
    *   **BIR Zonal Values:** Outdated (2018/2019) and static.
    *   **Bank Appraisals:** Conservative and opaque.
    *   **Market Listings:** Highly variable and often inflated.

## Slide 2: Statement of the Problem
**Visual:** "Broken Compass" or diverging price tags icon
**Content:**
*   There is **no scientifically validated, data-driven model** for residential property valuation in Cebu City.
*   Stakeholders (Developers, Brokers, Buyers) rely on:
    *   "Gut feel" / Intuition
    *   Disjointed data sources
    *   Manual "Sales Comparison" of just ~3 properties.
*   **Core Question:** How can real estate firms utilize data-driven models to predict property values accurately and consistently?

## Slide 3: Research Objectives
**Visual:** Target / Bullseye
**Content:**
1.  **Develop** a rigorous data processing pipeline to aggregate sparse property data.
2.  **Compare** the accuracy of **Hedonic Regression** (Traditional) vs. **Machine Learning** (Random Forest, XGBoost).
3.  **Quantify** the "Valuation Gap" between administrative pricing (BIR) and market reality.
4.  **Measure** the value of "Future Factors" (e.g., proximity to planned Cebu BRT stations).

## Slide 4: Solution Requirements
**Visual:** Technical Stack Icons (Python, Pandas, Scikit-Learn, QGIS)
**Content:**
*   **Data Aggregation:** Application to scrape and parse listings from web portals (Ceiling Price) and bank foreclosures (Floor Price).
*   **Geospatial Engine:** Logic to calculate "Isochrones" and distances (Haversine) to key hubs (Ayala, IT Park, BRT).
*   **Modeling Engine:** Python-based environment to train and tune ML models (RF, XGBoost).
*   **Dashboard:** A prototype interface (Streamlit) for plotting values and "What-If" scenarios.

## Slide 5: Significance
**Visual:** Stakeholder Icons (Broker, Gov, Investor)
**Content:**
*   **For CPRE (Brokerage):** Provides a standardized, defensible pricing tool for clients.
*   **For Investors/Buyers:** Increases transparency and trust in "Fair Market Value."
*   **For Policymakers:** Highlights the lag in tax mapping (Zonal Values) vs. market growth.
*   **Academic Contribution:** First major study to apply ML valuation specifically to the *Cebu* context.

## Slide 6: Scope and Delimitations
**Visual:** Map of Cebu with boundaries
**Content:**
*   **Scope:**
    *   **Location:** Cebu City and immediate Metro Cebu neighbors (Mandaue, Talisay).
    *   **Type:** Residential Properties (House & Lot, Condominium, Vacant Lot).
    *   **Timeframe:** Listings active from Q4 2024 to Q1 2026.
*   **Delimitations:**
    *   Excludes Commercial/Industrial properties.
    *   Does not account for "Interior Finish" quality (unobservable in text data).
    *   Uses *Listing/Asking Prices* as a proxy for Market Value (due to Data Privacy on sold deeds).

## Slide 7: Dataset Source and Description

**Visual:** Data Pipeline Diagram (BDO PDF -> Excel -> Scraper -> CSV)

**Content:**

*   **Hybrid Data Strategy (The "Why"):**
    *   **Constraint:** Actual Deed of Sale data is private/inaccessible.
    *   **Source A (Floor):** **BDO Foreclosures** (Verified but Conservative). Used to set the price baseline.
    *   **Source B (Ceiling):** **Online Listings** (Abundant but Speculative). Used to capture market sentiment.

*   **Validation Layer (The "How"):**
    *   **Human-in-the-Loop:** Collaboration with licensed brokers (CPRE).
    *   **Method:** Expert sanity checks on outliers (e.g., flagging unrealistic Asking Prices).

*   **Variables:**
    *   **Target:** Price (Php) / Price per Sqm.
    *   **Features:** Lot Area, Floor Area, Bedrooms, Bathrooms, Location (Coords), Distance to CBD.

## Slide 8: Methodology

**Visual:** Flowchart (Data Cleaning -> Feature Eng -> Modeling -> Eval)

**Content:**

1.  **Preprocessing:**
    *   Regex parsing (e.g., extracting "3BR" integers).
    *   Outlier Removal (IQR Rule).
    *   Log-Transformation of Price (Normalizing skewed values).

2.  **Geospatial Feature Engineering:**
    *   Calculate distance to nearest **Cebu BRT Station**.
    *   **Amenity Score:** Count of schools/hospitals within 1km radius.

3.  **Modeling Strategy:**
    *   **Baseline:** OLS Linear Regression (for Interpretability).
    *   **Challengers:** Random Forest & XGBoost (for Non-linearity & Accuracy).
    *   **Tuning:** GridSearchCV for hyperparameter optimization.

## Slide 9: Expected Analytics Results
**Visual:** Bar Chart placeholder (Model Accuracy), SHAP Plot example
**Content:**
*   **Accuracy Target:** Machine Learning models expected to achieve **R-Squared > 0.80**, outperforming OLS.
*   **Key Drivers:** Expect "Location" (Distance to IT Park) and "Floor Area" to be top predictors.
*   **Explainability:** SHAP Force Plots will explain *individual* property valuations (e.g., "This condo is +1M due to BRT proximity").

## Slide 10: Ethical Considerations
**Visual:** Privacy Shield / Scales of Justice
**Content:**
*   **Data Privacy:** Strict adherence to DPA 2012. No private owner names or contact numbers will be scraped/stored.
*   **Transparency:** The model is a *decision support tool*, not a replacement for professional appraisal.
*   **Bias Mitigation:** "Human-in-the-loop" validation with licensed brokers to flag realistic vs. speculative pricing.
