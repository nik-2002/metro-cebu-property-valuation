"""
experiment_simplified_features.py
================================
Test a LEANER feature set per stratum (2026-06-15), from the block-ablation findings:
  - GLOBAL drops (confirmed-redundant, ~0 cost): bir_zonal_rr_log, mcrai_composite, ROAD distances.
  - HOUSES additionally: the whole MCRAI block (it was noise there, ablation Δ −0.4).
  - Lots KEEP MCRAI (ablation Δ +1.7 = real signal).

Re-tunes the RF grid on the simplified set (fair comparison) and reports vs the deployed FULL model.
PARALLEL across (stratum x param-combo) cells, RF n_jobs=1 (simultaneous testing). Read-only.
"""

import os
import sys

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.ensemble import RandomForestRegressor

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from finalize_stratified_groupcv import build_features, group_oof, iaao_panel, RF_GRID, RANDOM_STATE  # noqa: E402

THESIS_DIR = os.path.dirname(SCRIPT_DIR)
PROCESSED = os.path.join(THESIS_DIR, "Data", "processed")
N_CORES = int(os.environ.get("ABLATION_CORES", "8"))

STRATA = {"condo": ("abt_condo.csv", "Condominium"),
          "houses": ("abt_houses.csv", "Houses"),
          "lot": ("abt_lot.csv", "Vacant Lot")}
DEPLOYED = {"condo": 19.8, "houses": 22.5, "lot": 38.0}

# 2026-06-15 config (user-directed): BIR 3->1 (keep rr_median) + drop ROAD + keep ONLY
# mcrai_composite (drop the 8 individual MCRAI categories; they're 0.57-0.96 inter-correlated
# and the composite carries 0.79-0.96 of each). Same drop for all strata.
GLOBAL_DROP = ["bir_zonal_rr_log", "bir_zonal_cr_median",
               "dist_to_trunk_road_m", "dist_to_primary_road_m"]


def simplified_X(key, X):
    drop = [c for c in GLOBAL_DROP if c in X.columns]
    # drop all individual mcrai_* EXCEPT the composite
    drop += [c for c in X.columns if c.startswith("mcrai_") and c != "mcrai_composite"]
    return X.drop(columns=drop), drop


def eval_combo(X, y, actual, groups, params):
    est = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=1, **params)
    p = iaao_panel(actual, np.exp(group_oof(est, X, y, groups)))
    return p["MdAPE"], p


def main():
    data, cells = {}, []
    for key, (csv, _) in STRATA.items():
        df = pd.read_csv(os.path.join(PROCESSED, csv)).reset_index(drop=True)
        Xfull, y_s = build_features(df)
        Xs, dropped = simplified_X(key, Xfull)
        data[key] = (Xs, y_s.to_numpy(float), df["price_per_sqm"].to_numpy(float),
                     df.groupby(["latitude", "longitude"]).ngroup().to_numpy(),
                     Xfull.shape[1], Xs.shape[1], dropped)
        cells += [(key, i, p) for i, p in enumerate(RF_GRID)]

    print(f"SIMPLIFIED FEATURE SET — re-tune ({len(cells)} cells / {N_CORES} cores)\n")
    res = Parallel(n_jobs=N_CORES)(
        delayed(lambda k, p: (k, *eval_combo(*data[k][:4], p)))(k, p) for k, _, p in cells)

    best = {}
    for k, md, panel in res:
        if k not in best or md < best[k][0]:
            best[k] = (md, panel)

    print(f"{'stratum':12}{'feat full→lean':>16}{'FULL MdAPE':>12}{'LEAN MdAPE':>12}{'Δ':>7}"
          f"{'COD':>7}{'PRD':>6}{'PE20':>6}")
    for key, (_, label) in STRATA.items():
        md, panel = best[key]
        ff, fs = data[key][4], data[key][5]
        print(f"{label:12}{f'{ff}→{fs}':>16}{DEPLOYED[key]:>12.1f}{md:>12.1f}"
              f"{md-DEPLOYED[key]:>+7.1f}{panel['COD']:>7.1f}{panel['PRD']:>6.2f}{panel['PE20']:>6.0f}")
    print("\ndropped per stratum:")
    for key, (_, label) in STRATA.items():
        print(f"  {label}: {data[key][6]}")


if __name__ == "__main__":
    main()
