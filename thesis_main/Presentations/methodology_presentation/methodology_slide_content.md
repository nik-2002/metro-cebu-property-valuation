# Methodology Presentation: Slide Content Guide

> **Thesis**: Data-Driven Property Valuation Model for Metro Cebu  
> **Author**: Chris Dominic Estreba  
> **Format**: 10 slides | 15 mins (+ 5 min Q&A)  
> **Date**: February 14, 2026  
> **Building from**: Project Concept (Jan 24) → Literature Review (Feb 7) → **Methodology (Feb 14)**

---

## Narrative Arc

```
RRL RECAP → DESIGN → DATA SOURCES → PIPELINE → FEATURE ENG. → TEXT FEATURES → MODELS → EVALUATION → FRAMEWORK → TIMELINE
     ↓          ↓          ↓            ↓            ↓              ↓              ↓          ↓           ↓           ↓
 "The Gap"  "Quant."   "Hybrid"     "Python"    "Geospatial"   "NLP (NEW)"    "3 Models"  "4 Metrics"  "Full Map"  "Gantt"
```

---

## SLIDE 1: Title & Recap (~1 min)

### Content
- **Title**: Research Methodology
- **Subtitle**: Data-Driven Property Valuation for Metro Cebu
- **Author**: Chris Dominic Estreba
- **Programme**: MS Data Science, UA&P
- **Date**: February 14, 2026

### Recap from RRL (transition)
> **Where we left off**: The literature confirms data scarcity is the core problem, tree-based ML outperforms neural networks on small datasets, and text-based features add 10–44% accuracy improvements. **To our knowledge, no study implements predictive ML modeling on property-level transaction data in Cebu.**

### Speaker Notes
> "Last week, our literature review established that a Cebu-focused valuation model is the clear research gap. Today I'll walk you through exactly *how* we plan to build and validate that model — including a new component: extracting value signals from listing text using NLP."

### Clarification Notes
- **Transaction-based**: Using actual property prices from listings/foreclosures, not just surveys or expert opinions
- **ML-augmented**: Machine Learning enhanced — going beyond traditional regression
- **NLP (Natural Language Processing)**: Using computational techniques to extract useful information from text (listing descriptions)

---

## SLIDE 2: Research Design (~1.5 min)

### Headline
**"Quantitative · Supervised Learning · Comparative Modeling"**

### Content
| Aspect                    | Detail                                                           |
| ------------------------- | ---------------------------------------------------------------- |
| **Design**                | Quantitative, Predictive Modeling                                |
| **Approach**              | Supervised Learning (Regression)                                 |
| **Dependent Variable**    | Property Price (₱) / Price per sqm                               |
| **Independent Variables** | Structural, Locational, Macroeconomic, **Text-derived** features |

### Comparison Framework
```
Interpretability ←————————————→ Predictive Accuracy

  Hedonic Regression        Random Forest          XGBoost
  (Baseline)               (Non-linear)         (High-performance)
```

### Key Design Choice
> We test whether **text-derived features** from listing descriptions and **government administrative data** (BIR Zonal Values) improve ML predictions — approaches validated by recent literature on hybrid NLP+ML models and by Agosto (2020) on government indicator effects.

### Speaker Notes
> "This is a quantitative study comparing three model architectures. The hedonic regression serves as our interpretable baseline — the same approach used in decades of real estate research. Random Forest and XGBoost are our ML challengers, chosen because the Tanzania study showed tree-based models handle small, noisy datasets best. What's new in our approach is that we also extract features from listing text — something the literature shows adds 10 to 44 percent improvement."

### Clarification Notes
- **Hedonic Regression**: A statistical method that decomposes property price into contributions from individual features (size, location, etc.). "Hedonic" = relating to pleasure/desirability — each feature adds or subtracts value. Originated from Rosen (1974).
- **Supervised Learning**: The model learns from labeled examples (properties with known prices) to predict prices for new properties.
- **Text-derived features**: Instead of ignoring listing descriptions, we convert text into numerical features the model can use (e.g., presence of "corner lot" or "flood-free").

---

## SLIDE 3: Data Sources — Hybrid Strategy (~2 min)

### Headline
**"Floor Price + Ceiling Price + Macro Context = Full Picture"**

