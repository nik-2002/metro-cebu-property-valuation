"""
run_models.py
=============
Pre-modeling data prep, OLS baseline, Random Forest, and XGBoost for the
Metro Cebu residential valuation thesis.

Reads:  thesis_main/Data/processed/abt_clean.csv
Writes: thesis_main/Models/  (OLS summary, RF pkl, XGB pkl, MCRAI weights)
        EDA/                  (SHAP beeswarm plots)
"""

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
THESIS_DIR = os.path.dirname(SCRIPT_DIR)           # thesis_main/
ROOT_DIR   = os.path.dirname(THESIS_DIR)           # workspace root (16 Thesis/)

ABT_PATH   = os.path.join(THESIS_DIR, "Data", "processed", "abt_clean.csv")
MODELS_DIR = os.path.join(THESIS_DIR, "Models")
EDA_DIR    = os.path.join(ROOT_DIR,   "EDA")

os.makedirs(MODELS_DIR, exist_ok=True)


# ===========================================================================
# STEP 1  Pre-modeling data prep
# ===========================================================================
print("=" * 70)
print("STEP 1 — Pre-modeling data prep")
print("=" * 70)

df = pd.read_csv(ABT_PATH)
df = df[df["market_segment"] == "open_market"].copy()
print(f"Filtered to open_market: {len(df)} rows")
print(f"Loaded ABT: {len(df):,} rows")

# Drop three implausible price rows (Decision 10)
IMPLAUSIBLE_IDS = [468, 714, 769]
df = df[~df["property_id"].isin(IMPLAUSIBLE_IDS)].copy()
print(f"After dropping implausible property_ids {IMPLAUSIBLE_IDS}: {len(df):,} rows")

# Drop rows where price_per_sqm is null
df = df[df["price_per_sqm"].notna()].copy()
print(f"After dropping null price_per_sqm: {len(df):,} rows")

# Drop rows where spatial_lag_price is null
df = df[df["spatial_lag_price"].notna()].copy()
print(f"After dropping null spatial_lag_price: {len(df):,} rows")
print(f"\nFinal modeling-ready dataset: {len(df):,} rows")


# ===========================================================================
# STEP 2  Feature matrix definition
# ===========================================================================
print("\n" + "=" * 70)
print("STEP 2 — Feature matrix definition")
print("=" * 70)

# Columns excluded from all feature matrices (leakage or metadata)
EXCLUDE_COLS = {
    "price_per_sqm", "log_price", "price_php", "valuation_gap",
    "price_outlier_flag", "price_type", "spatial_lag_price",
    "property_id", "property_name", "address", "geocode_source",
    "barangay_geocoded", "source", "floor_area_imputed",
    # mcrai_composite is a weighted sum of the 9 individual mcrai_* scores.
    # Including it alongside its components creates a rank-deficient design matrix
    # (confirmed: eigenvalue ~1e-19). Exclude from all feature matrices.
    "mcrai_composite",
    # market_segment is constant (open_market) after Decision 17 filter — not a model feature.
    "market_segment",
}

# Categorical columns to one-hot encode
CAT_COLS = ["city", "property_type"]

# One-hot encode categorical columns
df_encoded = pd.get_dummies(df, columns=CAT_COLS, drop_first=True, dtype=int)

# Identify remaining feature columns (exclude target + leakage)
feature_cols = [
    c for c in df_encoded.columns
    if c not in EXCLUDE_COLS and c != "log_price"
]

# Impute any remaining nulls with column median.
# All-null columns (no observed values) cannot be median-imputed — fill with 0 separately.
all_null_cols  = [c for c in feature_cols if df_encoded[c].isna().all()]
imputable_cols = [c for c in feature_cols
                  if df_encoded[c].isnull().any() and not df_encoded[c].isna().all()]

if all_null_cols:
    print(f"All-null columns (filling with 0): {all_null_cols}")
    df_encoded[all_null_cols] = df_encoded[all_null_cols].fillna(0)

