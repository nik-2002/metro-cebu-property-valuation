"""
answer_rq2_rq3.py
=================
Read-only analysis that closes two research-question gaps under the SAME leak-free
evaluation used for deployment (Decision 42 / Decision 44).

RQ2 — fair model head-to-head: OLS vs Random Forest vs XGBoost, all scored under the
       SAME GroupKFold(5) grouped by coordinate cluster. Headline metric MdAPE/PE20.
RQ3 — geospatial ablation: the SAME RF (deployed best params) on three nested feature
       tiers (Structural -> +Admin location -> +Engineered geospatial), same folds,
       to measure how much the engineered geospatial features actually add.

Reuses the exact feature spec of run_models_stratified.build_features and the leak-free
harness of finalize_stratified_groupcv.py. Writes new CSVs only; touches no model,
manifest, or ABT.

Outputs:
    Models/stratified/model_comparison_groupcv.csv   (RQ2)
    Models/stratified/ablation_groupcv.csv           (RQ3)
"""

import json
import os

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GroupKFold

try:
    from xgboost import XGBRegressor
    HAVE_XGB = True
except ImportError:
    HAVE_XGB = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
THESIS_DIR = os.path.dirname(SCRIPT_DIR)
PROCESSED_DIR = os.path.join(THESIS_DIR, "Data", "processed")
MODELS_DIR = os.path.join(THESIS_DIR, "Models", "stratified")
MANIFEST = os.path.join(MODELS_DIR, "deployment_manifest.json")

RANDOM_STATE = 42
N_SPLITS = 5
TARGET = "log_price"

STRATA = {
    "condo":  {"csv": "abt_condo.csv",  "label": "Condominium"},
    "houses": {"csv": "abt_houses.csv", "label": "Houses"},
    "lot":    {"csv": "abt_lot.csv",    "label": "Vacant Lot"},
}

# Mirror run_models_stratified.py exactly.
ALL_CBD = [
    "dist_cebu_business_park_m", "dist_mandaue_cbd_m", "dist_mactan_cbd_m",
    "dist_srp_m", "dist_talisay_tabunok_m", "dist_consolacion_m",
    "dist_naga_city_m", "dist_airport_m",
]
CBD_TOP2 = {
    "condo":  ["dist_cebu_business_park_m", "dist_talisay_tabunok_m"],
    "houses": ["dist_cebu_business_park_m", "dist_mandaue_cbd_m"],
    "lot":    ["dist_cebu_business_park_m", "dist_mandaue_cbd_m"],
}
EXCLUDE_COLS = {
    "property_id", "price_type", "property_name", "address", "latitude", "longitude",
    "price_php", "price_per_sqm", "log_price", "valuation_gap",
}
REDUNDANT_COLS = {"is_mactan_island"}
CAT_COLS = ["city", "property_type"]

XGB_GRID = [
    {"n_estimators": n, "max_depth": d, "learning_rate": lr, "subsample": 0.9}
    for n in (300, 500)
    for d in (3, 5)
    for lr in (0.05, 0.1)
]


def build_full_and_ols(df: pd.DataFrame, stratum_key: str):
    """Return (X_full, X_ols, y) matching run_models_stratified.build_features."""
    enc = pd.get_dummies(df.copy(), columns=CAT_COLS, drop_first=True, dtype=int)
    drop_set = EXCLUDE_COLS | REDUNDANT_COLS | {TARGET}
    feature_cols = [c for c in enc.columns if c not in drop_set]

    all_null = [c for c in feature_cols if enc[c].isna().all()]
    if all_null:
        enc[all_null] = enc[all_null].fillna(0)
    impute_cols = [c for c in feature_cols if enc[c].isna().any() and not enc[c].isna().all()]
    if impute_cols:
        enc[impute_cols] = SimpleImputer(strategy="median").fit_transform(enc[impute_cols])

    enc["log_area_sqm"] = np.log1p(enc["area_sqm"])
    y = enc[TARGET].astype(float)
    X_full = enc[feature_cols].astype(float).copy()

    cbd_drop = [c for c in ALL_CBD if c not in CBD_TOP2[stratum_key]]
    ols_drop = set(cbd_drop) | {"mcrai_composite", "bir_zonal_rr_median", "area_sqm"}
    X_ols = X_full.drop(columns=[c for c in ols_drop if c in X_full.columns]).copy()
    X_ols["log_area_sqm"] = enc["log_area_sqm"].astype(float).values
    return X_full, X_ols, y


def iaao_panel(actual, pred):
    """Identical to finalize_stratified_groupcv.iaao_panel."""
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
    """Leak-free out-of-fold predictions (log scale)."""
    oof = np.zeros(len(y), float)
    for tr, te in GroupKFold(n_splits=N_SPLITS).split(X, y, groups):
        m = clone(estimator); m.fit(X.iloc[tr], y[tr]); oof[te] = m.predict(X.iloc[te])
    return oof


def rf_best_params():
    with open(MANIFEST) as fh:
        man = json.load(fh)
    return {k: man["strata"][k]["best_params"] for k in STRATA}, man


