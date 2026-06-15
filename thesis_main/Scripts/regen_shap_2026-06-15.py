"""
regen_shap_2026-06-15.py
========================
Regenerate the deployed-model SHAP beeswarm plots from the EXACT saved model pkls
(EDA/plots/10_stratified_models/shap_{key}_rf_summary.png).

Why: finalize_stratified_groupcv.py skips SHAP when `shap` is unavailable in the runtime
("shap/matplotlib missing — beeswarm skipped"), so the SHAP plots went stale at 2026-06-05 —
before the multi-source expansion (Decision 47) AND the per-stratum feature selection (47i/49).
This loads each deployed pkl + rebuilds its exact feature matrix and re-renders SHAP. No retrain
(deterministic models unchanged); only the interpretation figures are refreshed.

Run with the interpreter that has shap (the repo .venv): ./.venv/bin/python Scripts/regen_shap_2026-06-15.py
"""
import os, sys, pickle
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import finalize_stratified_groupcv as F  # build_features, STRATUM_DROP, try_shap, dirs

STRATA = {
    "condo":  ("abt_condo.csv",  "Condominium"),
    "houses": ("abt_houses.csv", "Houses"),
    "lot":    ("abt_lot.csv",    "Vacant Lot"),
}

for key, (csv, label) in STRATA.items():
    df = pd.read_csv(os.path.join(F.PROCESSED_DIR, csv)).reset_index(drop=True)
    X, _ = F.build_features(df)
    drop = [c for c in F.STRATUM_DROP.get(key, []) if c in X.columns]
    if drop:
        X = X.drop(columns=drop)
    with open(os.path.join(F.MODELS_DIR, f"{key}_model.pkl"), "rb") as fh:
        model = pickle.load(fh)
    assert model.n_features_in_ == X.shape[1], \
        f"{key}: model expects {model.n_features_in_} feats, rebuilt {X.shape[1]} — feature mismatch"
    print(f"\n=== {label} ({X.shape[1]} features, deployed pkl) ===")
    F.try_shap(model, X, key, label)
print("\nDone — SHAP beeswarms refreshed in EDA/plots/10_stratified_models/")
