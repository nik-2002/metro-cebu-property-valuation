# Literature-Thesis Interplay Map

> **Thesis**: Data-Driven Property Valuation Model for Cebu City  
> **Author**: Chris Dominic Estreba  
> **Purpose**: Direct mapping of 19 key papers to thesis components for RRL presentation

---

## Executive Summary

This document maps **11 Tier A papers** + **8 Hybrid LLM papers** directly to the thesis framework. Each paper is categorized by which thesis component it supports:

| Thesis Component      | Papers Supporting It |
| --------------------- | -------------------- |
| Problem Statement     | 4 papers             |
| Methodology           | 6 papers             |
| Feature Engineering   | 5 papers             |
| Benchmarks & Metrics  | 4 papers             |
| Regulatory Compliance | 2 papers             |

---

## 1. Problem Statement Support

### 1.1 "Information scarcity is the core valuation problem"

| Paper                      | Location | Key Finding                                                                               | Direct Quote                                                                                                     |
| -------------------------- | -------- | ----------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **Cheloti & Mooya (2021)** | Kenya    | "Limited information" ranked #1 problem (Mean Rank 2.91); valuer misconduct ranked *last* | "The core reason for valuation problems... is limited and unreliable information and **not** valuer misconduct." |
| **Otty et al. (2025)**     | Nigeria  | Lack of comparable sales: RII = 0.8842 (highest challenge)                                | "Lack of evidence on recent sales... is the most significant challenge."                                         |
| **Ajibola (2010)**         | Lagos    | 92.7% of valuers cite insufficient market evidence                                        | "Valuation as presently carried out is not a good proxy for sale and mortgage transactions."                     |

**→ Thesis Application**: Justifies why Cebu needs a data-driven model. The problem isn't "bad appraisers" — it's "bad data infrastructure."

---

### 1.2 "Valuation inaccuracy is severe in developing markets"

| Paper                              | Location           | Key Finding                                                                | Implication for Cebu                                                                   |
| ---------------------------------- | ------------------ | -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **Ajibola (2010)**                 | Lagos              | Valuation inaccuracy: +24.8% to +51.5% (vs ±10% global norm)               | Sets baseline: If Cebu achieves <20% error, it outperforms comparable emerging markets |
| **Becsky-Nagy & Sachicola (2025)** | Sub-Saharan Africa | Credit availability dropped 50.7% → 33.4% (2010-2022) as urbanization rose | Shows systemic failure of traditional finance to keep pace with urban growth           |

**→ Thesis Application**: Establishes urgency. Without data-driven tools, Cebu risks similar valuation dysfunction as African markets.

---

## 2. Methodology Justification

### 2.1 "Tree-based ML outperforms Neural Networks on small tabular data"

| Paper                    | Location | Sample Size | Finding                                                                        | Model Comparison                                 |
| ------------------------ | -------- | ----------- | ------------------------------------------------------------------------------ | ------------------------------------------------ |
| **Nyanda et al. (2024)** | Tanzania | 954         | Neural Network **failed** (108.6% MAPE); Random Forest achieved **52.4% MAPE** | RF/XGBoost >> NN for emerging market valuation   |
| **Ölçer et al. (2023)**  | Turkey   | 60          | SNN achieved **73% accuracy** vs CNN **39%** on small datasets                 | Siamese Networks viable for low-sample scenarios |

**→ Thesis Application**: Directly justifies your choice of **Random Forest + XGBoost** over deep learning. NN requires large datasets; Cebu has ~1,000 listings.

---

### 2.2 "Satellite imagery enables scalable feature extraction"

| Paper             | Location | Method                             | Accuracy                          |
| ----------------- | -------- | ---------------------------------- | --------------------------------- |
| **Gyekye (2025)** | Ghana    | Residual U-Net for roof extraction | 82.99% accuracy, 91.84% precision |

**→ Thesis Application**: If you expand to satellite-derived features (building footprints, roof types), this provides the technical precedent.

