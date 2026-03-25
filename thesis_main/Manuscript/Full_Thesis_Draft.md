# **Chapter 1 | The Problem and Its Setting**

## **1.1 Background of the Study**

### **1.1.1 What is Real Estate?**

Real estate sits at the intersection of shelter, commerce, and investment. Under Article 415 of the Philippine Civil Code, immovable property includes land, buildings, and permanent attachments. Unlike many other assets, real estate is both something people use and something they price, finance, and trade.

In actual transactions, that price is shaped by several actors with different interests. Brokers and agents facilitate sales, banks finance purchases and assess collateral risk, appraisers estimate value, and local government units set administrative benchmarks such as zonal values for taxation. Although these actors approach property from different functions, all depend on a defensible estimate of value. This study examines how that value is determined, how fair it is, and how transparent the valuation process is.

### **1.1.2 Real Estate in Cebu**

Cebu has become one of the Philippines' most dynamic regional economies, recording 7.3% growth in 2024 (PSA Region 7, 2025). Much of this growth has come from the IT-BPM sector, the expansion of call center activity, and the post-pandemic recovery of tourism, hospitality, and retail. These shifts have fed directly into demand for residential and mixed-use property.

Across Metro Cebu, particularly Cebu City, Mandaue, Lapu-Lapu, Talisay, Minglanilla, and Consolacion, that demand has made the property market notably active. Residential property prices in the area rose by 11.5% in 2025, the highest rate outside the National Capital Region (BSP, 2025).

That pressure is also being reinforced by infrastructure projects that are changing accessibility across the urban area. The Cebu Bus Rapid Transit (CBRT), the Metro Cebu Expressway, and the continued development of the South Road Properties are likely to affect land values by altering connectivity, travel times, and the attractiveness of nearby locations. For a valuation study, these spatial shifts matter because they change not only where demand is strongest, but also how quickly existing benchmarks can become outdated.

### **1.1.3 The Problem: How is Price Decided in Cebu?**

Despite this growth, property pricing system in Metro Cebu is still assembled from several partial and often inconsistent reference points. In practice, three sources are used most often, and each has clear limitations.

First, BIR zonal values serve as administrative benchmarks for taxation, but they often lag behind actual market conditions. A 2023 appraisal review found that ony 60% of LGUs nationwide had updated their assessment schedules(Otsuka et al., 2023), which suggests that some zonal values in Cebu may no longer reflect current prices. Second, back appraisals are designed mainly to manage lending risk, so they may produce values that are more conservative than open-market prices. Third, listing prices and agent quotes often reflect asking positions rather than verified transaction values, and these are not standardized across platforms or sellers.

The result is a valuation gap between official benchmarks, estimates based on lenders, and prices that markets are seemingly willing to bear. For buyers and sellers, this makes pricing harder to interpret. For banks, it complicates collateral assessment. For local governments, it weakens the connection between tax benchmarks and market reality. Metro Cebu therfore has an active property market, but not yet a consistent and validated valuation system that are on property level.

This problem is not unique to the Philippines. In Kenya, 427 registered valuers identified limited information as the primary valuation problem (Cheloti & Mooya, 2021). In Lagos, 92.7% of valuers cited insufficient market evidence on top of the reported valuation errors that are far above the norm (Ajibola, 2010). All in all, these cases suggest that valuation problems in emerging markets are often rooted not so much in proffesional judgement itself but more so in the quality and availability of market data.

### **1.1.4 Why Metro Cebu, and Why Now?**

Three converging factors make it timely to build a data-driven valuation model for Metro Cebu:

1. **Prices are moving faster than the benchmarks can follow**: With 11.5% growth in 2025 and some zonal values outdated since 2019, the gap between official benchmarks and market reality is widening. Continued reliance on outdated models perpetuates mispricing.
2. **Infrastructure is redrawing the value map in real time**: Projects like the CBRT and the Expressway are restructuring barangay accessibility and desirability. Traditional appraisal methods, reliant on historical comparables, cannot price these spatial changes in real-time. A GIS-augmented model built on geocoded property data addresses this constraint.
3. **The data now exists to do this properly**: Online platforms (Lamudi, Dot Property), open geospatial data (OpenStreetMap), and geocoding tools (Google Maps API) enable the construction of a street-level dataset without requiring private deed-of-sale records. Furthermore, open-source GIS software allows us to transform this data into an interactive web map, providing prescriptive spatial decision support for practitioners.

