# **Chapter 1 | The Problem and Its Setting**

## **1.1 Background of the Study**

The Residential Real Estate Price Index (RREPI, hereafter referred to as RPPI) released by the Bangko Sentral ng Pilipinas (BSP) also reported a 7.5% increase in housing prices nationwide in Q2 2025, led by double-digit growth in areas outside Metro Manila, including the Visayas (Bangko Sentral ng Pilipinas, 2025). This consistent upward movement in property values reflects both strong domestic consumption and the sustained demand for housing and investment properties.

### **1.1.1 Subsystem: Cebu’s Economic Landscape**

Within this national context, Cebu stands out as one of the Philippines’ fastest-growing regional economies, expanding by 7.3% in 2024 (Philippine Statistics Authority Region 7, 2025). Services and industry—particularly real estate, IT-BPM, and tourism—serve as key growth drivers. Cebu’s real estate sector thrives due to infrastructure expansion projects like the Cebu Bus Rapid Transit (CBRT) and Metro Cebu Expressway, both of which are expected to elevate accessibility and land values along their routes (Cebu Daily News, 2025; Department of Public Works and Highways, 2025). Meanwhile, the province’s tourism and connectivity are bolstered by the Mactan-Cebu International Airport (MCIA), which served 11.32 million passengers in 2024, and continues to open new international routes (Philippine Star, 2025).

Cebu’s residential and commercial property markets have become more diverse, featuring sustainable mixed-use developments and vertical housing projects (Cebu Daily News, 2024). As a result, the city has emerged as a real estate hotspot outside Metro Manila, with Metro Cebu posting an 11.5% rise in property prices, one of the highest among areas outside NCR (Bangko Sentral ng Pilipinas, 2025).

### **1.1.2 Focal Stakeholder**

The Cebu real estate sector, represented by local firms such as **Cebu Premiere Real Estate (CPRE)**, operates in this dynamic yet competitive environment. CPRE serves as both a property developer and brokerage company, managing listings, pricing, and sales across Cebu. However, property pricing still largely depends on manual appraisals, comparable sales, and zonal values set by the Bureau of Internal Revenue (BIR). While such methods offer practical references, they lack the analytical precision of modern data-driven approaches (LandValuePH, 2025; Agosto, 2020). Research shows that Cebu land values are influenced by multiple factors including accessibility to transport, neighborhood quality, environmental conditions, and zoning regulations (Agosto, 2020; Agosto, 2017). The absence of integrated, multi‑source valuation tools makes pricing inconsistent and subjective.

### **1.1.3 Expectation (Ideal Scenario)**

Ideally, real estate pricing in Cebu should be data-based, transparent, and standardized. A data-driven valuation model that incorporates quantifiable features—such as location, lot size, accessibility, and nearby developments—would help achieve more accurate property assessments. This would benefit not only firms like CPRE but also buyers, investors, and banks that rely on fair market values for decision-making.

## **1.2 Statement of the Problem**

Given the current scenario, the decision problem is:
**How can real estate firms in Cebu, such as CPRE, utilize data-driven models to predict property values more accurately and consistently?**

From a research standpoint, the research problem lies in the limited application of predictive analytics and empirical modeling (both statistical and machine‑learning based) in local property valuation, leading to inconsistent and subjective pricing. Despite the existence of valuation standards and indices like the RPPI, many local firms still depend on manual methods without empirical models or accessible datasets.

## **1.3 Significance of the Study**

Addressing this gap is crucial, as a predictive valuation model could improve market transparency and operational efficiency in Cebu’s real estate industry. A data-based system benefits multiple stakeholders:

1.  **Real estate brokers and appraisers**, by providing standardized valuation tools.
2.  **Property buyers and investors**, by ensuring fair and data-backed pricing.
3.  **Banks and lending institutions**, through more accurate collateral assessments.
4.  **Local governments**, by gaining access to data that can help update zonal values and taxation benchmarks (Cebu Daily News, 2018; BSP, 2025).

