# Summary Report: A Framework for Measuring Geospatial Amenity Accessibility in the Philippines

**Reference:** Alvarez et al. (2021)

## 1. Definition of Terms

* **Amenities:** Facilities or services of a place (e.g., health centers, schools, banks, transportation hubs, grocery stores) that contribute to the quality of life or desirability of an area.
* **Spatial Data:** Information about the physical location and shape of geographic features, often represented by coordinates (latitude/longitude) and used in Geographic Information Systems (GIS).
* **Spatial Inequality:** The unequal distribution of resources, services, or amenities across geographic areas, leading to disparities in accessibility and quality of life based on location.
* **Project OHANA:** "Open-source Heatmap and Analytics for Nationwide Amenities Accessibility" — a scalable framework for calculating and visualizing amenity accessibility across the Philippines using open-source data.
* **Hansen's Gravitation Model:** A mathematical model that measures accessibility by weighing the number of nearby amenities against the friction (distance) required to reach them. Higher scores indicate better access.
* **Neighborhood Distance:** The maximum search radius (14.2 km in this study) within which surrounding zones and their amenities are considered when calculating a zone's accessibility score. Zones beyond this radius are excluded.
* **Self-Distance:** A default minimum distance (0.5 km in this study) assigned when amenities fall within the same zone as the point of measurement. This prevents divide-by-zero errors and accounts for short intra-zone travel.

## 2. Introduction & Context

Rapid urbanization in the Philippines, particularly in Metro Manila and Metro Cebu, has led to significant spatial inequality in social infrastructure and basic services. Addressing these disparities requires robust spatial data, but developing countries often lack granular, up-to-date information — manual surveying is expensive and time-consuming. To bridge this gap, Alvarez et al. (2021) introduced Project OHANA, leveraging open-source data from OpenStreetMap to systematically map and measure amenity accessibility across the nation.

This framework is directly relevant to our thesis on ML-based real estate valuation in Cebu, as it provides a standardized methodology to quantify the accessibility of urban amenities — a factor strongly correlated with property values.

## 3. Methodology

The study extracted amenity data from OpenStreetMap (OSM) via the Overpass API, grouping them into six categories: Health, Finance, Education, Security, Transportation, and Grocery. The Philippine map was divided into 1km × 1km grid zones, each represented by a centroid.

Hansen's Gravitation Model was then applied to compute accessibility scores for each zone, measuring access based on the volume of amenities and the friction of travel (distance). The key parameters used were: a friction coefficient ($\beta$) of 2.0, a maximum neighborhood distance of 14.2 km, and a self-distance of 0.5 km. Distance between zone centroids was calculated using great-circle distance, with fixed transportation mode and constant travel speed assumed.

## 4. Key Findings

**National Level:** The NCR dominated with an average accessibility score of 814.45. CALABARZON (26.97) and Central Luzon (18.24) followed, benefiting from proximity to the capital. ARMM ranked lowest at 2.43, reflecting severe inaccessibility. This pattern mirrors the World Bank's assessment of overconcentrated development in Metro Manila.

**Within NCR:** Accessibility was not uniform. Central cities like Mandaluyong and San Juan scored highest due to their strategic geography, while Navotas and Muntinlupa scored lower due to geographic barriers (water bodies). Makati heavily skewed the "Financial" category with over 4,700 institutions.

## 5. Use Cases

### LGU Revenue vs. Amenity Accessibility

The study tested whether higher amenity accessibility correlates with local government revenue. In NCR, a strong positive correlation was found (Pearson = 0.901) — wealthier LGUs had significantly higher accessibility. However, in Cebu and Davao, **no significant correlation** existed at the provincial level. Most cities clustered at low accessibility despite varying revenues. Only economic hubs like Cebu City, Mandaue, Lapu-lapu, and Talisay diverged from this trend.

### Health Amenity Equity for the Elderly

Using the Gini coefficient, the study measured spatial inequality of healthcare access. NCR showed relatively low inequality (Gini = 0.4392), indicating even distribution. **Cebu Province exhibited extreme inequality (Gini = 0.9182)** — isolated municipalities had near-zero access, while Mandaue City effectively monopolized healthcare facilities relative to its area.

## 6. Relevance to Thesis (Cebu Real Estate Valuation)

* **Feature Engineering:** We can adopt Hansen's Gravitation Model with OSM data (Health, Finance, Transport) to engineer "Accessibility Scores" as ML features for the Lamudi property dataset.
* **Validating Spatial Inequality:** The study confirms Cebu has high spatial inequality, with resources concentrated around Mandaue and Cebu City. This validates our hypothesis that geospatial coordinates will be a strong predictor in our valuation model.
* **Beyond Simple Distance:** An aggregate accessibility score — accounting for the density of amenities within a radius — is more informative than measuring distance to the nearest single amenity, and could meaningfully improve model accuracy.
