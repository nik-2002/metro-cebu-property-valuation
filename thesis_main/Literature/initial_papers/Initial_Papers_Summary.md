# Initial Papers Summary (Topic Proposal Phase)

> **Context**: These papers were compiled during the thesis topic proposal phase (2025) and uploaded to the NotebookLM notebook "Data-Driven Real Estate Valuation: The Cebu Model"

---

## Overview

| #   | Paper                                     | Focus Area          | Key Contribution to Thesis                        |
| --- | ----------------------------------------- | ------------------- | ------------------------------------------------- |
| 1   | Determinants of Land Values in Cebu City  | **Cebu-specific**   | Primary local reference for feature selection     |
| 2   | Domingo & Fulleros REPI Model             | Philippine Index    | Documents REPI framework and zonal value gaps     |
| 3   | Spatial Segmentation from Online Listings | Methodology         | Validates using web listings for valuation        |
| 4   | Gayathri Thekkayil (JISEM)                | ML Valuation        | Supports Random Forest/XGBoost approach           |
| 5   | Macroeconomic Determinants Research       | Macro Context       | Links inflation/interest rates to property prices |
| 6   | PIDS Discussion Paper (pids-dps2004-49)   | Philippine Context  | Early PH housing market analysis                  |
| 7   | TPS 2023 Paper                            | Statistical Methods | Time series and spatial modeling techniques       |
| 8   | 2012.09115v1 (Nightlights/Satellite)      | Proxy Data          | Using remote sensing for data-scarce regions      |

---

## Detailed Summaries

### 1. Determinants of Land Values in Cebu City
**Author**: Augusto B. Agosto (2017, 2020)  
**Type**: Conference Paper / Local Study

#### Key Findings
- **Accessibility** is the strongest driver — distance to CBD, ports, airports
- **Infrastructure projects** (BRT, expressways) elevate values along corridors
- **Physical attributes**: lot area, shape, frontage, slope affect price
- **Risk factors**: flooding, landslides significantly reduce value
- **Neighborhood quality**: schools, hospitals, retail raise desirability

#### Methodology
- Survey of 52 real estate practitioners
- Factor analysis + Principal Component Analysis
- Multiple regression (SPSS)

#### 31 Determinants Grouped Into:
1. **Mobility**: Transport access, road network
2. **Livability**: Open spaces, parks, environment
3. **Economic**: Employment access, rental potential
4. **Government**: Zoning, assessments, taxation
5. **Ownership**: Title security, legal clarity

#### Thesis Application
> **Primary source for feature selection** — directly informs which variables to include (distance to CBD, amenity scores, flood risk)

---

### 2. Domingo & Fulleros REPI Model (BIS Papers, 2005)
**Authors**: Estrella V. Domingo, Reynaldo F. Fulleros  
**Publication**: BIS Papers No. 21

#### Key Findings
- Philippines historically lacked unified real estate price index
- **BIR zonal values are outdated** — lag behind market prices
- Multiple valuation systems across agencies create inconsistency
- Proposed REPI framework to track real property prices over time

#### Thesis Application
> Supports the "Valuation Gap" concept — documents systematic disconnect between administrative and market values that the thesis aims to quantify

---

### 3. Spatial Segmentation from Online Listings
**File**: `Exploring_spatial_segmentation_housing_markets_online_listings_14May'24.pdf`

#### Key Findings
- Web-scraped listing data can effectively segment housing markets
- Online listings provide real-time "asking price" data
- Spatial clustering reveals distinct micro-markets within cities

#### Methodology
- Large-scale web scraping of property portals
- Spatial analysis techniques

#### Thesis Application
> Validates hybrid data strategy — using Lamudi/DotProperty listings as "ceiling price" proxy alongside BDO foreclosures as "floor price"

---

### 4. Gayathri Thekkayil (JISEM Paper)
**File**: `JISEM_5_GAYATHRI+THEKKAYIL_4_3666.pdf`

#### Key Findings
- Machine learning models outperform traditional regression for property valuation
- Tree-based methods (Random Forest, XGBoost) handle non-linear relationships
- Feature importance analysis reveals key value drivers

#### Thesis Application
> Methodological support for choosing RF/XGBoost over simple linear regression

---