if imputable_cols:
    print(f"Columns with remaining nulls (imputing with median): {imputable_cols}")
    imputer = SimpleImputer(strategy="median")
    df_encoded[imputable_cols] = imputer.fit_transform(df_encoded[imputable_cols])

# Log-transform area/size variables for OLS (log-linear hedonic model).
# Raw area variables cause OLS to produce astronomical predictions on large lots
# (e.g., 150,000 sqm × coeff → exp(6) = 400x amplification in PHP/sqm).
# Log1p is used because some imputed lot_area_sqm values may be near-zero.
for col in ["lot_area_sqm", "floor_area_sqm", "area_sqm"]:
    df_encoded[f"log_{col}"] = np.log1p(df_encoded[col])

# X_full: all features (for RF and XGBoost)
X_full = df_encoded[feature_cols].copy()

# X_ols: additional collinear variables dropped for OLS stability
# - dist_talisay_tabunok_m: Decision 11 (r>0.95 with srp and naga)
# - is_mactan_island: perfectly collinear with city_Lapu-Lapu City one-hot dummy
# - bir_zonal_rr_log: log-transform of bir_zonal_rr_median (near-perfect collinearity)
# - is_vacant_lot: perfectly collinear with property_type_Vacant Lot one-hot dummy
# - latitude, longitude: raw coordinates cause extreme coefficient instability in OLS
#   (coeff ~27 on longitude means a 0.1-degree test shift → 15x price amplification).
#   City dummies already capture geographic location for OLS.
# - lot_area_sqm, floor_area_sqm, area_sqm: replaced with log versions below
#   (standard log-linear hedonic spec; raw areas cause 400x back-transform amplification
#   on the 150k-sqm outlier row still in the modeling dataset)
OLS_EXTRA_DROPS = ["dist_talisay_tabunok_m", "is_mactan_island", "bir_zonal_rr_log",
                   "is_vacant_lot", "latitude", "longitude",
                   "lot_area_sqm", "floor_area_sqm", "area_sqm",
                   # log_lot_area_sqm is constant (=0) when restricted to open_market
                   # because Lamudi listings do not collect lot_area_sqm.
                   "log_lot_area_sqm"]
X_ols_base = X_full.drop(columns=OLS_EXTRA_DROPS, errors="ignore").copy()
# Attach log area columns (computed from df_encoded above).
# log_lot_area_sqm excluded: constant=0 for open_market (already in OLS_EXTRA_DROPS).
# log_area_sqm excluded: perfectly collinear with log_floor_area_sqm for open_market
#   rows where lot_area_sqm is null (area_sqm = floor_area_sqm by Decision 1 fallback).
log_area_cols = ["log_floor_area_sqm"]
log_area_df = df_encoded[log_area_cols].reset_index(drop=True)
X_ols = pd.concat([X_ols_base.reset_index(drop=True), log_area_df], axis=1)

y = df_encoded["log_price"]

print(f"\nX_full shape: {X_full.shape}")
print("X_full columns:")
for c in X_full.columns:
    print(f"  {c}")

print(f"\nX_ols shape: {X_ols.shape}")
print(f"(dropped from X_full for OLS: {OLS_EXTRA_DROPS})")
print("(added to X_ols: log_floor_area_sqm)")


# ===========================================================================
# STEP 3  Train / test split
# ===========================================================================
print("\n" + "=" * 70)
print("STEP 3 — Train / test split (80/20, random_state=42)")
print("=" * 70)
# market_segment is constant (open_market) after Decision 17 filter.
# stratify=market_seg_col is retained unchanged to preserve the exact
# train/test split that produced all recorded model artifacts.
# Removing it would change sklearn's internal RNG path and alter the split.

market_seg_col = df["market_segment"].reset_index(drop=True)

