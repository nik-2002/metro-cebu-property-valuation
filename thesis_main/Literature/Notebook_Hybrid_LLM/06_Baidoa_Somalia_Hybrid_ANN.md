# Modeling Residential Property Prices in Emerging Climate-Responsive Urban Markets: Baidoa City, Somalia

**Source**: NotebookLM Direct Query (LLM Embeddings Research Notebook)

---

## Bibliographic Context

- **Title**: Modeling Residential Property Prices in Emerging Climate-Responsive Urban Markets: A Hybrid Modeling Framework for Baidoa City-Somalia
- **Authors**: Multiple authors (not fully specified in source)
- **Publication**: Frontiers in Built Environment (Urban Science), Volume 11, 2025
- **Keywords**: #EmergingMarkets #HedonicPricing #ANN #Somalia #ClimateResponsive

---

## Abstract

> "This study aims to examine the determinants of residential property prices in Baidoa's climate-responsive real estate market. It investigates both linear and non-linear interactions among key variables to enhance property valuation models and inform urban development strategies. A hybrid-methods design was adopted, integrating a hedonic regression model with an artificial neural network (ANN) framework. The ANN model further reduced prediction errors by approximately 20%, effectively capturing complex non-linear relationships among the predictors."

---

## Research Objective

Develop a **hybrid hedonic + ANN model** for property valuation in an **emerging market** (Baidoa, Somalia) with limited infrastructure and data.

---

## Methodology

### Hybrid Framework
1. **Hedonic Regression (OLS)**: Baseline linear model
2. **Artificial Neural Network (Multilayer Perceptron)**: Captures non-linear relationships
3. **Validation**: 5-fold cross-validation + 95% confidence intervals

**Note**: Study reviewed NLP in literature but did NOT use NLP—focused on structured features.

---

## Dataset: Baidoa Housing Survey

| Attribute       | Value                                                            |
| --------------- | ---------------------------------------------------------------- |
| **Location**    | Baidoa City, Somalia                                             |
| **Sample Size** | **118 residential properties**                                   |
| **Features**    | Property size, bedrooms, CBD proximity, safety, age, air quality |
| **Sampling**    | Stratified random                                                |

---

## Results

| Model              | R²     | MAE (Test) | MSE Improvement   |
| ------------------ | ------ | ---------- | ----------------- |
| Hedonic Regression | 0.742  | —          | Baseline          |
| **ANN**            | Higher | **1,200**  | **20% reduction** |

### Key Finding
ANN achieves **20% reduction in MAE/MSE** compared to linear hedonic model by capturing non-linear relationships.

---

## Limitations

1. **Small Sample**: Only 118 properties limits statistical power
2. **Single City**: Baidoa-specific, may not generalize
3. **Missing Variables**: No public transport/walkability data (underdeveloped infrastructure)
4. **Subjectivity**: Safety/air quality from non-standardized local assessments
5. **Black Box**: ANN lacks transparency compared to regression

---

## Thesis Utility

### Key Insight for Emerging Markets
> "This makes it particularly suitable for emerging urban contexts where housing markets are shaped by both formal planning logic and informal dynamics."

### Relevance to Cebu
- Cebu shares characteristics with Baidoa: emerging market, mixed formal/informal
- Hybrid hedonic + ML approach works with small samples (n=118)
- Key predictors: CBD proximity, safety, infrastructure

### Sample Size Comparison
| Study         | Location    | Sample Size  | Model                     |
| ------------- | ----------- | ------------ | ------------------------- |
| Baidoa        | Somalia     | 118          | ANN + Hedonic             |
| Cebu (Target) | Philippines | ~1,000-3,000 | Similar approach feasible |

---

## Critical Quote

> "This makes it particularly suitable for emerging urban contexts where housing markets are shaped by both formal planning logic and informal dynamics."

---

*Summary generated: 2026-02-04 | Source: NotebookLM Deep Research*
