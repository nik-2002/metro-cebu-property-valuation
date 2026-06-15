"""Export MCRAI amenity CSVs to GeoJSON point layers for QGIS."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


CATEGORIES = {
    "education": "education.geojson",
    "health": "health.geojson",
    "finance": "finance.geojson",
    "grocery": "grocery.geojson",
    "transport": "transport.geojson",
    "security": "security.geojson",
    "tourism": "tourism.geojson",
    "recreation": "recreation.geojson",
    "retail_density": "retail_density.geojson",
}


def dataframe_to_feature_collection(df: pd.DataFrame) -> dict:
    property_columns = [column for column in df.columns if column not in {"lat", "lon"}]
    features = []

    for row in df.itertuples(index=False):
        row_data = row._asdict()
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row_data["lon"], row_data["lat"]],
            },
            "properties": {column: row_data[column] for column in property_columns},
        }
        features.append(feature)

    return {"type": "FeatureCollection", "features": features}


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    thesis_dir = script_dir.parent
    amenities_dir = thesis_dir / "Data" / "amenities"
    output_dir = thesis_dir / "QGIS"
    output_dir.mkdir(parents=True, exist_ok=True)

    files_written = 0

    for category, output_name in CATEGORIES.items():
        csv_path = amenities_dir / f"{category}.csv"
        output_path = output_dir / output_name

        df = pd.read_csv(csv_path)
        df = df.dropna(subset=["lat", "lon"]).copy()

        feature_collection = dataframe_to_feature_collection(df)
        output_path.write_text(json.dumps(feature_collection, ensure_ascii=False, indent=2))

        files_written += 1
        print(f"  \u2713 {output_name} \u2014 {len(feature_collection['features'])} features")

    print(f"Total files written: {files_written}")


if __name__ == "__main__":
    main()
