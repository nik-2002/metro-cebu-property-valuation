# Literature: Decision 20 — Spatial Sorting and Negative MCRAI Coefficients

> Purpose: Support the Chapter 3/4 interpretation that negative OLS coefficients for `mcrai_security`, `mcrai_tourism`, and `mcrai_retail_density` reflect spatial sorting artifacts rather than direct disamenity effects.
> Last updated: 2026-05-07
> Decision log: `modeling_decisions.md` Decision 20

---

## The Argument to Support

Three MCRAI categories returned negative OLS coefficients in the open_market hedonic model:
- `mcrai_security` (−0.093) — police stations, barangay halls, fire stations
- `mcrai_tourism` (−0.023) — resorts, hotels, lodging
- `mcrai_retail_density` (−0.007) — restaurants, cafes, convenience stores

The thesis argues these do **not** mean proximity to security/tourism/retail depresses prices causally. The correct framing is **spatial sorting**: public security infrastructure is placed where lower-income populations cluster (following Tiebout 1956); tourism corridors correlate with certain neighborhood types that are priced lower; and commercial density above a threshold imposes noise/congestion externalities that offset accessibility benefits.

The OLS model cannot disentangle these sorting effects from direct disamenity without neighborhood income controls, which are unavailable for this dataset.

---

## 1. Spatial Sorting — Theoretical and Empirical Basis

### Tiebout, C.M. (1956)
- "A Pure Theory of Local Expenditures." *Journal of Political Economy*, 64(5), 416–424.
- URL: https://ideas.repec.org/a/ucp/jpolec/v64y1956p416.html
- **Key finding:** Households self-select into jurisdictions based on preferred tax/service bundles, producing income-stratified neighborhood equilibria. Lower-income neighborhoods attract certain public facilities (including security infrastructure) not because those facilities raise property values, but because they are deployed where population need is highest. Foundational theoretical basis for interpreting negative security coefficients as sorting artifacts.
- **Verified:** Yes.

### Bayer, P. & McMillan, R. (2012)
- "Tiebout Sorting and Neighborhood Stratification." *Journal of Public Economics*, 96(11), 1129–1143.
- DOI: https://doi.org/10.1016/j.jpubeco.2012.02.006 | NBER WP: https://www.nber.org/papers/w17364
- **Key finding:** Empirically demonstrates using Census micro-data and an equilibrium sorting model that Tiebout sorting produces income stratification across neighborhoods — public good provision (including safety infrastructure) clusters where lower-income populations sort, not where high property values are located. Directly supports the spatial sorting interpretation of negative `mcrai_security` coefficients.
- **Verified:** Yes.

---

## 2. Police / Public Safety Facility Proximity — Nonlinear Price Effects

### Dronyk-Trosper, T. (2017)
- "Searching for Goldilocks: The Distance-Based Capitalization Effects of Local Public Services." *Real Estate Economics*, 45(3), 650–678.
- DOI: https://doi.org/10.1111/1540-6229.12171 | SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2489167
- **Key finding:** Uses over 3 million home sales in Florida to model capitalization effects of fire stations, police facilities, and EMS facilities on residential property values. Finds nonlinear effects — very close proximity to these facilities is associated with depressed prices (noise, traffic, institutional character of surroundings) while moderate distances capture the service-quality benefit. The "Goldilocks" framing directly supports a negative MCRAI coefficient for police/security facilities at residential scale.
- **Verified:** Yes.

### Brasington, D.M. & Parent, O. (2024)
- "Fire Protection Services and House Prices: A Regression Discontinuity Investigation." *Regional Science and Urban Economics*, 105.
- DOI: https://doi.org/10.1016/j.regsciurbeco.2024.103984
- **Key finding:** Using regression discontinuity around fire levy votes in Ohio, finds that public safety service quality (not physical proximity) is what gets capitalized into prices. Loss of fire protection reduces house values by ~6.7%. Supports framing security infrastructure as a service-delivery variable rather than a proximity amenity — explaining why physical nearness to a barangay hall or police substation does not generate a price premium.
- **Verified:** Yes.

---

## 3. Commercial / Retail Density — Threshold Disamenity Effect

### Yang, H.J., Song, J., & Choi, M.J. (2016)
- "Measuring the Externality Effects of Commercial Land Use on Residential Land Value: A Case Study of Seoul." *Sustainability*, 8(5), 432.
- DOI: https://doi.org/10.3390/su8050432 | URL: https://www.mdpi.com/2071-1050/8/5/432
- **Key finding:** Hedonic price model on 25,126 parcels in Seoul finds an inverted-U relationship between commercial land use concentration and residential land values. Higher commercial density initially raises values (accessibility/convenience) but depresses values beyond a threshold due to excessive noise, traffic, and crowding. Directly supports the interpretation that high local restaurant/cafe/retail density can become a net disamenity — explaining the negative `mcrai_retail_density` OLS coefficient.
- **Verified:** Yes.

