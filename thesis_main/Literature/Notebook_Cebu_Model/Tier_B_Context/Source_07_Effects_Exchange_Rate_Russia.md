# Effects of Exchange Rate Changes on Real Estate Prices in Russia During the Russian-Ukrainian War
**Source ID:** fa4d856b-90e1-447d-9858-d91f328f7410
> **Abstract**: "The ruble-dollar exchange rate fell 42.7% in two weeks... Inflation rose from 9.2% to 17.8%... The relationship between real estate prices and exchange rates shifted from positive (0.59 correlation pre-war) to negative (-0.21 elasticity during war)."

## 0. Bibliographic Context
- **Citation (APA)**: Han, Z. (2024). Effects of Exchange Rate Changes on Real Estate Prices in Russia During the Russian-Ukrainian War. *Highlights in Business, Economics and Management*, 39.
- **Author**: Zhengrong Han (Beijing Normal University-Hong Kong Baptist University UIC)
- **Publication**: *MSIED 2024* (2024)
- **Study Context**: **Russia**. Analyzing structural breaks in market behavior due to geopolitical shock (War).
- **Keywords**: #ExchangeRate #RealEstatePrices #StructuralBreak #WarImpact #Elasticity #Macroeconomics
- **Data Availability**: Public macroeconomic data used.

## 1. Key Quantitative Findings
- **Macro Shock**:
    - **Exchange Rate**: Fell **42.7%** (63.6 -> 111.1) in 2 weeks.
    - **Inflation**: Peaked at **17.8%**.
    - **Interest Rate**: Hiked from **9.5% to 20%**.
- **Model Results (Pre-War vs. War)**:
    - **R-Squared**: Dropped from **0.78** (Pre) to **0.56** (War).
    - **Exchange Rate Elasticity**:
        - **Pre-War**: **+0.263** (1% currency drop -> 0.26% price hike).
        - **War Period**: **-0.21** (Relationship inverted!).
    - **GDP Elasticity**:
        - **Pre-War**: **+2.456** (Strong positive link).
        - **War Period**: **-0.46** (Negative link).

## 2. Thesis Utility: "The Cebu Model"
*Relevance to Data-Driven Real Estate Valuation:*
- **Application**: **Macro-Factor Adjustment**. Use this to argue that your valuation model must account for "Structural Breaks" (like COVID or inflation spikes). A static model fails when correlations invert (as seen here: +0.26 becomes -0.21).
- **Relevance**: Demonstrates how to use **Log-Log Regression** to calculate "Elasticity Coefficients," a technique you can apply to your Mass Appraisal model for sensitivity analysis.
- **Theoretical Framework**: **IS-LM Model** (Investment-Saving, Liquidity-Money) & **Structural Break Theory**.

## 3. Methodology
- **Model**: Log-Log Linear Regression (`ln_repx = ß0 + ß1 ln_exr...`).
- **Periods**:
    - Pre-War: Jan 2003 – July 2021.
    - War: Jan 2022 – June 2023.
- **Variables**: Real Estate Price Index, Exchange Rate, GDP, Inflation.

## 4. Limitations & Future Research
- **Constraints**: "During War" model had only **7 observations** (quarterly), making it statistically unstable (p=0.0653, marginally significant).
- **Future Research Suggestions**:
    - **Sample Size**: Needs longer horizon post-war to validate the "negative correlation" persistence.
    - **Variables**: Expand model to include Interest Rates and Migration flows (Brain Drain).

## 5. Critical Quotes
> "For every 1% change in the exchange rate, the expected percent change in real estate prices is -0.21% [during war]."
> "Geopolitical events... can invert standard economic correlations."