### **1.1.5 Ideal Scenario**

The core problem is not that Cebu lacks valuation activity, it's that the activity lacks a common significant basis. A data-driven model that quantifies the contribution of specific value drivers, such as lot area, proximity to economic nodes, nearby amenities, and neighborhood trends, would provide reproducible estimates for residential properties. Delivered through an interactive QGIS map and a Streamlit web application, this model would help move Cebu from heuristic pricing toward a more transparent and evidence-based valuation process aligned with IVS 2025.

---

## **1.2 Statement of the Problem**

**Decision Problem**: How can real estate firms in Metro Cebu utilize data-driven models, augmented with geospatial feature engineering, to predict property values more accurately and consistently?

**Research Problem**: In Metro Cebu, reliance on outdated administrative benchmarks and manual appraisals produces inconsistent, subjective pricing. No existing study combines transaction-level data with GIS-derived geospatial features (proximity analysis, amenity scoring, spatial autocorrelation) for the Metro Cebu market, and none provides a prescriptive spatial visualization layer for decision support.

---

## **1.3 Research Questions**

1. What value drivers significantly influence property prices in Metro Cebu?
2. Which modeling technique—**Hedonic Regression**, **Random Forest**, or **XGBoost**—produces the most accurate valuation out of sample (lowest MAPE)?
3. Do **geospatial features**—proximity to economic nodes, amenity density, and spatial autocorrelation—significantly improve model performance compared to structural-only models?
4. How large is the "Valuation Gap" between the model's data-driven predictions and traditional BIR Zonal Values?

---

## **1.4 Significance of the Study**

Addressing this valuation gap benefits multiple stakeholders:

1. **Real Estate Brokers and Appraisers**: Provides standardized tools compliant with IVS 2025 transparency requirements, including SHAP-based explainability, an interactive QGIS map for spatial analysis, and a Streamlit interface for property-level valuation review.
2. **Property Investors**: Ensures fair, data-backed pricing and helps identify undervalued areas visually through geospatial heatmaps.
3. **Banks and Lending Institutions**: Improves collateral assessment accuracy through reproducible, auditable models, wich reduceds exposure to pricing errors that manual appraisals can miss.
4. **Local Government Units (LGUs)**: Facilitates the updating of zonal values using market-based evidence, mapping the geographic divergence between official and actual prices.

This study is significant within the Philippine context as the first Cebu-specific, data-driven valuation model integrating GIS-based feature engineering. While prior Philippine machine learning studies focus on Metro Manila or use aggregate indices, no work applies geocoded proximity analysis, OSM amenity scoring, and spatial autocorrelation to transaction-level data for Metro Cebu. By delivering results through an interactive QGIS map and a Streamlit web application, this study extends beyond predictive analytics into applied decision support, offering tools that are usable in a fragmented local market.

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

This study produces two applied deliverables: an interactive QGIS map for spatial analysis and a Streamlit web application for property-level prediction and explanation.

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

The review moves from valuation concepts and the Philippine setting to the practical constraints that shape valuation work in emerging markets. It then turns to modeling approaches, the use of geospatial features in property valuation, macroeconomic influences, and the compliance issues that matter if these models are to be used in practice. The chapter closes by identifying the specific gap that this study addresses in the Metro Cebu context.

---

## **2.2 Core Concepts and Philippine Context**

### **2.2.1 Valuation Foundations**

Market value is the most probable price under fair, open-market conditions on the valuation date. Market price is the amount actually paid in a specific transaction; the two can differ in practice (Philippine Valuation Standards [PVS], 2018). Hedonic Pricing Theory, introduced by Rosen (1974), provides the foundational framework for this study. It posits that the price of a differentiated good—such as a house—can be decomposed into a function of its constituent attributes: $P = f(\text{Structural}, \text{Locational}, \text{Environmental})$. This theory underpins the hedonic regression model used as our interpretive baseline.

### **2.2.2 Philippine Indices and Administrative Benchmarks**

