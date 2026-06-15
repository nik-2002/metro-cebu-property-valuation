"""
run_models_stratified.py
========================
Per-stratum modeling for the Metro Cebu residential valuation thesis
(redefense remediation, Phase 4).

Reads the three cleaned, deduplicated stratum ABTs produced by
prepare_stratified_abt.py (Decisions 31-34):
    Data/processed/abt_condo.csv   (Condominium, 654 rows)
    Data/processed/abt_houses.csv  (Single Detached + House and Lot + Townhouse + Apartment, 558)
    Data/processed/abt_lot.csv     (Vacant Lot, 204)

TARGET (Decision 34): log_price = log(price_per_sqm). Predictions are per-sqm;
total price = exp(prediction) * area_sqm. Metrics are reported per-sqm (primary,
matches the deliverable) and on total price (for comparison with the old global
total-price baseline RF: R2=0.807, MAPE=59.28%).

For each stratum: OLS (comparator) -> Random Forest -> XGBoost, SHAP on the best
tree model, and deploy the best-per-stratum tree model by lowest test MAPE.

Modeling spec (Decisions 32 + 34):
  - OLS: drop mcrai_composite (VIF ~1e11), drop raw bir_zonal_rr_median (keep log),
         trim CBD distances to top-2 per stratum, log-transform area, HC3 robust SE.
  - RF / XGBoost: full feature set (composite, raw BIR, all 8 CBDs retained).
  - is_mactan_island DROPPED from all feature sets (identical to city_Lapu-Lapu City;
    verified 291/291, 126/126, 44/44).
  - latitude/longitude are NOT model features (location via CBD distances, city dummies,
    spatial_lag_price) — matches the stratified EDA feature universe.
  - spatial_lag_price retained on predictive grounds (strong Spearman rho).
  - is_ceiling_price / price_type are not features (retired leftover, Decision 34c).

Writes:
    Models/stratified/{condo,houses,lot}_model.pkl   (deployed best tree model)
    Models/stratified/{condo,houses,lot}_rf.pkl / _xgb.pkl   (reference)
    Models/stratified/ols_summary_{stratum}.txt
    Models/stratified/model_comparison_stratified.csv
    Models/stratified/deployment_manifest.json
    EDA/plots/10_stratified_models/shap_{stratum}_{family}_summary.png
"""

import json
import os
import pickle

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
import statsmodels.api as sm
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
THESIS_DIR = os.path.dirname(SCRIPT_DIR)            # thesis_main/
ROOT_DIR   = os.path.dirname(THESIS_DIR)            # workspace root (16 Thesis/)

PROCESSED_DIR = os.path.join(THESIS_DIR, "Data", "processed")
MODELS_DIR    = os.path.join(THESIS_DIR, "Models", "stratified")
SHAP_DIR      = os.path.join(ROOT_DIR, "EDA", "plots", "10_stratified_models")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(SHAP_DIR, exist_ok=True)

RANDOM_STATE = 42
TEST_SIZE = 0.20

# ---------------------------------------------------------------------------
# Stratum configuration
# ---------------------------------------------------------------------------
ALL_CBD = [
    "dist_cebu_business_park_m", "dist_mandaue_cbd_m", "dist_mactan_cbd_m",
    "dist_srp_m", "dist_talisay_tabunok_m", "dist_consolacion_m",
    "dist_naga_city_m", "dist_airport_m",
]

# Top-2 CBD distances per stratum, by |Spearman rho| with price_per_sqm
# (eda_stratified_v2_run.log Section 4; Decision 32 Flag 2).
CBD_TOP2 = {
    "condo":  ["dist_cebu_business_park_m", "dist_talisay_tabunok_m"],
    "houses": ["dist_cebu_business_park_m", "dist_mandaue_cbd_m"],
    "lot":    ["dist_cebu_business_park_m", "dist_mandaue_cbd_m"],
}

STRATA = {
    "condo":  {"csv": "abt_condo.csv",  "label": "Condominium"},
    "houses": {"csv": "abt_houses.csv", "label": "Houses"},
    "lot":    {"csv": "abt_lot.csv",    "label": "Vacant Lot"},
}

TARGET = "log_price"  # = log(price_per_sqm) after Decision 34

# Identifiers / targets / leakage — never model features.
EXCLUDE_COLS = {
    "property_id", "price_type", "property_name", "address",
    "latitude", "longitude",
    "price_php", "price_per_sqm", "log_price", "valuation_gap",
}

