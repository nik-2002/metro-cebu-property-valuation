# Thesis Proposal — Pitch Script / Speaker Notes

> **24 Slides | Data Science Focus | February 21, 2026**

---

### Slide 1 — Title Slide
**Core Narrative**
> "Good morning to the panel. I am Chris Dominic Estreba from the MS Data Science program. Today I am presenting my thesis proposal titled: Data-Driven Property Valuation Model for Metro Cebu. My objective is to address a fragmented real estate market not through economic theory alone, but through applied machine learning, NLP, and rigorous data engineering."

**Defense / Q&A Notes**
*   **If asked "Why this topic?":** Real estate pricing is currently an *opinion*, not an objective fact. Zonal values are outdated, and appraisers lack data. Data science thrives where data is messy but valuable.
*   **Adviser:** Randy Marasigan
*   **Focus:** Maintain a strict Data Science persona. Pivot economic questions back to data availability, feature engineering, and model accuracy.

---

### Slide 2 — Background: The Cebu Real Estate Landscape
**Core Narrative**
> "To understand the business problem, we look at Cebu. Our regional property prices just grew by 11.5%, significantly outpacing the capital. This real estate boom is heavily fueled by the $38.3 billion in OFW remittances crashing into our local economy. The stakeholders here—banks, LGUs, and brokers—are operating in a high-velocity, high-stakes environment."

**Defense / Q&A Notes**
*   **Growth Stat Defense:** 11.5% is the Q3 2024 YoY growth for Areas Outside NCR (AONCR), per the official BSP Residential Real Estate Price Index (RREPI).
*   **Remittance Stat Defense:** $38.3B total for 2024. Why does this matter? Local wages don't support these property prices; foreign capital does. This makes the market volatile and highly speculative.
*   **Stakeholder Pain Points:**
    *   *Banks*: Overvaluing collateral leads to Non-Performing Loans (NPLs) if bubble pops.
    *   *LGUs*: Leaving billions of pesos in Real Property Tax (RPT) uncollected because Zonal Values are stuck in the 1990s/2000s.

---

### Slide 3 — Statement of the Problem: Expectation vs. Reality
**Core Narrative**
> "The expectation is that an economy moving this fast requires highly accurate, continuously updated valuation tools to prevent systemic financial risk. The reality is completely different. The business problem is that pricing is highly subjective; only 37% of local governments even update their Zonal Values. The underlying data problem is even worse: true Deed of Sale transaction data is strictly private. What data we do have is messy, unstructured web listings that lack spatial context and sit in disconnected silos."

**Defense / Q&A Notes**
*   **The 37% Stat:** Sourced from the TPS 2023 study by Ramolete et al. It proves government failure to track the market.
*   **The Privacy Problem (Crucial Defense):** If the panel asks *why not use actual sales data?* Answer mathematically: "Actual Deed of Sale data is protected by the Data Privacy Act (RA 10173) and banking secrecy laws. There is no open, digital MLS (Multiple Listing Service) in the Philippines like there is in the US (Zillow). Ergo, web scraping and foreclosure aggregation is the *only* mathematically viable proxy."

---

### Slide 4 — Research Objectives
**Core Narrative**
> "My research objectives are designed to bridge this gap. Primarily, I am utilizing machine learning on a hybrid dataset to accurately predict residential prices in Metro Cebu. My secondary objectives test the mechanics of that model: identifying exact driving features, quantifying the accuracy gained by integrating NLP text features, and calculating the mathematical gap between market reality and outdated BIR schedules."

**Defense / Q&A Notes**
*   **Primary Objective Scope:** We are predicting the *listing/asking* proxy price and the *distressed* foreclosure price to bracket the true market value.
*   **Secondary 2 (NLP):** This is the core Data Science novelty. We aren't just counting bedrooms; we are converting human sentiment in text into math.
*   **Secondary 3 (Val Gap):** Formula: `[(ML Predicted Value - BIR Zonal) / BIR Zonal] * 100`. This will be visualized territorially via a geospatial heatmap.

---

