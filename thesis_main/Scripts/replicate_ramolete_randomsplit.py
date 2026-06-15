"""
replicate_ramolete_randomsplit.py
=================================
Benchmark replication for Ramolete et al. (2023), *The Philippine Statistician* 72(1):
"Utilization of Machine Learning, Government-Based and Non-Conventional Indicators for
Property Value Prediction in the Philippines."

WHY THIS SCRIPT EXISTS
----------------------
Ramolete et al. is our closest Philippine comparable (Lamudi listings + OSM + government
indicators + tree-based ML + segmentation). They report MAPE 10.7-21% — but on a PLAIN
RANDOM 80/20 split. Our deployed numbers (MdAPE 20-26%, MAPE 32-38%) are on a stricter
leak-free GroupKFold(5) grouped by coordinate cluster. The two are NOT comparable: a random
split lets rows that share a coordinate (same condo building, subdivision-centroid geocodes,
relistings) land in both train and test, so the model is partly tested on locations it has
already seen. That inflates the score.

To compare honestly we run OUR models under THEIR protocol — a random 80/20 split that ignores
coordinate groups — and measure how much the random split inflates each stratum. The delta
between random-split MAPE and leak-free MAPE is the "cost of evaluation rigor" (expected to be
largest for condos, where coordinate clustering is most severe).

WHAT IT DOES NOT DO
-------------------
It does NOT change abt_clean.csv, the strata, or the deployed models. It only re-evaluates the
same models under a different split and writes a comparison CSV. This is diagnostic/benchmark
work, not a modeling decision.

DESIGN
------
- Models per stratum: OLS (hedonic baseline), Random Forest (deployed best params), XGBoost
  (comparator best params). Mirrors our RQ2 trio. Ramolete used a wider zoo (DT/GBM/RF/
  ExtraTrees/XGB/LightGBM/AdaBoost); what we replicate is their *protocol*, not their model list.
- Protocol: plain random 80/20 split, NO coordinate grouping. Because a single split on the
  small Lot stratum (n=255) is very noisy, we run N_REPEATS random splits with different seeds
  and report mean +/- std; we also report the literal single seed=42 split for a faithful
  one-shot replication.
- Headline metric MAPE (Ramolete's headline) plus MdAPE/PE20 for continuity with our reporting.
- Leak-free MAPE is read back from deployment_manifest.json so the comparison is one table.

Reuses, unchanged:
  finalize_stratified_groupcv.build_features  (tree X_full + y)
  run_models_stratified.build_features        (X_ols for OLS)
  finalize_stratified_groupcv.iaao_panel      (metric panel; we use MAPE/MdAPE/PE20)

Output: Models/stratified/ramolete_randomsplit_comparison.csv  + printed tables.
"""

import json
import os
import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# Reuse the authoritative harness untouched.
from finalize_stratified_groupcv import build_features as build_tree_features  # noqa: E402
from finalize_stratified_groupcv import iaao_panel  # noqa: E402
from finalize_stratified_groupcv import STRATUM_DROP  # noqa: E402
from run_models_stratified import build_features as build_ols_features  # noqa: E402

THESIS_DIR = os.path.dirname(SCRIPT_DIR)
PROCESSED_DIR = os.path.join(THESIS_DIR, "Data", "processed")
MODELS_DIR = os.path.join(THESIS_DIR, "Models", "stratified")
MANIFEST = os.path.join(MODELS_DIR, "deployment_manifest.json")
OUT_CSV = os.path.join(MODELS_DIR, "ramolete_randomsplit_comparison.csv")

RANDOM_STATE = 42
TEST_SIZE = 0.20
N_REPEATS = 25

STRATA = {
    "condo":  {"csv": "abt_condo.csv",  "label": "Condominium"},
    "houses": {"csv": "abt_houses.csv", "label": "Houses"},
    "lot":    {"csv": "abt_lot.csv",    "label": "Vacant Lot"},
}

# Deployed RF best params (deployment_manifest.json, refreshed post-Decision 47i / 3,616-row ABT).
RF_BEST = {
    "condo":  {"n_estimators": 300, "max_features": 0.7, "min_samples_leaf": 1, "max_depth": None},
    "houses": {"n_estimators": 300, "max_features": 1.0, "min_samples_leaf": 2, "max_depth": None},
    "lot":    {"n_estimators": 300, "max_features": 1.0, "min_samples_leaf": 1, "max_depth": 20},
}

# XGB comparator best params (data_health_check.XGB_BEST).
XGB_BEST = {
    "condo":  {"n_estimators": 300, "max_depth": 3, "learning_rate": 0.05, "subsample": 0.9},
    "houses": {"n_estimators": 500, "max_depth": 3, "learning_rate": 0.05, "subsample": 0.9},
    "lot":    {"n_estimators": 300, "max_depth": 5, "learning_rate": 0.05, "subsample": 0.9},
}


def make_model(family: str, key: str):
    if family == "OLS":
        return LinearRegression()
    if family == "RF":
        return RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1, **RF_BEST[key])
    if family == "XGB":
        return XGBRegressor(random_state=RANDOM_STATE, n_jobs=-1, verbosity=0, **XGB_BEST[key])
    raise ValueError(family)


