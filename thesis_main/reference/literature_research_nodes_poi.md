# Literature Research: CBD Node Selection and POI Expansion
> Purpose: Research brief for Gemini Deep Research and NotebookLM
> Date: 2026-04-22
> Feeds into: Decision 5 (CBD node selection) and proposed Decision 8 (expanded POI categories)
> Canonical decisions log: `thesis_main/reference/modeling_decisions.md`

---

## Context for the Researcher

This thesis builds a residential property valuation model for Metro Cebu (6 LGUs: Cebu City, Mandaue City, Lapu-Lapu City, Talisay City, Minglanilla, Consolacion) using a hybrid dataset of ~1,110 listings. The model uses proximity features (distance to nodes) and Hansen gravity accessibility scores as geospatial inputs.

Two open questions need literature grounding:

1. **Which urban nodes should be included as distance features?** — specifically whether Metro Cebu supports a polycentric model with multiple distinct subcenters, and whether Naga City (just outside the study area) should still be included as an influence node.

2. **Should tourism and lifestyle POIs be added as Hansen score categories?** — beach resorts, hotels, parks, convenience stores, gasoline stations, and similar non-traditional amenity types that may affect residential values in Cebu's coastal municipalities.

---

## Part 1: CBD Node Selection — Polycentric Urbanism

### Research Questions for Gemini

**Prompt 1 — Theoretical basis for polycentric distance features:**
> "I am building a hedonic price model for residential properties in Metro Cebu, Philippines. I currently include distance-to-node features for the following locations: Cebu Business Park, IT Park, Mandaue CBD, Mactan CBD, South Road Properties (SM Seaside), Talisay Tabunok, Minglanilla Poblacion, and Naga City. Using polycentric urbanism theory (Giuliano & Small 1991; McMillen 2003; Anas, Arnott & Small 1998), what criteria should I use to justify each of these as a distinct subcenter? Which of these would likely fail the subcenter test and which would clearly qualify? Please be specific about the criteria."

**Prompt 2 — Metro Cebu urban structure:**
> "Is there academic literature, government planning documents (NEDA, HLURB, DHSUD), or urban economics research that describes Metro Cebu as a polycentric urban region? Specifically: are there sources that identify Mandaue, Mactan/Lapu-Lapu, South Road Properties, and Talisay as distinct employment or commercial subcenters separate from the Cebu City CBD? Please cite specific documents or studies if possible."

**Prompt 3 — Naga City as a boundary subcenter:**
> "In polycentric urban economics, can a commercial or industrial node located just outside a study area's boundary still exert measurable influence on property values inside the boundary? I am studying Metro Cebu (6 LGUs) but Naga City — a large municipality with significant industrial and commercial activity immediately to the south — is excluded. Should I include distance-to-Naga-City as a feature for properties in Talisay and Minglanilla? What does the literature say about cross-boundary subcenter effects in hedonic models?"

**Prompt 4 — Heikkila et al. and CBD distance significance:**
> "Heikkila et al. (1989) argued that in polycentric cities, distance to the CBD can become statistically insignificant compared to distance to the nearest subcenter. Is this finding applicable to mid-sized Southeast Asian cities like Cebu? What does more recent literature say about whether monocentric or polycentric distance structures better explain residential prices in developing-country cities?"

**Prompt 5 — Philippine-specific urban polycentrism:**
> "Is there literature on polycentric urban structure in Philippine cities, particularly secondary cities outside Metro Manila? Can findings from Metro Manila polycentric studies be applied to Metro Cebu? Are there any PSA, NEDA, or academic studies that describe Cebu's urban spatial structure in terms of multiple commercial or employment centers?"

---

### Key Sources to Verify and Locate

| Source | What to confirm |
|---|---|
| Giuliano & Small (1991) | Subcenter identification criteria — employment density + total employment thresholds |
| McMillen (2003) | Nonparametric subcenter identification; "bumpy" distance gradient argument |
| Anas, Arnott & Small (1998) | Monocentric → polycentric → dispersed urban evolution framework |
| Heikkila et al. (1989) | CBD distance becoming insignificant in polycentric residential markets |
| Ballesteros (2002) — PIDS | Philippine housing market institutional context |
| NEDA Region 7 Development Plan | Does it identify Naga City or South Cebu as a growth corridor? |
| HLURB / DHSUD Metro Cebu CLUP | Are Mandaue, Mactan, SRP, Talisay named as distinct planning nodes? |
| Agosto (2017) | Does it identify specific geographic nodes beyond "transport accessibility"? |

---

### Node Defensibility Summary (Current Assessment)

