# Ramolete et al. (2023) — Their Method + Our Protocol Replication (2026-06-14)

> Purpose: make the Chapter 7 benchmark against Ramolete et al. defensible by (1) documenting
> their full end-to-end process and (2) running OUR models under THEIR evaluation protocol
> (random 80/20 split) so the comparison is like-for-like. Feeds the Ch7 benchmarking item in
> `ch_correction_checklist_2026-06-13.md` and `avm_benchmarks_2026-06-13.md`.
>
> ⚠ Verify author list / page numbers against the PDF before final citation (CLAUDE.md rule).
> Script: `Scripts/replicate_ramolete_randomsplit.py` · Output:
> `Models/stratified/ramolete_randomsplit_comparison.csv`.

---

## 1. Why they are the right comparable

Ramolete, Bramaskara, Reyes & Heinrich (2023), *The Philippine Statistician*, Vol. 72, No. 1 —
"Utilization of Machine Learning, Government-Based and Non-Conventional Indicators for Property
Value Prediction in the Philippines." It is the closest published Philippine study to this
thesis: **Lamudi listings + OpenStreetMap amenities + government indicators + tree-based ML +
market segmentation.** Same data source, same scraper family (BeautifulSoup), same broad recipe
— different region (Cavite / Metro Manila vs Metro Cebu) and, crucially, a **different
evaluation protocol** (random split vs our leak-free GroupKFold).

## 2. Their end-to-end process

**Data collection (web scraping).**
- Source: **Lamudi.com.ph** property listings, scraped with **`requests` + BeautifulSoup** — the
  same source and scraper family this thesis started with.
- Geography: **Cavite and Metro Manila.** The headline modelling set is **3,212 house listings
  in Cavite** (house-dominated — important for the like-for-like comparison below).
- Per listing they captured price and structural attributes (area, bedrooms, bathrooms, etc.).

**Feature enrichment (three indicator families).**
- **Non-conventional / spatial:** **OpenStreetMap** amenities and buildings overlaid on each
  listing's location (proximity / count of nearby points of interest).
- **Government-based:** **PSA** socio-economic data and the **DTI 2021 National Competitiveness
  Index** joined by locality. Their key finding: **government indicators substantially improve
  accuracy** — the direct analogue of this thesis's **BIR zonal-value feature**.
- Conventional structural attributes from the listing itself.

**Cleaning + segmentation.**
- Standard listing cleaning (price/area sanity, missing-value handling).
- **Market segmentation by unsupervised clustering — K-Means and BIRCH** — before modelling.
  Segmenting **lowered error**, which validates this thesis's **property-type stratification**
  (Decision 27): both papers independently find that splitting the market before modelling helps.

**Modelling.**
- A wide tree-based model zoo: **Decision Tree, Gradient Boosting Machine, Random Forest,
  Extremely Randomized Trees (ExtraTrees), XGBoost, LightGBM, AdaBoost.**
- In the non-segmented setup, **AdaBoost performed most reliably**; with segmentation the
  tree ensembles improved further.

**Evaluation protocol — the key difference.**
- **Plain random 80/20 train-test split.** Not spatially grouped, not coordinate-aware. With
  Lamudi data this lets rows that share a location (same building, subdivision-centroid
  geocodes, relistings) sit in **both** train and test.
- **Headline metric: MAPE, reported as a range of 10.7%–21%** across areas/segments (they also
  report Mean Absolute Error).

## 3. What we replicate, and what we do not

We replicate their **protocol**, not their full model zoo. Our deployed pipeline is a three-model
comparison (OLS / Random Forest / XGBoost) under **leak-free GroupKFold(5)** grouped by
coordinate cluster. For this benchmark we re-run those same three models on the same three strata
under **their protocol — a plain random 80/20 split that ignores coordinate groups** — so the
only thing that changes is the split.