### 5. Macroeconomic Determinants Research
**File**: `MacroeconomicDeterminantsResearch.pdf`

#### Key Findings
- **Interest rates** negatively impact housing prices (higher rates = lower demand)
- **Inflation** affects affordability and buyer budgets
- **Remittances** (OFW inflows) drive demand in Philippine housing
- **Exchange rates** influence foreign investment in real estate

#### Thesis Application
> Justifies including macro controls (BSP RPPI, interest rate trends) as features; explains Cebu's sensitivity to OFW remittance cycles

---

### 6. PIDS Discussion Paper (pids-dps2004-49)
**Source**: Philippine Institute for Development Studies

#### Key Findings
- Early analysis of Philippine housing market dynamics
- Documents historical gaps in property data infrastructure
- Discusses regional disparities in real estate development

#### Thesis Application
> Historical context — shows that data scarcity in PH property markets is a documented, long-standing problem

---

### 7. TPS 2023 Paper (tps_2023_72_1_1)
**Focus**: Statistical/Econometric Methods

#### Key Findings
- Techniques for handling time-series property data
- Spatial econometric approaches for location effects
- Methods for dealing with heterogeneous submarkets

#### Thesis Application
> Informs modeling decisions — supports use of barangay/corridor fixed effects and time-aware validation splits

---

### 8. Nightlights/Satellite Paper (2012.09115v1)
**Focus**: Remote Sensing for Economic Proxy

#### Key Findings
- Nighttime lights (luminosity) strongly proxy economic activity
- Satellite imagery can fill data gaps in developing nations
- High spatial resolution captures local variations

#### Thesis Application
> Future feature expansion — potential to incorporate satellite-derived building footprints or luminosity scores for neighborhoods with poor official data

---

## BDO Foreclosure Data Files (Reference Data)
The following files in this folder are **data sources**, not papers:

| File                                               | Description                          | Use                          |
| -------------------------------------------------- | ------------------------------------ | ---------------------------- |
| `METRO-MANILA-as-of-October-29-2025.pdf`           | BDO foreclosed properties (NCR)      | Comparison benchmark         |
| `LUZON-as-of-October-29-2025.pdf`                  | BDO foreclosed properties (Luzon)    | Regional context             |
| `VISAYAS-as-of-October-29-2025.pdf`                | BDO foreclosed properties (Visayas)  | **Primary Cebu data**        |
| `MINDANAO-as-of-October-29-2025.pdf`               | BDO foreclosed properties (Mindanao) | Regional context             |
| `SUBDIVISION-PROPERTIES-as-of-October-29-2025.pdf` | Subdivision-specific listings        | Subdivision feature encoding |
| `FORT-VICTORIA-BGC.pdf`                            | Specific development reference       | Comparables outside Cebu     |

---

## Synthesis: How Initial Papers Map to Thesis

```
┌─────────────────────────────────────────────────────────────────┐
│                    THESIS FRAMEWORK                             │
├────────────────┬────────────────┬────────────────┬─────────────┤
│   PROBLEM      │   METHODOLOGY  │   FEATURES     │   CONTEXT   │
├────────────────┼────────────────┼────────────────┼─────────────┤
│ Domingo REPI   │ Gayathri ML    │ Agosto Cebu    │ PIDS 2004   │
│ (zonal gaps)   │ (RF/XGBoost)   │ (31 factors)   │ (PH market) │
│                │                │                │             │
│                │ Spatial Seg.   │ Macro Research │ TPS 2023    │
│                │ (online data)  │ (inflation/FX) │ (methods)   │
│                │                │                │             │
│                │ Nightlights    │                │             │
│                │ (satellite)    │                │             │
└────────────────┴────────────────┴────────────────┴─────────────┘
```

---

## Key Takeaways for RRL Presentation

1. **The Agosto paper is your anchor** — only Cebu-specific empirical study on land value determinants
2. **Domingo & Fulleros documents the institutional problem** — zonal values lagging market
3. **ML papers justify methodology shift** — tree-based models outperform hedonic on heterogeneous data
4. **Macro research connects to BSP RPPI** — explains why national indices matter for local valuation

---

*Generated: 2026-02-05 | Source: NotebookLM Notebook "Data-Driven Real Estate Valuation: The Cebu Model"*
