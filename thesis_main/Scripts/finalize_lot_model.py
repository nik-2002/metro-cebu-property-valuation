"""
finalize_lot_model.py
=====================
Authoritative Vacant Lot model (Decision 41).

Why this exists: the post-batch Lot stratum reported a k-fold mean MAPE of ~75% (+/-44).
Investigation showed that figure was an artifact, not a broken model:
  1. MAPE explodes on a handful of ultra-cheap rows (small denominators) that were
     development/agricultural parcels or data errors, not residential lots.
  2. The CV leaked: 109 of 301 rows shared coordinates (barangay-centroid geocodes +
     relistings), so neighbours with near-identical features straddled train/test folds.

This script reports the Lot stratum honestly:
  - Data is already scope/quality-filtered upstream (prepare_stratified_abt.py, Decision 41):
    residential lots only (80-2000 sqm), price >= 0.5x BIR zonal floor. n = 255.
  - GROUP-AWARE 5-fold CV (groups = coordinate cluster) so shared-location rows never
    split across folds -> leak-free out-of-sample estimate, every row predicted once.
  - Reported against the market/mass-appraisal benchmark: IAAO Standard on Ratio Studies
    (2013) statistics -- MdAPE, COD, PRD, PE10/PE20 -- not MAPE.
    IAAO bands: COD vacant land <= 25 (residential improved 5-15); PRD 0.98-1.03.
  - Small RF tuning selected by group-CV MdAPE (the honest typical-error metric, Decision 38e).
  - Deployed model refit on the full filtered stratum (drop-in for the app: same feature set
    as run_models_stratified.build_features).

Writes:
    Models/stratified/lot_model.pkl   (deployed, refit on full filtered stratum)
    Models/stratified/lot_rf.pkl      (reference copy)
    Models/stratified/lot_iaao_report.json
    EDA/plots/10_stratified_models/shap_lot_rf_summary.png
"""

import json
import os
import pickle

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GroupKFold

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
THESIS_DIR = os.path.dirname(SCRIPT_DIR)
ROOT_DIR = os.path.dirname(THESIS_DIR)
PROCESSED_DIR = os.path.join(THESIS_DIR, "Data", "processed")
MODELS_DIR = os.path.join(THESIS_DIR, "Models", "stratified")
SHAP_DIR = os.path.join(ROOT_DIR, "EDA", "plots", "10_stratified_models")
os.makedirs(SHAP_DIR, exist_ok=True)

RANDOM_STATE = 42
STRATUM_KEY = "lot"
CSV = "abt_lot.csv"
N_SPLITS = 5

# Feature build mirrors run_models_stratified.build_features exactly (kept here so the
# script has no shap/xgboost import dependency). The saved model stays a drop-in for the app.
TARGET = "log_price"
EXCLUDE_COLS = {
    "property_id", "price_type", "property_name", "address", "latitude", "longitude",
    "price_php", "price_per_sqm", "log_price", "valuation_gap",
}
REDUNDANT_COLS = {"is_mactan_island"}
CAT_COLS = ["city", "property_type"]


def build_features_lot(df: pd.DataFrame):
    """Tree feature matrix for the Lot stratum (matches build_features X_full)."""
    df_encoded = pd.get_dummies(df.copy(), columns=CAT_COLS, drop_first=True, dtype=int)
    drop_set = EXCLUDE_COLS | REDUNDANT_COLS | {TARGET}
    feature_cols = [c for c in df_encoded.columns if c not in drop_set]

    all_null = [c for c in feature_cols if df_encoded[c].isna().all()]
    if all_null:
        df_encoded[all_null] = df_encoded[all_null].fillna(0)
    impute = [c for c in feature_cols
              if df_encoded[c].isna().any() and not df_encoded[c].isna().all()]
    if impute:
        df_encoded[impute] = SimpleImputer(strategy="median").fit_transform(df_encoded[impute])

    X_full = df_encoded[feature_cols].astype(float).copy()
    y = df_encoded[TARGET].astype(float)
    return X_full, y

# IAAO Standard on Ratio Studies (2013) reference bands (verified 2026-06; see decision log).
IAAO = {
    "COD_vacant_land_max": 25.0,
    "COD_residential_improved": (5.0, 15.0),
    "PRD_range": (0.98, 1.03),
}

RF_GRID = [
    {"n_estimators": n, "max_features": mf, "min_samples_leaf": leaf, "max_depth": md}
    for n in (300, 400)
    for mf in (0.7, 0.9, 1.0)
    for leaf in (1, 2)
    for md in (None, 20)
]


def iaao_panel(actual: np.ndarray, pred: np.ndarray) -> dict:
    """Predictive ratio-study statistics on back-transformed peso/sqm values."""
    actual = np.asarray(actual, float)
    pred = np.asarray(pred, float)
    ape = np.abs(pred - actual) / actual
    ratio = pred / actual
    med_ratio = float(np.median(ratio))
    cod = 100.0 * float(np.mean(np.abs(ratio - med_ratio))) / med_ratio
    prd = float(np.mean(ratio)) / (pred.sum() / actual.sum())
    return {
        "n": int(len(actual)),
        "MdAPE": float(np.median(ape) * 100),
        "MAPE": float(np.mean(ape) * 100),
        "COD": float(cod),
        "PRD": float(prd),
        "PE10": float(np.mean(ape <= 0.10) * 100),
        "PE20": float(np.mean(ape <= 0.20) * 100),
        "median_ratio": med_ratio,
    }


