# Describe the House and I Will Tell You the Price: House Price Prediction with Textual Description Data

**Source**: NotebookLM Direct Query (LLM Embeddings Research Notebook)

---

## Bibliographic Context

- **Title**: Describe the House and I Will Tell You the Price: House Price Prediction with Textual Description Data
- **Authors**: Hanxiang Zhang, Yansong Li, Paula Branco (Corresponding)
- **Affiliation**: School of Electrical Engineering and Computer Science, University of Ottawa, Ottawa, ON, Canada
- **Publication**: *Natural Language Engineering* (2024), Cambridge University Press
- **Keywords**: #NLP #Word2Vec #BERT #HousePricePrediction #TextEmbeddings #Regression

---

## Abstract

> "House price prediction is an important problem that could benefit home buyers and sellers. Traditional models for house price prediction use numerical attributes such as the number of rooms but disregard the house description text. The recent developments in text processing suggest these can be valuable attributes, which motivated us to use house descriptions. This paper focuses on the house asking/advertising price and studies the impact of using house description texts to predict the final house price. We processed the description text through three word embedding techniques: TF-IDF, Word2Vec, and BERT. Our results show that by using exclusively the description data with Word2Vec and a Deep Learning model, we can achieve good performance. An R² of 0.7904 is achieved by the deep learning model using only description data on the testing data."

---

## Research Questions

1. **Can house description text improve price prediction** compared to traditional models using only numerical attributes?
2. **Which embedding technique performs best**: TF-IDF, Word2Vec, or BERT?
3. **What is the optimal feature combination**: text-only, non-text-only, or combined?

---

## Dataset: Ontario, Canada

| Attribute        | Value                                                                                      |
| ---------------- | ------------------------------------------------------------------------------------------ |
| **Source**       | Major Canadian real estate listing website (web crawler)                                   |
| **Location**     | Greater Golden Horseshoe Region, Ontario: Ottawa, Toronto, Mississauga, Brampton, Hamilton |
| **Raw Size**     | 10,418 listings                                                                            |
| **Cleaned Size** | **10,251 listings**                                                                        |
| **Data Split**   | 90% training, 10% testing                                                                  |
| **Validation**   | 4 repetitions × 10-fold cross-validation + grid search                                     |

---

## Methodology: Embedding Techniques

### 1. Word2Vec (Best Performer)

| Parameter               | Value                                                                                                |
| ----------------------- | ---------------------------------------------------------------------------------------------------- |
| **Preprocessing**       | Clean numbers, expand abbreviations ("bdrm"→"bedroom"), fix typos, remove punctuation, lemmatization |
| **Stop Words**          | NOT removed (preserves context)                                                                      |
| **Architecture**        | Continuous Skip-gram                                                                                 |
| **Training**            | **Self-trained on collected real estate data** (not pre-trained)                                     |
| **Vector Dimension**    | 300                                                                                                  |
| **Window Size**         | 8                                                                                                    |
| **Training Iterations** | 30                                                                                                   |
| **Sentence Embedding**  | Mean pooling of token embeddings                                                                     |

### 2. BERT (Worst Performer)

| Parameter            | Value                                    |
| -------------------- | ---------------------------------------- |
| **Preprocessing**    | None (BERT handles raw text)             |
| **Model**            | Pre-trained BERT base                    |
| **Training Source**  | Wikipedia + BooksCorpus (general corpus) |
| **Fine-tuning**      | None (used as feature extractor only)    |
| **Vector Dimension** | 768                                      |

### 3. TF-IDF (Baseline)
- Standard TF-IDF vectorization with stop word removal

---

## Regression Models Tested

1. **Linear Support Vector Regression (L-SVR)** — worst performer
2. **Random Forest (RF)**
3. **Gradient Boosting (GB)** — best for combined features
4. **Deep Neural Network (DNN)** — best for text-only

---

## Results: Performance Metrics

### Final Test Results (Held-Out 10%)

| Model Input      | Algorithm         | Embedding    | Test R²    | Test RMSE  |
| ---------------- | ----------------- | ------------ | ---------- | ---------- |
| Non-textual only | Gradient Boosting | N/A          | 0.6738     | 0.0155     |
| **Textual only** | **DNN**           | **Word2Vec** | **0.7904** | 0.0238     |
| Combined (All)   | Gradient Boosting | TF-IDF       | 0.7184     | **0.0144** |

**Key Findings**:
- **Best R²**: Text-only (DNN + Word2Vec) at **0.7904**
- **Best RMSE**: Combined (GB + TF-IDF) at **0.0144** (~$72,234 CAD error)

### BERT vs Word2Vec Comparison

