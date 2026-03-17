# Thesis Presentation Script: Data-Driven Property Valuation for Cebu City

*Note to Speaker: This script is synchronized with the final "Ash Grey and Black" PDF deck (17 Slides).*

---

## Slide 1: Title Slide

**Narration:**
"Good morning, members of the panel. I am [Your Name], and for my thesis proposal, I present: 'Data-Driven Property Valuation Factors and Model for Cebu City: A Comparative Analysis of Hedonic Regression and Machine Learning Approaches.'"

---

## Slide 2: Introduction

**Narration:**
"Let me begin with why this matters. Real estate is a massive pillar of the Philippine economy, contributing roughly 6% to our GDP (PSA, 2024).

But in Cebu, the valuation landscape is fundamentally fragmented. We currently rely on three discordant sources:

1. **BIR Zonal Values:** Which are notoriously outdated and often lower than market value.
2. **Bank Appraisals:** Which are conservative and opaque.
3. **Market Listings:** Which vary wildly depending on the seller's optimism.

This creates confusion. My study aims to build a transparent, data-driven model to estimate 'Fair Market Value' for our stakeholders, specifically Cebu Premiere Real Estate (CPRE).

Think of it this way: **Traditional valuation relies on the Sales Comparison Approach—comparing 3 similar unsold properties. My study scales this up. Instead of comparing 3 properties, I use Hedonic Modeling to compare 955 properties simultaneously, isolating the specific contributory value of location and structural features using Machine Learning.**"

**Q&A / Supporting Details:**

* *Why 6% GDP?* The PSA (2024) confirmed that Real Estate and Renting activities accounted for ~6% of GDP.
* *How outdated are Zonal Values?* Most Zonal Values in Cebu haven't been revised since 2018-2019, despite post-pandemic inflation.

---

## Slide 3: Problem Statement

**Narration:**
"The core problem is simple: We lack a scientifically validated model to estimate residential property values in Cebu City.
As Agosto (2017) noted, stakeholders often rely on intuition or disjointed data sources.
This leads to our primary research question: **'How can we accurately predict the market value of a residential property in Cebu using available data?'**"

---

## Slide 4: Research Questions

**Narration:**
"To answer this, I will investigate four key areas:

1. **Model Comparison:** Does a Machine Learning model (like Random Forest or XGBoost) actually outperform traditional Hedonic Regression?
2. **Key Drivers:** What are the most significant determinants of value? Is it Floor Area, or is it Proximity to the CBD?
3. **Valuation Gap:** What is the magnitude of the difference between BIR Zonal Values and actual Market Asking Prices?
4. **Future Factors:** Can we quantify the value captured by planned infrastructure like the Cebu Bus Rapid Transit (CBRT)?"

**Q&A / Supporting Details:**

* *Why compare to Hedonic Regression?* OLS Regression is the industry standard (Rosen, 1974). We need to prove ML adds value over this baseline.

---

## Slide 5: Research Significance

**Narration:**
"This study holds significance for three main groups:

1. **The Stakeholder (CPRE):** It provides a quantitative tool for pricing advice.
2. **The Academe:** It fills a regional gap, focusing on Cebu's unique market dynamics.
3. **Policymakers:** It provides data on the lag of Zonal Values, supporting tax reform discussions."

---

## Slide 6: Review of Related Literature (Theories)

**Narration:**
"My theoretical foundation rests on two pillars:

1. **Hedonic Pricing Theory (Rosen, 1974):** Which treats a house as a bundle of attributes (Physical, Locational, Environmental).
2. **Spatial Economics:** Specific to Cebu, Agosto (2017) found that 'Accessibility' is the primary determinant of land rent."

---

## Slide 7: Review of Related Literature (Empirical)

**Narration:**
"Empirically, the literature shows a clear progression:

* **Domingo & Fulleros (2005):** Established the 'Valuation Gap' concept in the Philippines.
* **Viray (2023):** Demonstrated that Machine Learning (Random Forest) reduces error by 15% compared to Linear Regression in Philippine provinces.
* **Gayathri & Thekkayil (2025):** The state-of-the-art. They showed that Ensemble Models (RF + XGBoost) combined with 'Future Infrastructure' factors can achieve up to 97% accuracy. This is the benchmark I aim to replicate."

---

## Slide 8: Conceptual Framework

**Narration:**
"My conceptual framework is straightforward:

