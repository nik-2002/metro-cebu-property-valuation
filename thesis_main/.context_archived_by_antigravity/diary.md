# Project Diary

## 2026-03-02
- **Official Panel Feedback Received**: Consolidated comments from adviser + panel members. 12 items total. Mapping below:

| #   | Feedback                                                                  | Status         | Notes                                                                              |
| --- | ------------------------------------------------------------------------- | -------------- | ---------------------------------------------------------------------------------- |
| 1   | No need for NLP on extracting features                                    | ✅ Done (Mar 1) | All NLP purged from Ch1-3                                                          |
| 2   | Have a clearer RRL presentation                                           | ⬜ Needs work   | Ch2 rewritten but RRL *presentation slides* not yet updated                        |
| 3   | Define property, Metro Cebu                                               | ✅ Done (Mar 1) | 6 LGUs defined; "Residential" scope stated                                         |
| 4   | More details on choice of problem and model selection                     | ⬜ NEW          | Need to expand Ch1/Ch3 justification for OLS/RF/XGBoost + why this problem matters |
| 5   | Show sample data structures you will be working on                        | ⬜ NEW          | Need sample tables in Ch3 showing raw vs. cleaned data schema                      |
| 6   | So many data structures considered; data processing is challenging        | ⬜ NEW          | Acknowledge complexity; justify each source's inclusion                            |
| 7   | Include what you envision for preprocessing                               | ⬜ NEW          | Per-source preprocessing details (regex, geocoding, imputation, etc.)              |
| 8   | Include creation of tangible web map and dashboard                        | ✅ Partial      | QGIS map + Streamlit in Ch3 §3.8, but need to make more concrete/tangible          |
| 9   | Focus on methodologies to add value drivers (schools, hospitals, transit) | ✅ Partial      | §3.4.1 covers pipeline, but needs more methodological depth                        |
| 10  | Come up with your own model for value drivers                             | ⬜ NEW          | Panel wants a novel/custom value driver scoring model, not just standard features  |
| 11  | Add more RRL                                                              | ⬜ NEW          | Need additional literature sources, especially GIS+ML in SE Asia                   |
| 12  | Coordinate with adviser                                                   | ⬜ Action item  | Schedule meeting with adviser                                                      |

