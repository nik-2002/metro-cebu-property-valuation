"""
finalize_stratified_groupcv.py
==============================
Authoritative honest-reporting + deployment for ALL THREE strata (Decision 42).

Generalizes Decision 41 (Lot) to Condo and Houses:
  - Leak-free evaluation via GroupKFold (groups = coordinate cluster), so the 109+ rows
    that share coordinates (barangay-centroid geocodes + relistings) never straddle folds.
    Ordinary held-out / ungrouped k-fold is optimistic on this data.
  - Deploy Random Forest for every stratum, tuned by group-CV MdAPE. This reverts the
    Decision 40 Houses->XGB-tuned switch, which won on a 0.22pp k-fold MAPE edge (noise).
  - Report the IAAO Standard on Ratio Studies (2013) panel: MdAPE, COD, PRD, PE10/PE20.
    Bands: COD residential improved 5-15, vacant land <=25; PRD 0.98-1.03.

Reads the three stratum CSVs from Data/processed/ (Lot already scope-filtered to n=255 by
prepare_stratified_abt.py, Decision 41). Rewrites deployment_manifest.json with leak-free
metrics for all three. Saves {stratum}_model.pkl + {stratum}_rf.pkl refit on the full stratum.

Note: this env lacks xgboost; RF is deployed (it won or tied the alternatives under honest
group-CV — see Decision 41). SHAP beeswarm is written if shap is installed, else RF
importances are printed.
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
N_SPLITS = 5
TARGET = "log_price"

STRATA = {
    "condo":  {"csv": "abt_condo.csv",  "label": "Condominium", "iaao_cod_max": 15.0, "iaao_kind": "residential improved"},
    "houses": {"csv": "abt_houses.csv", "label": "Houses",      "iaao_cod_max": 15.0, "iaao_kind": "residential improved"},
    "lot":    {"csv": "abt_lot.csv",    "label": "Vacant Lot",  "iaao_cod_max": 25.0, "iaao_kind": "vacant land"},
}

EXCLUDE_COLS = {
    "property_id", "price_type", "property_name", "address", "latitude", "longitude",
    "price_php", "price_per_sqm", "log_price", "valuation_gap",
}
REDUNDANT_COLS = {"is_mactan_island"}
CAT_COLS = ["city", "property_type"]
PRD_RANGE = (0.98, 1.03)

RF_GRID = [
    {"n_estimators": n, "max_features": mf, "min_samples_leaf": leaf, "max_depth": md}
    for n in (300, 400)
    for mf in (0.7, 0.9, 1.0)
    for leaf in (1, 2)
    for md in (None, 20)
]

# Per-stratum feature selection (Decision 47i, 2026-06-15) — EDA-grounded (VIF, OLS sig,
# leave-one-block-out, MCRAI internal corr 0.57-0.96):
#   ALL strata drop: bir_zonal_rr_log (=log of rr_median), bir_zonal_cr_median (commercial,
#                    not OLS-sig, corr 0.59), both ROAD distances (not sig, ~0 ablation).
#   Condo+Houses additionally collapse MCRAI to mcrai_composite only (8 individuals dropped —
#                    they're 0.57-0.96 inter-correlated; composite carries 0.79-0.96 of each;
#                    composite-only improved condo 19.8->19.1, houses parity).
#   Lot KEEPS the individual MCRAI (grocery/hospitals are OLS-significant land-value signals;
#                    collapsing cost lots +1.1pp).
_ROAD = ["dist_to_trunk_road_m", "dist_to_primary_road_m"]
_BIR_EXTRA = ["bir_zonal_rr_log", "bir_zonal_cr_median"]
_MCRAI_INDIV = ["mcrai_education", "mcrai_grocery", "mcrai_health", "mcrai_hospitals",
                "mcrai_recreation", "mcrai_security", "mcrai_tourism", "mcrai_retail_density"]
STRATUM_DROP = {
    "condo":  _ROAD + _BIR_EXTRA + _MCRAI_INDIV,   # MCRAI -> composite only
    "houses": _ROAD + _BIR_EXTRA + _MCRAI_INDIV,   # MCRAI -> composite only
    # Lot keeps the individual MCRAI, but drops: (a) mcrai_composite — an EXACT linear blend of
    # education/grocery/recreation (R^2=1.0 vs the individuals -> perfect collinearity); (b)
    # mcrai_security — 36.9% zero-rate, LGU-uneven data gap, OLS-insignificant, lowest RF
    # importance; (c) mcrai_retail_density — univariate corr w/ lot price +0.047 (~noise),
    # OLS sig-negative artifact, free to drop (ablation -0.1pp).
    # (Decision 49, investigate_mcrai_lot_2026-06-15.py.)
    "lot":    _ROAD + _BIR_EXTRA + ["mcrai_composite", "mcrai_security", "mcrai_retail_density"],
}


def build_features(df: pd.DataFrame):
    """Tree feature matrix (matches run_models_stratified.build_features X_full)."""
    enc = pd.get_dummies(df.copy(), columns=CAT_COLS, drop_first=True, dtype=int)
    drop_set = EXCLUDE_COLS | REDUNDANT_COLS | {TARGET}
    cols = [c for c in enc.columns if c not in drop_set]
    all_null = [c for c in cols if enc[c].isna().all()]
    if all_null:
        enc[all_null] = enc[all_null].fillna(0)
    impute = [c for c in cols if enc[c].isna().any() and not enc[c].isna().all()]
    if impute:
        enc[impute] = SimpleImputer(strategy="median").fit_transform(enc[impute])
    return enc[cols].astype(float).copy(), enc[TARGET].astype(float)


def iaao_panel(actual, pred):
    actual = np.asarray(actual, float); pred = np.asarray(pred, float)
    ape = np.abs(pred - actual) / actual
    ratio = pred / actual
    med = float(np.median(ratio))
    return {
        "n": int(len(actual)),
        "MdAPE": float(np.median(ape) * 100), "MAPE": float(np.mean(ape) * 100),
        "COD": 100.0 * float(np.mean(np.abs(ratio - med))) / med,
        "PRD": float(np.mean(ratio)) / (pred.sum() / actual.sum()),
        "PE10": float(np.mean(ape <= 0.10) * 100), "PE20": float(np.mean(ape <= 0.20) * 100),
        "median_ratio": med,
    }


def group_oof(estimator, X, y, groups):
    oof = np.zeros(len(y), float)
    for tr, te in GroupKFold(n_splits=N_SPLITS).split(X, y, groups):
        m = clone(estimator); m.fit(X.iloc[tr], y[tr]); oof[te] = m.predict(X.iloc[te])
    return oof


def try_shap(model, X, key, label):
    imp = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
    print("  Top 6 (RF importance): " + ", ".join(f"{f}={v:.3f}" for f, v in imp.head(6).items()))
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import shap
        sv = shap.TreeExplainer(model).shap_values(X)
        shap.summary_plot(sv, X, max_display=20, show=False, plot_type="dot")
        plt.title(f"SHAP — {label} (RF, top 20)", pad=12); plt.tight_layout()
        out = os.path.join(SHAP_DIR, f"shap_{key}_rf_summary.png")
        plt.savefig(out, dpi=150, bbox_inches="tight"); plt.close("all")
        print(f"  SHAP plot -> {out}")
    except ImportError:
        print("  (shap/matplotlib missing — beeswarm skipped)")


def fit_stratum(key, cfg):
    df = pd.read_csv(os.path.join(PROCESSED_DIR, cfg["csv"])).reset_index(drop=True)
    X, y_s = build_features(df)
    drop = [c for c in STRATUM_DROP.get(key, []) if c in X.columns]
    if drop:
        X = X.drop(columns=drop)
        print(f"  per-stratum feature selection: dropped {len(drop)} cols -> {X.shape[1]} features")
    y = y_s.to_numpy(float)
    actual = df["price_per_sqm"].to_numpy(float)
    groups = df.groupby(["latitude", "longitude"]).ngroup().to_numpy()
    n_groups = int(pd.Series(groups).nunique())
    print("\n" + "=" * 72)
    print(f"{cfg['label']}  n={len(df)}  features={X.shape[1]}  coord-groups={n_groups}")
    print("=" * 72)

    best = None
    for p in RF_GRID:
        est = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1, **p)
        m = iaao_panel(actual, np.exp(group_oof(est, X, y, groups)))
        if best is None or m["MdAPE"] < best["m"]["MdAPE"]:
            best = {"p": p, "m": m}
    bp, bm = best["p"], best["m"]
    cod_ok = bool(bm["COD"] <= cfg["iaao_cod_max"])
    prd_ok = bool(PRD_RANGE[0] <= bm["PRD"] <= PRD_RANGE[1])
    print(f"Best RF {bp}")
    print(f"  group-CV: MdAPE={bm['MdAPE']:.1f}%  MAPE={bm['MAPE']:.1f}%  COD={bm['COD']:.1f}"
          f"  PRD={bm['PRD']:.2f}  PE10={bm['PE10']:.0f}%  PE20={bm['PE20']:.0f}%")
    print(f"  IAAO ({cfg['iaao_kind']}): COD<= {cfg['iaao_cod_max']:.0f} -> {'PASS' if cod_ok else 'ABOVE'}"
          f" | PRD {PRD_RANGE[0]}-{PRD_RANGE[1]} -> {'PASS' if prd_ok else 'regressive'}")

    model = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1, **bp)
    model.fit(X, y)
    for fn in (f"{key}_model.pkl", f"{key}_rf.pkl"):
        with open(os.path.join(MODELS_DIR, fn), "wb") as fh:
            pickle.dump(model, fh)
    try_shap(model, X, key, cfg["label"])

    return {
        "label": cfg["label"], "n_rows": int(len(df)), "n_coordinate_groups": n_groups,
        "deployed_family": "Random Forest", "best_params": bp,
        "evaluation": f"GroupKFold({N_SPLITS}) pooled out-of-fold, leak-free (groups=coordinate cluster)",
        "selection_basis": "lowest group-CV MdAPE among RF grid",
        "metrics_group_cv": bm,
        "iaao_benchmark": {"kind": cfg["iaao_kind"], "COD_max": cfg["iaao_cod_max"],
                           "PRD_range": list(PRD_RANGE), "COD_pass": cod_ok, "PRD_pass": prd_ok},
        "model_file": f"{key}_model.pkl",
        "features": list(X.columns),
    }


def main():
    print("STRATIFIED HONEST FINALIZE — RF, GroupKFold, IAAO panel (Decision 42)")
    results = {k: fit_stratum(k, cfg) for k, cfg in STRATA.items()}

    mp = os.path.join(MODELS_DIR, "deployment_manifest.json")
    if os.path.exists(mp):
        with open(mp) as fh:
            old = fh.read()
        with open(os.path.join(MODELS_DIR, "deployment_manifest.backup_pre_groupcv.json"), "w") as fh:
            fh.write(old)

    manifest = {
        "random_state": RANDOM_STATE,
        "target": "log_price = log(price_per_sqm)  (Decision 34)",
        "prediction": "exp(model output) = price_per_sqm; total price = price_per_sqm * area_sqm",
        "evaluation": "GroupKFold(5) leak-free, groups = coordinate cluster (Decision 42)",
        "deployment": "Random Forest per stratum, tuned by group-CV MdAPE",
        "iaao_reference": "IAAO Standard on Ratio Studies (2013): COD residential improved 5-15, "
                          "vacant land <=25; PRD 0.98-1.03. In-sample assessment-roll bands; values "
                          "here are stricter out-of-sample CV estimates.",
        "strata": results,
    }
    with open(mp, "w") as fh:
        json.dump(manifest, fh, indent=2)

    print("\n" + "=" * 72)
    print(f"{'DEPLOYED (group-CV, RF)':<14}{'n':>5}{'MdAPE':>8}{'COD':>7}{'PRD':>6}{'PE20':>6}  IAAO-COD")
    print("=" * 72)
    for k, r in results.items():
        m = r["metrics_group_cv"]
        verdict = "PASS" if r["iaao_benchmark"]["COD_pass"] else "above"
        print(f"{r['label']:<14}{r['n_rows']:>5}{m['MdAPE']:>8.1f}{m['COD']:>7.1f}{m['PRD']:>6.2f}"
              f"{m['PE20']:>6.0f}  {verdict} (<= {r['iaao_benchmark']['COD_max']:.0f})")
    print(f"\nManifest rewritten -> {mp}")


if __name__ == "__main__":
    main()
