# RRL Presentation: Slide Content Guide (v2)

> **Papers**: 10 essential | **Format**: 10 slides | 15 mins

---

## SLIDE 1: Title (~30 sec)

### Content
- **Title**: Review of Related Literature
- **Subtitle**: Data-Driven Property Valuation for Cebu City
- **Author**: Chris Dominic Estreba
- **Programme**: MS Data Science
- **Date**: February 2026

### Speaker Notes
> "Good morning. Today I'll present the related literature that forms the foundation for my thesis on developing a data-driven property valuation model for Cebu City."

---

## SLIDE 2: Global Problem — Data Scarcity (~2 min)

### Headline
**"Data scarcity — not appraiser incompetence — is the core problem"**

### Content
| Finding                                                 | Source |
| ------------------------------------------------------- | ------ |
| "Limited information" = **#1 problem** (Mean Rank 2.91) | Kenya  |
| **92.7%** cite insufficient market evidence             | Lagos  |
| Error: **+24% to +51%** vs ±10% global norm             | Lagos  |

### Quote (callout box)
> "The core reason... is limited information and **not** valuer misconduct."  
> — Cheloti & Mooya (2021)

### Recommendations
- Use **3 stat cards** or a clean table
- Bold the numbers for visual impact
- Optional: World map highlighting Kenya and Nigeria

### Speaker Notes
> "The literature from Africa — facing similar challenges to the Philippines — shows the problem isn't bad appraisers. It's bad data. In Kenya, information scarcity ranked #1. In Lagos, 92% cite insufficient evidence, and valuations deviate by up to 51%."

### Q&A Footnotes
- **Mean Rank 2.91**: From a Friedman ANOVA ranking of valuation problems; lower rank = more severe problem. "Limited information" ranked highest (worst).
- **±10% global norm**: International standard acceptable margin of error for valuations. Anything beyond this is considered inaccurate.
- **Market evidence**: Comparable sales data, rental rates, transaction records used to justify valuations.

---

## SLIDE 3: Philippine Context (~1.5 min)

### Headline
**"The Philippines faces the same structural gap"**

### Content (TPS 2023)
| Problem                        | Detail                                      |
| ------------------------------ | ------------------------------------------- |
| **Outdated zonal values**      | Only **60%** of LGUs updated (2017-2020)    |
| **Missing market schedules**   | Only **37%** submitted updated SMVs         |
| **Multiple valuation systems** | 2-3 different values for same property      |
| **Agency disconnect**          | BIR vs LGU vs LRA with overlapping mandates |

### Key Institutional Issues
- **Fragmentation**: Different agencies (BIR, LGU, LRA) use different methods, timelines, and standards
- **Political intervention**: Keeps valuations artificially low
- **Data poverty**: Transaction records exist but are not processed or tabulated
- **Heuristics overload**: Valuers rely on mental shortcuts due to missing data

### Recommendations
- **Table** for the 4 problems with icons
- Consider flow diagram showing agency fragmentation
- Optional: Timeline showing 3-year SMV update requirement vs actual compliance

### Speaker Notes
> "The Philippines has the same structural gap. Only 60% of LGUs updated zonal values over 4 years, and just 37% submitted market schedules. But beyond the numbers, the system is fragmented — BIR, LGUs, and LRA all have overlapping mandates and produce different values for the same property. Political pressure keeps valuations low, and assessors often lack standardized training."

### Q&A Footnotes
- **Zonal Values**: BIR-set minimum property values per geographic zone for Capital Gains Tax (6%) and Documentary Stamp Tax. Updated irregularly. Often lower than market.
- **Market Value Schedules (SMV)**: LGU-maintained fair market values for Real Property Tax. Should update every 3 years per RA 7160 (Local Government Code).
- **TRAIN Law (2017)**: Required automatic 3-year updates; compliance remains low.
- **LRA (Land Registration Authority)**: Maintains title records and transfers but lacks resources to tabulate data for valuation use.
- **Multiple valuations**: A property may have BIR zonal value (for tax), LGU SMV (for RPT), and appraiser's opinion (for bank loan) — often contradicting each other.
- **Heuristics**: Mental shortcuts valuers use when data is missing; introduces bias and inconsistency.