| Embedding                   | DNN Validation R² | Performance |
| --------------------------- | ----------------- | ----------- |
| **Word2Vec** (self-trained) | 0.6041 ± 0.041    | **Best**    |
| BERT (pre-trained)          | 0.6021 ± 0.040    | Worst       |

**Word2Vec outperformed BERT**:
- Gradient Boosting: Word2Vec **43.54% better** in R² vs TF-IDF
- BERT consistently displayed worst scores for both R² and RMSE

**Why Word2Vec Won**:
- Word2Vec was **self-trained** on real estate-specific vocabulary
- BERT was pre-trained on general corpora (Wikipedia/BooksCorpus)
- Domain-specific training captured industry vocabulary better

### Text vs No-Text Baselines

| Comparison                        | Improvement                          |
| --------------------------------- | ------------------------------------ |
| Text-only R² vs Non-text R² (DNN) | **28.77% higher** (0.7904 vs 0.6738) |
| Combined R² vs Non-text R² (GB)   | 5.9% higher in validation            |
| Combined RMSE vs Non-text RMSE    | 0.0144 vs 0.0155 (better)            |

**Key Insight**: Text alone is a strong predictor—achieved highest R² of any configuration.

---

## Validation Results (Grid Search)

### Best R² Scores by Feature Type

| Feature Type     | Best Algorithm | Best R² (Validation) |
| ---------------- | -------------- | -------------------- |
| Non-textual only | Random Forest  | 0.6830 ± 0.034       |
| Textual only     | DNN + Word2Vec | 0.6041 ± 0.041       |
| All features     | GB + TF-IDF    | 0.7214 ± 0.034       |
| All features     | GB + Word2Vec  | 0.7107 ± 0.034       |

---

## Limitations

1. **Data Bias**: Descriptions written by experts to sell houses—may highlight specific characteristics to enhance perceived quality
2. **BERT Underperformance**: Pre-trained on general corpora, missed real estate-specific vocabulary
3. **SVR Limitations**: Linear SVR couldn't model non-linear price relationships
4. **Feature Overlap**: Random Forest showed no improvement when adding text, possibly due to information redundancy
5. **Error Margins**: RMSE indicates $72K–$122K CAD error margins—needs improvement
6. **Black Box**: Neural networks lack explainability

---

## Practical Implications

1. **Home Buyers**: Models can provide initial market value assessments
2. **Sellers**: Tool helps draft descriptions highlighting features for target price
3. **Text is Powerful**: Description alone achieves R² = 0.79—strong standalone predictor
4. **Best Practice**: Combine text + non-text for lowest absolute error

**Web Application**: Authors provide free tool at [URL] for price prediction from text descriptions only.

---

## Future Research Directions

1. **BERT Adaptation**: Fine-tune BERT on real estate corpus or develop domain-specific model
2. **Architecture Exploration**: Compare multiple neural network architectures
3. **Advanced Techniques**: GANs for oversampling, reinforcement learning for feature selection
4. **Explainability**: Explore neural-backed decision trees to address black box issue
5. **Generalizability**: Validate on different cities and countries
6. **Bias Investigation**: Analyze how different writing styles/audiences impact performance

---

## Thesis Utility: "The Cebu Model"

### Direct Applications
- **Self-Train Word2Vec**: Train on Cebu listing descriptions instead of using pre-trained BERT
- **Domain Vocabulary**: Filipino/Cebuano real estate terms (e.g., "subdivision," "barangay") need custom training
- **Embedding Dimension**: 300-dim Word2Vec with mean pooling is simple and effective

### Key Takeaway
> **Pre-trained BERT underperforms self-trained Word2Vec in real estate domain.** Domain-specific training matters more than model complexity.

### Feasibility for Cebu
| Requirement | Ottawa (This Study)   | Cebu (Estimated)        |
| ----------- | --------------------- | ----------------------- |
| Sample size | 10,251                | ~1,000–3,000            |
| Text length | Varies (descriptions) | Available from listings |
| Language    | English               | Mixed Filipino/English  |

**Challenge**: Need enough listings to self-train Word2Vec (~5,000+ recommended). May need to augment with Manila data.

---

## Critical Quotes

> "An R² of 0.7904 is achieved by the deep learning model using only description data on the testing data. This clearly indicates that using the house description text alone is a strong predictor for the house price."

> "Word2Vec outperformed TF-IDF by 43.54% in R² score for the Gradient Boosting model."

> "BERT consistently displayed the worst scores for both R² and RMSE compared to TF-IDF and Word2Vec."

> "The Word2Vec model was self-trained on the specific real estate description text collected for the study, allowing it to capture industry-specific vocabulary."

> "Combining the textual and non-textual features improves the learned model and provides performance benefits when compared against using only one of the feature types."

---

*Summary generated: 2026-02-04 | Source: NotebookLM Deep Research*