Ultimately, this research contributes to bridging the gap between traditional property appraisal and data science, supporting Cebu’s shift toward evidence-based urban and economic planning.

## **1.4 Purpose Statement**

The purpose of this study is to develop a data-driven property valuation model for Cebu’s real estate market using multiple data sources. The study aims to identify the factors that significantly influence property values and apply both regression-based and machine-learning techniques to improve valuation accuracy. This aligns with the goal of enhancing fairness and consistency in real estate transactions in Cebu.

## **1.5 Research Questions**

1.  What measurable factors significantly influence property prices in Cebu City?
2.  How can predictive analytics and data modeling be applied to property valuation in Cebu?
3.  Which modeling techniques (e.g., hedonic regression and machine-learning methods) produce the most accurate valuation results?
4.  How does the proposed data-driven valuation model compare with traditional appraisal methods?
5.  How can the model support decision-making for developers, brokers, and policymakers?

## **1.6 Scope and Limitations**

[to be written]

# **Chapter 2 | Review of Related Literature**

## **2.1 Purpose**

This chapter reviews the existing literature on data‑driven property valuation in the Philippines, with Cebu as the focus. It explains the main ideas we use, the usual factors that affect value, and how tools like RPPI/REPI and BIR zonal values describe price movements.

We also connect these ideas to Cebu’s recent housing situation so the discussion is not too abstract. In the end, we point out a gap: there are still very few Cebu‑specific, multi‑source, property‑level models that are simple to run and repeat. Our study seeks to help fill this gap. The next sections start with basic concepts, then move to the Cebu context, and then to the models and results we build on.

## **2.2 Core concepts**

Market value is the most probable price under fair, open‑market conditions on the valuation date. Market price is the amount actually paid in a specific deal. These two can differ in practice (Philippine Valuation Standards \[PVS\], 2018). An appraisal is a written opinion of value for a specific property and date. It uses market‑based approaches such as the sales comparison, income, and cost approaches. Land valuation focuses on the land part only and sets aside the improvements (PVS, 2018). Highest and Best Use (HBU) is the use that is legally allowed, physically possible, financially feasible, and gives the highest value (International Valuation Standards \[IVS\], 2020).

The Bureau of Internal Revenue (BIR) issues zonal values mainly for tax bases, such as capital gains tax (CGT) and documentary stamp tax (DST). These values are not live market prices (BIR, n.d.). For market‑level context, the Bangko Sentral ng Pilipinas (BSP) publishes the Residential Real Estate Price Index (RREPI, often called RPPI), with sub‑indices including Metro Cebu. The Real Estate Price Index (REPI) is a proposed Philippine framework that aims to address gaps in zonal‑based valuation (BSP, 2025; National Statistical Coordination Board \[NSCB\], n.d.).

In this study we treat indices and official schedules as context, not as appraisals. RREPI/RPPI show how prices move over time. REPI seeks to measure prices using more transaction sources. Local Government Unit (LGU) assessments and BIR zonal values are mainly administrative benchmarks and not real‑time prices (BSP, 2025; Domingo & Fulleros, 2005; NSCB, n.d.; Eurostat, 2013; BIR, n.d.; PVS, 2018). These basic ideas provide the terms we use when we discuss Cebu and Philippine housing in the next section.

## **2.3 Cebu and PH context**

Residential prices continued to rise through Q2 2025, but the growth was slower than in late 2024\. House prices moved more steadily than condo prices. Cebu generally followed the pattern of Areas Outside the National Capital Region (AONCR), with stronger movements near major employment centers (BSP, 2025). Cebu’s demand reflects Information Technology–Business Process Management (IT‑BPM) jobs, tourism recovery, and remittances. Access projects like the Cebu Bus Rapid Transit (BRT) and expressway corridors also help support land values. At the same time, zoning rules and flood risk still influence how different areas behave (Cebu Daily News, 2024; Cushman & Wakefield, 2024). Furthermore, governance fragmentation across Metro Cebu’s distinct cities often leads to uneven infrastructure development, affecting spatial value distribution (Mercado et al., 2004).

