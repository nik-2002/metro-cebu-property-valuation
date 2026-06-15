"""Fill CBD-node distances, airport distance, and spatial_lag_price.

compute_road_distances.py only fills the trunk/primary road distances; the 7
CBD-node network distances, the airport haversine distance, and spatial_lag_price
have no standalone current script (they were historically filled inside the merge
step). This reuses the canonical network_utils functions to fill them:

- 7 CBD-node distances (Dijkstra on the cached Metro Cebu graph) — only for rows
  that are still missing them (the newly appended batch).
- dist_airport_m (haversine) — same rows.
- spatial_lag_price — recomputed for ALL rows over the full ABT (1km radius, mean
  neighbour total price), so the neighbour pool is consistent after the new rows
  are added.

Operates on abt_clean.csv in place.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

SCRIPT_DIR = Path(__file__).resolve().parent
THESIS_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from network_utils import load_metro_cebu_graph, network_distances_from_sources  # noqa: E402

ABT_PATH = THESIS_DIR / "Data" / "processed" / "abt_clean.csv"
CBD_NODES_PATH = THESIS_DIR / "Data" / "processed" / "cbd_nodes.csv"

AIRPORT = (10.30719, 123.97899)
# 500 m spatial-lag radius (2026-06-14): walkable-neighbourhood scale. Grounded in
# arXiv 1902.00562 ("The Spatially-Conscious Machine Learning Model"), which aggregates
# spatial-lag features within 500 m of each property, and consistent with this thesis's own
# MCRAI "micro" amenity scale (500-800 m). Replaces the earlier 1 km radius.
SPATIAL_LAG_RADIUS_M = 500
EARTH_RADIUS_M = 6_371_000
LAT_DEG_PER_M = 1 / 111_320
LON_DEG_PER_M = 1 / 109_639


def haversine_m(lat1, lon1, lat2, lon2):
    r1, o1, r2, o2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = r2 - r1, o2 - o1
    a = np.sin(dlat / 2) ** 2 + np.cos(r1) * np.cos(r2) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * np.arcsin(np.sqrt(a))


def main():
    abt = pd.read_csv(ABT_PATH)
    print(f"ABT: {abt.shape}")

    nodes = pd.read_csv(CBD_NODES_PATH).set_index("hub_id")
    cbd_nodes = {hid: (r["centroid_lat"], r["centroid_lon"]) for hid, r in nodes.iterrows()}
    cbd_cols = [f"dist_{hid}_m" for hid in cbd_nodes]

    # rows missing CBD distances (the new batch)
    need = abt[cbd_cols[0]].isna() & abt["latitude"].notna() & abt["longitude"].notna()
    idx = abt.index[need].tolist()
    print(f"Rows needing CBD/airport distances: {len(idx)}")

    if idx:
        coords = list(zip(abt.loc[idx, "latitude"], abt.loc[idx, "longitude"]))
        G = load_metro_cebu_graph()
        net, _ = network_distances_from_sources(G, coords, cbd_nodes)
        for pos, di in enumerate(idx):
            for hid in cbd_nodes:
                abt.at[di, f"dist_{hid}_m"] = round(net[pos][hid], 1)
            abt.at[di, "dist_airport_m"] = round(
                float(haversine_m(abt.at[di, "latitude"], abt.at[di, "longitude"], *AIRPORT)), 1
            )
        print("  CBD + airport distances filled.")

    # spatial_lag_price — recompute for ALL rows over the full ABT.
    # SAME-STRATUM neighbours only (2026-06-14): a property's neighbourhood price level should
    # average comparable products, not mix vacant lots with condo towers. Group at the stratum
    # level (Condo / Houses / Lot) so a Single Detached still learns from nearby House-and-Lot
    # (same market) without rare labels (Townhouse) becoming too sparse.
    STRATUM_MAP = {
        "Condominium": "Condo", "Apartment": "Condo",
        "House and Lot": "Houses", "Single Detached": "Houses", "Townhouse": "Houses",
        "Vacant Lot": "Lot",
    }
    valid = abt["latitude"].notna() & abt["longitude"].notna()
    sub = abt[valid]
    coord_arr = sub[["latitude", "longitude"]].to_numpy(float)
    price_arr = pd.to_numeric(sub["price_php"], errors="coerce").to_numpy()
    stratum_arr = sub["property_type"].map(STRATUM_MAP).to_numpy()
    tree = cKDTree(coord_arr)
    radius_deg = SPATIAL_LAG_RADIUS_M * max(LAT_DEG_PER_M, LON_DEG_PER_M) * 1.02

    lag = np.full(len(sub), np.nan)
    positions = sub.index.to_numpy()
    for i in range(len(sub)):
        lat, lon = coord_arr[i]
        neigh = tree.query_ball_point([lat, lon], r=radius_deg)
        vals = [
            price_arr[j] for j in neigh
            if j != i and not np.isnan(price_arr[j])
            and stratum_arr[j] == stratum_arr[i]                      # same-stratum only
            and haversine_m(lat, lon, coord_arr[j][0], coord_arr[j][1]) <= SPATIAL_LAG_RADIUS_M
        ]
        if vals:
            lag[i] = round(float(np.nanmean(vals)))
    abt.loc[positions, "spatial_lag_price"] = lag
    print(f"  spatial_lag_price recomputed (same-stratum) for {len(sub)} rows "
          f"({np.isnan(lag).sum()} with no same-stratum neighbour).")

    abt.to_csv(ABT_PATH, index=False)
    print(f"Saved. CBD fill now: {abt[cbd_cols[0]].notna().sum()}/{len(abt)}; "
          f"airport {abt['dist_airport_m'].notna().sum()}/{len(abt)}; "
          f"spatial_lag {abt['spatial_lag_price'].notna().sum()}/{len(abt)}")


if __name__ == "__main__":
    main()
