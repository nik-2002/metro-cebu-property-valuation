# Thesis Proposal Presentation Outline

> **Thesis**: Data-Driven Property Valuation Model for Metro Cebu
> **Author**: Chris Dominic Estreba | MS Data Science, UA&P
> **Target Length**: ~26 Slides
> **Core Objective**: Present a compelling Data Science project by clearly articulating the business problem, the data problem, and the rigorous machine learning methodology used to solve it.

---

## **Part I: Project Concept (The Business & Data Problem)**

### 1. Title Slide
- Title, Subtitle, Author, Programme, Date.

### 2. Background: The Cebu Real Estate Landscape
- High-growth market: 11.5% regional price growth, massive OFW remittance influx.
- **The Stakeholders**: Banks (mortgages), LGUs (taxation), Brokers/Buyers (transactions). 

### 3. Statement of the Problem: Expectation vs. Reality
- **Expectation**: A fast-growing, multi-billion peso market requires highly accurate, objective, and continuously updated valuation models to prevent systemic risk.
- **Reality (The Business Problem)**: Valuation is fragmented. Government Zonal Values are outdated (only 37% of LGUs update them). Bank models are opaque. Appraisers lack data and rely on intuition.
- **Reality (The Data Problem)**: Actual Deed of Sale data is private. Available data (listings, foreclosures) is messy, unstructured, lacks spatial intelligence, and exists in silos.

### 4. Research Objectives
- **Primary**: Utilize machine learning on a hybrid dataset (foreclosures + listings) to predict residential property prices in Metro Cebu.
- **Secondary 1**: Determine the most important feature variables driving property values.
- **Secondary 2**: Quantify the accuracy gain from integrating Natural Language Processing (NLP) text features.
- **Secondary 3**: Measure the mathematical "Valuation Gap" between market reality and BIR Zonal Values.

### 5. Significance of the Study
- **For LGUs/Government**: Data-driven baseline to update taxation schedules fairly.
- **For Banks**: Reduces risk exposure on collateral; faster loan approvals.
- **For the Public/Brokers**: Transparent, objective pricing eliminating extreme speculation.

### 6. Scope and Delimitations
- **In Scope**: Residential properties (Condos, Houses, Townhouses) in Metro Cebu.
- **Out of Scope**: Commercial/Industrial properties (valued via Income Approach, which requires different data). 

---

## **Part II: Review of Related Literature (The Data Foundation)**
*Focus: How previous research dictates our data science methodology.*

### 7. The Global Data Scarcity Problem
- Studies in Kenya and Lagos prove that valuation inaccuracy (+51% error) is driven by "insufficient data", not valuer incompetence. The Philippines faces the exact same gap.

### 8. Setting the Baseline: Agosto (2020)
- The only Cebu-specific study. Proved that Transport Accessibility and Amenities dictate value.
- **The Limitation**: Used a survey of 51 practitioners. We are advancing this by using mathematical modeling on actual transaction data.

### 9. Model Selection Rationale (Tanzania Evidence)
- **Why not Deep Learning?** Nyanda et al. (2024) tested on ~954 properties. We are not leaning towards Deep Learning because of the sparse nature of our data, where Neural Networks typically struggle.
- Tree-based models (Random Forest, XGBoost) succeeded (48% error). This dictates our choice of models for our similarly-sized dataset.

### 10. The NLP Rationale (Ottawa & Shanghai Evidence)
- Standard models ignore the text paragraph in a listing. Because we are relying heavily on web scraping, extracting value from unstructured text descriptions is crucial.
- Literature proves text extraction (Word2Vec, ChatGPT) adds 10-44% accuracy by capturing nuances like "corner lot" or "newly renovated".

### 11. Macro Factors & Compliance
- **Macro**: Exchange rates (OFW power) heavily drive developing real estate markets (Nigerian study).
- **Compliance**: IVS 2025 mandates that Automated Valuation Models (AVMs) must have human oversight and transparency.

---

## **Part III: Methodology & Expected Results**

### 12. Research Design
- Quantitative, Predictive Modeling. Supervised Learning (Regression) targeting `Log(Price)`.

### 13. Dataset Source and Description (The Hybrid Strategy)
- Overcoming data privacy by combining the "Floor" and "Ceiling".
- **Floor**: BDO Foreclosures (Verified, distressed bank pricing).
- **Ceiling**: Web-scraped Listings from Lamudi/DotProperty (Speculative asking prices).
- **Control**: BIR Zonal Values and BSP Price Index.

