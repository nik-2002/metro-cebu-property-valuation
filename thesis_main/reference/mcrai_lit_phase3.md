# MCRAI Phase 3 Literature Research — Working Notes

> Status: COMPLETE — Decision 28 logged in `modeling_decisions.md` (2026-05-15)
> Started: 2026-05-15
> Purpose: Build literature basis for MCRAI category restructuring before recomputing Hansen scores

---

## Current 9 MCRAI categories
education, health, finance, grocery, transport, security, tourism, recreation, retail_density

---

## Studies Found So Far

### Yao, Zhang & Li (2017) — Beijing POI Hedonic Study
- **Citation**: Yao, Y., Zhang, J., & Li, X. (2017). Exploring Determinants of Housing Prices in Beijing: An Enhanced Hedonic Regression with Open Access POI Data. *ISPRS International Journal of Geo-Information*, 6(11), 358.
- **URL**: https://www.mdpi.com/2220-9964/6/11/358
- **Context**: Beijing, 6,959 residential properties, POI-based hedonic regression with eigenvector spatial filtering
- **POI categories used**: education (kindergartens, schools, universities), health (clinics, hospitals, pharmacies), transport (roads, bus stations, car parks), culture (theatres, museums), recreation (parks, forests, lakes)
- **Key finding**: Education, health, transport, recreation all positive and statistically significant. Two-stage structure: POI accessibility → hedonic regression.
- **Relevance**: Closest methodological match to MCRAI. Validates 4–5 category structure. Does NOT include finance, security, or tourism as standalone categories.
- **Verify before citing**: DOI 10.3390/ijgi6110358 — confirm findings match above

### Moosavi, Tavakkoli-Moghaddam & Ghodratnama (2021) — Bangkok Google Maps + ML
- **Citation**: Moosavi, V., Tavakkoli-Moghaddam, R., & Ghodratnama, A. (2021). Google Maps amenities and condominium prices: Investigating the effects and relationships using machine learning. *Cities*, 109, 103050.
- **URL**: https://www.sciencedirect.com/science/article/abs/pii/S0197397521001521
- **Context**: Bangkok, 500 condominiums, 285 factors across 95 Google Maps amenity types, XGBoost + hedonic
- **Key finding**: XGBoost retained 36 of 285 factors as important. Transport and recreation strongest drivers. Health less consistent for condos specifically. Retail and food amenities matter but relationship is non-linear (humped/bounded).
- **Relevance**: SE Asian context (Thailand), condo market, confirms transport + recreation dominance. Google Maps data source matches our workflow.
- **Verify before citing**: DOI 10.1016/j.cities.2021.103050 — confirm author names and findings

### Rey-Blanco, Zofío & González-Arias (2023) — Optimal Gravity Accessibility Indices
- **Citation**: Rey-Blanco, D., Zofío, J.L., & González-Arias, P. (2023). Improving hedonic housing price models by integrating optimal accessibility indices into regression and random forest analyses. *Expert Systems with Applications*, 213, 119241.
- **URL**: https://www.sciencedirect.com/science/article/pii/S0957417423015610
- **Context**: Multi-city, gravity-based accessibility indices integrated into both hedonic regression and Random Forest
- **Key finding**: Category-specific calibration of gravity indices outperforms a single global composite. Validates Hansen-type accessibility as a feature engineering approach for ML models.
- **Relevance**: Directly validates our Hansen gravity approach and the use of RF alongside hedonic regression. Supports category-specific radii and decay parameters.
- **Verify before citing**: DOI 10.1016/j.eswa.2022.119241 — confirm journal and year

---

## Preliminary Category Recommendation (NOT YET DECIDED)

| Category | Lean | Basis |
|---|---|---|
| transport | Retain | Strongest signal across all SE Asian studies |
| education | Retain | Universally significant across all three studies above |
| health | Retain | Consistently included; less significant for condos but defensible for house/lot strata |
| recreation | Retain | Significant in all contexts — Yao 2017, Moosavi 2021, Jakarta/Shanghai green space |
| grocery | Retain | Essential-goods access proxy; standard in residential accessibility literature |
| finance | Drop | Not a standard hedonic amenity category in any study reviewed; proxies urban density not residential amenity |
| security | Pending | Negative OLS coef (Decision 20, spatial sorting). No study uses security as standalone positive amenity |
| tourism | Pending | Negative OLS coef (Decision 20). Not a residential amenity category in literature reviewed |
| retail_density | Pending | Negative OLS coef (Decision 20); Yang et al. (2016) inverted-U threshold effect |

