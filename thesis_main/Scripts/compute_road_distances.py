"""Compute road-network distances to trunk and primary corridors."""

import sys
import math
import os
import tempfile
import numpy as np
import pandas as pd
import networkx as nx
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from network_utils import load_metro_cebu_graph
import osmnx as ox

TRUNK_HIGHWAYS = {"trunk", "trunk_link"}
PRIMARY_HIGHWAYS = {"primary", "primary_link"}


def haversine_m(lat1, lon1, lat2, lon2):
    radius_m = 6_371_000
    rlat1, rlon1, rlat2, rlon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    return 2 * radius_m * math.asin(math.sqrt(a))


def as_highway_values(highway_attr):
    if highway_attr is None:
        return set()
    if isinstance(highway_attr, str):
        return {highway_attr}
    if isinstance(highway_attr, (list, tuple, set)):
        values = set()
        for item in highway_attr:
            values.update(as_highway_values(item))
        return values
    return {str(highway_attr)}


def ensure_undirected_graph(G):
    if not nx.is_directed(G):
        return G
    if hasattr(ox, "utils_graph") and hasattr(ox.utils_graph, "get_undirected"):
        return ox.utils_graph.get_undirected(G)
    if hasattr(ox, "convert") and hasattr(ox.convert, "to_undirected"):
        return ox.convert.to_undirected(G)
    return nx.MultiGraph(G) if G.is_multigraph() else nx.Graph(G)


def collect_road_nodes(G, target_highways):
    node_ids = set()
    edge_count = 0

    if G.is_multigraph():
        for u, v, _key, data in G.edges(data=True, keys=True):
            if as_highway_values(data.get("highway")) & target_highways:
                edge_count += 1
                node_ids.update((u, v))
    else:
        for u, v, data in G.edges(data=True):
            if as_highway_values(data.get("highway")) & target_highways:
                edge_count += 1
                node_ids.update((u, v))

    return node_ids, edge_count


def prepare_node_coords(G, node_ids):
    ordered_nodes = list(node_ids)
    lats = np.array([G.nodes[node_id]["y"] for node_id in ordered_nodes], dtype=float)
    lons = np.array([G.nodes[node_id]["x"] for node_id in ordered_nodes], dtype=float)
    return lats, lons


def nearest_haversine_distance(lat, lon, target_lats, target_lons):
    if len(target_lats) == 0:
        return np.nan

    target_rlats = np.radians(target_lats)
    target_rlons = np.radians(target_lons)
    rlat = math.radians(lat)
    rlon = math.radians(lon)
    dlat = target_rlats - rlat
    dlon = target_rlons - rlon
    a = np.sin(dlat / 2) ** 2 + np.cos(rlat) * np.cos(target_rlats) * np.sin(dlon / 2) ** 2
    distances = 2 * 6_371_000 * np.arcsin(np.sqrt(a))
    return float(np.min(distances))


def build_distance_series(valid_index, orig_nodes, source_lats, source_lons, length_map, target_lats, target_lons):
    values = pd.Series(np.nan, index=valid_index, dtype=float)
    fallback_count = 0

    for df_idx, orig_node, lat, lon in zip(valid_index, orig_nodes, source_lats, source_lons):
        distance_m = length_map.get(orig_node)
        if distance_m is None:
            distance_m = nearest_haversine_distance(lat, lon, target_lats, target_lons)
            fallback_count += 1
        values.loc[df_idx] = distance_m

    return values, fallback_count


def snap_nearest_nodes(G, lons, lats):
    try:
        return ox.distance.nearest_nodes(G, X=lons.tolist(), Y=lats.tolist())
    except Exception as exc:
        if "no database context specified" not in str(exc).lower() or not hasattr(ox, "projection"):
            raise
        original_is_projected = ox.projection.is_projected
        try:
            ox.projection.is_projected = lambda _crs: False
            return ox.distance.nearest_nodes(G, X=lons.tolist(), Y=lats.tolist())
        finally:
            ox.projection.is_projected = original_is_projected


