# **Chapter 1 | The Problem and Its Setting**

## **1.1 Background of the Study**

### **1.1.1 What is Real Estate?**

Real estate is fundamental to both shelter and commerce. Under Article 415 of the Philippine Civil Code, immovable property encompasses land, any standing buildings, and permanent attachments. As one of the oldest asset classes, it serves dual roles: providing physical space and functioning as an investment vehicle.

In practice, a network of participants drives the real estate industry. Brokers and agents facilitate transactions. Banks finance purchases through mortgages, treating the property as collateral. Appraisers assess worth to ensure transaction prices reflect economic reality. Meanwhile, local government units (LGUs) set administrative benchmarks—such as zonal values—that dictate taxation. At the center of this ecosystem is the *price*: the single metric that buyers, sellers, lenders, and government officials must align on.

This study examines how that price is determined, its fairness, and the transparency of the valuation process.

### **1.1.2 Real Estate in Cebu**

Cebu is not just a tourist destination; it is one of the Philippines' most dynamic regional economies, growing at 7.3% in 2024 (PSA Region 7, 2025). This outpaces many developed cities nationwide. Key drivers include IT-BPM companies populating Cebu IT Park, expanding call centers leveraging the young workforce, and a post-pandemic tourism rebound revitalizing hospitality and retail.

This economic activity directly translates into real estate demand. Metro Cebu—spanning Cebu City, Mandaue, Lapu-Lapu, Talisay, Minglanilla, and Consolacion—now represents one of the country's most active property markets. It posted an 11.5% increase in residential property prices in 2025 alone, the highest growth rate outside the National Capital Region (BSP, 2025).

Infrastructure projects actively reshaping the city's geography exacerbate this pressure. The Cebu Bus Rapid Transit (CBRT), the Metro Cebu Expressway, and the South Road Properties development act as major value drivers. Historically, properties near infrastructure corridors appreciate faster than those further away—a pattern expected to repeat as these projects near completion (DPWH, 2025).

### **1.1.3 The Problem: How is Price Decided in Cebu?**

Given this rapid growth, the property pricing system in Metro Cebu remains surprisingly fragmented. It rests on three imperfect pillars:

1. **BIR Zonal Values**: These administrative benchmarks, set by the Bureau of Internal Revenue, compute transaction taxes but fail to reflect live market prices. A 2023 appraisal review found that only 60% of LGUs nationwide had updated their assessment schedules (Otsuka et al., 2023). Consequently, zonal values in many Cebu barangays remain stagnant while market prices climb.
2. **Bank Appraisals**: To protect lenders, bank appraisals often employ forced-sale metrics rather than mirroring the dynamic open market. Consequently, appraised values for mortgages frequently fall below what a willing buyer would actually pay.
3. **Online Listings and Agent Quoted Prices**: Conversely, these prices are aspirational, inflated by seller expectations, and lack standardization across the market.

This fragmentation creates a persistent **Valuation Gap**: a measurable divergence between official assessments and actual trading prices. For buyers, this gap generates confusion. For sellers, it leads to mispricing. For banks, it introduces risk. For LGUs, it results in foregone tax revenue. Despite these inefficiencies, Metro Cebu currently lacks a validated, property-level valuation model.

This issue extends beyond the Philippines. In Kenya, 427 registered valuers ranked "limited information" as the primary valuation problem (Cheloti & Mooya, 2021). Similarly, 92.7% of valuers in Lagos cited insufficient market evidence, contributing to valuation errors reaching +51% above the global norm (Ajibola, 2010). These are not failures of professional skill; they are failures of data and systems.

### **1.1.4 Why Metro Cebu, and Why Now?**

Three converging factors make it timely to build a data-driven valuation model for Metro Cebu:

1. **Rapid and Opaque Price Movement**: With 11.5% growth in 2025 and some zonal values outdated since 2019, the gap between official benchmarks and market reality is widening. Continued reliance on outdated models perpetuates mispricing.
2. **Infrastructure-Driven Spatial Disruption**: Projects like the CBRT and the Expressway are restructuring barangay accessibility and desirability. Traditional appraisal methods, reliant on historical comparables, cannot price these spatial changes in real-time. A GIS-augmented model built on geocoded property data addresses this constraint.
3. **Data Availability Meets Prescriptive Tools**: Online platforms (Lamudi, Dot Property), open geospatial data (OpenStreetMap), and geocoding tools (Google Maps API) enable the construction of a street-level dataset without requiring private deed-of-sale records. Furthermore, open-source GIS software allows us to transform this data into an interactive web map, providing prescriptive spatial decision support for practitioners.

### **1.1.5 Ideal Scenario**

Ideally, property pricing in Metro Cebu should be consistent, transparent, and defensible. A data-driven model that quantifies the contribution of specific value drivers—lot area, proximity to economic nodes, nearby amenities, and neighborhood trends—would provide reproducible estimates for residential properties. Delivered via an interactive QGIS map, this model would transition Cebu from heuristic pricing toward evidence-based valuation, aligning with international standards (IVS 2025) and serving all market stakeholders.

---

## **1.2 Statement of the Problem**

**Decision Problem**: How can real estate firms in Metro Cebu utilize data-driven models, augmented with geospatial feature engineering, to predict property values more accurately and consistently?

