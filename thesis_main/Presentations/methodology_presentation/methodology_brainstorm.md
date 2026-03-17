# Methodology Brainstorm

> **Thesis**: Data-Driven Property Valuation Model for Cebu City  
> **Context**: Preparing Methodology Presentation (10 slides, 15 min) — Feb 14, 2026  
> **Goal**: Solidify the methodology *before* writing the slides  
> **Status**: Working Draft

---

## 1. What We Promised in the RRL (Feb 7)

The RRL presentation (Slide 9: Synthesis) made specific claims that our methodology **must deliver on**:

| RRL Promise                                                                | Status            | Where           |
| -------------------------------------------------------------------------- | ----------------- | --------------- |
| "No Cebu-specific, transaction-based, ML-augmented model exists"           | ⚠️ Needs softening | See §2          |
| First Cebu model using actual transaction data                             | ✅ Core            | Data Sources    |
| Hybrid: BDO foreclosures (floor) + Lamudi (ceiling) + broker consultations | ✅ Core            | Data Sources    |
| SHAP interpretability for IVS compliance                                   | ✅ Core            | Evaluation      |
| Tree-based ML (RF/XGBoost) > NN on small data (Tanzania, n=954)            | ✅ Core            | Model Selection |
| Text features add 10-44% accuracy (Ottawa, Melbourne, Seattle, Shanghai)   | ⚠️ NOW CORE        | NLP Pipeline    |

---

## 2. Addressing Professor Feedback: Agosto Claim

### The Problem
Professor challenged: "Are we sure Agosto is the only Cebu-specific study?"

### Research Findings
Other Cebu real estate studies exist, but none apply predictive modeling:

| Study                                                         | Year   | Approach                      | Why it's different                     |
| ------------------------------------------------------------- | ------ | ----------------------------- | -------------------------------------- |
| Sajor — "Globalization and Urban Property Boom in Metro Cebu" | 2003   | Qualitative political economy | No valuation model; macro-sociological |
| Informal Land Market in Cebu City                             | ~2000s | Household interviews          | Qualitative; no price prediction       |
| Cebu City RPT Revision (LFC/Assessor)                         | 2023   | Administrative schedules      | Policy, not ML or regression           |
| Cebu Chamber Presentation (Agosto)                            | 2022   | Policy analysis               | Same author, no new empirical model    |

### Recommended Language
> "To our knowledge and through our review, we have yet to find a study that implements quantitative predictive modeling to property-level transaction data in Cebu City."

This is **specific and defensible** — it scopes the gap to *predictive modeling on transaction data*, not "any Cebu study."

---

## 3. Core Methodology Components (Must Deliver)

### 3.1 Research Design
- **Design**: Quantitative, Predictive Modeling
- **Approach**: Supervised Learning (Regression)
- **Comparison Framework**: Interpretability ←→ Accuracy spectrum

### 3.2 Three-Model Comparison

| #   | Model                      | Type                | Strength                                       | Literature Justification                      |
| --- | -------------------------- | ------------------- | ---------------------------------------------- | --------------------------------------------- |
| 1   | **Hedonic OLS** (Baseline) | Parametric          | Interpretable; coefficients = economic meaning | Standard in RE valuation (Agosto, Rosen 1974) |
| 2   | **Random Forest**          | Ensemble (Bagging)  | Non-linear; robust to overfitting              | Tanzania (Nyanda): 52% MAPE on n=954          |
| 3   | **XGBoost**                | Ensemble (Boosting) | Best tabular performance                       | Tanzania: 48% MAPE (best); Boosting beat all  |

**Why not Neural Networks?** Tanzania study: NN achieved 108.6% MAPE (failed) on comparable sample size.

### 3.3 Hybrid Data Strategy

