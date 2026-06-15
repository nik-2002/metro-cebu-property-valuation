"""
hyperparameter_tuning_sweep.py
==============================
Wider, non-conservative hyperparameter exploration for the stratified models, plus
elbow-method sweep plots (performance vs one parameter at a time). Read-only; does
NOT touch deployed models or the manifest.

All scoring uses the leak-free harness: MdAPE under GroupKFold(5), groups = coordinate
cluster, random_state=42 (identical to deployment).

Outputs:
  EDA/tables/hpo_grid_results_rf.csv    full RF grid (every combo + MdAPE/PE20)
  EDA/tables/hpo_grid_results_xgb.csv   full XGB grid
  EDA/tables/hpo_best_params.csv        best-found vs deployed, per stratum/model
  EDA/plots/11_hyperparameter_tuning/{rf,xgb}_<param>.png   elbow sweeps
"""

import itertools
import json
import os
import warnings

# Cap BLAS threads BEFORE numpy import so single-threaded fits don't contend.
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold
from xgboost import XGBRegressor

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from answer_rq2_rq3 import build_full_and_ols, STRATA, PROCESSED_DIR, MANIFEST

THESIS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES_DIR = os.path.join(THESIS_DIR, "EDA", "tables")
PLOTS_DIR = os.path.join(THESIS_DIR, "EDA", "plots", "11_hyperparameter_tuning")
os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

RANDOM_STATE, N_SPLITS = 42, 5
LABELS = {"condo": "Condominium", "houses": "Houses", "lot": "Vacant Lot"}
COLORS = {"condo": "#3b6fb6", "houses": "#4f9d5d", "lot": "#c89a2b"}

# Deployed XGB best (from answer_rq2_rq3 leak-free run) — used as the hold-constant base.
XGB_BEST = {
    "condo":  {"n_estimators": 300, "max_depth": 3, "learning_rate": 0.05, "subsample": 0.9},
    "houses": {"n_estimators": 500, "max_depth": 3, "learning_rate": 0.05, "subsample": 0.9},
    "lot":    {"n_estimators": 300, "max_depth": 5, "learning_rate": 0.05, "subsample": 0.9},
}

# ---- Exploratory grids (sized to finish single-threaded in ~3 min) ----
RF_GRID = {
    "n_estimators": [200, 400],
    "max_features": [0.7, 1.0],
    "min_samples_leaf": [1, 2],
    "max_depth": [None, 20],
}  # 16 combos
XGB_GRID = {
    "n_estimators": [200, 400],
    "max_depth": [3, 5],
    "learning_rate": [0.05, 0.1],
    "subsample": [0.8, 1.0],
}  # 16 combos

# ---- Sweep ranges (one param at a time; others held at the per-stratum best) ----
# These drive the elbow plots — the primary deliverable.
RF_SWEEPS = {
    "n_estimators": [100, 200, 300, 400, 500, 600],
    "max_depth": [3, 5, 10, 15, 20, "None"],
    "max_features": [0.3, 0.5, 0.7, 0.9, 1.0],
    "min_samples_leaf": [1, 2, 4, 8],
}
XGB_SWEEPS = {
    "n_estimators": [100, 200, 300, 400, 500, 600],
    "max_depth": [2, 3, 4, 5, 6, 8],
    "learning_rate": [0.01, 0.03, 0.05, 0.1, 0.2, 0.3],
    "subsample": [0.6, 0.8, 0.9, 1.0],
}


def mdape(actual, pred):
    return float(np.median(np.abs(pred / actual - 1)) * 100)


def pe20(actual, pred):
    return float(np.mean(np.abs(pred / actual - 1) <= 0.20) * 100)


def oof_mdape_pe20(estimator, X, y, groups, actual):
    oof = np.zeros(len(y))
    for tr, te in GroupKFold(N_SPLITS).split(X, y, groups):
        m = clone(estimator); m.fit(X.iloc[tr], y[tr]); oof[te] = m.predict(X.iloc[te])
    p = np.exp(oof)
    return mdape(actual, p), pe20(actual, p)


def make_rf(params):
    return RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=1, **params)


def make_xgb(params):
    return XGBRegressor(random_state=RANDOM_STATE, n_jobs=1, verbosity=0, **params)


def load_stratum(key):
    df = pd.read_csv(os.path.join(PROCESSED_DIR, STRATA[key]["csv"])).reset_index(drop=True)
    X, _, y_s = build_full_and_ols(df, key)
    y = y_s.to_numpy(float)
    actual = df["price_per_sqm"].to_numpy(float)
    groups = df.groupby(["latitude", "longitude"]).ngroup().to_numpy()
    return X, y, groups, actual


def grid_search(make_fn, grid, data, deployed_md):
    keys = list(grid)
    rows, best = [], {}
    for key in STRATA:
        X, y, groups, actual = data[key]
        best_md = None
        for combo in itertools.product(*(grid[k] for k in keys)):
            params = dict(zip(keys, combo))
            md, p20 = oof_mdape_pe20(make_fn(params), X, y, groups, actual)
            rows.append({"stratum": LABELS[key], **params, "MdAPE": md, "PE20": p20})
            if best_md is None or md < best_md["MdAPE"]:
                best_md = {"MdAPE": md, "PE20": p20, **params}
        best[key] = best_md
        print(f"    {LABELS[key]:12s} best MdAPE={best_md['MdAPE']:.2f}%  "
              f"(deployed {deployed_md[key]:.2f}%)  params={ {k:best_md[k] for k in keys} }")
    return pd.DataFrame(rows), best