* **Inputs:** Physical traits, Locational factors, and Macro indicators.
* **Process:** Data Cleaning, Regex Parsing, and training three models (OLS, RF, XGB).
* **Output:** A predicted 'Fair Market Value'."

---

## Slide 9: Methodology - Data Processing

**Narration:**
"Now, we address the biggest bottleneck of this study: **Data Availability**.
Unlike in the US or Europe, the Philippines has no centralized Multiple Listing Service (MLS). Data is scattered, hidden, or unverified.

To overcome this **scarcity**, I propose a 'Hybrid Data Collection' pipeline:

1. **The Floor Price (Verified):** I will extract datasets from BDO's Foreclosed Asset PDF listings. While the nationwide dataset contains **959 listings**, my analysis found only **22 properties** for Cebu Province. This scarcity validates the "Data Gap" problem.
2. **The Ceiling Price (Market):** To solve this sparsity, I will web-scrape public listings from portals (like Lamudi/DotProperty). As Sousa et al. (2024) validated, aggregating thousands of online listings is the only way to build a robust model when official data is this sparse.
3. **The Validation Layer (Expert):** Finally, I will integrate a **Human-in-the-Loop** approach using my family's brokerage network. This serves two purposes:
   * **Domain Validation:** Using expert intuition ("Gut Feel") to sanity-check model outliers.
   * **Data Augmentation:** Leveraging industry contacts to potentially source additional foreclosure listings from other banks beyond BDO.

By combining the sparse but verified floor price, the abundant market price, and expert validation, we bracket the 'True Market Value'."

**Q&A / Supporting Details:**

* *Why is data the bottleneck?* Privacy laws (Data Privacy Act) protect final Deed of Sale prices. We must rely on *proxies* (Asking/Foreclosure prices) rather than final transaction amounts.
* *How robust is the scraping?* The scraper handles paginated results and cleans "dirty" text (e.g., "3br" vs "3 bedrooms") using Regex pipeline.
* *How do you use 'Gut Feel'?* It serves as **Domain Expert Validation**. If the model predicts a price that defies the 20+ years of experience of our brokerage network, we investigate that outlier. It creates a "Human-in-the-Loop" quality check.

---

## Slide 10: Data Cleaning Strategy

**Narration:**
"Zooming in on Data Cleaning:

1. **Handling Missing Values:** Rows without Price will be dropped. Missing Lot Area will be imputed with the Barangay median.
2. **Text Processing:** We will parse descriptions to structured integers (e.g., '3BR with 2TB' becomes Bedrooms=3, Bathrooms=2).
   This ensures the model trains on clean, structured data."

---

## Slide 11: Feature Engineering (Geospatial)

**Narration:**
"Moving to **Geospatial Feature Engineering**, this is where we unlock the true value of 'Location'.
A simple address like 'Barangay Lahug' is too broad. To capture the granular value of specific streets, I will compute exact **Geospatial Vectors**:

1. **Distance to CBD:** Using the **Haversine Formula**, I will calculate the precise great-circle distance from each property to the two major economic hubs: Ayala Center and IT Park. This captures the 'Accessibility' premium.
2. **Distance to Transport:** I will map the proximity to the nearest planned **CBRT Station**. This allows us to test if future infrastructure is arguably already priced in.
3. **Neighborhood Quality:** Instead of subjective ratings, I will calculate an 'Amenity Score' by counting the number of schools and hospitals within a 1km radius.

These numeric vectors transform vague location names into mathematical features that the model can learn from."

**Q&A / Supporting Details:**

* *Did you use GIS software like QGIS?* For the modeling pipeline, I used **Python** exclusively to ensure automation. I utilized the **`geopy`** library to geocode addresses, the **Haversine formula** to calculate precise spherical distances, and the **OpenStreetMap (Overpass) API** to programmatically count amenities. We can use QGIS for final visualization, but the math is handled in Python.

---

## Slide 12: Preliminary EDA (Data Snapshot)

**Narration:**
"Before modeling, our **Exploratory Data Analysis (EDA)** reveals a critical insight: Property prices are highly right-skewed.

* This means we have a long tail of ultra-expensive properties.
* **Actionable Insight:** I will apply a **Log Transformation** to the target variable. This normalizes the distribution, ensuring our model isn't biased by billionaires' mansions."

---

## Slide 13: Model Tuning Strategy

