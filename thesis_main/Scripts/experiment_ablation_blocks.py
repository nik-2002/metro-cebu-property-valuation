"""
experiment_ablation_blocks.py
=============================
Leave-one-block-out feature ablation (2026-06-15), EDA-driven + PARALLEL.

The 2x sample VIF flagged heavy redundancy: MCRAI block VIF 30+ (condos),
bir_zonal_rr_log = log(rr_median), CBD distances VIF ~10. This decomposes the price signal per
stratum by dropping each coherent block and measuring the leak-free GroupKFold MdAPE hit.

SPEED — "simultaneous testing": each (stratum x block) cell is independent, so we run them all in
parallel with joblib.Parallel(n_jobs=N_CORES), each fit single-threaded (RF n_jobs=1). On ~1.3k-row
strata RF barely parallelises within a fit, so parallelising ACROSS fits uses the cores far better.
Ablation uses the DEPLOYED best params per stratum (single fit per block, not a 16-combo re-tune) —
standard for directional ablation, and ~16x less compute than re-tuning.

Blocks: CBD / MCRAI / BIR / ROAD / LAG / STRUCT  + redundant singletons bir_rr_log, mcrai_composite.
Read-only: does NOT touch the deployed manifest or models.
"""

import os
import sys

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.ensemble import RandomForestRegressor

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from finalize_stratified_groupcv import build_features, group_oof, iaao_panel, RANDOM_STATE  # noqa: E402

THESIS_DIR = os.path.dirname(SCRIPT_DIR)
PROCESSED = os.path.join(THESIS_DIR, "Data", "processed")
N_CORES = int(os.environ.get("ABLATION_CORES", "8"))

STRATA = {"condo": ("abt_condo.csv", "Condominium"),
          "houses": ("abt_houses.csv", "Houses"),
          "lot": ("abt_lot.csv", "Vacant Lot")}
DEPLOYED = {"condo": 19.8, "houses": 22.5, "lot": 38.0}
RF_BEST = {
    "condo":  {"n_estimators": 400, "max_features": 0.9, "min_samples_leaf": 2, "max_depth": None},
    "houses": {"n_estimators": 300, "max_features": 1.0, "min_samples_leaf": 2, "max_depth": 20},
    "lot":    {"n_estimators": 400, "max_features": 1.0, "min_samples_leaf": 1, "max_depth": None},
}
CBD = ["dist_cebu_business_park_m", "dist_mandaue_cbd_m", "dist_mactan_cbd_m", "dist_srp_m",
       "dist_talisay_tabunok_m", "dist_consolacion_m", "dist_naga_city_m", "dist_airport_m"]
BLOCKS = ["FULL", "CBD", "MCRAI", "BIR", "ROAD", "LAG", "STRUCT", "bir_rr_log", "mcrai_composite"]


def cols_for_block(c, block):
    if block == "FULL":   return []
    if block == "CBD":    return [x for x in CBD if x in c]
    if block == "MCRAI":  return [x for x in c if x.startswith("mcrai_")]
    if block == "BIR":    return [x for x in c if x.startswith("bir_zonal_")]
    if block == "ROAD":   return [x for x in c if x in ("dist_to_trunk_road_m", "dist_to_primary_road_m")]
    if block == "LAG":    return [x for x in c if x == "spatial_lag_price"]
    if block == "STRUCT": return [x for x in c if x in ("area_sqm", "bedrooms", "bathrooms",
                                                        "bedrooms_imputed", "bathrooms_imputed")]
    if block == "bir_rr_log":      return [x for x in c if x == "bir_zonal_rr_log"]
    if block == "mcrai_composite": return [x for x in c if x == "mcrai_composite"]
    return []


def run_cell(key, block, X, y, actual, groups):
    drop = cols_for_block(list(X.columns), block)
    if block != "FULL" and not drop:
        return key, block, np.nan
    est = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=1, **RF_BEST[key])
    mdape = iaao_panel(actual, np.exp(group_oof(est, X.drop(columns=drop), y, groups)))["MdAPE"]
    return key, block, round(mdape, 1)


def main():
    data, cells = {}, []
    for key, (csv, _) in STRATA.items():
        df = pd.read_csv(os.path.join(PROCESSED, csv)).reset_index(drop=True)
        X, y_s = build_features(df)
        data[key] = (X, y_s.to_numpy(float), df["price_per_sqm"].to_numpy(float),
                     df.groupby(["latitude", "longitude"]).ngroup().to_numpy())
        cells += [(key, b) for b in BLOCKS]

    print(f"LEAVE-ONE-BLOCK-OUT ABLATION — {len(cells)} cells across {N_CORES} cores (single-fit, "
          f"deployed params, leak-free GroupKFold)\n")
    results = Parallel(n_jobs=N_CORES, verbose=5)(
        delayed(run_cell)(k, b, *data[k]) for k, b in cells)

    tbl = {key: {} for key in STRATA}
    for k, b, v in results:
        tbl[k][b] = v
    rows = []
    for key, (_, label) in STRATA.items():
        full = tbl[key]["FULL"]
        rec = {"stratum": label, "n": len(data[key][1]), "FULL": full}
        for b in BLOCKS[1:]:
            rec[b] = tbl[key][b]
        rows.append(rec)
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(THESIS_DIR, "Models", "stratified", "ablation_blocks.csv"), index=False)

    print("\n=== MdAPE when each BLOCK is dropped (Δ vs FULL in parens) ===")
    disp = out.copy()
    for b in BLOCKS[1:]:
        disp[b] = out.apply(lambda r: f"{r[b]:.1f} ({r[b]-r['FULL']:+.1f})" if pd.notna(r[b]) else "-", axis=1)
    print(disp.to_string(index=False))
    print("\n-> Models/stratified/ablation_blocks.csv")
    print("NOTE: FULL here is a single-fit deployed-params refit; may differ ~0.x from the grid-tuned "
          "deployed MdAPE. Read the Δ columns, not absolute FULL.")


if __name__ == "__main__":
    main()
