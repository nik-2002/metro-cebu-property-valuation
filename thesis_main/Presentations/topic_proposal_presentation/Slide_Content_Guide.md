# Thesis Proposal: Slide Content Guide

> **Version 2.0**: Data Science & Business Problem Focus | **24 Slides**

---

## **Part I: Project Concept (The Business & Data Problem)**

### SLIDE 1: Title Slide

- **Title**: Data-Driven Property Valuation Model for Metro Cebu
- **Subtitle**: Machine Learning Approaches to Fragmented Real Estate Pricing
- **Author**: Chris Dominic Estreba | MS Data Science, UA&P
- **Date**: February 2026

### SLIDE 2: Background: The Cebu Real Estate Landscape

- **Metric 1**: 11.5% regional property price growth (outpacing NCR).
- **Metric 2**: Supported by $38.3B in national OFW remittances.
- **Stakeholders**: Banks (mortgage risk), LGUs (taxation gaps), Brokers (pricing strategy).

### SLIDE 3: Statement of the Problem: Expectation vs. Reality

- **Expectation**: A fast-growing, multi-billion peso market requires highly accurate, continuously updated valuation models to prevent systemic financial risk.
- **Reality (Business Problem)**: Fragmented pricing. Only 37% of LGUs updated Zonal Values. Appraisers rely purely on intuition.
- **Reality (Data Problem)**: Actual Deed of Sale transaction data is private. Existing data is messy, unstructured, lacks spatial context, and sits in silos.

### SLIDE 4: Research Objectives

- **Primary**: Utilize machine learning on a hybrid dataset to predict residential prices in Metro Cebu.
- **Secondary 1**: Determine the most statistically significant geographic and structural features driving value.
- **Secondary 2**: Quantify the accuracy improvement gained by extracting unstructured text features via NLP.
- **Secondary 3**: Measure the mathematical "Valuation Gap" between market reality and BIR schedules.

### SLIDE 5: Significance of the Study

- **For LGUs**: Provides a data-driven baseline to update outdated Real Property Tax (RPT) schedules.
- **For Banks**: Reduces downside risk exposure on collateral by identifying over-speculation.
- **For the Public/CPRE**: Creates a transparent, objective pricing baseline to anchor negotiations.

### SLIDE 6: Scope and Delimitations

- **In Scope**: Residential properties (Condos, Houses, Townhouses) across Metro Cebu (Cebu City, Mandaue, Lapu-Lapu, Talisay, Consolacion, Minglanilla).
- **Out of Scope**: Commercial and Industrial real estate (These require Income-Approach valuation methodologies outside the data constraints of this study).

---

## **Part II: Review of Related Literature (The Data Foundation)**

### SLIDE 7: The Global Data Scarcity Problem

- **Finding (Kenya)**: "Limited information" ranked as the #1 problem for valuers (Mean Rank 2.91).
- **Finding (Lagos)**: 92.7% of valuers cite insufficient market evidence, causing pricing errors up to 51%.
- **Takeaway**: Bad valuations are a data-scarcity problem, not a competency problem.

### SLIDE 8: Setting the Baseline: Agosto (2020)

- **The Study**: The only major Cebu-specific empirical study on land value determinants.
- **The Finding**: Transport accessibility and recreational facilities are the top drivers of value.
- **The Limitation**: Relied on a survey of 51 practitioners. **Our thesis advances this by testing these assumptions against actual predictive models.**

### SLIDE 9: Model Selection Rationale (Tanzania Evidence)

- **Study**: Nyanda et al. (2024) in Dar es Salaam on ~954 properties.
- **Deep Learning**: Neural Networks catastrophically failed (108.6% MAPE). We are avoiding DL because our data is too sparse.
- **Tree-Based Models**: XGBoost succeeded (48.0% MAPE). This literature strictly informs our decision to use Random Forest and XGBoost.

### SLIDE 10: The NLP Rationale (Ottawa & Shanghai Evidence)

- **The Context**: Because we are heavily web scraping, unstructured text descriptions are a massive, untapped signal.
- **The Evidence**: An Ottawa study achieved an R-squared of 0.79 using self-trained Word2Vec embeddings.
- **The Takeaway**: Reading 8 recent papers proves text extraction drastically improves accuracy by 10-44%.

### SLIDE 11: Macro Factors & Compliance

- **Macro Drivers**: A 2023 Nigerian study proved Exchange Rate (r = -0.925) predicts property value better than inflation—highly relevant for Cebu's OFW market.
- **Compliance Constraint**: IVS 2025 mandates that Automated Valuation Models (AVMs) must have human oversight. Pure algorithmic prediction is not compliant.

---

## **Part III: Methodology & Expected Results**

### SLIDE 12: Research Design

- **Core Design**: Quantitative, Predictive Modeling.
- **Approach**: Supervised Machine Learning (Regression task).
- **Target Variable (Y)**: Price per sqm or Log(Price).

### SLIDE 13: Dataset Source and Description (The Hybrid Strategy)

- **Overcoming Privacy Limitations**:
  - **The Floor**: BDO Foreclosures (distressed, verified bank pricing).
  - **The Ceiling**: Lamudi/LifeNavi web scraping (speculative asking prices).
- **Control Variables**: BIR Zonal Values, BSP Residential Real Estate Price Index.

### SLIDE 14: The Data Pipeline

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

### SLIDE 15: Feature Categories

