# Smart Real Estate Investment: ML Models for Identifying High-ROI Properties in Seattle

**Source**: NotebookLM Direct Query (LLM Embeddings Research Notebook)

---

## Bibliographic Context

- **Title**: Smart Real Estate Investment: Machine Learning Models for Identifying High-ROI Properties in Seattle
- **Author**: Aditya Kasturi
- **Affiliation**: Realogics Sotheby's International Realty, USA
- **Publication**: Preprints.org (2025)
- **Keywords**: #BERT #EnsembleLearning #ROI #SeattleRealEstate #XGBoost #StackingModels

---

## Abstract

The study addresses the need for localized forecasting models to identify high return-on-investment (ROI) residential properties in the volatile Seattle housing market. The research integrates ensemble learning techniques (Random Forest, XGBoost, StackingAveragedModels) with multimodal data, combining structured features with unstructured text embeddings from property descriptions. StackingAveragedModels achieved the highest accuracy (R² = 0.78), significantly outperforming single-model regressors.

---

## Methodology

### Multimodal Feature Engineering
1. **Structured Features**: Lot size, year built, interior space, school ratings
2. **BERT Embeddings**: Property listing descriptions → text embeddings
3. **Spatial-Temporal Features**: Location and time-based features

### Models Tested
- Random Forest
- XGBoost
- **StackingAveragedModels** (best performer)

### BERT Usage
BERT embeddings capture "nuanced property attributes missed in structured variables":
- Sentiment cues
- Keywords like "renovated," "view"
- Qualitative descriptors

---

## Dataset: King County, Washington

| Attribute       | Value                                    |
| --------------- | ---------------------------------------- |
| **Location**    | King & Snohomish Counties (Seattle area) |
| **Timeframe**   | 2015–2024                                |
| **Sample Size** | **4,600+ transactions**                  |

---

## Results

| Model                      | R²       | RMSE            | RMSLE |
| -------------------------- | -------- | --------------- | ----- |
| **StackingAveragedModels** | **0.78** | $74,100–$88,000 | 0.232 |

### BERT Impact
> **11.2% decrease in MAE** when including BERT text embeddings vs structured data only.

---

## Limitations

1. **Privacy Risks**: Geolocation + text can reveal private information, serve as demographic proxies
2. **Algorithmic Bias**: May perpetuate housing discrimination; positive descriptions more prevalent in affluent areas
3. **Black Box**: Ensemble/DL architectures difficult for regulators to audit
4. **Gentrification Risk**: Could direct investment away from low-income areas

---

## Thesis Utility

### Key Insight
> "Integrating engineered property attributes with natural language embeddings through ensemble machine learning enhances ROI forecasting in the urban real estate market significantly."

### Application to Cebu
- BERT embeddings add 11% accuracy—worth exploring for Cebu listings
- Stacking ensemble outperforms single models
- Consider ethical implications for Cebu's mixed-income neighborhoods

---

*Summary generated: 2026-02-04 | Source: NotebookLM Deep Research*
