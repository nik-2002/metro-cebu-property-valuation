# RRL Presentation: Narrative Outline (v2)

> **Thesis**: Data-Driven Property Valuation Model for Cebu City  
> **Format**: 10 slides | 15 mins (+ 5 min Q&A)  
> **Papers**: 11 total (3 required with methodology + findings)

---

## Narrative Arc

```
GLOBAL PROBLEM → PH INSTITUTIONAL GAP → CEBU CASE → TECH SOLUTION
      ↓                  ↓                  ↓            ↓
"Data scarcity"    "BIR zonal lags"    "Agosto study"  "ML + hybrid data"
(Kenya, Lagos)     (TPS 2023)          (31 factors)    (Word2Vec, XGBoost)
```

---

## Slide Structure

### Slide 1: Title & Context (1 min)
- Thesis title, author, adviser
- Hook: *"Cebu's property market lacks accurate, data-driven valuation tools"*

---

### Slide 2: Global Problem — Data Scarcity (2 min)
**Papers**: Cheloti & Mooya (Kenya), Ajibola (Lagos), **TPS 2023 (Philippines)**

| Finding                             | Source      |
| ----------------------------------- | ----------- |
| "Limited information" = #1 problem  | Kenya       |
| 92.7% cite insufficient market data | Lagos       |
| Valuation error: +24% to +51%       | Lagos       |
| *[TPS 2023 Philippine finding]*     | Philippines |

**Narrative**: *"This isn't unique to Africa — the Philippines faces the same structural problem."*

**Info needed**:
- [ ] TPS 2023: Key Philippine-specific finding on data scarcity
- [ ] TPS 2023: Methodology and sample

---

### Slide 3: Philippine Context — Institutional Gap (1.5 min)
**Papers**: TPS 2023, Domingo & Fulleros (REPI) [footnote]

**Key points**:
- BIR zonal values lag behind market prices
- No unified real estate price index until REPI proposal
- Regional disparities in data infrastructure

**Narrative**: *"The Philippine system has documented gaps — this creates the opportunity for a data-driven solution."*

**Info needed**:
- [ ] TPS 2023: Specific institutional critique
- [ ] REPI: Year proposed, adoption status

---

### Slide 4: The Local Anchor — Cebu Study (2 min) ⭐
**Paper**: Agosto (Cebu City) — PRIMARY REFERENCE

**Key points**:
- Only Cebu-specific empirical study
- 31 factors: Mobility, Livability, Economic, Government, Ownership
- Survey of 52 practitioners + PCA + regression

**Narrative**: *"This is our foundation — but it's survey-based, not transaction-based."*

**Info needed**:
- [ ] Top 5 determinants by factor loading
- [ ] Limitations stated by author

---

### Slide 5: ML Beats Traditional — Tanzania Evidence (1.5 min)
**Paper**: Nyanda et al. (Tanzania)

| Model          | MAPE     |
| -------------- | -------- |
| Neural Network | 108.6% ❌ |
| Random Forest  | 52.4%    |
| Boosting       | 48.0% ✅  |

**Narrative**: *"Deep learning fails on small, noisy data. Tree-based models win."*

**Info needed**:
- [ ] Sample size (formal vs informal)
- [ ] Features used

---

### Slide 6: Text Features Add Value (1.5 min)
**Papers**: Ottawa Word2Vec, Shanghai ChatGPT

| Approach              | R²   | Insight                      |
| --------------------- | ---- | ---------------------------- |
| Self-trained Word2Vec | 0.79 | Domain-trained beats BERT    |
| ChatGPT 10-shot       | 0.80 | LLM viable for small samples |

**Narrative**: *"Listing descriptions contain signal — text features matter."*

**Info needed**:
- [ ] Ottawa sample size
- [ ] Text feature extraction method

---

### Slide 7: Macro Matters (1 min)
**Paper**: Nworah et al. (Nigeria)

- Exchange rate vs RE: r = **-0.925**
- Inflation vs RE: r = **-0.508**

**Narrative**: *"OFW remittances flow through exchange rates — this matters for Cebu."*

---

### Slide 8: Proxy Data for Data-Poor Regions (1 min)
**Paper**: Chen & Nordhaus (Luminosity)

- Optimal weight: ~30% for Grade D (poor stats), <3% for Grade A-C
- Measurement error ≥25%

**Narrative**: *"Satellite data helps — but don't trust it 100%."*

---

### Slide 9: Risk & Compliance (1.5 min)
**Papers**: IMF VaR, IVS 2025

| Source   | Key Point                                                                        |
| -------- | -------------------------------------------------------------------------------- |
| IMF      | 5% probability of 12% crash in emerging markets                                  |
| IVS 2025 | "No model without professional judgement... can produce IVS-compliant valuation" |

**Narrative**: *"Our model augments appraisers — it doesn't replace them."*

---

### Slide 10: Synthesis — The Cebu Gap (2 min)
**Key points**:
1. Literature agrees: Data scarcity is the core problem
2. Tree-based ML (RF/XGBoost) outperforms NN on small data
3. Text features add 10-44% accuracy
4. **Gap**: No Cebu-specific, transaction-based, ML-augmented model exists

**Narrative**: *"The literature gives us the toolkit — Cebu is the missing case study."*

---

## Paper Summary Table

| #   | Paper                      | Role                      | Layer          |
| --- | -------------------------- | ------------------------- | -------------- |
| 1   | Cheloti & Mooya (Kenya)    | Data scarcity #1 problem  | Global         |
| 2   | Ajibola (Lagos)            | 92.7% cite bad data       | Global         |
| 3   | **TPS 2023 (Philippines)** | PH-specific evidence      | **Philippine** |
| 4   | Agosto (Cebu) ⭐            | 31 determinants           | **Cebu**       |
| 5   | Nyanda et al. (Tanzania)   | RF beats NN               | Method         |
| 6   | Ottawa Word2Vec            | Self-trained embeddings   | Method         |
| 7   | Shanghai ChatGPT           | LLM 10-shot               | Method         |
| 8   | Nworah (Nigeria)           | Exchange rate > inflation | Features       |
| 9   | Chen & Nordhaus            | Luminosity weighting      | Features       |
| 10  | IMF VaR                    | 12% crash buffer          | Risk           |
| 11  | IVS 2025                   | Human oversight required  | Compliance     |

---

## Information Checklist

| Slide | Paper            | Missing Info                      |
| ----- | ---------------- | --------------------------------- |
| 2-3   | TPS 2023         | PH-specific findings, methodology |
| 4     | Agosto           | Top 5 determinants, limitations   |
| 5     | Tanzania         | Sample split, features            |
| 6     | Ottawa, Shanghai | Sample sizes, text methods        |

---

*Ready for NotebookLM queries*
