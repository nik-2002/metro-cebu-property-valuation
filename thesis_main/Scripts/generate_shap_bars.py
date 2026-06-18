"""
generate_shap_bars.py
=====================
Mean |SHAP| horizontal bar charts per stratum (simpler than the beeswarm for the
results chapter). Loads the EXACT deployed pkls and rebuilds each feature matrix
via finalize_stratified_groupcv, identical to regen_shap_2026-06-15.py.
Writes EDA/plots/10_stratified_models/shap_{key}_rf_bar.png.
Run: ./.venv/bin/python Scripts/generate_shap_bars.py
"""
import os, sys, pickle, re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import finalize_stratified_groupcv as F

THESIS = os.path.dirname(SCRIPT_DIR)
OUT = os.path.join(THESIS, "EDA", "plots", "10_stratified_models")
os.makedirs(OUT, exist_ok=True)
TOPN = 12

STRATA = {"condo": ("abt_condo.csv", "Condominium"),
          "houses": ("abt_houses.csv", "Houses"),
          "lot": ("abt_lot.csv", "Vacant Lot")}

NODE = {"cebu_business_park": "Cebu Business Park", "mandaue_cbd": "Mandaue CBD",
        "mactan_cbd": "Mactan CBD", "srp": "SRP", "talisay_tabunok": "Talisay Tabunok",
        "consolacion": "Consolacion", "naga_city": "Naga City", "airport": "Airport"}


def pretty(col):
    m = re.match(r"dist_(.+)_m$", col)
    if m:
        return f"Dist. to {NODE.get(m.group(1), m.group(1).replace('_', ' ').title())}"
    if col == "mcrai_composite":
        return "MCRAI composite"
    if col.startswith("mcrai_"):
        return "MCRAI: " + col[len("mcrai_"):].replace("_", " ").title()
    if col == "spatial_lag_price":
        return "Neighborhood price (spatial lag)"
    if col in ("area_sqm", "floor_area_sqm"):
        return "Floor / lot area"
    if col.startswith("bir_zonal"):
        return "BIR zonal value"
    if col.startswith("city_"):
        return "City: " + col[len("city_"):].replace("_", " ")
    if col == "is_mactan_island":
        return "Mactan island"
    return col.replace("_", " ").capitalize()


for key, (csv, label) in STRATA.items():
    df = pd.read_csv(os.path.join(F.PROCESSED_DIR, csv)).reset_index(drop=True)
    X, _ = F.build_features(df)
    drop = [c for c in F.STRATUM_DROP.get(key, []) if c in X.columns]
    if drop:
        X = X.drop(columns=drop)
    with open(os.path.join(F.MODELS_DIR, f"{key}_model.pkl"), "rb") as fh:
        model = pickle.load(fh)
    expl = shap.TreeExplainer(model)
    sv = expl.shap_values(X)
    mean_abs = np.abs(sv).mean(axis=0)
    s = pd.Series(mean_abs, index=X.columns).sort_values(ascending=False).head(TOPN)
    s = s.iloc[::-1]  # ascending for barh (largest on top)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.barh([pretty(c) for c in s.index], s.values, color="#4878a8", edgecolor="white")
    ax.set_xlabel("Mean |SHAP| (impact on log price per sqm)", fontsize=9)
    ax.tick_params(axis="y", labelsize=9)
    ax.tick_params(axis="x", labelsize=8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, f"shap_{key}_rf_bar.png"), dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote shap_{key}_rf_bar.png  (top {TOPN} of {X.shape[1]} features)")
print("done ->", OUT)
