"""
sensitivity_mcrai_beta_radii.py
================================
Non-destructive sensitivity analysis on the MCRAI *scoring* parameters that
Decision 56 did not vary: the distance-decay exponent (BETA) and the category
search radii.

Design:
  - Load the three processed stratum CSVs only in memory.
  - Load the road graph once.
  - Compute per-property, per-category network distances once at the widest
    category radius needed across all variants (baseline radius * 1.25).
  - Re-derive the 8 MCRAI category columns + composite for each variant from
    the cached distances, then re-run the deployed GroupKFold evaluation with
    deployed RF hyperparameters held fixed.

Writes:
  thesis_main/Models/sensitivity_mcrai_beta_radii.csv

Does NOT modify:
  - Data/processed/abt_clean.csv
  - Data/processed/abt_{condo,houses,lot}.csv
  - Models/stratified/deployment_manifest.json
  - deployed model pickles
"""

import json
import os
import sys
from collections import OrderedDict

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pyproj.datadir as _pyproj_datadir

    _pyproj_datadir.set_data_dir("/Users/nicoestreba/miniconda3/share/proj")
except Exception:
    pass

from compute_hansen_scores import BETA as BASELINE_BETA
from compute_hansen_scores import CATEGORY_RADII_KM, FLOOR_KM
from finalize_stratified_groupcv import MODELS_DIR, PROCESSED_DIR, STRATA
from network_utils import GRAPH_CACHE, load_metro_cebu_graph, network_distances_from_properties
from sensitivity_mcrai_weights import evaluate

COMPOSITE_WEIGHTS = {
    "education": 0.447,
    "grocery": 0.345,
    "recreation": 0.222,
}

MCRAI_CATEGORIES = list(CATEGORY_RADII_KM.keys())
RADIUS_SCALE_VARIANTS = (0.75, 1.0, 1.25)
VARIANTS = [
    {"variant": "baseline", "beta": BASELINE_BETA, "radius_scale": 1.0},
    {"variant": "beta_1.5", "beta": 1.5, "radius_scale": 1.0},
    {"variant": "beta_2.5", "beta": 2.5, "radius_scale": 1.0},
    {"variant": "radii_0.75x", "beta": BASELINE_BETA, "radius_scale": 0.75},
    {"variant": "radii_1.25x", "beta": BASELINE_BETA, "radius_scale": 1.25},
]


def load_manifest():
    manifest_path = os.path.join(MODELS_DIR, "deployment_manifest.json")
    with open(manifest_path) as fh:
        return json.load(fh)


def load_strata_frames():
    frames = OrderedDict()
    for key, cfg in STRATA.items():
        path = os.path.join(PROCESSED_DIR, cfg["csv"])
        frames[key] = pd.read_csv(path).reset_index(drop=True)
    return frames


def build_property_cache_index(strata_frames):
    rows = []
    for key, df in strata_frames.items():
        subset = df[["property_id", "latitude", "longitude"]].copy()
        subset["stratum"] = key
        rows.append(subset)
    props = pd.concat(rows, ignore_index=True)

    if props["property_id"].isna().any():
        raise ValueError("property_id contains nulls; expected stable join key")
    if props["property_id"].duplicated().any():
        dupes = props.loc[props["property_id"].duplicated(), "property_id"].head(10).tolist()
        raise ValueError(f"property_id is not unique across strata; sample duplicates: {dupes}")
    if props[["latitude", "longitude"]].isna().any().any():
        raise ValueError("latitude/longitude contains nulls; cannot compute network distances")

    return props


def load_amenity_coords(thesis_dir):
    amenities_dir = os.path.join(thesis_dir, "Data", "amenities")
    amenity_coords = {}
    for category in MCRAI_CATEGORIES:
        path = os.path.join(amenities_dir, f"{category}.csv")
        df = pd.read_csv(path)
        amenity_coords[category] = (df["lat"].to_numpy(float), df["lon"].to_numpy(float))
        print(f"Loaded {len(df):>4} amenities for {category}")
    return amenity_coords


def max_radius_by_category():
    return {cat: radius * max(RADIUS_SCALE_VARIANTS) for cat, radius in CATEGORY_RADII_KM.items()}


def compute_distance_cache(props, amenity_coords):
    print("\nLoading Metro Cebu road graph once...")
    cache_candidates = [
        os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..",
                "..",
                "..",
                "..",
                "thesis",
                "thesis_main",
                "Data",
                "processed",
                "metro_cebu_network.pkl",
            )
        ),
        GRAPH_CACHE,
    ]
    cache_path = next((path for path in cache_candidates if os.path.exists(path)), GRAPH_CACHE)
    print(f"Using graph cache path: {cache_path}")
    graph = load_metro_cebu_graph(cache_path=cache_path)

    source_coords = list(zip(props["latitude"].to_numpy(float), props["longitude"].to_numpy(float)))
    category_radii = max_radius_by_category()
    print(f"\nComputing network distances once for {len(source_coords)} properties...")
    dist_results = network_distances_from_properties(
        graph,
        source_coords,
        amenity_coords,
        category_radii=category_radii,
    )

    cache = {}
    for idx, property_id in enumerate(props["property_id"].tolist()):
        cache[property_id] = dist_results[idx]
    return cache