Higher borrowing costs and higher inflation in 2024–2025 affected housing affordability and how developers timed their projects in both the National Capital Region (NCR) and AONCR. Listing data and market reports show wider price differences across barangays in Cebu (Philippine News Agency, 2025; Cushman & Wakefield, 2024). This broader view helps explain why some drivers matter more than others in Cebu. The next subsection moves from these overall trends to the main property‑level drivers that other studies have found.

## **2.4 Main drivers of value**

Given this setting, the literature points to several main drivers of land and property values. Price levels tend to be higher when access is better and travel time is shorter to Central Business Districts (CBDs), ports or the airport, and mass‑transit or major roads. This pattern appears along Cebu’s BRT and expressway corridors (Determinants of Land Values in Cebu City, 2020; Cebu Daily News, 2024). Neighborhood services and utilities, such as schools, hospitals, retail, and basic water and power, raise desirability. Noise and safety issues reduce it (Determinants of Land Values in Cebu City, 2020).

Site traits such as lot area, usable shape and frontage, corner exposure, slope or elevation, and flood or landslide risk affect both value and how easy it is to sell a lot (Determinants of Land Values in Cebu City, 2020; Top 10 Factors on Property Value in PH, n.d.). Where there are building improvements, floor area, build quality, age, layout, parking, and maintenance condition also matter in many studies (Malpezzi, 2003). Title clarity, right‑of‑way and easements, and zoning compliance help reduce uncertainty and discounts (PVS, 2018; IVS, 2020). Interest rates, inflation, and local supply and demand conditions change buyer budgets and price differences; studies confirm that interest rates and construction costs are significant negative drivers of housing prices (Udomsap & Abid, 2020). Recent RREPI/RPPI reports and news articles reflect these shifts (BSP, 2025; Philippine News Agency, 2025; Cushman & Wakefield, 2024).

These drivers later become the concrete variables that models use as predictors. The next subsection looks at how different studies, in the Philippines and abroad, actually build price models using these kinds of inputs.

## **2.5 Modeling lenses and related work**

Classical work on property valuation treats price as the result of many attributes. Hedonic regression models show how structural and locational features enter the price, usually in a linear or log‑linear form (Rosen, 1974; Malpezzi, 2003). Spatial econometrics adds terms for neighborhood effects when nearby prices move together. This is important in dense cities where locations influence each other (Anselin, 1988). For the Philippines, studies on Metro Manila use hedonic and spatial models and find that structural variables, environmental or service variables, and spatial spillovers all help explain variation in prices and rents (Dann et al., 2020).

More recent Philippine work starts to add machine learning. One study for Central Pangasinan combines BIR zonal values, the BSP price index, and a construction cost index, then compares multiple linear regression with Random Forest. The tree‑based model has lower error (Viray, 2023). Another paper tests the effect of adding government indicators to standard features and finds that these public indicators improve machine‑learning valuation accuracy (Ramolete et al., 2023). A preprint on Manila listings compares linear models with gradient boosting and reports that gradient boosting performs best after feature selection (Perdio et al., 2023).

International reviews and case studies show a similar pattern. Surveys of deep learning in real estate suggest that while neural networks excel with images, tree-based ensembles (Random Forest, XGBoost) remain highly competitive and efficient for structured tabular data (Wang & Li, 2020). Consequently, these models often perform better than hedonic regressions in terms of prediction error. Hedonic models remain easier to interpret and explain (Breiman, 2001; Friedman, 2001; Chen & Guestrin, 2016; Sharma et al., 2024; Weng, 2022; Utomo et al., 2024; Moreno‑Foronda et al., 2025). However, recent advances in Explainable AI (XAI) using SHAP values help bridge this trust gap by visualizing feature contributions in "black box" models (Hu et al., 2024). Taken together, these studies give us a menu of features and methods. The next subsection sums up what they tend to agree on before we state the remaining gap.