The Bureau of Internal Revenue (BIR) issues zonal values primarily for tax purposes, such as capital gains tax (CGT) and documentary stamp tax (DST). These values are administratively set and are not live market prices (BIR, n.d.). Critically, the Tax Policy Study of 2023 (TPS 2023) found that only approximately 60% of Local Government Units (LGUs) have updated their assessment schedules, meaning zonal values in many areas—including parts of Cebu—are materially outdated.

For market-level context, the Bangko Sentral ng Pilipinas (BSP) publishes the Residential Real Estate Price Index (RREPI), which reported a 7.5% nationwide increase in housing prices in Q2 2025. Metro Cebu posted 11.5%—one of the highest growth rates outside the National Capital Region—reflecting sustained demand driven by IT-BPM, tourism, and infrastructure development (BSP, 2025).

### **2.2.3 Cebu's Economic Landscape**

Cebu's property market is expanding within one of the country's fastest-growing regional economies, which grew by 7.3% in 2024 (PSA Region 7, 2025). Demand has been reinforced by IT-BPM activity, tourism recovery, and infrastructure projects such as the Cebu Bus Rapid Transit (CBRT) and Metro Cebu Expressway. Yet valuation practice in Cebu still leans heavily on manual appraisal and zonal benchmarks, which do not always move as quickly as market conditions do. The result is a valuation gap in which official BIR zonal values can lag behind actual market prices, creating uncertainty for buyers, sellers, and lenders.

### **2.2.4 Cebu-Specific Empirical Work**

Agosto (2020) conducted the only Cebu-specific empirical study on land value determinants, surveying 51 real estate practitioners. The study identified transport accessibility as the primary driver of land values, followed by neighborhood quality and environmental conditions. However, the study was survey-based and did not utilize transaction-level data or machine learning methods. That leaves a gap between what Cebu practitioners identify as important and what has actually been tested using property-level data and predictive models.

---

## **2.3 The Core Problem: Data Scarcity in Emerging Markets**

International literature consistently identifies data scarcity—not valuer misconduct—as the primary obstacle to accurate property valuation in developing countries.

- **Kenya**: Cheloti and Mooya (2021) conducted a census survey of 427 registered valuers in Nairobi. "Limited information" was ranked as the primary valuation problem (Mean Rank 2.91), while valuer misconduct ranked last (2.32). They concluded that limited and unreliable information, rather than incompetence, causes valuation problems.
- **Nigeria (Lagos)**: Ajibola (2010) surveyed 300 valuers and found that 92.7% cited insufficient market evidence as the primary challenge. Valuation inaccuracy ranged from +24.8% to +51.5%, far exceeding the global norm of ±10%.
- **Sub-Saharan Africa**: Becsky-Nagy and Sachicola (2025) conducted a systematic review across 46 countries, finding a strong negative correlation between urbanization and credit access (r = −0.935). This suggested that financial infrastructure failed to keep pace with rapid urban growth—a pattern relevant to Metro Cebu's expansion.

Taken together, these studies suggest that valuation error in emerging markets is often rooted less in professional failure than in thin, inconsistent, or inaccessible market data. That framing matters for this study because it shifts attention from individual appraisal practice to the quality, structure, and availability of the information on which valuation depends.

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

Given a sample size close to ours, the Tanzania study is useful less as a fixed benchmark than as a caution about model choice under limited data conditions. In that setting, tree-based models performed more reliably than deep learning architectures, which were more prone to overfitting. For a dataset of roughly 1,000 observations, the evidence points toward Random Forest and XGBoost as more defensible starting points than neural networks.

### **2.4.4 Southeast Asian Applications**

Work from Southeast Asia points in a similar direction. In Indonesia, Wibowo et al. (2023) found that adding macroeconomic and spatial variables, including coordinates and amenity proximity, improved residential price prediction in Surabaya. In Malaysia, Samsudin et al. (2022) showed that Random Forest combined with GIS-based inputs improved valuation performance for heritage properties in Penang relative to more conventional econometric approaches. While these studies come from different property contexts, they suggest that in fast-changing urban markets, spatial information is not just supplementary detail but part of the valuation signal itself.

### **2.4.5 Comparative Reviews**

Review studies suggest that this is not an isolated pattern. Wang and Li (2020) found that although deep learning performs well when image data is available, tree-based ensembles such as Random Forest and XGBoost remain highly competitive for structured tabular datasets. Moreno-Foronda et al. (2025) and Sharma et al. (2024) likewise report strong performance from XGBoost in house price prediction tasks. Hu et al. (2024), meanwhile, show that SHAP-based explainability can narrow the interpretability gap between less transparent ML models and more conventional hedonic approaches.

