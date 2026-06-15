# AVM Accuracy Benchmarks — External Reference Points (2026-06-13)

> Purpose: ground the thesis models against industry/academic AVM benchmarks so Chapter 7
> can say "comparable systems achieve X" with real sources. Honest positioning: our model is
> a decision-support prototype on sparse *listing* data, not an assessment-grade AVM on
> transaction data. Verify primary sources (marked ⚠) before final citation.

## Our models (leak-free GroupKFold, recap)

| Stratum | MdAPE | MAPE | PE10 | PE20 | COD | PRD |
|---|---:|---:|---:|---:|---:|---:|
| Condominium | 20.1% | 35.2% | 26.9% | 49.8% | 36.3 | 1.21 |
| Houses | 22.1% | 32.4% | 23.7% | 45.0% | 33.0 | 1.18 |
| Vacant Lot | 25.6% | 37.8% | 24.3% | 41.6% | 36.9 | 1.28 |

## Benchmark landscape

| Benchmark | Typical accuracy | What it's built on | Source / status |
|---|---|---|---|
| **IAAO Ratio Study (2013)** | COD residential **5–15**; PRD **0.98–1.03** | assessor sale-ratio studies | established; already in project manifest |
| **IAAO Standard on AVMs (2003)** | commonly cited acceptance: **MAPE ~13%, ~50% within ±10%, ~65% within ±15%, ~80% within ±20%, FSD <19%, COD <13** | pooled AVM test sets | ⚠ confirm exact thresholds in the primary PDF (couldn't machine-read it) |
| **Zillow Zestimate (2025)** | median error **1.74% on-market, 7.20% off-market** (US nationwide) | millions of transactions, rich features | Zillow published figures (via secondary sources) |
| **Academic ML (transaction data)** | MAPE **~7–10%** (XGBoost/LightGBM); Hong Kong RF **MAPE 9.33%, R² 0.89** on ~40,000 sales | large clean transaction datasets, mature markets | published studies (illustrative range) |

## Where we stand — honest reading

Against the commercial/academic benchmarks our absolute accuracy is **clearly lower**:
- PE20 **42–50%** vs an AVM-grade ~80%; MAPE **32–38%** vs ~13% (IAAO) / 7–10% (academic);
  median error **20–26%** vs Zillow off-market 7.2%; COD **33–37** vs <13–15.
- So we **cannot** claim AVM-grade or assessment-grade accuracy. (Already the project's stated position.)

**Why that is expected and defensible — the apples-to-oranges caveats:**
1. **Listings, not sales.** We train on *asking prices* (no public deed-of-sale access in PH), which carry seller-strategy noise the benchmarks don't.
2. **Sample size.** ~255–687 rows per stratum vs millions (Zillow) / tens of thousands (academic).
3. **Feature poverty.** No interior finish, condition, view, or quality fields that mature AVMs use.
4. **Market maturity / data infrastructure.** Metro Cebu lacks the transaction registries and dense comparable sales these benchmarks rely on — which is the thesis's whole premise (the data-sparsity gap).
5. **Honest evaluation — but only a small slice of the gap.** Leak-free GroupKFold gives pessimistic but trustworthy numbers; some benchmarks use optimistic random splits. **Measured (`ramolete_replication_2026-06-14.md`):** re-running our models under a random 80/20 split improves RF MAPE by only **2–5pp** (most for condos). So evaluation rigor explains a *few points*, not the bulk of the distance to commercial/academic AVMs — that distance is mostly points 1–4 (listings, small n, feature poverty, thin market). Do not over-attribute the gap to "honesty."

## The defensible claim (use this, don't overclaim)

> The models are not assessment-grade by IAAO standards and do not match transaction-based
> commercial AVMs — which is expected given sparse, listing-based data in a market without
> public sale records. As a **decision-support prototype**, they materially out-perform the
> two references Metro Cebu actually relies on — the **hedonic OLS baseline** and the **BIR
> zonal benchmark** — under honest leak-free evaluation. The contribution is a first
> Cebu-specific, GIS-augmented valuation model where no AVM previously existed, not a claim
> of parity with mature-market systems.

## Verification TODO before final manuscript
- ⚠ Confirm IAAO AVM acceptance thresholds (MAPE 13% / PE 50-65-80 / FSD 19% / COD 13) against the primary IAAO Standard on AVMs.
- Pull the exact citation + year for the Hong Kong RF study and one SE-Asian ML hedonic study (verify DOI; do not cite from search summary).
- Confirm Zillow's current published median-error figures from zillow.com/zestimate.

## Sources consulted
- Zillow accuracy (secondary): https://listwithclever.com/real-estate-blog/how-accurate-is-a-zillow-zestimate-5-things-to-know/ ; https://www.zillow.com/zestimate/
- IAAO Standard on AVMs (primary, verify): https://www.iaao.org/wp-content/uploads/Standard_on_Automated_Valuation_Models.pdf
- AVM performance metrics: https://www.tandfonline.com/doi/full/10.1080/15214842.2020.1757352 ; https://www.prres.org/uploads/780/1665/Rossini_Automated_Valuation_Model_Accuracy_Some_Empirical_Testing.pdf
- ML property valuation: https://www.tandfonline.com/doi/full/10.1080/09599916.2020.1832558 ; https://arxiv.org/pdf/2110.07151