---

## SLIDE 4: Cebu Anchor — Agosto Study ⭐ (~2 min)

### Headline
**"The only Cebu-specific empirical study on land value determinants"**

### Content
**Top 5 Determinants (by Factor Loading)**
1. Accessibility to public transportation
2. Recreational facilities
3. Open spaces and parks
4. Environmental quality
5. Level of ownership

### Methodology
| Aspect     | Detail                       |
| ---------- | ---------------------------- |
| Sample     | 51 practitioners             |
| Variables  | 31 tested → 11 factors (PCA) |
| Limitation | Residential properties only  |

### Recommendations
- **Numbered list with icons** for determinants
- Add "PRIMARY REFERENCE" badge
- Optional: Cebu map showing 15 sampled vicinities

### Speaker Notes
> "Agosto is my primary local reference — the only Cebu-specific study. He identified transport access as the strongest driver, followed by recreational facilities. However, this is survey-based, not transaction-based — where my thesis differs."

### Q&A Footnotes
- **Factor Loading**: A coefficient (0 to 1) indicating how strongly a variable correlates with a factor in PCA. Higher loading = stronger contribution.
- **PCA (Principal Component Analysis)**: Dimensionality reduction technique that groups correlated variables into fewer "factors." Used here to reduce 31 variables to 11.
- **Survey-based vs Transaction-based**: Agosto relied on practitioner opinions; my thesis uses actual transaction data (foreclosure prices, listing prices).

---

## SLIDE 5: ML Beats Traditional (~1.5 min)

### Headline
**"Tree-based models outperform neural networks on small data"**

### Content (Tanzania — Nyanda et al., 2024)
| Model          | MAPE         |
| -------------- | ------------ |
| Neural Network | **108.6%** ❌ |
| Random Forest  | 52.7%        |
| **Boosting**   | **48.0%** ✅  |

### Study Details
| Aspect       | Detail                                       |
| ------------ | -------------------------------------------- |
| Sample       | 954 observations (524 formal + 430 informal) |
| Training set | Only **419** observations (formal market)    |
| Features     | Location, structural, temporal, proximity    |

### Neural Network Architecture
- **Type**: Feedforward / Multilayer Perceptron
- **Layers**: 2 hidden layers
- **Neurons**: 4-5 in Layer 1, 2-5 in Layer 2
- **Regularization**: L2 penalty = 3

### Why NN Failed
1. **Too few samples**: 419 training points is far too small for deep learning
2. **High variance data**: Outliers and heterogeneity confused the model
3. **Poor generalization**: Overfitted to training noise, failed on test set

### Recommendations
- **Bar chart** comparing MAPE values
- Red for NN failure, green for Boosting
- Optional: Small NN diagram showing 2-layer architecture

### Speaker Notes
> "Tanzania tested ML on a dual formal-informal market — similar to Cebu. The neural network had only 2 hidden layers with 4-5 neurons, but even with regularization, it failed catastrophically at 108% error. Why? Only 419 training samples — far too few for deep learning. Boosting achieved 48% because tree-based models handle small, noisy data better."

### Q&A Footnotes
- **MAPE (Mean Absolute Percentage Error)**: Average of |Actual - Predicted| / Actual × 100%. 108% means predictions were off by more than the actual value.
- **Feedforward NN / MLP**: Neural network where information flows one direction from input to output; no recurrence or memory.
- **L2 Regularization**: Adds penalty for large weights to prevent overfitting; didn't save NN here because problem was data volume, not complexity.
- **Random Forest**: Ensemble of decision trees; robust to overfitting on small data.
- **Boosting**: Sequential ensemble where each tree corrects previous errors; often best for tabular data.
- **Formal vs Informal market**: Formal = registered titles, bank-financed; Informal = customary tenure, cash transactions.
- **Sample size guideline**: Neural networks typically need **10-25× more data** than tree-based models to perform well. Tanzania's 419 training samples worked for RF/Boosting but was far too small for NN.

