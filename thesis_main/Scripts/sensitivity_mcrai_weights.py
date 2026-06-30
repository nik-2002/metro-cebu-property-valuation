"""
sensitivity_mcrai_weights.py
============================
Sensitivity analysis on the MCRAI composite *scoring* (panel comment, 2026-06-28).

Tests how robust the deployed stratified models are to the MCRAI composite-weight
and keep-positives decisions (Decision 20 / 29). Ceteris paribus: each stratum's
deployed RF hyperparameters are held fixed (from deployment_manifest.json) and the
leak-free GroupKFold(5) evaluation is re-run; ONLY the mcrai_composite column is
rebuilt under each weighting variant. The individual mcrai_* category columns
already in the stratum CSVs are reused, so no network re-scoring is needed.

Scope: Condominium and Houses use mcrai_composite, so the weighting choice can
affect them. Vacant Lot drops the composite and uses individual MCRAI categories
(Decision 49), so it is invariant to composite weights by design and is reported
as such. (Beta/radii sensitivity, which would move Lot, is a separate re-scoring
experiment.)

Non-destructive: reads Data/processed/abt_{condo,houses}.csv, writes
Models/sensitivity_mcrai_weights.csv. Does NOT touch abt_clean.csv or the
deployed models.
"""

import json
import os

import numpy as np
import pandas as pd

# Reuse the EXACT evaluation machinery from the deployment finalizer.
from finalize_stratified_groupcv import (
    PROCESSED_DIR, MODELS_DIR, STRATA, STRATUM_DROP,
    build_features, group_oof, iaao_panel,
)
from sklearn.ensemble import RandomForestRegressor

RANDOM_STATE = 42
POSITIVE_CATS = ["education", "grocery", "recreation"]
ALL_CATS = ["education", "grocery", "health", "hospitals",
            "recreation", "security", "tourism", "retail_density"]
BASELINE = {"education": 0.447, "grocery": 0.345, "recreation": 0.222}  # deployed (Decision 29)
N_PERTURB = 50
PERTURB_PCT = 0.25


def composite_from_weights(df, weights):
    """Rebuild mcrai_composite as a weighted sum of existing mcrai_* columns."""
    return sum(w * df[f"mcrai_{cat}"] for cat, w in weights.items())


def evaluate(df, best_params, key):
    """Group-CV out-of-fold IAAO panel for one stratum, given the (already-set) composite."""
    X, y_s = build_features(df)
    drop = [c for c in STRATUM_DROP.get(key, []) if c in X.columns]
    if drop:
        X = X.drop(columns=drop)
    y = y_s.to_numpy(float)
    actual = df["price_per_sqm"].to_numpy(float)
    groups = df.groupby(["latitude", "longitude"]).ngroup().to_numpy()
    est = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1, **best_params)
    return iaao_panel(actual, np.exp(group_oof(est, X, y, groups)))


def main():
    manifest = json.load(open(os.path.join(MODELS_DIR, "deployment_manifest.json")))
    rows = []

    for key in ("condo", "houses"):
        df0 = pd.read_csv(os.path.join(PROCESSED_DIR, STRATA[key]["csv"])).reset_index(drop=True)
        bp = manifest["strata"][key]["best_params"]
        label = STRATA[key]["label"]

        # Named variants probing the scoring decisions.
        variants = {
            "baseline (OLS-derived 0.447/0.345/0.222)": BASELINE,
            "equal weights (3 positive cats)": {c: 1 / 3 for c in POSITIVE_CATS},
            "all 8 categories, equal (keep-positives off)": {c: 1 / 8 for c in ALL_CATS},
            "no composite (MCRAI signal removed)": {c: 0.0 for c in POSITIVE_CATS},
        }

        base_m = None
        for name, w in variants.items():
            df = df0.copy()
            df["mcrai_composite"] = composite_from_weights(df, w)
            m = evaluate(df, bp, key)
            if name.startswith("baseline"):
                base_m = m
            rows.append({
                "stratum": label, "variant": name,
                "MdAPE": m["MdAPE"], "PE20": m["PE20"], "COD": m["COD"], "PRD": m["PRD"],
                "dMdAPE": m["MdAPE"] - base_m["MdAPE"] if base_m else 0.0,
                "dPE20": m["PE20"] - base_m["PE20"] if base_m else 0.0,
            })

        # Robustness: random +/-25% perturbations of the baseline weights, renormalized.
        rng = np.random.default_rng(RANDOM_STATE)
        dmd, dpe = [], []
        for _ in range(N_PERTURB):
            factors = 1 + rng.uniform(-PERTURB_PCT, PERTURB_PCT, size=len(POSITIVE_CATS))
            raw = np.array([BASELINE[c] for c in POSITIVE_CATS]) * factors
            w = dict(zip(POSITIVE_CATS, raw / raw.sum()))
            df = df0.copy()
            df["mcrai_composite"] = composite_from_weights(df, w)
            m = evaluate(df, bp, key)
            dmd.append(m["MdAPE"] - base_m["MdAPE"])
            dpe.append(m["PE20"] - base_m["PE20"])
        rows.append({
            "stratum": label, "variant": f"+/-{int(PERTURB_PCT*100)}% weight perturbation (n={N_PERTURB})",
            "MdAPE": base_m["MdAPE"] + float(np.mean(dmd)), "PE20": base_m["PE20"] + float(np.mean(dpe)),
            "COD": np.nan, "PRD": np.nan,
            "dMdAPE": float(np.mean(np.abs(dmd))), "dPE20": float(np.mean(np.abs(dpe))),
        })
        print(f"[{label}] perturbation: mean|dMdAPE|={np.mean(np.abs(dmd)):.2f}pp "
              f"max|dMdAPE|={np.max(np.abs(dmd)):.2f}pp | mean|dPE20|={np.mean(np.abs(dpe)):.2f}pp "
              f"max|dPE20|={np.max(np.abs(dpe)):.2f}pp")

    out = pd.DataFrame(rows)
    pd.set_option("display.width", 160, "display.max_columns", 20)
    print("\n=== MCRAI composite-weight sensitivity (group-CV, RF params fixed at deployed) ===")
    print(out.to_string(index=False, float_format=lambda v: f"{v:.2f}"))
    out_path = os.path.join(MODELS_DIR, "..", "sensitivity_mcrai_weights.csv")
    out.to_csv(os.path.abspath(out_path), index=False)
    print(f"\nNote: Vacant Lot uses individual MCRAI categories (composite dropped, Decision 49),"
          f"\nso it is invariant to composite weights and is not in this table.")
    print(f"Saved -> {os.path.abspath(out_path)}")


if __name__ == "__main__":
    main()