def metrics_on_split(model, X, y, actual, seed):
    """One random 80/20 split. y is log(price_per_sqm); actual is price_per_sqm.

    Returns MAPE/MdAPE/PE20 on the held-out 20%, back-transformed to price_per_sqm.
    """
    idx = np.arange(len(y))
    tr, te = train_test_split(idx, test_size=TEST_SIZE, random_state=seed, shuffle=True)
    model.fit(X.iloc[tr], y[tr])
    pred_log = model.predict(X.iloc[te])
    panel = iaao_panel(actual[te], np.exp(pred_log))
    return panel["MAPE"], panel["MdAPE"], panel["PE20"]


def run_stratum(key, cfg, leakfree):
    df = pd.read_csv(os.path.join(PROCESSED_DIR, cfg["csv"])).reset_index(drop=True)
    X_tree, y_s = build_tree_features(df)
    # Match the deployed model: apply the per-stratum feature selection (Decision 47i).
    drop = [c for c in STRATUM_DROP.get(key, []) if c in X_tree.columns]
    if drop:
        X_tree = X_tree.drop(columns=drop)
    _, X_ols, _, _ = build_ols_features(df, key)
    y = y_s.to_numpy(float)
    actual = df["price_per_sqm"].to_numpy(float)

    print("\n" + "=" * 78)
    print(f"{cfg['label']}  n={len(df)}  (random 80/20, no coordinate grouping)")
    print("=" * 78)

    rows = []
    for family in ("OLS", "RF", "XGB"):
        X = X_ols if family == "OLS" else X_tree
        # Repeated random splits for a stable estimate.
        reps = np.array([metrics_on_split(make_model(family, key), X, y, actual, RANDOM_STATE + i)
                         for i in range(N_REPEATS)])
        mape_mean, mdape_mean, pe20_mean = reps.mean(axis=0)
        mape_std = reps[:, 0].std(ddof=1)
        # Literal one-shot seed=42 split (faithful single replication).
        mape42, mdape42, pe2042 = metrics_on_split(make_model(family, key), X, y, actual, RANDOM_STATE)

        lf_mape = leakfree.get(key, {}).get("MAPE", np.nan)
        lf_mdape = leakfree.get(key, {}).get("MdAPE", np.nan)
        delta_mape = lf_mape - mape_mean  # how much leak-free is HIGHER (the inflation removed)

        rows.append({
            "stratum": cfg["label"], "model": family, "n": len(df),
            "rand8020_MAPE_mean": round(mape_mean, 2), "rand8020_MAPE_std": round(mape_std, 2),
            "rand8020_MdAPE_mean": round(mdape_mean, 2), "rand8020_PE20_mean": round(pe20_mean, 1),
            "rand8020_MAPE_seed42": round(mape42, 2), "rand8020_MdAPE_seed42": round(mdape42, 2),
            "leakfree_MAPE": round(lf_mape, 2) if lf_mape == lf_mape else None,
            "leakfree_MdAPE": round(lf_mdape, 2) if lf_mdape == lf_mdape else None,
            "leakage_inflation_MAPE": round(delta_mape, 2) if delta_mape == delta_mape else None,
        })
        print(f"  {family:<4} random-8020 MAPE={mape_mean:6.2f}% (+/-{mape_std:.2f}, "
              f"seed42={mape42:6.2f}%)  MdAPE={mdape_mean:6.2f}%  PE20={pe20_mean:4.1f}%"
              f"   | leak-free MAPE={lf_mape:6.2f}%  -> inflation {delta_mape:+.2f}pp")
    return rows


def main():
    print("RAMOLETE ET AL. (2023) PROTOCOL REPLICATION — random 80/20, our data, our models")
    print(f"Repeats per model: {N_REPEATS} random seeds (mean +/- std) + literal seed=42.\n")
    print("Reminder: random split re-introduces the coordinate leakage that GroupKFold removes;")
    print("the gap to the leak-free number is the cost of honest evaluation, not model quality.")

    with open(MANIFEST) as fh:
        manifest = json.load(fh)
    leakfree = {k: r["metrics_group_cv"] for k, r in manifest["strata"].items()}

    all_rows = []
    for key, cfg in STRATA.items():
        all_rows.extend(run_stratum(key, cfg, leakfree))

    out = pd.DataFrame(all_rows)
    out.to_csv(OUT_CSV, index=False)

    print("\n" + "=" * 78)
    print("SUMMARY — random-80/20 vs leak-free GroupKFold (MAPE), per stratum x model")
    print("=" * 78)
    print(f"{'stratum':<13}{'model':<5}{'rand80/20':>11}{'leak-free':>11}{'inflation':>11}")
    for r in all_rows:
        print(f"{r['stratum']:<13}{r['model']:<5}"
              f"{r['rand8020_MAPE_mean']:>10.2f}%{(r['leakfree_MAPE'] or float('nan')):>10.2f}%"
              f"{(r['leakage_inflation_MAPE'] or float('nan')):>+10.2f}")
    print(f"\nComparison CSV -> {OUT_CSV}")
    print("\nLike-for-like note: Ramolete's data is house-dominated (3,212 Cavite houses), so the")
    print("HOUSES stratum random-split MAPE is the fairest comparison to their 10.7-21% band.")


if __name__ == "__main__":
    main()