Because a single 80/20 split on the smaller Vacant Lot stratum (n=849) is noisy, we run **25
repeated random splits** (different seeds) and report the mean ± SD, plus the literal single
seed=42 split for a faithful one-shot replication. Headline metric is **MAPE** (theirs), with
MdAPE/PE20 alongside for continuity with our own reporting.

> **Refresh note (2026-06-15).** Re-run on the expanded 3,616-row ABT (Condo 1,300 / Houses 1,223 /
> Lot 849) with the deployed Decision 47i per-stratum feature sets and refreshed RF params. The
> earlier (1,849-row) version of this table is superseded by the numbers below.

The point of the exercise: the gap between the random-split MAPE and our leak-free MAPE is the
**cost of evaluation rigor** — how much a naive split flatters the model by leaking shared
locations. We expect it to be **largest for condominiums**, where coordinate clustering is most
severe (one 64-unit building on a single pin).

## 4. Results — our models under their random 80/20 protocol

> **Model roles.** Only **Random Forest is the deployed model** (the price surface). **OLS and
> XGBoost are comparators only** — OLS is the hedonic baseline, XGB a second tree family included
> to show the leakage pattern is not peculiar to RF (RF ≈ XGB was a statistical tie in RQ2; RF was
> deployed for robustness). XGB/OLS are never shipped.

Random Forest, mean of 25 random splits (Vacant Lot single seed=42 in parentheses where the
spread is large). Leak-free MAPE is the deployed GroupKFold number from the manifest.

| Stratum | n | RF random-80/20 MAPE (mean ± sd) | seed=42 | RF random-80/20 MdAPE | Leak-free MAPE | Leak-free MdAPE |
|---|---|---|---|---|---|---|
| Condominium | 1,300 | **31.5% ± 4.1** | 27.0% | **16.2%** | 36.5% | 19.3% |
| Houses | 1,223 | **33.8% ± 3.1** | 34.5% | **22.1%** | 35.1% | 22.7% |
| Vacant Lot | 849 | **56.1% ± 7.4** | 62.1% | **36.2%** | 58.0% | 38.2% |

**Read the direction carefully:** the random-split numbers are *better* (lower error) than our
deployed leak-free numbers across the board — Condo MAPE 31.5% < 36.5%, MdAPE 16.2% < 19.3%, and
likewise for houses/lots. That is **expected and is the whole finding, not a sign the random setup
is superior.** A random 80/20 split lets rows sharing a coordinate (same building, centroid
geocodes, relistings) fall into both train and test, so the model is partly scored on locations it
has already memorised — which flatters the result. The leak-free GroupKFold number is the harder,
honest one because no location appears in both train and test. We report the leak-free number as
the headline precisely because the random-split number is optimistically biased.

Leakage inflation (leak-free MAPE − random MAPE), RF: **Condo +5.1pp, Houses +1.3pp, Lot +1.8pp.**
Condo is the largest — consistent with condos having the densest coordinate clustering — but the
effect is modest in absolute terms (1–5pp), and on the expanded data it **shrank** for houses and
lots (more training data leaves less room for a naive split to flatter the model). XGB mirrors RF
and barely inflates at all now (Condo +1.7, Houses −0.1, Lot −1.0pp). OLS is unstable under random
splits (Condo MAPE 43.9% ± 6.4, Lot 61.0% ± 5.3) and is not a useful read here; the tree models
are the meaningful comparison. Full OLS/RF/XGB × stratum grid in the CSV.

## 5. What the gap to Ramolete actually means (corrected, honest reading)

The original assumption was that our higher headline MAPE was *mostly* the price of leak-free
evaluation. **The replication refutes that.** Two findings:

1. **Coordinate leakage explains only a few points.** Switching from leak-free GroupKFold to a
   random 80/20 split improves RF MAPE by just **1–5pp** (most for condos, +5pp). It is real but
   small — and on the expanded data it shrank further for houses (+1.3pp) and lots (+1.8pp).
