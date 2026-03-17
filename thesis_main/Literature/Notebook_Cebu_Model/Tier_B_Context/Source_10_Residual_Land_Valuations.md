# How To Value - Residual Land Valuations vs. Direct Comparison
**Source ID:** a4d33457-3f8d-42da-9f88-466d3cfc1d42
> **Abstract**: "Revenue – Costs = Residual Land Value... This value helps the developer determine the maximum amount that could be paid for a parcel of land... Useful when 'there is nothing remotely comparable to this site in the neighbourhood'."

## 0. Bibliographic Context
- **Citation (APA)**: Newcombe, L. (2025). *How To Value - Residual Land Valuations vs. Direct Comparison*. Altus Group.
- **Author**: Lionel Newcombe (Altus Group)
- **Publication**: Industry Article (Jan 7, 2025)
- **Study Context**: **Commercial Real Estate (CRE)**. Practical guide on development feasibility.
- **Keywords**: #ResidualLandValue #DevelopmentFeasibility #CRE #LandValue #ProfitMargin
- **Data Availability**: Industry Guide.

## 1. Key Quantitative Findings
- **The Core Formula**:
    - **Land Price** = (Gross Development Value - Selling Costs) - (Construction Costs + Professional Fees + Contingency + Developer's Margin).
- **Sensitivity Dynamics**:
    - **Variable**: "Land Value" and "End Sale Value" are the hardest to estimate (High Variance).
    - **Fixed**: "Permit fees," "Construction costs," and "Professional services" are relatively static (Low Error Margin).
- **Optimization**: The model works "in reverse" to find the *maximum* viable land price for a fixed profit target.

## 2. Thesis Utility: "The Cebu Model"
*Relevance to Data-Driven Real Estate Valuation:*
- **Application**: **Algorithm Logic**. If your model attempts to value *vacant land* (common in Cebu), you should code this "Residual" logic as a feature: `Predicted_Condo_Price - Construction_Cost = Implied_Land_Value`.
- **Relevance**: Justifies using "Residual Value" when "Direct Comparison" fails (i.e., when you have no sales comps for land, which Source 8 confirmed is a major problem).
- **Theoretical Framework**: **Residual Theory of Land Value** (Land price is a residue of surplus productivity).

## 3. Methodology
- **Type**: Operational Guide.
- **Algorithm**: Reverse-engineering distinct cost components to solve for land value.

## 4. Limitations & Future Research
- **Constraints**: "Garbage in, garbage out" – highly sensitive to the "End Sale Value" prediction.
- **Future Research Suggestions**:
    - **Software vs. Spreadsheets**: Evaluate the accuracy trade-off between Excel models vs. specialized tools like ARGUS EstateMaster (suggested by Author).
    - **Highest & Best Use**: Research methods to algorithmically determine the optimal use case for a site.

## 5. Critical Quotes
> "The final figure is calculated by working in reverse to determine what land price will achieve the target return."
> "Helps you assess a project’s viability... without needing to know the actual land value."