---

### 2.3 "Text embeddings from listings improve predictions"

| Paper                           | Location  | Method                      | Performance Gain                     |
| ------------------------------- | --------- | --------------------------- | ------------------------------------ |
| **Describe the House (Ottawa)** | Canada    | Self-trained Word2Vec + DNN | R² = **0.79** (44% better than BERT) |
| **MHPP (Melbourne)**            | Australia | SBERT + CLIP + LightGBM     | **26% MAE improvement**              |
| **Seattle BERT ROI**            | USA       | BERT + XGBoost Stacking     | **11% MAE reduction**                |
| **Shanghai Lane Houses**        | China     | ChatGPT 10-shot prompting   | R² = **0.80** (beat Random Forest)   |

**→ Thesis Application**: If you process listing descriptions (e.g., "corner lot with garden"), Word2Vec or BERT embeddings can add 10-26% accuracy. Domain-trained Word2Vec (Ottawa) beats pre-trained BERT.

---

## 3. Feature Engineering Evidence

### 3.1 Structural & Location Features

| Feature Category            | Supporting Paper        | Finding                                                        |
| --------------------------- | ----------------------- | -------------------------------------------------------------- |
| **Distance to CBD/Transit** | Tanzania #13, Kenya #02 | Access variables consistently top-ranked in feature importance |
| **Lot/Floor Area**          | All hedonic models      | Standard predictor; log-transform recommended                  |
| **Property Type**           | Tanzania #13            | Formal vs informal market segmentation matters                 |

### 3.2 Text-Derived Features

| Feature                  | Supporting Paper | Premium/Effect                             |
| ------------------------ | ---------------- | ------------------------------------------ |
| **Listing "Uniqueness"** | UConn (Atlanta)  | 5.6% price premium for unique descriptions |
| **Sentiment Score**      | Malaysia #08     | r = 0.78 correlation with prices           |
| **Keyword Embeddings**   | Ottawa #03       | 44% R² improvement from text features      |

### 3.3 Macro & Administrative Features

| Feature              | Supporting Paper        | Finding                                                |
| -------------------- | ----------------------- | ------------------------------------------------------ |
| **Exchange Rate**    | Nworah et al. (Nigeria) | r = **-0.925** (stronger than inflation at r = -0.508) |
| **BIR Zonal Values** | Lagos #38               | Documents gap between admin values and market prices   |

**→ Thesis Application**: Your "Valuation Gap" (Market Price − Zonal Value) is empirically supported by Lagos findings showing systematic admin-market disconnect.

---

## 4. Benchmark Targets

### 4.1 Performance Baselines from Literature

| Metric                                 | Paper         | Baseline Value | Your Target      |
| -------------------------------------- | ------------- | -------------- | ---------------- |
| **MAPE (dual formal/informal market)** | Tanzania #13  | 52.4% (RF)     | < 40%            |
| **R² (with text features)**            | Ottawa #03    | 0.79           | > 0.70           |
| **R² (LLM prompting)**                 | Shanghai #04  | 0.80           | Feasibility test |
| **MAE improvement from text**          | Melbourne #02 | 26%            | > 15%            |

### 4.2 ML vs Traditional Method Comparison

| Study    | Traditional Method Error | ML Method Error    | Improvement         |
| -------- | ------------------------ | ------------------ | ------------------- |
| Tanzania | 52.7% (Linear)           | 48.0% (Boosting)   | ~4.7%               |
| Ottawa   | 0.55 R² (No Text)        | 0.79 R² (Word2Vec) | +44%                |
| Baidoa   | Hedonic baseline         | Hybrid ANN         | 20% error reduction |

**→ Thesis Application**: Your RQ3 ("Which model is most accurate?") can reference these as prior benchmarks.

---

## 5. Regulatory & Interpretability Constraints

### 5.1 IVS 2025 Compliance

