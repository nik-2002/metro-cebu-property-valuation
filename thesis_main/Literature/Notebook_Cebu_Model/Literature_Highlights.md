# Critical Literature Highlights (Cheat Sheet)
*A currated list of the most impactful sources found during the review Process. Use these for your Problem Statement, Methodology justification, and Limitations.*

## 🚨 Critical Warnings & Limitations
| Source                                        | Finding                                                                                                          | Why it Matters                                                                                                                                            |
| :-------------------------------------------- | :--------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Source 18 (Nighttime Lights - World Bank)** | **"Little explanatory power"** and "unstable over time."                                                         | **WARNING:** Do not blindly use DMSP Nighttime Lights as a proxy for growth. Citations warn against it. Use with caution or verify with newer VIIRS data. |
| **Source 13 (Tanzania ML)**                   | **Neural Networks Failed** (108% Error) on small/noisy data.                                                     | Justifies why you should use **Random Forest** or **XGBoost** (which performed best) instead of Deep Learning for tabular valuation data.                 |
| **Source 2 (Kenya)**                          | **Info Asymmetry > Corruption**. Ranked "Limited Information" (2.91) as a bigger problem than Corruption (2.43). | Validates your thesis premise: The problem isn't just "bad people," it's "bad data."                                                                      |
| **Source 21 (Deallink)**                      | **Historical Comps Fail**. During high inflation, "static models are insufficient" and multiples contract.       | **WARNING:** Don't use historical sales comps (e.g., 2022 data) for 2025 valuations without "Scenario-based modeling" adjustments.                        |

## 📐 Methodological Benchmarks
| Source                         | Finding                                                                                                                               | Why it Matters                                                                                                                |
| :----------------------------- | :------------------------------------------------------------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------- |
| **Source 13 (Tanzania)**       | **Dual Market Benchmarks**: Random Forest MAPE was **~52%** for combined formal/informal markets.                                     | Gives you a realistic **Baseline Accuracy** to beat. If your Cebu model gets <30% MAPE, you are outperforming the literature. |
| **Source 8 (Nigeria)**         | **Replacement Cost Dominance**. Used by surveyors (Mean Score 4.45) when sales comps are missing.                                     | justifying fallback methods in your algorithm when no sales data exists.                                                      |
| **Source 1 (Ghana)**           | **Residual U-Net**. Achieved **83% Accuracy** for roof extraction.                                                                    | Proof of concept for using Satellite Imagery to generate "Building Footprint" features.                                       |
| **Source 29 (IMF - Global)**   | **12% "VaR" Buffer**. In emerging markets, there is a 5% prob of a 12% price crash.                                                   | Use this to recommend a **"Safety Buffer"** for Bank LTVs in your Cebu model.                                                 |
| **Source 28 (Vietnam/Global)** | **Banks Don't Help**. Bank credit "does not significantly moderate" bubble risks.                                                     | proves that *tech-based* valuation (your thesis) is needed because *regulatory* valuation fails.                              |
| **Source 40 (IVS 2025)**       | **Human Judgement Mandatory**. "No model... without... professional judgement... can produce an IVS-compliant valuation."             | **CRITICAL REGULATORY CONSTRAINT**: Your thesis cannot claim to *replace* valuers. It must claim to *augment* them.           |
| **Source 32 (Chen - Yale)**    | **Light Proxy Weighting**. Lights have 25% error, but should weight **30%** in poor-data countries (Grade D) vs **<1%** in rich ones. | Provides the formula for *how* to mix Nightlights into your model (Don't trust them 100%, trust them 30%).                    |
| **Source 36 (Roofs - PMC)**    | **SNN > CNN**. Siamese Networks (73% acc) beat CNNs (39% acc) on small datasets (n=60).                                               | Use **Siamese Networks** for your roof classifier if you only have a few labeled Cebu examples.                               |

## 📈 Macro-Economic Relationships
| Source                  | Finding                                                                                          | Why it Matters                                                                                                                |
| :---------------------- | :----------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------- |
| **Source 20 (Nigeria)** | **Exchange Rate (-0.92)** is a stronger predictor than **Inflation (-0.50)**.                    | Suggests you should include `USD_PHP_Exchange_Rate` as a feature in your model, as it drives value more than CPI.             |
| **Source 7 (Russia)**   | **Elasticity Flip**. Correlation shifted from **+0.26** (Pre-War) to **-0.21** (During War).     | Proves that "Structural Breaks" (like COVID/War) essentially break valuation models. Your model needs to handle time-regimes. |
| **Source 17 (US)**      | **Cap Rate Expansion**. Interest rates force Cap Rates up, compressing value even if rent grows. | Explains theoretical value drops during high-interest periods (like 2023-2024).                                               |

---

## 🛡️ Source Quality Audit (Batch 4 Review)
*Summary of audit conducted on all 44 sources regarding data availability and quality.*

**🔴 Critical "Holes" (Unusable Sources)**
*Excluded from quantitative analysis due to failed access.*
*   **Source 06 (Land Plots)**: Restricted (IAAO Login).
*   **Source 42 (Restricted Case)**: Restricted (IAAO Login).
*   **Source 31 (Price Fluctuation)**: Missing Full Text (Citation Only).

**🟡 Qualitative/Thin Sources (Context Only)**
*Valid for theory, but contain no stats.*
*   **Source 35 (Rwanda)**: Valid case study, but no revenue $ stats found in text.
*   **Source 43 (CAMA)**: Qualitative industry overview.
*   **Source 34 (Nightlights)**: Missing text, but "Informal Economy" insight salvaged from citations.

**🟢 Robust Sources**
*   **38 Sources** are confirmed data-rich and validated for the Literature Review.

---
*Updated automatically as new batches are processed.*