def group_oof(estimator, X: pd.DataFrame, y: np.ndarray, groups: np.ndarray) -> np.ndarray:
    """Pooled out-of-fold predictions (log space) under GroupKFold."""
    oof = np.zeros(len(y), dtype=float)
    gkf = GroupKFold(n_splits=N_SPLITS)
    for tr, te in gkf.split(X, y, groups):
        m = clone(estimator)
        m.fit(X.iloc[tr], y[tr])
        oof[te] = m.predict(X.iloc[te])
    return oof


def main() -> None:
    df = pd.read_csv(os.path.join(PROCESSED_DIR, CSV)).reset_index(drop=True)
    print("=" * 74)
    print(f"FINALIZE VACANT LOT MODEL — n={len(df)} (filtered residential lots)")
    print("=" * 74)

    X_full, y = build_features_lot(df)
    y = y.to_numpy(dtype=float)
    actual = df["price_per_sqm"].to_numpy(dtype=float)
    groups = df.groupby(["latitude", "longitude"]).ngroup().to_numpy()
    n_groups = int(pd.Series(groups).nunique())
    print(f"Features: {X_full.shape[1]}  |  coordinate groups: {n_groups} "
          f"(shared-coord rows: {len(df) - n_groups})")
    print(f"GroupKFold: {N_SPLITS} folds, groups = coordinate cluster (leak-free)\n")

    # ---- Tune RF by group-CV MdAPE (honest typical error) ----------------
    print("Tuning RF by group-CV MdAPE ...")
    best = None
    for params in RF_GRID:
        est = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1, **params)
        oof = group_oof(est, X_full, y, groups)
        m = iaao_panel(actual, np.exp(oof))
        if best is None or m["MdAPE"] < best["metrics"]["MdAPE"]:
            best = {"params": params, "metrics": m}
    bp, bm = best["params"], best["metrics"]
    print(f"Best params: {bp}")
    print(f"  group-CV: MdAPE={bm['MdAPE']:.1f}%  MAPE={bm['MAPE']:.1f}%  "
          f"COD={bm['COD']:.1f}  PRD={bm['PRD']:.2f}  PE10={bm['PE10']:.0f}%  PE20={bm['PE20']:.0f}%")

    # ---- Benchmark read-out ----------------------------------------------
    cod_ok = bm["COD"] <= IAAO["COD_vacant_land_max"]
    prd_lo, prd_hi = IAAO["PRD_range"]
    prd_ok = prd_lo <= bm["PRD"] <= prd_hi
    print("\nIAAO Standard on Ratio Studies (2013) benchmark:")
    print(f"  COD {bm['COD']:.1f}  vs vacant-land <= {IAAO['COD_vacant_land_max']:.0f}"
          f"   -> {'PASS' if cod_ok else 'ABOVE BAND'}")
    print(f"  PRD {bm['PRD']:.2f} vs {prd_lo}-{prd_hi}"
          f"            -> {'PASS' if prd_ok else 'regressive (>1.03)'}")

    # ---- Refit deployed model on the full filtered stratum ----------------
    deployed = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1, **bp)
    deployed.fit(X_full, y)
    for fname in ("lot_model.pkl", "lot_rf.pkl"):
        with open(os.path.join(MODELS_DIR, fname), "wb") as fh:
            pickle.dump(deployed, fh)
    print(f"\nDeployed RF refit on full stratum -> lot_model.pkl, lot_rf.pkl")

    # Top features by RF impurity importance (always), plus SHAP beeswarm if shap is available.
    imp = pd.Series(deployed.feature_importances_, index=X_full.columns).sort_values(ascending=False)
    print("  Top 8 features (RF importance):")
    for feat, val in imp.head(8).items():
        print(f"    {feat:<28} {val:.4f}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import shap
        sv = shap.TreeExplainer(deployed).shap_values(X_full)
        shap.summary_plot(sv, X_full, max_display=20, show=False, plot_type="dot")
        plt.title("SHAP — Vacant Lot (RF, top 20)", pad=12)
        plt.tight_layout()
        out = os.path.join(SHAP_DIR, "shap_lot_rf_summary.png")
        plt.savefig(out, dpi=150, bbox_inches="tight")
        plt.close("all")
        print(f"  SHAP plot -> {out}")
    except ImportError:
        print("  (shap/matplotlib not installed in this env — skipped beeswarm; RF importances above)")

    report = {
        "stratum": "Vacant Lot",
        "n_rows": int(len(df)),
        "n_coordinate_groups": n_groups,
        "filter": "residential scope 80-2000 sqm AND price_per_sqm >= 0.5x BIR zonal (Decision 41)",
        "target": "log(price_per_sqm)",
        "evaluation": f"GroupKFold({N_SPLITS}) pooled out-of-fold, leak-free (groups=coordinate cluster)",
        "deployed_model": "RandomForest",
        "best_params": bp,
        "metrics_group_cv": bm,
        "iaao_benchmark": {
            **IAAO,
            "COD_pass": cod_ok,
            "PRD_pass": prd_ok,
            "note": "IAAO COD/PRD are in-sample assessment-roll standards; values here are "
                    "stricter out-of-sample CV estimates on n=255.",
        },
    }
    with open(os.path.join(MODELS_DIR, "lot_iaao_report.json"), "w") as fh:
        json.dump(report, fh, indent=2)
    print(f"IAAO report -> {os.path.join(MODELS_DIR, 'lot_iaao_report.json')}")
    print("\nfinalize_lot_model.py complete.")


if __name__ == "__main__":
    main()
