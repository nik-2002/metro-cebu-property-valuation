# **Chapter 2 | Review of Related Literature**

## **2.1 Purpose**

This chapter reviews the existing body of knowledge on data-driven property valuation, drawing from both Philippine and international literature. It establishes the theoretical foundations underpinning this study, surveys empirical evidence on machine learning approaches to real estate pricing, and identifies a critical research gap: the absence of a Cebu-specific, transaction-based, ML-augmented valuation model.

The review is organized thematically. We begin with core valuation concepts and the Philippine regulatory landscape (Section 2.2), then examine the problem of data scarcity in emerging markets (Section 2.3). We survey traditional and ML-based modeling approaches (Section 2.4), introduce the role of geospatial feature engineering in property valuation (Section 2.5), and discuss macroeconomic determinants (Section 2.6). We then address compliance and explainability requirements under IVS 2025 (Section 2.7) before synthesizing the literature into a unified gap statement (Section 2.8).

---

## **2.2 Core Concepts and Philippine Context**

### **2.2.1 Valuation Foundations**

Market value is the most probable price under fair, open-market conditions on the valuation date. Market price is the amount actually paid in a specific transaction; the two can differ in practice (Philippine Valuation Standards [PVS], 2018). Hedonic Pricing Theory, introduced by Rosen (1974), provides the foundational framework for this study. It posits that the price of a differentiated good—such as a house—can be decomposed into a function of its constituent attributes: $P = f(\text{Structural}, \text{Locational}, \text{Environmental})$. This theory underpins the hedonic regression model used as our interpretive baseline.

### **2.2.2 Philippine Indices and Administrative Benchmarks**

The Bureau of Internal Revenue (BIR) issues zonal values primarily for tax purposes, such as capital gains tax (CGT) and documentary stamp tax (DST). These values are administratively set and are not live market prices (BIR, n.d.). Critically, the Tax Policy Study of 2023 (TPS 2023) found that only approximately 60% of Local Government Units (LGUs) have updated their assessment schedules, meaning zonal values in many areas—including parts of Cebu—are materially outdated.

For market-level context, the Bangko Sentral ng Pilipinas (BSP) publishes the Residential Real Estate Price Index (RREPI), which reported a 7.5% nationwide increase in housing prices in Q2 2025. Metro Cebu posted 11.5%—one of the highest growth rates outside the National Capital Region—reflecting sustained demand driven by IT-BPM, tourism, and infrastructure development (BSP, 2025).

### **2.2.3 Cebu's Economic Landscape**

Cebu stands out as one of the Philippines' fastest-growing regional economies, expanding by 7.3% in 2024 (PSA Region 7, 2025). Real estate growth is driven by the IT-BPM sector, tourism recovery, and major infrastructure projects such as the Cebu Bus Rapid Transit (CBRT) and Metro Cebu Expressway, both expected to elevate land values along their routes (DPWH, 2025). However, property pricing in Cebu largely depends on manual appraisals and zonal values. While practical, these methods lack the precision of modern data-driven approaches. This creates a "Valuation Gap" wherein official BIR Zonal Values often lag behind true market prices, producing inefficiencies for buyers, sellers, and lenders.

### **2.2.4 Cebu-Specific Empirical Work**

Agosto (2020) conducted the only Cebu-specific empirical study on land value determinants, surveying 51 real estate practitioners. The study identified transport accessibility as the primary driver of land values, followed by neighborhood quality and environmental conditions. However, the study was survey-based and did not utilize transaction-level data or machine learning methods. Our study validates and extends Agosto's findings with actual property data and predictive modeling.

---

## **2.3 The Core Problem: Data Scarcity in Emerging Markets**

International literature consistently identifies data scarcity—not valuer misconduct—as the primary obstacle to accurate property valuation in developing countries.

- **Kenya**: Cheloti and Mooya (2021) conducted a census survey of 427 registered valuers in Nairobi. "Limited information" was ranked as the **#1 valuation problem** (Mean Rank 2.91), while valuer misconduct ranked last (2.32). The authors concluded: *"The core reason for valuation problems is limited and unreliable information and not valuer misconduct."*