## **2.6 What the literature agrees on**

Across sources, several points are consistently highlighted. Access to jobs and transport matters a lot. Areas near major roads or BRT nodes tend to have higher prices. Basic services and neighborhood amenities raise value. Flood and slope risk lower it. Clear title and zoning reduce discounts. Submarkets exist inside cities, so barangay or corridor effects still show up even after we control for other variables (Determinants of Land Values in Cebu City, 2020; PVS, 2018; BSP, 2025). These patterns are consistent across both hedonic and machine‑learning studies and prepare us to identify what is still missing.

## **2.7 The gap**

Taken together, these studies show that there is still no Cebu‑focused, multi‑source model that works at the property level and is easy to run. RREPI/RPPI give trends. REPI sketches a national framework. Prior Philippine studies using machine learning are either limited in coverage or focus on other cities. None of them deliver an open, repeatable tool for Cebu pricing (BSP, 2025; Domingo & Fulleros, 2005; Ramolete et al., 2023). Our thesis responds to this by designing and testing a practical valuation model for Cebu that follows these lessons but is grounded in local data.

## **2.8 Bridge to methods**

To sum up, the literature gives us the key concepts, Cebu context, main drivers, and a set of modeling approaches that work reasonably well. It also shows the gap in Cebu‑specific tools that can be used in practice. Next, Chapter 3 explains our data, how we build features (location, access, risk, title, structure, market context), and the models we will test using the ideas above.

# **Chapter 3 | Research Methodology**

## **3.1 Research Design**

This study employs a **quantitative research design** focused on predictive modeling. Specifically, we use a supervised learning approach to estimate residential property values in Cebu City. The "dependent variable" is the market price (or price per square meter), and the "independent variables" are the property structural features, location attributes, and macroeconomic indicators.

The study compares a baseline **Hedonic Price Model** (Multiple Linear Regression) against non-linear **Machine Learning approaches** (Random Forest and Gradient Boosting/XGBoost). This design allows us to quantifying the trade-off between interpretability (hedonic) and predictive accuracy (ML), while explicitly testing the value of government administrative data (BIR Zonal Values) as a feature.

## **3.2 Research Population and Data Sources**

The "population" for this study consists of residential properties (House & Lot, Condominium, Vacant Lot) in the **Metro Cebu** area, with a specific focus on Cebu City.

### **3.2.1 Primary Data: Foreclosed Properties**

The primary dataset is a snapshot of foreclosed property listings from **BDO Unibank**, dated November 18, 2025 (`BDO-Properties-as-of-11.18.25`).

- **Volume**: The raw file contains **955** property entries.
- **Coverage**: Includes properties across multiple regions, from which we will filter for **Cebu** (Region VII / Central Visayas).
- **Key Variables**:
  - **Location**: Region, City, Property Address (approximated for geocoding).
  - **Physical**: Lot Area (sqm), Floor Area (sqm), Property Type (e.g., "House and Lot", "Condominium").
  - **Financial**: Advertised Price (Php), which serves as our proxy for "Market Price" (specifically, distressed market value).
  - **Descriptive**: A text field (`Property Description`) containing details like bedrooms and bathrooms, which will be parsed.

### **3.2.2 Secondary Data: Online Listings**

To supplement the distressed asset data and represent "fair market value" listings, we will collect current property listings from public online platforms (e.g., Lamudi, Facebook Marketplace). Research indicates that online listings effectively capture market segmentation and pricing clusters even in the absence of official transaction records (Sousa et al., 2024). This dataset will help validate if foreclosed properties transact at a significant discount compared to the broader market. _(Note: This data collection is ongoing)._

