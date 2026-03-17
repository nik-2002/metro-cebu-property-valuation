# Machine Learning Valuation in Dual Market Dynamics: A Case Study of the Formal and Informal Real Estate Market in Dar es Salaam
**Source ID:** [Pending - Extracted via Title Query]
> **Abstract**: "Predictive accuracy declines when models incorporate data from both markets... Random Forest ranked first with data from both formal and informal markets (MAPE ~52%)... Validation of ML feasibility in sparse/diverse data environments."

## 0. Bibliographic Context
- **Citation (APA)**: Nyanda, F., Mattsson, H., & Wilhelmsson, M. (2024). Machine Learning Valuation in Dual Market Dynamics: A Case Study of the Formal and Informal Real Estate Market in Dar es Salaam. *Buildings*, 14(10), 3172.
- **Authors**: Frank Nyanda (Tanzania) & Mats Wilhelmsson (KTH Sweden)
- **Publication**: *Buildings* (MDPI), Oct 2024
- **Study Context**: **Dar es Salaam, Tanzania**. Modeling "Dual Markets" (Formal vs. Informal) using ML.
- **Keywords**: #MachineLearning #DualMarket #InformalRealEstate #RandomForest #Tanzania #Africa
- **Data Availability**: Proprietary dataset (n=954).

## 1. Key Quantitative Findings
- **Dataset**:
    - **Total**: **954** observations (430 Informal, 524 Formal).
    - **Mean Price**: 193 million TZS (High Variance: SD 184m).
- **Model Performance (MAPE - Lower is Better)**:
    - **Formal Market Only**:
        - Nearest Neighbors: **37.6%** (Best).
        - Random Forest: **56.4%**.
        - Neural Net: **108.6%** (Failed).
    - **Dual Market (Formal + Informal)**:
        - Boosting: **48.0%** (Best).
        - Random Forest: **52.7%** (Robust).
        - Regression Tree: **137.9%** (Worst).
- **Impact of Informality**: Adding informal data *decreased* accuracy (R-squared dropped from ~0.99 to ~0.84), showing the "noise" involved in informal sectors.

## 2. Thesis Utility: "The Cebu Model"
*Relevance to Data-Driven Real Estate Valuation:*
- **Application**: **Algorithm Selection**. Use this to justify choosing **Random Forest or Boosting** (XGBoost/LightGBM) over Neural Networks for small/noisy datasets (n<1000). The study explicitly shows NN failing (108% error!).
- **Relevance**: Directly mirrors your Cebu context (Dual Market: Formal Developers vs. Informal/Colorum sales).
- **Theoretical Framework**: **Dual Market Theory** (Segmented markets behave differently).

## 3. Methodology
- **Target**: Residential properties in Dar es Salaam.
- **Models**: OLS, Ridge, Lasso, Elastic Net, KNN, SVM, Decision Tree, Random Forest, XGBoost, Neural Network.
- **Metric**: MAPE (Mean Absolute Percentage Error) and MSE.

## 4. Limitations & Future Research
- **Constraints**: Small sample (n=954); "Sparse and diverse" data led to relatively high error rates (>30% MAPE is high for valuation).
- **Future Research Suggestions**:
    - **Augmentation**: "Use of augmentation techniques to increase sample size."
    - **Policy**: "Enforced standardisation of data collection" for informal agents.

## 5. Critical Quotes
> "Predictive accuracy declines when models incorporate data from both markets... reflects the challenges of dealing with less structured data."
> "Neural Network: MAPE 108.594% [Poor performance on small tabular data]."