- **Nigeria (Lagos)**: Ajibola (2010) surveyed 300 valuers and found that **92.7%** cited insufficient market evidence as the primary challenge. Valuation inaccuracy ranged from **+24.8% to +51.5%**, far exceeding the global norm of ±10%.

- **Sub-Saharan Africa**: Becsky-Nagy and Sachicola (2025) conducted a systematic review across 46 countries and found a strong negative correlation between urbanization and credit access (r = −0.935), suggesting that financial infrastructure fails to keep pace with rapid urban growth—a pattern relevant to Metro Cebu's expansion.

These findings confirm that valuation inaccuracy is fundamentally a *data problem*, not a *competency problem*. This insight is central to our study's rationale: if the problem is data, the solution is data science.

---

## **2.4 Modeling Approaches: Traditional vs. Machine Learning**

### **2.4.1 Hedonic Regression**

Classical hedonic regression models decompose property price into a function of structural and locational attributes, typically in a log-linear form (Rosen, 1974; Malpezzi, 2003). Spatial econometrics extends this framework by incorporating neighborhood effects and spatial autocorrelation (Anselin, 1988). For the Philippines, Dann et al. (2020) applied hedonic and spatial models to Metro Manila data (2000–2010) and found that structural variables, environmental quality, and spatial spillovers all significantly explain price variation.

### **2.4.2 Philippine Machine Learning Studies**

More recent Philippine work incorporates machine learning:

- **Viray (2023)** compared Multiple Linear Regression with Random Forest for property price forecasting in Central Pangasinan, combining BIR zonal values, BSP RPPI, and construction cost indices. The tree-based model achieved lower prediction error.
- **Ramolete et al. (2023)** demonstrated that incorporating government-based indicators improves ML valuation accuracy, achieving MAPE of **10–21%** with larger, cleaner datasets.
- **Perdio et al. (2023)** tested linear models against gradient boosting on Manila listings and found gradient boosting to be superior after feature selection.

### **2.4.3 International Evidence: The Tanzania Benchmark**

The most directly relevant international study is Nyanda, Mattsson, and Wilhelmsson (2024), who tested eight ML algorithms on **~954 residential properties** in Dar es Salaam—a sample size nearly identical to our BDO dataset.

| Model                           | MAPE                                              |
| ------------------------------- | ------------------------------------------------- |
| Neural Network                  | **108.6%** ❌ (failed — overfitting on small data) |
| Random Forest                   | 52.7%                                             |
| **Gradient Boosting (XGBoost)** | **48.0%** ✅                                       |

This empirical evidence explicitly justifies our choice to prioritize Random Forest and XGBoost over deep learning architectures. Neural networks are powerful but require substantially larger datasets to avoid overfitting. For datasets of ~1,000 observations, tree-based ensembles are the proven, optimal choice.

### **2.4.4 Comparative Reviews**

Broader systematic reviews confirm this pattern. Wang and Li (2020) surveyed deep learning methods in real estate and found that while neural networks excel with image data, tree-based ensembles (Random Forest, XGBoost) remain highly competitive for structured tabular data. Moreno-Foronda et al. (2025) and Sharma et al. (2024) similarly demonstrate XGBoost's consistent superiority in house price prediction tasks. Hu et al. (2024) showed that advances in Explainable AI (XAI) using SHAP values bridge the interpretability gap between "black box" ML models and transparent hedonic regression.

---

## **2.5 Geospatial Feature Engineering in Property Valuation**

Real estate is inherently spatial: a property's value is determined not only by its physical attributes but also by *where* it is located and *what surrounds it*. Tobler's First Law of Geography—"Everything is related to everything else, but near things are more related than distant things" (Tobler, 1970)—provides the theoretical basis for incorporating geospatial features into valuation models.

### **2.5.1 Geocoding and Location Precision**

Geocoding—the process of converting addresses into geographic coordinates (latitude/longitude)—is a foundational step in geospatial property analysis. Modern geocoding services such as the **Google Maps Geocoding API** provide high-precision coordinates from unstructured or semi-structured address strings, enabling consistent spatial analysis even when input addresses vary in format or completeness. Google Maps API is widely used in urban analytics for its global coverage, address disambiguation capabilities, and integration with the Google Places ecosystem, which provides supplementary metadata on nearby amenities and land use (Google Developers, 2025).