def sweep_plot(make_fn, model_name, fname_prefix, param, values, base_params, data, deployed_val):
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(7, 4.2))
    xpos = list(range(len(values)))
    sweep_rows = []
    for key in STRATA:
        X, y, groups, actual = data[key]
        ys = []
        for v in values:
            p = dict(base_params[key])
            p[param] = (None if v == "None" else v)
            md, _ = oof_mdape_pe20(make_fn(p), X, y, groups, actual)
            ys.append(md)
            sweep_rows.append({"model": model_name, "param": param, "stratum": LABELS[key],
                               "value": str(v), "MdAPE": md})
        ax.plot(xpos, ys, marker="o", ms=5, lw=1.8, color=COLORS[key], label=LABELS[key])
        # mark the deployed value for this stratum, if present in the swept range
        dv = deployed_val[key]
        dv_key = "None" if dv is None else dv
        if dv_key in values:
            i = values.index(dv_key)
            ax.scatter([i], [ys[i]], s=150, marker="*", color=COLORS[key],
                       edgecolor="black", linewidth=0.6, zorder=5)
    ax.set_xticks(xpos)
    ax.set_xticklabels([str(v) for v in values])
    ax.set_xlabel(param)
    ax.set_ylabel("MdAPE (%)  — lower is better")
    ax.set_title(f"{model_name}: MdAPE vs {param}   (deployed = starred point; other params at best)", fontsize=11)
    ax.legend(title=None, frameon=False, fontsize=9)
    sns.despine(ax=ax)
    fig.tight_layout()
    out = os.path.join(PLOTS_DIR, f"{fname_prefix}_{param}.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"    saved {out}")
    return sweep_rows


def main():
    man = json.load(open(MANIFEST))
    rf_deployed = {k: man["strata"][k]["best_params"] for k in STRATA}
    rf_deployed_md = {k: man["strata"][k]["metrics_group_cv"]["MdAPE"] for k in STRATA}
    # XGB deployed-md: recompute quickly from its base
    data = {k: load_stratum(k) for k in STRATA}
    xgb_deployed_md = {}
    for k in STRATA:
        X, y, g, a = data[k]
        xgb_deployed_md[k], _ = oof_mdape_pe20(make_xgb(XGB_BEST[k]), X, y, g, a)

    print("WIDER GRID SEARCH — Random Forest")
    rf_rows, rf_best = grid_search(make_rf, RF_GRID, data, rf_deployed_md)
    rf_rows.to_csv(os.path.join(TABLES_DIR, "hpo_grid_results_rf.csv"), index=False)

    print("WIDER GRID SEARCH — XGBoost")
    xgb_rows, xgb_best = grid_search(make_xgb, XGB_GRID, data, xgb_deployed_md)
    xgb_rows.to_csv(os.path.join(TABLES_DIR, "hpo_grid_results_xgb.csv"), index=False)

    # best vs deployed summary
    summ = []
    for k in STRATA:
        summ.append({"model": "RandomForest", "stratum": LABELS[k],
                     "deployed_MdAPE": round(rf_deployed_md[k], 2),
                     "best_found_MdAPE": round(rf_best[k]["MdAPE"], 2),
                     "improvement_pp": round(rf_deployed_md[k] - rf_best[k]["MdAPE"], 2),
                     "best_params": {p: rf_best[k][p] for p in RF_GRID}})
        summ.append({"model": "XGBoost", "stratum": LABELS[k],
                     "deployed_MdAPE": round(xgb_deployed_md[k], 2),
                     "best_found_MdAPE": round(xgb_best[k]["MdAPE"], 2),
                     "improvement_pp": round(xgb_deployed_md[k] - xgb_best[k]["MdAPE"], 2),
                     "best_params": {p: xgb_best[k][p] for p in XGB_GRID}})
    pd.DataFrame(summ).to_csv(os.path.join(TABLES_DIR, "hpo_best_params.csv"), index=False)

    print("\nELBOW SWEEP PLOTS — Random Forest")
    rf_base = {k: dict(rf_deployed[k]) for k in STRATA}
    all_sweeps = []
    for param, vals in RF_SWEEPS.items():
        dv = {k: rf_deployed[k].get(param) for k in STRATA}
        all_sweeps += sweep_plot(make_rf, "Random Forest", "rf", param, vals, rf_base, data, dv)

    print("ELBOW SWEEP PLOTS — XGBoost")
    xgb_base = {k: dict(XGB_BEST[k]) for k in STRATA}
    for param, vals in XGB_SWEEPS.items():
        dv = {k: XGB_BEST[k].get(param) for k in STRATA}
        all_sweeps += sweep_plot(make_xgb, "XGBoost", "xgb", param, vals, xgb_base, data, dv)
    pd.DataFrame(all_sweeps).to_csv(os.path.join(TABLES_DIR, "hpo_sweeps.csv"), index=False)

    print("\n=== BEST-FOUND vs DEPLOYED ===")
    print(pd.DataFrame(summ)[["model", "stratum", "deployed_MdAPE", "best_found_MdAPE", "improvement_pp"]].to_string(index=False))


if __name__ == "__main__":
    main()