### Slide 5 — Significance of the Study
**Core Narrative**
> "The significance of this model scales to all stakeholders. For local government, it provides a transparent, data-driven baseline which can be used to legally update Real Property Tax schedules. For banks, risk exposure drops when they can computationally identify over-speculation. And for the buying public, it anchors negotiations to an objective, algorithmic baseline."

**Defense / Q&A Notes**
*   **LGU Legal Mandate:** Republic Act 7160 (Local Government Code) *legally requires* LGUs to conduct general revisions of property assessments every 3 years. They fail to do this because it's too expensive/slow manually. This model automates it.
*   **Bank Application:** Banks can run our model on a developer's pre-selling price. If the model says the unit is worth P3M but the developer wants P5M, the bank flags it as high-risk speculation.

---

### Slide 6 — Scope and Delimitations
**Core Narrative**
> "For our scope, this model is strictly delimited to residential properties—specifically Condos, Houses, and Townhouses across Metro Cebu. We are explicitly excluding commercial and industrial real estate, as those assets are valued primarily on an 'Income Approach' which requires cash flow data that is outside the parameters of our model."

**Defense / Q&A Notes**
*   **Why exclude Commercial?** Commercial real estate is valued based on its Return on Investment (ROI) and cap rates (Discounted Cash Flow / Income Approach). We do not have access to corporate P&L statements. Residential is valued primarily on the Sales Comparison Approach (Hedonic pricing), which perfectly matches machine learning.
*   **Metro Cebu Definition:** We are scraping Cebu City, Mandaue, Lapu-Lapu, Talisay, Consolacion, and Minglanilla.

---

### Slide 7 — The Global Data Scarcity Problem
**Core Narrative**
> "Moving to the literature, we root our methodology in global precedents. Studies spanning from Kenya to Lagos proved that massive valuation errors—sometimes exceeding 51%—are fundamentally driven by 'limited information', not incompetent appraisers. Bad value predictions are a data-scarcity problem, and data scarcity is exactly what Data Science is designed to solve."

**Defense / Q&A Notes**
*   **Kenya (Cheloti & Mooya, 2021)**: Survey of appraisers. "Limited info" was the #1 ranked problem overall (Mean Rank 2.91). Valuer misconduct/incompetence ranked dead last.
*   **Lagos (Ajibola)**: 92.7% cite bad data; typical error was huge (+24% to +51%).
*   **Argument:** Human appraisers fail because they operate blind. Algorithms fail if fed bad data. The foundational literature proves the bottleneck is data ingestion, not mathematical complexity.

---

### Slide 8 — Setting the Baseline: Agosto (2020)
**Core Narrative**
> "Locally, we lean on Agosto's 2020 study, which is the only major study on land values specific to Cebu. He correctly identified transport accessibility and amenities as the top drivers of value. However, his limitation was that his findings were based purely on a Likert survey of 51 practitioners. We are advancing his foundational work by replacing opinions with actual predictive models trained on real transaction data."

**Defense / Q&A Notes**
*   **Agosto's Math:** He used Principal Component Analysis (PCA) on 31 variables to extract 11 core factors.
*   **The Flaw (Our Opportunity):** His data source was *human opinion* (surveys). Brokers might *say* transport matters most, but their actual pricing logic might differ. We answer his research question using hard empirical ML instead of opinion surveys.

---

### Slide 9 — Model Selection Rationale (Tanzania Evidence)
**Core Narrative**
> "When selecting our algorithms, we looked to a 2024 study in Tanzania that operated on a dataset of exactly 954 properties—very close to our own sample size. Their data proved too sparse for Deep Learning, causing Neural Networks to catastrophically fail with a 108% error. In contrast, XGBoost succeeded beautifully with a 48% error. This literature strictly informs our decision to avoid deep learning and build our methodology around tree-based models."

**Defense / Q&A Notes**
*   **Nyanda et al. (2024):** If the panel pushes you on Neural Networks, completely shut it down with this paper. NN models generated *negative* R² values and 108.6% MAPE on n=954.
*   **Why Tree Models?** Random Forest and XGBoost are specifically engineered to handle the 'curse of dimensionality' in small tabular datasets. They slice data efficiently without needing millions of epochs to converge.

---