### **3.2.3 Macroeconomic and Administrative Data**

- **BIR Zonal Values**: Official zonal values for the specific barangays in Cebu City, used to calculate the "valuation gap."
- **BSP Residential Property Price Index (RPPI)**: Quarterly index values for Areas Outside NCR (AONCR) to control for time-trend effects (inflation/market cycle).

## **3.3 Data Instrument**

The research does not use a survey questionnaire. Instead, the "instrument" is a **computational data pipeline** built using the Python programming language.

- **Data Processing**: `Pandas` for cleaning, merging, and variable transformation.
- **Geocoding**: Google Maps API or OpenStreetMap (Nominatim) to convert text addresses into Latitude/Longitude coordinates.
- **Modeling**: `Scikit-learn` for Linear Regression and Random Forest; `XGBoost` or `LightGBM` for gradient boosting models.
- **Deployment**: `Streamlit` to create the interactive valuation dashboard for the end-user (CPRE).

## **3.4 Data Gathering Procedures**

1.  **Ingestion**: The BDO Excel file is ingested into the Python environment.
2.  **Filtering**: The dataset is filtered to include only "Residential" properties located in "Cebu City" or key Metro Cebu cities (Mandaue, Lapu-Lapu, Talisay, Minglanilla, Consolacion).
3.  **Parsing**: The `Property Description` field is parsed using Regular Expressions (Regex) to extract structured features:
    - Number of Bedrooms (BR)
    - Number of Bathrooms (TB/T&B)
    - Parking/Garage availability
4.  **Geocoding**: Property addresses are batch-processed to obtain spatial coordinates (Lat/Lon) and specific Barangay names.
5.  **Augmentation**:
    - **Proximity Features**: Distances to key landmarks (Ayala Center Cebu, IT Park, SM Seaside, Mactan Airport) are calculated using the Haversine formula.
    - **Zonal Value Mapping**: Each property is matched to its corresponding BIR Zonal Value based on its Barangay and Street/Subdivision.

## **3.5 Data Treatment and Analysis**

The data analysis proceeds in three stages:

### **3.5.1 Pre-processing**

- **Outlier Detection**: Properties with extreme prices (e.g., top 1%) or unrealistic dimensions (e.g., Lot Area < 20 sqm) are flagged or removed.
- **Imputation**: Missing values for `Floor Area` (if minor) may be imputed using median values per Property Type.
- **Feature Engineering**: Creation of new variables such as `Price per Square Meter` and `Valuation Gap` (Advertised Price - Zonal Value).

### **3.5.2 Modeling Strategy**

We train three distinct model architectures to estimate price:

1.  **Multiple Linear Regression (Hedonic)**: Interpretable baseline.
    $$ \ln(Price) = \alpha + \beta*1 \ln(Area) + \beta_2 (Bedrooms) + \beta_3 (Distance*{CBD}) + \epsilon $$
2.  **Random Forest Regressor**: Captures non-linearities (e.g., price plateaus) and interactions (e.g., location value depending on lot size).
3.  **XGBoost Regressor**: High-performance gradient boosting to minimize prediction error.

### **3.5.3 Validation and Metrics**

To ensure the model generalizes well to unseen data:

- **Validation Scheme**: We use a **Time-Aware Train-Test Split** (training on older listings, testing on newer ones) or standard **K-Fold Cross Validation**.
- **Performance Metrics**:
  - **MAE (Mean Absolute Error)**: Average error in Pesos (interpretable for business).
  - **MAPE (Mean Absolute Percentage Error)**: Average % error (e.g., "off by 10%").
  - **RMSE (Root Mean Square Error)**: Penalizes large errors.
  - **R-squared ($R^2$)**: Percentage of price variation explained by the model.

Finally, we assess the **Feature Importance** scores from the Tree-based models to confirm which factors (e.g., Location vs. Floor Area vs. Zonal Value) are the strongest drivers of property value in Cebu.
