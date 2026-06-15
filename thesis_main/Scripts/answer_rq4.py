"""
answer_rq4.py
=============
RQ4 — quantify and map the "valuation gap": how far market and model prices sit from
BIR zonal benchmarks (Decision 44). Read-only; uses the deployed RF's leak-free
out-of-fold predictions (same GroupKFold harness as deployment). Touches no model,
manifest, or ABT.

Outputs:
    Models/stratified/valuation_gap_summary.csv     (by LGU x stratum)
    Data/processed/valuation_gap_per_property.csv    (one row per property)
    QGIS/data/valuation_gap.geojson                  (point layer for QGIS)
"""

import json
import os

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GroupKFold

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
THESIS_DIR = os.path.dirname(SCRIPT_DIR)
PROCESSED_DIR = os.path.join(THESIS_DIR, "Data", "processed")
MODELS_DIR = os.path.join(THESIS_DIR, "Models", "stratified")
QGIS_DIR = os.path.join(THESIS_DIR, "QGIS", "data")
MANIFEST = os.path.join(MODELS_DIR, "deployment_manifest.json")
os.makedirs(QGIS_DIR, exist_ok=True)

RANDOM_STATE = 42
N_SPLITS = 5
TARGET = "log_price"
STRATA = {"condo": ("abt_condo.csv", "Condominium"),
          "houses": ("abt_houses.csv", "Houses"),
          "lot": ("abt_lot.csv", "Vacant Lot")}
EXCLUDE_COLS = {"property_id", "price_type", "property_name", "address", "latitude",
                "longitude", "price_php", "price_per_sqm", "log_price", "valuation_gap"}
REDUNDANT_COLS = {"is_mactan_island"}
CAT_COLS = ["city", "property_type"]


def build_full(df, stratum_key):
    enc = pd.get_dummies(df.copy(), columns=CAT_COLS, drop_first=True, dtype=int)
    drop_set = EXCLUDE_COLS | REDUNDANT_COLS | {TARGET}
    cols = [c for c in enc.columns if c not in drop_set]
    all_null = [c for c in cols if enc[c].isna().all()]
    if all_null:
        enc[all_null] = enc[all_null].fillna(0)
    impute = [c for c in cols if enc[c].isna().any() and not enc[c].isna().all()]
    if impute:
        enc[impute] = SimpleImputer(strategy="median").fit_transform(enc[impute])
    return enc[cols].astype(float), enc[TARGET].astype(float)


def group_oof(estimator, X, y, groups):
    oof = np.zeros(len(y), float)
    for tr, te in GroupKFold(n_splits=N_SPLITS).split(X, y, groups):
        m = clone(estimator); m.fit(X.iloc[tr], y[tr]); oof[te] = m.predict(X.iloc[te])
    return oof


def main():
    with open(MANIFEST) as fh:
        man = json.load(fh)

    per_rows = []
    for key, (csv, label) in STRATA.items():
        df = pd.read_csv(os.path.join(PROCESSED_DIR, csv)).reset_index(drop=True)
        X, y_s = build_full(df, key)
        y = y_s.to_numpy(float)
        groups = df.groupby(["latitude", "longitude"]).ngroup().to_numpy()
        bp = man["strata"][key]["best_params"]
        rf = RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1, **bp)
        pred_psqm = np.exp(group_oof(rf, X, y, groups))

        sub = pd.DataFrame({
            "property_id": df.get("property_id"),
            "city": df["city"], "stratum": label,
            "latitude": df["latitude"], "longitude": df["longitude"],
            "area_sqm": df["area_sqm"],
            "price_per_sqm": df["price_per_sqm"],
            "pred_price_per_sqm": pred_psqm,
            "bir_zonal_rr_median": df["bir_zonal_rr_median"],
        })
        per_rows.append(sub)

    per = pd.concat(per_rows, ignore_index=True)
    bir = per["bir_zonal_rr_median"]
    valid = bir.notna() & (bir > 0)
    skipped = int((~valid).sum())
    per = per[valid].copy()
    per["listing_gap"] = per["price_per_sqm"] - per["bir_zonal_rr_median"]
    per["model_gap"] = per["pred_price_per_sqm"] - per["bir_zonal_rr_median"]
    per["listing_gap_pct"] = per["listing_gap"] / per["bir_zonal_rr_median"] * 100
    per["model_gap_pct"] = per["model_gap"] / per["bir_zonal_rr_median"] * 100

    per.to_csv(os.path.join(PROCESSED_DIR, "valuation_gap_per_property.csv"), index=False)

    # ---- summary by LGU x stratum ----
    def agg(g):
        return pd.Series({
            "n": len(g),
            "median_listing_gap": g["listing_gap"].median(),
            "median_model_gap": g["model_gap"].median(),
            "median_listing_gap_pct": g["listing_gap_pct"].median(),
            "median_model_gap_pct": g["model_gap_pct"].median(),
            "pct_market_above_bir": float((g["listing_gap"] > 0).mean() * 100),
        })
    summary = per.groupby(["city", "stratum"]).apply(agg, include_groups=False).reset_index()
    city_roll = per.groupby("city").apply(agg, include_groups=False).reset_index()
    city_roll.insert(1, "stratum", "ALL")
    summary = pd.concat([summary, city_roll], ignore_index=True)
    summary.to_csv(os.path.join(MODELS_DIR, "valuation_gap_summary.csv"), index=False)

    # ---- GeoJSON for QGIS ----
    feats = []
    for _, r in per.iterrows():
        if pd.isna(r["latitude"]) or pd.isna(r["longitude"]):
            continue
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [float(r["longitude"]), float(r["latitude"])]},
            "properties": {
                "city": r["city"], "stratum": r["stratum"],
                "price_per_sqm": _num(r["price_per_sqm"]),
                "pred_price_per_sqm": _num(r["pred_price_per_sqm"]),
                "bir_zonal_rr_median": _num(r["bir_zonal_rr_median"]),
                "listing_gap": _num(r["listing_gap"]),
                "model_gap": _num(r["model_gap"]),
                "listing_gap_pct": _num(r["listing_gap_pct"]),
                "model_gap_pct": _num(r["model_gap_pct"]),
            },
        })
    with open(os.path.join(QGIS_DIR, "valuation_gap.geojson"), "w") as fh:
        json.dump({"type": "FeatureCollection", "features": feats}, fh)

    print(f"Rows used: {len(per)}  (skipped {skipped} with missing/zero BIR)")
    print("\nValuation gap by LGU x stratum (median, PHP/sqm and % of BIR):")
    show = summary.copy()
    for c in ["median_listing_gap", "median_model_gap"]:
        show[c] = show[c].map(lambda v: f"{v:,.0f}")
    for c in ["median_listing_gap_pct", "median_model_gap_pct", "pct_market_above_bir"]:
        show[c] = show[c].map(lambda v: f"{v:.0f}%")
    print(show.to_string(index=False))
    print("\nWrote valuation_gap_summary.csv, valuation_gap_per_property.csv, valuation_gap.geojson")


def _num(v):
    return None if pd.isna(v) else round(float(v), 2)


if __name__ == "__main__":
    main()