**Research Problem**: The limited application of predictive analytics, machine learning, and GIS-based features in local property valuation, combined with reliance on outdated administrative benchmarks, results in subjective pricing. Currently, no study synthesizes transaction-level data with GIS-derived geospatial features (proximity analysis, amenity scoring, spatial autocorrelation) for the Metro Cebu market, nor provides a prescriptive spatial visualization layer for decision support.visualization layer for decision support.

---

## **1.3 Research Questions**

1. What value drivers significantly influence property prices in Metro Cebu?
2. Which modeling technique—**Hedonic Regression**, **Random Forest**, or **XGBoost**—produces the most accurate valuation out of sample (lowest MAPE)?
3. Do **geospatial features**—proximity to economic nodes, amenity density, and spatial autocorrelation—significantly improve model performance compared to structural-only models?
4. How large is the "Valuation Gap" between the model's data-driven predictions and traditional BIR Zonal Values?

---

## **1.4 Significance of the Study**

Addressing this valuation gap benefits multiple stakeholders:

1. **Real Estate Brokers and Appraisers**: Provides standardized tools compliant with IVS 2025 transparency requirements, offering SHAP-based explainability and an interactive QGIS map for spatial analysis.
2. **Property Investors**: Ensures fair, data-backed pricing and helps identify undervalued areas visually through geospatial heatmaps.
3. **Banks and Lending Institutions**: Improves collateral assessment accuracy via reproducible, auditable models.
4. **Local Government Units (LGUs)**: Facilitates the updating of zonal values using market-based evidence, mapping the geographic divergence between official and actual prices.

This study is significant within the Philippine context as the first Cebu-specific, data-driven valuation model integrating GIS-based feature engineering. While prior Philippine machine learning studies focus on Metro Manila or use aggregate indices, no work applies geocoded proximity analysis, OSM amenity scoring, and spatial autocorrelation to transaction-level data for Metro Cebu. By delivering results through an interactive QGIS map, this study extends beyond predictive analytics into prescriptive decision support, offering a practical tool for professionals in a fragmented market.

---

## **1.5 Scope and Limitations**

### **Scope**

This study focuses on the residential real estate market within Metro Cebu. While the National Economic and Development Authority (NEDA) defines Metro Cebu as encompassing 13 LGUs, this study operationally scopes "Metro Cebu" to its central urban core: **Cebu City, Mandaue, Lapu-Lapu, Talisay, Minglanilla, and Consolacion**. This constraint ensures high data density and robust geospatial analysis, as these six LGUs represent the most active transaction zones and the highest concentration of infrastructure development.

The primary data sources include:

- **Institutional foreclosed and acquired listings** (floor price) from BDO Unibank, Pag-IBIG Fund (HDMF), PNB, RCBC, and Union Bank. Aggregating multiple sources prevents pricing bias.
- **Publicly available online listings** from Lamudi and Dot Property, proxying "fair market" asking prices (ceiling price).
- **BIR Zonal Values** serving as the administrative benchmark at the barangay level.
- **BSP RPPI** as a macroeconomic time-trend control.
- **Google Maps API** for converting property addresses to latitude and longitude coordinates.
- **OpenStreetMap (OSM)** for retrieving amenity and land-use data within property vicinities.

The study evaluates three predictive models: **Hedonic Regression (OLS)**, **Random Forest**, and **XGBoost** (see Section 1.6 for rationale). Geospatial features are engineered via geocoding, Haversine proximity analysis, OSM amenity scoring, and spatial lag computation.

The primary deliverable is an **interactive QGIS map** visualizing property-level predictions, the Valuation Gap, and spatial price patterns.

### **Limitations**

1. **Data Source Bias**: Foreclosed assets reflect prices lower than the open market average. While the hybrid strategy brackets the true value, it does not directly observe it. We mitigate this using a source indicator variable.
2. **Unobserved Heterogeneity**: The model cannot capture qualitative features omitted from listings, such as interior finish quality or views, typically assessed during physical inspections.
3. **Geospatial Approximation**: Addresses are geocoded via Google Maps API, which may introduce minor spatial errors compared to exact lot-parcel shapefiles. Additionally, OSM coverage in peripheral barangays may be less robust than in the urban core.
4. **Temporal Scope**: The analysis provides a cross-sectional snapshot as of late 2025; it does not capture long-term cyclical real estate trends.
5. **Geographic Coverage**: The six selected LGUs represent the urban conurbation but exclude the broader municipalities of Cebu Province.

---

## **1.6 Model Selection Rationale**

This study employs three complementary models that span the interpretability–accuracy spectrum. This trio has been validated in comparable emerging-market real estate studies (Yacim & Boshoff, 2018; Pai & Wang, 2020).

- **Hedonic Regression (OLS)** serves as the interpretable baseline. It is the established standard in property valuation (Rosen, 1974), embedded in both the Philippine Valuation Standards (PVS, 2018) and IVS 2025. OLS produces explicit coefficients for each value driver, directly quantifying their price contribution. We extend it with a spatial lag term to account for autocorrelation among neighboring properties.
- **Random Forest** (Breiman, 2001) addresses the linearity assumption of OLS by capturing non-linear interactions between value drivers—particularly relevant for our hybrid dataset, where foreclosed and listed properties may occupy different pricing regimes. Its bagging mechanism also provides robustness against outliers.
- **XGBoost** (Chen & Guestrin, 2016) is the primary candidate for predictive accuracy: it consistently achieves top performance on structured tabular data (Grinsztajn et al., 2022) and integrates natively with SHAP (Lundberg & Lee, 2017) to provide property-level explainability, a practical requirement under IVS 2025 transparency standards.