### Content

| Source                                    | Role                     | Volume                 | Nature                    |
| ----------------------------------------- | ------------------------ | ---------------------- | ------------------------- |
| **BDO Foreclosures**                      | Verified Floor Price     | 955 raw → ~80-100 Cebu | Conservative / Distressed |
| **Online Listings** (Lamudi, DotProperty) | Market Ceiling Price     | Target: 500+           | Asking / Speculative      |
| **BIR Zonal Values**                      | Administrative Benchmark | Per barangay           | Static / Regulatory       |
| **BSP RPPI**                              | Time-trend Control       | Quarterly index        | Macro / Cyclical          |

### Why Hybrid?
> **"Actual Deed of Sale data is private and inaccessible."**
> — Online listing data can effectively segment housing markets and capture pricing clusters that sparse official records miss (Spatial Segmentation study, 2024).

### Validation Layer: Human-in-the-Loop
- Licensed real estate brokers (CPRE network)
- **Role 1**: Validate outliers ("Why is this Lahug property so cheap?")
- **Role 2**: Domain sanity check on key drivers vs. brokerage experience

### Speaker Notes
> "We don't have access to actual sale prices — that's a Data Privacy constraint. So we use a hybrid approach: BDO foreclosures as a conservative floor, and Lamudi listings as a market ceiling. True market value lies between. The spatial segmentation study validated this aggregation approach using online listings. And to keep us grounded, real brokers will review our outliers."

### Clarification Notes
- **BDO Foreclosures**: Properties repossessed by BDO bank due to unpaid mortgages. Sold at below-market prices ("distressed") → acts as a price **floor**.
- **Online Listings (Lamudi/DotProperty)**: Asking prices posted by sellers/agents. Typically above actual sale price → acts as a price **ceiling**.
- **BIR Zonal Values**: Bureau of Internal Revenue-assigned land values per zone, used for tax computation. Often outdated and lower than market (Domingo & Fulleros, 2005 documented this gap).
- **BSP RPPI**: Bangko Sentral ng Pilipinas Residential Property Price Index — a quarterly index tracking residential property prices (AONCR = Areas Outside NCR).
- **CPRE**: Certified Philippine Real Estate (practitioners) — the professional network of licensed brokers.
- **Role 1 (Outlier Validation)**: When the model flags a property with an unusual price (e.g., suspiciously cheap for Lahug), a broker reviews it to determine if it's a data error, an actual distressed sale, or a genuine anomaly.
- **Role 2 (Domain Sanity Check)**: Brokers compare the model's top feature drivers (from SHAP analysis) against their real-world experience — e.g., "Does it make sense that proximity to IT Park is the #1 price driver in this barangay?"
- **Human-in-the-Loop**: A design principle where human experts review and validate automated outputs before they are treated as final — required by IVS 2025.

---

## SLIDE 4: Data Pipeline — Gathering Procedures (~2 min)

### Headline
**"From Raw Excel to Model-Ready Features"**

### Content — Pipeline Flowchart
```
┌────────────┐    ┌──────────┐    ┌────────────┐    ┌───────────────┐    ┌───────────┐
│ 1. INGEST  │ →  │ 2. FILTER│ →  │ 3. PARSE   │ →  │ 4. GEOCODE    │ →  │ 5. AUGMENT│
│ BDO Excel  │    │ Cebu only│    │ Regex: BR, │    │ Address →     │    │ Distances,│
│ + Scrape   │    │ Residntl │    │ T&B, Pkg   │    │ Lat/Lon +     │    │ Amenity   │
│ Lamudi     │    │          │    │            │    │ Barangay      │    │ Scores,   │
│            │    │          │    │            │    │               │    │ Text Feat.│
└────────────┘    └──────────┘    └────────────┘    └───────────────┘    └───────────┘
```

### Step Details
1. **Ingestion**: BDO Excel + Lamudi web scraping into Python (Pandas)
2. **Filtering**: Residential only → Metro Cebu (Cebu City, Mandaue, Lapu-Lapu, Talisay, Minglanilla, Consolacion)
3. **Parsing**: Regex extraction from `Property Description` text field
   - Bedrooms (BR), Bathrooms (T&B), Parking/Garage