### Hangzhou POI Accessibility Study (2022) — ASCE JUPD
- **Citation**: Wen, H. et al. (2022). Influence of POI Accessibility on Temporal–Spatial Differentiation of Housing Prices: A Case Study of Hangzhou, China. *Journal of Urban Planning and Development*, 148(4).
- **URL**: https://ascelibrary.org/doi/10.1061/%28ASCE%29UP.1943-5444.0000878
- **Context**: Hangzhou, China; geographically and temporally weighted regression; multiple POI categories
- **Key finding**: Education resources (schools) and transport access become MORE prominent drivers of housing prices over time. CBD/employment concentration also significant. Recreation/parks significant.
- **Relevance**: Validates the education + transport + recreation core — directly comparable multi-category POI study using gravity-style accessibility.
- **Verify before citing**: Confirm author list and exact journal volume/issue.

### South Tangerang HPM Study (2024) — Planning Malaysia
- **Citation**: [Author TBC] (2024). Hedonic Pricing Model (HPM) on South Tangerang Residential Property Value. *Planning Malaysia Journal*.
- **URL**: https://www.planningmalaysia.org/index.php/pmj/article/view/1681
- **Context**: South Tangerang City, Indonesia (Jakarta suburban); multiple linear regression HPM; residential properties scraped from listing sites July 2023–January 2024
- **Key finding**: **SIGNIFICANT**: distance to KRL stations (commuter rail), public parks, top high schools, CBD, building area, land area, rooms. **INSIGNIFICANT**: distance to malls, hospitals, universities, population density.
- **Relevance**: SE Asian developing-city context. Directly supports dropping malls/retail as a category. Hospitals insignificant — challenges blanket retention of health. High schools significant but universities not — secondary education matters more than tertiary for residential buyers.
- **Verify before citing**: Confirm author, year, and that "no partial effect" for hospitals/malls is the correct characterization of results.

### Philippines ML Property Valuation Study (2023) — The Philippine Statistician
- **Citation**: [Author TBC] (2023). Utilization of Machine Learning, Government-Based and Non-Conventional Indicators for Property Value Prediction in the Philippines. *The Philippine Statistician*, 72(1).
- **URL**: https://www.psai.ph/docs/publications/tps/tps_2023_72_1_1.pdf
- **Context**: Philippines (Cavite + Metro Manila); uses OpenStreetMap geolocation data + PSA/BIR/DTI government indicators; MAPE 10.7–21%
- **Key finding**: OSM-derived geolocation features + government indicators improve model performance. LGU competitiveness index (economic dynamism, infrastructure, resiliency) has substantial positive effect.
- **Relevance**: Most directly comparable Philippines-context study. Validates OSM-based spatial features for Philippine property valuation. Does not test amenity categories individually — focuses on government socio-economic indicators as supplementary features.
- **Verify before citing**: Download PDF and confirm author list, exact data sources, and feature list.

### Agosto (2017) — Determinants of Land Values in Cebu City, Philippines
- **Citation**: Agosto, A.B. (2017). Determinants of Land Values in Cebu City, Philippines. University of San Carlos.
- **URL**: https://www.researchgate.net/publication/345343910_Determinants_of_Land_Values_in_Cebu_City_Philippines / https://appraiserph.com/2017/04/03/determinants-of-land-values-in-cebu-city-philippines/
- **Context**: Cebu City only; survey of 52 real estate practitioners, valuers, assessors; 31 determinants; factor analysis + PCA + multiple regression
- **Key finding**: Accessibility to public transportation ranks **#1 of 31 determinants**. Top category groupings: (1) Mobility — transport; (2) Livability — open space, parks, recreational facilities, environmental quality; (3) Economic — employment access, rental income. Health services appear in the list but not in the top-ranked cluster.
- **Relevance**: Only Cebu City-specific hedonic determinants study found. Directly grounds transport as the dominant amenity driver in our study area. Recreation/parks in livability cluster = #2 group. Finance/banking not mentioned as a top determinant.
- **Verify before citing**: Confirm full publication details — journal or thesis? Year confirmed as 2017 via appraiserph.com post date. Author institution: University of San Carlos.

### Alvarez et al. (2021) — OHANA Framework, ISPRS Archives
- **Citation**: Alvarez, F.D., Madridejos, J.M., Sarmiento, J.A., Valdez, E., & Lecaros, L.L. (2021). A Framework for Measuring Geospatial Amenity Accessibility in the Philippines. *ISPRS Archives*, XLVI-4/W6-2021, 19–26.
- **URL**: https://isprs-archives.copernicus.org/articles/XLVI-4-W6-2021/19/2021/
- **Context**: Nationwide Philippines; Hansen gravity model with OSM data; equity-focused (Gini coefficient on accessibility scores); applied to NCR, Cebu, Davao
- **Key finding**: Confirms Hansen gravity model is implementable with OSM data at Philippine city scale. Health and transport are the primary categories used in OHANA equity analysis. Framework is normative (equity mapping), not revealed-preference (valuation).
- **Relevance**: OHANA is the methodological precursor to MCRAI. Confirms the Hansen + OSM approach is published and defensible in a Philippines context. The key distinction for the thesis is that OHANA measures equity (where services *should* be), whereas MCRAI measures revealed market preference (what buyers *pay* for).
- **Verify before citing**: DOI available via ISPRS Archives page. Confirm category list from the PDF.