### Slide 10 — The NLP Rationale (Ottawa & Shanghai Evidence)
**Core Narrative**
> "The next piece of literature dictates our feature engineering. Standard valuation models completely ignore the text paragraph written in a listing. However, because our data relies heavily on web scraping, extracting unstructured text is crucial to gaining an edge. An Ottawa study achieved an R-squared of 0.79 using Word2Vec embeddings on listing text. Reading recent papers proves text extraction drastically improves accuracy by 10 to 44%."

**Defense / Q&A Notes**
*   **Zhang et al. (2024, Ottawa):** Self-trained Word2Vec (on 10k listings) beat pre-trained BERT by 44%. Why? Because real estate uses weird local abbreviations ("T&B," "RFO," "near IT park") that globally trained models like BERT don't understand well.
*   **The NLP Pitch:** If an outlier condo is priced 20% higher than its neighbor, the standard structured data (beds, baths, sqm) might look identical. The *reason* it's 20% higher is hidden in the text: "Corner lot", "Newly Renovated." If we don't parse the text, the model treats it as an inexplicable error.

---

### Slide 11 — Macro Factors & Compliance
**Core Narrative**
> "Finally, we factor in macroeconomics and compliance. A Nigerian study proved that Exchange Rates are a significantly stronger predictor of property prices than domestic inflation—a vital insight given Cebu's OFW market. On the compliance side, the 2025 International Valuation Standards just updated their rules, explicitly banning pure algorithmic Automated Valuation Models unless they provide transparency and involve human oversight."

**Defense / Q&A Notes**
*   **Nworah et al. (2023):** Exchange rate correlation was massive (r = -0.925). Why? When the Peso weakens against the Dollar, OFW purchasing power skyrockets, instantly driving up demand and developer asking prices.
*   **IVS 2025 Standard:** Section 105, Para 60: "No model without professional judgement... can produce IVS-compliant valuation."
*   **Our Shield:** This is why we must use SHAP (explainability) and frame the model as a "Decision Support Tool" for brokers, not an autonomous agent.

---

### Slide 12 — Research Design
**Core Narrative**
> "This brings us to our Methodology. The research design is quantitative predictive modeling. From a machine learning perspective, this is a supervised regression task targeting either Price per square meter or the Log of the total price."

**Defense / Q&A Notes**
*   **If asked "Why Log of Price?":** Property prices are heavily right-skewed (a few P50M mansions distort the curve of P3M condos). `np.log1p()` normalizes the distribution, ensuring the model's loss function doesn't over-punish errors on ultra-luxury properties at the expense of regular housing.

---

### Slide 13 — Dataset Source and Description (The Hybrid Strategy)
**Core Narrative**
> "To bypass the strict data privacy of actual Deeds of Sale, I engineered a hybrid data strategy. We combine a 'Floor' of distressed, verified BDO bank foreclosures, with a 'Ceiling' of thousands of speculative, web-scraped listings from Lamudi. By testing our models between these two poles, we can mathematically bracket the true market value, controlled against the BIR Zonal baselines."

**Defense / Q&A Notes**
*   **BDO (Floor):** ~955 foreclosures. These prices are real, documented, and verified by bank appraisers. However, they sold at a heavy discount (distressed). Thus, it is the mathematical "floor."
*   **Lamudi/LifeNavi (Ceiling):** Web scraping yields high volume (~3k-5k rows), but the prices are pure speculation. Sellers list higher than they expect to receive. Thus, it is the mathematical "ceiling."
*   **Interpolation Strategy:** The actual market clearing price exists somewhere in the statistical gap between the Lamudi asking price (ceiling) and the BDO foreclosure matrix (floor).

---

### Slide 14 — The Data Pipeline
**Core Narrative**
> "Our data pipeline is a rigorous 5-step process. We ingest the raw Excel and scraped HTML. We filter for Metro Cebu residential stock. We parse the messy descriptions using Regex to extract exact structural counts like bedrooms and bathrooms. We geocode the raw addresses to return precise Latitude and Longitude. And finally, we augment the set with spatial distances and NLP vectors."