4. **Geocoding**: Google Maps API / OpenStreetMap (Nominatim) → Lat/Lon + Barangay assignment
5. **Augmentation**: Feature engineering — proximity, amenity scores, **text features** (next slide)

### Tools
| Step            | Tool                                           |
| --------------- | ---------------------------------------------- |
| Data Processing | `Python`, `Pandas`                             |
| Geocoding       | Google Maps API / OSM Nominatim                |
| NLP / Text      | `Scikit-learn` (TF-IDF), `Transformers` (BERT) |
| Modeling        | `Scikit-learn`, `XGBoost`                      |
| Dashboard       | `Streamlit`                                    |

### Speaker Notes
> "This slide shows our computational pipeline. The key challenge is parsing — BDO's descriptions are messy text like '3BR/2TB H&L with carport'. We use Regular Expressions to extract structured numbers from that. After parsing, we geocode addresses to get coordinates and barangay names, which unlock all our spatial features. Step 5 now also includes text feature extraction, which I'll explain next."

### Clarification Notes
- **Regex (Regular Expressions)**: Pattern-matching rules for text. E.g., the pattern `(\d+)\s*BR` finds "3" in "3BR townhouse". Used to extract bedroom/bathroom counts from messy descriptions.
- **Geocoding**: Converting a street address ("123 Salinas Drive, Lahug") into geographic coordinates (lat: 10.3157, lon: 123.8854). Enables distance calculations.
- **Web Scraping**: Automated extraction of data from websites (Lamudi, DotProperty). Uses Python libraries like BeautifulSoup or Scrapy.
- **Pandas**: The standard Python library for tabular data manipulation — think of it as a programmable Excel.

---

## SLIDE 5: Feature Engineering (~2 min)

### Headline
**"Turning raw attributes into predictive features — including text"**

### Feature Categories

| Category            | Features                                                          | Source              |
| ------------------- | ----------------------------------------------------------------- | ------------------- |
| **Structural**      | Lot Area, Floor Area, Bedrooms, Bathrooms, Parking, Property Type | BDO / Lamudi        |
| **Locational**      | Barangay, Lat/Lon coordinates                                     | Geocoding           |
| **Proximity**       | Distance to Ayala, IT Park, SM Seaside, Mactan Airport            | Haversine formula   |
| **Text Features** ⭐ | Keywords, TF-IDF vectors, or BERT embeddings from descriptions    | NLP Pipeline        |
| **Amenity Score**   | Count of schools, hospitals, commercial within 1km radius         | OSM / Google Places |
| **Administrative**  | BIR Zonal Value per barangay                                      | BIR schedules       |
| **Macro**           | BSP RPPI quarterly index (AONCR)                                  | BSP data            |

### Text Feature Extraction (Core) 🔑

Listing descriptions contain value signals that structured data misses:
- *"corner lot with garden, near park"* → location premium
- *"newly renovated, modern kitchen"* → condition premium
- *"flood-free zone"* → risk reduction

**Approach** (progressive, based on data volume):

| Method                          | When                       | Expected Impact                      |
| ------------------------------- | -------------------------- | ------------------------------------ |
| **TF-IDF / Keyword Features**   | Baseline (any sample size) | Captures key terms                   |
| **Pre-trained BERT Embeddings** | If descriptions are rich   | 10–15% MAE reduction (Seattle study) |
| **Self-trained Word2Vec**       | If n > 5,000 listings      | R² ~0.79 (Ottawa study)              |

### Engineered Variables
- **Price per sqm** = Price ÷ Lot Area
- **Valuation Gap** = Advertised Price − BIR Zonal Value
- **Log(Price)** — target transformation for skewness

### Speaker Notes
> "Feature engineering is where our model differs from existing Cebu studies. We're not just using structured data — we're also extracting information from the text descriptions. The Ottawa study showed that self-trained Word2Vec embeddings on listing text improved R-squared to 0.79. The Seattle study showed BERT embeddings reduced MAE by 11 percent. We start simple with TF-IDF keywords, then test BERT if text quality allows. This follows through on what we identified in the RRL — that text features are an underexploited signal in property valuation."

