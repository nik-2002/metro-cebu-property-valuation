# RoofNet: A Global Multimodal Dataset for Roof Material Classification
**Source ID:** [Refined via Deep Search]
> **Abstract**: "Over 51,500 samples... High class imbalance (Metal dominates, Thatch underrepresented)... Domain gap in image quality."

## 0. Bibliographic Context
- **Citation (APA)**: Law, N. T., & Miura, Y. (2023). *RoofNet: A Global Multimodal Dataset*. arXiv.
- **Study Context**: **Global**. Benchmark dataset for hazard modeling.

## 1. Key Quantitative Findings
- **Dataset**: 51,503 images from 112 countries.
- **Performance**: Fine-tuning CLIP improved accuracy by **+39.84%**.
- **Imbalance**: Heavy dominance of Metal/Concrete; "Long-tail" classes (Thatch, Green Roofs) are rare.

## 2. Thesis Utility: "The Cebu Model"
*Relevance to Data-Driven Real Estate Valuation:*
- **Application**: **Transfer Learning**. Use RoofNet as your pre-trained model.
- **Relevance**: Specifically useful for **Tropical Material Representation**: Notes that "Corrugated metal sheets" in tropics (rusted/bleached) look different from European metal.

## 4. Limitations & Future Research
- **Limitation**: **Class Imbalance** (Need augmentation for rare roofs).
- **Limitation**: **Resolution Gap** (RoofNet is Hi-Res, but real disaster imagery is often Low-Res/0.5m).
- **Future Research**:
    - "Targeted data augmentation".
    - "Improved resolution harmonization strategies".

## 5. Critical Quotes
> "Includes rich metadata including roof shape... critical priors for estimating structural vulnerability."