X_full_reset = X_full.reset_index(drop=True)
X_ols_reset  = X_ols.reset_index(drop=True)
y_reset      = y.reset_index(drop=True)

(X_full_train, X_full_test,
 X_ols_train,  X_ols_test,
 y_train,      y_test,
 seg_train,    seg_test) = train_test_split(
    X_full_reset, X_ols_reset, y_reset, market_seg_col,
    test_size=0.2, random_state=42, stratify=market_seg_col
)

print(f"Train size: {len(X_full_train):,} rows")
print(f"Test  size: {len(X_full_test):,} rows")

# area_sqm for per-sqm evaluation (shared across all models — same test rows)
area_sqm_test = X_full_test["area_sqm"].reset_index(drop=True)


# ===========================================================================
# Helper — evaluation metrics (back-transformed from log total price to PHP)
# ===========================================================================
def evaluate(y_true_log, y_pred_log, model_name: str) -> dict:
    """Compute test metrics after back-transforming log total-price predictions."""
    y_true = np.exp(y_true_log)
    y_pred = np.exp(y_pred_log)
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2   = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    print(f"\n{model_name} — Test-set metrics (total PHP price, back-transformed):")
    print(f"  MAPE : {mape:.2f}%")
    print(f"  MAE  : {mae:,.2f}")
    print(f"  RMSE : {rmse:,.2f}")
    print(f"  R2   : {r2:.4f}")
    return {"Model": model_name, "MAE": mae, "MAPE": mape, "RMSE": rmse, "R2": r2}


def evaluate_per_sqm(y_true_log, y_pred_log, area_sqm: pd.Series, model_name: str) -> dict:
    """Compute MAE and RMSE in PHP/sqm after dividing back-transformed predictions by area.

    MAPE is identical to total-price MAPE (area cancels), so only MAE and RMSE are reported here.
    These are the metrics interpretable for valuation practice.
    """
    y_true_php = np.exp(np.asarray(y_true_log))
    y_pred_php = np.exp(np.asarray(y_pred_log))
    area = area_sqm.reset_index(drop=True).to_numpy(dtype=float).copy()
    # Guard against zero area (should not occur on open_market, but be safe)
    area[area == 0] = np.nan
    ppsqm_true = y_true_php / area
    ppsqm_pred = y_pred_php / area
    mask = np.isfinite(ppsqm_true) & np.isfinite(ppsqm_pred)
    mae_sqm  = mean_absolute_error(ppsqm_true[mask], ppsqm_pred[mask])
    rmse_sqm = np.sqrt(mean_squared_error(ppsqm_true[mask], ppsqm_pred[mask]))
    mape_sqm = np.mean(np.abs((ppsqm_true[mask] - ppsqm_pred[mask]) / ppsqm_true[mask])) * 100
    print(f"\n{model_name} — Per-sqm metrics (PHP/sqm):")
    print(f"  MAPE  : {mape_sqm:.2f}%  (same as total-price MAPE by construction)")
    print(f"  MAE   : PHP {mae_sqm:,.0f}/sqm")
    print(f"  RMSE  : PHP {rmse_sqm:,.0f}/sqm")
    return {"Model": model_name, "MAPE_sqm": mape_sqm, "MAE_sqm": mae_sqm, "RMSE_sqm": rmse_sqm}


