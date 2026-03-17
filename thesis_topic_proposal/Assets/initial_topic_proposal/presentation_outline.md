# Thesis Presentation Outline: Data-Driven Property Valuation for Cebu City

## Slide 1: Title Slide

- **Title:** Data-Driven Property Valuation Factors and Model for Cebu City
- **Subtitle:** A Comparative Analysis of Hedonic Regression and Machine Learning Approaches
- **Presenter:** [Your Name]
- **Context:** Research Methods / Thesis Proposal Defense
- **Date:** December 2025

## Slide 2: The Problem (Stakeholder Focus)

- **Stakeholder:** Cebu Premiere Real Estate (CPRE).
- **Current Pain Point:** Valuation relies on fragmented data (outdated BIR Zonal Values, subjective bank appraisals, inconsistent listing prices).
- **The Gap:** No transparent, data-driven tool exists to estimate *fair market value* specifically for Cebu's residential market.
- **Consequence:** Difficulty in advising clients (buyers/sellers) on "fair" pricing.

## Slide 3: Research Objectives

1. **Compare Models:** Test if Machine Learning (Random Forest, XGBoost) outperforms traditional Hedonic Regression in predicting property values.
2. **Identify Drivers:** Quantify the impact of specific features (Location, Floor Area, Amenities) on price.
3. **Valuation Gap:** Analyze the discrepancy between BIR Zonal Values and Market Prices.
4. **Future Factors:** Assess the impact of infrastructure projects (CBRT, Metro Cebu Expressway).

## Slide 4: Literature Review - The "Why"

- **Local Context (Agosto, 2017):** Confirmed that "Accessibility" is the dominant driver of land values in Cebu.
- **The Gap (Domingo & Fulleros, 2005):** Established the "Valuation Gap" between tax values and market realities.
- **Methodology (Viray, 2023):** Demonstrated that Random Forest can outperform Linear Regression in Philippine settings.
- **New Insight (Gayathri & Thekkayil, 2025):** Validated the use of **Ensemble Models (RF + XGBoost)** and the inclusion of **"Future Factors"** (infrastructure plans) for high accuracy (97%).

## Slide 5: Methodology - The Pipeline

- **Data Source:** BDO Foreclosed Properties (Verified: 955 entries).
- **Data Processing:**
  1. **Ingestion:** Load Excel data.
  2. **Cleaning:** Regex parsing for "Property Description", handling missing values.
  3. **Feature Engineering:** Geocoding (Lat/Long), Distance to CBD/CBRT, "Future Factor" flags.
- **Modeling:**
  - Baseline: OLS Linear Regression (Interpretability).
  - Challengers: Random Forest & XGBoost (Predictive Power).

## Slide 6: Preliminary Data Insights

- **Dataset Volume:** 955 Residential Properties.
- **Key Features Available:** Region, City, Lot Area, Floor Area, Price.
- **Next Step:** Extracting "Bedrooms", "Bathrooms", and "Subdivision" from unstructured text descriptions.

## Slide 7: Expected Output & Value

- **For CPRE:** A working prototype/dashboard where they input property details and get a "Fair Market Value" range.
- **For Academia:** Empirical evidence on the drivers of Cebu real estate value.
- **For Policy:** Insights into the divergence of Zonal vs. Market values.

## Slide 8: Timeline & Next Steps

- **Now:** Finalize Chapter 3 (Methodology) & Data Cleaning Pipeline.
- **Next Week:** Feature Engineering (Geocoding & Distance Calculation).
- **Month End:** Model Training & Evaluation.