### Clarification Notes
- **TF-IDF (Term Frequency-Inverse Document Frequency)**: A simple NLP technique that scores how important a word is to a document relative to all documents. "Corner lot" appearing frequently in one listing but rarely across all listings gets a high score. No AI model needed — just statistics.
- **BERT (Bidirectional Encoder Representations from Transformers)**: A pre-trained language model by Google that understands word meaning in context. "Bank" near "river" vs. "bank" near "loan" get different representations. We use it "frozen" — no retraining, just extract embeddings.
- **Word2Vec**: A technique that learns word meanings from patterns in a text corpus. Words used in similar contexts get similar numerical representations. "Self-trained" means we train it on our own Cebu listing corpus, so it learns local terms like "Lahug" or "corner lot".
- **Embeddings**: Numerical vector representations of text. A description like "3BR corner lot near Ayala" becomes a list of numbers (e.g., 768 dimensions for BERT) that captures its semantic meaning.
- **Haversine Formula**: Calculates the great-circle distance between two GPS coordinates. Used to compute "distance to IT Park" etc.
- **Valuation Gap**: The difference between what the market thinks a property is worth (listing price) and what the government values it at (BIR Zonal Value). A large gap suggests the zonal values are outdated.
- **Price per sqm**: Normalizes prices by area so a 200sqm lot and a 50sqm lot can be compared fairly.

---

## SLIDE 6: Pre-processing (~1 min)

### Headline
**"Clean data in, clean predictions out"**

### Steps
| Step                         | Method                                            | Rationale                                                                            |
| ---------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------ |
| **Outlier Detection**        | IQR Method                                        | Removes pricing anomalies / data entry errors without arbitrary cutoffs              |
| **Log Transformation**       | ln(Price)                                         | Normalizes right-skewed price distribution; reduces pull of ultra-expensive outliers |
| **Missing Value Imputation** | Barangay-level Median                             | Preserves local context (a missing Floor Area in Lahug ≠ in Talisay)                 |
| **Encoding**                 | One-Hot for categorical (Property Type, Barangay) | Required for regression models                                                       |
| **Text Pre-processing**      | Lowercase, stopword removal, tokenization         | Standard NLP pipeline before TF-IDF/BERT                                             |

### Visual Suggestion
> ![Price Distribution Comparison: Raw vs Log-Transformed](/Users/nicoestreba/.gemini/antigravity/brain/2cb28f12-96c5-4022-ac9e-96d6fbaa12f4/price_distribution_histogram_comparison_1771031882506.png)
> (Above: Side-by-side histogram showing how log transformation normalizes right-skewed property prices)

### Speaker Notes
> "Property prices are naturally right-skewed — a few luxury properties pull the tail. Log transformation normalizes this. For missing values, we impute using the barangay median, not the city-wide median, because a property in Lahug has a fundamentally different price profile than one in Talisay. For text, we do standard NLP cleaning — lowercase, remove stopwords, then tokenize for our feature extraction."

### Clarification Notes
- **IQR (Interquartile Range) Method**: A statistical method for outlier detection. Calculates Q1 (25th percentile) and Q3 (75th percentile), then flags anything below Q1−1.5×IQR or above Q3+1.5×IQR as an outlier. More robust than arbitrary cutoffs.
- **Log Transformation**: Taking the natural logarithm of price. If prices range from ₱500K to ₱50M, ln(prices) compresses this to ~13 to ~18. Makes the distribution more symmetric, which helps regression models perform better.
- **Right-skewed**: Most properties cluster at lower prices, with a long tail of expensive properties pulling the mean upward. The median is a more accurate "typical" price than the mean.
- **Imputation**: Filling in missing values. If a listing doesn't mention floor area, we estimate it using the median floor area of other properties in the same barangay.
- **One-Hot Encoding**: Converting categories (e.g., "Condominium", "House & Lot", "Townhouse") into binary columns. The model sees [1,0,0] for Condo, [0,1,0] for H&L, etc.
- **Stopword Removal**: Removing common words ("the", "is", "a") that don't carry useful meaning for NLP features.
- **Tokenization**: Splitting text into individual words or sub-words for analysis.

---

## SLIDE 7: Modeling Strategy (~2 min)

