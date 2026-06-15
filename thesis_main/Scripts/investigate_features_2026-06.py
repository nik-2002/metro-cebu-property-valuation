"""
investigate_features_2026-06.py
==============================
Post-expansion feature investigation (Decision 47 follow-up). Uses leak-free OOF predictions
from the deployed RF (same GroupKFold harness) to answer:

  Q1  SOURCE EFFECT — is the FilipinoHomes ~26% price gap vs Lamudi explained by the features,
      or a residual `source` signal? Look at signed OOF residuals (log scale) by source per
      stratum; if a source's residuals are systematically off-zero, the model can't explain it
      from features. Also test: does adding a source dummy lower OOF MdAPE?
  Q2  HIGH-ERROR LOTS — profile the worst-predicted lots (top-decile APE) vs the rest: LGU,
      source, area, dist-CBP, price band — what distinguishes them?
  Q3  (VIF read separately from EDA tables.)

Read-only: does NOT touch the manifest or models.
"""

import os
import sys

import numpy as np
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from finalize_stratified_groupcv import build_features, group_oof, RANDOM_STATE  # noqa: E402
from sklearn.ensemble import RandomForestRegressor

THESIS_DIR = os.path.dirname(SCRIPT_DIR)
PROCESSED = os.path.join(THESIS_DIR, "Data", "processed")
ABT = pd.read_csv(os.path.join(PROCESSED, "abt_clean.csv"))[["property_id", "source"]]
RF_BEST = {
    "condo":  {"n_estimators": 400, "max_features": 0.9, "min_samples_leaf": 2, "max_depth": None},
    "houses": {"n_estimators": 300, "max_features": 1.0, "min_samples_leaf": 2, "max_depth": 20},
    "lot":    {"n_estimators": 400, "max_features": 1.0, "min_samples_leaf": 1, "max_depth": None},
}
STRATA = {"condo": "abt_condo.csv", "houses": "abt_houses.csv", "lot": "abt_lot.csv"}


def oof_frame(key):
    df = pd.read_csv(os.path.join(PROCESSED, STRATA[key])).reset_index(drop=True)
    X, y_s = build_features(df)
    y = y_s.to_numpy(float)
    groups = df.groupby(["latitude", "longitude"]).ngroup().to_numpy()
    est = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1, **RF_BEST[key])
    pred_log = group_oof(est, X, y, groups)
    actual = df["price_per_sqm"].to_numpy(float)
    pred = np.exp(pred_log)
    out = df.copy()
    out["pred_psqm"] = pred
    out["resid_log"] = pred_log - y                 # +ve = model OVER-predicts
    out["ape"] = np.abs(pred - actual) / actual
    out = out.merge(ABT, on="property_id", how="left")
    out["src"] = out["source"].str.replace("_2026-06", "").str.replace("_playwright", "_pw")
    return out, X


def q1_source_effect(frames):
    print("\n" + "=" * 74)
    print("Q1 — SOURCE EFFECT (signed OOF residual on log scale; +ve = model OVER-predicts)")
    print("=" * 74)
    print("If a source's median residual is ~0, the features explain it. Off-zero = source signal.")
    for key, (out, _) in frames.items():
        print(f"\n{key.upper()}:")
        g = out.groupby("src").agg(n=("ape", "size"),
                                   med_resid_log=("resid_log", "median"),
                                   med_ape=("ape", "median"))
        g["med_ape_%"] = (g["med_ape"] * 100).round(1)
        g["price_ratio_pred/act"] = np.exp(g["med_resid_log"]).round(3)
        print(g[["n", "med_resid_log", "price_ratio_pred/act", "med_ape_%"]].round(3).to_string())


def q1b_source_dummy(frames):
    print("\n" + "=" * 74)
    print("Q1b — does adding a `source` dummy lower OOF MdAPE? (signal beyond existing features)")
    print("=" * 74)
    for key, (out, X) in frames.items():
        df = pd.read_csv(os.path.join(PROCESSED, STRATA[key])).reset_index(drop=True)
        y = np.log(df["price_per_sqm"].to_numpy(float))
        groups = df.groupby(["latitude", "longitude"]).ngroup().to_numpy()
        actual = df["price_per_sqm"].to_numpy(float)
        src = out["src"].to_numpy()
        Xs = X.copy()
        for s in pd.unique(src):
            Xs[f"src_{s}"] = (src == s).astype(int)
        est = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1, **RF_BEST[key])
        base = np.median(np.abs(out["pred_psqm"] / actual - 1)) * 100
        pred2 = np.exp(group_oof(est, Xs, y, groups))
        with_src = np.median(np.abs(pred2 / actual - 1)) * 100
        print(f"  {key:7} MdAPE  base={base:5.1f}  +source_dummy={with_src:5.1f}  "
              f"delta={with_src-base:+.2f}")


def q2_high_error_lots(frames):
    print("\n" + "=" * 74)
    print("Q2 — HIGH-ERROR LOTS (top-decile APE vs rest)")
    print("=" * 74)
    out = frames["lot"][0]
    thr = out["ape"].quantile(0.90)
    hi = out[out["ape"] >= thr]
    lo = out[out["ape"] < thr]
    print(f"top-decile APE threshold = {thr*100:.0f}%  (n_hi={len(hi)}, n_rest={len(lo)})")
    cols = ["area_sqm", "price_per_sqm", "dist_cebu_business_park_m", "bir_zonal_rr_median",
            "spatial_lag_price", "mcrai_composite"]
    comp = pd.DataFrame({"high_err_median": hi[cols].median(), "rest_median": lo[cols].median()})
    comp["ratio"] = (comp["high_err_median"] / comp["rest_median"]).round(2)
    print("\nmedian feature values — worst-predicted lots vs rest:")
    print(comp.round(1).to_string())
    print("\nhigh-error lots by source:")
    print((hi["src"].value_counts(normalize=True) * 100).round(0).to_string())
    print("\nhigh-error lots by LGU:")
    print((hi["city"].value_counts(normalize=True) * 100).round(0).to_string())
    print(f"\ndirection: model OVER-predicts {100*(hi['resid_log']>0).mean():.0f}% of high-error lots "
          f"(under-predicts the rest).")


def main():
    print("FEATURE INVESTIGATION — leak-free OOF, deployed RF (Decision 47 follow-up)")
    frames = {k: oof_frame(k) for k in STRATA}
    q1_source_effect(frames)
    q1b_source_dummy(frames)
    q2_high_error_lots(frames)


if __name__ == "__main__":
    main()
