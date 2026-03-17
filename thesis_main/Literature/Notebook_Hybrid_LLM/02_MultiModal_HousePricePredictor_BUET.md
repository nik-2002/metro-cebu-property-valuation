# A Multi-Modal Deep Learning Based Approach for House Price Prediction

**Source**: NotebookLM Direct Query (LLM Embeddings Research Notebook)

---

## Bibliographic Context

- **Title**: A Multi-Modal Deep Learning Based Approach for House Price Prediction
- **Authors**: 
  - Md Hasebul Hasan (BUET, Bangladesh)
  - Md Abid Jahan (BUET, Bangladesh)
  - Mohammed Eunus Ali (BUET, Bangladesh)
  - Yuan-Fang Li (Monash University, Australia)
  - Timos Sellis (Athena Research Center, Greece)
- **Affiliation**: Bangladesh University of Engineering and Technology; Monash University; Athena Research Center
- **Publication**: arXiv (2024)
- **Code Repository**: https://github.com/4P0N/mhpp
- **Keywords**: #MultiModal #BERT #CLIP #HousePricePrediction #DeepLearning #GeoSpatial

---

## Abstract

> "Accurate prediction of house price, a vital aspect of the residential real estate sector, is of substantial interest for a wide range of stakeholders. However, predicting house prices is a complex task due to the significant variability influenced by factors such as house features, location, neighborhood, and many others. Despite numerous attempts utilizing a wide array of algorithms, including recent deep learning techniques, to predict house prices accurately, existing approaches have fallen short of considering a wide range of factors such as textual and visual features. This paper addresses this gap by comprehensively incorporating attributes, such as features, textual descriptions, geo-spatial neighborhood, and house images, typically showcased in real estate listings in a house price prediction system."

---

## Research Objective

**Primary Goal**: Propose a Multi-Modal House Price Predictor (MHPP) that comprehensively incorporates four key components:
1. Raw house features
2. Spatial neighborhood information
3. Textual descriptions
4. House images

**Hypothesis**: Learning a joint embedding of these diverse data types will "significantly improve the house price prediction accuracy."

---

## Methodology: MHPP Architecture

The framework uses **four parallel processing streams** that converge via **concatenation fusion**:

### 1. Raw Features Stream
- Processes standard tabular data (e.g., number of rooms, bathrooms, parking, air conditioning)
- **43 distinct attributes** per property

### 2. Geo-Spatial Stream (GSNE)
- **Geo-Spatial Network Embedding (GSNE)** captures location and neighborhood impact
- Constructs a graph where nodes = houses and POIs (schools, bus stations)
- Captures **first-order proximity** (direct connections) and **second-order proximity** (intermediary connections)
- Uses **Gaussian encoder** to project nodes into Gaussian space

### 3. Text Stream (SBERT)
- **Sentence-BERT (SBERT)** processes advertisement textual descriptions
- Captures aesthetic features and intricate details not in raw data
- Produces fixed-size **384-dimensional** semantic vectors
- **Optimal dimension after PCA**: 128 dimensions

### 4. Image Stream (CLIP)
- **CLIP (Contrastive Learning Image Pre-training)** extracts image embeddings
- Architecture: **ResNet50** (image encoder) + **DistilBERT** (text encoder)
- Captures visual condition and layout
- **Optimal dimension**: 256 dimensions

### Fusion Strategy
Concatenation of all embeddings into unified vector:
```
V = F_raw | GE | TE | IE
```
Where:
- F_raw = raw features
- GE = geo-spatial embedding
- TE = text embedding (SBERT)
- IE = image embedding (CLIP)

---

## Dataset: Melbourne, Australia

| Attribute        | Value                                                  |
| ---------------- | ------------------------------------------------------ |
| **Source**       | Prominent real estate website                          |
| **Location**     | Melbourne, Australia                                   |
| **Size**         | **52,851** transaction records                         |
| **Timeframe**    | 2013–2015                                              |
| **Raw Features** | 43 attributes per property                             |
| **POIs**         | 13,340 regions, 709 schools, 218 train stations        |
| **Text**         | Up to 280 words per listing                            |
| **Images**       | Average of 5 images per property (interior + exterior) |

---

## Results and Performance Metrics

### Metrics Used
- **MAE (Mean Absolute Error)**
- **RMSE (Root Mean Squared Error)**
- **Note**: R² and MAPE not reported

### Best Performing Configuration: Raw + GSNE + Text + Image