### Peng & Chiang (2015) — Non-linearity of Hospital Proximity, Taipei
- **Citation**: Peng, C.W., & Chiang, Y.H. (2015). The non-linearity of hospitals' proximity on property prices: experiences from Taipei, Taiwan. *Journal of Property Research*, 32(4), 341–361.
- **URL**: https://www.tandfonline.com/doi/abs/10.1080/09599916.2015.1089923
- **Context**: Taipei metropolis; quantile regression on hospital spline distance; hospital classified as "semi-obnoxious facility"
- **Key finding**: **Goldilocks/non-linear effect.** Very close proximity (0–500m): disamenity — sirens, ambulance noise, congestion, institutional surroundings → negative price effect. Medium distance (500m–1km+): amenity — accessible care → positive. "Close but not too close" is the market preference. Lower quantile properties (Q10–Q20) are most responsive to high proximity.
- **Relevance**: Directly explains why a Hansen gravity score for health may show a mixed or negative OLS coefficient — the formula weights closer POIs MORE heavily (1/d²), so properties immediately adjacent to a hospital get the highest health score even though those properties may price lower due to disamenity. This is a methodological caution, not a reason to drop health entirely.
- **Verify before citing**: DOI 10.1080/09599916.2015.1089923 — confirm findings match above.

### Li et al. (2022) — Hospital and Rail Accessibility, Fuzhou China (Frontiers)
- **Citation**: Li et al. (2022). Do hospital and rail accessibility have a consistent influence on housing prices? Empirical evidence from China. *Frontiers in Environmental Science*, 10, 1044600.
- **URL**: https://www.frontiersin.org/journals/environmental-science/articles/10.3389/fenvs.2022.1044600/full
- **Context**: Fuzhou, China; spatial hedonic regression with interaction terms between hospital and rail accessibility
- **Key finding**: Mixed results depending on hospital grade and interaction with transit. Grade-A tertiary hospitals within 1,000m: +10.7% and +7.5% price premium (Wang & Gao 2014 cited within). Each additional walkable hospital: −2.8% (Yang et al. 2016 cited within). The net effect depends on hospital grade and density — high-grade hospitals are amenities, clusters of lower-grade hospitals are disamenities.
- **Relevance**: Hospital grade matters. In Metro Cebu, `health.csv` mixes hospitals, clinics, and pharmacies — the positive amenity effect is most likely driven by hospitals, not clinics. Retaining health as a single blended category may dilute the signal.
- **Verify before citing**: DOI via Frontiers page.

---

## Updated Category Evidence Table

| Category | Agosto 2017 (Cebu) | South Tangerang | Hangzhou | Beijing (Yao 2017) | Bangkok (Moosavi 2021) | Lean |
|---|---|---|---|---|---|---|
| transport | ✅ **#1 of 31** | ✅ KRL significant | ✅ Significant | ✅ Significant | ✅ Strongest driver | **Retain** |
| education | Not top-ranked | ✅ High schools; universities NOT | ✅ Significant | ✅ Significant | ✅ Moderate | **Retain (secondary focus)** |
| recreation | ✅ Livability #2 group | ✅ Public parks significant | ✅ Significant | ✅ Significant | ✅ Strong for condos | **Retain** |
| health | In list, not top-ranked | ❌ Hospitals insignificant | Not tested | ✅ Positive | ⚠️ Less consistent for condos | **Ambiguous — stratum-specific?** |
| grocery | Not mentioned | Not tested | Not tested | Retail positive | ✅ Food/shopping positive | **Retain (essential goods proxy)** |
| finance | Not mentioned | Not tested | Not tested | Not a category | Not a category | **Drop** |
| security | Not top-ranked | Not tested | — | — | — | **Drop (Decision 20)** |
| tourism | Not mentioned | Not tested | — | — | — | **Drop (Decision 20)** |
| retail_density | Not mentioned | ❌ Malls insignificant | — | Shopping positive but non-linear | ⚠️ Humped/bounded | **Drop from composite (Decision 20)** |

---

## Open Questions Before Decision 28

1. Are there studies that directly use Hansen gravity composite with this exact 4–6 category structure in a developing-country city context?
2. Is there a Philippines-specific hedonic study that uses amenity categories we can directly cite?
3. Do security/tourism/retail_density stay as individual model features in stratified models, or drop entirely?
4. Should finance be retired from POI files entirely, or just excluded from composite?

---

## Still Need to Find

- More SE Asian studies using Hansen gravity composite (not just distance-to-amenity)
- Philippines-specific study using accessibility categories in hedonic model
- Study that explicitly justifies dropping finance as an amenity category
- Literature on property-type-specific category sets (do condo buyers value different amenities than house buyers?)