**Narration:**
"We don't just use 'default' settings. Comparison requires fairness, so I will perform **Hyperparameter Tuning** for each model:

* **GridSearchCV:** I will systematically test thousands of combinations—like varying the 'Number of Trees' in Random Forest or the 'Learning Rate' in XGBoost.
* This ensures that when we say 'XGBoost won', it won because it was better, not because the other models were poorly configured."

---

## Slide 14: Methodology - Modeling

**Narration:**
"For the core valuation engine, I propose a competitive **Benchmark Study** involving three distinct algorithms:

1. **The Baseline: OLS Regression.** We start here because it is interpretable (e.g., coefficient $x$ means price increases by $y$ per sqm). However, it assumes strict linearity, which real estate often violates.
2. **Challenger 1: Random Forest.** This model builds hundreds of 'Decision Trees' to capture non-linear patterns—like how the price per sqm might actually *decrease* for ultra-large lots (diminishing returns).
3. **Challenger 2: XGBoost.** This is our high-performance candidate. By using gradient boosting to iteratively correct the errors of previous trees, XGBoost often yields the lowest error rates in Kaggle competitions and modern valuation studies.

I will tune these models using **GridSearchCV** to ensure we are comparing their best possible versions."

---

## Slide 15: Empirical Framework (Evaluation)

**Narration:**
"To objectively measure success, I will use three standard metrics:

**MAE (Mean Absolute Error):** Following **Viray (2023)**, I use this because it is the most practical metric for stakeholders. It gives us the average error in *Pesos*. For example, 'The model is off by +/- 500,000 pesos on average.'

**RMSE (Root Mean Squared Error):** Also utilized by **Viray (2023)**, this metric penalizes large errors more heavily, ensuring our model isn't making catastrophic mistakes on expensive properties.

**R-Squared:** This tells us 'Goodness of Fit'. My target is an R-Squared of **> 0.80**. This is a conservative benchmark, considering **Gayathri & Thekkayil (2025)** recently achieved ~97% accuracy with similar ensemble models."

---

## Slide 16: Model Interpretation Strategy (XAI)

**Narration:**
"To address the 'Black Box' nature of ML models, I will use **SHAP (Shapley Additive Explanations)** Force Plots.

* **Global Interpretability:** Allows us to see which features (like Distance vs. Floor Area) drive the market overall.
* **Local Interpretability:** Allows us to explain *individual* prices—showing exactly why a specific unit is priced higher or lower.
  This builds trust with stakeholders who need to understand the 'Why' behind the number."

---

## Slide 17: Scope and Limitations

**Narration:**
"To ensure feasibility, I have defined strict boundaries.

**The Context:**
First, this is an **Applied Research** study. Its primary goal is not just theoretical novelty, but to solve a specific business problem for CPRE.

**The Scope:**

* **Geography:** Primarily Cebu City and immediate Metro Cebu neighbors.
* **Property Type:** Residential only.

**The Edge Cases & Risks (Worst-Case Scenarios):**

1. **Risk: Anti-Scraping Measures.**
   * *Worst Case:* If portals block our scrapers, I will pivot to manually encoding the static PDFs from BDO and other banks, focusing 100% on the 'Floor Price' model.
2. **Risk: 'Fake' Pricing.**
   * *Constraint:* 'Market Price' is based on *Asking Price*, not sold price. Sellers often inflate prices.
   * *Mitigation:* I will use **Interquartile Range (IQR)** filtering to remove extreme outliers, and rely on the **Broker Validation Layer** to manually flag unrealistic listings."

---

## Slide 18: Timeline & Milestones

**Narration:**
"My timeline is as follows:

* **Dec - Jan:** Data Collection & Cleaning.
* **February:** Feature Engineering (Geocoding) & "Future Factor" tagging.
* **March:** Model Training & Hyperparameter Tuning.
* **April:** Evaluation, Interpretation, and Final Manuscript."

---

## Slide 19: Ethical Considerations

**Narration:**
"Finally, we address **Ethics**.

* **Privacy:** I strictly use *public* foreclosure listings. No private homeowner identities are scraped.
* **Transparency:** This model is a *guide*, not a mandate. We explicitly state the Error Margins (MAE) so users know it's an estimate, not a guarantee."

---

## Slide 20: References

**Narration:**
"Here are the key references supporting this study."

---

## Slide 21: Q & A

**Narration:**
"Thank you. The floor is now open for questions and clarifications."
