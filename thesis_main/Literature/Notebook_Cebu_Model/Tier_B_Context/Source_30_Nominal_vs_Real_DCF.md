# Nominal versus Real DCF Valuation (Contextual Summary)
**Source ID:** [Pending - Extracted via Citation Analysis]
> **Abstract**: "Discounted cash flow models must be meticulously adjusted to distinguish between 'nominal' and 'real' growth rates to avoid overvaluation."

## 0. Bibliographic Context
- **Citation (APA)**: Polanitzer, R. (n.d.). *Nominal versus Real DCF Valuation*. Medium. (Cited in *Structural Paradigms...*).
- **Author**: Roi Polanitzer
- **Publication**: Medium (Financial Modeling Blog)
- **Study Context**: **Financial Modeling**. Technical guide on Inflation adjustments in DCF.
- **Keywords**: #DCF #NominalVsReal #Inflation #ValuationModeling #DiscountRate
- **Data Availability**: Methodology only.

## 1. Key Quantitative Findings
*Note: The detailed text of this source was missing from the NotebookLM index, but its core argument is preserved in citations:*
- **The Core Error**: Valuers often mix **Nominal Cash Flows** (Inflation included) with **Real Discount Rates** (Inflation excluded), or vice versa.
- **The Rule**:
    - If Cash Flow is **Nominal** (includes rent, price growth), use a **Nominal WACC**.
    - If Cash Flow is **Real** (constant purchasing power), use a **Real WACC**.
    - **Fisher Equation**: $(1 + Nominal Rate) = (1 + Real Rate) * (1 + Inflation Rate)$.

## 2. Thesis Utility: "The Cebu Model"
*Relevance to Data-Driven Real Estate Valuation:*
- **Application**: **Algorithm Consistency**. If your feature set includes `Inflation_Rate` (Nominal), ensure your target variable `Price` isn't implicitly treated as "Real."
- **Relevance**: A technical "Check the Box" item for your Methodology chapter to prove you understand financial math.
- **Theoretical Framework**: **Fisher Effect**.

## 3. Methodology
- **Type**: Technical Tutorial.

## 4. Limitations & Future Research
- **Constraints**: Source text unavailable; inferred from citations.

## 5. Critical Quotes
> "Discounted cash flow models must be meticulously adjusted to distinguish between 'nominal' and 'real' growth rates."
