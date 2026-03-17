# Predicting Rental Price of Lane Houses in Shanghai with ML and LLMs

**Source**: NotebookLM Direct Query (LLM Embeddings Research Notebook)

---

## Bibliographic Context

- **Title**: Predicting Rental Price of Lane Houses in Shanghai with Machine Learning Methods and Large Language Models
- **Authors**: Tingting Chen, Shijing Si (Corresponding)
- **Affiliation**: Department of Data Science and Big Data Technology, Shanghai International Studies University
- **Publication**: arXiv (2024)
- **Keywords**: #LLM #ChatGPT #FewShotLearning #RentalPricePrediction #Shanghai

---

## Abstract

> "This study utilizes five traditional machine learning methods—multiple linear regression (MLR), ridge regression (RR), lasso regression (LR), decision tree (DT), and random forest (RF)—along with a Large Language Model (LLM) approach using ChatGPT, for predicting the rental prices of lane houses in Shanghai. It applies these methods to examine a public data sample of about 2,609 lane house rental transactions in 2021 in Shanghai. In terms of predictive power, RF has achieved the best performance among the traditional methods. However, the LLM approach, particularly in the 10-shot scenario, shows promising results that surpass traditional methods in terms of R-Squared value."

---

## Research Objective

Compare **traditional ML methods** vs **ChatGPT (LLM)** for rental price prediction using few-shot learning in an emerging market context.

---

## Methodology

### Traditional ML Models
- Multiple Linear Regression (MLR)
- Ridge Regression (RR)
- Lasso Regression (LR)
- Decision Tree (DT)
- Random Forest (RF)

### LLM Approach
- **Model**: ChatGPT (GPT-3.5/4)
- **Technique**: Few-shot in-context learning
- **Prompt Engineering**: Converted structured features into natural language context
- **Scenarios Tested**: 0-shot, 1-shot, 5-shot, **10-shot**

---

## Dataset: Shanghai Lane Houses

| Attribute        | Value                                                  |
| ---------------- | ------------------------------------------------------ |
| **Source**       | Kaggle (Shanghai Lane House Rental Prices 2021)        |
| **Initial Size** | 2,608 entries                                          |
| **Cleaned Size** | **2,549 entries**                                      |
| **Features**     | 16 attributes (district, bedrooms, sqm, heating, etc.) |

---

## Results

| Model                              | R²       | MAE     | MSE     |
| ---------------------------------- | -------- | ------- | ------- |
| Random Forest (Best Traditional)   | 0.74     | 3.06e+3 | 3.71e+7 |
| **ChatGPT 10-shot (Best Overall)** | **0.80** | 3.85e+3 | 7.38e+7 |
| ChatGPT 5-shot                     | 0.67     | —       | —       |
| ChatGPT 1-shot                     | <0.67    | —       | —       |
| ChatGPT 0-shot                     | Worst    | —       | —       |

### Key Finding
**10-shot ChatGPT achieves highest R² (0.80)**, surpassing all traditional ML models. However, it has higher absolute error (MSE) than Random Forest.

---

## Limitations

1. **LLM Data Translation**: Converting structured data to natural language is challenging
2. **Low-Shot Underperformance**: 0-shot and 1-shot lag behind traditional ML
3. **Random Forest Overfitting**: May not generalize to unseen data
4. **Higher MSE**: LLM has better R² but worse absolute error

---

## Thesis Utility

### Key Insight
> **With sufficient examples (10-shot), LLMs can outperform traditional ML in R².** But they require careful prompt engineering and may have higher absolute error.

### Feasibility for Cebu
- Need ~10 high-quality examples per prediction
- May work for specific property types with consistent features
- Higher compute cost than traditional ML

---

## Critical Quote

> "The 10-shot method, in particular, achieves the highest R-Squared value of 0.80, surpassing all traditional machine learning models."

---

*Summary generated: 2026-02-04 | Source: NotebookLM Deep Research*