---

## **2.5 Geospatial Feature Engineering in Property Valuation**

For residential property, location is not a secondary attribute. It shapes accessibility, neighborhood quality, exposure to surrounding land uses, and connection to the wider urban system. Tobler's First Law of Geography, that near things tend to be more related than distant ones (Tobler, 1970), provides a clear basis for treating spatial relationships as part of the valuation problem rather than as background context.

### **2.5.1 Geocoding and Location Precision**

Geocoding matters in this study because the dataset begins with imperfect addresses rather than parcel-level coordinates. Converting those addresses into latitude and longitude makes the later proximity, amenity, and neighborhood calculations possible. Services such as the Google Maps Geocoding API are widely used for this purpose because they can handle incomplete or inconsistently formatted addresses while still producing coordinates precise enough for urban spatial analysis (Google Developers, 2025).

For open-source alternatives, **OpenStreetMap (OSM)** via the Nominatim geocoder provides community-maintained geospatial data at no cost. While OSM coverage varies by region, urban areas in the Philippines—particularly Metro Cebu—have beneficiary coverage from the local OpenStreetMap community and humanitarian mapping initiatives (Humanitarian OpenStreetMap Team, 2024). This study employs Google Maps API as the primary geocoding engine for address-to-coordinate conversion, supplemented by OSM for amenity and land-use data retrieval.

### **2.5.2 Proximity Analysis and Accessibility**

Distance-based features—proximity to commercial centers, transportation hubs, schools, and employment nodes—are robust value drivers in hedonic pricing literature (Rosen, 1974; Malpezzi, 2003). Computations utilizing the Haversine formula are the standard for estimating geographic distances in urban property studies (Sinnott, 1984).

Agosto (2020) confirmed that transport accessibility is the primary driver of land values in Cebu, followed by neighborhood quality. For Metro Cebu, proximity to key economic nodes—Cebu IT Park, Ayala Center Cebu, SM Seaside City, Mactan-Cebu International Airport—and planned infrastructure like the Cebu Bus Rapid Transit (CBRT) stations provide critical, measurable value signals.

### **2.5.3 Amenity Scoring via OpenStreetMap**

Beyond direct point-to-point distances, the density and diversity of amenities within a defined radius present a richer characterization of neighborhood quality. OSM's tagging system allows researchers to query counts of schools, hospitals, commercial establishments, restaurants, and public transport stops within a specified radius of a property. This "amenity score" effectively captures walkability and local service accessibility (Boeing, 2017, 2019).

The Python library `osmnx` provides programmatic access to OSM data for network analysis and amenity retrieval. Studies validating OSM-derived features in property valuation include Fonte et al. (2017), who demonstrated that volunteered geographic information (VGI) from OSM serves as a reliable proxy for land-use classification in Europe, and Yao et al. (2018), who used Point of Interest (POI) density to substantially improve housing price predictions in China.

In the Philippine setting, the use of OpenStreetMap cannot simply be assumed. Alvarez et al. (2021), through Project OHANA, provide more locally relevant support for its use by showing that OSM data can sustain nationwide amenity accessibility analysis in the country. Their work does not eliminate data quality concerns, but it does suggest that OSM is sufficiently robust to support spatial analysis of the kind required in this study.

### **2.5.4 Spatial Autocorrelation and Neighbor Price Effects**

A critical consideration in property valuation is **spatial autocorrelation**: properties located near each other tend to have similar prices, violating the independence assumption of standard regression (Anselin, 1988). This phenomenon is well-documented: housing prices exhibit positive spatial dependence because neighboring properties share the same schools, transportation access, environmental quality, and market conditions.

Two approaches address spatial effects in modeling:

1. **Spatial Lag Model (SLM)**: Includes a spatially weighted average of neighboring property prices as an independent variable, directly capturing the effect of nearby market conditions on a property's value.
2. **Moran's I Statistic**: A diagnostic measure of global spatial autocorrelation (Moran, 1950). A statistically significant positive Moran's I in the residuals of a non-spatial model indicates that spatial effects are present and should be incorporated.

