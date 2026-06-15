"""
build_overview_html.py
======================
Build the self-contained illustrated study overview: regenerate the 3 RF SHAP plots fresh
(the on-disk copies keep getting reverted by Google Drive sync), then base64-embed every figure
into the HTML so the output is fully self-contained and immune to the source PNGs changing.

Run with the interpreter that has shap (the repo .venv):
  ./.venv/bin/python thesis_main/Scripts/build_overview_html.py
"""
import os, re, sys, base64, pickle, tempfile
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
THESIS = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
import finalize_stratified_groupcv as F  # build_features, STRATUM_DROP, dirs

SRC = os.path.join(THESIS, "study_overview_2026-06-15.src.html")
OUT = os.path.join(THESIS, "study_overview_2026-06-15.html")
PLOTS = os.path.join(THESIS, "EDA", "plots")
TMP = tempfile.gettempdir()

# ---- 1. regenerate the 3 deployed-model SHAP beeswarms to /tmp (current, Drive-proof) ----
def regen_shap():
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import shap
    out = {}
    for key, csv, label in (("condo", "abt_condo.csv", "Condominium"),
                            ("houses", "abt_houses.csv", "Houses"),
                            ("lot", "abt_lot.csv", "Vacant Lot")):
        df = pd.read_csv(os.path.join(F.PROCESSED_DIR, csv)).reset_index(drop=True)
        X, _ = F.build_features(df)
        drop = [c for c in F.STRATUM_DROP.get(key, []) if c in X.columns]
        if drop:
            X = X.drop(columns=drop)
        with open(os.path.join(F.MODELS_DIR, f"{key}_model.pkl"), "rb") as fh:
            model = pickle.load(fh)
        assert model.n_features_in_ == X.shape[1], f"{key}: feature mismatch"
        sv = shap.TreeExplainer(model).shap_values(X)
        shap.summary_plot(sv, X, max_display=12, show=False, plot_size=(7.2, 5.2))
        plt.title(f"SHAP — {label}", fontsize=11)
        plt.tight_layout()
        p = os.path.join(TMP, f"ov_shap_{key}.png")
        plt.savefig(p, dpi=130, bbox_inches="tight"); plt.close("all")
        out[key] = p
        print(f"  SHAP {label} -> {p}")
    return out

print("Regenerating SHAP plots (fresh, from deployed models)...")
shap_paths = regen_shap()

# ---- 2. figure key -> file path ----
FIG = {
    "geocoding":   f"{PLOTS}/09_data_integrity/Master_geocoding_clusters.png",
    "duplicates":  f"{PLOTS}/09_data_integrity/duplicate_listings_by_strictness.png",
    "target_box":  f"{PLOTS}/01_target/all_strata_price_boxplot.png",
    "price_lgu":   f"{PLOTS}/02_geographic/price_by_lgu_faceted.png",
    "condo_pdist": f"{PLOTS}/01_target/Condo_price_distribution.png",
    "house_pdist": f"{PLOTS}/01_target/Houses_price_distribution.png",
    "lot_pdist":   f"{PLOTS}/01_target/Lot_price_distribution.png",
    "condo_corr":  f"{PLOTS}/04_correlation/Condo_spearman_vs_price.png",
    "house_corr":  f"{PLOTS}/04_correlation/Houses_spearman_vs_price.png",
    "lot_corr":    f"{PLOTS}/04_correlation/Lot_spearman_vs_price.png",
    "condo_cooks": f"{PLOTS}/07_outliers/Condo_cooks_distance.png",
    "lot_mcrai_lgu": f"{PLOTS}/09_data_integrity/Lot_mcrai_by_lgu_heatmap.png",
    "mcrai_price": f"{PLOTS}/08_mcrai/composite_vs_price_all_strata.png",
    "condo_mcrai": f"{PLOTS}/08_mcrai/Condo_mcrai_distributions.png",
    "lot_mcrai":   f"{PLOTS}/08_mcrai/Lot_mcrai_distributions.png",
    "condo_vif":   f"{PLOTS}/05_multicollinearity/Condo_vif.png",
    "lot_vif":     f"{PLOTS}/05_multicollinearity/Lot_vif.png",
    "rf_nest":     f"{PLOTS}/11_hyperparameter_tuning/rf_n_estimators.png",
    "rf_maxfeat":  f"{PLOTS}/11_hyperparameter_tuning/rf_max_features.png",
    "lot_resid":   f"{PLOTS}/06_ols_residuals/Lot_residuals_vs_fitted.png",
    "house_qq":    f"{PLOTS}/06_ols_residuals/Houses_qq_plot.png",
    "shap_condo":  shap_paths["condo"],
    "shap_houses": shap_paths["houses"],
    "shap_lot":    shap_paths["lot"],
}

def datauri(path):
    with open(path, "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode("ascii")

# ---- 3. read template, embed, write ----
with open(SRC, encoding="utf-8") as fh:
    html = fh.read()

missing, embedded, total_bytes = [], 0, 0
for key, path in FIG.items():
    token = f'src="FIG:{key}"'
    if token not in html:
        print(f"  ! key not referenced in HTML: {key}")
        continue
    if not os.path.exists(path):
        missing.append((key, path)); continue
    uri = datauri(path)
    total_bytes += os.path.getsize(path)
    html = html.replace(token, f'src="{uri}"')
    embedded += 1

leftover = re.findall(r'src="FIG:([^"]+)"', html)
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(html)

print(f"\nEmbedded {embedded} figures (~{total_bytes/1024/1024:.1f} MB source) -> {OUT}")
print(f"Output size: {os.path.getsize(OUT)/1024/1024:.1f} MB")
if missing:
    print("MISSING files:"); [print("  ", k, p) for k, p in missing]
if leftover:
    print("UNRESOLVED placeholders:", leftover)
