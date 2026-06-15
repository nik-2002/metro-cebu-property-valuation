"""Export the cached Metro Cebu road network and transport midpoints as GeoJSON."""

from __future__ import annotations

import pickle
from pathlib import Path

import geopandas as gpd
import osmnx as ox
import pandas as pd


def export_geojson(layer: gpd.GeoDataFrame, output_path: Path, label: str, count_label: str) -> None:
    layer = layer.set_crs("EPSG:4326", allow_override=True) if layer.crs is None else layer
    layer.to_file(output_path, driver="GeoJSON")
    print(f"{label}: crs={layer.crs} {count_label}={len(layer)} path={output_path}")


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    processed_dir = base_dir / "Data" / "processed"
    graph_path = processed_dir / "metro_cebu_network.pkl"
    transport_csv_path = base_dir / "Data" / "amenities" / "transport.csv"

    qgis_data_dir = base_dir / "QGIS" / "data"
    qgis_data_dir.mkdir(parents=True, exist_ok=True)
    roads_output_path = qgis_data_dir / "metro_cebu_roads.geojson"
    nodes_output_path = qgis_data_dir / "metro_cebu_nodes.geojson"
    transport_output_path = qgis_data_dir / "transport_midpoints.geojson"

    if not graph_path.exists():
        raise FileNotFoundError(f"Cached graph not found: {graph_path}")
    if not transport_csv_path.exists():
        raise FileNotFoundError(f"Transport CSV not found: {transport_csv_path}")

    with graph_path.open("rb") as file_obj:
        graph = pickle.load(file_obj)

    nodes_gdf, edges_gdf = ox.graph_to_gdfs(graph)
    export_geojson(edges_gdf, roads_output_path, "metro_cebu_roads.geojson", "edges")
    export_geojson(nodes_gdf, nodes_output_path, "metro_cebu_nodes.geojson", "rows")

    transport_df = pd.read_csv(transport_csv_path)
    transport_gdf = gpd.GeoDataFrame(
        transport_df.copy(),
        geometry=gpd.points_from_xy(transport_df["lon"], transport_df["lat"]),
        crs="EPSG:4326",
    )
    export_geojson(transport_gdf, transport_output_path, "transport_midpoints.geojson", "rows")


if __name__ == "__main__":
    main()