| Regression Model    | MAE       | RMSE     |
| ------------------- | --------- | -------- |
| **LightGBM** (Best) | **0.112** | **0.16** |
| XGBoost             | 0.115     | 0.164    |
| Gradient Boosting   | 0.116     | 0.169    |
| Kernel Ridge        | 0.12      | 0.168    |
| Elastic Net         | 0.151     | 0.211    |
| Lasso               | 0.159     | 0.223    |

### Comparison to Baselines

#### Raw Features Baseline
| Model    | Raw MAE | Multimodal MAE | Improvement |
| -------- | ------- | -------------- | ----------- |
| LightGBM | 0.135   | 0.112          | 17.0%       |
| Lasso    | 0.251   | 0.159          | 36.7%       |

#### State-of-the-Art Baseline (Raw + GSNE)
| Model           | Baseline MAE | Multimodal MAE | MAE Improvement | RMSE Improvement |
| --------------- | ------------ | -------------- | --------------- | ---------------- |
| **Elastic Net** | 0.205        | 0.151          | **26.34%**      | **26.99%**       |
| Lasso           | 0.209        | 0.159          | 23.92%          | 23.10%           |
| XGBoost         | 0.132        | 0.115          | 12.88%          | 12.30%           |
| LightGBM        | 0.127        | 0.112          | 11.81%          | 11.11%           |

### Impact of Individual Modalities (Ablation)

| Configuration               | Lasso MAE |
| --------------------------- | --------- |
| Baseline (Raw + GSNE)       | 0.209     |
| Baseline + Text             | 0.175     |
| Baseline + Image            | 0.165     |
| **Baseline + Text + Image** | **0.159** |

**Key Finding**: Image embeddings had slightly stronger impact than text for some models, but combination yields best results.

---

## Optimal Embedding Dimensions

| Modality     | Full Dimension | Optimal After PCA |
| ------------ | -------------- | ----------------- |
| Text (SBERT) | 384            | **128**           |
| Image (CLIP) | 512            | **256**           |

**Critical Note**: Reducing text embedding below 128 dimensions caused information loss and increased error.

---

## Limitations

1. **Geographic Specificity**: Evaluated only on Melbourne dataset; generalizability to other markets not demonstrated
2. **Sensitivity to Dimensionality**: Downsampling embeddings too much leads to information loss
3. **Excluded Data Types**: Does not account for social security data or social media trends

---

## Future Research Directions

1. **Complex Real-Life Data**: Integrate social security data and social media trends
2. **Broader Dataset**: Test on multiple cities with different market characteristics
3. **Dynamic Factors**: Incorporate temporal changes in neighborhood desirability

---

## Key Conclusions

1. **Multi-modal outperforms single-modality**: MHPP outperformed state-of-the-art GSNE-based methods by up to **26% MAE improvement**
2. **Text and images are critical**: Adding text and image embeddings provides significant accuracy gains
3. **Pre-trained models work**: SBERT for text and CLIP for images effectively capture nuanced features
4. **LightGBM is best downstream model**: Achieved lowest MAE (0.112) and RMSE (0.16)
5. **Embedding dimension matters**: 128 for text, 256 for images optimal balance

---

## Thesis Utility: "The Cebu Model"

### Direct Applications
- **Model Architecture**: Replicate MHPP pipeline with:
  - SBERT for listing descriptions (Filipino/Cebuano may need multilingual SBERT)
  - Consider simpler image pipeline (CLIP may be overkill for small data)
  - XGBoost/LightGBM as downstream regressor
- **Embedding Dimensions**: Use 128 for text, 256 for images as starting point
- **Fusion Strategy**: Concatenation is simple and effective

### Feasibility Assessment for Cebu
| Requirement | Melbourne         | Cebu (Estimated)          |
| ----------- | ----------------- | ------------------------- |
| Sample size | 52,851            | ~1,000–3,000              |
| Text data   | 280 words/listing | Available from listings   |
| Image data  | 5 images/property | Available but variable    |
| POI data    | 13,340 regions    | Available via Google Maps |

**Challenge**: Melbourne had 50x+ more samples. May need to simplify architecture or use frozen pre-trained embeddings without fine-tuning.

---

## Critical Quotes

> "The text embedding of the house advertisement description and image embedding of the house pictures in addition to raw attributes and geo-spatial embedding, can significantly improve the house price prediction accuracy."

> "The comprehensive model achieved the lowest error rates across various regression algorithms."

> "Adding text embedding to the baseline significantly improved accuracy. For Lasso, the MAE dropped from 0.209 to 0.175."

> "The combination of both text and image embeddings provided the highest accuracy, confirming that integrating all relevant elements yields the best predictive capacity."

---

*Summary generated: 2026-02-04 | Source: NotebookLM Deep Research*
