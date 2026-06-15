"""
data_health_check.py
====================
Reliability diagnostics for the deployed stratified RF models (read-only).
Answers: are the models healthy, and are the RQ2/RQ3 conclusions robust to their
own uncertainty? Uses the same leak-free GroupKFold harness.

Reports per stratum:
  1. Overfitting    : train (in-sample) MdAPE vs leak-free OOF MdAPE.
  2. Stability      : per-fold OOF MdAPE (mean +/- std) + bootstrap 95% CI on OOF MdAPE.
  3. RQ2 tie test   : bootstrap 95% CI on (RF - XGB) OOF MdAPE difference.
  4. RQ3 uplift test: bootstrap 95% CI on (structural - full) OOF MdAPE difference.
  5. IAAO health    : COD / PRD (from the OOF predictions).
"""

import json
import os
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GroupKFold
from xgboost import XGBRegressor

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from answer_rq2_rq3 import build_full_and_ols, tier_columns, STRATA, PROCESSED_DIR, MANIFEST

RANDOM_STATE, N_SPLITS = 42, 5
RNG = np.random.default_rng(42)
B = 2000

XGB_BEST = {
    "condo":  {"n_estimators": 300, "max_depth": 3, "learning_rate": 0.05, "subsample": 0.9},
    "houses": {"n_estimators": 500, "max_depth": 3, "learning_rate": 0.05, "subsample": 0.9},
    "lot":    {"n_estimators": 300, "max_depth": 5, "learning_rate": 0.05, "subsample": 0.9},
}


def mdape(actual, pred):
    return float(np.median(np.abs(pred / actual - 1)) * 100)


def cod_prd(actual, pred):
    ratio = pred / actual
    med = np.median(ratio)
    cod = 100.0 * np.mean(np.abs(ratio - med)) / med
    prd = np.mean(ratio) / (pred.sum() / actual.sum())
    return cod, prd


def oof_and_folds(estimator, X, y, groups):
    oof = np.zeros(len(y))
    fold_scores = []
    actual_all = np.exp(y)
    for tr, te in GroupKFold(N_SPLITS).split(X, y, groups):
        m = clone(estimator); m.fit(X.iloc[tr], y[tr]); oof[te] = m.predict(X.iloc[te])
        fold_scores.append(mdape(np.exp(y[te]), np.exp(oof[te])))
    return np.exp(oof), fold_scores


def boot_ci(actual, pred):
    n = len(actual)
    stats = [mdape(actual[idx], pred[idx]) for idx in (RNG.integers(0, n, n) for _ in range(B))]
    return np.percentile(stats, [2.5, 97.5])


def boot_diff_ci(actual, pred_a, pred_b):
    n = len(actual)
    diffs = []
    for _ in range(B):
        idx = RNG.integers(0, n, n)
        diffs.append(mdape(actual[idx], pred_a[idx]) - mdape(actual[idx], pred_b[idx]))
    return np.percentile(diffs, [2.5, 97.5]), float(np.mean(np.array(diffs) > 0))


def main():
    man = json.load(open(MANIFEST))
    for key, cfg in STRATA.items():
        df = pd.read_csv(os.path.join(PROCESSED_DIR, cfg["csv"])).reset_index(drop=True)
        X, _, y_s = build_full_and_ols(df, key)
        y = y_s.to_numpy(float)
        actual = df["price_per_sqm"].to_numpy(float)
        groups = df.groupby(["latitude", "longitude"]).ngroup().to_numpy()
        bp = man["strata"][key]["best_params"]

        rf = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1, **bp)
        rf_oof, rf_folds = oof_and_folds(rf, X, y, groups)
        xgb = XGBRegressor(random_state=RANDOM_STATE, n_jobs=-1, verbosity=0, **XGB_BEST[key])
        xgb_oof, _ = oof_and_folds(xgb, X, y, groups)

        # structural-only RF (RQ3 tier 1)
        tcols = tier_columns(X)["1_structural"]
        rf_struct_oof, _ = oof_and_folds(
            RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1, **bp), X[tcols], y, groups)

        # in-sample (train) fit for overfitting check
        rf_full = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1, **bp).fit(X, y)
        train_md = mdape(actual, np.exp(rf_full.predict(X)))

        oof_md = mdape(actual, rf_oof)
        ci = boot_ci(actual, rf_oof)
        cod, prd = cod_prd(actual, rf_oof)
        (tie_lo, tie_hi), p_rf_worse = boot_diff_ci(actual, rf_oof, xgb_oof)
        (up_lo, up_hi), _ = boot_diff_ci(actual, rf_struct_oof, rf_oof)  # struct - full (positive = geo helps)

        print("=" * 78)
        print(f"{cfg['label']}  (n={len(df)}, coord-groups={pd.Series(groups).nunique()})")
        print("=" * 78)
        print(f"  1. Overfitting:  train MdAPE={train_md:5.1f}%   OOF MdAPE={oof_md:5.1f}%   "
              f"gap={oof_md-train_md:4.1f}pp")
        print(f"  2. Stability:    per-fold OOF MdAPE = {np.mean(rf_folds):.1f}% +/- {np.std(rf_folds):.1f}  "
              f"(folds: {', '.join(f'{s:.0f}' for s in rf_folds)})")
        print(f"                   bootstrap 95% CI on OOF MdAPE = [{ci[0]:.1f}, {ci[1]:.1f}]%")
        print(f"  3. RQ2 tie:      RF-XGB MdAPE diff 95% CI = [{tie_lo:+.1f}, {tie_hi:+.1f}]pp  "
              f"(straddles 0 = tie: {'YES' if tie_lo < 0 < tie_hi else 'NO'})")
        print(f"  4. RQ3 uplift:   (structural - full) MdAPE 95% CI = [{up_lo:+.1f}, {up_hi:+.1f}]pp  "
              f"(excludes 0 = real uplift: {'YES' if up_lo > 0 else 'NO'})")
        print(f"  5. IAAO health:  COD={cod:.1f} (resid<=15)   PRD={prd:.2f} (0.98-1.03)  "
              f"-> {'regressive' if prd > 1.03 else 'ok'}")
        print()


if __name__ == "__main__":
    main()