## 2026-03-01
- **Manuscript Revisions Complete (Ch1–3)**: Full post-panel revision of all three chapters. All NLP/text feature references purged (verified: 0 grep hits). GIS/geocoding elevated as core contribution throughout.
- **Chapter 2 Rewrite**: §2.5 replaced entirely — from NLP/Text Feature Extraction → **Geospatial Feature Engineering in Property Valuation**. New subsections: Geocoding (Google Maps API), Proximity Analysis (Haversine), Amenity Scoring (OSM/osmnx), Spatial Autocorrelation (Moran's I, Spatial Lag). §2.8 synthesis updated with GIS-centric gap statement.
- **Chapter 3 Rewrite**: Removed all NLP pipeline steps. Added §3.2.4 (Geospatial Data Sources), §3.2.5 (Target Variable clarification), §3.4.1 (Geospatial Feature Engineering pipeline). Updated hedonic equation (`AmenityScore` + `SpatialLag` replace `TextFeatures`). **QGIS Interactive Map** elevated to §3.8.1 (Primary Deliverable).
- **Chapter 1 Revised**: Removed NLP research question. Added RQ3 (geospatial features). Defined Metro Cebu (6 LGUs: Cebu City, Mandaue, Lapu-Lapu, Talisay, Minglanilla, Consolacion). Emphasized Philippine-context novelty. Framed thesis as predictive + prescriptive.
- **Empirical Framework Updated**: `EmpiricalFramework.drawio` rebuilt — NLP box → GIS/Geospatial Features (CORE), QGIS Interactive Map as core prescriptive output, data pipeline flow added, Google Maps API + OSM as data sources. User manually adjusted positions in draw.io editor.
- **Terminology Standardized**: "value drivers" used consistently (11 occurrences across manuscript).
- **GIS Roadmap Created**: `roadmap_gis.md` — 5 phases: Geocoding → Proximity → OSM Amenity → Spatial Autocorrelation → QGIS Map. Target: features by Mar 14, map by Apr 18.
- **Panel Feedback 10/10 Addressed**: All items from Feb 26 panel feedback verified as incorporated.
- **Remaining**: LaTeX sync, presentation outline update.

## 2026-02-26
- **Thesis Proposal Panel Q&A Completed**: Presented to panel; received approval pending revisions. Full transcript saved to `Presentations/topic_proposal_presentation/Thesis Proposal.txt`. Key points extracted to `Panel_QA_Notes.md`.
- **MAJOR PIVOT — NLP Removed, GIS/Geocoding Focus**: Per panel feedback and strategic decision, **NLP feature extraction (TF-IDF, BERT, Word2Vec) is removed** from the thesis scope. The core methodological contribution is now **GIS/geospatial feature engineering**: geocoding, Haversine proximity, OSM amenity scoring, building density, and spatial autocorrelation.
- **Panel Key Feedback**:
  - Define "Metro Cebu" precisely (list of LGUs + map).
  - Clarify target variable (midpoint of floor–ceiling price range).
  - GIS/spatial augmentation is the **crux** of the thesis work.
  - **Interactive QGIS map** required as a deliverable (Sir Randy's requirement).
  - **Diversify floor price sources**: Don't rely solely on BDO foreclosures — add Pag-IBIG, PNB, RCBC, Union Bank, SSS/GSIS acquired assets to prevent single-source bias.
  - Address **spatial autocorrelation** (neighbor price effects).
  - **SHAP explainability** is non-negotiable (IVS 2025 compliance).
  - Standardize terminology to **"value drivers"**.
  - RRL needs clearer separation between literature findings vs. thesis methodology.
  - Philippine-context novelty is a strength — emphasize it.
- **Roadmap Impact**: `roadmap_llm_embeddings.md` → **DEFERRED/OUT OF SCOPE**. `roadmap_bayesian_layer.md` → remains exploratory (not affected by panel).

## 2026-02-13
- **Methodology Solidification**: Addressed professor feedback on Agosto exclusivity claim. Web research found additional Cebu studies (Sajor 2003, informal land market, RPT revision) but none apply predictive ML to transaction data. Reframed gap claim.
- **NLP Text Features → Core**: Promoted text feature extraction from exploratory to core methodology. Literature supports 10-44% improvement (Ottawa Word2Vec, Melbourne SBERT, Seattle BERT, Shanghai ChatGPT). Approach: TF-IDF baseline → BERT → Word2Vec if data permits.
- **Methodology Brainstorm Doc Created**: `Presentations/methodology_presentation/methodology_brainstorm.md` — comprehensive working document for presentation prep.
- **Decisions Logged**: 3-model comparison (core), hybrid data (core), SHAP (core), BIR integration (core), text features (core), Bayesian layer (exploratory).

## 2026-02-04
- **Literature Summary Generation Complete**: Generated detailed markdown summaries for all 44 sources in the NotebookLM thesis notebook. Used hybrid approach: NotebookLM MCP queries for raw data extraction, then structured synthesis.
- **Claude Opus Audit**: Cross-verified 8 key quantitative claims against NotebookLM source data—all confirmed accurate (no hallucinations detected).
- **Folder Reorganization**: Organized summaries into quality tiers:
  - `Tier_A_High_Quality/` (11 sources): Rigorous, quantitative, thesis-relevant
  - `Tier_B_Context/` (29 sources): Background/methodological context
  - `Unusable/` (4 sources): Restricted/missing content (6, 31, 42, 44)
- **Tier A Enhancement (3 Phases)**:
  - Phase 1: Deep rewrites for Sources 36, 38, 40 (1.3-1.8KB → 4.7-6.1KB)
  - Phase 2: Methodology enhancement for Sources 20, 29, 32 (2.5-2.7KB → 5.0-5.2KB)
  - Phase 3: Spot-checks verified Sources 01, 02, 05, 08, 13 (already complete)
- **Key Findings**: IVS 2025 requires "professional judgement" for AVM compliance; SNN outperforms CNN on small datasets (73% vs 39%); Exchange rate (-0.925) stronger predictor than inflation (-0.508) in Nigeria; Yale optimal weight θ*=30% for Grade D countries.


## 2026-01-27
- **NotebookLM MCP Server Setup**: Installed and configured the NotebookLM MCP server for Antigravity. Server now connects to 34 notebooks. Auth tokens stored in `~/.notebooklm-mcp/auth.json`.
- Consolidated all context tracking to this `.context/` folder instead of Antigravity's default location.