def tier_columns(X_full):
    cols = list(X_full.columns)
    structural = ([c for c in ["area_sqm", "bedrooms", "bathrooms",
                               "bedrooms_imputed", "bathrooms_imputed"] if c in cols]
                  + [c for c in cols if c.startswith("property_type_")])
    admin = structural + [c for c in cols if c.startswith("city_")] \
        + [c for c in ["bir_zonal_rr_median", "bir_zonal_rr_log", "bir_zonal_cr_median"] if c in cols]
    geo = [c for c in cols if c.startswith("dist_") or c.startswith("mcrai_")] \
        + [c for c in ["spatial_lag_price"] if c in cols]
    full = admin + geo
    # de-dup while preserving order
    def uniq(seq):
        seen = set(); return [x for x in seq if not (x in seen or seen.add(x))]
    return {"1_structural": uniq(structural), "2_+admin": uniq(admin), "3_+geospatial": uniq(full)}


def main():
    best_params, man = rf_best_params()
    print("=" * 80)
    print("RQ2 + RQ3 — leak-free GroupKFold(5) by coordinate cluster")
    print(f"xgboost available: {HAVE_XGB}")
    print("=" * 80)

    rq2_rows, rq3_rows = [], []

    for key, cfg in STRATA.items():
        df = pd.read_csv(os.path.join(PROCESSED_DIR, cfg["csv"])).reset_index(drop=True)
        X_full, X_ols, y_s = build_full_and_ols(df, key)
        y = y_s.to_numpy(float)
        actual = df["price_per_sqm"].to_numpy(float)
        groups = df.groupby(["latitude", "longitude"]).ngroup().to_numpy()
        bp = best_params[key]

        print(f"\n{'-'*80}\n{cfg['label']}  n={len(df)}  X_full={X_full.shape[1]}  "
              f"X_ols={X_ols.shape[1]}  coord-groups={pd.Series(groups).nunique()}\n{'-'*80}")

        # ---------- RQ2: OLS vs RF vs XGB (same folds) ----------
        ols = LinearRegression()
        m_ols = iaao_panel(actual, np.exp(group_oof(ols, X_ols, y, groups)))

        rf = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1, **bp)
        m_rf = iaao_panel(actual, np.exp(group_oof(rf, X_full, y, groups)))

        models = [("OLS", m_ols), ("Random Forest", m_rf)]

        if HAVE_XGB:
            best_xgb = None
            for p in XGB_GRID:
                est = XGBRegressor(random_state=RANDOM_STATE, n_jobs=-1, verbosity=0, **p)
                m = iaao_panel(actual, np.exp(group_oof(est, X_full, y, groups)))
                if best_xgb is None or m["MdAPE"] < best_xgb[1]["MdAPE"]:
                    best_xgb = (p, m)
            models.append(("XGBoost", best_xgb[1]))
            print(f"  XGB best grid: {best_xgb[0]}")

        # sanity: RF must match manifest metrics_group_cv
        man_md = man["strata"][key]["metrics_group_cv"]["MdAPE"]
        flag = "PASS" if abs(m_rf["MdAPE"] - man_md) < 0.5 else "CHECK"
        print(f"  RF MdAPE {m_rf['MdAPE']:.2f}% vs manifest {man_md:.2f}% -> {flag}")

        for name, m in models:
            print(f"  {name:<14} MdAPE={m['MdAPE']:6.2f}%  PE20={m['PE20']:5.1f}%  "
                  f"MAPE={m['MAPE']:6.2f}%  COD={m['COD']:5.1f}  PRD={m['PRD']:.2f}")
            rq2_rows.append({"stratum": cfg["label"], "model": name, "n": m["n"],
                             "MdAPE": m["MdAPE"], "PE20": m["PE20"], "MAPE": m["MAPE"],
                             "COD": m["COD"], "PRD": m["PRD"], "PE10": m["PE10"]})

        # ---------- RQ3: geospatial ablation (same RF, same folds) ----------
        tiers = tier_columns(X_full)
        print("  Ablation (RF, same folds):")
        prev = {}
        for tname, tcols in tiers.items():
            rf_t = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1, **bp)
            m = iaao_panel(actual, np.exp(group_oof(rf_t, X_full[tcols], y, groups)))
            print(f"    {tname:<14} ({len(tcols):>2} feats)  MdAPE={m['MdAPE']:6.2f}%  PE20={m['PE20']:5.1f}%")
            rq3_rows.append({"stratum": cfg["label"], "tier": tname, "n_feats": len(tcols),
                             "n": m["n"], "MdAPE": m["MdAPE"], "PE20": m["PE20"], "MAPE": m["MAPE"]})
            prev[tname] = m
        up13 = prev["1_structural"]["MdAPE"] - prev["3_+geospatial"]["MdAPE"]
        up23 = prev["2_+admin"]["MdAPE"] - prev["3_+geospatial"]["MdAPE"]
        print(f"    uplift  Structural->Full ΔMdAPE={up13:+.2f}pp   "
              f"+Admin->+Geospatial ΔMdAPE={up23:+.2f}pp (pure geospatial)")

    comp = pd.DataFrame(rq2_rows)
    abl = pd.DataFrame(rq3_rows)
    comp.to_csv(os.path.join(MODELS_DIR, "model_comparison_groupcv.csv"), index=False)
    abl.to_csv(os.path.join(MODELS_DIR, "ablation_groupcv.csv"), index=False)
    print("\nWrote model_comparison_groupcv.csv and ablation_groupcv.csv")


if __name__ == "__main__":
    main()
