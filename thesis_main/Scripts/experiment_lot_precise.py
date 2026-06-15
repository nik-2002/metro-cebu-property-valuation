"""
experiment_lot_precise.py
=========================
Isolating experiment (2026-06-14): does the Vacant Lot degradation (25.6 -> 38.0 MdAPE after the
multi-source merge) come from CENTROID-geocoded lots corrupting the location signal, or from
feature engineering / inherent lot heterogeneity?

Test: retrain the lot RF (same GroupKFold harness, same RF grid) on:
  (A) ALL 851 lots                          -> the degraded retrain (expect ~38)
  (B) PRECISE-coord lots only (746)         -> drop APPROXIMATE/GEOMETRIC_CENTER (105 centroids)
Compare to the validated 255-lot baseline (MdAPE 25.6).

  If (B) recovers toward 25.6  -> centroid DATA was the cause; precise new lots are usable.
  If (B) stays high            -> feature engineering / lots inherently hard.

Read-only: does NOT touch the deployed manifest or model pkls.
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
LOT_CSV = os.path.join(THESIS_DIR, "Data", "processed", "abt_lot.csv")
STAGED = os.path.join(THESIS_DIR, "Data", "raw", "multisource_batch_2026-06_staged.csv")
PRECISE = {"original", "embedded", "ROOFTOP", "RANGE_INTERPOLATED"}


def best_rf(df, label):
    X, y_s = build_features(df)
    y = y_s.to_numpy(float)
    actual = df["price_per_sqm"].to_numpy(float)
    groups = df.groupby(["latitude", "longitude"]).ngroup().to_numpy()
    best = None
    for p in RF_GRID:
        est = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1, **p)
        m = iaao_panel(actual, np.exp(group_oof(est, X, y, groups)))
        if best is None or m["MdAPE"] < best["MdAPE"]:
            best = m
    print(f"  {label:28} n={len(df):4d}  groups={pd.Series(groups).nunique():4d}  "
          f"MdAPE={best['MdAPE']:5.1f}  COD={best['COD']:5.1f}  PRD={best['PRD']:.2f}  PE20={best['PE20']:.0f}")
    return best


def main():
    lot = pd.read_csv(LOT_CSV)
    staged = pd.read_csv(STAGED)[["property_id", "geocode_precision"]]
    lot = lot.merge(staged, on="property_id", how="left")
    lot["prec"] = lot["geocode_precision"].fillna("original")
    lot["is_precise"] = lot["prec"].isin(PRECISE)

    print("LOT EXPERIMENT — centroid vs precise (validated baseline = MdAPE 25.6 on 255 lots)\n")
    best_rf(lot.drop(columns=["geocode_precision", "prec", "is_precise"]),
            "(A) ALL lots")
    precise = lot[lot["is_precise"]].drop(columns=["geocode_precision", "prec", "is_precise"]).copy()
    best_rf(precise, "(B) PRECISE-coord lots only")
    # also: original Lamudi-only as a re-baseline under the same harness
    # (mark old rows: those not in staged)
    new_ids = set(pd.read_csv(STAGED)["property_id"])
    orig = lot[~lot["property_id"].isin(new_ids)].drop(columns=["geocode_precision", "prec", "is_precise"]).copy()
    best_rf(orig, "(C) original Lamudi lots only")


if __name__ == "__main__":
    main()