### **Why Not Other Models?**

Several alternatives were evaluated but ultimately set aside:

| Model                       | Rationale for Exclusion                                                                                          |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Deep Neural Networks        | Require >10,000 labeled samples; our dataset size is insufficient, and global interpretability is sacrificed.    |
| Support Vector Regression   | Computationally expensive to tune; poor native interpretability; generally weaker than boosting on tabular data. |
| k-Nearest Neighbors         | Lacks model coefficients for explanatory analysis; highly sensitive to feature scale.                            |
| Gaussian Process Regression | Computationally intractable beyond ~2,000 samples.                                                               |
| LASSO / Ridge               | Constrained by linearity assumptions; effectively subsumed by the OLS baseline for our purposes.                 |

---

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

- **Kenya**: Cheloti and Mooya (2021) conducted a census survey of 427 registered valuers in Nairobi. "Limited information" was ranked as the primary valuation problem (Mean Rank 2.91), while valuer misconduct ranked last (2.32). They concluded that limited and unreliable information, rather than incompetence, causes valuation problems.
- **Nigeria (Lagos)**: Ajibola (2010) surveyed 300 valuers and found that 92.7% cited insufficient market evidence as the primary challenge. Valuation inaccuracy ranged from +24.8% to +51.5%, far exceeding the global norm of ±10%.
- **Sub-Saharan Africa**: Becsky-Nagy and Sachicola (2025) conducted a systematic review across 46 countries, finding a strong negative correlation between urbanization and credit access (r = −0.935). This suggested that financial infrastructure failed to keep pace with rapid urban growth—a pattern relevant to Metro Cebu's expansion.

These findings confirm that valuation inaccuracy is fundamentally a *data problem*. If the problem is data, the solution lies in data science.

---

## **2.4 Modeling Approaches: Traditional vs. Machine Learning**

### **2.4.1 Hedonic Regression**

Classical hedonic regression models decompose property price into a function of structural and locational attributes, typically in a log-linear form (Rosen, 1974; Malpezzi, 2003). Spatial econometrics extends this framework by incorporating neighborhood effects and spatial autocorrelation (Anselin, 1988). For the Philippines, Dann et al. (2020) applied hedonic and spatial models to Metro Manila data (2000–2010) and found that structural variables, environmental quality, and spatial spillovers all significantly explain price variation.

### **2.4.2 Philippine Machine Learning Studies**

More recent Philippine work incorporates machine learning:

- **Viray (2023)** compared Multiple Linear Regression with Random Forest for predicting property prices in Central Pangasinan, combining BIR zonal values, BSP RPPI, and construction cost indices. The tree-based model achieved a lower prediction error.
- **Ramolete et al. (2023)** demonstrated that incorporating government indicators improves ML valuation accuracy, achieving a MAPE of 10–21% with larger, cleaner datasets.
- **Perdio et al. (2023)** tested linear models against gradient boosting on Manila listings, finding gradient boosting superior after feature selection.

### **2.4.3 International Evidence: The Tanzania Benchmark**

The most directly relevant international study is Nyanda, Mattsson, and Wilhelmsson (2024), who tested eight ML algorithms on approximately 954 residential properties in Dar es Salaam—a sample size nearly identical to our BDO dataset.

| Model          | MAPE                                             |
| -------------- | ------------------------------------------------ |
| Neural Network | 108.6% (failed due to overfitting on small data) |
| Random Forest  | 52.7%                                            |
| XGBoost        | **48.0%**                                  |

This empirical evidence explicitly justifies prioritizing Random Forest and XGBoost over deep learning architectures. Neural networks are powerful but require substantially larger datasets to avoid overfitting. For datasets of ~1,000 observations, tree-based ensembles are the proven, optimal choice.

### **2.4.4 Southeast Asian Applications**

Beyond Africa, studies in rapidly urbanizing Southeast Asian emerging markets—which closely mirror the Philippines' economic structure—further validated combining spatial data with ensemble models. In Indonesia, Wibowo et al. (2023) demonstrated that integrating macroeconomic and spatial features (such as geographic coordinates and proximity to amenities) significantly improved predictive accuracy for residential property valuation in Surabaya. Similarly, in Malaysia, Samsudin et al. (2022) applied Random Forest models augmented with geographic information systems (GIS) to value heritage properties in Penang, finding that spatial data visualization dramatically improved valuation precision over traditional econometric methods. These regional studies emphasized that in data-scarce, highly dynamic urban environments, integrating GIS coordinates within tree-based machine learning models provided the most robust valuation framework.

### **2.4.5 Comparative Reviews**

Broader systematic reviews confirm this pattern. Wang and Li (2020) surveyed deep learning methods in real estate and found that while neural networks excel with image data, tree-based ensembles (Random Forest, XGBoost) remain highly competitive for structured tabular data. Moreno-Foronda et al. (2025) and Sharma et al. (2024) similarly demonstrated XGBoost's consistent superiority in house price prediction tasks. Furthermore, Hu et al. (2024) showed that advances in Explainable AI (XAI) using SHAP values bridge the interpretability gap between "black box" ML models and transparent hedonic regression.

