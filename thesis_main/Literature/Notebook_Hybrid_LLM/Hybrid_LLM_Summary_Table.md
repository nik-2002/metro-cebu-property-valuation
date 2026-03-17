# Hybrid LLM + Traditional ML Literature: Summary Table

**Research Question**: Can LLM embeddings (BERT, Word2Vec, GPT) enhance traditional ML models for real estate valuation?

---

## Overview Table

| #   | Paper                       | Location        | Sample Size | Method                         | Best R²      | Key Finding                         |
| --- | --------------------------- | --------------- | ----------- | ------------------------------ | ------------ | ----------------------------------- |
| 01  | Multimodal ML Survey (UTS)  | Global (Survey) | N/A         | 5-Modality Framework           | N/A          | Multimodal > single-modality by 2%+ |
| 02  | MHPP (BUET/Monash)          | Melbourne, AU   | 52,851      | SBERT + CLIP + GSNE + LightGBM | 0.112 MAE    | 26% MAE improvement                 |
| 03  | Describe the House (Ottawa) | Canada          | 10,251      | Self-trained Word2Vec + DNN    | **0.79**     | Word2Vec beats BERT by 44%          |
| 04  | Shanghai Lane Houses        | Shanghai, CN    | 2,549       | ChatGPT 10-shot                | **0.80**     | LLM beats Random Forest             |
| 05  | UConn Uniqueness            | Atlanta, GA     | 40,918      | Paragraph Vector + Hedonic     | 5.6% premium | Text uniqueness = soft value        |
| 06  | Baidoa Hybrid               | Somalia         | 118         | ANN + Hedonic                  | 0.74         | 20% error reduction                 |
| 07  | Seattle BERT ROI            | Seattle, WA     | 4,600       | BERT + XGBoost Stacking        | 0.78         | 11% MAE reduction from text         |
| 08  | Malaysia Sentiment          | Malaysia        | N/A         | BERT Sentiment + ARIMA/LSTM    | r=0.78       | 20% accuracy improvement            |

---

## By Embedding Type

### BERT-Based
| Paper         | Pre-trained or Fine-tuned | Performance             |
| ------------- | ------------------------- | ----------------------- |
| 03 (Ottawa)   | Pre-trained (frozen)      | **Worst** (vs Word2Vec) |
| 07 (Seattle)  | Pre-trained               | 11% MAE reduction       |
| 08 (Malaysia) | Fine-tuned multilingual   | r=0.78 correlation      |

### Word2Vec
| Paper       | Training                   | Performance        |
| ----------- | -------------------------- | ------------------ |
| 03 (Ottawa) | **Self-trained on domain** | **Best** (R²=0.79) |

### LLM (ChatGPT)
| Paper         | Method            | Performance    |
| ------------- | ----------------- | -------------- |
| 04 (Shanghai) | 10-shot prompting | R²=0.80 (best) |

---

## By Sample Size

| Sample Range | Papers                                                | Key Insight                                 |
| ------------ | ----------------------------------------------------- | ------------------------------------------- |
| **<500**     | Baidoa (118)                                          | Hybrid hedonic+ANN works with small samples |
| **1K–5K**    | Shanghai (2,549), Seattle (4,600)                     | LLM prompting viable                        |
| **10K–50K**  | Ottawa (10,251), Atlanta (40,918), Melbourne (52,851) | Full multimodal pipelines effective         |

---

## Key Takeaways for Cebu

### Sample Size: ~1,000–3,000 (Estimated)
**Most Applicable Papers**: 
- Baidoa (n=118): Proves hybrid works with small samples
- Shanghai (n=2,549): ChatGPT 10-shot viable
- Ottawa (n=10,251): Self-trained Word2Vec possible if ~5,000+ listings

### Recommended Approach (Ranked)
1. **Self-trained Word2Vec + XGBoost** (Ottawa approach)
   - Requires: 5,000+ listings with descriptions
   - Expected: R² ~0.70–0.79
   
2. **ChatGPT 10-shot Prompting** (Shanghai approach)
   - Requires: ~10 examples per prediction type
   - Expected: R² ~0.70–0.80
   - Limitation: Higher compute cost

3. **Pre-trained BERT Embeddings** (Seattle approach)
   - Requires: Any sample size (frozen BERT)
   - Expected: 10–15% MAE reduction
   - Limitation: May miss domain-specific vocabulary

### Text Features Worth Exploring
| Feature Type             | Evidence                | Paper    |
| ------------------------ | ----------------------- | -------- |
| **Listing descriptions** | 44% better than no-text | Ottawa   |
| **Uniqueness score**     | 5.6% price premium      | UConn    |
| **Sentiment index**      | r=0.78 with prices      | Malaysia |

### Language Considerations
- Cebu listings: Mixed Filipino/English
- Need multilingual BERT (Malaysia paper) or self-trained Word2Vec (Ottawa paper)
- Consider augmenting with Manila data for vocabulary

---

## IVS Compliance Considerations

| Concern           | Solution                     | Paper Reference         |
| ----------------- | ---------------------------- | ----------------------- |
| Black box problem | Use SHAP values with XGBoost | Survey (01)             |
| Interpretability  | Hybrid hedonic + ML          | Baidoa (06), UConn (05) |
| Algorithmic bias  | Test across property types   | Seattle (07)            |

---

**Total Literature Captured**: 8 papers from 8 countries (Australia, Bangladesh, Canada, China, Greece, Malaysia, Somalia, USA)

**NotebookLM Notebook ID**: 23f2f622-c012-4ec8-999b-6a69c5949e23

---

*Generated: 2026-02-04*
