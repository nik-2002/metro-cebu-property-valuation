# GIS Roadmap — Geospatial Feature Engineering & QGIS Map

> This roadmap details the GIS/geospatial component of the thesis — the **core methodological contribution**.
> Target completion: **March 14, 2026** (geocoding + features) | **April 18, 2026** (QGIS map).

---

## Phase 1: Geocoding (Mar 1–7)

| Step | Task                                                  | Tool                      | Status |
| ---- | ----------------------------------------------------- | ------------------------- | ------ |
| 1.1  | Batch geocode BDO Metro Cebu addresses (~80–100)      | Google Maps Geocoding API | ⬜      |
| 1.2  | Batch geocode Lamudi Metro Cebu listings (~500+)      | Google Maps Geocoding API | ⬜      |
| 1.3  | Handle geocoding failures (retry, Nominatim fallback) | geopy / Nominatim         | ⬜      |
| 1.4  | Validate 10% sample — plot on QGIS, visual check      | QGIS                      | ⬜      |
| 1.5  | Standardize barangay names from geocode results       | Python / Pandas           | ⬜      |

**Input**: Raw property addresses (BDO Excel + Lamudi scraped)
**Output**: `geocoded_properties.csv` with `lat`, `lon`, `standardized_barangay`

---

## Phase 2: Proximity Features (Mar 7–10)

| Step | Task                                             | Tool                   | Status |
| ---- | ------------------------------------------------ | ---------------------- | ------ |
| 2.1  | Define reference nodes with coordinates          | Manual / Google Maps   | ⬜      |
| 2.2  | Compute Haversine distance to each node          | Python (haversine lib) | ⬜      |
| 2.3  | EDA: distance distributions + price correlations | Matplotlib / Seaborn   | ⬜      |

**Reference Nodes**:
- Ayala Center Cebu (10.3186°N, 123.9056°E) — primary CBD
- Cebu IT Park (10.3308°N, 123.9060°E) — IT-BPM employment hub
- SM Seaside City (10.2804°N, 123.8771°E) — commercial center
- Mactan-Cebu International Airport (10.3075°N, 123.9795°E)
- CBRT station locations (TBD — DPWH/DOTr alignment plan)

**Output**: New columns `dist_ayala`, `dist_itpark`, `dist_smseaside`, `dist_airport`, `dist_cbrt_nearest`

---

## Phase 3: OSM Amenity Scoring (Mar 10–12)

| Step | Task                                                      | Tool                 | Status |
| ---- | --------------------------------------------------------- | -------------------- | ------ |
| 3.1  | Query OSM for POIs within 1 km radius per property        | osmnx                | ⬜      |
| 3.2  | Count by category: education, health, commercial, transit | osmnx + Pandas       | ⬜      |
| 3.3  | Compute composite amenity score                           | Pandas               | ⬜      |
| 3.4  | EDA: amenity score vs. price                              | Matplotlib / Seaborn | ⬜      |

**POI Categories**:
| OSM Tag                                    | Category   | Example           |
| ------------------------------------------ | ---------- | ----------------- |
| `amenity=school` / `amenity=university`    | Education  | USC, CIT-U        |
| `amenity=hospital` / `amenity=clinic`      | Healthcare | Chong Hua, VSMMC  |
| `shop=mall` / `amenity=marketplace`        | Commercial | Ayala, SM, Carbon |
| `highway=bus_stop` / `amenity=bus_station` | Transit    | Jeepney stops     |

**Output**: New columns `amenity_education`, `amenity_health`, `amenity_commercial`, `amenity_transit`, `amenity_total`

---

## Phase 4: Spatial Autocorrelation (Mar 12–14)

| Step | Task                                                      | Tool             | Status |
| ---- | --------------------------------------------------------- | ---------------- | ------ |
| 4.1  | Build spatial weights matrix (K-nearest or distance band) | PySAL / libpysal | ⬜      |
| 4.2  | Compute spatial lag variable (mean neighbor price)        | PySAL            | ⬜      |
| 4.3  | Compute Moran's I on OLS residuals                        | PySAL (esda)     | ⬜      |
| 4.4  | Decision: use spatial lag as ML feature or fit SAR model  | Analysis         | ⬜      |

**Output**: New column `spatial_lag_price`, Moran's I test result

---

## Phase 5: QGIS Interactive Map (Apr 1–18)

| Step | Task                                               | Tool                      | Status |
| ---- | -------------------------------------------------- | ------------------------- | ------ |
| 5.1  | Export final dataset as GeoPackage / GeoJSON       | geopandas                 | ⬜      |
| 5.2  | Create QGIS project with Metro Cebu basemap        | QGIS                      | ⬜      |
| 5.3  | Layer: Property predictions (color by error)       | QGIS styling              | ⬜      |
| 5.4  | Layer: Valuation Gap heatmap (Model vs. BIR Zonal) | QGIS heatmap renderer     | ⬜      |
| 5.5  | Layer: Proximity contours (isochrone rings)        | QGIS / osmnx              | ⬜      |
| 5.6  | Layer: Amenity density overlay                     | QGIS kernel density       | ⬜      |
| 5.7  | Style + export interactive HTML                    | qgis2web plugin or folium | ⬜      |

**Output**: `metro_cebu_valuation.qgz` (QGIS project) + `interactive_map.html`

---

## Dependencies

| Dependency             | Status        | Notes                                          |
| ---------------------- | ------------- | ---------------------------------------------- |
| `thesis-gis` conda env | ✅ Done        | geopandas, osmnx, folium, googlemaps installed |
| Google Maps API key    | ✅ Done        | Stored in `.env`, verified working             |
| OSM query test         | ✅ Done        | Verified Cebu amenity queries via osmnx        |
| BDO data cleaned       | ⬜ In progress | ~80–100 Cebu residential entries               |
| Lamudi data scraped    | ⬜ Pending     | Target: 500+ listings                          |
| ML models trained      | ⬜ Pending     | Required before QGIS map (Phase 5)             |
