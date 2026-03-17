# AI-Driven Sentiment Analysis with NLP for Enhanced Property Market Valuation in Malaysia

**Source**: NotebookLM Direct Query (LLM Embeddings Research Notebook)

---

## Bibliographic Context

- **Title**: AI-Driven Sentiment Analysis with Natural Language Processing (NLP) for Enhanced Property Market Valuation in Malaysia
- **Authors**: Muhammad Najib Razali, Muhammad Yusaimi Abdul Hamid, Mazlan Che Soh, Fazira Shafie
- **Affiliation**: Universiti Teknologi Malaysia
- **Publication**: PRRES (Pacific Rim Real Estate Society) Conference (2025)
- **Keywords**: #SentimentAnalysis #BERT #LSTM #ARIMA #GARCH #MalaysiaRealEstate

---

## Abstract

> "This study aims to enhance property market valuation in Malaysia by integrating AI-driven sentiment analysis with traditional econometric models and advanced machine learning (ML) techniques. The proposed framework combines ARIMA and GARCH models with deep learning algorithms such as LSTM and ANN. Sentiment analysis leverages NLP through BERT to extract market sentiment from property-related news, social media discussions, and corporate disclosures."

---

## Methodology: Hybrid Framework

### Econometric Models
- **ARIMA**: Time series forecasting
- **GARCH**: Volatility modeling

### Deep Learning
- **LSTM**: Sequential pattern recognition
- **ANN**: Non-linear relationships

### Sentiment Analysis
- **BERT (Multilingual)**: Fine-tuned for Bahasa Malaysia, English, Mandarin
- **Sources**: Property news, social media, corporate disclosures
- **Bias Reduction**: 12% reduction in classification bias between languages

---

## Dataset: Malaysia Property Market

| Attribute     | Value                                             |
| ------------- | ------------------------------------------------- |
| **Location**  | Malaysia (national)                               |
| **Timeframe** | 2015–2024                                         |
| **Languages** | Bahasa Malaysia, English, Mandarin                |
| **Sources**   | News portals, social media, corporate disclosures |

---

## Results

### Accuracy Improvement
| Model                         | MAE      | RMSE     |
| ----------------------------- | -------- | -------- |
| Baseline (ARIMA-GARCH)        | —        | —        |
| **Hybrid (+ Sentiment LSTM)** | **1.24** | **1.87** |
| **Improvement**               | —        | **~20%** |

### Sentiment-Price Correlation
| Sentiment Source            | Correlation (r) |
| --------------------------- | --------------- |
| **Overall Sentiment Index** | **0.78**        |
| News-based Sentiment        | 0.81            |
| Social Media Sentiment      | 0.74            |

### Key Temporal Finding
- Sentiment-price correlation strengthened after 2018
- Particularly strong during COVID-19 (2020–2021)

---

## Limitations

1. **Missing Variables**: No neighborhood amenities, infrastructure, environmental data
2. **Sampling Bias**: Excludes investors not active online
3. **Malaysia-Specific**: May not generalize to other markets
4. **Stability Assumption**: Struggles with unexpected shocks

---

## Thesis Utility

### Key Insight
> "Positive market sentiment coincided with rising property prices, while negative sentiment served as an early indicator of downturns."

### Application to Cebu
- Sentiment from Philippine news/social media could enhance predictions
- News sentiment (r=0.81) stronger than social media (r=0.74)
- Consider Filipino/English multilingual BERT

### Novel Angle
Sentiment analysis as **leading indicator** of price changes—could add temporal dimension to Cebu model.

---

## Critical Quote

> "The overall sentiment index was positively correlated with property price changes (r = 0.78, p < 0.01)... implying that positive market sentiment coincided with rising property prices, while negative sentiment served as an early indicator of downturns."

---

*Summary generated: 2026-02-04 | Source: NotebookLM Deep Research*
