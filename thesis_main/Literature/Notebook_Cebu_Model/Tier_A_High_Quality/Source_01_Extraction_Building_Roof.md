# EXTRACTION OF BUILDING ROOF OUTLINES FROM REMOTE SENSING IMAGERY USING DEEP LEARNING
**Source ID:** 9e731654-bc61-4b55-953b-2466743d285e
> **Abstract**: "Automated extraction of building roof outlines from remote sensing data is critical for urban planning... This project aims to assess how well Deep Neural Networks (DNNs) can accurately identify and outline buildings... The project investigates the performance of two prominent Deep Learning architectures, U-Net and Residual U-NeT... U-NeT achieved 82.43% accuracy... while Residual U-NeT achieved 82.99% accuracy."

## 0. Bibliographic Context
- **Citation (APA)**: Gyekye, J. (2025). *Extraction of Building Roof Outlines from Remote Sensing Imagery Using Deep Learning*. University of Mines and Technology. ResearchGate.
- **Author**: Jerry Gyekye (University of Mines and Technology, Tarkwa, Ghana)
- **Publication**: ResearchGate (July 2025)
- **Study Context**: **Tarkwa, Ghana**. Addressing data gaps in cadastral mapping for developing nations.
- **Keywords**: #DeepLearning #RemoteSensing #BuildingExtraction #UNet #ResidualUNet #DroneImagery #Ghana
- **Data Availability**: Not explicitly stated as public (Dataset internal to study).

## 1. Key Quantitative Findings
- **Model Performance**:
    - **Residual U-Net**: **82.99%** Accuracy, **91.84%** Precision, **82.49%** F1-Score.
    - **U-Net**: **82.43%** Accuracy, **89.09%** Precision, **81.89%** F1-Score.
- **Dataset Specs**:
    - **Sample**: **4,580** images (128x128 pixels).
    - **Resolution**: **3 cm/pixel** (Drone Orthomosaic).
    - **Coverage**: **130.84 hectares**.
- **Training**:
    - **Converged At**: Epoch **26** (Residual) vs **43** (Standard U-Net).
    - **Augmentation**: 500 samples/image (Rotation ±45°, Scale 0.5-1.5x).

## 2. Thesis Utility: "The Cebu Model"
*Relevance to Data-Driven Real Estate Valuation:*
- **Application**: Blueprint for **Feature Engineering** pipeline. Use this Residual U-Net architecture to extract "Building Footprint" and "Roof Material" from Cebu satellite imagery.
- **Relevance**: Directly addresses the **Information Modeling** component of your thesis by creating proxy variables for property quality where tax decs are missing.
- **Theoretical Framework**: **Deep Learning (Convolutional Neural Networks)** for Semantic Segmentation. Specifically compares **Standard Encoder-Decoder (U-Net)** vs. **ResNet-style definitions (Residual U-Net)**.

## 3. Methodology
- **Input**: RGB Drone Imagery converted to Orthomosaic.
- **Preprocessing**: Grayscale conversion -> Tile slicing (128x128) -> Augmentation.
- **Architecture**: 
    - *Residual U-Net*: Replaces standard convolutional blocks with residual blocks (skip connections) to facilitate deeper network training without vanishing gradients.

## 4. Limitations & Future Research
- **Constraints**: 
    - Computational cost: Residual U-Net took longer per epoch despite faster convergence.
    - Resolution dependence: Study used ultra-high-res (3cm) drone data; generalized satellite data (30cm+) performance is untested.
- **Future Research Suggestions**:
    - Investigate **Transfer Learning** to apply this model to different geographic regions (e.g., varying roof architectures in Southeast Asia).
    - Explore **Instance Segmentation** (Mask R-CNN) to separate touching buildings better than Semantic Segmentation.

## 5. Critical Quotes
> "Residual U-Net... validating the efficiency of residual connections in remote sensing segmentation tasks."
> "Accurate, up-to-date information on building footprints is a prerequisite for... valuation and taxation."