---

## SLIDE 6: Text Features Add Value (~1.5 min)

### Headline
**"Listing descriptions contain predictive signal"**

### Content (Ottawa — Zhang et al., 2024)
| Metric | Value                       |
| ------ | --------------------------- |
| Sample | 10,251 listings             |
| Method | Self-trained Word2Vec + DNN |
| R²     | **0.79**                    |

### Key Finding
> **Self-trained Word2Vec outperformed pre-trained BERT by 44%**

### Implication
- Lamudi/DotProperty listing text could provide similar gains
- Domain-specific training > generic pre-trained models

### Recommendations
- Single **stat card** layout
- Highlight the 44% improvement
- Show example listing text if space permits

### Speaker Notes
> "The Ottawa study shows listing descriptions — like 'corner lot with garden' — have predictive value. Their self-trained Word2Vec achieved R² of 0.79, beating pre-trained BERT. If we process Lamudi text, we may see similar gains."

### Q&A Footnotes
- **Word2Vec**: Neural network that converts words to dense vectors where similar words have similar vectors. "Self-trained" = trained on domain-specific listing data.
- **BERT**: Bidirectional Encoder Representations from Transformers. Pre-trained language model from Google. "Pre-trained" = trained on general web text, not real estate.
- **R² (R-squared)**: Proportion of variance explained by the model (0 to 1). 0.79 = model explains 79% of price variation.
- **DNN (Deep Neural Network)**: Multi-layer neural network used here to combine text embeddings with property features.

---

## SLIDE 7: Macro Factors (~1 min)

### Headline
**"Exchange rates predict property values better than inflation"**

### Content (Nigeria — Nworah et al., 2023)
| Variable      | Correlation    |
| ------------- | -------------- |
| Exchange Rate | **r = -0.925** |
| Inflation     | r = -0.508     |

### Philippine OFW Context
| Metric           | Value                                                | Source |
| ---------------- | ---------------------------------------------------- | ------ |
| 2024 Remittances | **USD 38.3 billion** (record high)                   | BSP    |
| YoY Growth       | +3.0%                                                | BSP    |
| Central Visayas  | "Sustained demand for residential/commercial spaces" | NEDA   |

### Cebu Implication
> Peso depreciation → More PHP per USD → Higher OFW buying power → Real estate demand ↑

### Recommendations
- **Two large numbers** side-by-side for correlation
- Add OFW remittance stat card
- Optional: USD/PHP trend chart

### Speaker Notes
> "Exchange rate has a stronger correlation with property values than inflation. For Cebu, this is critical — 2024 remittances hit a record USD 38.3 billion nationally. When the peso weakens, OFW families receive more pesos per dollar, increasing buying power for real estate."

### Q&A Footnotes
- **r = -0.925**: Pearson correlation. Negative = inverse relationship. Very high magnitude.
- **OFW remittances**: Overseas Filipino Workers send USD; converted to PHP at prevailing rates.
- **BSP (Bangko Sentral ng Pilipinas)**: Central bank; publishes monthly remittance data.
- **Central Visayas (Region VII)**: Includes Cebu, Bohol, Siquijor, Negros Oriental. Major OFW source region.

---

## SLIDE 8: Risk & Compliance (~1.5 min)

### Headline
**"Models augment — they don't replace — professional judgment"**

### IMF (International Monetary Fund) House-Prices-at-Risk
| Market Type        | 5th Percentile Risk | Meaning                             |
| ------------------ | ------------------- | ----------------------------------- |
| Emerging Markets   | **-12%**            | Worst 5% scenario = 12% price crash |
| Advanced Economies | -10.5%              | Lower downside risk                 |

### Risk Drivers (Emerging Markets)
- **Financial tightening**: +0.3-0.7 pp downside risk
- **Credit booms**: +1.0 pp at medium-term horizon
- **Overvaluation**: +0.7-1.0 pp correction signal

