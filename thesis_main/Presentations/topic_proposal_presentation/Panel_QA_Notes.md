# Thesis Proposal Panel Q&A — Key Takeaways

> **Date**: February 2026  
> **Thesis**: Data-Driven Property Valuation Model for Metro Cebu  
> **Source**: Transcribed Q&A session from the thesis proposal panel  
> **Post-Panel Decision**: Focus on GIS/geocoding; **remove NLP feature extraction**.

---

## 1. Define "Metro Cebu" Precisely

The panel asked for a **clear geographic definition** of Metro Cebu. Municipalities/cities mentioned: Carcar, San Fernando, Naga City, Minglanilla, Talisay, Cebu City, Lapu-Lapu, and Mandaue. Some of these are not yet officially cities.

**Action:** Provide a precise, citable geographic boundary definition with a reference map in the manuscript.

---

## 2. Clarify the Target Variable (What Price Are We Predicting?)

The panel asked whether the model predicts the **high (listing/ceiling), low (foreclosure/floor), or midpoint**.

- **Ceiling**: Web-scraped listing prices (speculative asking prices)
- **Floor**: Foreclosed property prices (distressed bank pricing)
- **Answer**: Predicting the **midpoint/mean** as the "objective truth" price.

**Action:** Justify the target variable choice (mean of floor–ceiling) clearly in the methodology section.

---

## 3. GIS/Spatial Augmentation Is the Core Contribution

The panel confirmed that the **real thesis work** is not the baseline regression — it's the **augmentation with geocoded/spatial data**:

- Geocoding addresses → lat/lon coordinates
- Computing **proximity features** (distance to economic anchors)
- Pulling spatial data from **Google Maps / OpenStreetMap (OSM)**
- This was described as the **"crux"** of the project — where 90% of the actual work lies.

**Action:** Position GIS/geospatial feature engineering as the **primary methodological contribution**, especially now that NLP is removed.

---

## 4. QGIS Interactive Map as a Key Deliverable

The panel pushed for a **tangible, practical output**: an **interactive map** built in QGIS.

- QGIS is natively Python-based, so model integration should be feasible.
- The map would serve as a **decision-support tool** for real estate brokers (REBAP — Real Estate Brokers Association of the Philippines).
- Output should be **prescriptive** — not just "what is the price?" but "what *should* it be?"
- **Sir Randy** specifically requested the interactive map.

**Action:** Commit to an interactive QGIS map as a deliverable. Document how the trained model feeds into it.

---

## 5. Address Spatial Autocorrelation (Neighbor Price Effects)

The panel raised an important question: **Do nearby property prices influence the target property's valuation?**

- If neighboring properties already have known prices, those could serve as **input features**.
- Example contrast: a BGC-quality property next to a slum area — proximity alone doesn't capture value.
- Clustering effects should be accounted for (geographically close properties should have similar values, unless there's a stark quality difference).

**Action:** Consider incorporating **spatial lag features** (e.g., average price of neighboring properties) or spatial clustering analysis. Acknowledge spatial autocorrelation in the methodology.

---

## 6. Model Explainability (SHAP) Is Non-Negotiable

The panel emphasized that **explainability** is a critical requirement — both for compliance (IVS 2025) and for practical adoption.

- Stakeholders need to understand **why** a model assigns a certain price, not just the predicted value.
- Spatial visualizations (choropleth maps, heat maps) complement SHAP by showing value drivers geographically.

**Action:** Keep SHAP as a core output. Combine with geographic visualizations for intuitive explainability.

---

## 7. Standardize Terminology: "Value Drivers"

The panel asked for the term used for features/variables that influence price. The agreed-upon convention: **"value drivers"**.

**Action:** Use "value drivers" consistently across all documents (manuscript, presentation, code comments).

---

## 8. Focus Presentations on What's Unique

The panel advised: **don't belabor the basics** (standard ML pipeline, regression, random forest, XGBoost). These are well-established. Instead, lead with what makes this thesis distinct:

- GIS/spatial feature engineering
- Interactive map output
- Philippine-context novelty

**Action:** In future presentations, front-load the GIS/geospatial differentiation. Treat core ML models as supporting infrastructure.

---

## 9. RRL Needs Clearer Separation

A panelist noted that the Review of Related Literature was **not sufficiently clear**. The presentation blurred the line between what *previous studies found* and what *this thesis will do*, causing confusion.

**Action:** Cleanly separate "what the literature established" from "how we build upon / differ from it."

---

## 10. Philippine-Context Novelty

The panel acknowledged that this type of **spatial/GIS-driven property valuation model is new for Philippine data**, which strengthens the thesis contribution.

**Action:** Emphasize this novelty in the Significance of the Study section.

---

## Summary: Revised Scope Post-Panel

| ✅ **Keep / Strengthen**                    | ❌ **Remove**                                    |
| :----------------------------------------- | :---------------------------------------------- |
| GIS / Geocoding pipeline                   | NLP feature extraction (TF-IDF, BERT, Word2Vec) |
| Proximity features (Haversine distances)   | Text Features category from feature table       |
| OSM Amenity Scoring                        | Slide on NLP & Text Data                        |
| Building Density (HDX data)                | Secondary Objective on NLP accuracy gain        |
| QGIS interactive map output                |                                                 |
| SHAP explainability                        |                                                 |
| Spatial autocorrelation / neighbor effects |                                                 |
| Heat maps & choropleth visuals             |                                                 |