For open-source alternatives, **OpenStreetMap (OSM)** via the Nominatim geocoder provides community-maintained geospatial data at no cost. While OSM coverage varies by region, urban areas in the Philippines—particularly Metro Cebu—have beneficiary coverage from the local OpenStreetMap community and humanitarian mapping initiatives (Humanitarian OpenStreetMap Team, 2024). This study employs Google Maps API as the primary geocoding engine for address-to-coordinate conversion, supplemented by OSM for amenity and land-use data retrieval.

### **2.5.2 Proximity Analysis and Accessibility**

Distance-based features—proximity to commercial centers, transportation hubs, schools, and employment nodes—are among the most robust value drivers identified in hedonic pricing literature (Rosen, 1974; Malpezzi, 2003). The Haversine formula, which computes great-circle distance between two points on a sphere given their latitudes and longitudes, is the standard method for computing geographic distances in urban property studies (Sinnott, 1984).

Agosto (2020) confirmed that transport accessibility is the **primary driver** of land values in Cebu, followed by neighborhood quality. For Metro Cebu specifically, proximity to key economic nodes—Cebu IT Park, Ayala Center Cebu, SM Seaside City, Mactan-Cebu International Airport—and planned infrastructure such as the **Cebu Bus Rapid Transit (CBRT)** stations provide measurable value signals.

### **2.5.3 Amenity Scoring via OpenStreetMap**

Beyond point-to-point distances, the density and diversity of nearby amenities within a defined radius provide a richer characterization of neighborhood quality. OSM's structured tagging system allows researchers to query counts of schools, hospitals, commercial establishments, restaurants, and public transport stops within a specified radius (e.g., 1 km) of each property, generating an "amenity score" that captures walkability and service accessibility (Boeing, 2017; Boeing, 2019).

The Python library `osmnx` (Boeing, 2017) provides programmatic access to OSM data for network analysis and amenity retrieval. Studies using OSM-derived features in property valuation include Fonte et al. (2017), who demonstrated that volunteered geographic information (VGI) from OSM can serve as a reliable proxy for land-use classification in European cities, and Yao et al. (2018), who used POI (Points of Interest) density from mapping platforms to predict housing prices in Chinese cities with significant accuracy gains.

### **2.5.4 Spatial Autocorrelation and Neighbor Price Effects**

A critical consideration in property valuation is **spatial autocorrelation**: properties located near each other tend to have similar prices, violating the independence assumption of standard regression (Anselin, 1988). This phenomenon is well-documented: housing prices exhibit positive spatial dependence because neighboring properties share the same schools, transportation access, environmental quality, and market conditions.

Two approaches address spatial effects in modeling:

1. **Spatial Lag Model (SLM)**: Includes a spatially weighted average of neighboring property prices as an independent variable, directly capturing the effect of nearby market conditions on a property's value.
2. **Moran's I Statistic**: A diagnostic measure of global spatial autocorrelation (Moran, 1950). A statistically significant positive Moran's I in the residuals of a non-spatial model indicates that spatial effects are present and should be incorporated.

For our study, we incorporate a **spatial lag variable**—the mean price of properties within a defined radius—as a feature in the ML models. This operationalizes Tobler's law within the predictive framework without imposing the parametric constraints of formal spatial econometric models.

### **2.5.5 Implications for Metro Cebu**

Metro Cebu presents a compelling context for geospatial feature engineering. The rapid development of infrastructure (CBRT, Metro Cebu Expressway), the heterogeneity of neighborhoods within a compact urban area, and the availability of geocoding services (Google Maps API) and open geospatial data (OSM) create the conditions for geospatial features to significantly enhance a data-driven valuation model. This is a key methodological contribution: no existing Cebu valuation study incorporates GIS-based proximity, amenity scoring, or spatial autocorrelation features derived from modern geospatial data sources.

---