def score_property_from_cache(category_distances, beta, radius_scale):
    scores = {}
    for category in MCRAI_CATEGORIES:
        cutoff = CATEGORY_RADII_KM[category] * radius_scale
        dists = category_distances[category]
        if len(dists) == 0:
            scores[f"mcrai_{category}"] = 0.0
            continue
        within = dists[dists <= cutoff]
        if len(within) == 0:
            scores[f"mcrai_{category}"] = 0.0
            continue
        floored = np.maximum(within, FLOOR_KM)
        scores[f"mcrai_{category}"] = float(np.sum(1.0 / (floored ** beta)))

    scores["mcrai_composite"] = float(
        sum(COMPOSITE_WEIGHTS[cat] * scores[f"mcrai_{cat}"] for cat in COMPOSITE_WEIGHTS)
    )
    return scores


def build_variant_scores(props, distance_cache, beta, radius_scale):
    score_rows = []
    for property_id in props["property_id"].tolist():
        row = {"property_id": property_id}
        row.update(score_property_from_cache(distance_cache[property_id], beta, radius_scale))
        score_rows.append(row)
    scores = pd.DataFrame(score_rows)

    mcrai_cols = [c for c in scores.columns if c.startswith("mcrai_")]
    scores[mcrai_cols] = scores[mcrai_cols].round(4)
    return scores


def inject_scores(df, scores):
    merged = df.drop(columns=[c for c in scores.columns if c != "property_id" and c in df.columns]).merge(
        scores,
        on="property_id",
        how="left",
        validate="one_to_one",
    )
    if len(merged) != len(df):
        raise ValueError(f"Row count changed after score injection: {len(df)} -> {len(merged)}")
    missing = merged[[c for c in scores.columns if c != "property_id"]].isna().any(axis=1).sum()
    if missing:
        raise ValueError(f"Score injection left {missing} rows without recomputed MCRAI values")
    return merged


def evaluate_variant(strata_frames, scores, manifest, variant_name, beta, radius_scale):
    rows = []
    baseline_mdape = {}
    per_stratum = {}

    for key, df0 in strata_frames.items():
        df = inject_scores(df0.copy(), scores)
        metrics = evaluate(df, manifest["strata"][key]["best_params"], key)
        per_stratum[key] = metrics
        row = {
            "stratum": key,
            "variant": variant_name,
            "beta": beta,
            "radius_scale": radius_scale,
            "MdAPE": metrics["MdAPE"],
            "PE20": metrics["PE20"],
        }
        rows.append(row)
        baseline_mdape[key] = metrics["MdAPE"]

    return rows, per_stratum, baseline_mdape


def print_summary(results_df):
    display = results_df.copy()
    display["MdAPE_delta_vs_baseline"] = display["MdAPE_delta_vs_baseline"].map(lambda v: f"{v:+.2f}")
    display["MdAPE"] = display["MdAPE"].map(lambda v: f"{v:.2f}")
    display["PE20"] = display["PE20"].map(lambda v: f"{v:.2f}")
    display["beta"] = display["beta"].map(lambda v: f"{v:.1f}")
    display["radius_scale"] = display["radius_scale"].map(lambda v: f"{v:.2f}")
    print("\n=== MCRAI beta/radii sensitivity (group-CV, RF params fixed at deployed) ===")
    print(display.to_string(index=False))

    lot_rows = results_df.loc[results_df["stratum"] == "lot", ["variant", "MdAPE_delta_vs_baseline", "PE20"]]
    print("\nVacant Lot deltas vs baseline:")
    for row in lot_rows.itertuples(index=False):
        print(f"  {row.variant:<12} MdAPE delta {row.MdAPE_delta_vs_baseline:+.2f} pp | PE20 {row.PE20:.2f}")


def main():
    manifest = load_manifest()
    strata_frames = load_strata_frames()
    props = build_property_cache_index(strata_frames)
    thesis_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    amenity_coords = load_amenity_coords(thesis_dir)
    distance_cache = compute_distance_cache(props, amenity_coords)

    all_rows = []
    baseline_mdape = {}
    for spec in VARIANTS:
        print(
            f"\nRunning variant={spec['variant']}  beta={spec['beta']:.1f}  "
            f"radius_scale={spec['radius_scale']:.2f}"
        )
        scores = build_variant_scores(props, distance_cache, spec["beta"], spec["radius_scale"])
        variant_rows, _, baseline_candidate = evaluate_variant(
            strata_frames, scores, manifest, spec["variant"], spec["beta"], spec["radius_scale"]
        )
        if spec["variant"] == "baseline":
            baseline_mdape = baseline_candidate
        for row in variant_rows:
            row["MdAPE_delta_vs_baseline"] = row["MdAPE"] - baseline_mdape[row["stratum"]]
            all_rows.append(row)

    out = pd.DataFrame(all_rows)
    out = out[
        ["stratum", "variant", "beta", "radius_scale", "MdAPE", "PE20", "MdAPE_delta_vs_baseline"]
    ]
    print_summary(out)

    out_path = os.path.abspath(os.path.join(MODELS_DIR, "..", "sensitivity_mcrai_beta_radii.csv"))
    out.to_csv(out_path, index=False)
    print(f"\nSaved -> {out_path}")


if __name__ == "__main__":
    main()
