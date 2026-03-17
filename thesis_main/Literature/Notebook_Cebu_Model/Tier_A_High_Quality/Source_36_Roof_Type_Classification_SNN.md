# Roof Type Classification with Innovative Machine Learning Approaches
**Source ID:** [Refined via Deep Search]
> **Abstract**: "SNN achieved 0.73 accuracy compared to 0.39 for CNN on small data... Low resolution imagery negatively impacted classification of Gable/Hip roofs."

## 0. Bibliographic Context
- **Citation (APA)**: Ölçer, N., Ölçer, D., & Sümer, E. (2023). Roof type classification with innovative machine learning approaches. *PeerJ Computer Science*, 9, e1268. doi:10.7717/peerj-cs.1268
- **Authors**: Naim Ölçer, Didem Ölçer, Emre Sümer
- **Affiliation**: Department of Computer Engineering, Başkent University, Ankara, Turkey
- **Publication**: PeerJ Computer Science (2023)
- **Study Context**: Computer Vision / Remote Sensing for building classification
- **Keywords**: #SiameseNeuralNetwork #OneShotLearning #RoofClassification #DataScarcity #CNN
- **Data Availability**: 
  - Training (Artificial): GitHub (`olcernaim/roof-type-classification`)
  - Test (Real): Alidoost & Arefi (2018) dataset (`loosgagnet/Building-detection-and-roof-type-recognition`)

## 1. Key Quantitative Findings

### Primary One-Shot Result (SNN trained on artificial data, tested on real data)
Average accuracy: **66.1%**

| Roof Type | Accuracy | Precision | Recall |
| --------- | -------- | --------- | ------ |
| **Flat**  | **99%**  | 0.65      | 0.99   |
| **Gable** | **47%**  | 0.70      | 0.47   |
| **Hip**   | **55%**  | 0.66      | 0.55   |

### SNN vs CNN on Real Data (Training Size Comparison)

| Training Size     | SNN Accuracy | CNN Accuracy |
| ----------------- | ------------ | ------------ |
| **1 sample**      | **55%**      | **0%**       |
| **60 samples**    | **73%**      | **39%**      |
| **2,400 samples** | **93%**      | **97%**      |

**Key Insight**: SNN outperforms CNN when data is scarce (n < 100). CNN only surpasses SNN with large datasets (n > 2,000).

## 2. Thesis Utility: "The Cebu Model"
*Relevance to Data-Driven Real Estate Valuation:*
- **Application**: **Methodology Selection**. If you have <100 labeled roof images in Cebu, start with SNN (One-Shot Learning). Switch to CNN only after collecting >2,000 samples.
- **Relevance**: Directly addresses the "Data Scarcity" problem central to your thesis. You can cite this as justification for choosing Siamese Networks over traditional CNNs.
- **Counter-Argument Addressed**: "Why not use a standard CNN?" → Because CNN achieves 0% accuracy with 1 sample vs SNN's 55%.
- **Keywords for Lit Review**: "One-Shot Learning", "Few-Shot Learning", "Data Scarcity", "Synthetic Data Augmentation"

## 3. Methodology
- **Research Design**: Experimental (Comparative Analysis)
- **Model Architecture**:
  - **SNN**: Siamese Neural Network with similarity metric learning
  - **CNN**: DenseNet architecture with Adam Optimizer
- **Training Strategy**:
  - **Primary Experiment (OSL)**: Trained on artificially generated images (one example per class), tested on real satellite images
  - **Comparison Experiments**: Trained on varying subsets of real data (1 to 2,400 images)
- **Data Split**: 50% of real dataset used for testing; training size varied
- **Data Generation**:
  - Synthetic training images created using **Autodesk Maya** (3D modeling)
  - Three different sun angles and textures per roof type for realism
- **Pre-processing**: Real images resized from 224×224 to 105×105 pixels, converted to .jpg
- **Roof Types Classified**:
  1. Flat
  2. Gable (including sub-types: Gable, Gable with Dormer, Gable & Valley)
  3. Hip (including sub-types: Hip, Hip & Valley)

## 4. Limitations & Future Research
- **Limitation (Resolution)**: Low-resolution satellite imagery caused failure distinguishing **Gable vs Hip** roofs (complex textures) vs Flat roofs (99% accuracy due to lack of surface detail)
- **Limitation (Geography)**: Tested on only one geographic area—generalizability unknown
- **Limitation (Roof Types)**: Only 3 categories; real-world has more variety
- **Future Research**:
  - "Diversify artificial data production" (Better textures)
  - "Test with different data sets" (Generalizability across geographies)
  - Higher-resolution imagery needed for texture-dependent classifications

## 5. Critical Quotes
> "The OSL approach can get satisfactory results even with just one data point."

> "Better results will be obtained with higher-resolution test data."

> "When there are only 60 images for training, the SNN model... (73%). The CNN model also gets low scores at this data size (39%)."

> "The authors attribute the high accuracy for Flat roofs to the lack of surface detail compared to the complex textures of Gable and Hip roofs."