For our study, we incorporate a **spatial lag variable**—the mean price of properties within a defined radius—as a feature in the ML models. This operationalizes Tobler's law within the predictive framework without imposing the parametric constraints of formal spatial econometric models.

### **2.5.5 Implications for Metro Cebu**

This matters in Metro Cebu because value shifts are unlikely to be evenly distributed across the urban area. Infrastructure projects such as the CBRT and Metro Cebu Expressway, uneven amenity access, and strong variation across neighborhoods all create spatial differences that a purely structural model would miss. In that sense, geospatial feature engineering is not an optional enhancement but a way of making the valuation model more responsive to how the city is actually changing.

---

## **2.6 Integrating Value Drivers: Indexing vs. Raw Features**

A critical challenge in geospatial ML models is how to operationalize distance metrics. Agosto (2020) identified transport accessibility and neighborhood quality as the primary value drivers in Cebu based on practitioner surveys. To integrate these findings into a machine learning pipeline, raw geospatial distances (e.g., Euclidean distance to the nearest hospital, school, or mall) are often insufficient on their own, as they can suffer from multicollinearity—a scenario where multiple distance variables are highly correlated with one another, complicating the model's feature importance weights.

Recent work suggests that raw distance variables are often too fragmented to stand on their own. Rey-Blanco, Zofío, and González-Arias (2024), for example, show that accessibility indices built from point-of-interest data can improve housing price prediction in both hedonic regression and Random Forest models. Grouping individual distances and counts into broader measures such as transit accessibility or commercial density can preserve the locational signal while reducing overlap across variables. For this study, that approach provides a practical way to translate Agosto's (2020) qualitative value drivers into features that can be used consistently in the model.

---

## **2.7 Macroeconomic Determinants**

While structural and locational attributes shape the price of an individual property, broader macroeconomic conditions influence the direction of the market as a whole. Nworah, Egbenta, and Ogbuefi (2023), in their study of real estate investment performance in Lagos from 2005 to 2022, found that exchange rate movements and inflation were both significantly associated with real estate outcomes.

- **Exchange Rate vs. Real Estate**: r = **−0.925** (the strongest predictor).
- **Inflation vs. Real Estate**: r = **−0.508** (significant but weaker).

In the Philippine case, that relationship is plausibly tied to remittance flows as well. In 2024, OFW remittances reached USD 38.3 billion nationally, and when the peso weakens, remitted income converts into more pesos. For households in Cebu, that can strengthen purchasing power and feed housing demand, which helps make sense of the 11.5% property price growth reported for Metro Cebu. The point is not that exchange rates alone explain local price movement, but that broader macro conditions can shape the direction and intensity of demand.

To control for these time-trend effects, we include the **BSP RPPI quarterly index** as a macro control variable in our models, following Udomsap and Abid (2020), who confirmed that interest rates and macroeconomic conditions are significant determinants of housing prices.

---

## **2.8 Compliance and Explainability: IVS 2025**

The International Valuation Standards (2025), effective January 31, 2025, introduced two critical new chapters relevant to data-driven valuation:

- **IVS 104 (Data and Inputs)**: Mandates that data used in valuations must be Accurate, Complete, Timely, and Transparent. Sources must be traceable from their origin ("provenance requirement").
- **IVS 105 (Valuation Models)**: Explicitly states that *"No model without the valuer applying professional judgement can produce an IVS-compliant valuation."* Automated Valuation Models (AVMs) must be tested, transparent, and paired with professional review.

For this study, the IVS revisions matter in two practical ways.

1. **SHAP Values for Transparency**: We employ SHAP (SHapley Additive exPlanations) to provide both global feature importance ("Which value drivers affect Metro Cebu prices most?") and local explanations ("This Lahug condo is +₱1.2M due to IT Park proximity, −₱300K due to small floor area"). This satisfies IVS 104's transparency requirement.
2. **Human-in-the-Loop Validation**: We engage licensed real estate brokers from the CPRE network to review model outputs, satisfying IVS 105's professional judgement mandate. This makes our model a *decision-support tool*, not a replacement for the appraiser.

---

## **2.8 Synthesis and Research Gap**