| Node | Variable | Theoretical basis | Status |
|---|---|---|---|
| Cebu Business Park | `dist_cebu_business_park_m` | Primary CBD — unambiguous | Keep |
| IT Park | `dist_it_park_m` | Employment subcenter, r=0.99 with CBP | Likely drop — literature may not distinguish from CBP |
| Mandaue CBD | `dist_mandaue_cbd_m` | Northern industrial/commercial node | Keep if literature supports |
| Mactan CBD / Lapu-Lapu | `dist_mactan_cbd_m` | Island commercial + aerotropolis | Keep — geometrically and economically distinct |
| South Road Properties | `dist_srp_m` | Waterfront planned commercial district | Pending — is SRP distinct from Talisay? |
| Talisay Tabunok | `dist_talisay_tabunok_m` | Southern commercial hub | Keep if supported as distinct node |
| Minglanilla Poblacion | `dist_minglanilla_poblacion_m` | Small town center, within scope | Borderline |
| Naga City | `dist_naga_city_m` | Outside scope but southern anchor | Pending — cross-boundary influence argument needed |
| Airport | `dist_airport_m` | Aerotropolis effect, unique signal | Keep |
| Consolacion | `dist_consolacion_m` | Northern peripheral node | Keep — strongest price correlation (-0.162) |

---

## Part 2: Expanded POI Categories — Tourism and Lifestyle Nodes

### The Proposal

Beyond the 6 current Hansen score categories (education, health, finance, grocery, transport, security), add tourism and lifestyle POIs that are economically meaningful in Metro Cebu's specific context — particularly for coastal municipalities.

**Proposed additional categories:**

| Category | POI types | Relevant LGUs | Hypothesis |
|---|---|---|---|
| Beach resorts | Beach resorts, dive shops, water sports | Lapu-Lapu, Talisay, Minglanilla | Proximity increases value for leisure buyers; may decrease for families |
| Hotels and hospitality | Hotels, boutique hotels, serviced apartments | Lapu-Lapu, Cebu City | Proximity signals tourist-accessible area; may indicate commercial noise |
| Parks and green space | Public parks, nature reserves, plazas | All 6 LGUs | Standard positive amenity effect |
| Convenience stores | 7-Eleven, Alfamart, Ministop | All 6 LGUs | Proxy for urban density and walkability |
| Gasoline stations | Petron, Shell, Caltex | All 6 LGUs | Proxy for road corridor accessibility |

### Research Questions for Gemini

**Prompt 6 — Tourism proximity and residential values:**
> "In hedonic pricing models, does proximity to beach resorts, hotels, or tourism infrastructure affect residential property values? I am studying coastal municipalities in Metro Cebu (Lapu-Lapu City, Talisay, Minglanilla) where beach resorts are a significant land use. Is the effect on nearby residential prices positive (amenity value), negative (noise/traffic externality), or mixed depending on property type? Please cite studies from Southeast Asia or similar coastal urban contexts if possible."

**Prompt 7 — Convenience stores and gasoline stations as accessibility proxies:**
> "Are convenience store density or gasoline station proximity used as proxy variables for urban accessibility or neighborhood commercial maturity in hedonic price models? Is there literature that validates these as useful features in residential price prediction, particularly in developing-country or Philippine urban contexts?"

**Prompt 8 — Green space and park proximity:**
> "What does the hedonic pricing literature say about proximity to parks and green space in urban residential markets? Is the effect consistent across property types (condominiums vs. single-detached houses vs. vacant lots)? Are there Southeast Asian or Philippine studies on this?"

**Prompt 9 — POI category selection for Hansen gravity models:**
> "I am computing Hansen gravity accessibility scores for residential properties in Metro Cebu. My current 6 categories are education, health, finance, grocery, transport, and security. I am considering adding beach resorts, hotels, parks, convenience stores, and gasoline stations. What criteria should I use to decide which POI categories to include in a Hansen accessibility model? How do researchers typically justify the inclusion or exclusion of specific POI types in accessibility-based hedonic models?"

---

### Implementation Notes (for Copilot after literature is confirmed)

- Additional Hansen categories use the same `compute_hansen_scores.py` framework — new categories just need a new POI list from Google Maps Places API and a category weight
- Weights for new categories need literature justification or sensitivity testing
- Beach resort proximity may need a **signed** or **nonlinear** effect (positive up to a threshold, then negative) — standard Hansen scoring won't capture this; flag for modeling stage
- Convenience stores and gasoline stations are dense enough in urban areas that the 5km radius may be too large — consider a tighter 1–2km radius for these categories

---

## What to Bring Back

After Gemini Deep Research, bring findings here to close:
- Decision 5: which CBD nodes to keep or drop
- Decision 8 (proposed): which additional POI categories to add to Hansen scoring
- Any new literature entries to add to `biblio.bib`
