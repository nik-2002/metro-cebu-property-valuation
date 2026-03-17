# GIS Data Notes

## Humanitarian Data Exchange (HDX) - Philippines Buildings
**Source:** [HOTOSM Philippines Buildings (OpenStreetMap Export)](https://data.humdata.org/dataset/hotosm_phl_buildings)

### Dataset Overview
- **Content:** Building footprints and associated metadata from OpenStreetMap for the Philippines.
- **Coverage:** Roughly 11.6 million buildings (approx. 52% of total estimated buildings based on AI mappings).
- **Data Vintage:** Average age of data is 3 years, with recent updates organically crowdsourced.
- **Formats Available:** GeoJSON, KML, SHP (Shapefile), Geopackage, CSV.

### Key Attributes
The dataset includes all OSM features matching `building IS NOT NULL`.
Important attributes for analysis include:
- `building`: The type of building (e.g., residential, commercial, industrial).
- `building:levels`: The number of floors in the building.
- `building:materials`: Construction materials.
- `addr:full`, `addr:city`, `addr:street`: Location details.
- `office`: Type of office if applicable.

### Potential Use Cases for Real Estate Valuation (Cebu Model)
1. **Built Environment Features:** 
   - **Spatio-Structural Density:** Calculate building density (number of buildings per sq km) around target properties.
   - **Footprint Area:** Determine the average or total building footprint area in a neighborhood, which can serve as a proxy for urbanization or land use intensity.
2. **Structural Characteristics:**
   - Use `building:levels` and `building:materials` to estimate the prevailing structural profile and economic status of a sub-market.
3. **Zoning / Land Use Proxy:**
   - The type of building (residential vs. commercial) can help classify neighborhoods and identify commercial hubs or residential zones without relying solely on local government zoning maps.
4. **Distance Metrics:**
   - Measure the spatial distance from subject properties to key building types (e.g., major commercial centers, offices, or industrial zones).

### Next Steps
- Download the Shapefile (SHP) or Geopackage for the Cebu province/city boundary.
- Load the data into a GIS tool (like QGIS) or use Python libraries (`geopandas`, `osmnx`) to filter for Cebu's specific bounding box or administrative boundaries.
- Perform spatial joins with the existing property dataset (`processed_properties_cebu.csv`) to engineer new location-based and structural features for the valuation model.