| Category            | Features                                                          | Source              |
| :------------------ | :---------------------------------------------------------------- | :------------------ |
| **Structural**      | Lot Area, Floor Area, Bedrooms, Bathrooms, Parking, Property Type | BDO / Lamudi        |
| **Locational**      | Barangay, Lat/Lon coordinates                                     | Geocoding           |
| **Proximity**       | Distance to Ayala, IT Park, SM Seaside, Mactan Airport            | Haversine formula   |
| **Text Features** ⭐ | Keywords, TF-IDF vectors, or BERT embeddings from descriptions    | NLP Pipeline        |
| **Amenity Score**   | Count of schools, hospitals, commercial within 1km radius         | OSM / Google Places |
| **Administrative**  | BIR Zonal Value per barangay                                      | BIR schedules       |
| **Macro**           | BSP RPPI quarterly index (AONCR)                                  | BSP data            |

### SLIDE 16: Feature Engineering: Geospatial & Spatial Data

- Transforming raw addresses into precise mathematical features that capture the true value of "Location."
- **Geocoding**: Using `geopy` / Nominatim API to convert text addresses ("Lahug, Cebu City") into exact Lat/Lon coordinates + Barangay classification.
- **Haversine Distance Vectors**: Computing great-circle distances from each property to 4 key economic anchors: Ayala Center, IT Park, SM Seaside, and Mactan Airport.
- **Amenity Scoring**: Querying OpenStreetMap (Overpass API) to count schools, hospitals, and commercial POIs within a 1km radius per property.
- **Building Density** *(exploratory)*: Leveraging HDX Philippines building footprint data (~11.6M structures) to compute neighborhood urbanization proxies.
- **QGIS Visualization**: Using QGIS for spatial validation, choropleth mapping, and generating publication-quality geospatial visuals (e.g., Valuation Gap heatmap overlay on Metro Cebu).
- **Output**: These spatial vectors feed directly into the Valuation Gap Heatmap on Slide 23.

### SLIDE 17: Feature Engineering: NLP & Text Data

- Turning qualitative sentences into quantitative vectors.
- **Tier 1**: TF-IDF Keywords (Baseline implementation for small datasets).
- **Tier 2**: Pre-trained BERT (Extracting semantic meaning across mixed Tagalog/English).
- **Tier 3**: Self-trained Word2Vec (If our scraper pulls >5,000 listings).

### SLIDE 18: Data Treatment & Pre-Processing

- **Distribution Normalization**: Applying `np.log1p()` to property prices to fix extreme right-skewness.
- **Missing Value Imputation**: Using Barangay-level Medians to preserve rigorous spatial context.
- **Outlier Handling**: IQR method to cleanly drop erroneous typing errors without arbitrary cutoffs.

### SLIDE 19: Core Models

- **Multiple Linear Regression**: Serves as our interpretable economic baseline, but cannot map complex spatial non-linearities.
- **Random Forest Regression**: Ensemble bagging significantly reduces variance and overfitting on noisy listings.
- **Gradient Boosting (XGBoost)**: The state-of-the-art for tabular tabular accuracy; sequentially corrects residual errors.
- **Optimization Strategy**: Use **GridSearchCV** combined with **K-Fold Cross Validation**. Tuning parameters like `n_estimators`, `max_depth`, and `learning_rate`.
- **Evaluation Metrics**:
  - **MAPE**: Mean Absolute Percentage Error (Primary benchmark for cross-study comparison, targeting <25%).
  - **MAE**: Mean Absolute Error (For communicating raw peso deviation to stakeholders).
  - **R²**: To identify how much total price variance our features explain.

### SLIDE 22: Expected Analytics Results: Explainability (SHAP)

- **Local Explanations**: Using SHAP Force Plots to explain individual prices (e.g. "This condo prediction is +P1.2M due to IT park proximity, but -P300k due to no parking").
- This satisfies the IVS 2025 mandate for transparency in Artificial Intelligence models.

### SLIDE 23: Valuation Gap (Expectation vs. Reality)

- **Calculation**: Subtracting the outdated BIR Zonal Value from the XGBoost ML Prediction.
- **Visualization**: A Geospatial heatmap identifying the exact barangays currently experiencing the highest speculative variation from government tax schedules.

### SLIDE 24: Empirical Framework

- [INSERT IMAGE HERE: High-level Empirical Framework architecture diagram showing inputs feeding into the 3 models, outputting Price and SHAP visuals].

### SLIDE 25: Ethical Considerations

- **Data Privacy**: We extract zero Personally Identifiable Information (PII) of sellers or buyers.
- **Algorithmic Bias**: Caution against historic pricing biases in low-income housing being learned and perpetuated by the models.
- **Role of AI**: This is strictly a decision support tool for licensed appraisers—not a fully autonomous valuer.

### SLIDE 26: Timeline & Milestones

- **Jan-Feb**: Data Collection (Lamudi scraping) & Proposal Finalization.
- **March**: Pipeline scripting, NLP execution, and Model Training.
- **April**: Evaluation, Broker Validation Workshops, and Manuscript Drafting.
- **May 9**: Final Research Paper Defense.

### SLIDE 27: Conclusion / Final Synthesis

- We identified a massive business gap in subjective property pricing.
- We bypassed data privacy issues using a robust floor-and-ceiling hybrid dataset.
- We built a rigorous, NLP-augmented Machine Learning pipeline to construct Cebu's first data-driven valuation engine.

### *(Optional)* SLIDE 28: Q&A

- "Thank you for listening. I open the floor to questions."