# Dropped from every feature set (perfectly redundant with city_Lapu-Lapu City).
REDUNDANT_COLS = {"is_mactan_island"}

CAT_COLS = ["city", "property_type"]


# ===========================================================================
# Evaluation — target is log(price_per_sqm)
# ===========================================================================
def evaluate(y_true_log, y_pred_log, model_name: str, area_sqm) -> dict:
    """Per-sqm metrics (primary) + total-price metrics (for baseline comparison).

    MAPE is identical on per-sqm and total price (area cancels in the ratio).
    """
    psqm_true = np.exp(np.asarray(y_true_log, dtype=float))
    psqm_pred = np.exp(np.asarray(y_pred_log, dtype=float))
    ape = np.abs((psqm_true - psqm_pred) / psqm_true)
    mape = float(np.mean(ape) * 100)
    med_ape = float(np.median(ape) * 100)  # Decision 38e: honest typical error
    r2_sqm   = r2_score(psqm_true, psqm_pred)
    mae_sqm  = mean_absolute_error(psqm_true, psqm_pred)
    rmse_sqm = float(np.sqrt(mean_squared_error(psqm_true, psqm_pred)))

    area = np.asarray(area_sqm, dtype=float)
    total_true = psqm_true * area
    total_pred = psqm_pred * area
    r2_total   = r2_score(total_true, total_pred)
    mae_total  = mean_absolute_error(total_true, total_pred)
    rmse_total = float(np.sqrt(mean_squared_error(total_true, total_pred)))

    print(f"  {model_name:<14} MAPE={mape:6.2f}%  MdAPE={med_ape:6.2f}%  R2(psqm)={r2_sqm:7.4f}  "
          f"R2(total)={r2_total:7.4f}  MAE=PHP {mae_sqm:,.0f}/sqm  MAE(total)=PHP {mae_total:,.0f}")
    return {
        "Model": model_name, "MAPE": mape, "MdAPE": med_ape,
        "R2_sqm": r2_sqm, "MAE_sqm": mae_sqm, "RMSE_sqm": rmse_sqm,
        "R2_total": r2_total, "MAE_total": mae_total, "RMSE_total": rmse_total,
    }