### 14. The Data Pipeline
- **Visual Flowchart**:
```text
┌────────────┐    ┌──────────┐    ┌────────────┐    ┌───────────────┐    ┌───────────┐
│ 1. INGEST  │ →  │ 2. FILTER│ →  │ 3. PARSE   │ →  │ 4. GEOCODE    │ →  │ 5. AUGMENT│
│ BDO Excel  │    │ Cebu only│    │ Regex: BR, │    │ Address →     │    │ Distances,│
│ + Scrape   │    │ Residntl │    │ T&B, Pkg   │    │ Lat/Lon +     │    │ Amenity   │
│ Lamudi     │    │          │    │            │    │ Barangay      │    │ Scores,   │
│            │    │          │    │            │    │               │    │ Text Feat.│
└────────────┘    └──────────┘    └────────────┘    └───────────────┘    └───────────┘
```

### 15. Feature Categories
We structure our variables across several categories before modeling:

| Category            | Features                                                          | Source              |
| :------------------ | :---------------------------------------------------------------- | :------------------ |
| **Structural**      | Lot Area, Floor Area, Bedrooms, Bathrooms, Parking, Property Type | BDO / Lamudi        |
| **Locational**      | Barangay, Lat/Lon coordinates                                     | Geocoding           |
| **Proximity**       | Distance to Ayala, IT Park, SM Seaside, Mactan Airport            | Haversine formula   |
| **Text Features** ⭐ | Keywords, TF-IDF vectors, or BERT embeddings from descriptions    | NLP Pipeline        |
| **Amenity Score**   | Count of schools, hospitals, commercial within 1km radius         | OSM / Google Places |
| **Administrative**  | BIR Zonal Value per barangay                                      | BIR schedules       |
| **Macro**           | BSP RPPI quarterly index (AONCR)                                  | BSP data            |

### 16. Feature Engineering: Geospatial & Spatial Data
- Geocoding raw addresses → precise Lat/Lon + Barangay using `geopy` / Nominatim.
- Haversine Distance Vectors to 4 economic anchors (Ayala, IT Park, SM Seaside, Mactan Airport).
- OpenStreetMap Amenity Scoring (schools, hospitals, commercial POIs within 1km radius).
- Building Density from HDX Philippines footprint data (~11.6M structures).
- QGIS for spatial validation, choropleth mapping, and publication-quality geospatial visuals.

### 17. Feature Engineering: NLP & Text Data
- NLP pipeline to convert raw descriptions into predictive vectors.
- Progression: TF-IDF (baseline) → Pre-trained BERT (if text is rich) → Self-trained Word2Vec (if n > 5k).

### 18. Data Treatment & Pre-Processing
- Outlier handling (IQR).
- Distribution Normalization (Log transformation of Price).
- Missing Value Imputation (Preserving spatial integrity via Barangay-level medians).

### 19. Core Models (Hedonic vs. Tree-Based)
- **Multiple Linear Regression**: Serves as our interpretable economic baseline, but cannot map complex spatial non-linearities.
- **Random Forest**: Ensemble bagging reduces overfitting and maps geospatial interactions cleanly.
- **XGBoost (Gradient Boosting)**: The state-of-the-art for tabular predictive maximum accuracy, sequentially correcting residual errors.
- **Optimization**: Hyperparameter tuning via GridSearchCV with K-Fold Cross Validation to ensure models generalize well.
- **Evaluation Metrics**:
  - **MAPE**: Primary metric for cross-reference (Targeting < 25%).
  - **RMSE & MAE**: For absolute peso-value error.
  - **R²**: To understand variance explained.

### 20. Ethical Considerations
- **Data Privacy**: No PII (Personally Identifiable Information) of buyers/sellers is scraped or exposed.
- **Algorithmic Bias**: Ensuring the model doesn't systematically undervalue low-income barangays due to historical data bias.
- **Human-in-the-loop**: The model is a decision-support tool meant to be reviewed by licensed brokers, not an autonomous agent. 

### 21. Thank You / Q&A
- Summarizing the pivot from a messy data problem to a structured, ML-driven solution that provides immediate business value to the Cebu market.
- Open floor for panel questions.
