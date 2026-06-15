"""
export_mcrai_pois_for_qgis.py

Exports each MCRAI amenity category as a GeoJSON point layer for QGIS visualization.
Reads CSVs from thesis_main/Data/amenities/ and writes to thesis_main/QGIS/data/mcrai_pois/.
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path

AMENITIES_DIR = Path(__file__).resolve().parents[1] / "Data" / "amenities"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "QGIS" / "data" / "mcrai_pois"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CATEGORIES = [
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

for category in CATEGORIES:
    csv_path = AMENITIES_DIR / f"{category}.csv"
    out_path = OUTPUT_DIR / f"mcrai_{category}_pois.geojson"

    df = pd.read_csv(csv_path)
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["lon"], df["lat"]),
        crs="EPSG:4326",
    )
    gdf.to_file(out_path, driver="GeoJSON")
    print(f"{category}: {len(gdf)} rows -> {out_path}")