def save_actual_vs_predicted_plot(y_true_log, y_pred_log, out_name: str) -> str:
    """Save a log-scale actual-vs-predicted scatter plot in PHP millions."""
    y_true_m = np.exp(y_true_log) / 1_000_000
    y_pred_m = np.exp(y_pred_log) / 1_000_000
    positive_min = min(y_true_m[y_true_m > 0].min(), y_pred_m[y_pred_m > 0].min())
    max_val = max(y_true_m.max(), y_pred_m.max())

    fig, ax = plt.subplots(figsize=(7.2, 6.4))
    ax.scatter(y_true_m, y_pred_m, s=26, alpha=0.65, color="#4c78a8", linewidths=0)
    ax.plot([positive_min, max_val], [positive_min, max_val], linestyle="--", color="#c62828", linewidth=1.5)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title("Actual vs Predicted Total Price — XGBoost Test Set (log scale)", pad=10)
    ax.set_xlabel("Actual total price (PHP millions, log scale)")
    ax.set_ylabel("Predicted total price (PHP millions, log scale)")
    ax.set_xlim(left=positive_min, right=max_val * 1.05)
    ax.set_ylim(bottom=positive_min, top=max_val * 1.05)
    ax.grid(True, which="both", linestyle=":", linewidth=0.6, alpha=0.5)
    fig.tight_layout()

    out_path = os.path.join(EDA_DIR, out_name)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Actual-vs-predicted plot saved -> {out_path}")
    return out_path


# ===========================================================================
# STEP 4  OLS baseline
# ===========================================================================
print("\n" + "=" * 70)
print("STEP 4 — OLS baseline (statsmodels, X_ols)")
print("=" * 70)

X_ols_train_sm = sm.add_constant(X_ols_train)
X_ols_test_sm  = sm.add_constant(X_ols_test)

# Align test columns to training columns (add any missing dummy columns)
for col in X_ols_train_sm.columns:
    if col not in X_ols_test_sm.columns:
        X_ols_test_sm[col] = 0
X_ols_test_sm = X_ols_test_sm[X_ols_train_sm.columns]

ols_model       = sm.OLS(y_train, X_ols_train_sm).fit()
ols_summary_txt = ols_model.summary().as_text()
print(ols_summary_txt)

# Save summary
ols_summary_path = os.path.join(MODELS_DIR, "ols_summary.txt")
with open(ols_summary_path, "w") as f:
    f.write(ols_summary_txt)
print(f"\nOLS summary saved -> {ols_summary_path}")

# Evaluate on test set
ols_preds = ols_model.predict(X_ols_test_sm)
metrics_ols = evaluate(y_test, ols_preds, "OLS")


# ===========================================================================
# STEP 5  Random Forest
# ===========================================================================
print("\n" + "=" * 70)
print("STEP 5 — Random Forest (n_estimators=300, X_full)")
print("=" * 70)

rf_model = RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1)
rf_model.fit(X_full_train, y_train)
rf_preds = rf_model.predict(X_full_test)
metrics_rf = evaluate(y_test, rf_preds, "Random Forest")

rf_pkl_path = os.path.join(MODELS_DIR, "rf_model.pkl")
with open(rf_pkl_path, "wb") as f:
    pickle.dump(rf_model, f)
print(f"RF model saved -> {rf_pkl_path}")


# ===========================================================================
# STEP 6  XGBoost
# ===========================================================================
print("\n" + "=" * 70)
print("STEP 6 — XGBoost (n_estimators=300, X_full)")
print("=" * 70)

xgb_model = xgb.XGBRegressor(
    n_estimators=300, learning_rate=0.05, max_depth=6,
    random_state=42, verbosity=0
)
xgb_model.fit(X_full_train, y_train)
xgb_preds = xgb_model.predict(X_full_test)
metrics_xgb = evaluate(y_test, xgb_preds, "XGBoost")
save_actual_vs_predicted_plot(y_test, xgb_preds, "xgb_actual_vs_predicted.png")

xgb_pkl_path = os.path.join(MODELS_DIR, "xgb_model.pkl")
with open(xgb_pkl_path, "wb") as f:
    pickle.dump(xgb_model, f)
print(f"XGB model saved -> {xgb_pkl_path}")


# ===========================================================================
# STEP 7  Model comparison table
# ===========================================================================
print("\n" + "=" * 70)
print("STEP 7 — Model comparison table")
print("=" * 70)