### Headline
**"Three models, one question: Which explains Metro Cebu's prices best?"**

### The Three Architectures

| #   | Model                                    | Type                | Strength                                          | Weakness                 |
| --- | ---------------------------------------- | ------------------- | ------------------------------------------------- | ------------------------ |
| 1   | **Multiple Linear Regression** (Hedonic) | Parametric          | Interpretable; coefficients have economic meaning | Assumes linearity        |
| 2   | **Random Forest**                        | Ensemble (Bagging)  | Handles non-linearities; robust to overfitting    | Less interpretable       |
| 3   | **XGBoost**                              | Ensemble (Boosting) | Best predictive performance on tabular data       | Hyperparameter-sensitive |

### Hedonic Equation
$$\ln(Price) = \alpha + \beta_1 \ln(Area) + \beta_2(Bedrooms) + \beta_3(Dist_{CBD}) + \beta_4(ZonalValue) + \beta_5(TextFeatures) + \epsilon$$

### Hyperparameter Tuning
- **GridSearchCV** with K-Fold Cross Validation
- Parameters: `n_estimators`, `max_depth`, `learning_rate` (XGBoost)

### Why These Three?
> Literature (Nyanda et al., Tanzania, 2024): Tree-based models achieved **48.0% MAPE** (Boosting/XGBoost) and **52.7% MAPE** (Random Forest) vs. Neural Network's **108.6% MAPE** (failed) on comparable sample size (~954 obs). Our BDO dataset is ~955 — same ballpark.

### Exploratory Extension: Hybrid LLM + ML Approach
> **Core idea**: Use listing text as a *feature source* — not a replacement for structured data.

```
[Listing Text] → [Embeddings] → [XGBoost/RF] → [Price]
                                       ↑
                          + structured features (sqm, location, etc.)
```

| Tier              | Method                    | When to Use                             | Expected Impact      | Evidence                    |
| ----------------- | ------------------------- | --------------------------------------- | -------------------- | --------------------------- |
| **1 (Default)**   | TF-IDF keywords           | Any sample size                         | Baseline text signal | Standard NLP                |
| **2 (If n > 5K)** | Self-trained Word2Vec     | 5,000+ listings with descriptions       | R² ~0.79             | Ottawa study (Zhang et al.) |
| **3 (Fallback)**  | Pre-trained BERT (frozen) | Any sample size; mixed Filipino/English | 10–15% MAE reduction | Seattle + Malaysia studies  |

> **Key finding from literature**: Self-trained Word2Vec **outperformed pre-trained BERT by 44%** in real estate domain (Ottawa, n=10K). 8 papers reviewed — text features improve accuracy by **10–26%** across all studies.

### Other Stretch Goals (If Time Permits)
- **CBRT Proximity** — Haversine distance to planned BRT stations (infrastructure premium)
- **Bayesian Uncertainty** — Credible intervals instead of point estimates (₱4.2M–₱5.1M)
- **Streamlit Dashboard** — Interactive valuation tool for brokers/CPRE

> *All exploratory extensions pursued only after core OLS/RF/XGBoost pipeline is validated.*

### Speaker Notes
> "We chose these three because they span the interpretability-accuracy spectrum. OLS gives us economic intuition — each coefficient tells us 'a 1% increase in area raises price by β%'. Random Forest and XGBoost capture the non-linear interactions that hedonic models miss, like how location value depends on lot size. The Tanzania study, with a similar 954-observation dataset, confirms tree-based models are the right choice over neural networks. Beyond the core three models, we're exploring a hybrid LLM approach — using listing text as feature input rather than replacing structured data. The Ottawa study showed self-trained Word2Vec embeddings on listing text achieved R-squared of 0.79, outperforming pre-trained BERT by 44%. We start with TF-IDF, then scale to Word2Vec if we get 5,000+ listings. This is our key methodological innovation for Cebu."