**Defense / Q&A Notes**
*   **Data Cleaning Reality:** Over 60% of the project time will be spent here.
*   **Parsing (Regex):** Brokers format listings terribly. E.g., "3BR, Two T&B". Regex pattern matching is the only way to programmatically extract integers `3` and `2` from that string across thousands of messy rows.
*   **Geocoding:** Using the Google Maps API or Nominatim API to convert text ("Lahug, Cebu City") into floats (`10.322, 123.899`).

---

### Slide 15 — Feature Categories
**Core Narrative**
> "Before modeling, our variables are structured into these categories. We have basic structural features from the parsers. We have locational coordinates. We use the Haversine formula to compute exact proximity distances to major landmarks. We extract the NLP text features. We count neighborhood amenities using OpenStreetMap arrays. And we peg the data against administrative Zonal values and Macro index timelines."

**Defense / Q&A Notes**
*   **Haversine Formula:** Don't just say "distance." Say "Haversine." It calculates the great-circle distance between two points on a sphere given their longitudes and latitudes. (Euclidean distance is mathematically wrong on a globe).
*   **Amenity Feature Creation:** We will query OpenStreetMap (OSM) to generate an integer count: "How many hospitals/schools/malls exist within a 1km Haversine radius of this specific coordinate?"

---

### Slide 16 — Feature Engineering: Geospatial & Spatial Data
**Core Narrative**
> "This slide highlights what I consider one of the most critical pillars of our methodology: turning raw addresses into precise mathematical features. A listing that says 'Lahug, Cebu City' is meaningless to an algorithm. We use the geopy library and the Nominatim API to geocode every listing into exact latitude and longitude coordinates, plus a structured Barangay classification. From those coordinates, we compute Haversine distance vectors—the great-circle distance on a spherical Earth—to four major economic anchors: Ayala Center, IT Park, SM Seaside, and Mactan Airport. These distances mathematically capture the 'accessibility premium' that Agosto identified in his 2020 study. We then query OpenStreetMap's Overpass API to generate an Amenity Score: how many schools, hospitals, and commercial points of interest exist within a 1km radius of each property. As an exploratory extension, we are investigating building footprint density data from the Humanitarian Data Exchange—covering approximately 11.6 million structures nationwide—to compute neighborhood urbanization proxies. Finally, we use QGIS as our geospatial visualization and validation platform—generating choropleth maps, spatial overlays, and the publication-quality Valuation Gap heatmap that anchors our final analysis."

**Defense / Q&A Notes**
*   **Haversine vs. Euclidean:** If the panel asks about distance calculation, emphasize: "Euclidean distance is mathematically wrong on a curved surface. The Haversine formula computes great-circle distance on a sphere, which is the correct distance metric for geographic coordinates. Formula: `d = 2r × arcsin(√(sin²(Δφ/2) + cos(φ₁)cos(φ₂)sin²(Δλ/2)))`."
*   **Why These 4 Anchors?** Ayala = primary CBD; IT Park = BPO employment hub driving condo demand; SM Seaside = southern commercial gravity; Mactan Airport = international connectivity (OFW relevance). Each represents a distinct economic pull.
*   **OSM Amenity Score:** We use Python's `osmnx` or direct Overpass API calls to count features tagged as `amenity=school`, `amenity=hospital`, `shop=*`, etc. within a 1km buffer.
*   **HDX Building Density:** 11.6 million buildings from OpenStreetMap exports. We can calculate buildings-per-sq-km as a proxy for urbanization intensity. This is exploratory—may be cut if it doesn't improve model performance.
*   **Why not just use Barangay as a categorical variable?** Because Barangay-level encoding treats all properties within a barangay as identical. Two condos 500m apart but on opposite sides of IT Park have vastly different proximity premiums. Continuous Haversine distances capture this granularity.
*   **QGIS Role:** Python handles the computation (geocoding, Haversine, amenity counts). QGIS handles visualization and spatial validation: importing Shapefiles/GeoJSON layers, overlaying property points on barangay boundaries, and producing the final choropleth maps for the Valuation Gap heatmap. Think of it as: Python = the math engine, QGIS = the cartographic layer.

---

### Slide 17 — Feature Engineering: NLP & Text Data
**Core Narrative**
> "I want to highlight the NLP feature extraction—this is the study's core innovation. We turn descriptive adjectives into quantitative arrays. As a baseline, we employ TF-IDF vectorization. Based on the volume of scraped text we ultimately secure, we have the architecture ready to scale up to pre-trained BERT embeddings or self-trained Word2Vec models to capture local real estate jargon."