comparison_raw = pd.DataFrame([metrics_ols, metrics_rf, metrics_xgb])
comparison_fmt = comparison_raw.copy()
comparison_fmt["MAPE"] = comparison_raw["MAPE"].map(lambda x: f"{x:.2f}%")
comparison_fmt["MAE"]  = comparison_raw["MAE"].map(lambda x: f"{x:,.2f}")
comparison_fmt["RMSE"] = comparison_raw["RMSE"].map(lambda x: f"{x:,.2f}")
comparison_fmt["R2"]   = comparison_raw["R2"].map(lambda x: f"{x:.4f}")
comparison_fmt = comparison_fmt.set_index("Model")
print(comparison_fmt.to_string())

comparison_path = os.path.join(MODELS_DIR, "model_comparison_baseline.csv")
comparison_raw.to_csv(comparison_path, index=False)
print(f"\nBaseline model comparison saved -> {comparison_path}")


# ===========================================================================
# STEP 7b  Per-sqm evaluation (MAE and RMSE in PHP/sqm)
# ===========================================================================
print("\n" + "=" * 70)
print("STEP 7b — Per-sqm evaluation (PHP/sqm — the metric shown in the app)")
print("=" * 70)

metrics_ols_sqm  = evaluate_per_sqm(y_test, ols_preds,  area_sqm_test, "OLS")
metrics_rf_sqm   = evaluate_per_sqm(y_test, rf_preds,   area_sqm_test, "Random Forest")
metrics_xgb_sqm  = evaluate_per_sqm(y_test, xgb_preds,  area_sqm_test, "XGBoost")

comparison_sqm = pd.DataFrame([metrics_ols_sqm, metrics_rf_sqm, metrics_xgb_sqm])
comparison_sqm_fmt = comparison_sqm.copy()
comparison_sqm_fmt["MAPE_sqm"]  = comparison_sqm["MAPE_sqm"].map(lambda x: f"{x:.2f}%")
comparison_sqm_fmt["MAE_sqm"]   = comparison_sqm["MAE_sqm"].map(lambda x: f"PHP {x:,.0f}/sqm")
comparison_sqm_fmt["RMSE_sqm"]  = comparison_sqm["RMSE_sqm"].map(lambda x: f"PHP {x:,.0f}/sqm")
comparison_sqm_fmt = comparison_sqm_fmt.set_index("Model")
print("\nPer-sqm comparison table:")
print(comparison_sqm_fmt.to_string())

sqm_path = os.path.join(MODELS_DIR, "model_comparison_per_sqm.csv")
comparison_sqm.to_csv(sqm_path, index=False)
print(f"\nPer-sqm comparison saved -> {sqm_path}")


# ===========================================================================
# STEP 8  SHAP for RF and XGBoost
# ===========================================================================
print("\n" + "=" * 70)
print("STEP 8 — SHAP analysis")
print("=" * 70)