---

## **2.5 Geospatial Feature Engineering in Property Valuation**

Real estate is inherently spatial: a property's value is determined not only by its physical attributes but also by *where* it is located and *what surrounds it*. Tobler's First Law of Geography—"Everything is related to everything else, but near things are more related than distant things" (Tobler, 1970)—provides the theoretical basis for incorporating geospatial features into valuation models.

### **2.5.1 Geocoding and Location Precision**

Geocoding—the process of converting addresses into geographic coordinates (latitude/longitude)—is a foundational step in geospatial property analysis. Modern geocoding services such as the **Google Maps Geocoding API** provide high-precision coordinates from unstructured or semi-structured address strings, enabling consistent spatial analysis even when input addresses vary in format or completeness. Google Maps API is widely used in urban analytics for its global coverage, address disambiguation capabilities, and integration with the Google Places ecosystem, which provides supplementary metadata on nearby amenities and land use (Google Developers, 2025).

For open-source alternatives, **OpenStreetMap (OSM)** via the Nominatim geocoder provides community-maintained geospatial data at no cost. While OSM coverage varies by region, urban areas in the Philippines—particularly Metro Cebu—have beneficiary coverage from the local OpenStreetMap community and humanitarian mapping initiatives (Humanitarian OpenStreetMap Team, 2024). This study employs Google Maps API as the primary geocoding engine for address-to-coordinate conversion, supplemented by OSM for amenity and land-use data retrieval.

### **2.5.2 Proximity Analysis and Accessibility**

Distance-based features—proximity to commercial centers, transportation hubs, schools, and employment nodes—are robust value drivers in hedonic pricing literature (Rosen, 1974; Malpezzi, 2003). Computations utilizing the Haversine formula are the standard for estimating geographic distances in urban property studies (Sinnott, 1984).

Agosto (2020) confirmed that transport accessibility is the primary driver of land values in Cebu, followed by neighborhood quality. For Metro Cebu, proximity to key economic nodes—Cebu IT Park, Ayala Center Cebu, SM Seaside City, Mactan-Cebu International Airport—and planned infrastructure like the Cebu Bus Rapid Transit (CBRT) stations provide critical, measurable value signals.

### **2.5.3 Amenity Scoring via OpenStreetMap**

Beyond direct point-to-point distances, the density and diversity of amenities within a defined radius present a richer characterization of neighborhood quality. OSM's tagging system allows researchers to query counts of schools, hospitals, commercial establishments, restaurants, and public transport stops within a specified radius of a property. This "amenity score" effectively captures walkability and local service accessibility (Boeing, 2017, 2019).

The Python library `osmnx` provides programmatic access to OSM data for network analysis and amenity retrieval. Studies validating OSM-derived features in property valuation include Fonte et al. (2017), who demonstrated that volunteered geographic information (VGI) from OSM serves as a reliable proxy for land-use classification in Europe, and Yao et al. (2018), who used Point of Interest (POI) density to substantially improve housing price predictions in China.

Crucially, the reliability of OpenStreetMap data has been explicitly validated in the Philippine context. Alvarez et al. (2021) from the University of the Philippines developed "Project OHANA" (Open-source Heatmap and Analytics for Nationwide Amenities Accessibility in the Philippines). By utilizing OSM data and gravitational models, they mapped nationwide spatial inequality and amenity accessibility. Their framework demonstrated that OSM data in the Philippines was sufficiently robust for rigorous spatial analysis, urban planning, and property valuation modeling.

### **2.5.4 Spatial Autocorrelation and Neighbor Price Effects**

A critical consideration in property valuation is **spatial autocorrelation**: properties located near each other tend to have similar prices, violating the independence assumption of standard regression (Anselin, 1988). This phenomenon is well-documented: housing prices exhibit positive spatial dependence because neighboring properties share the same schools, transportation access, environmental quality, and market conditions.

Two approaches address spatial effects in modeling:

1. **Spatial Lag Model (SLM)**: Includes a spatially weighted average of neighboring property prices as an independent variable, directly capturing the effect of nearby market conditions on a property's value.
2. **Moran's I Statistic**: A diagnostic measure of global spatial autocorrelation (Moran, 1950). A statistically significant positive Moran's I in the residuals of a non-spatial model indicates that spatial effects are present and should be incorporated.

For our study, we incorporate a **spatial lag variable**—the mean price of properties within a defined radius—as a feature in the ML models. This operationalizes Tobler's law within the predictive framework without imposing the parametric constraints of formal spatial econometric models.

### **2.5.5 Implications for Metro Cebu**

Metro Cebu presents a compelling context for geospatial feature engineering. The rapid development of infrastructure (CBRT, Metro Cebu Expressway), the heterogeneity of neighborhoods within a compact urban area, and the availability of geocoding services (Google Maps API) and open geospatial data (OSM) create the conditions for geospatial features to significantly enhance a data-driven valuation model. This is a key methodological contribution: no existing Cebu valuation study incorporates GIS-based proximity, amenity scoring, or spatial autocorrelation features derived from modern geospatial data sources.

---

## **2.6 Integrating Value Drivers: Indexing vs. Raw Features**