### Clarification Notes
- **OLS (Ordinary Least Squares)**: The classic regression method. Finds the best-fit line that minimizes the sum of squared errors. Each coefficient (β) tells you exactly how much one unit of change in a feature affects price.
- **Random Forest (Bagging)**: Creates many decision trees, each trained on a random subset of data, then averages their predictions. "Bagging" = Bootstrap Aggregating. Robust because individual tree errors cancel out.
- **XGBoost (Boosting)**: Creates trees sequentially — each new tree focuses on correcting the errors of previous trees. Typically the best-performing algorithm for structured/tabular data.
- **Bagging vs. Boosting**: Bagging trains trees independently and averages (reduces variance). Boosting trains trees sequentially, each fixing prior mistakes (reduces bias). Boosting generally wins on accuracy but is more prone to overfitting.
- **Hyperparameter Tuning**: Model settings (e.g., number of trees, tree depth, learning rate) that aren't learned from data — we search for the best combination using GridSearchCV.
- **GridSearchCV**: Exhaustively tests all combinations of hyperparameters using cross-validation, then selects the best-performing set.
- **Non-linear interactions**: When the effect of one feature depends on another. E.g., a large lot in Lahug is worth disproportionately more than a large lot in a rural barangay — the value of lot size *interacts* with location.

---

## SLIDE 8: Evaluation, Explainability & Benchmarks (~1.5 min)

### Headline
**"Making our model transparent — and measuring it against the literature"**

### Explainability: SHAP Values (Primary Focus)
- **Why SHAP?** IVS 2025 requires AVM transparency — "no model without professional judgement can produce an IVS-compliant valuation"
- **Global Feature Importance**: Which factors drive Metro Cebu property prices most?
  - Expected: Lot Area, Proximity to CBD, Barangay, Zonal Value
- **Force Plots**: Explain *individual* predictions
  - e.g., "This Lahug condo is +₱1.2M due to IT Park proximity, −₱300K due to small floor area"
- **NLP Feature Attribution**: How much do text-derived features (TF-IDF/BERT) improve predictions vs. structured-only models?

### Target Benchmarks (from Literature)
| Study                          | Context                                                   | Best MAPE | Our Target   | Why This Target?                                                                                                                          |
| ------------------------------ | --------------------------------------------------------- | --------- | ------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Ramolete et al. (PH, 2023)     | Cavite & NCR; Lamudi; AdaBoost/XGBoost; segmented markets | 10.7–21%  | **< 25%**    | They had larger, cleaner NCR data + market segmentation (87.5% benefited). Metro Cebu has fewer listings and no prior segmentation study. |
| Nyanda et al. (Tanzania, 2024) | Dar es Salaam; 954 obs; Boosting                          | 48.0%     | **Beat 48%** | Comparable sample size (~955 BDO obs), but we add NLP features + online listings they didn't have.                                        |

### Validation Scheme
| Method                          | Description                                                   |
| ------------------------------- | ------------------------------------------------------------- |
| **K-Fold CV** (k=5 or 10)       | Robust performance across data splits                         |
| **Time-Aware Split** (optional) | Train on older listings, test on newer — simulates deployment |

### Key Metrics (Slide Footnote)
> **MAPE** — primary metric (cross-study comparison) | **R²** — "model explains X% of price variation"
> *(MAE reported for broker communication: "off by ₱X on average")*

### Speaker Notes
> "The core of this slide is explainability. SHAP values make our ML models IVS-compliant — instead of a black box, we can tell CPRE *exactly* why the model priced a property at ₱5M. The Ramolete study achieved 10.7–21% MAPE in Cavite and Metro Manila, but they had larger datasets from Lamudi and used market segmentation that boosted 87.5% of predictions. We set a conservative <25% target because Metro Cebu has fewer listings and no prior ML study to build on. For Tanzania, Nyanda's 48% MAPE came from a similar 954-observation dataset — we should beat this because we're adding NLP features and online listing data that they didn't use."

