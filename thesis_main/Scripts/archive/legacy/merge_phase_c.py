"""Append Phase C Lamudi rows to the cleaned ABT and enrich only the new slice."""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from compute_hansen_scores import BETA, FLOOR_KM, CATEGORY_RADII_KM
from join_bir_zonal import join_bir_to_abt, reverse_geocode_abt
from network_utils import load_metro_cebu_graph, network_distances_from_properties, network_distances_from_sources


WORKSPACE_ROOT = SCRIPT_DIR.parents[1]
ABT_PATH = WORKSPACE_ROOT / "thesis_main" / "Data" / "processed" / "abt_clean.csv"
PHASE_C_PATH = WORKSPACE_ROOT / "thesis_main" / "Data" / "raw" / "phase_c_lamudi.csv"
CBD_NODES_PATH = WORKSPACE_ROOT / "thesis_main" / "Data" / "processed" / "cbd_nodes.csv"
BIR_SUMMARY_PATH = WORKSPACE_ROOT / "thesis_main" / "Data" / "BIR Zonal Values" / "bir_barangay_summary.csv"
AMENITIES_DIR = WORKSPACE_ROOT / "thesis_main" / "Data" / "amenities"

AIRPORT = (10.30719, 123.97899)
SPATIAL_LAG_RADIUS_M = 1_000
EARTH_RADIUS_M = 6_371_000
LAT_DEG_PER_M = 1 / 111_320
LON_DEG_PER_M = 1 / 109_639

AMENITY_CATEGORIES = [
    "education",
    "finance",
    "grocery",
    "health",
    "security",
    "transport",
    "tourism",
    "recreation",
    "retail_density",
]

# Decision 20 final composite: positive-coefficient OLS categories only.
MCRAI_WEIGHTS = {
    "education": 0.401,
    "grocery": 0.310,
    "recreation": 0.199,
    "transport": 0.102,
}


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    rlat1, rlon1, rlat2, rlon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    abt = pd.read_csv(ABT_PATH)
    phase = pd.read_csv(PHASE_C_PATH)
    return abt, phase


def compute_area_sqm(df: pd.DataFrame) -> pd.Series:
    lot = pd.to_numeric(df["lot_area_sqm"], errors="coerce")
    floor = pd.to_numeric(df["floor_area_sqm"], errors="coerce")
    return pd.Series(
        np.where(
            lot.isna(),
            floor,
            np.where(floor.isna(), lot, np.maximum(lot, floor)),
        ),
        index=df.index,
        dtype="float64",
    )


def align_phase_schema(existing_abt: pd.DataFrame, phase: pd.DataFrame) -> pd.DataFrame:
    missing_cols = [col for col in existing_abt.columns if col not in phase.columns]
    for col in missing_cols:
        phase[col] = np.nan

    phase = phase.reindex(columns=existing_abt.columns).copy()

    next_property_id = int(existing_abt["property_id"].max()) + 1
    phase["property_id"] = np.arange(next_property_id, next_property_id + len(phase))
    phase["market_segment"] = "open_market"
    phase["source"] = "Lamudi"
    phase["price_type"] = "open_market"
    phase["geocode_source"] = "Lamudi_json_ld"
    phase["price_outlier_flag"] = False
    phase["is_mactan_island"] = (phase["city"] == "Lapu-Lapu City").astype(int)
    phase["is_vacant_lot"] = (phase["property_type"] == "Vacant Lot").astype(int)
    phase["bedrooms_imputed"] = phase["bedrooms"].isna().astype(int)
    phase["bathrooms_imputed"] = phase["bathrooms"].isna().astype(int)
    phase["floor_area_imputed"] = phase["floor_area_sqm"].isna().astype(int)
    return phase


def enrich_cbd_distances(new_rows: pd.DataFrame) -> pd.DataFrame:
    nodes_df = pd.read_csv(CBD_NODES_PATH).set_index("hub_id")
    cbd_nodes = {
        hub_id: (row["centroid_lat"], row["centroid_lon"])
        for hub_id, row in nodes_df.iterrows()
    }

    valid_mask = new_rows["latitude"].notna() & new_rows["longitude"].notna()
    valid_indices = new_rows.index[valid_mask].tolist()
    valid_coords = list(zip(new_rows.loc[valid_mask, "latitude"], new_rows.loc[valid_mask, "longitude"]))

    for hub_id in cbd_nodes:
        new_rows[f"dist_{hub_id}_m"] = np.nan
    new_rows["dist_airport_m"] = np.nan

    if not valid_coords:
        return new_rows

    graph = load_metro_cebu_graph()
    net_dists, _ = network_distances_from_sources(graph, valid_coords, cbd_nodes)
    for list_pos, df_idx in enumerate(valid_indices):
        lat = new_rows.at[df_idx, "latitude"]
        lon = new_rows.at[df_idx, "longitude"]
        for hub_id in cbd_nodes:
            col = f"dist_{hub_id}_m"
            new_rows.at[df_idx, col] = round(net_dists[list_pos][hub_id], 1)
        new_rows.at[df_idx, "dist_airport_m"] = round(haversine_m(lat, lon, *AIRPORT), 1)

    return new_rows


