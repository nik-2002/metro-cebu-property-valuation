# Downside Risks to House Prices (IMF Global Financial Stability Report)
**Source ID:** [Refined via Deep Search]
> **Abstract**: "House Prices at Risk (HaR) model uses panel quantile regression... 5th percentile captures downside risks up to 3 years ahead... 32 economies analyzed."

## 0. Bibliographic Context
- **Citation (APA)**: International Monetary Fund [IMF]. (2018). Downside Risks to House Prices. In *Global Financial Stability Report* (April 2018 Chapter). Washington, DC: IMF.
- **Authors (IMF Staff)**:
  - **Team Lead**: Nico Valckx
  - **Authors**: Andrea Deghi, Mitsuru Katagiri, Oksana Khadarina, Sohaib Shahid
  - **Contributors**: Adrian Alter, Elizabeth Mahoney, Peichu Xie, Janice Yi Xue
  - **Guidance**: Dong He, Fabio Natalucci, Claudio Raddatz
- **Publication**: IMF Global Financial Stability Report (October 2017/April 2018)
- **Study Context**: Global—macroprudential early warning system for housing bubbles
- **Keywords**: #HousePricesAtRisk #QuantileRegression #FinancialStability #IMF #EarlyWarning #Macroprudential
- **Data Availability**: Aggregated panel data (32 countries)

## 1. Key Quantitative Findings

### Sample Coverage
- **Countries**: 32 advanced and emerging market economies
  - 22 major advanced economies
  - 10 emerging market economies (4 Latin America, 3 East Asia, Russia, South Africa, Turkey)
- **Cities**: 31 cities (largest city per country, except South Africa)

### Forecast Horizon
- **Short-term**: 1 year ahead
- **Medium-term**: 3 years ahead
- **Empirical Range**: 1 to 16 quarters ahead

### Risk Percentiles
- **5th Percentile**: Captures downside risks (large price declines)
- **50th Percentile**: Median (baseline scenario)
- **95th Percentile**: Upside risks (used for capital inflow analysis)

## 2. HaR Model Predictors

The House Prices at Risk model includes five key vulnerability factors:

| Predictor                        | Description                                                             |
| -------------------------------- | ----------------------------------------------------------------------- |
| **1. Financial Conditions**      | Overall metric of risk pricing in the economy                           |
| **2. Real GDP Growth**           | Proxy for household real income developments                            |
| **3. Credit Booms**              | Periods where credit-to-GDP ratio > long-term trend                     |
| **4. House Price Overvaluation** | Measured by price-to-GDP per capita ratio (deviation from fundamentals) |
| **5. Past House Price Growth**   | Captures momentum effects                                               |

## 3. Thesis Utility: "The Cebu Model"
*Relevance to Data-Driven Real Estate Valuation:*
- **Application**: **Risk Modeling Extension**. While your thesis focuses on point estimates, you could add a "Value at Risk" module using quantile regression to capture downside scenarios.
- **Relevance**: The HaR framework shows how to model tail risks—useful if banks want to stress-test your valuations.
- **Predictor Selection**: Consider including `Credit_to_GDP` and `Price_to_GDP_Ratio` as features for detecting overvaluation in Cebu.
- **Chapter Reference**: Chapter 2 (Financial Stability Literature), Chapter 5 (Future Extensions)

## 4. Methodology
- **Research Design**: Quantitative, Panel Data Analysis
- **Statistical Method**: **Panel Quantile Regression**
- **Framework**: Builds on the Growth-at-Risk (GaR) methodology
- **Key Quote**: "Using a statistical technique known as quantile regression, it is possible to study how house prices at risk move when the conditioning variables change."
- **Target Variable**: Future house price growth (conditional distribution)
- **Primary Quantile**: 5th percentile (downside risk focus)
- **Comparison**: 5th vs 50th percentile to assess asymmetric risk

## 5. Limitations & Future Research
- **Limitation (Data Lag)**: Relies on quarterly data which may not capture rapid shifts
- **Limitation (Emerging Markets)**: Only 10 emerging economies—limited representation
- **Limitation (City vs National)**: City-level analysis may miss suburban/rural dynamics
- **Future Research**:
  - Apply HaR to individual city-level markets (e.g., Cebu Metro)
  - Incorporate climate risks as additional predictor
  - Real-time monitoring with higher-frequency data

## 6. Critical Quotes
> "Using a statistical technique known as quantile regression, it is possible to study how house prices at risk move when the conditioning variables change."

> "Identify the size of very large declines in future house prices (that is, downside risks to future house prices) within the lowest (least likely) quantiles of its conditional distribution, typically the 5th percentile."

> "Credit booms: periods during which the credit-to-GDP ratio is above the long-term trend."

> "House price overvaluation... captures the degree of deviation from fundamental valuation levels."
