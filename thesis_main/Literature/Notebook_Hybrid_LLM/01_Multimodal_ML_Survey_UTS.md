# Multimodal Machine Learning for Real Estate Appraisal: A Comprehensive Survey

**Source**: NotebookLM Direct Query (LLM Embeddings Research Notebook)

---

## Bibliographic Context

- **Title**: Multimodal Machine Learning for Real Estate Appraisal: A Comprehensive Survey
- **Authors**: Chenya Huang, Bin Liang, Zhidong Li, Fang Chen
- **Affiliation**: University of Technology Sydney, Sydney, Australia
- **Publication**: arXiv (2025)
- **Keywords**: #MultimodalML #RealEstateAppraisal #FusionTechniques #DeepLearning #HousingPricePrediction

---

## Abstract

> "Real estate appraisal has undergone a significant transition from manual to automated valuation and is entering a new phase of evolution. Leveraging comprehensive attention to various data sources, a novel approach to automated valuation, multimodal machine learning, has taken shape. This approach integrates multimodal data to deeply explore the diverse factors influencing housing prices. Furthermore, multimodal machine learning significantly outperforms single-modality or fewer-modality approaches in terms of prediction accuracy, with enhanced interpretability. However, systematic and comprehensive survey work on the application in the real estate domain is still lacking. In this survey, we aim to bridge this gap by reviewing the research efforts."

---

## Research Questions

The survey is organized around two core research questions:

1. **RQ 1: Model Performance** — Which models achieve the highest predictive accuracy?
2. **RQ 2: Modality Fusion** — How should different data modalities be combined effectively?

---

## Theoretical Framework: Five Modalities Taxonomy

The authors propose a comprehensive classification of real estate data into **five distinct modalities**:

### 1. Attributes Data
The inherent characteristics of a specific property.
- **Data Types**: Continuous (numerical) and categorical
- **Examples**: 
  - Number of bedrooms
  - Floor level
  - Area (size)
  - Location
  - Amenities (swimming pool, parking)
- **Note**: Property address is collected here but is distinct from "Textual" modality

### 2. Market Data
Information from real estate and broader financial/economic markets (time series format).
- **Data Types**: Real estate sales figures, financial indicators, economic metrics
- **Examples**:
  - Historical property sales data (transaction volumes, price trends)
  - Interest rates (deposit and loan)
  - Property tax rates
  - GDP growth rates
  - Rent-related data

### 3. Visual Data
Intuitive information about a property through images (not video).
- **Data Types**: Images processed through classification or feature extraction (vector transformation)
- **Examples**:
  - **Internal Views**: Photos of kitchens, bathrooms, bedrooms
  - **External Views**: Frontal view of house, street view
  - **Satellite Views**: Aerial/overhead imagery

### 4. Textual Data
Language-based information about properties.
- **Data Types**: Three categories identified:
  1. **Descriptive**: Direct descriptions of house characteristics (most common)
  2. **Promotional**: Marketing messages and rhetoric from advertisements
  3. **Sentiment/External**: News articles, blogs, reviews, comments affecting prices

### 5. GIS Data (Geographic Information System)
Captures "geographical dependence" and spatial factors.
- **Data Types**: Spatial coordinates, infrastructure data, demographics, satellite imagery
- **Examples**:
  - Basic Location: Latitude, longitude, regional names
  - Infrastructure: Transportation data, Points of Interest (POI)
  - Demographics/Environment: Population data, mobility maps, remote sensing
  - Calculated Metrics: Distances to transportation/POIs, facility counts

### Modality Usage Trends
- **Attributes** and **Market** data are foundational—present in nearly all studies from 2008-2024
- **Textual**, **Visual**, and **GIS** have grown since 2014 with deep learning maturity
- Before diverse data collection, heterogeneous tabular data (attributes + market) dominated

---

## Fusion Techniques Taxonomy

The survey categorizes fusion methods by **timing of integration**:

### 1. Early Fusion
- **Definition**: Raw data or extracted features from different modalities combined into unified representation **before** model input
- **Advantages**: Excels at capturing deep interactions between modalities
- **Disadvantages**: 
  - Performance suffers if single modality has low data quality
  - Can lead to "curse of dimensionality" with heterogeneous data

### 2. Late Fusion
- **Definition**: Each modality processed separately; individual predictions aggregated through weighted integration at **output level**
- **Advantages**: 
  - Highly robust—effective even if one modality has poor quality
  - Well-suited for tasks where modalities are strongly independent
- **Disadvantages**: Misses opportunity to capture deep feature interactions during learning

### 3. Hybrid Fusion
- **Definition**: Combines early and late fusion mechanisms; integrates data across **multiple levels** of the model
- **Advantages**: Addresses limitations of both methods by combining strengths
- **Disadvantages**: More complex to implement

### Effectiveness for Real Estate
- **No single "best" technique** — effectiveness depends on data characteristics
- **Early fusion** preferred when modalities complement each other (e.g., text explaining room attributes)
- **Late fusion** preferred when data quality varies or modalities are independent
- **Hybrid fusion** offers balanced approach for complex real estate tasks
- **Key finding**: Multimodal approaches (regardless of fusion type) outperform single-modality approaches

---

## Machine Learning Models Reviewed

### Traditional Machine Learning

| Model                   | Description                                            | Performance Notes                                                                |
| ----------------------- | ------------------------------------------------------ | -------------------------------------------------------------------------------- |
| **SVM**                 | Support Vector Machines (variants: SSELS-SVM, PSO-SVM) | One study found SVM "most successful" vs KNN and RF                              |
| **Random Forest**       | Ensemble method, widely used for mass appraisal        | Outperforms MLP, KNN, regression; struggles with nonlinear relationships vs DNNs |
| **XGBoost**             | Tree-based ensemble                                    | Significantly outperforms linear regression-based XGBoost; R² 0.45 vs 0.21       |
| **LitBoost / CatBoost** | Alternative boosting models                            | Reviewed alongside XGBoost                                                       |
| **Lasso Regression**    | Used for text regression tasks                         | Baseline comparison                                                              |
| **Linear Regression**   | Standard baseline                                      | Often outperformed by modern methods                                             |

### Deep Learning

| Model                           | Application                                 | Performance Notes                                                      |
| ------------------------------- | ------------------------------------------- | ---------------------------------------------------------------------- |
| **CNN**                         | Feature extraction from visual/textual data | Efficient but lacks interpretability for visual features               |
| **GNN (Graph Neural Networks)** | Spatial relationship modeling               | MugRep (GNN-based) achieved MAE 0.3244, superior to DNN, GBRT, SVR, LR |
| **RNN/LSTM**                    | Sequential data (market time series)        | Used for temporal patterns                                             |
| **Transformers**                | Cutting-edge framework (proposed 2017)      | Real estate still in "initial exploration phase"                       |
| **GAN**                         | Image generation for visual processing      | Emerging application                                                   |

### Performance Benchmarks

| Framework                    | MAE        | Comparison                                                  |
| ---------------------------- | ---------- | ----------------------------------------------------------- |
| **ST-RAP** (spatio-temporal) | **21.77**  | vs MugRep (35.46), ReGram (34.61), SVR (90.31), LR (105.09) |
| **MugRep** (GNN-based)       | **0.3244** | Superior to DNN, GBRT, SVR, LR                              |

**Key Finding**: Deep learning generally outperforms traditional methods; multimodal > single-modality

---

## Evaluation Metrics

The survey identifies standard metrics used across reviewed studies:

- **R² (Coefficient of Determination)**: Explains variance in predictions
- **MAE (Mean Absolute Error)**: Average magnitude of errors
- **RMSE (Root Mean Square Error)**: Used alongside MAE for overall performance
- **MAPE (Mean Absolute Percentage Error)**: Cross-category model comparisons