def run_shap(model, X_test, stratum_key: str, family: str) -> None:
    """TreeExplainer SHAP beeswarm for the deployed model; saved to SHAP_DIR."""
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)
    if isinstance(shap_values, list):
        shap_values = shap_values[0]

    mean_abs = pd.Series(np.abs(shap_values).mean(axis=0), index=X_test.columns)
    mean_abs = mean_abs.sort_values(ascending=False)
    print(f"  Top 8 features by mean |SHAP| ({family}):")
    for feat, val in mean_abs.head(8).items():
        print(f"    {feat:<28} {val:.5f}")

    shap.summary_plot(shap_values, X_test, max_display=20, show=False, plot_type="dot")
    plt.title(f"SHAP — {STRATA[stratum_key]['label']} ({family.upper()}, top 20)", pad=12)
    plt.tight_layout()
    out_path = os.path.join(SHAP_DIR, f"shap_{stratum_key}_{family}_summary.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close("all")
    print(f"  SHAP plot -> {out_path}")


# ===========================================================================
# Per-stratum pipeline
# ===========================================================================
def build_features(df: pd.DataFrame, stratum_key: str):
    """Return (X_full, X_ols, y, area_sqm_series) for one stratum."""
    df = df.copy()

    # One-hot city + property_type (drop_first => Cebu City / Apartment reference).
    # Condo and Lot have a single property_type, so drop_first removes it entirely.
    df_encoded = pd.get_dummies(df, columns=CAT_COLS, drop_first=True, dtype=int)

    drop_set = EXCLUDE_COLS | REDUNDANT_COLS | {TARGET}
    feature_cols = [c for c in df_encoded.columns if c not in drop_set]

    all_null = [c for c in feature_cols if df_encoded[c].isna().all()]
    if all_null:
        print(f"  All-null columns filled with 0: {all_null}")
        df_encoded[all_null] = df_encoded[all_null].fillna(0)
    impute_cols = [c for c in feature_cols
                   if df_encoded[c].isna().any() and not df_encoded[c].isna().all()]
    if impute_cols:
        print(f"  Median-imputed columns: {impute_cols}")
        imputer = SimpleImputer(strategy="median")
        df_encoded[impute_cols] = imputer.fit_transform(df_encoded[impute_cols])

    # log-area for the log-log hedonic OLS spec (Decision 13).
    df_encoded["log_area_sqm"] = np.log1p(df_encoded["area_sqm"])

    y = df_encoded[TARGET].astype(float)
    X_full = df_encoded[feature_cols].astype(float).copy()

    # OLS feature set: Decision 32 drops + per-stratum CBD trim + log-area.
    cbd_drop = [c for c in ALL_CBD if c not in CBD_TOP2[stratum_key]]
    ols_drop = set(cbd_drop) | {"mcrai_composite", "bir_zonal_rr_median", "area_sqm"}
    X_ols = X_full.drop(columns=[c for c in ols_drop if c in X_full.columns]).copy()
    X_ols["log_area_sqm"] = df_encoded["log_area_sqm"].astype(float).values

    return X_full, X_ols, y, df_encoded["area_sqm"].astype(float)


def fit_stratum(stratum_key: str) -> dict:
    cfg = STRATA[stratum_key]
    print("\n" + "=" * 78)
    print(f"STRATUM: {cfg['label']}  ({cfg['csv']})")
    print("=" * 78)

    df = pd.read_csv(os.path.join(PROCESSED_DIR, cfg["csv"]))
    print(f"Rows: {len(df):,}")

    X_full, X_ols, y, area = build_features(df, stratum_key)
    print(f"X_full features: {X_full.shape[1]}  |  X_ols features: {X_ols.shape[1]}")
    print(f"OLS CBD kept: {CBD_TOP2[stratum_key]}")

    idx = np.arange(len(y))
    (X_full_tr, X_full_te, X_ols_tr, X_ols_te,
     y_tr, y_te, idx_tr, idx_te) = train_test_split(
        X_full, X_ols, y, idx, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    area_te = area.to_numpy()[idx_te]
    print(f"Train: {len(y_tr):,}  Test: {len(y_te):,}")

    results = []

    # ---- OLS (comparator) -------------------------------------------------
    print("\n[OLS] statsmodels, HC3 robust SE")
    X_ols_tr_sm = sm.add_constant(X_ols_tr, has_constant="add")
    X_ols_te_sm = sm.add_constant(X_ols_te, has_constant="add")
    for col in X_ols_tr_sm.columns:
        if col not in X_ols_te_sm.columns:
            X_ols_te_sm[col] = 0
    X_ols_te_sm = X_ols_te_sm[X_ols_tr_sm.columns]
    ols = sm.OLS(y_tr, X_ols_tr_sm).fit(cov_type="HC3")
    results.append(evaluate(y_te, ols.predict(X_ols_te_sm), "OLS", area_te))
    with open(os.path.join(MODELS_DIR, f"ols_summary_{stratum_key}.txt"), "w") as fh:
        fh.write(ols.summary().as_text())

    # ---- Random Forest ----------------------------------------------------
    print("\n[RF] n_estimators=300")
    rf = RandomForestRegressor(n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1)
    rf.fit(X_full_tr, y_tr)
    rf_metrics = evaluate(y_te, rf.predict(X_full_te), "Random Forest", area_te)
    results.append(rf_metrics)
    with open(os.path.join(MODELS_DIR, f"{stratum_key}_rf.pkl"), "wb") as fh:
        pickle.dump(rf, fh)

    # ---- XGBoost ----------------------------------------------------------
    print("\n[XGB] n_estimators=300, lr=0.05, max_depth=6")
    xgbr = xgb.XGBRegressor(
        n_estimators=300, learning_rate=0.05, max_depth=6,
        random_state=RANDOM_STATE, verbosity=0,
    )
    xgbr.fit(X_full_tr, y_tr)
    xgb_metrics = evaluate(y_te, xgbr.predict(X_full_te), "XGBoost", area_te)
    results.append(xgb_metrics)
    with open(os.path.join(MODELS_DIR, f"{stratum_key}_xgb.pkl"), "wb") as fh:
        pickle.dump(xgbr, fh)

    # ---- Deployment selection: best tree model by lowest test MAPE --------
    tree_choices = {"Random Forest": (rf, rf_metrics), "XGBoost": (xgbr, xgb_metrics)}
    best_family = min(tree_choices, key=lambda k: tree_choices[k][1]["MAPE"])
    best_model, best_metrics = tree_choices[best_family]
    short = "rf" if best_family == "Random Forest" else "xgb"
    print(f"\n>> Deployed for {cfg['label']}: {best_family} "
          f"(MAPE={best_metrics['MAPE']:.2f}%, R2_sqm={best_metrics['R2_sqm']:.4f})")
    with open(os.path.join(MODELS_DIR, f"{stratum_key}_model.pkl"), "wb") as fh:
        pickle.dump(best_model, fh)

    print(f"\n[SHAP] {best_family}")
    run_shap(best_model, X_full_te, stratum_key, short)

    for row in results:
        row["Stratum"] = cfg["label"]
    return {
        "stratum_key": stratum_key,
        "label": cfg["label"],
        "n_rows": int(len(df)),
        "n_test": int(len(y_te)),
        "deployed_family": best_family,
        "deployed_features": list(X_full.columns),
        "deployed_metrics": {k: best_metrics[k] for k in
                             ("MAPE", "MdAPE", "R2_sqm", "MAE_sqm", "R2_total", "MAE_total")},
        "results": results,
    }


def main() -> None:
    print("=" * 78)
    print("STRATIFIED MODEL BUILD — target=log(price_per_sqm), best-per-stratum (RF/XGB)")
    print("=" * 78)

    summaries = [fit_stratum(k) for k in STRATA]

    all_rows = [r for s in summaries for r in s["results"]]
    comp = pd.DataFrame(all_rows)[
        ["Stratum", "Model", "MAPE", "MdAPE", "R2_sqm", "MAE_sqm", "RMSE_sqm",
         "R2_total", "MAE_total", "RMSE_total"]
    ]
    comp_path = os.path.join(MODELS_DIR, "model_comparison_stratified.csv")
    comp.to_csv(comp_path, index=False)

    print("\n" + "=" * 78)
    print("COMPARISON (all strata x all models)")
    print("=" * 78)
    show = comp.copy()
    show["MAPE"]     = show["MAPE"].map(lambda x: f"{x:.2f}%")
    show["MdAPE"]    = show["MdAPE"].map(lambda x: f"{x:.2f}%")
    show["R2_sqm"]   = show["R2_sqm"].map(lambda x: f"{x:.4f}")
    show["R2_total"] = show["R2_total"].map(lambda x: f"{x:.4f}")
    show["MAE_sqm"]  = show["MAE_sqm"].map(lambda x: f"{x:,.0f}")
    show["RMSE_sqm"] = show["RMSE_sqm"].map(lambda x: f"{x:,.0f}")
    show["MAE_total"]  = show["MAE_total"].map(lambda x: f"{x:,.0f}")
    show["RMSE_total"] = show["RMSE_total"].map(lambda x: f"{x:,.0f}")
    print(show.to_string(index=False))
    print(f"\nComparison saved -> {comp_path}")

    manifest = {
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "target": "log_price = log(price_per_sqm)  (Decision 34)",
        "prediction": "exp(model output) = price_per_sqm; total price = price_per_sqm * area_sqm",
        "selection_rule": "best of RF/XGBoost per stratum by lowest test MAPE; OLS comparator only",
        "global_total_price_baseline": {"model": "Random Forest", "R2_total": 0.807, "MAPE": 59.28},
        "strata": {
            s["stratum_key"]: {
                "label": s["label"],
                "n_rows": s["n_rows"],
                "n_test": s["n_test"],
                "deployed_family": s["deployed_family"],
                "deployed_metrics": s["deployed_metrics"],
                "model_file": f"{s['stratum_key']}_model.pkl",
                "n_features": len(s["deployed_features"]),
                "features": s["deployed_features"],
            }
            for s in summaries
        },
    }
    with open(os.path.join(MODELS_DIR, "deployment_manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
    print(f"Deployment manifest -> {os.path.join(MODELS_DIR, 'deployment_manifest.json')}")

    print("\n" + "=" * 78)
    print("DEPLOYED MODELS (per-sqm target) vs GLOBAL TOTAL-PRICE BASELINE (R2=0.807, MAPE=59.28%)")
    print("=" * 78)
    for s in summaries:
        m = s["deployed_metrics"]
        print(f"  {s['label']:<12} {s['deployed_family']:<14} "
              f"MAPE={m['MAPE']:6.2f}%  R2_sqm={m['R2_sqm']:7.4f}  R2_total={m['R2_total']:7.4f}  "
              f"(n_test={s['n_test']})")

    print("\nrun_models_stratified.py complete.")


if __name__ == "__main__":
    main()