| Paper           | Key Requirement                  | Quote                                                                                                       |
| --------------- | -------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **IVSC (2025)** | Professional judgement mandatory | "No model... without the valuer applying professional judgement... can produce an IVS-compliant valuation." |
| **IVSC (2025)** | Data quality standards           | IVS 104: Data must be **Accurate, Complete, Timely, Transparent**                                           |

**→ Thesis Application**: Frame your model as **"Decision Support Tool"** not "Replacement Appraiser." Your Human-in-the-Loop validation aligns with IVS 105.

### 5.2 Explainability Solutions

| Method                  | Supporting Paper      | Application                                      |
| ----------------------- | --------------------- | ------------------------------------------------ |
| **SHAP Values**         | Multimodal Survey #01 | XGBoost feature importance visualization         |
| **Hybrid Hedonic + ML** | Baidoa #06, UConn #05 | Keep interpretable hedonic baseline alongside ML |

---

## 6. Visual Synthesis: Paper → Thesis Component Matrix

```
                    ┌──────────────────────────────────────────────────────────┐
                    │                THESIS FRAMEWORK                          │
                    ├────────────┬────────────┬────────────┬──────────────────┤
                    │  PROBLEM   │  METHOD    │  FEATURES  │  VALIDATION      │
┌───────────────────┼────────────┼────────────┼────────────┼──────────────────┤
│ TIER A PAPERS     │            │            │            │                  │
├───────────────────┼────────────┼────────────┼────────────┼──────────────────┤
│ Kenya #02         │     ●      │            │            │                  │
│ Nigeria #08       │     ●      │            │            │                  │
│ Lagos #38         │     ●      │            │     ●      │                  │
│ SSA Review #05    │     ●      │            │            │                  │
│ Tanzania #13      │            │     ●      │     ●      │        ●         │
│ Ghana #01         │            │     ●      │            │                  │
│ Turkey #36        │            │     ●      │            │                  │
│ Nigeria Inflation │            │            │     ●      │                  │
│ IMF #29           │            │            │     ●      │                  │
│ Luminosity #32    │            │            │     ●      │                  │
│ IVS 2025 #40      │            │            │            │        ●         │
├───────────────────┼────────────┼────────────┼────────────┼──────────────────┤
│ HYBRID LLM PAPERS │            │            │            │                  │
├───────────────────┼────────────┼────────────┼────────────┼──────────────────┤
│ Ottawa #03        │            │     ●      │     ●      │                  │
│ Melbourne #02     │            │     ●      │     ●      │                  │
│ Shanghai #04      │            │     ●      │            │                  │
│ UConn #05         │            │            │     ●      │                  │
│ Seattle #07       │            │     ●      │     ●      │                  │
│ Malaysia #08      │            │            │     ●      │                  │
│ Baidoa #06        │            │     ●      │            │        ●         │
│ Survey #01        │            │     ●      │            │        ●         │
└───────────────────┴────────────┴────────────┴────────────┴──────────────────┘
```

---

## 7. Key Takeaways for Presentation

### What the Literature Agrees On:
1. **Data scarcity** is the #1 barrier in emerging markets (not corruption or incompetence)
2. **Tree-based ML** (RF, XGBoost) outperforms Neural Networks on small tabular datasets
3. **Text features** from listings improve predictions by 10-44%
4. **IVS 2025** requires human oversight — models *augment*, not *replace*

### How Cebu Thesis Fills the Gap:
1. First **Cebu-specific** property-level valuation model
2. Uses **hybrid data** (foreclosures + online listings) to address data scarcity
3. Tests **feature importance** using SHAP for regulatory transparency
4. Incorporates **future factors** (CBRT) that traditional appraisals miss

### Benchmark to Beat:
> **Tanzania (2024)**: 52% MAPE with Random Forest on n=954 dual-market data  
> **Ottawa (2023)**: R² = 0.79 with self-trained Word2Vec embeddings

---

*Generated: 2026-02-04 | For RRL Presentation*
