"""Compute Metro Cebu Residential Accessibility Index (MCRAI) scores."""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from network_utils import load_metro_cebu_graph, network_distances_from_properties

BETA = 2.0
FLOOR_KM = 0.5

CATEGORY_RADII_KM = {
    # Decision 30 (2026-05-22): education 0.8→2.5 (jeepney-mode-corrected school catchment,
    # Philippine learner survey median home-to-school distance 3-5 km); hospitals 3.0→5.0
    # (standard tertiary-care catchment methodology, 42 hospitals across 6 LGUs).
    "education":      2.5,
    "health":         2.0,
    "hospitals":      5.0,
    "grocery":        2.0,
    "security":       2.0,
    "tourism":        3.0,
    "recreation":     1.5,
    "retail_density": 1.0,
}


def main():
    base_dir = Path(__file__).resolve().parents[1]
    abt_path = base_dir / "Data" / "processed" / "abt_clean.csv"
    amenities_dir = base_dir / "Data" / "amenities"

    print(f"Loading ABT from {abt_path}")
    abt = pd.read_csv(abt_path)
    print(f"ABT shape before: {abt.shape}")

    hansen_cols = [col for col in abt.columns if col.startswith("hansen_")]
    if hansen_cols:
        abt.drop(columns=hansen_cols, inplace=True)
        print(f"Dropped legacy hansen columns: {hansen_cols}")

    # Decision 28: mcrai_finance retired (no SE Asian hedonic basis).
    # Decision 29: mcrai_transport retired in favor of dist_to_trunk_road_m / dist_to_primary_road_m.
    for stale_col in ("mcrai_finance", "mcrai_transport"):
        if stale_col in abt.columns:
            abt.drop(columns=[stale_col], inplace=True)
            print(f"Dropped stale {stale_col} column")

    if "latitude" not in abt.columns or "longitude" not in abt.columns:
        raise ValueError("ABT must have latitude and longitude columns")

    amenity_categories = [
        "education",
        "grocery",
        "health",
        "hospitals",
        "security",
        "tourism",
        "recreation",
        "retail_density",
    ]
    amenities = {}
    for category in amenity_categories:
        path = amenities_dir / f"{category}.csv"
        if not path.exists():
            raise FileNotFoundError(f"Amenity file not found: {path}")
        df = pd.read_csv(path)
        amenities[category] = df
        print(f"Loaded {len(df)} {category} amenities")

    print("\nLoading Metro Cebu road network...")
    G = load_metro_cebu_graph()

    valid_mask = abt["latitude"].notna() & abt["longitude"].notna()
    valid_indices = abt.index[valid_mask].tolist()
    source_coords = list(zip(abt.loc[valid_mask, "latitude"], abt.loc[valid_mask, "longitude"]))

    amenity_coords = {
        category: (amenities[category]["lat"].values, amenities[category]["lon"].values)
        for category in amenity_categories
    }

    print(f"\nComputing network distances for {len(source_coords)} properties...")
    dist_results = network_distances_from_properties(
        G,
        source_coords,
        amenity_coords,
        category_radii=CATEGORY_RADII_KM,
    )

    for category in amenity_categories:
        abt[f"mcrai_{category}"] = 0.0

    for category in amenity_categories:
        print(f"Computing mcrai_{category}...")
        col_vals = [0.0] * len(abt)
        for list_pos, df_idx in enumerate(valid_indices):
            dists = dist_results[list_pos][category]
            if len(dists) == 0:
                col_vals[df_idx] = 0.0
            else:
                dists_floored = np.maximum(dists, FLOOR_KM)
                col_vals[df_idx] = float(np.sum(1.0 / (dists_floored ** BETA)))
        abt[f"mcrai_{category}"] = col_vals

    print("Computing mcrai_composite...")
    # Stage 2 MCRAI weights — Decision 20 (positive-coefficient OLS categories only),
    # renormalized after Decision 29 retired mcrai_transport in favor of
    # dist_to_trunk_road_m and dist_to_primary_road_m (computed in compute_road_distances.py).
    # security, tourism, retail_density remain individual model features only (not in composite).
    weights = {
        "education":  0.447,
        "grocery":    0.345,
        "recreation": 0.222,
    }
    abt["mcrai_composite"] = sum(weights[category] * abt[f"mcrai_{category}"] for category in weights)

    mcrai_cols = [col for col in abt.columns if col.startswith("mcrai_")]
    for col in mcrai_cols:
        abt[col] = abt[col].round(4)

    if "is_mactan_island" not in abt.columns:
        abt["is_mactan_island"] = (abt["city"] == "Lapu-Lapu City").astype(int)
        print(f"is_mactan_island added: {abt['is_mactan_island'].sum()} rows = 1")

    amenity_score_cols = [col for col in abt.columns if col.startswith("amenity_score_")]
    if amenity_score_cols:
        abt.drop(columns=amenity_score_cols, inplace=True)
        print(f"Dropped amenity_score columns: {amenity_score_cols}")

    print(f"\nABT shape after: {abt.shape}")
    print("\nMCRAI score statistics:")
    for col in mcrai_cols:
        print(f"  {col}: mean={abt[col].mean():.4f}  zeros={(abt[col] == 0.0).sum()}")

    print(f"\nSaving ABT to {abt_path}")
    abt.to_csv(abt_path, index=False)
    print("Done.")


if __name__ == "__main__":
    main()
