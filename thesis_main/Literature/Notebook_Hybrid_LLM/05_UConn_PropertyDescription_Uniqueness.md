# Information Value of Property Description: A Machine Learning Approach

**Source**: NotebookLM Direct Query (LLM Embeddings Research Notebook)

---

## Bibliographic Context

- **Title**: Information Value of Property Description: A Machine Learning Approach
- **Author**: Lily Shen
- **Affiliation**: Clemson University (formerly UConn Finance Department)
- **Publication**: Working Paper (November 2018)
- **Keywords**: #UnsupervisedLearning #HedonicPricing #TextualData #Uniqueness #AtlantaRealEstate

---

## Abstract

> "This paper employs a ML–Hedonic approach to quantify the value of uniqueness, a type of 'soft' information embedded in real estate advertisements. We first propose an unsupervised learning algorithm to quantify levels of semantic deviation ('uniqueness') in descriptions, the textual portions of real estate advertisements. The results indicate textual data disseminate information that numerical data cannot capture. A one standard deviation (0.08) increase in description uniqueness compared to neighboring properties leads to a 5.6% increase in property sale prices and a 2.3-day delay in the closing time."

---

## Research Objective

Quantify the **economic value of textual uniqueness** in property descriptions using unsupervised learning + hedonic pricing models.

---

## Methodology: ML-Hedonic Hybrid

### Unsupervised Learning Component
1. **Paragraph Vector Method** (Neural Network): Learns semantic meaning of descriptions
2. **Text → Vector**: Converts descriptions into high-dimensional vectors
3. **Uniqueness Score**: Calculates cosine distance from neighborhood centroid
4. **Result**: Scalar "uniqueness" measure per property

### Hedonic Regression Component
- Feed uniqueness score into OLS hedonic model
- Control for physical characteristics, location, time

**Key Innovation**: Unsupervised learning to "harden" soft information from text.

---

## Dataset: Atlanta, Georgia

| Attribute              | Value                        |
| ---------------------- | ---------------------------- |
| **Location**           | Atlanta, GA                  |
| **Timeframe**          | January 2010 – December 2017 |
| **Total Transactions** | **40,918**                   |
| **Unique Sales**       | 37,124                       |
| **Repeat Sales**       | 3,794                        |

---

## Results

### Price Premium from Uniqueness
| Effect             | Magnitude                     |
| ------------------ | ----------------------------- |
| **Price Increase** | +5.6% per 1 SD uniqueness     |
| **Liquidity Cost** | +2.3 days to closing per 1 SD |

### Spillover Effects
- **"Bad" house in good neighborhood**: Gains price premium (positive spillover)
- **"Good" house in bad neighborhood**: Suffers discount (negative spillover)

### Agent Experience
- Experienced agents write more value-enhancing descriptions
- Positive correlation between agent tenure and description effectiveness

---

## Limitations

1. **Geographic Scope**: Limited to Atlanta single-family homes
2. **Selection Bias**: Excludes unsold properties (descriptions deleted)
3. **Short Descriptions Excluded**: <9 characters removed
4. **Liquidity Trade-off**: Higher uniqueness = higher price but slower sale

---

## Thesis Utility

### Key Insight
> **Text descriptions carry "soft" information worth 5.6% price premium.** The value comes from describing unique features, not just marketing language.

### Application to Cebu
- Listing descriptions in Cebu likely carry similar soft information
- Could extract uniqueness scores from Filipino/English listings
- Use as additional feature in valuation model

### Novel Contribution
> "While most ML studies in economics focus on predictions, this paper suggests ML has also allowed the hardening of 'soft' information using textual data."

---

## Critical Quote

> "A one standard deviation increase in description uniqueness leads to a 5.6% increase in property sale prices."

---

*Summary generated: 2026-02-04 | Source: NotebookLM Deep Research*
