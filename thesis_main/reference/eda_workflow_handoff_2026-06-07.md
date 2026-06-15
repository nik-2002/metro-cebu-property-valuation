# EDA and Workflow Handoff - 2026-06-07

> Purpose: Plain-language handoff for the next Claude/session. This file backtracks the recent EDA, scrape, cleanup, and modeling decisions so the project does not drift back to older global-model assumptions.

---

## Current Bottom Line

The current modeling direction is defensible, but the documentation and EDA artifacts are behind the latest dataset.

The active workflow is no longer the old single global Random Forest / total-price / random held-out split. The active workflow is:

1. Build a clean open-market residential ABT from Lamudi-derived listings.
2. Recompute canonical location features after each data refresh.
3. Split into three strata: Condo, Houses, Vacant Lot.
4. Model `log(price_per_sqm)` per stratum.
5. Back-transform predictions to `price_per_sqm`; total estimated price is `price_per_sqm * area_sqm`.
6. Deploy Random Forest per stratum.
7. Evaluate with GroupKFold by coordinate cluster so repeated/shared-coordinate listings do not leak across train/test folds.

Current source of truth:
- `thesis_main/Scripts/prepare_stratified_abt.py`
- `thesis_main/Scripts/finalize_stratified_groupcv.py`
- `thesis_main/Models/stratified/deployment_manifest.json`
- `thesis_main/reference/modeling_decisions.md` Decisions 42 and 43

---

## What Happened With The New Scrape

The older scraper was a normal HTML/requests-style pipeline. Lamudi later blocked that style through a browser/JavaScript challenge, so Playwright was introduced to behave like a real browser.

The Playwright batch did not add thousands of usable rows. The useful funnel was:

| Stage | Rows |
|---|---:|
| Scraped/listed candidates | 665 |
| With coordinates | 654 |
| Valid price range | 600 |
| Inside six target LGUs | 560 |
| Residential recode retained | 533 |
| After spatial cap | 400 |
| Net staged rows after dedup against ABT | 275 |

After merge and enrichment, the master `abt_clean.csv` became 1,849 data rows. The current modeling stratum files are:

| Stratum CSV | Data rows |
|---|---:|
| `abt_condo.csv` | 687 |
| `abt_houses.csv` | 674 |
| `abt_lot.csv` | 255 |

Important: the saved structured EDA log in `thesis_main/EDA/plots/eda_stratified_v2_run.log` is stale because it used earlier counts: Condo 654, Houses 558, Lot 204. Rerun EDA before using the plots/tables as final thesis evidence.

---

## EDA Issues And Whether They Were Addressed

| EDA issue | What it means in plain language | Workflow response | Current status |
|---|---|---|---|
| Skewed prices | Some listings are much more expensive than the typical row, so raw prices are not well behaved. | Model `log(price_per_sqm)` instead of raw total price. Back-transform for reporting/app output. | Addressed in stratum CSVs and manifest. |
| Heteroscedasticity | OLS errors get wider/narrower across price levels; normal OLS standard errors are unreliable. | Use HC3 robust standard errors in OLS diagnostics. Do not use OLS as the deployed model. | Addressed for diagnostics; not a Random Forest blocker. |
| Residual non-normality | OLS residuals are not perfectly normal, common in listing data. | Keep OLS as diagnostic only; rely on tree models for deployment. | Addressed by not overclaiming OLS inference. |
| Collinearity / high VIF | Some location/MCRAI variables overlap strongly, so OLS coefficients can become unstable. | Use a trimmed OLS diagnostic spec; keep full feature set in Random Forest where correlated predictors are less destabilizing. | Mostly addressed, but the final EDA should reprint VIF on current rows. |
| MCRAI overlap with CBD distance | Amenity access and CBD proximity measure related spatial effects. | Interpret MCRAI as a local accessibility block, not as the dominant driver. Do not overclaim MCRAI. | Addressed narratively; needs clear Chapter 4/7 wording. |
| Duplicate listings | Same or near-same listing can inflate support for a location/price. | Drop hard duplicates in `prepare_stratified_abt.py` using identical coordinates, area, and price per sqm. | Addressed. |
| Shared coordinates / geocoding clusters | Multiple listings can share a barangay-centroid or same pin. Random splitting leaks location information. | Use GroupKFold by coordinate cluster in final evaluation. | Strongly addressed in Decision 42. |
| Vacant Lot instability | Land prices need missing parcel-specific features such as frontage, zoning, title, slope, and flood risk. | Apply residential-lot scope filter and report Lot as weakest stratum. | Addressed, but must be framed as a data ceiling, not a modeling failure. |
| Thin LGU cells | Some city x stratum combinations have few listings. | Stratify by property type and use cautious interpretation; do not overread LGU boxplots where n is small. | Needs current EDA rerun with sample-size labels/tables. |

---

## Current Model Standing

From `deployment_manifest.json`:

| Stratum | Rows | Coordinate groups | Model | MdAPE | PE20 | COD | PRD |
|---|---:|---:|---|---:|---:|---:|---:|
| Condominium | 687 | 388 | Random Forest | 20.1% | 49.8% | 36.3 | 1.21 |
| Houses | 674 | 509 | Random Forest | 22.1% | 45.0% | 33.0 | 1.18 |
| Vacant Lot | 255 | 203 | Random Forest | 25.6% | 41.6% | 36.9 | 1.28 |

Plain defense version:

> The model is usually off by around 20 to 26 percent in typical cases. Vacant lots are weakest because land value depends on lot-level attributes that are not available in online listing data. The model does not meet strict IAAO ratio-study bands, so it should be framed as a decision-support AVM prototype, not an official assessment-grade mass appraisal system.

---

## What To Say About Heteroscedasticity And Collinearity

Use this wording:

> EDA found heteroscedasticity and collinearity, which are important issues for OLS interpretation. We addressed heteroscedasticity using HC3 robust standard errors in the OLS diagnostic model. We addressed collinearity by not relying on OLS coefficients as the final valuation engine. The deployed model is a stratified Random Forest, which is less sensitive to correlated predictors. OLS is retained only as a transparent diagnostic baseline.

Do not say:

- "Heteroscedasticity was fixed."
- "Collinearity no longer exists."
- "The model is IAAO compliant."
- "MCRAI is the dominant price driver."

Better phrasing:

- "Detected and accounted for."
- "Handled as a diagnostic limitation."
- "Reported transparently."
- "Random Forest was chosen partly because the spatial predictors are nonlinear and correlated."

---

## Immediate Next Steps

1. Rerun `eda_stratified_v2.py` on the current 687/674/255 stratum CSVs.
2. Rerun `eda_data_integrity.py` or update its outputs on the current ABT.
3. Save key EDA numeric outputs as CSV/JSON, not only printed logs:
   - target summaries
   - city x stratum counts
   - thin-cell flags
   - VIF flags
   - OLS residual diagnostic table
   - Cook's distance top rows
   - MCRAI zero-rate table
   - duplicate count table
4. Add a one-page defense table: EDA issue, implication, workflow response, defense wording.
5. Update Chapters 3, 6, 7, 8, 9, and the abstract to match Decision 42.
6. Fix the Streamlit app manifest contract if not already fixed: app should read `metrics_group_cv`, not old `deployed_metrics`.

---

## Claude Instruction

When resuming this project, do not restart from old global-model assumptions. Start from Decision 42 and this handoff. Keep explanations understandable to the author and defensible to a panel. If a technical choice cannot be explained in two plain sentences, write the plain-language defense before adding details.