def run_shap(model, X_test, model_tag: str):
    print(f"\nComputing SHAP values for {model_tag}...")
    explainer   = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    # RF returns list for multi-output; grab single output
    if isinstance(shap_values, list):
        shap_values = shap_values[0]

    # Top 10 features by mean |SHAP|
    mean_abs_shap = pd.Series(
        np.abs(shap_values).mean(axis=0), index=X_test.columns
    ).sort_values(ascending=False)
    print(f"Top 10 features by mean |SHAP| — {model_tag}:")
    print(mean_abs_shap.head(10).to_string())

    # Beeswarm summary plot (top 20 features)
    shap.summary_plot(
        shap_values, X_test,
        max_display=20, show=False, plot_type="dot"
    )
    plt.title(f"SHAP Beeswarm — {model_tag} (top 20 features)", pad=12)
    plt.tight_layout()
    out_path = os.path.join(EDA_DIR, f"shap_{model_tag.lower()}_summary.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close("all")
    print(f"SHAP plot saved -> {out_path}")
    return mean_abs_shap


rf_shap  = run_shap(rf_model,  X_full_test, "rf")
xgb_shap = run_shap(xgb_model, X_full_test, "xgb")


# ===========================================================================
# STEP 8b  SHAP block aggregation — MCRAI vs CBD distances (RF deployed model)
# ===========================================================================
print("\n" + "=" * 70)
print("STEP 8b — SHAP block aggregation (RF): MCRAI vs CBD distances")
print("=" * 70)

MCRAI_COLS = [
    "mcrai_education", "mcrai_finance", "mcrai_grocery", "mcrai_health",
    "mcrai_security", "mcrai_transport", "mcrai_tourism",
    "mcrai_recreation", "mcrai_retail_density",
]
CBD_COLS = [
    "dist_cebu_business_park_m", "dist_mandaue_cbd_m", "dist_mactan_cbd_m",
    "dist_srp_m", "dist_talisay_tabunok_m", "dist_naga_city_m",
    "dist_consolacion_m", "dist_airport_m",
]

total_shap = rf_shap.sum()

mcrai_present = [c for c in MCRAI_COLS if c in rf_shap.index]
cbd_present   = [c for c in CBD_COLS   if c in rf_shap.index]
other_cols    = [c for c in rf_shap.index if c not in mcrai_present and c not in cbd_present]

mcrai_total = rf_shap[mcrai_present].sum()
cbd_total   = rf_shap[cbd_present].sum()
other_total = rf_shap[other_cols].sum()

block_lines = []
block_lines.append("SHAP Block Aggregation — Random Forest (deployed model)")
block_lines.append("=" * 60)
block_lines.append(f"{'Feature block':<30} {'Sum |SHAP|':>12} {'% of total':>12}")
block_lines.append("-" * 60)
block_lines.append(f"{'MCRAI (9 categories)':<30} {mcrai_total:>12.4f} {100*mcrai_total/total_shap:>11.1f}%")
block_lines.append(f"{'CBD distances (8 nodes)':<30} {cbd_total:>12.4f} {100*cbd_total/total_shap:>11.1f}%")
block_lines.append(f"{'Structural & other':<30} {other_total:>12.4f} {100*other_total/total_shap:>11.1f}%")
block_lines.append(f"{'TOTAL':<30} {total_shap:>12.4f} {'100.0%':>12}")
block_lines.append("")
block_lines.append("Individual MCRAI rankings within full feature list:")
block_lines.append("-" * 60)
block_lines.append(f"  {'Feature':<30} {'Mean |SHAP|':>12} {'Overall rank':>14}")
all_ranked = rf_shap.reset_index()
all_ranked.columns = ["feature", "shap"]
all_ranked["rank"] = range(1, len(all_ranked) + 1)
for feat in mcrai_present:
    row = all_ranked[all_ranked["feature"] == feat].iloc[0]
    block_lines.append(f"  {feat:<30} {row['shap']:>12.6f} {int(row['rank']):>14}")
block_lines.append("")
block_lines.append("Individual CBD distance rankings within full feature list:")
block_lines.append("-" * 60)
block_lines.append(f"  {'Feature':<30} {'Mean |SHAP|':>12} {'Overall rank':>14}")
for feat in cbd_present:
    row = all_ranked[all_ranked["feature"] == feat].iloc[0]
    block_lines.append(f"  {feat:<30} {row['shap']:>12.6f} {int(row['rank']):>14}")

block_str = "\n".join(block_lines)
print(block_str)

shap_block_path = os.path.join(MODELS_DIR, "shap_block_summary_rf.txt")
with open(shap_block_path, "w") as f:
    f.write(block_str)
print(f"\nSHAP block summary saved -> {shap_block_path}")


# ===========================================================================
# STEP 9  Stage 1 OLS coefficients -> MCRAI Stage 2 weights
# ===========================================================================
print("\n" + "=" * 70)
print("STEP 9 — MCRAI Stage 2 weight derivation from OLS coefficients")
print("=" * 70)

MCRAI_CATS = [
    "mcrai_education", "mcrai_finance", "mcrai_grocery", "mcrai_health",
    "mcrai_security", "mcrai_transport", "mcrai_tourism",
    "mcrai_recreation", "mcrai_retail_density",
]

ALPHA = 0.05

rows = []
for cat in MCRAI_CATS:
    if cat in ols_model.params.index:
        coef  = ols_model.params[cat]
        pval  = ols_model.pvalues[cat]
        sig   = bool(pval < ALPHA)
        rows.append({"category": cat, "coef": coef, "pval": pval, "significant": sig})
    else:
        rows.append({"category": cat, "coef": None, "pval": None, "significant": False})

mcrai_df = pd.DataFrame(rows)

# Normalized weights from significant categories
sig_df = mcrai_df[mcrai_df["significant"] & mcrai_df["coef"].notna()].copy()
if len(sig_df) > 0:
    sig_df["abs_coef"] = sig_df["coef"].abs()
    total = sig_df["abs_coef"].sum()
    sig_df["weight_normalized"] = sig_df["abs_coef"] / total

# Build report
final_composite_weights = {
    "mcrai_education": 0.401,
    "mcrai_grocery": 0.310,
    "mcrai_recreation": 0.199,
    "mcrai_transport": 0.102,
}

lines = []
lines.append("MCRAI Stage 2 Weights — Decision 20 Final Composite Specification")
lines.append("=" * 60)
lines.append("  Final composite uses positive-coefficient OLS categories only.")
lines.append("  Excluded from composite: mcrai_security, mcrai_tourism, mcrai_retail_density")
lines.append("  See modeling_decisions.md Decision 20 and lit_decision20_spatial_sorting.md.")
lines.append("  Weights below are the rounded implementation values used in compute_hansen_scores.py.")
lines.append("")
lines.append(f"{'Category':<25} {'Final Weight':>12}")
lines.append("-" * 60)
for category, weight in final_composite_weights.items():
    lines.append(f"{category:<25} {weight:>12.6f}")
lines.append("")
lines.append("Diagnostic only — OLS Stage 1 coefficients on open_market sample:")
lines.append("-" * 60)
lines.append(f"  Significance threshold: p < {ALPHA}")
lines.append("")
lines.append(f"{'Category':<25} {'Coef':>12} {'p-value':>10} {'Sig?':>6}")
lines.append("-" * 60)
for _, row in mcrai_df.iterrows():
    if row["coef"] is not None:
        sig_str = "YES" if row["significant"] else "no"
        lines.append(
            f"{row['category']:<25} {row['coef']:>12.6f} {row['pval']:>10.4f} {sig_str:>6}"
        )
    else:
        lines.append(f"{row['category']:<25} {'N/A':>12} {'N/A':>10} {'N/A':>6}")

lines.append("")
lines.append("Diagnostic only — |coef| normalized across significant categories:")
lines.append("-" * 60)
if len(sig_df) > 0:
    for _, row in sig_df.iterrows():
        lines.append(f"  {row['category']:<25}: {row['weight_normalized']:.6f}")
    lines.append(f"  {'Sum':<25}: {sig_df['weight_normalized'].sum():.6f}")
else:
    lines.append("  No MCRAI categories reached p < 0.05 in OLS Stage 1.")

lines.append("")
lines.append(
    "NOTE: The normalized |coef| values above are retained as diagnostics only. "
    "They do not define mcrai_composite after Decision 20."
)

report_str = "\n".join(lines)
print(report_str)

mcrai_path = os.path.join(MODELS_DIR, "mcrai_stage2_weights.txt")
with open(mcrai_path, "w") as f:
    f.write(report_str)
print(f"\nMCRAI Stage 2 weights saved -> {mcrai_path}")

print("\n" + "=" * 70)
print("run_models.py complete.")
print("=" * 70)
