"""
experiment_no_cbd.py
====================
Ablation (2026-06-15): how much does the model depend on the 8 CBD-node distance features?
Re-train each stratum WITHOUT the CBD distances (RF grid re-tuned under the same leak-free
GroupKFold) and compare to the deployed with-CBD model.

CBD features removed: dist_{cebu_business_park,mandaue_cbd,mactan_cbd,srp,talisay_tabunok,
consolacion,naga_city,airport}_m. Everything else kept (MCRAI, BIR zonal, spatial_lag,
road distances, structural). Read-only: does NOT touch the deployed manifest or models.
"""

import os
import sys

import numpy as np
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from finalize_stratified_groupcv import (build_features, group_oof, iaao_panel,  # noqa: E402
                                         RF_GRID, RANDOM_STATE)
from sklearn.ensemble import RandomForestRegressor

THESIS_DIR = os.path.dirname(SCRIPT_DIR)
PROCESSED = os.path.join(THESIS_DIR, "Data", "processed")
STRATA = {"condo": ("abt_condo.csv", "Condominium"),
          "houses": ("abt_houses.csv", "Houses"),
          "lot": ("abt_lot.csv", "Vacant Lot")}
CBD_COLS = ["dist_cebu_business_park_m", "dist_mandaue_cbd_m", "dist_mactan_cbd_m", "dist_srp_m",
            "dist_talisay_tabunok_m", "dist_consolacion_m", "dist_naga_city_m", "dist_airport_m"]
DEPLOYED = {"condo": 19.8, "houses": 22.5, "lot": 38.0}  # current with-CBD MdAPE


def best_grid(X, y, actual, groups):
    best = None
    for p in RF_GRID:
        est = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1, **p)
        m = iaao_panel(actual, np.exp(group_oof(est, X, y, groups)))
        if best is None or m["MdAPE"] < best["MdAPE"]:
            best = m
    return best


def main():
    print("ABLATION — drop the 8 CBD-node distances, re-tune RF, leak-free GroupKFold\n")
    print(f"{'stratum':12}{'n':>6}{'feat':>6}  {'with-CBD':>9}{'no-CBD MdAPE':>14}{'  COD':>7}{'PRD':>6}{'PE20':>6}")
    for key, (csv, label) in STRATA.items():
        df = pd.read_csv(os.path.join(PROCESSED, csv)).reset_index(drop=True)
        X, y_s = build_features(df)
        y = y_s.to_numpy(float)
        actual = df["price_per_sqm"].to_numpy(float)
        groups = df.groupby(["latitude", "longitude"]).ngroup().to_numpy()
        Xn = X.drop(columns=[c for c in CBD_COLS if c in X.columns])
        m = best_grid(Xn, y, actual, groups)
        print(f"{label:12}{len(df):>6}{Xn.shape[1]:>6}  {DEPLOYED[key]:>9.1f}{m['MdAPE']:>14.1f}"
              f"{m['COD']:>7.1f}{m['PRD']:>6.2f}{m['PE20']:>6.0f}  "
              f"(delta {m['MdAPE']-DEPLOYED[key]:+.1f})")


if __name__ == "__main__":
    main()
