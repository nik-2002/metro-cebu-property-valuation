# The Impact of Inflation on Real Estate Investment Performance and Effective Investment Decisions
**Source ID:** [Refined via Deep Search]
> **Abstract**: "Correlation of -0.508 (Inflation vs RE Performance)... Exchange rate shows stronger negative correlation (-0.925)... Data analyzed with SPSS and EViews."

## 0. Bibliographic Context
- **Citation (APA)**: Nworah, J., Egbenta, I., & Ogbuefi, J. (2023). The Impact of Inflation on Real Estate Investment Performance and Effective Investment Decisions. *International Journal of Real Estate Studies*, 17(1).
- **Authors**:
  - Joseph Nworah (Ph.D candidate, Estate Management, University of Nigeria, Nsukka)
  - Idu Egbenta (Ph.D, Estate Management, University of Nigeria, Nsukka)
  - Joseph Ogbuefi (Professor of Estate Management, University of Nigeria, Nsukka)
- **Publication**: International Journal of Real Estate Studies (2023)
- **Study Context**: Nigeria—analyzing macroeconomic impacts on real estate returns
- **Keywords**: #Inflation #ExchangeRate #RealEstate #Nigeria #Regression #InvestmentPerformance
- **Data Availability**: Secondary data from CBN, NBS, IMF, World Bank

## 1. Key Quantitative Findings

### Primary Correlation Coefficients

| Variable Pair                                | Correlation (r)                             | Interpretation              |
| -------------------------------------------- | ------------------------------------------- | --------------------------- |
| **Inflation vs Real Estate Performance**     | **-0.508** (text) / **-0.808** (Table 13.1) | Moderate-to-strong negative |
| **Exchange Rate vs Real Estate Performance** | **-0.925**                                  | Very strong negative        |
| Exchange Rate vs Average Rental (Detached)   | +0.927                                      | Strong positive             |
| Exchange Rate vs Average Rental (Terrace)    | +0.886                                      | Strong positive             |
| Inflation vs Average Rental (Detached)       | -0.151                                      | Weak negative               |
| Inflation vs Average Rental (Terrace)        | -0.125                                      | Weak negative               |

### Key Finding
> **Exchange rate (-0.925) has a stronger negative impact on real estate performance than inflation (-0.508).**

This is counterintuitive—exchange rate instability hurts more than price inflation in emerging markets like Nigeria (and likely Cebu).

## 2. Thesis Utility: "The Cebu Model"
*Relevance to Data-Driven Real Estate Valuation:*
- **Application**: **Feature Engineering**. Include `Exchange_Rate` as a predictor—it may matter more than `Inflation_Rate` in emerging markets.
- **Relevance**: Philippines (like Nigeria) has currency volatility. This paper suggests you should weight exchange rate fluctuations heavily in your model.
- **Counter-Argument Addressed**: "Real estate is an inflation hedge" → Not in emerging markets. The data shows negative correlation, not positive.
- **Data Discrepancy Note**: The paper reports -0.508 in text but -0.808 in Table 13.1. Cite Table 13.1 for rigor.
- **Chapter Reference**: Chapter 2 (Macroeconomic Factors), Chapter 3 (Feature Selection)

## 3. Methodology
- **Research Design**: Quantitative, Time-Series Analysis
- **Data Collection**:
  - Primary: Records from Estate Surveyors and Valuers Registration Board of Nigeria (ESVARBON)
  - Secondary: Lagos State/National Population Commission, National Bureau of Statistics, Central Bank of Nigeria, IMF, World Bank
- **Sample Period**: 2005–2022 (some exchange rate data extends to 2023)
- **Statistical Tests**:
  - **Pearson Correlation Analysis**: To determine relationship between variables
  - **Regression Analysis**: Simple linear regression (single IV per hypothesis)
- **Software**: **SPSS** and **EViews**
- **Control Variables**: None explicitly modeled (simple bivariate regression)
- **Hypothesis Models**:
  - H1: Total Annual Returns (DV) ~ Inflation Rate (IV)
  - H2: Real Estate Sector Performance (DV) ~ Exchange Rate (IV)

## 4. Limitations & Future Research
- **Limitation (Bivariate Design)**: Simple linear regression without control variables—confounders not addressed
- **Limitation (Data Quality)**: Secondary data from multiple agencies may have inconsistencies
- **Limitation (Geography)**: Nigeria-only; findings may not directly transfer to Philippines
- **Future Research**:
  - Multivariate regression with controls (GDP growth, interest rates)
  - Cross-country comparison (Nigeria vs other emerging markets)
  - Longer time series for robustness

## 5. Critical Quotes
> "Data collected were analysed using Pearson Correlation Analysis to determine the relationship... Regression analysis was also employed on the data to determine the level of contribution or degree of impact."

> "The two variables must be continuous variables... there should be independence of observations and lastly the variables must be normally distributed."

> "Exchange rate and real estate performance correlation: -0.925." (Stronger than inflation)

> "The basic assumptions or criteria to use these tests are: the two variables must be continuous variables."