### Impact of Multimodality (Ablation Studies)
- **Tri-modal combinations** more accurate than bi-modal
- **Full modality combinations** yield highest performance peak
- **Example**: Combining textual descriptions with attribute data improved accuracy by **2.16%**

---

## Limitations and Challenges

### Current Limitations
1. **Technological Lag**: Real estate ML hasn't kept pace with broader multimodal advances; still exploring Transformer framework (2017) while field has moved to large models
2. **Heterogeneity**: Modalities have distinct structures, making integration difficult
3. **Dimensionality**: Fusing heterogeneous data causes "curse of dimensionality"
4. **Interpretability**: Visual feature extraction efficient but lacks explainability; deep learning generally suffers from low interpretability
5. **Data Quality**: In early fusion, low-quality single modality degrades overall performance
6. **Simplistic Features**: Some studies use overly simplistic features (e.g., traffic speed only for transportation) missing true geographic dependencies

### Identified Gaps
1. **No Systematic Survey**: Prior to this work, no comprehensive survey on multimodal ML for real estate existed
2. **Outdated Models**: Real estate applications often use older neural architectures
3. **Modality Classification**: Lack of detailed, consistent taxonomy for data modalities
4. **Modality Contribution Analysis**: Studies rarely evaluate specific contribution of each modality beyond ablation

---

## Future Research Directions

The authors outline three primary directions:

### 1. Multimodal Data Enhancement Potential
- Explore how modalities can **complement each other** to address data quality issues
- Instead of removing missing values, use "enhancement effects" (e.g., textual descriptions filling missing room details in attribute data)

### 2. Up-to-date Technology
- Move beyond current neural networks and basic Transformers
- Leverage **large model technologies** (e.g., LLMs, vision-language models) to align with modern multimodal learning era

### 3. Evaluate Contribution of Modalities
- Go beyond ablation studies (which only select relevant modalities)
- Calculate **detailed contribution levels** of specific modalities
- Determine specific impact of each modality on predictions to improve interpretability

---

## Recommendations

1. **Focus on Synergistic Relationships**: Prioritize how modalities interact and complement each other for better fusion and alignment
2. **Implement Cutting-Edge Technologies**: Apply state-of-the-art multimodal techniques rather than relying on outdated models
3. **Improve Interpretability**: Integrate modality contribution analysis to address long-standing explainability limitations

---

## Thesis Utility: "The Cebu Model"

### Direct Applications
- **Taxonomy Adoption**: Use the 5-modality framework (Attributes, Market, Textual, Visual, GIS) to structure your feature engineering
- **Fusion Strategy**: Consider **hybrid fusion** for combining BERT text embeddings with structured tabular features
- **Model Selection**: XGBoost or Random Forest with multimodal features as robust baseline; consider GNNs for spatial relationships

### Counter-Arguments Addressed
- "Why not just use traditional hedonic models?" → Survey shows multimodal approaches outperform single-modality by 2%+
- "Deep learning requires too much data" → Hybrid fusion with traditional ML can leverage embeddings without full DL pipeline

### Gaps This Paper Identifies That Your Thesis Could Fill
- Application of multimodal ML to **emerging markets** (Cebu falls in this category)
- Integration of **local text data** (Filipino/Cebuano listings) with structured features
- Contribution analysis of each modality for Cebu-specific context

---

## Critical Quotes

> "Multimodal machine learning significantly outperforms single-modality or fewer-modality approaches in terms of prediction accuracy, with enhanced interpretability."

> "The application of multimodal machine learning in real estate has not kept pace with broader advancements in the field."

> "Combining textual descriptions with attribute data improved accuracy by 2.16%."

> "Tree-based XGBoost (R² 0.45) was found to be vastly superior to Linear Regression-based XGBoost (R² 0.21)."

> "Future studies should go beyond ablation studies to calculate the detailed contribution levels of specific modalities."

---

*Summary generated: 2026-02-04 | Source: NotebookLM Deep Research*