### Clarification Notes
- **SHAP (SHapley Additive exPlanations)**: A game-theory-based method that assigns each feature a contribution to each individual prediction. Named after Lloyd Shapley (Nobel Economics, 2012).
- **SHAP Force Plot**: A visual showing how each feature pushes a specific prediction higher or lower from the average. E.g., "IT Park proximity pushes this prediction +₱1.2M, but small floor area pushes it −₱300K."
- **IVS 2025 (International Valuation Standards)**: The global standard for property valuation, effective Jan 31, 2025. Key requirement: AVMs must be transparent and paired with professional judgement.
- **AVM (Automated Valuation Model)**: Any computational model that estimates property value without physical inspection.
- **MAPE (Mean Absolute Percentage Error)**: |actual − predicted| / actual × 100, averaged. Allows cross-study comparison regardless of currency.
- **R² (Coefficient of Determination)**: Proportion of price variation explained by the model. R²=0.80 means 80% explained.
- **K-Fold Cross Validation**: Splits data into K parts, trains on K−1, tests on 1. Repeats K times. Prevents lucky splits.
- **Market Segmentation**: Ramolete clustered properties into sub-markets before modeling. This improved accuracy for 87.5% of properties. We may attempt this if Metro Cebu data supports meaningful clusters.

---

## SLIDE 9: Empirical Framework (~1 min)

### Headline
**"Connecting the dots: Variables → Models → Output"**

### Framework Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                    INDEPENDENT VARIABLES                         │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐  ┌──────────┐     │
│  │Structural│  │Locational│  │  Proximity  │  │   Macro  │     │
│  │• Lot Area│  │• Barangay│  │• Dist to CBD│  │• RPPI    │     │
│  │• Floor   │  │• Lat/Lon │  │• Amenity Scr│  │• Zonal   │     │
│  │• BR/TB   │  │          │  │             │  │  Value   │     │
│  └────┬─────┘  └────┬─────┘  └──────┬──────┘  └────┬─────┘     │
│       │              │               │              │           │
│  ┌────┴──────────────┴───────────────┴──────────────┘           │
│  │  ┌────────────────────────────────────────────────────────┐  │
│  │  │ TEXT FEATURES (NLP)                                     │  │
│  │  │ Listing Descriptions → TF-IDF / BERT → Feature Vectors │  │
│  │  └──────────────────────────┬─────────────────────────────┘  │
│  └─────────────────────────────┤                                │
│                                ↓                                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              MODELING ENGINE                               │  │
│  │   Hedonic OLS  │  Random Forest  │  XGBoost               │  │
│  │   (Baseline)   │  (Non-linear)   │  (Best predictor)      │  │
│  └───────────────────────┬───────────────────────────────────┘  │
│                          ↓                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              OUTPUT                                        │  │
│  │   Predicted Price  │  Feature Importance  │  SHAP          │  │
│  │   + Valuation Gap  │  Rankings            │  Force Plot    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         HUMAN-IN-THE-LOOP VALIDATION                       │  │
│  │   Broker Review  │  Outlier Flagging  │  IVS Compliance    │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Exploratory Extensions (Brief Mention)
> Beyond the core pipeline, we are exploring:
> - **Future Factors**: Distance to planned CBRT stations (not yet built)
> - **Bayesian Uncertainty**: Credible intervals instead of point estimates
> - **Streamlit Dashboard**: Interactive tool for CPRE end-users

### Speaker Notes
> "This framework summarizes the full pipeline. Four categories of structured features plus our NLP text features feed into three competing models. The models output predicted prices, feature importance rankings, and SHAP explanations. Critically, the final layer is human validation — brokers review outliers and confirm the model's drivers match reality. This is our response to IVS 2025's requirement that AVMs cannot stand alone. We're also exploring some extensions — BRT proximity effects and Bayesian confidence intervals — but those are stretch goals beyond the core methodology."

### Clarification Notes
- **CBRT (Cebu Bus Rapid Transit)**: A proposed mass transit system for Metro Cebu. Testing whether proximity to *planned* (not yet built) stations is already reflected in current property prices.
- **Bayesian Uncertainty / Credible Intervals**: Instead of giving a single point estimate ("₱5M"), giving a probability range ("95% chance the fair price is between ₱4.5M and ₱5.5M"). More useful for decision-making than a single number.
- **Streamlit**: A Python framework for building interactive web dashboards. Would allow CPRE brokers to input property details and get a real-time valuation estimate with SHAP explanations.

---

## SLIDE 10: Research Project Plan (~1 min)

### Headline
**"From here to Final Defense: The Roadmap"**

### Gantt Chart / Timeline

