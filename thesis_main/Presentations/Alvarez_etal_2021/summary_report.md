# Summary Report: A Framework for Measuring Geospatial Amenity Accessibility in the Philippines
**Reference:** Alvarez et al. (2021)

## 1. Definition of Terms

*   **Amenities:** Useful features, facilities, or services of a place (e.g., health centers, schools, banks, transportation hubs, grocery stores) that contribute to the quality of life or desirability of an area.
*   **Spatial Data:** Information about the physical location and shape of geographic features and the relationships between them. This is often represented by geographic coordinates (latitude and longitude) and used in Geographic Information Systems (GIS).
*   **Spatial Inequality:** The unequal distribution of resources, services, or amenities across different geographic areas, leading to disparities in accessibility and quality of life for residents based on their location.
*   **Project OHANA:** "Open-source Heatmap and Analytics for Nationwide Amenities Accessibility," an initiative designed to provide an accessible, scalable framework for calculating and visualizing amenity accessibility across the Philippines using open-source data.
*   **Hansen's Gravitation Model:** A mathematical model used to measure accessibility. It calculates how easily people can reach amenities from a specific location based on the attractiveness (number) of amenities available and the friction (distance or travel time) of reaching them.
*   **Neighborhood Distance:** A parameter in accessibility modeling representing the maximum search radius (in this study, 14.2 km) considered when calculating accessibility for a specific zone. Amenities beyond this distance are excluded or assumed to have negligible impact.
*   **Self-Distance:** A default minimum distance (in this study, 0.5 km) assigned to amenities located within the exact same zone as the point of measurement. This prevents divide-by-zero errors in mathematical models and accounts for the short, intra-zone travel required to access local amenities.

## 2. Introduction & Context

Rapid urbanization in the Philippines, particularly in areas like Metro Manila and Metro Cebu, has led to significant spatial inequality in terms of social infrastructure and basic services. Addressing these disparities requires robust spatial data to inform urban planning. However, developing countries frequently lack granular, scalable, and up-to-date spatial data, as manual surveying is both expensive and time-consuming. To bridge this gap, Alvarez et al. (2021) introduced Project OHANA, leveraging open-source data to systematically map and measure amenity accessibility across the nation.

For our thesis on Machine Learning-based real estate valuation in Cebu, this framework is highly relevant. It provides a standardized methodology to quantify the accessibility of urban amenities, which is a critical feature often correlated with property values.

## 3. Methodology: Geospatial Amenity Accessibility

The study utilized open-source spatial data from OpenStreetMap (OSM) extracted via the Overpass API. Amenities were grouped into six primary categories: Health, Finance, Education, Security, Transportation, and Grocery. The researchers divided the Philippine map into a grid of 1km x 1km zones, assigning a centroid to each.

To calculate the amenity accessibility score for each zone, the researchers applied Hansen's Gravitation Model. This model evaluates accessibility based on the volume of amenities and the friction of travel (distance). Specific parameters were applied to tailor the model: a friction coefficient ($\beta$) of 2.0 to represent travel difficulty, a maximum neighborhood distance of 14.2 km to define the relevant search radius for external amenities, and a self-distance of 0.5 km to serve as the baseline distance for amenities located within the same 1km zone.

## 4. Key Findings: Amenity Accessibility 

At the national level, the study revealed stark contrasts. The National Capital Region (NCR) exhibited extremely high, saturated accessibility, achieving a score of 814.45. Neighboring regions like CALABARZON (26.97) and Central Luzon (18.24) followed, benefiting from their industrial proximity to the capital. Conversely, regions like ARMM ranked the lowest (2.43), indicating severe inaccessibility.

Within the NCR itself, accessibility was not uniform. Central cities like Mandaluyong and San Juan scored the highest due to their strategic, central geography. In contrast, cities adjacent to natural barriers, like Navotas and Muntinlupa, scored lower. The data also highlighted specific concentrations, such as Makati skewing the "Financial" amenities category with over 4,700 institutions.

## 5. Practical Applications and Use Cases

The authors highlighted two main use cases to demonstrate the utility of their accessibility scores. These cases are particularly insightful for analyzing spatial dynamics:

### Local Government Revenue vs. Amenity Accessibility
The first use case tested the hypothesis that higher amenity accessibility boosts property values and tax collections, which in turn funds more amenities. In the NCR, there was a significant positive correlation (Pearson = 0.901) between local government revenue and accessibility. However, in Cebu and Davao, **no significant correlation was found** at the provincial level. Most cities in these provinces clustered at low accessibility levels despite varying revenues. In Cebu, specific economic hubs (Cebu City, Mandaue, Lapu-lapu, and Talisay) diverged from the broader provincial trend, acting as isolated centers of high accessibility.

### Health Amenity Equity for the Elderly
The second use case applied the Gini coefficient to measure the spatial inequality of healthcare access for the elderly. While the NCR showed relatively low inequality (Gini = 0.4392), indicating an even distribution of health services, **Cebu Province exhibited extremely high inequality (Gini = 0.9182)**. The data showed that isolated municipalities had almost zero access, whereas specific areas like Mandaue City effectively monopolized healthcare facilities relative to their geographic area.

## 6. Relevance to Thesis (Cebu Real Estate Valuation)

The methodology and findings of Alvarez et al. (2021) directly inform our thesis on real estate valuation in Cebu:

*   **Feature Engineering:** By adopting Hansen's Gravitation Model and leveraging OSM data (Health, Finance, Transport), we can engineer robust "Accessibility Scores" as features for the Lamudi property dataset. 
*   **Validating Spatial Inequality:** The study statistically confirms that Cebu suffers from high spatial inequality, with resources centralized around Mandaue and Cebu City. This validates our hypothesis that a property's geospatial coordinates will be a highly significant predictor in our ML valuation model.
*   **Beyond Euclidean Distance:** The research demonstrates that calculating an aggregate accessibility score—which accounts for the density of surrounding amenities within a defined radius—is far more sophisticated and likely more predictive than simply measuring the linear distance to the nearest single mall or hospital.