```
┌──────────────────────────────────────────────────────────────────────┐
│                     DATA LANDSCAPE                                   │
│                                                                      │
│   CEILING (Market Ask)          TRUE VALUE           FLOOR (Distress)│
│   ┌──────────────┐          ┌──────────────┐     ┌──────────────┐   │
│   │ Lamudi /      │          │   Unknown    │     │ BDO          │   │
│   │ DotProperty   │   ???    │   (Deed of   │     │ Foreclosures │   │
│   │ Online        │◄────────►│   Sale is    │◄───►│ 955 raw      │   │
│   │ Listings      │          │   private)   │     │ → ~80-100    │   │
│   │ Target: 500+  │          │              │     │ Cebu entries │   │
│   └──────────────┘          └──────────────┘     └──────────────┘   │
│                                    ↑                                 │
│                    ┌───────────────┴────────────────┐                │
│                    │  ADMINISTRATIVE / MACRO ANCHORS │                │
│                    │  • BIR Zonal Values (per brgy)  │                │
│                    │  • BSP RPPI (quarterly index)   │                │
│                    └────────────────────────────────┘                │
└──────────────────────────────────────────────────────────────────────┘
```

**Why hybrid?** Deed of Sale data is private (Data Privacy Act). Sousa et al. (2024) validated that aggregating online listings captures pricing clusters that sparse official records miss.

### 3.4 Feature Engineering

| Category             | Features                                             | Source            | Literature Support                            |
| -------------------- | ---------------------------------------------------- | ----------------- | --------------------------------------------- |
| **Structural**       | Lot Area, Floor Area, BR, TB, Parking, Property Type | BDO/Lamudi        | Agosto (31 factors), all hedonic models       |
| **Locational**       | Barangay, Lat/Lon                                    | Geocoding         | Tanzania #13, Kenya #02                       |
| **Proximity**        | Distance to CBD, IT Park, SM Seaside, Airport        | Haversine         | Access variables top-ranked (Tanzania, Kenya) |
| **Administrative**   | BIR Zonal Value, Valuation Gap                       | BIR Schedules     | Lagos #38 (admin-market disconnect)           |
| **Macro**            | BSP RPPI quarterly index                             | BSP Data          | Nigeria #20 (exchange rate r=-0.925)          |
| **Future Factors** ⭐ | Distance to planned CBRT stations                    | BRT Master Plan   | Novel — no existing Cebu study tests this     |
| **Amenity Score**    | Count of schools, hospitals, commercial within 1km   | OSM/Google Places | Standard in hedonic lit                       |
| **Text Features** ⭐  | Embeddings from listing descriptions                 | NLP pipeline      | Ottawa (R²=0.79), Seattle (11% MAE↓)          |

### 3.5 Text Feature Extraction (NEW — Core) 🔑

This is the key addition that wasn't in the original Chapter 3 but was promised by the RRL.

#### The Problem
Listing descriptions contain valuable signal that structured features miss:
- *"corner lot with garden, near a park"* → location premium
- *"newly renovated, modern kitchen"* → condition premium
- *"flood-free zone"* → risk reduction

#### Literature Evidence

| Paper            | Method                      | Result                                     |
| ---------------- | --------------------------- | ------------------------------------------ |
| Ottawa (2023)    | Self-trained Word2Vec + DNN | R² = 0.79 (44% better than BERT)           |
| Melbourne (2024) | SBERT + CLIP + LightGBM     | 26% MAE improvement                        |
| Seattle (2023)   | BERT + XGBoost stacking     | 11% MAE reduction                          |
| Shanghai (2024)  | ChatGPT 10-shot prompting   | R² = 0.80                                  |
| UConn (Atlanta)  | Paragraph Vector + Hedonic  | 5.6% price premium for unique descriptions |
| Malaysia         | BERT Sentiment + ARIMA/LSTM | 20% accuracy improvement                   |

#### Approach for Cebu (Decision Required)

Based on `.context/roadmap_llm_embeddings.md`, three options in ranked order:

**Option A: TF-IDF / Keyword Features (Simple, Safe)**
- Extract keyword presence: "corner lot", "flood-free", "renovated", "near school"
- Binary or count-based features fed into XGBoost
- Pros: No embedding training needed, interpretable, works with any sample size
- Cons: Misses semantic meaning