A critical challenge in geospatial ML models is how to operationalize distance metrics. Agosto (2020) identified transport accessibility and neighborhood quality as the primary value drivers in Cebu based on practitioner surveys. To integrate these findings into a machine learning pipeline, raw geospatial distances (e.g., Euclidean distance to the nearest hospital, school, or mall) are often insufficient on their own, as they can suffer from multicollinearity—a scenario where multiple distance variables are highly correlated with one another, complicating the model's feature importance weights.

To resolve this, recent literature advocated for the construction of "Accessibility Indices" or "Amenity Scores" before feeding spatial data into the predictive model. Rey-Blanco, Zofío, and González-Arias (2024) demonstrated this approach by building optimal walk and car accessibility indices from raw point-of-interest data. They found that integrating these structured, composite indices into hedonic regression and Random Forest analyses significantly improved housing price predictions compared to using raw, unaggregated distance features. By aggregating individual distances and counts into unified themes (e.g., a "Commercial Density Score" or "Transit Accessibility Index"), models could capture the holistic utility of a location while maintaining statistical robustness and interpretability. This study extends this indexing framework to methodically map Agosto's (2020) qualitative drivers into quantitative ML inputs.

---

## **2.7 Macroeconomic Determinants**

While local property attributes drive individual prices, macroeconomic factors drive the underlying trend. Nworah, Egbenta, and Ogbuefi (2023) studied the impact of inflation on real estate investment performance in Lagos (2005–2022) and found:

- **Exchange Rate vs. Real Estate**: r = **−0.925** (the strongest predictor).
- **Inflation vs. Real Estate**: r = **−0.508** (significant but weaker).

This finding is particularly relevant to the Philippine context. In 2024, OFW remittances reached a record **USD 38.3 billion** nationally. For Cebu, peso depreciation translates to more PHP per USD remitted, increasing OFW buying power and driving real estate demand. This mechanism—remittances amplified by exchange rate effects—helps explain the 11.5% property price growth in Metro Cebu.

To control for these time-trend effects, we include the **BSP RPPI quarterly index** as a macro control variable in our models, following Udomsap and Abid (2020), who confirmed that interest rates and macroeconomic conditions are significant determinants of housing prices.

---

## **2.8 Compliance and Explainability: IVS 2025**

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

---

# **Chapter 3 | Research Methodology**

## **3.1 Research Design**

This study will employ a **quantitative, non-experimental design** focused on predictive and prescriptive analytics. Specifically, we will use a supervised learning approach to estimate residential property values in Metro Cebu and will visualize the results through an interactive GIS platform for prescriptive decision support. The dependent variable will be the property price (or price per square meter), and the independent variables will encompass structural features, geospatial value drivers, administrative benchmarks, and macroeconomic indicators.

The study will compare three supervised learning models to quantify the trade-off between interpretability and predictive accuracy, while testing the incremental value of GIS-derived features and administrative data:

1. **Ordinary Least Squares (OLS) / Hedonic Regression**: An interpretable baseline grounded in Hedonic Pricing Theory (Rosen, 1974). Coefficients carry direct economic meaning (e.g., "each additional bedroom adds ₱X to value").
2. **Random Forest Regressor**: A tree-based ensemble that captures non-linear relationships and feature interactions without requiring explicit specification (Breiman, 2001).
3. **XGBoost Regressor**: A gradient boosting algorithm optimized for predictive accuracy on structured tabular data (Chen & Guestrin, 2016). Empirically, XGBoost often performs well on datasets of similar scale (Nyanda et al., 2024).

---

## **3.2 Data Sources: The Hybrid Strategy**

To overcome the data scarcity challenge identified in the literature (Cheloti & Mooya, 2021), we will aggregate multiple data sources into a hybrid dataset. Since actual Deed of Sale transaction data is private and inaccessible, we will bracket the "True Market Value" between a conservative floor and a speculative ceiling.

| Source                             | Role                      | Volume                     | Nature                    |
| ---------------------------------- | ------------------------- | -------------------------- | ------------------------- |
| **Bank Foreclosures**        | Verified Floor Price      | BDO, PNB, RCBC, Union Bank | Conservative / Distressed |
| **Pag-IBIG / Gov't Assets**  | Verified Floor Price      | HDMF acquired assets       | Conservative / Distressed |
| **Online Listings** (Lamudi) | Market Ceiling Price      | Target: 500+               | Asking / Speculative      |
| **BIR Zonal Values**         | Administrative Benchmark  | Per barangay               | Static / Regulatory       |
| **BSP RPPI**                 | Time-Trend Control        | Quarterly index            | Macro / Cyclical          |
| **Google Maps API**          | Geocoding / Location Data | Per property               | Geospatial / Dynamic      |
| **OpenStreetMap (OSM)**      | Amenity & Land-Use Data   | Per property radius        | Geospatial / Open Data    |

### **3.2.1 Primary Data: Verified Floor Price (Foreclosed / Acquired Assets)**

The floor price dataset will aggregate foreclosed and acquired property listings from multiple institutional sources to prevent single-source bias:

- **BDO Unibank**: 955 raw foreclosure entries nationwide (as of November 18, 2025).
- **Pag-IBIG Fund (HDMF)**: Acquired assets representing the affordable housing segment.
- **PNB, RCBC, and Union Bank**: Additional listings to broaden coverage.
- **SSS / GSIS**: Government-acquired properties within Metro Cebu.