**Defense / Q&A Notes**
*   **TF-IDF (Term Frequency-Inverse Document Frequency):** Our fallback. It mathematically identifies words that are frequent in one specific listing but rare across the whole dataset (e.g., "penthouse"), assigning it a high numerical weight.
*   **Why Word2Vec / BERT?** TF-IDF doesn't understand context. It treats "near mall" and "close to mall" as entirely different. BERT maps them to similar vectors in semantic space.

---

### Slide 18 — Data Treatment & Pre-Processing
**Core Narrative**
> "To achieve a model-ready state, the data undergoes strict pre-processing. Property prices are right-skewed and violate normality rules; we fix this via Log transformation. When imputing missing values—say, a missing floor area—we do not use a global average. We impute using the Barangay-level median to rigorously preserve the spatial integrity of the local neighborhood. And we execute outlier purges using the IQR method to drop scraping artifacts cleanly."

**Defense / Q&A Notes**
*   **Imputation Defense:** If the panel asks how you handle missing data (NaNs). Answer: "If a condo is missing its lot size, imputing the average lot size of the *entire dataset* is statistically fatal. A lot in rural Minglanilla is 500sqm; a lot in IT Park is 30sqm. We strictly use `groupby('Barangay').median()`."
*   **IQR (Interquartile Range) Method:** Formulas: `Q1 - 1.5*IQR` and `Q3 + 1.5*IQR`. Anything outside this is dropped. This prevents a broker accidentally typing "P5,000,000,000" from ruining our model training.

---

### Slide 19 — Core Models (Hedonic vs. Tree-Based)
**Core Narrative**
> "For the main modeling architecture, we benchmark three pipelines. First, Multiple Linear Regression serves as our classical 'Hedonic' economic baseline, but struggles to map complex spatial non-linearities. Second, Random Forest utilizes ensemble bagging to map those geospatial interactions cleanly and reduce variance. Finally, XGBoost applies gradient boosting sequentially to correct residual errors. Because XGBoost has a high risk of memorizing small datasets, optimization is critical. We use GridSearchCV wrapped in K-Fold Cross Validation. We measure success primarily through MAPE—Mean Absolute Percentage Error—with our goal strictly targeting under 25% error to compare against international benchmarks."

**Defense / Q&A Notes**
*   **The Model Progression:** The linear model (OLS) proves *why* ML is necessary. If OLS gets 50% MAPE and XGBoost gets 20% MAPE, it mathematically proves real estate is non-linear.
*   **Bagging vs Boosting:** Random Forest builds independent trees (Bagging). XGBoost builds tree #2 specifically targeting what tree #1 got wrong (Boosting).
*   **GridSearchCV:** We tune `max_depth` (e.g. 3-7) and `learning_rate` (e.g. 0.01-0.1).
*   **K-Fold CV:** Prevents lucky train/test splits by training on 4 folds, testing on 1, and repeating 5 times.
*   **Why MAPE over RMSE?** RMSE heavily penalizes large absolute errors. MAPE treats errors proportionally. A 10% error is a 10% error regardless of house price.
*   **Target Defense:** In the Ramolete TPS 2023 study, ML models achieved ~20-25% MAPE locally. If we hit 25%, the model is a massive academic success.

---

### Slide 20 — Ethical Considerations
**Core Narrative**
> "Ethically, this project is watertight. 100% of the data ingested is public listing information or anonymized agency aggregates; we process zero personally identifiable information. Furthermore, we are writing bias-awareness directly into the dashboard—ensuring the model does not systematically undervalue properties in lower-class barangays based on inherited historic data biases."

**Defense / Q&A Notes**
*   **Legal Defense:** Web scraping public prices is not illegal. We do not extract names, phone numbers, or exact unit numbers.
*   **Role of AI:** This is strictly a decision support tool for licensed appraisers—not a fully autonomous valuer.

---

### Slide 21 — Thank You For Listening / Q&A
**Core Narrative**
> "Thank you for listening. I open the floor to questions."

---