**Option B: Pre-trained BERT Embeddings (Moderate)**
- Use frozen multilingual BERT (handles Filipino/English mix)
- Extract 768-dim embeddings → PCA → top-N components as features
- Pros: Works with any sample size, captures semantics
- Cons: May miss Cebuano vocabulary; BERT is large

**Option C: Self-trained Word2Vec (Best if data permits)**  
- Train Word2Vec on Cebu listing corpus
- Requires: ~5,000+ listings with descriptions
- Pros: Domain-specific, best R² (0.79 per Ottawa)
- Cons: Need enough text data

**Proposed Strategy**: **Start with Option A (TF-IDF), test Option B (BERT) as enhancement.**  
If we scrape enough Lamudi data (5K+), extend to Option C (Word2Vec).

#### Language Consideration
- Cebu listings: Mixed Filipino/English/Cebuano
- Multilingual BERT (Malaysia paper approach) handles this
- Or: normalize text to English before embedding

### 3.6 Pre-processing

| Step                     | Method                                    | Rationale                                           |
| ------------------------ | ----------------------------------------- | --------------------------------------------------- |
| Outlier Detection        | IQR method                                | Removes pricing anomalies without arbitrary cutoffs |
| Log Transformation       | ln(Price)                                 | Normalizes right-skewed price distribution          |
| Missing Value Imputation | Barangay-level Median                     | Preserves local context                             |
| Encoding                 | One-Hot (Property Type, Barangay)         | Required for regression                             |
| Text Pre-processing      | Lowercase, stopword removal, tokenization | Standard NLP pipeline                               |

### 3.7 SHAP Values & IVS Compliance

- **SHAP Feature Importance**: Which factors drive Cebu property prices?
- **SHAP Force Plots**: Explain *individual* predictions
  - e.g., "This Lahug condo is +₱1.2M due to IT Park proximity, −₱300K due to small floor area"
- **IVS 2025 Alignment**: "No model without professional judgement can produce an IVS-compliant valuation"
  - Our response: Human-in-the-Loop validation by licensed brokers (CPRE)

### 3.8 Validation

| Method                              | Description                            |
| ----------------------------------- | -------------------------------------- |
| K-Fold Cross Validation (k=5 or 10) | Robust performance across data splits  |
| Time-Aware Split (optional)         | Train on older listings, test on newer |

| Metric | Interpretation                 | Target (from Literature)      |
| ------ | ------------------------------ | ----------------------------- |
| MAE    | Average error in Pesos         | Business-friendly             |
| MAPE   | Average % error                | < 25% (beat Ramolete PH 2023) |
| RMSE   | Penalizes large errors         | Minimize                      |
| R²     | % of price variation explained | > 0.70 (match Ottawa)         |

---

## 4. Exploratory Goals (Mention Briefly in Presentation)

These are stretch goals — worth mentioning as "future work" or "exploratory" in the presentation:

| Goal                           | Description                                                | Literature Basis                                  | Feasibility                         |
| ------------------------------ | ---------------------------------------------------------- | ------------------------------------------------- | ----------------------------------- |
| **Satellite Imagery Features** | Building footprints, roof types from aerial/satellite data | Ghana (Gyekye 2025): 83% accuracy roof extraction | Needs labeled Cebu imagery          |
| **ChatGPT Feature Scoring**    | Use LLM to score listing quality, condition, etc.          | Shanghai (2024): R²=0.80 with 10-shot             | API cost; novel approach            |
| **Bayesian Uncertainty Layer** | Credible intervals instead of point estimates              | `.context/roadmap_bayesian_layer.md`              | Strong IVS alignment; scope concern |
| **Streamlit Dashboard**        | Interactive valuation tool for CPRE end-users              | Chapter 3 mentions Streamlit                      | Dev effort; timeline risk           |

---

## 5. Methodology Flow (Presentation Narrative)

