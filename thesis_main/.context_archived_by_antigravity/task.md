# Tasks

- [x] Complete Thesis Manuscript <!-- id: 6 -->
    - [x] Identify missing sections in Full_Thesis_Draft.md <!-- id: 7 -->
    - [x] Draft "1.6 Scope and Limitations" <!-- id: 8 -->
    - [x] Review Chapter 2 for citation gaps <!-- id: 9 -->
    - [x] Review Chapter 3 for consistency with planned methodology <!-- id: 10 -->
    - [ ] Finalize formatting and references <!-- id: 11 -->
- [x] Sync Manuscript with Presentation Script <!-- id: 12 -->
    - [x] Analyze presentation_script.md for new concepts <!-- id: 13 -->
    - [x] Map differences to Manuscript chapters <!-- id: 14 -->
    - [x] Update Manuscript with new ideas <!-- id: 15 -->
- [x] Convert Thesis to LaTeX <!-- id: 16 -->
    - [x] Create TeX directory structure <!-- id: 17 -->
    - [x] Setup main.tex with academic preamble <!-- id: 18 -->
    - [x] Convert Chapter 1 to chapter1.tex <!-- id: 19 -->
    - [x] Convert Chapter 2 to chapter2.tex <!-- id: 20 -->
    - [x] Convert Chapter 3 to chapter3.tex <!-- id: 21 -->
    - [x] Create biblio.bib for references <!-- id: 22 -->
- [x] Refine Thesis Content <!-- id: 23 -->
    - [x] Fix Chapter 1 flow "also reported" <!-- id: 24 -->
    - [x] Standardize citations in Chapter 3 <!-- id: 25 -->
- [x] Setup NotebookLM MCP Server <!-- id: 26 -->
    - [x] Install `notebooklm-mcp-server` globally via pip <!-- id: 27 -->
    - [x] Configure `~/.gemini/antigravity/mcp_config.json` <!-- id: 28 -->
    - [x] Authenticate via browser login <!-- id: 29 -->
    - [x] Verify connection (34 notebooks listed) <!-- id: 30 -->
- [x] Generate Literature Summaries <!-- id: 31 -->
    - [x] Create Summaries directory structure <!-- id: 32 -->
    - [x] Generate summaries for all 44 sources <!-- id: 33 -->
    - [x] Claude Opus audit (verified 8 claims, no hallucinations) <!-- id: 34 -->
    - [x] Organize into Tier A/B/Unusable folders <!-- id: 35 -->
- [x] Enhance Tier A Summaries <!-- id: 42 -->
    - [x] Phase 1: Deep rewrites (Sources 36, 38, 40) <!-- id: 43 -->
    - [x] Phase 2: Methodology enhancement (Sources 20, 29, 32) <!-- id: 44 -->
    - [x] Phase 3: Spot-checks (Sources 01, 02, 05, 08, 13) <!-- id: 45 -->

---

## Post-Panel Revisions (2026-02-26)

> **PIVOT**: NLP feature extraction removed. GIS/geocoding is now the core contribution.
> Thesis is now **predictive + prescriptive** (QGIS interactive map).