def atomic_write_csv(df, target_path):
    fd, tmp_path = tempfile.mkstemp(
        dir=str(target_path.parent),
        prefix=f"{target_path.stem}.",
        suffix=".tmp",
    )
    os.close(fd)
    try:
        df.to_csv(tmp_path, index=False)
        os.replace(tmp_path, target_path)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def print_summary(label, series):
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    print(
        f"{label} summary: min={numeric.min():.0f}  median={numeric.median():.0f}  "
        f"max={numeric.max():.0f}  mean={numeric.mean():.2f}"
    )


def main():
    base_dir = Path(__file__).resolve().parents[1]
    abt_path = base_dir / "Data" / "processed" / "abt_clean.csv"

    print(f"Loading ABT from {abt_path}")
    abt = pd.read_csv(abt_path)
    print(f"ABT shape before: {abt.shape}")
    print(f"ABT column count before: {len(abt.columns)}")

    if "latitude" not in abt.columns or "longitude" not in abt.columns:
        raise ValueError("ABT must have latitude and longitude columns")

    print("\nLoading Metro Cebu road network...")
    G = load_metro_cebu_graph()
    G = ensure_undirected_graph(G)

    trunk_nodes, trunk_edge_count = collect_road_nodes(G, TRUNK_HIGHWAYS)
    primary_nodes, primary_edge_count = collect_road_nodes(G, PRIMARY_HIGHWAYS)
    if not trunk_nodes:
        raise ValueError("No trunk nodes found in the graph")
    if not primary_nodes:
        raise ValueError("No primary nodes found in the graph")

    print(f"Trunk edges in graph: {trunk_edge_count}")
    print(f"Primary edges in graph: {primary_edge_count}")
    print(f"Trunk nodes in graph: {len(trunk_nodes)}")
    print(f"Primary nodes in graph: {len(primary_nodes)}")

    valid_mask = abt["latitude"].notna() & abt["longitude"].notna()
    valid_index = abt.index[valid_mask]
    valid_lats = abt.loc[valid_mask, "latitude"].to_numpy(dtype=float)
    valid_lons = abt.loc[valid_mask, "longitude"].to_numpy(dtype=float)

    print(f"\nSnapping {valid_mask.sum()} properties to the road graph...")
    orig_nodes = snap_nearest_nodes(G, valid_lons, valid_lats)

    print("Computing multi-source Dijkstra distances...")
    trunk_length_map = nx.multi_source_dijkstra_path_length(G, sources=trunk_nodes, weight="length")
    primary_length_map = nx.multi_source_dijkstra_path_length(G, sources=primary_nodes, weight="length")

    trunk_lats, trunk_lons = prepare_node_coords(G, trunk_nodes)
    primary_lats, primary_lons = prepare_node_coords(G, primary_nodes)

    trunk_series, trunk_fallbacks = build_distance_series(
        valid_index,
        orig_nodes,
        valid_lats,
        valid_lons,
        trunk_length_map,
        trunk_lats,
        trunk_lons,
    )
    primary_series, primary_fallbacks = build_distance_series(
        valid_index,
        orig_nodes,
        valid_lats,
        valid_lons,
        primary_length_map,
        primary_lats,
        primary_lons,
    )

    abt["dist_to_trunk_road_m"] = trunk_series.reindex(abt.index).round().astype("Int64")
    abt["dist_to_primary_road_m"] = primary_series.reindex(abt.index).round().astype("Int64")

    print_summary("dist_to_trunk_road_m", abt["dist_to_trunk_road_m"])
    print_summary("dist_to_primary_road_m", abt["dist_to_primary_road_m"])

    total_fallbacks = trunk_fallbacks + primary_fallbacks
    print(
        "Number of Haversine fallbacks: "
        f"trunk={trunk_fallbacks}, primary={primary_fallbacks}, total={total_fallbacks}"
    )
    if total_fallbacks > 0:
        print(f"WARNING: {total_fallbacks} properties required Haversine fallback distances")

    print(f"\nABT shape after: {abt.shape}")
    print(f"ABT column count after: {len(abt.columns)}")

    print(f"\nSaving ABT to {abt_path}")
    atomic_write_csv(abt, abt_path)
    print("Done.")


if __name__ == "__main__":
    main()