```
How we go from "problem" to "answer":

    ┌──────────────────────────────────────────────────────────────────┐
    │  1. DATA COLLECTION                                              │
    │     BDO Foreclosures + Lamudi Scraping + BIR Zonal + BSP RPPI   │
    └──────────────────────┬───────────────────────────────────────────┘
                           ↓
    ┌──────────────────────────────────────────────────────────────────┐
    │  2. DATA PIPELINE (Python)                                       │
    │     Ingest → Filter (Cebu) → Parse (Regex) → Geocode → Augment  │
    └──────────────────────┬───────────────────────────────────────────┘
                           ↓
    ┌──────────────────────────────────────────────────────────────────┐
    │  3. FEATURE ENGINEERING                                          │
    │     Structural + Locational + Proximity + Admin + Macro          │
    │     + Future Factors (CBRT) + Amenity Score                      │
    │     + TEXT FEATURES (TF-IDF / BERT embeddings) ← NEW            │
    └──────────────────────┬───────────────────────────────────────────┘
                           ↓
    ┌──────────────────────────────────────────────────────────────────┐
    │  4. PRE-PROCESSING                                               │
    │     Outlier Detection → Log Transform → Imputation → Encoding   │
    └──────────────────────┬───────────────────────────────────────────┘
                           ↓
    ┌──────────────────────────────────────────────────────────────────┐
    │  5. MODELING (3-Model Comparison)                                 │
    │     Hedonic OLS (Baseline) vs Random Forest vs XGBoost           │
    │     + Text features as additional input to all models            │
    └──────────────────────┬───────────────────────────────────────────┘
                           ↓
    ┌──────────────────────────────────────────────────────────────────┐
    │  6. EVALUATION                                                    │
    │     MAE / MAPE / RMSE / R² + SHAP Values                        │
    │     K-Fold CV + Time-Aware Split                                 │
    └──────────────────────┬───────────────────────────────────────────┘
                           ↓
    ┌──────────────────────────────────────────────────────────────────┐
    │  7. HUMAN-IN-THE-LOOP VALIDATION                                 │
    │     Broker review (CPRE) + Outlier flagging + IVS compliance     │
    └──────────────────────────────────────────────────────────────────┘
```

---

## 6. Key Methodology Decisions Log

| Decision        | Choice                                                | Rationale                                                        | Date         |
| --------------- | ----------------------------------------------------- | ---------------------------------------------------------------- | ------------ |
| Model selection | OLS + RF + XGBoost (no NN)                            | Tanzania: NN failed (108% MAPE) on n=954                         | Jan 2026     |
| Data strategy   | Hybrid (BDO + Lamudi + BIR + BSP)                     | Deed of Sale is private; need floor + ceiling                    | Jan 2026     |
| Agosto claim    | Softened: "no predictive ML on Cebu transaction data" | Professor feedback; other Cebu studies exist but are qualitative | Feb 13, 2026 |
| Text features   | Core methodology (not exploratory)                    | RRL promised this; 8 papers support 10-44% improvement           | Feb 13, 2026 |
| Text approach   | Start TF-IDF → test BERT → Word2Vec if n>5K           | Pragmatic ramp-up based on data availability                     | Feb 13, 2026 |
| SHAP values     | Core (IVS compliance)                                 | IVS 2025: "no model without professional judgement"              | Jan 2026     |
| Bayesian layer  | Exploratory (mention only)                            | Strong rationale but scope concern                               | Feb 8, 2026  |

---

## 7. Open Questions for Presentation Prep

1. **Sample size for text features**: How many Lamudi listings can we realistically scrape by data collection deadline (Feb 28)?
   - If < 1,000: TF-IDF only
   - If 1,000–5,000: TF-IDF + frozen BERT
   - If > 5,000: Self-trained Word2Vec viable
2. **CBRT data source**: Where do we get the planned station locations? (BRT master plan PDF?)
3. **Broker validation**: How many CPRE brokers do we target? (3? 5?) And what's the protocol?
4. **Time-aware split feasibility**: Do we have enough temporal spread in BDO data for a meaningful time split?

---

*Created: 2026-02-13 | For methodology presentation preparation*