### IVS 2025 (International Valuation Standards) AVM Requirements
| Requirement                  | Detail                                                 |
| ---------------------------- | ------------------------------------------------------ |
| **No standalone compliance** | AVM alone cannot produce IVS-compliant valuation       |
| **Valuer oversight**         | Must apply professional judgment on inputs/outputs     |
| **Four characteristics**     | Accuracy, Completeness, Timeliness, Transparency       |
| **Documentation**            | Model selection, inputs, limitations must be justified |

### Thesis Positioning
> **Our model = Decision Support Tool with SHAP transparency**

### Recommendations
- **Split layout**: Risk metrics (left) | IVS requirements (right)
- IVS quote in callout box
- Consider adding China as emerging market example

### Speaker Notes
> "Two final considerations. The IMF found emerging markets face 5% probability of a 12% crash — banks need buffers. Credit booms and overvaluation increase this risk. And IVS 2025 is explicit: no AVM alone can be compliant. It requires valuer judgment, accuracy, completeness, timeliness, and transparency. My thesis addresses this through SHAP explainability."

### Q&A Footnotes
- **House-prices-at-risk (HaR)**: IMF's adaptation of Value-at-Risk for real estate. 5th percentile = worst 5% of outcomes.
- **pp (percentage point)**: Absolute change in percentage, not relative.
- **IVS 2025**: Effective January 31, 2025. Emphasizes data quality (IVS 104) and human oversight (IVS 105).
- **AVM (Automated Valuation Model)**: Computer-generated estimate; must be reviewed by qualified valuer.
- **Four characteristics**: Accuracy (error-free), Completeness (all features), Timeliness (current market), Transparency (understood limitations).
- **China example**: IMF notes high volatility, credit-to-GDP gaps, and regional disparities in house prices at risk.

---

## SLIDE 9: Synthesis (~2 min)

### Headline
**"The literature provides the toolkit. Cebu is the missing case study."**

### What Literature Agrees On
1. ✅ Data scarcity is THE core problem
2. ✅ Tree-based ML (RF/XGBoost) beats NN on small data
3. ✅ Text features add 10-44% accuracy
4. ✅ Models must support, not replace, humans

### The Gap
> **No Cebu-specific, transaction-based, ML-augmented model exists.**

### Thesis Contribution
- First Cebu model using actual transaction data
- Hybrid: BDO foreclosures (floor) + Lamudi (ceiling) + **broker consultations**
- SHAP interpretability for IVS compliance

### Recommendations
- **Checklist visual** for agreement points
- Bold highlight for "The Gap"
- 3 icons/cards for thesis contribution

### Speaker Notes
> "The literature agrees: data scarcity is the problem, tree-based ML works, text helps, and human judgment is required. But no Cebu-specific model exists. My thesis fills this gap using foreclosure + listing data with XGBoost and SHAP."

### Approaches Considered but Rejected
- **Satellite luminosity proxies**: Not useful for Grade B-C countries like Philippines (Chen & Nordhaus, 2011)

### Q&A Footnotes
- **SHAP (SHapley Additive exPlanations)**: Game theory-based method to explain individual predictions. Shows which features increased or decreased the predicted value.
- **Floor/Ceiling pricing**: Foreclosures represent distressed (low) prices; online listings represent asking (high) prices. True market value lies between.
- **Transaction-based**: Using actual sale/foreclosure prices rather than surveys or opinions.
- **Chen & Nordhaus (2011)**: Found luminosity data adds <3% value for countries with decent statistics.

---

## Paper Reference Summary

| #   | Paper                   | Slide |
| --- | ----------------------- | ----- |
| 1   | Cheloti & Mooya (Kenya) | 2     |
| 2   | Ajibola (Lagos)         | 2     |
| 3   | TPS 2023 (Philippines)  | 3     |
| 4   | Agosto (Cebu) ⭐         | 4     |
| 5   | Nyanda (Tanzania)       | 5     |
| 6   | Ottawa Word2Vec         | 6     |
| 7   | Nworah (Nigeria)        | 7     |
| 8   | IMF VaR                 | 8     |
| 9   | IVS 2025                | 8     |

*Chen & Nordhaus (2011) mentioned in Slide 9 footnote as rejected approach*
