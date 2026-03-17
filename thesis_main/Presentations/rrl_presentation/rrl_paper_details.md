# RRL Paper Details (NotebookLM Query Results)

> Compiled: 2026-02-06 | Ready for slide creation

---

## 1. TPS 2023 — Ramolete et al. (Philippines) 🇵🇭

**Title**: Utilization of ML, Government-Based and Non-Conventional Indicators for Property Value Prediction in the Philippines

### Key Statistics
| Metric            | Value                                    |
| ----------------- | ---------------------------------------- |
| Study Areas       | Cavite (Region IV-A), Metro Manila (NCR) |
| Data Source       | Lamudi listings (web-scraped)            |
| Best MAPE         | **10.7%–21%**                            |
| Cavite Best       | 11.5% MAPE (segmented)                   |
| Metro Manila Best | 12.1% MAPE (segmented)                   |

### Institutional Critiques
- **Only 60%** of LGUs updated zonal values (2017-2020)
- **Only 37%** submitted updated market value schedules
- BIR vs LGU disconnect creates appraisal variation
- Traditional methods "fail to account for non-pecuniary values"

### Methodology
- **Models**: AdaBoost, GBM, XGBoost
- **Features**: OSM amenities, CMCI index, PSA socio-economic data
- **Segmentation**: 87.5% of properties benefited from clustering

### Quotable
> "Including government-based indicators had a substantial positive effect on model performance."

---

## 2. Agosto — Cebu City Land Values 🇵🇭

**Title**: Determinants of Land Values in Cebu City, Philippines

### Top 5 Determinants (by Factor Loading)
1. Accessibility to public transportation
2. Recreational facilities
3. Open spaces and parks
4. Environmental quality
5. Level of ownership

### Sample & Methodology
| Metric             | Value             |
| ------------------ | ----------------- |
| Survey Distributed | 60 questionnaires |
| Valid Responses    | **51**            |
| Vicinities Sampled | 15 barangays      |
| Variables Tested   | 31 determinants   |
| Factors Extracted  | 11 (via PCA)      |

### Methodology
- 5-point Likert scale survey
- Factor Analysis (PCA with varimax rotation)
- Multiple Regression (SPSS)
- Secondary data: BIR zonal values, Cebu land use maps

### Limitations
> "The study sample was **limited to residential properties**."

---

## 3. Nyanda et al. — Tanzania ML Valuation 🇹🇿

**Title**: ML Valuation in Dual Market Dynamics (Dar es Salaam)

### Sample Size Split
| Market          | Observations |
| --------------- | ------------ |
| Formal Agents   | 524          |
| Informal Agents | 430          |
| **Total**       | **954**      |

### Features Used
- **Location**: Kimabu, Goba, Tabata, Kawe (binary)
- **Structural**: Storeys, bedrooms, plot size, fence, roof/ceiling/floor types
- **Temporal**: Year of transaction (2010-2019)
- **Spatial**: Distance to arterial road, hospital, airport, food market; X/Y coordinates

### Model Performance (Testing MAPE)
| Model            | Formal Only | Formal + Informal |
| ---------------- | ----------- | ----------------- |
| Neural Network   | 108.6% ❌    | 63.5%             |
| Random Forest    | 56.4%       | 52.7%             |
| **Boost**        | 101.5%      | **48.0%** ✅       |
| Nearest Neighbor | **37.6%** ✅ | 75.6%             |

### Key Insight
> NN failed on small/noisy data. Tree-based models (Boost, RF) outperformed.

---

## 4. Ottawa Word2Vec — Zhang et al. (Canada) 🇨🇦

**Title**: Describe the house and I will tell you the price

### Sample Size
| Stage          | Count                                            |
| -------------- | ------------------------------------------------ |
| Raw listings   | 10,418                                           |
| After cleaning | **10,251**                                       |
| Cities         | Ottawa, Toronto, Mississauga, Brampton, Hamilton |

### Text Feature Extraction
- **Word2Vec**: Self-trained Continuous Skip-gram
  - Dimension: 300
  - Window size: 8
  - Sentence embedding: Mean pooling
  - Stop words **NOT removed** (preserves context)
- **BERT**: Pre-trained base model (768 dimensions)
- **TF-IDF**: 412-word vector after preprocessing

### R² Results
| Model                      | R²           |
| -------------------------- | ------------ |
| Baseline (no text)         | 0.6738       |
| Combined (text + features) | 0.7184       |
| **Word2Vec-only DNN**      | **0.7904** ✅ |

### Key Insight
> Self-trained domain Word2Vec outperformed pre-trained BERT.

---

## 5. Shanghai ChatGPT — Lane Houses 🇨🇳

**Title**: Predicting Rental Price of Lane Houses with ML and LLMs

### Sample Size
| Stage           | Count     |
| --------------- | --------- |
| Initial dataset | 2,609     |
| After cleaning  | **2,549** |

### 10-Shot Prompting Structure
- **Prompt-as-Prefix** methodology
- 10 examples selected for **high relevance** to test case
- Same geographic area + similar attributes
- Prompt fields: `[Location]`, `[Type and area]`, `[Features]`, `[Statistics]`, `[Instruction]`

### R² Comparison
| Model               | R²         |
| ------------------- | ---------- |
| Random Forest       | 0.74       |
| **ChatGPT 10-shot** | **0.80** ✅ |

### Key Insight
> LLM 10-shot prompting outperformed traditional ML on small sample.

---

## Quick Reference for Slides

| Slide | Paper    | Key Stat                   | Quote                                       |
| ----- | -------- | -------------------------- | ------------------------------------------- |
| 2-3   | TPS 2023 | 60% LGU update rate        | "Government indicators improve performance" |
| 4     | Agosto   | 51 respondents, 31 factors | "Limited to residential"                    |
| 5     | Tanzania | 954 obs, Boost 48% MAPE    | "NN failed (108.6%)"                        |
| 6     | Ottawa   | 10,251 listings, R²=0.79   | "Self-trained beats BERT"                   |
| 6     | Shanghai | 2,549 listings, R²=0.80    | "10-shot beats RF"                          |
