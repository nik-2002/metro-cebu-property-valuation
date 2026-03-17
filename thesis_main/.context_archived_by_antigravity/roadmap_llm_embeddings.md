# Research Roadmap: LLM Embeddings for Real Estate Valuation

> **Purpose**: Track exploration of hybrid LLM + traditional ML approach. Prevent rabbit holes.

> [!CAUTION]
> **STATUS: ❌ OUT OF SCOPE (2026-02-26)**
> Per thesis proposal panel decision, NLP feature extraction has been **removed** from the thesis scope. The core contribution is now GIS/geospatial feature engineering. This roadmap is preserved for reference but is **no longer active**.

## Current Status
- [x] Identified limitation of full LLM fine-tuning (data scarcity)
- [x] Identified promising alternative: **LLM embeddings as features**
- [x] Literature search on hybrid approaches ✅ **8 papers reviewed**
- [x] Feasibility assessment for Cebu data ✅ **See below**
- [x] Decision: incorporate into thesis or not → **❌ REMOVED — Panel directed focus to GIS/geocoding instead (2026-02-26)**

---

## The Core Idea

```
[Listing Text] → [LLM Embeddings] → [Random Forest/XGBoost] → [Price]
     ↓                                        ↑
"3BR corner lot,                    + sqm, location, roof type
 near Ayala, renovated"               (structured features)
```

**Why this works** (per literature):
- Text adds **10-26% accuracy improvement** across all studies
- Self-trained Word2Vec outperforms pre-trained BERT by **44%** (Ottawa paper)
- Works with small samples: Baidoa (n=118), Shanghai (n=2,549)

---

## Literature Review Summary (Completed 2026-02-04)

| Paper             | Location | n    | Method                    | Result                     |
| ----------------- | -------- | ---- | ------------------------- | -------------------------- |
| UTS Survey        | Global   | -    | 5-Modality Framework      | Multimodal > single by 2%+ |
| MHPP (Melbourne)  | AU       | 52K  | SBERT+CLIP+LightGBM       | 26% MAE improvement        |
| **Ottawa (Best)** | CA       | 10K  | **Self-trained Word2Vec** | **R²=0.79**                |
| Shanghai          | CN       | 2.5K | ChatGPT 10-shot           | R²=0.80                    |
| UConn             | USA      | 41K  | Paragraph Vector          | 5.6% price premium         |
| Baidoa            | Somalia  | 118  | ANN+Hedonic               | 20% error reduction        |
| Seattle           | USA      | 4.6K | BERT+Stacking             | 11% MAE reduction          |
| Malaysia          | MY       | -    | BERT Sentiment            | r=0.78 correlation         |

**Key Finding**: **Self-trained Word2Vec beats pre-trained BERT** in real estate domain.

📁 Full summaries: `Literature/Hybrid_LLM_Traditional_ML_RRL/`

---

## Decision Criteria Assessment

| Criterion            | Threshold          | ✅/❌ | Evidence                                |
| -------------------- | ------------------ | --- | --------------------------------------- |
| **Data requirement** | <2,000 samples     | ✅   | Baidoa (n=118), Shanghai (n=2,549) work |
| **Interpretability** | SHAP support       | ✅   | XGBoost + SHAP (Survey recommendation)  |
| **Compute**          | Consumer GPU/cloud | ✅   | Word2Vec trains on CPU; BERT frozen     |
| **Novelty**          | Adds to Cebu Model | ✅   | No Philippine hybrid studies found      |

**Verdict**: ✅ All criteria met

---

## Recommended Approach for Cebu

### Option 1: Self-Trained Word2Vec + XGBoost ⭐ RECOMMENDED
- **Requirement**: ~5,000+ listings with descriptions
- **Expected**: R² ~0.70–0.79
- **Pros**: Best domain-specific performance, low compute
- **Cons**: Needs sufficient corpus

### Option 2: ChatGPT 10-Shot Prompting
- **Requirement**: ~10 examples per property type
- **Expected**: R² ~0.70–0.80
- **Pros**: Works with minimal data
- **Cons**: Higher inference cost, API dependency

### Option 3: Pre-Trained BERT (Frozen)
- **Requirement**: Any sample size
- **Expected**: 10–15% MAE reduction
- **Cons**: Misses Cebuano/Filipino vocabulary

---

## Language Considerations for Cebu

- Listings: Mixed **Filipino/English**
- Options:
  1. Self-train Word2Vec on Cebu corpus (best if n>5,000)
  2. Use multilingual BERT (Malaysia paper approach)
  3. Augment with Manila listings for vocabulary

---

## Next Steps

1. [ ] Assess actual Cebu listing count (need ~5,000+ for Word2Vec)
2. [ ] Extract sample listing descriptions to assess text quality
3. [ ] Make final decision on approach (Word2Vec vs ChatGPT)
4. [ ] If proceeding, add to thesis Chapter 3 Methodology
5. [ ] Update thesis scope document

---

*Created: 2026-02-04 | Updated: 2026-02-04 (Literature review complete)*
