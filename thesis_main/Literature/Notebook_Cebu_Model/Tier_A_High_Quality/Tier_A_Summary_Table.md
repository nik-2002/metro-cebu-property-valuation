# Tier A Literature Summary: High-Quality References

> **Note**: This table summarizes the 11 Tier A (high-quality, quantitative, thesis-relevant) sources. Data extracted directly from NotebookLM source content.

| #   | Title                                                                                | Authors (Year)                       | Publication                                                    | Primary Finding                                                                                                        | Methodology                                                                                              | Regional Context                          | Key Quote                                                                                                    |
| --- | ------------------------------------------------------------------------------------ | ------------------------------------ | -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| 01  | Extraction of Building Roof Outlines from Remote Sensing Imagery Using Deep Learning | Gyekye (2025)                        | ResearchGate / UMaT Thesis                                     | **Res U-Net 82.99% accuracy**, 91.84% precision; outperformed standard U-Net (82.43%)                                  | Deep Learning (U-Net vs Residual U-Net); 3cm/pixel drone imagery; 4,580 images (128×128 tiles)           | Tarkwa, **Ghana**                         | "Residual U-Net... exhibited improved performance compared to the original U-Net module."                    |
| 02  | Valuation Problems in Developing Countries: A New Perspective                        | Cheloti & Mooya (2021)               | *Land* (MDPI), 10(12), 1352                                    | "Limited information" ranked **#1 problem** (Mean Rank 2.91); Valuer misconduct ranked **last** (2.32)                 | Census survey of 427 Kenya valuers (132 responses); Friedman ANOVA                                       | Nairobi, **Kenya**                        | "The core reason for valuation problems... is limited and unreliable information and not valuer misconduct." |
| 05  | Challenges in Property Valuation in Sub-Saharan Africa: A Systematic Review          | Becsky-Nagy & Sachicola (2025)       | *Vezetéstudomány* / Budapest Management Review                 | Urbanization vs Credit correlation: **−0.935** (credit shrinks as cities grow); Credit dropped 50.7%→33.4% (2010-2022) | PRISMA-based SLR (25 articles); Pearson correlation on World Bank data                                   | **Sub-Saharan Africa** (46 countries)     | "Financial infrastructure fails to keep pace with rapid urbanization."                                       |
| 08  | Evaluation of Challenges of Valuation of Specialized Properties                      | Otty, Nwosu, Okoro (2025)            | *British Journal of Environmental Sciences*, 13(1)             | Lack of comparable sales: **RII 0.8842** (top challenge); Replacement Cost Method: Mean 4.45 (dominant method)         | Survey of 45 registered firms (38 responses); Mean Score + RII analysis                                  | Enugu, **Nigeria**                        | "Lack of evidence on recent sales... is the most significant challenge."                                     |
| 13  | Machine Learning Valuation in Dual Market Dynamics                                   | Nyanda, Mattsson, Wilhelmsson (2024) | *Buildings* (MDPI), 14(10), 3172                               | Formal market: SVM **52.4% MAPE**; Dual market: Boosting **48.0% MAPE**; Neural Net **failed** (108.6%)                | 8 ML algorithms; 954 observations (524 formal, 430 informal); k-fold CV                                  | Dar es Salaam, **Tanzania**               | "ML's effectiveness in handling limited data... in emerging markets where traditional methods often fail."   |
| 20  | The Impact of Inflation on Real Estate Investment Performance                        | Nworah, Egbenta, Ogbuefi (2023)      | *Journal of Law and Sustainable Development*, 11(12)           | Inflation vs RE: **r = −0.508**; Exchange Rate vs RE: **r = −0.925** (stronger negative impact)                        | Pearson Correlation + Simple Linear Regression; Secondary data 2005–2022; SPSS/EViews                    | Lagos, **Nigeria**                        | "Inflation impacts highly on real estate and capable of distorting projections in property investment."      |
| 29  | Downside Risks to House Prices (Global Financial Stability Report)                   | Valckx et al. / IMF (2019)           | *IMF Global Financial Stability Report*, April 2019, Chapter 2 | House prices at risk modeled at **5th percentile**; Overvaluation + credit booms predict downside risk                 | Panel quantile regression (Growth-at-Risk framework); 32 advanced + emerging economies                   | **Global** (32 countries, 31 cities)      | "House-prices-at-risk measure is a useful early-warning indicator for financial stability surveillance."     |
| 32  | Using Luminosity Data as a Proxy for Economic Statistics                             | Chen & Nordhaus (2011)               | *PNAS*, 108(21), 8589–8594                                     | Optimal weight on lights: **<3%** for Grade A–C; **~30%** for Grade D (poor stats); Measurement error **≥25%**         | Comparison of DMSP-OLS nightlights vs G-Econ GDP at 1°×1° grid level (1992–2008)                         | **Global** (by statistical quality grade) | "Luminosity has informational value for countries with low-quality statistical systems."                     |
| 36  | Roof Type Classification with Innovative Machine Learning Approaches                 | Ölçer, Ölçer, Sümer (2023)           | *PeerJ Computer Science*, 9, e1268                             | SNN **73% accuracy** (60 samples) vs CNN **39%**; One-shot learning: SNN **55%** vs CNN **0%** (1 sample)              | Siamese Neural Network (OSL) trained on artificial images (Autodesk Maya); tested on real satellite data | **Turkey** (methodology paper)            | "The OSL approach can get satisfactory results even with just one data point."                               |
| 38  | Valuation Inaccuracy: An Examination of Causes in Lagos Metropolis                   | Ajibola (2010)                       | *Journal of Sustainable Development*, 3(4), 187–193            | Inaccuracy range: **+24.8% to +51.5%** (vs ±10% global norm); **92.7%** cite insufficient market evidence              | Survey of 300 valuers (150 responses); Descriptive statistics                                            | Lagos, **Nigeria**                        | "Valuation as presently carried out is not a good proxy for sale and mortgage transactions."                 |
| 40  | International Valuation Standards (IVS 2025)                                         | IVSC (2025)                          | IVSC Official Standards (Effective 31 Jan 2025)                | **IVS 104**: Data must be Accurate, Complete, Timely, Transparent; **IVS 105**: AVMs require professional judgement    | Standards Document; Principles-based framework                                                           | **Global** (IVSC member countries)        | "No model without the valuer applying professional judgement... can produce an IVS-compliant valuation."     |

---

## Quick Reference: Key Metrics by Theme

### Data Scarcity Problem
| Source       | Metric    | Finding                          |
| ------------ | --------- | -------------------------------- |
| 02 (Kenya)   | Mean Rank | 2.91 (information = top problem) |
| 08 (Nigeria) | RII       | 0.8842 (lack of sales data)      |
| 38 (Lagos)   | Survey %  | 92.7% cite insufficient evidence |

### ML Performance Benchmarks
| Source        | Model            | Accuracy/Error       |
| ------------- | ---------------- | -------------------- |
| 01 (Ghana)    | Res U-Net        | 82.99%               |
| 13 (Tanzania) | Random Forest    | 52.7% MAPE           |
| 13 (Tanzania) | Neural Net       | 108.6% MAPE (failed) |
| 36 (Turkey)   | SNN (60 samples) | 73% vs CNN 39%       |

### Macroeconomic Correlations
| Source       | Variables              | r-value |
| ------------ | ---------------------- | ------- |
| 05 (SSA)     | Urbanization vs Credit | −0.935  |
| 20 (Nigeria) | Exchange Rate vs RE    | −0.925  |
| 20 (Nigeria) | Inflation vs RE        | −0.508  |

---

*Generated: 2026-02-04 | Source: NotebookLM Direct Query*
