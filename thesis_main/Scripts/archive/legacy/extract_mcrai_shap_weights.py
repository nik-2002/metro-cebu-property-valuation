"""
extract_mcrai_shap_weights.py — MCRAI SHAP weight extraction.
Mirrors run_models.py pre-processing, loads RF pkl, computes SHAP on test set.
Writes: thesis_main/Models/mcrai_shap_weights.txt  and  EDA/mcrai_shap_weights.png
"""
import os, pickle
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd, shap
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
THESIS_DIR = os.path.dirname(SCRIPT_DIR)
ROOT_DIR   = os.path.dirname(THESIS_DIR)
ABT_PATH   = os.path.join(THESIS_DIR, "Data", "processed", "abt_clean.csv")
RF_PKL     = os.path.join(THESIS_DIR, "Models", "rf_model.pkl")
MODELS_DIR = os.path.join(THESIS_DIR, "Models")
EDA_DIR    = os.path.join(ROOT_DIR, "EDA")

MCRAI_COLS = [
    "mcrai_education", "mcrai_finance", "mcrai_grocery", "mcrai_health",
    "mcrai_security", "mcrai_transport", "mcrai_tourism",
    "mcrai_recreation", "mcrai_retail_density",
]

# --- Pre-processing: mirror run_models.py exactly ---
print("Loading ABT ...")
df = pd.read_csv(ABT_PATH)
df = df[~df["property_id"].isin([468, 714, 769])].copy()
df = df[df["price_per_sqm"].notna()].copy()
df = df[df["spatial_lag_price"].notna()].copy()
print(f"Modeling-ready rows: {len(df):,}")

EXCLUDE_COLS = {
    "price_per_sqm", "log_price", "price_php", "valuation_gap",
    "price_outlier_flag", "price_type", "spatial_lag_price",
    "property_id", "property_name", "address", "geocode_source",
    "barangay_geocoded", "source", "mcrai_composite",
}

CAT_COLS = ["city", "property_type", "market_segment"]
df_encoded = pd.get_dummies(df, columns=CAT_COLS, drop_first=True, dtype=int)

feature_cols = [
    c for c in df_encoded.columns
    if c not in EXCLUDE_COLS and c != "log_price"
]

null_cols = [c for c in feature_cols if df_encoded[c].isnull().any()]
if null_cols:
    imp = SimpleImputer(strategy="median")
    df_encoded[null_cols] = imp.fit_transform(df_encoded[null_cols])

for col in ["lot_area_sqm", "floor_area_sqm", "area_sqm"]:
    df_encoded[f"log_{col}"] = np.log1p(df_encoded[col])

X_full = df_encoded[feature_cols].copy()
y      = df_encoded["log_price"]

# --- Reconstruct identical 80/20 test split (random_state=42) ---
market_seg_col = df["market_segment"].reset_index(drop=True)
X_full_reset   = X_full.reset_index(drop=True)
y_reset        = y.reset_index(drop=True)

_, X_test, _, _ = train_test_split(
    X_full_reset, y_reset,
    test_size=0.2, random_state=42, stratify=market_seg_col,
)
print(f"Test set size: {len(X_test):,} rows")

# --- Load trained RF model (no retraining) ---
print(f"Loading RF model from {RF_PKL} ...")
with open(RF_PKL, "rb") as fh:
    rf_model = pickle.load(fh)

# --- SHAP values on test set ---
print("Computing SHAP values (TreeExplainer) ...")
explainer = shap.TreeExplainer(rf_model)
shap_vals = explainer.shap_values(X_test)
shap_df   = pd.DataFrame(shap_vals, columns=X_test.columns)

missing = [c for c in MCRAI_COLS if c not in shap_df.columns]
if missing:
    raise ValueError(f"MCRAI columns missing from SHAP output: {missing}")

mean_abs = shap_df[MCRAI_COLS].abs().mean()
total    = mean_abs.sum()
weights  = mean_abs / total
ranked   = weights.sort_values(ascending=False)

# --- Print table ---
W = 60
print()
print("MCRAI SHAP-Derived Weights (test set, RF)")
print("=" * W)
print(f"  {'Category':<26}  {'Mean |SHAP|':>12}  {'Norm. Weight':>12}")
print("-" * W)
for cat in ranked.index:
    print(f"  {cat:<26}  {mean_abs[cat]:>12.6f}  {weights[cat]:>12.6f}")
print("-" * W)
print(f"  {'Sum':<26}  {total:>12.6f}  {weights.sum():>12.6f}")

# --- Save text file ---
out_txt = os.path.join(MODELS_DIR, "mcrai_shap_weights.txt")
with open(out_txt, "w") as fh:
    print("MCRAI SHAP-Derived Weights (test set, RF)", file=fh)
    print("=" * W, file=fh)
    print(f"  {'Category':<26}  {'Mean |SHAP|':>12}  {'Norm. Weight':>12}", file=fh)
    print("-" * W, file=fh)
    for cat in ranked.index:
        print(f"  {cat:<26}  {mean_abs[cat]:>12.6f}  {weights[cat]:>12.6f}", file=fh)
    print("-" * W, file=fh)
    print(f"  {'Sum':<26}  {total:>12.6f}  {weights.sum():>12.6f}", file=fh)
print(f"Weights saved -> {out_txt}")

# --- Horizontal bar chart: lowest weight at bottom, highest at top ---
plot_order = ranked.index[::-1]
plot_vals  = weights[plot_order]
labels     = [c.replace("mcrai_", "") for c in plot_order]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(labels, plot_vals.values, color="#2a6ebb", edgecolor="white")

for bar, val in zip(bars, plot_vals.values):
    ax.text(
        val + 0.004, bar.get_y() + bar.get_height() / 2,
        f"{val:.3f}", va="center", ha="left", fontsize=9,
    )

ax.set_xlabel("Normalized Weight (sum = 1.0)", fontsize=10)
ax.set_title("MCRAI SHAP-Derived Weights — Random Forest (Test Set)", fontsize=11)
ax.set_xlim(0, plot_vals.max() + 0.08)
ax.tick_params(axis="y", labelsize=10)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()

out_png = os.path.join(EDA_DIR, "mcrai_shap_weights.png")
plt.savefig(out_png, dpi=150, bbox_inches="tight")
plt.close()
print(f"Bar chart saved -> {out_png}")