Taken together, the literature points to four recurring themes. First, valuation work in emerging markets is persistently constrained by data scarcity and uneven market information. Second, for small to mid-sized tabular datasets, tree-based machine learning models tend to perform more reliably than deep learning approaches. Third, spatial features such as proximity, amenity access, and neighborhood effects add information that conventional structural variables alone do not capture. Fourth, any model intended for valuation practice still has to remain transparent enough to support professional review under IVS 2025.

What remains missing is a Cebu-specific study that brings those strands together using property-level data. Prior Philippine ML studies focus on Metro Manila (Perdio et al., 2023; Dann et al., 2020), Central Pangasinan (Viray, 2023), or broader indicator-based approaches rather than property-level modeling (Ramolete et al., 2023). The only Cebu-specific study identified here, Agosto (2020), is valuable in showing what practitioners regard as important, but it is survey-based and does not test those factors using observed property data.

This thesis addresses that gap by developing a Metro Cebu valuation model that combines hybrid multi-source data, tree-based machine learning, geospatial feature engineering, SHAP-based explainability, and professional review. The aim is not to replace appraisal judgement, but to produce a more transparent and spatially grounded decision-support tool for the local market.

---

## **2.9 Bridge to Methodology**

Chapter 3 builds on this review by showing how those ideas are translated into data sources, engineered features, model comparisons, and evaluation procedures for Metro Cebu. In other words, the next chapter moves from what the literature suggests to how those insights are operationalized in this study.

---

# **Chapter 3 | Research Methodology**

## **3.1 Research Design**

This study uses a quantitative, non-experimental design to model residential property values in Metro Cebu. The analysis is predictive in that it estimates prices from observed property characteristics, and prescriptive in that the results are later organized for spatial decision support through GIS. The dependent variable is property price, or where appropriate price per square meter, while the independent variables include structural, geospatial, administrative, and macroeconomic features.

Three supervised learning approaches are compared in order to balance interpretability and predictive performance, while also testing whether GIS-derived and administrative variables improve the model beyond structural features alone:

1. **Ordinary Least Squares (OLS) / Hedonic Regression**: An interpretable baseline grounded in Hedonic Pricing Theory (Rosen, 1974). Coefficients carry direct economic meaning (e.g., "each additional bedroom adds ₱X to value").
2. **Random Forest Regressor**: A tree-based ensemble that captures non-linear relationships and feature interactions without requiring explicit specification (Breiman, 2001).
3. **XGBoost Regressor**: A gradient boosting algorithm optimized for predictive accuracy on structured tabular data (Chen & Guestrin, 2016). Empirically, XGBoost often performs well on datasets of similar scale (Nyanda et al., 2024).

---

## **3.2 Data Sources: The Hybrid Strategy**

Because direct deed-of-sale transaction records are not publicly accessible, the dataset is assembled from multiple sources that reflect different segments of the residential market. Foreclosure and acquired-asset listings provide a more conservative segment of observed prices, while online listings provide asking prices that reflect current market exposure more closely. The purpose of this hybrid strategy is not to claim direct observation of a single true market price, but to work with the most usable price signals available under existing data constraints.

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

These distressed assets are treated as a lower-bound segment of the observed market rather than as direct equivalents of open-market transaction prices. Using multiple institutional sources helps reduce the bias that might result if the dataset were drawn from only one lender or seller.

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

To represent current asking prices in the residential market, the study also collects listings from public online platforms, primarily Lamudi. As Sousa et al. (2024) note, large listing datasets can capture pricing patterns that are often missing from sparse official records. For this reason, the study targets at least 500 Metro Cebu residential listings.

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

Within this hybrid dataset, foreclosure prices and online listing prices are not treated as identical market signals. A source indicator is therefore included so the model can account for systematic level differences between distressed and market-facing listings. This allows the analysis to estimate price relationships across both segments without assuming that they represent the same selling condition.

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

Licensed real estate brokers from the CPRE network are included as a validation layer, not to replace statistical evaluation, but to check whether the model outputs remain plausible within local market practice. Their role is limited to two tasks:

1. **Sanity Check**: Reviewing SHAP-derived value driver rankings against practitioner knowledge.
2. **Outlier Review**: Examining cases with high prediction error to distinguish likely data issues from genuine market anomalies.

---

## **3.3 Data Pipeline**

The data preparation process proceeds in five stages.

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

Geospatial feature construction is the part of the method that most directly connects the valuation model to the urban structure of Metro Cebu. Rather than treating location as a background descriptor, this stage translates accessibility, amenity access, and neighborhood context into variables that can enter the model explicitly.