2. **Even under Ramolete's own protocol, our MAPE is ~32–34% (houses) — still above their
   10.7–21%.** So the protocol difference does NOT explain the gap. The remaining ~13pp (houses)
   is a genuine, explainable performance difference: their **3,212 Cavite houses** vs our
   **1,223**, a thinner and noisier Cebu listing market, their richer feature set (PSA
   socio-economic + DTI competitiveness), and their AdaBoost/segmentation. We must not wave the
   gap away as "we're just more honest."

**The redeeming, defensible point — lead with MdAPE.** Our RF *typical* error (MdAPE) under the
random split is **16.2% (condo) / 22.1% (houses)** — condo inside, houses right at the top of
Ramolete's MAPE band. The MAPE–MdAPE divergence (≈32–34% vs ≈16–22%) says the *median* property
is predicted competitively; a minority of hard properties with large percentage errors pulls the
mean (MAPE) up. That tail — not the typical case — is where the headline gap lives.

**Vacant Lot is now visibly the weakest stratum (random MAPE 56%, MdAPE 36%), and that is honest,
not a regression.** The earlier (1,849-row) replication showed Lot MdAPE ≈21% on the random split,
but that was the small, geographically concentrated, optimistic lot sample (Decision 47f). On the
expanded, broader sample the lot error rises to its true level — bare-land value depends on
parcel-specific attributes (frontage, zoning, title, slope, flood) absent from listing data
(`feature_investigation_2026-06-14.md`). Lots are not a fair comparison to Ramolete (house study);
houses remain the like-for-like.

**Where part of that tail comes from — the geocoding link (`shared_pin_investigation_2026-06-14.md`).**
A companion investigation found that **~31–37% of the Houses and Lot strata sit on
centroid-snapped coordinates**: listings with incomplete addresses (subdivision/barangay/city,
no street number) were geocoded to a barangay or subdivision *centroid*, not the true parcel.
Their spatial features — CBD network distances, MCRAI accessibility, road distances, spatial lag
— were therefore computed from the wrong point. That injects spatial-feature noise into roughly a
third of houses/lots, which plausibly feeds the heavy error tail (high MAPE relative to MdAPE) and
is part of the genuine, non-protocol gap to Ramolete. Note this does NOT break the leak-free CV:
GroupKFold groups by exact lat/lon, so a centroid's listings all fall in the same fold (no
train/test leakage). It is a **data-quality limitation** (noisy features on some rows), not an
evaluation flaw — and a candidate fix for future work (re-geocode incomplete addresses).

## 6. The Chapter 7 framing (paste-ready)

> Replicating Ramolete et al.'s random 80/20 protocol on the same models, our house-stratum
> Random Forest reaches MAPE ≈ **33.8%** (typical error, MdAPE ≈ 22%) — the MdAPE sitting at the
> top of their reported 10.7–21% band. The identical model under our stricter leak-free
> GroupKFold protocol reports 35.1%. Preventing coordinate leakage therefore costs only ~1pp on
> houses (up to ~5pp on condominiums, where listings cluster most densely); it is **not** the
> main reason our headline error exceeds theirs. The larger share of the difference is a genuine
> performance gap, attributable to their larger house sample (3,212 vs 1,223), a thinner Cebu
> market, and their additional socio-economic and competitiveness features. Because Ramolete et
> al.'s data is house-dominated, the houses stratum is the fairest like-for-like comparison.

**Honest takeaway for the defense:** the model's *typical* prediction (~16% condo / ~22% houses
off) is competitive with the closest Philippine study; the higher mean error reflects a tail of
hard-to-value properties and a thinner dataset — not a broken model, and not merely an artifact of
honest evaluation. Vacant lots are the exception (random MAPE 56% / MdAPE 36%) and reflect a
genuine bare-land data ceiling, not an evaluation gap.

## 6. Caveats to keep in the prose
- Listings, not closed sales (asking-price noise) — both studies share this.
- Different region and market thickness (Cebu vs Cavite/Manila).
- Their MAPE is a cross-area/segment range, not a single figure.
- We replicate their protocol and three of their model families, not the full zoo or their
  exact feature set.