## **2.6 Macroeconomic Determinants**

While local property attributes drive individual prices, macroeconomic factors drive the underlying trend. Nworah, Egbenta, and Ogbuefi (2023) studied the impact of inflation on real estate investment performance in Lagos (2005–2022) and found:

- **Exchange Rate vs. Real Estate**: r = **−0.925** (the strongest predictor).
- **Inflation vs. Real Estate**: r = **−0.508** (significant but weaker).

This finding is particularly relevant to the Philippine context. In 2024, OFW remittances reached a record **USD 38.3 billion** nationally. For Cebu, peso depreciation translates to more PHP per USD remitted, increasing OFW buying power and driving real estate demand. This mechanism—remittances amplified by exchange rate effects—helps explain the 11.5% property price growth in Metro Cebu.

To control for these time-trend effects, we include the **BSP RPPI quarterly index** as a macro control variable in our models, following Udomsap and Abid (2020), who confirmed that interest rates and macroeconomic conditions are significant determinants of housing prices.

---

## **2.7 Compliance and Explainability: IVS 2025**

The International Valuation Standards (2025), effective January 31, 2025, introduced two critical new chapters relevant to data-driven valuation:

- **IVS 104 (Data and Inputs)**: Mandates that data used in valuations must be Accurate, Complete, Timely, and Transparent. Sources must be traceable from their origin ("provenance requirement").
- **IVS 105 (Valuation Models)**: Explicitly states that *"No model without the valuer applying professional judgement can produce an IVS-compliant valuation."* Automated Valuation Models (AVMs) must be tested, transparent, and paired with professional review.

This standard has two direct implications for our study:

1. **SHAP Values for Transparency**: We employ SHAP (SHapley Additive exPlanations) to provide both global feature importance ("Which value drivers affect Metro Cebu prices most?") and local explanations ("This Lahug condo is +₱1.2M due to IT Park proximity, −₱300K due to small floor area"). This satisfies IVS 104's transparency requirement.
2. **Human-in-the-Loop Validation**: We engage licensed real estate brokers from the CPRE network to review model outputs, satisfying IVS 105's professional judgement mandate. This makes our model a *decision-support tool*, not a replacement for the appraiser.

---

## **2.8 Synthesis and Research Gap**

The literature converges on four key findings:

1. ✅ **Data scarcity** is the primary obstacle to accurate valuation in emerging markets (Kenya, Nigeria, Philippines).
2. ✅ **Tree-based ML models** (XGBoost, Random Forest) outperform neural networks on small (~1,000-observation) datasets (Tanzania).
3. ✅ **Geospatial features**—proximity analysis, amenity scoring, and spatial autocorrelation—significantly enhance property valuation accuracy, yet remain underutilized in Philippine studies.
4. ✅ **Models must support, not replace, human judgement** to comply with IVS 2025.

❌ **No Cebu-specific, transaction-based, ML-augmented valuation model with GIS-based feature engineering currently exists.**

Prior Philippine ML studies focus on Metro Manila (Perdio et al., 2023; Dann et al., 2020), Central Pangasinan (Viray, 2023), or use aggregate indices rather than property-level data (Ramolete et al., 2023). The only Cebu-specific study (Agosto, 2020) is survey-based, not data-driven. None incorporate GIS-derived features (geocoded proximity, OSM amenity scoring, spatial autocorrelation) or provide IVS-compliant explainability through a prescriptive geospatial visualization layer.

**This thesis fills that gap** by developing a data-driven valuation model for Metro Cebu that combines hybrid multi-source data, tree-based ML, GIS-based geospatial feature engineering, SHAP explainability, and human-in-the-loop validation—delivered through an interactive QGIS map for prescriptive decision support.

---

## **2.9 Bridge to Methodology**

The literature provides both the theoretical grounding (hedonic pricing theory, Tobler's First Law, IVS compliance) and the empirical evidence (Tanzania benchmarks, geospatial accuracy gains) to justify our methodological choices. Chapter 3 details the data sources, geospatial feature engineering pipeline, modeling strategy, and evaluation framework that operationalize these insights for the Metro Cebu context.