- [x] Explore Geospatial Literature <!-- id: 70 -->
    - [x] Search for GIS-based property valuation papers (geocoding, proximity, amenity scoring) <!-- id: 71 -->
    - [x] Review Google Maps API usage in real estate studies <!-- id: 72 -->
    - [x] Review OpenStreetMap usage in real estate / urban studies <!-- id: 73 -->
    - [x] Review spatial autocorrelation (Moran's I, spatial lag) in valuation <!-- id: 74 -->
    - [x] Compile findings for Ch2 §2.5 rewrite <!-- id: 75 -->
- [x] Update Manuscript for Post-Panel Pivot <!-- id: 46 -->
    - [x] Remove NLP/text features from Chapter 3 Methodology <!-- id: 47 -->
    - [x] Remove NLP RQ from Chapter 1 Research Questions <!-- id: 48 -->
    - [x] Strengthen GIS/geospatial section as primary contribution <!-- id: 49 -->
    - [x] Add precise Metro Cebu geographic definition (list of LGUs + map) <!-- id: 50 -->
    - [x] Clarify target variable justification (midpoint of floor–ceiling) <!-- id: 51 -->
    - [x] Add spatial autocorrelation / neighbor price effects discussion <!-- id: 52 -->
    - [x] Standardize terminology to "value drivers" throughout <!-- id: 53 -->
    - [x] Improve RRL: separate literature findings from thesis methodology <!-- id: 54 -->
    - [x] Emphasize Philippine-context novelty in Significance section <!-- id: 55 -->
    - [x] Replace Ch2 §2.5 (NLP) → §2.5 (Geospatial Feature Engineering) <!-- id: 76 -->
    - [x] Add QGIS interactive map as deliverable in Ch3 §3.8 <!-- id: 77 -->
    - [x] Frame thesis as predictive + prescriptive <!-- id: 78 -->
- [x] Update Empirical Framework <!-- id: 79 -->
    - [x] Replace NLP box → GIS/Geospatial Features box <!-- id: 80 -->
    - [x] Add QGIS Interactive Map as core output (not exploratory) <!-- id: 81 -->
    - [x] Add data pipeline flow (gathering → cleaning → GIS augmentation → modeling) <!-- id: 82 -->
    - [x] Update data source label (add Google Maps API, OSM) <!-- id: 83 -->
- [ ] Update Presentation Outline <!-- id: 56 -->
    - [ ] Remove Slide 17 (NLP & Text Data) <!-- id: 57 -->
    - [ ] Remove Text Features from Feature Categories table <!-- id: 58 -->
    - [ ] Update Research Objectives slide (remove NLP objective) <!-- id: 59 -->
    - [ ] Add QGIS interactive map as deliverable slide <!-- id: 60 -->
- [ ] Update LaTeX Chapters <!-- id: 61 -->
    - [ ] Sync chapter1.tex with revised objectives <!-- id: 62 -->
    - [ ] Sync chapter2.tex with revised RRL <!-- id: 63 -->
    - [ ] Sync chapter3.tex with revised methodology (GIS-centric) <!-- id: 64 -->
    - [ ] Update biblio.bib (remove NLP-only sources if unused) <!-- id: 65 -->

---

## GIS Roadmap (2026-03-01)

> Roadmap for the GIS/geospatial component — the core methodological contribution.
> See also: `roadmap_gis.md` for detailed milestones.

- [x] Setup GIS Python Environment (`thesis-gis` conda env) <!-- id: 84 -->
    - [x] Install geopandas, osmnx, folium, geopy, googlemaps <!-- id: 85 -->
    - [x] Configure Google Maps API key (secure `.env`) <!-- id: 86 -->
    - [x] Verify OSM query + Google geocoding on test addresses <!-- id: 87 -->
- [ ] Geocoding Pipeline <!-- id: 88 -->
    - [ ] Batch geocode BDO Cebu addresses via Google Maps API <!-- id: 89 -->
    - [ ] Batch geocode Lamudi addresses via Google Maps API <!-- id: 90 -->
    - [ ] Handle failed geocodes (manual fallback or Nominatim) <!-- id: 91 -->
    - [ ] Validate: spot-check 10% of geocoded coords on QGIS <!-- id: 92 -->
- [ ] Proximity Feature Engineering <!-- id: 93 -->
    - [ ] Define reference nodes (Ayala, IT Park, SM Seaside, Airport, CBRT stations) <!-- id: 94 -->
    - [ ] Compute Haversine distances for all geocoded properties <!-- id: 95 -->
    - [ ] EDA: plot distance distributions + correlation with price <!-- id: 96 -->
- [ ] OSM Amenity Scoring <!-- id: 97 -->
    - [ ] Query OSM via osmnx for POIs within 1 km of each property <!-- id: 98 -->
    - [ ] Categories: schools, hospitals, commercial, transit <!-- id: 99 -->
    - [ ] Compute amenity score (total count or weighted) <!-- id: 100 -->
    - [ ] EDA: amenity score vs. price scatterplot <!-- id: 101 -->
- [ ] Spatial Autocorrelation <!-- id: 102 -->
    - [ ] Compute spatial lag variable (mean price within 1–2 km) <!-- id: 103 -->
    - [ ] Compute Moran's I on OLS residuals <!-- id: 104 -->
    - [ ] Decision: incorporate spatial lag as feature or use SAR model <!-- id: 105 -->
- [ ] QGIS Interactive Map <!-- id: 106 -->
    - [ ] Export geocoded + predicted data as GeoPackage / GeoJSON <!-- id: 107 -->
    - [ ] Load into QGIS project <!-- id: 108 -->
    - [ ] Layer 1: Property points (color-coded by prediction error) <!-- id: 109 -->
    - [ ] Layer 2: Valuation Gap heatmap (Model vs. BIR Zonal) <!-- id: 110 -->
    - [ ] Layer 3: Proximity contours to economic nodes <!-- id: 111 -->
    - [ ] Layer 4: Amenity density overlay <!-- id: 112 -->
    - [ ] Style and export interactive HTML (qgis2web or folium fallback) <!-- id: 113 -->