| Phase                   | Activity                                         | Timeline        |
| ----------------------- | ------------------------------------------------ | --------------- |
| **Phase 1: Data**       | Data collection (Lamudi scraping) + BDO cleaning | Feb 14 – Feb 28 |
| **Phase 2: Proposal**   | Submit written Project Proposal to panelists     | Feb 18          |
| ^                       | Panel Presentation: Research Project Proposal    | Feb 21          |
| ^                       | Submit revised proposal                          | Feb 28          |
| **Phase 3: Build**      | Feature engineering + Geocoding + NLP pipeline   | Mar 1 – Mar 14  |
| ^                       | Model training + hyperparameter tuning           | Mar 15 – Mar 28 |
| **Phase 4: Colloquium** | Research Project Updates presentation            | Mar 28          |
| **Phase 5: Evaluate**   | SHAP analysis + Broker validation sessions       | Apr 1 – Apr 18  |
| ^                       | Streamlit dashboard prototype                    | Apr 11 – Apr 25 |
| **Phase 6: Write**      | Draft final research paper (Chapters 4-10)       | Apr 18 – May 2  |
| ^                       | Initial submission to panelists                  | Apr 25          |
| **Phase 7: Defend**     | Panel Presentation: Final Research Paper         | May 9           |
| ^                       | Final Submission                                 | May 23          |

### Key Milestones
- ✅ **Done**: Project Concept (Jan 24), Literature Review (Feb 7), Methodology (Feb 14)
- 🔜 **Next**: Written Proposal (Feb 18) → Panel Presentation (Feb 21)
- 🎯 **Final**: Paper submission (Apr 25) → Defense (May 9)

### Speaker Notes
> "Here's our full project roadmap aligned with the course schedule. The immediate next step is submitting our written proposal on February 18, followed by the panel presentation on February 21. The core development happens in March — data pipeline, NLP features, and modeling. April is for evaluation, the dashboard prototype, and writing. We defend on May 9."

---

## Appendix: Paper-to-Slide Continuity Map

| Presentation                  | Key Takeaway                                         | Carried Forward                       |
| ----------------------------- | ---------------------------------------------------- | ------------------------------------- |
| **Project Concept** (Slide 8) | Methodology overview: Regex → Feature Eng → 3 Models | Expanded into Slides 4-7 here         |
| **RRL** (Slide 5)             | Tree-based ML beats NN on ~950 obs (Tanzania)        | Justifies model choice in Slide 7     |
| **RRL** (Slide 6)             | Text features boost accuracy 10-44% (8 papers)       | **NEW**: Text features now in Slide 5 |
| **RRL** (Slide 9)             | "No Cebu-specific predictive ML model exists"        | Motivates entire methodology          |
| **RRL** (Slide 8)             | IVS 2025: Human oversight required                   | Human-in-the-Loop in Slides 3 & 9     |
| **RRL** (Slides 2-3)          | Data scarcity is the core problem                    | Hybrid data strategy in Slide 3       |

---

## Appendix: Q&A Preparation

### Likely Questions & Prepared Answers

**Q: Why not use neural networks?**
> Tanzania study (Nyanda et al.): NN achieved 108.6% MAPE on n=954, while XGBoost achieved 48%. Our BDO dataset is ~955 observations — same ballpark. Tree-based models are the safer bet.

**Q: How do you handle mixed Filipino/English listing text?**
> Two options: (1) Multilingual BERT handles code-switching natively, or (2) TF-IDF is language-agnostic for keyword extraction. We start with TF-IDF and test multilingual BERT if text quality is sufficient.

**Q: Is BDO foreclosure data representative of market prices?**
> No — it's a floor price (distressed sales). That's exactly why we use hybrid data. BDO gives us a conservative anchor; Lamudi gives us a ceiling. The true value lies between, and brokers help us calibrate.

**Q: What if you don't get enough Lamudi listings?**
> The methodology scales. With <500 listings, we use TF-IDF keywords only. With 1,000+, we can test BERT embeddings. The 3-model comparison works regardless of NLP complexity.

**Q: How is this different from Agosto's study?**
> Agosto (2020) used a survey of 52 practitioners and factor analysis. Our approach uses actual transaction/listing data, machine learning, and text-derived features. To our knowledge, no existing study applies predictive ML modeling to property-level transaction data in Cebu.