These distressed assets, priced below standard market rates to ensure liquidity, will serve as the conservative price floor. Aggregating across multiple institutions will mitigate pricing strategy bias.

**Sample Data Structure: BDO Foreclosures (Raw vs. Cleaned)**

| Raw Column (BDO Excel)   | Processed Feature           | Description                  |
| :----------------------- | :-------------------------- | :--------------------------- |
| `REGION`               | `Region`                  | Filtered to Region VII       |
| `CITY_PROVINCE`        | `City`                    | Filtered to Metro Cebu LGUs  |
| `PROPERTY_ADDRESS`     | `Address`                 | Geocoded string              |
| `LOT_AREA`             | `Lot Area`                | Numeric (sqm)                |
| `FLOOR_AREA`           | `Floor Area`              | Numeric (sqm)                |
| `MINIMUM_BID_PRICE`    | `Actual Price`            | Numeric target variable (₱) |
| `PROPERTY_DESCRIPTION` | `Bedrooms`, `Bathrooms` | Parsed via regex             |

### **3.2.2 Secondary Data: Market Ceiling Price (Online Listings)**

To denote "fair market" asking prices, we will collect current residential listings from public online platforms, primarily Lamudi. As validated by Sousa et al. (2024), aggregating thousands of online listings captures pricing clusters often missed by sparse official records. We will target 500+ Metro Cebu residential listings.

**Sample Data Structure: Lamudi Listings (Raw vs. Cleaned)**

| Raw Field (Web Scrape)       | Processed Feature           | Description                                       |
| :--------------------------- | :-------------------------- | :------------------------------------------------ |
| `Location`                 | `Barangay`, `City`      | Parsed location string                            |
| `Price`                    | `Actual Price`            | Target variable (₱), cleaned of currency symbols |
| `Bedrooms`                 | `Bedrooms`                | Numeric extract                                   |
| `Bathrooms`                | `Bathrooms`               | Numeric extract                                   |
| `Floor area`               | `Floor Area`              | Numeric extract (sqm)                             |
| `Land Size`                | `Lot Area`                | Numeric extract (sqm)                             |
| `Latitude` / `Longitude` | `Latitude`, `Longitude` | Direct coordinate mapping                         |

### **3.2.3 Administrative and Macroeconomic Data**

- **BIR Zonal Values**: Official zonal values per barangay, to be used both as a model feature and to calculate the "Valuation Gap" (Market Price − Zonal Value).
- **BSP RPPI**: Quarterly Residential Real Estate Price Index for Areas Outside NCR (AONCR), controlling for time-trend effects (inflation/market cycle).

### **3.2.4 Geospatial Data Sources**

- **Google Maps Geocoding API**: Will convert property addresses into precise latitude/longitude coordinates, enabling all subsequent spatial analyses. Chosen for its superior address disambiguation in Philippine contexts.
- **OpenStreetMap (OSM)**: Will provide open geospatial data for amenity density analysis. Will be queried via the `osmnx` Python library (Boeing, 2017) to retrieve counts of schools, hospitals, commercial establishments, restaurants, and public transport stops within defined radii of each property.

### **3.2.5 Target Variable**

Given this hybrid strategy, BDO foreclosure prices will serve as the floor, and Lamudi listings will serve as the ceiling. We will include a source indicator variable in the model to account for systematic price-level differences between distressed and market listings. This will allow the model to learn the structural relationship between property attributes and price across both market segments.

**Final Feature Matrix Schema (Pre-Modeling)**

| Feature Group         | Variables                                                                    | Type                  |
| :-------------------- | :--------------------------------------------------------------------------- | :-------------------- |
| **Identifiers** | `ID`, `Source` (BDO/Lamudi)                                              | Categorical           |
| **Structural**  | `Lot Area`, `Floor Area`, `Bedrooms`, `Bathrooms`, `Property Type` | Numeric / Categorical |
| **Locational**  | `Latitude`, `Longitude`, `Barangay`                                    | Numeric / Categorical |
| **Geospatial**  | `Dist_CBD`, `Dist_Airport`, `Dist_CBRT`                                | Numeric (Meters)      |
| **Amenity**     | `OSM_Amenity_Score`                                                        | Numeric (Count/Index) |
| **Economic**    | `BIR_Zonal_Value`, `Spatial_Lag_Mean`                                    | Numeric (₱)          |
| **Target**      | `Actual Price`, `Log_Price`                                              | Numeric (₱)          |

### **3.2.6 Validation Layer: Human-in-the-Loop**

To comply with IVS 2025 (IVS 105) and ground the computational model in local reality, licensed real estate brokers from the CPRE network will serve as a validation layer:

1. **Sanity Check**: Reviewing SHAP-derived value driver rankings against domain knowledge.
2. **Outlier Review**: Investigating properties with high prediction error to identify data quality issues vs. genuine market anomalies.

---

## **3.3 Data Pipeline**

The data pipeline will follow five stages, implemented in Python:

1. **Ingestion**: We will ingest BDO Excel files via Pandas and will collect Lamudi listings using web scraping logic.
2. **Filtering**: The dataset will be restricted to residential properties within Metro Cebu (Cebu City, Mandaue, Lapu-Lapu, Talisay, Minglanilla, and Consolacion).
3. **Regex Parsing and Cleaning**:
   - *BDO Data*: The `Property Description` string often bundles features (e.g., "3BR 2TB"). We will apply regex patterns to extract `Bedrooms` and `Bathrooms`. Missing values in lot/floor area will be imputed based on the median of similar property types in the same barangay.
   - *Lamudi Data*: Scraped fields often contain varying text formats (e.g., "₱ 5,000,000" or "Contact agent for price"). We will clean currency symbols and commas, dropping rows without explicit numerical prices.
4. **Geocoding**: We will batch-process addresses through the Google Maps Geocoding API, standardizing barangay names and securing precise coordinates.
5. **GIS Augmentation**: From these geocoded coordinates, we will engineer geospatial features:
   - Proximity metrics (Haversine distances to key economic nodes).
   - Amenity scores (OSM-derived counts within a 1 km radius).
   - Spatial lag (mean price of neighboring properties within a 1 km radius).

**Tools**: Python (Pandas, Scikit-learn, XGBoost, osmnx), Google Maps API for geocoding, QGIS for spatial visualization.

---

## **3.4 Feature Engineering**

| Category                 | Features                                                                             | Source             |
| ------------------------ | ------------------------------------------------------------------------------------ | ------------------ |
| **Structural**     | Lot Area, Floor Area, Bedrooms, Bathrooms, Parking, Property Type                    | BDO / Lamudi       |
| **Locational**     | Barangay, Latitude/Longitude                                                         | Google Maps API    |
| **Geospatial** ⭐  | Proximity to Ayala, IT Park, SM Seaside, Airport,**CBRT stations** (Haversine) | Geocoding + GIS    |
| **Amenity Score**  | Count of schools, hospitals, commercial centers, transit stops within 1 km radius    | OSM / osmnx        |
| **Spatial Lag**    | Mean price of neighboring properties within defined radius                           | Computed from data |
| **Administrative** | BIR Zonal Value (per barangay)                                                       | BIR schedules      |
| **Macro**          | BSP RPPI quarterly index                                                             | BSP data           |
| **Data Source**    | Source indicator (BDO vs. Lamudi)                                                    | Engineered         |

**Engineered variables**: Price per sqm, Valuation Gap (Price − Zonal Value), Log(Price).

### **3.4.1 Geospatial Feature Engineering**

This is the core methodological contribution of this study. Geospatial features will be extracted through the following pipeline:

1. **Geocoding (Google Maps API)**: Each property address will be geocoded to obtain precise latitude/longitude coordinates. The Google Maps Geocoding API has been chosen for its superior handling of Philippine address formats, which often include barangay names, landmarks, or informal location descriptors.
2. **Proximity Features (Haversine Formula)**: For each geocoded property, the Haversine formula will compute great-circle distances to key economic and infrastructure nodes:

- Ayala Center Cebu (primary CBD)
  - Cebu IT Park (employment hub)
  - SM Seaside City (commercial center)
  - Mactan-Cebu International Airport
  - Planned Cebu Bus Rapid Transit (CBRT) station locations

3. **Custom Value Driver Scoring Model (OSM via osmnx)**:
   Rather than relying solely on arbitrary distances, we will develop a custom amenity scoring model using OpenStreetMap data. Utilizing the `osmnx` library, we will query points of interest (POI) within a 1 kilometer network radius of each property. We will select a 1 km radius as it generally corresponds to a 10-15 minute walkable catchment area. The amenity score will be computed not just as a raw count, but as a weighted index reflecting urban density:

   - Educational institutions (schools, universities): Standard weight
   - Healthcare facilities (hospitals, clinics): High weight
   - Commercial establishments (malls, markets): Medium weight
   - Public transport stops (jeepney routes, bus stops): High weight

   *Note: Specific weight allocations will be finalized during initial exploratory data analysis to ensure they reflect local variance correctly.*
4. **Spatial Lag Variable**: To capture neighborhood price effects (spatial autocorrelation), we will compute the mean actual price of all other properties within a 1 kilometer radius of the target property. This will operationalize Tobler's First Law—that near things are more related than distant things—directly into our non-spatial ML algorithms.

---

## **3.5 Pre-processing**

| Step                         | Method                                     | Rationale                                      |
| ---------------------------- | ------------------------------------------ | ---------------------------------------------- |
| **Outlier Detection**  | IQR (Interquartile Range) method           | Statistically principled; no arbitrary cutoffs |
| **Log Transformation** | ln(Price) as target variable               | Normalizes the right-skewed price distribution |
| **Missing Values**     | Barangay-level median imputation           | Preserves local spatial context                |
| **Encoding**           | One-Hot Encoding (Property Type, Barangay) | Required for regression and tree-based models  |

---

## **3.6 Modeling Strategy**

### **3.6.1 The Three Models**

| # | Model                              | Strength                                          | Weakness                 |
| - | ---------------------------------- | ------------------------------------------------- | ------------------------ |
| 1 | **Hedonic Regression (OLS)** | Interpretable; coefficients have economic meaning | Assumes linearity        |
| 2 | **Random Forest**            | Handles non-linearities; robust to overfitting    | Less interpretable       |
| 3 | **XGBoost**                  | Best predictive performance on tabular data       | Hyperparameter-sensitive |

