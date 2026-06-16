"""
regen_shap_2026-06-16.py
========================
Regenerate the deployed-model SHAP interpretation artifacts from the EXACT saved
pkls, in ONE TreeExplainer pass per stratum. Supersedes the stale 2026-06-05 era
artifacts that still showed retired/dropped features (individual MCRAI + road
features for condo/houses; mcrai_finance/transport in the block summary).

Writes:
    EDA/plots/10_stratified_models/shap_{key}_rf_summary.png   (beeswarm, top 20)
    Models/shap_block_summary_rf.txt                           (block aggregation, all 3 strata)

No retrain. Loads each deployed pkl, rebuilds its exact lean feature matrix
(build_features + STRATUM_DROP), asserts feature-count match, then explains.

Run: ./.venv/bin/python Scripts/regen_shap_2026-06-16.py
"""
import os, sys, pickle
import numpy as np
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import finalize_stratified_groupcv as F  # build_features, STRATUM_DROP, dirs

import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import shap

STRATA = {
    "condo":  ("abt_condo.csv",  "Condominium"),
    "houses": ("abt_houses.csv", "Houses"),
    "lot":    ("abt_lot.csv",    "Vacant Lot"),
}


def blocks(cols):
    cbd   = [c for c in cols if c.startswith("dist_") and c.endswith("_m") and "road" not in c]
    mcrai = [c for c in cols if c.startswith("mcrai_")]
    slag  = [c for c in cols if c == "spatial_lag_price"]
    bir   = [c for c in cols if c.startswith("bir_")]
    cityt = [c for c in cols if c.startswith("city_") or c.startswith("property_type_")]
    used  = set(cbd + mcrai + slag + bir + cityt)
    struct = [c for c in cols if c not in used]
    return {"CBD distances": cbd, "MCRAI": mcrai, "spatial_lag_price": slag,
            "BIR zonal": bir, "city/type dummies": cityt, "structural": struct}


def main():
    summary_lines = ["SHAP Block Aggregation — Random Forest (deployed stratified models)",
                     "Regenerated 2026-06-16 from deployed pkls (matches deployment_manifest.json).",
                     "=" * 72]
    for key, (csv, label) in STRATA.items():
        df = pd.read_csv(os.path.join(F.PROCESSED_DIR, csv)).reset_index(drop=True)
        X, _ = F.build_features(df)
        drop = [c for c in F.STRATUM_DROP.get(key, []) if c in X.columns]
        if drop:
            X = X.drop(columns=drop)
        with open(os.path.join(F.MODELS_DIR, f"{key}_model.pkl"), "rb") as fh:
            model = pickle.load(fh)
        assert model.n_features_in_ == X.shape[1], \
            f"{key}: model expects {model.n_features_in_} feats, rebuilt {X.shape[1]}"

        print(f"=== {label}: explaining {X.shape[1]} feats x {len(X)} rows ===", flush=True)
        sv = shap.TreeExplainer(model).shap_values(X, check_additivity=False)
        msh = np.abs(sv).mean(0)
        s = pd.Series(msh, index=X.columns).sort_values(ascending=False)

        # beeswarm
        shap.summary_plot(sv, X, max_display=20, show=False, plot_type="dot")
        plt.title(f"SHAP — {label} (RF, top 20)", pad=12); plt.tight_layout()
        out = os.path.join(F.SHAP_DIR, f"shap_{key}_rf_summary.png")
        plt.savefig(out, dpi=150, bbox_inches="tight"); plt.close("all")
        print(f"  beeswarm -> {out}", flush=True)

        # block summary text
        tot = s.sum()
        summary_lines += ["", f"[{label}]  n={len(X)}  features={X.shape[1]}",
                          "-" * 60, "  Block                     Sum|SHAP|    % of total"]
        for name, cols in blocks(X.columns).items():
            ssum = s[cols].sum() if cols else 0.0
            summary_lines.append(f"  {name:<24} {ssum:10.4f}   {ssum/tot*100:6.1f}%")
        summary_lines.append("  Top 8 features (mean|SHAP|):")
        for f, v in s.head(8).items():
            summary_lines.append(f"      {v:9.4f}   {f}")

    txt = os.path.join(F.MODELS_DIR.replace(os.path.join("Models", "stratified"), "Models"),
                       "shap_block_summary_rf.txt")
    # F.MODELS_DIR is .../Models/stratified; block summary lives in .../Models
    txt = os.path.join(os.path.dirname(F.MODELS_DIR), "shap_block_summary_rf.txt")
    with open(txt, "w") as fh:
        fh.write("\n".join(summary_lines) + "\n")
    print(f"\nblock summary -> {txt}", flush=True)
    print("Done — SHAP artifacts refreshed against deployed pkls.", flush=True)


if __name__ == "__main__":
    main()