1. **Geocoding (Google Maps API)**: Each property address will be geocoded to obtain precise latitude/longitude coordinates. The Google Maps Geocoding API has been chosen for its superior handling of Philippine address formats, which often include barangay names, landmarks, or informal location descriptors.
2. **Proximity Features (Haversine Formula)**: For each geocoded property, the Haversine formula will compute great-circle distances to key economic and infrastructure nodes:

- Ayala Center Cebu (primary CBD)
  - Cebu IT Park (employment hub)
  - SM Seaside City (commercial center)
  - Mactan-Cebu International Airport
  - Planned Cebu Bus Rapid Transit (CBRT) station locations

3. **Custom Value Driver Scoring Model (OSM via osmnx)**:
   Rather than relying only on separate distance measures, the study also constructs an amenity score from OpenStreetMap data. Using the osmnx library, points of interest within a 1 kilometer network radius of each property will be queried and grouped into categories relevant to residential valuation. A 1 km radius is used because it roughly corresponds to a 10 to 15 minute walkable catchment in urban settings. The resulting score is designed to reflect neighborhood service access rather than simple amenity counts alone.

   - Educational institutions (schools, universities): Standard weight
   - Healthcare facilities (hospitals, clinics): High weight
   - Commercial establishments (malls, markets): Medium weight
   - Public transport stops (jeepney routes, bus stops): High weight

   *Note: Initial weights will be drawn from the literature and then checked during exploratory analysis so that no single amenity category dominates the index without empirical basis.*

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

In this form, the hedonic model retains its interpretive structure while allowing administrative and spatial variables to enter directly into the price equation. This makes it possible to compare a more conventional valuation framework with the tree-based models without stripping out the locational features that are central to the study.

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

SHAP is used here to interpret model outputs at both the dataset and property level, which is important if the results are to remain reviewable in valuation practice and consistent with IVS 2025 transparency requirements.

- **Global SHAP (Summary Plots)**: Will identify which value drivers affect Metro Cebu property prices most across the entire dataset. This will answer RQ1 ("What value drivers significantly influence property prices in Metro Cebu?").
- **Local SHAP (Force Plots)**: Will explain individual predictions. For example: *"This Lahug condo is valued at ₱X: +₱1.2M due to IT Park proximity, −₱300K due to small floor area, +₱200K due to high amenity score."*

This helps keep the model interpretable enough to function as a support tool rather than a purely opaque prediction system. In practical terms, the model is evaluated not only by how accurately it predicts price, but also by whether its outputs can still be examined and discussed in terms that practitioners can understand.

---

## **3.8 Deliverables**

### **3.8.1 QGIS Interactive Map**

The main applied output of the study is an interactive QGIS project that organizes model results spatially. Rather than presenting the results only as tables or summary statistics, the map is intended to show how predicted values, valuation gaps, and locational patterns are distributed across Metro Cebu.

1. **Property Valuations**: Point vectors representing individual geocoded properties. They will be color-coded based on the model's prediction error (actual vs. predicted), allowing users to visually identify undervalued anomalies or overvalued clusters.
2. **Valuation Gap Heatmap**: A raster heatmap visualizing the divergence between the ML model predictions and the official BIR Zonal Values. Hotspots will indicate areas where official valuations significantly lag market realities.
3. **CBRT & Infrastructure Overlays**: Line segments denoting the planned CBRT route with 500m and 1km buffer zones. This will allow users to visualize how upcoming public transit infrastructure intersects with current market valuations.
4. **Value Driver Contours**: ISO-chrones or distance contours measuring proximity to the CBD (Ayala Center) or IT Park.

The purpose of this output is to make the model easier to inspect geographically, especially for brokers, investors, and local government users who need to compare values across locations rather than only at the level of individual records.

### **3.8.2 Streamlit Web Application**

A Streamlit web application will complement the QGIS map by providing an interactive interface for testing individual property inputs against the trained model. Users will be able to enter structural property features, select a location, and receive a predicted price together with a SHAP-based explanation of the factors contributing to that estimate. While the QGIS output emphasizes spatial comparison across Metro Cebu, the Streamlit application provides a more direct way to inspect individual predictions and their underlying value drivers.

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
