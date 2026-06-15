"""Export ABT property points to GeoJSON for QGIS."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def dataframe_to_feature_collection(df: pd.DataFrame) -> dict:
    property_columns = [column for column in df.columns if column not in {"latitude", "longitude"}]
    features = []

    for row in df.itertuples(index=False):
        row_data = row._asdict()
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [row_data["longitude"], row_data["latitude"]],
                },
                "properties": {column: row_data[column] for column in property_columns},
            }
        )

    return {"type": "FeatureCollection", "features": features}


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    thesis_dir = script_dir.parent
    abt_path = thesis_dir / "Data" / "processed" / "abt_clean.csv"
    output_dir = thesis_dir / "QGIS" / "data"
    output_path = output_dir / "abt_clean.geojson"

    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(abt_path)
    df = df.dropna(subset=["latitude", "longitude"]).copy()

    feature_collection = dataframe_to_feature_collection(df)
    output_path.write_text(json.dumps(feature_collection, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"  \u2713 {output_path.name} \u2014 {len(feature_collection['features'])} features")


if __name__ == "__main__":
    main()