### Song, Y. & Knaap, G.J. (2004)
- "Measuring the Effects of Mixed Land Uses on Housing Values." *Regional Science and Urban Economics*, 34(6), 663–680.
- DOI: https://doi.org/10.1016/j.regsciurbeco.2004.02.003 | ScienceDirect: https://www.sciencedirect.com/science/article/abs/pii/S016604620400016X
- **Key finding:** Hedonic study in the Portland, Oregon metro area. Finds that mixed land use effects on housing values depend heavily on land use type and distance — commercial proximity does not reliably predict positive price effects, and in some configurations produces null or negative coefficients. Supports the claim that retail density near residential properties is not a universal positive signal.
- **Verified:** Yes.

---

## 4. Tourism / Resort Proximity — Disamenity Effects

### Chen, W.Y. & Jim, C.Y. (2010)
- "Amenities and Disamenities: A Hedonic Analysis of the Heterogeneous Urban Landscape in Shenzhen (China)." *The Geographical Journal*, 176(3), 227–240.
- DOI: https://doi.org/10.1111/j.1475-4959.2010.00358.x
- **Key finding:** Examines apartment transactions in Shenzhen using hedonic methods. Finds that urban landscape elements produce both positive and negative capitalization depending on type — urban villages show clear disamenity effects (−3.72% for visibility). Demonstrates that proximity to large-scale non-residential land uses in Chinese cities can depress residential values. **Note:** This study covers urban villages and parks — NOT theme parks or resorts specifically. Use with care.
- **Verified:** Yes. But scope is limited — not a direct resort/hotel disamenity study.

### ⚠️ UNVERIFIED — "Shenzhen theme park study" (ResearchGate only)
The existing `Polycentric Urbanism_ Metro Cebu POI Analysis.md` file cites a Shenzhen hedonic study as reference 20:

> "The Impact of Tourism Resources on Tourism Real Estate Value"
> ResearchGate: https://www.researchgate.net/publication/283634356_The_Impact_of_Tourism_Resources_on_Tourism_Real_Estate_Value
> Accessed: April 23, 2026

The POI analysis file claims it found that "distance to theme parks and major resorts had a severe negative effect on price" in the Overseas Chinese Town (OCT) area of Shenzhen. **The ResearchGate URL exists but a journal name and DOI have not been confirmed.** A ResearchGate link alone is not citable. Do NOT use this in the manuscript until the actual journal publication and DOI are verified.

**Status as of 2026-05-07:** NOT confirmed. ResearchGate link identified but peer-review source unverified.

**To verify:** Open the ResearchGate URL above. If it resolves to a journal article with a DOI, record the full citation here. Search terms if URL fails: "tourism real estate value" "Shenzhen" hedonic; or "OCT" "theme park" "property values" China.

**Workaround for defense:** If this paper cannot be confirmed, use the Dronyk-Trosper (2017) nonlinear proximity argument as a stand-in: proximity to large commercial-tourism infrastructure depresses values through noise and congestion, consistent with the "Goldilocks" framing. This is defensible and independently verified.

---

## Chapter 3/4 Framing Guidance

**For `mcrai_security` (negative coefficient):**
> Cite Tiebout (1956) and Bayer & McMillan (2012) for the sorting mechanism. Cite Dronyk-Trosper (2017) for the empirical nonlinear proximity effect. Frame as: "The negative OLS coefficient for `mcrai_security` is consistent with spatial sorting — security infrastructure is more densely deployed in lower-price neighborhoods, reflecting population need rather than property value generation (Tiebout 1956; Bayer & McMillan 2012). Physical proximity to police substations and barangay halls is further associated with noise and institutional externalities that offset service benefits (Dronyk-Trosper 2017)."

**For `mcrai_retail_density` (negative coefficient):**
> Cite Yang et al. (2016) for the inverted-U threshold effect. Frame as: "Beyond a threshold, commercial food and retail density introduces noise, traffic, and crowding externalities that depress residential values — consistent with findings from Seoul's urban commercial land use literature (Yang et al. 2016). The negative coefficient likely reflects over-concentration of commercial activity near residential properties in high-density barangays."

**For `mcrai_tourism` (negative coefficient):**
> Frame as externality effect from resort/hotel corridor proximity — consistent with tourism literature showing noise, transient populations, and commercialization as residential disamenities. Cite Chen & Jim (2010) with the caveat that direct resort evidence is from developing-city hedonic literature broadly. Acknowledge this is the weakest of the three literature bases — verify the Shenzhen theme park citation before submission.

---

## Status Summary

| Claim | Literature basis | Status |
|---|---|---|
| Security: spatial sorting mechanism | Tiebout (1956), Bayer & McMillan (2012) | ✅ Verified |
| Security: nonlinear proximity disamenity | Dronyk-Trosper (2017) | ✅ Verified |
| Security: service quality vs. proximity | Brasington & Parent (2024) | ✅ Verified |
| Retail: threshold commercial disamenity | Yang et al. (2016), Song & Knaap (2004) | ✅ Verified |
| Tourism: resort/hotel proximity externality | Chen & Jim (2010) — limited scope | ⚠️ Partial |
| Tourism: Shenzhen theme park specifically | Not found | ❌ Unverified — do not cite |