def enrich_mcrai(new_rows: pd.DataFrame) -> pd.DataFrame:
    valid_mask = new_rows["latitude"].notna() & new_rows["longitude"].notna()
    valid_indices = new_rows.index[valid_mask].tolist()
    source_coords = list(zip(new_rows.loc[valid_mask, "latitude"], new_rows.loc[valid_mask, "longitude"]))

    for category in AMENITY_CATEGORIES:
        new_rows[f"mcrai_{category}"] = 0.0
    new_rows["mcrai_composite"] = 0.0

    if not source_coords:
        return new_rows

    amenities = {category: pd.read_csv(AMENITIES_DIR / f"{category}.csv") for category in AMENITY_CATEGORIES}
    amenity_coords = {
        category: (amenities[category]["lat"].values, amenities[category]["lon"].values)
        for category in AMENITY_CATEGORIES
    }

    graph = load_metro_cebu_graph()
    dist_results = network_distances_from_properties(
        graph,
        source_coords,
        amenity_coords,
        category_radii=CATEGORY_RADII_KM,
    )

    for category in AMENITY_CATEGORIES:
        col_vals = [0.0] * len(new_rows)
        for list_pos, df_idx in enumerate(valid_indices):
            dists = dist_results[list_pos][category]
            if len(dists) == 0:
                continue
            dists_floored = np.maximum(dists, FLOOR_KM)
            col_vals[df_idx] = float(np.sum(1.0 / (dists_floored ** BETA)))
        new_rows[f"mcrai_{category}"] = col_vals

    composite = np.zeros(len(new_rows))
    for category, weight in MCRAI_WEIGHTS.items():
        composite += weight * new_rows[f"mcrai_{category}"].astype(float)
    new_rows["mcrai_composite"] = composite.round(4)

    mcrai_cols = [f"mcrai_{category}" for category in AMENITY_CATEGORIES]
    new_rows[mcrai_cols] = new_rows[mcrai_cols].round(4)
    return new_rows


def enrich_bir(new_rows: pd.DataFrame) -> pd.DataFrame:
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    bir_summary = pd.read_csv(BIR_SUMMARY_PATH)
    bir_enriched = reverse_geocode_abt(new_rows.copy(), api_key)
    return join_bir_to_abt(bir_enriched, bir_summary)


def recompute_new_derived(new_rows: pd.DataFrame, merged_all: pd.DataFrame) -> pd.DataFrame:
    new_rows["area_sqm"] = compute_area_sqm(new_rows)
    valid_area = new_rows["area_sqm"].notna() & (new_rows["area_sqm"] > 0)
    new_rows["price_per_sqm"] = np.nan
    new_rows.loc[valid_area, "price_per_sqm"] = (
        pd.to_numeric(new_rows.loc[valid_area, "price_php"], errors="coerce")
        / pd.to_numeric(new_rows.loc[valid_area, "area_sqm"], errors="coerce")
    )
    positive_ppsqm = new_rows["price_per_sqm"] > 0
    new_rows["log_price"] = np.nan
    new_rows.loc[positive_ppsqm, "log_price"] = np.log(new_rows.loc[positive_ppsqm, "price_per_sqm"])
    new_rows["valuation_gap"] = new_rows["price_per_sqm"] - new_rows["bir_zonal_rr_median"]

    price_arr = pd.to_numeric(merged_all["price_php"], errors="coerce").to_numpy()
    coord_arr = merged_all[["latitude", "longitude"]].to_numpy(dtype=float)
    tree = cKDTree(coord_arr)
    radius_deg = SPATIAL_LAG_RADIUS_M * max(LAT_DEG_PER_M, LON_DEG_PER_M) * 1.02
    id_to_pos = {pid: pos for pos, pid in enumerate(merged_all["property_id"].tolist())}

    lag_vals = []
    for _, row in new_rows.iterrows():
        lat = row["latitude"]
        lon = row["longitude"]
        if pd.isna(lat) or pd.isna(lon):
            lag_vals.append(np.nan)
            continue
        self_pos = id_to_pos[row["property_id"]]
        neighbours = tree.query_ball_point([lat, lon], r=radius_deg)
        neighbour_prices = [
            price_arr[pos]
            for pos in neighbours
            if pos != self_pos
            and not np.isnan(price_arr[pos])
            and haversine_m(lat, lon, coord_arr[pos][0], coord_arr[pos][1]) <= SPATIAL_LAG_RADIUS_M
        ]
        lag_vals.append(round(float(np.nanmean(neighbour_prices))) if neighbour_prices else np.nan)

    new_rows["spatial_lag_price"] = lag_vals
    return new_rows


def main() -> None:
    existing_abt, phase_c = load_inputs()
    existing_rows = len(existing_abt)
    phase_rows = len(phase_c)

    print("=" * 70)
    print("Merge Phase C Lamudi Into Clean ABT")
    print("=" * 70)
    print(f"Existing ABT rows: {existing_rows}")
    print(f"Phase C rows: {phase_rows}")

    new_rows = align_phase_schema(existing_abt, phase_c)
    new_rows = enrich_cbd_distances(new_rows)
    new_rows = enrich_mcrai(new_rows)
    new_rows = enrich_bir(new_rows)

    merged_all = pd.concat([existing_abt, new_rows], ignore_index=True)
    new_rows = recompute_new_derived(new_rows, merged_all)
    merged_all = pd.concat([existing_abt, new_rows], ignore_index=True)
    merged_all = merged_all[existing_abt.columns].reset_index(drop=True)

    ABT_PATH.parent.mkdir(parents=True, exist_ok=True)
    merged_all.to_csv(ABT_PATH, index=False)

    print(f"Existing rows: {existing_rows}")
    print(f"New rows appended: {phase_rows}")
    print(f"Total rows: {len(merged_all)}")
    print(f"open_market rows: {(merged_all['market_segment'] == 'open_market').sum()}")
    print(f"Rows with null price_per_sqm: {merged_all['price_per_sqm'].isna().sum()}")


if __name__ == "__main__":
    main()