### **3.6.2 Hedonic Equation**

The hedonic regression will take the following log-linear form:

$$
\ln(Price) = \alpha + \beta_1 \ln(Area) + \beta_2(BR) + \beta_3(Dist_{CBD}) + \beta_4(ZonalValue) + \beta_5(AmenityScore) + \beta_6(SpatialLag) + \epsilon
$$

Where $AmenityScore$ represents the OSM-derived neighborhood quality index, $SpatialLag$ captures neighboring property price effects, and $ZonalValue$ is the BIR benchmark. This specification will extend the traditional hedonic model by explicitly incorporating GIS-derived geospatial features and administrative data.

### **3.6.3 Hyperparameter Tuning**

For the ML models (Random Forest and XGBoost), hyperparameters will be optimized via **GridSearchCV** with **K-Fold Cross Validation** (K = 5 or 10, depending on final sample size). This will avoid overfitting while maximizing generalization performance.

---

## **3.7 Evaluation and Explainability**

### **3.7.1 Performance Metrics**

| Metric         | Description                    | Purpose                                        |
| -------------- | ------------------------------ | ---------------------------------------------- |
| **MAPE** | Mean Absolute Percentage Error | Primary metric; enables cross-study comparison |
| **R²**  | Coefficient of Determination   | Proportion of variance explained               |
| **MAE**  | Mean Absolute Error (in ₱)    | Business-interpretable error                   |
| **RMSE** | Root Mean Square Error         | Penalizes large errors                         |

### **3.7.2 Benchmark Targets**

| Study                  | Context                     | MAPE    | Our Target                                           |
| ---------------------- | --------------------------- | ------- | ---------------------------------------------------- |
| Ramolete et al. (2023) | Philippines, larger dataset | 10–21% | < 25% (they had larger, cleaner data)                |
| Nyanda et al. (2024)   | Tanzania, n ≈ 954          | 48%     | Beat 48% (same sample size, but we add GIS features) |

### **3.7.3 SHAP Explainability**

To satisfy IVS 2025 transparency requirements (IVS 104) and provide actionable insights, we will employ **SHAP (SHapley Additive exPlanations)**:

- **Global SHAP (Summary Plots)**: Will identify which value drivers affect Metro Cebu property prices most across the entire dataset. This will answer RQ1 ("What value drivers significantly influence property prices in Metro Cebu?").
- **Local SHAP (Force Plots)**: Will explain individual predictions. For example: *"This Lahug condo is valued at ₱X: +₱1.2M due to IT Park proximity, −₱300K due to small floor area, +₱200K due to high amenity score."*

This dual-level explainability will make the model transparent and auditable, positioning it as a **decision-support tool** rather than a black box.

---

## **3.8 Deliverables**

### **3.8.1 QGIS Interactive Map (Primary Deliverable)**

The core prescriptive output will be a QGIS interactive project map. This will not be a static image, but an exploratory environment designed for decision support consisting of the following key layers:

1. **Property Valuations**: Point vectors representing individual geocoded properties. They will be color-coded based on the model's prediction error (actual vs. predicted), allowing users to visually identify undervalued anomalies or overvalued clusters.
2. **Valuation Gap Heatmap**: A raster heatmap visualizing the divergence between the ML model predictions and the official BIR Zonal Values. Hotspots will indicate areas where official valuations significantly lag market realities.
3. **CBRT & Infrastructure Overlays**: Line segments denoting the planned CBRT route with 500m and 1km buffer zones. This will allow users to visualize how upcoming public transit infrastructure intersects with current market valuations.
4. **Value Driver Contours**: ISO-chrones or distance contours measuring proximity to the CBD (Ayala Center) or IT Park.

This deliverable will transform the ML model from a theoretical exercise into an actionable system, equipping brokers, investors, and local government units with spatial intelligence.

### **3.8.2 Streamlit Web Application (Exploratory)**

Complementing the QGIS map, we will provide an interactive Streamlit web dashboard. Users will be able to input specific property structural features (e.g., floor area, bedrooms) and select a location on a map. The application will then query the underlying trained XGBoost/Random Forest model and output a predicted price along with a SHAP Waterfall plot. This will dynamically explain *why* the property received that specific valuation, detailing the exact peso contribution of each feature.

---

## **3.9 Timeline and Milestones**

| Phase                   | Activity                                               | Timeline         |
| ----------------------- | ------------------------------------------------------ | ---------------- |
| **1. Data**       | Lamudi scraping + BDO cleaning                         | Feb 18 – Feb 28 |
| **2. Proposal**   | Panel Presentation                                     | Feb 21           |
| **3. Build**      | Geocoding + GIS feature engineering (Google Maps, OSM) | Mar 1 – Mar 14  |
|                         | Model training + Hyperparameter tuning                 | Mar 15 – Mar 28 |
| **4. Colloquium** | Research updates presentation                          | Mar 28           |
| **5. Evaluate**   | SHAP analysis + QGIS map + Broker validation           | Apr 1 – Apr 18  |
| **6. Write**      | Draft final paper (Chapters 4–10)                     | Apr 18 – May 2  |
| **7. Defend**     | Final Research Paper presentation                      | May 9            |
|                         | Final Submission                                       | May 23           |
