from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio


APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"
DEFAULT_BOUNDARY_ZIP = Path("/private/tmp/phl_admin_boundaries.gdb.zip")
HDX_GDB_URL = (
    "https://data.humdata.org/dataset/caf116df-f984-4deb-85ca-41b349d3f313/"
    "resource/3fa0dbcf-e07d-4506-9821-ba15baa6da07/download/"
    "phl_admin_boundaries.gdb.zip"
)

METRO_CEBU_BBOX = (123.70, 10.17, 124.21, 10.52)
SOURCE_LGU_NAMES = {
    "Cebu City (Capital)": "Cebu City",
    "Consolacion": "Consolacion",
    "Lapu-Lapu City (Opon)": "Lapu-Lapu City",
    "Mandaue City": "Mandaue City",
    "Minglanilla": "Minglanilla",
    "City of Talisay": "Talisay City",
}

SURFACE_FILES = {
    "sdh": "grid_sdh.parquet",
    "condo": "grid_condo.parquet",
    "vacant": "grid_vacant.parquet",
}


def _download_boundary_zip(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(HDX_GDB_URL, headers={"User-Agent": "MetroCebuEstimator/0.1"})
    with urllib.request.urlopen(req, timeout=120) as response, path.open("wb") as fh:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            fh.write(chunk)


def _load_barangays(boundary_zip: Path) -> gpd.GeoDataFrame:
    if not boundary_zip.exists():
        _download_boundary_zip(boundary_zip)

    path = f"/vsizip/{boundary_zip}"
    barangays = pyogrio.read_dataframe(
        path,
        layer="phl_admin4",
        bbox=METRO_CEBU_BBOX,
        columns=["adm4_name", "adm4_pcode", "adm3_name", "area_sqkm", "geometry"],
    )
    barangays = barangays[barangays["adm3_name"].isin(SOURCE_LGU_NAMES)].copy()
    barangays["lgu"] = barangays["adm3_name"].map(SOURCE_LGU_NAMES)
    barangays = barangays.rename(columns={"adm4_name": "barangay"})
    barangays = barangays[["adm4_pcode", "barangay", "lgu", "area_sqkm", "geometry"]]
    barangays = barangays.sort_values(["lgu", "barangay"]).reset_index(drop=True)
    barangays["geometry"] = barangays.geometry.make_valid().simplify(0.00012, preserve_topology=True)
    return barangays


def _surface_points(surface_path: Path) -> gpd.GeoDataFrame:
    surface = pd.read_parquet(surface_path).copy()
    if "low_confidence" not in surface.columns:
        surface["low_confidence"] = False
    if "dist_to_listing_m" not in surface.columns:
        surface["dist_to_listing_m"] = 0.0

    return gpd.GeoDataFrame(
        surface,
        geometry=gpd.points_from_xy(surface["lon"], surface["lat"]),
        crs="EPSG:4326",
    )


def _nearest_fill(
    missing: gpd.GeoDataFrame,
    points: gpd.GeoDataFrame,
    stats: pd.DataFrame,
) -> pd.DataFrame:
    if missing.empty:
        return stats

    centroid_points = missing.copy()
    centroid_points["geometry"] = centroid_points.geometry.representative_point()
    nearest = gpd.sjoin_nearest(
        centroid_points.to_crs(32651),
        points.to_crs(32651),
        how="left",
        distance_col="nearest_grid_m",
    ).to_crs(4326)

    fill = nearest[[
        "adm4_pcode",
        "price_per_sqm",
        "dist_to_listing_m",
        "low_confidence",
        "nearest_grid_m",
    ]].copy()
    fill["price_q25"] = fill["price_per_sqm"]
    fill["price_q75"] = fill["price_per_sqm"]
    fill["point_count"] = 0
    fill["confident_point_count"] = 0
    fill["low_conf_share"] = 1.0
    fill["fallback_nearest"] = True

    fill = fill.set_index("adm4_pcode")[
        [
            "price_per_sqm",
            "price_q25",
            "price_q75",
            "point_count",
            "confident_point_count",
            "low_conf_share",
            "dist_to_listing_m",
            "nearest_grid_m",
            "fallback_nearest",
        ]
    ]
    return pd.concat([stats, fill], axis=0)


def _aggregate_surface(barangays: gpd.GeoDataFrame, surface_path: Path) -> gpd.GeoDataFrame:
    points = _surface_points(surface_path)
    joined = gpd.sjoin(
        points,
        barangays[["adm4_pcode", "geometry"]],
        how="inner",
        predicate="within",
    )
    joined["is_confident"] = ~joined["low_confidence"].astype(bool)

    stats = joined.groupby("adm4_pcode").agg(
        price_per_sqm=("price_per_sqm", "median"),
        price_q25=("price_per_sqm", lambda s: float(s.quantile(0.25))),
        price_q75=("price_per_sqm", lambda s: float(s.quantile(0.75))),
        point_count=("price_per_sqm", "size"),
        confident_point_count=("is_confident", "sum"),
        low_conf_share=("low_confidence", "mean"),
        dist_to_listing_m=("dist_to_listing_m", "median"),
    )
    stats["nearest_grid_m"] = 0.0
    stats["fallback_nearest"] = False

    missing = barangays[~barangays["adm4_pcode"].isin(stats.index)]
    stats = _nearest_fill(missing, points, stats)

    out = barangays.merge(stats.reset_index(), on="adm4_pcode", how="left")
    out = out.dropna(subset=["price_per_sqm"]).copy()
    out["low_confidence"] = (out["low_conf_share"] >= 0.5) | (out["confident_point_count"] <= 0)
    out["price_label"] = out["price_per_sqm"].map(lambda v: f"PHP {v:,.0f} /sqm")
    out["confidence_label"] = np.where(
        out["fallback_nearest"],
        out["nearest_grid_m"].map(lambda d: f"Nearest grid estimate · {d:,.0f} m from barangay interior"),
        np.where(
            out["low_confidence"],
            out["dist_to_listing_m"].map(lambda d: f"Low confidence · median grid cell {d/1000:.1f} km from listing"),
            "Grounded in nearby listings",
        ),
    )
    return out


def _write_geojson(gdf: gpd.GeoDataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    clean = gdf.copy()
    clean["price_per_sqm"] = clean["price_per_sqm"].round(0).astype(int)
    clean["price_q25"] = clean["price_q25"].round(0).astype(int)
    clean["price_q75"] = clean["price_q75"].round(0).astype(int)
    clean["low_conf_share"] = clean["low_conf_share"].round(3)
    clean["dist_to_listing_m"] = clean["dist_to_listing_m"].round(0).astype(int)
    clean["nearest_grid_m"] = clean["nearest_grid_m"].round(0).astype(int)
    clean.to_file(output_path, driver="GeoJSON")


def build(boundary_zip: Path) -> None:
    barangays = _load_barangays(boundary_zip)
    print(f"Loaded {len(barangays)} Metro Cebu barangays")

    for key, filename in SURFACE_FILES.items():
        surface = _aggregate_surface(barangays, DATA_DIR / filename)
        output_path = DATA_DIR / f"barangay_surface_{key}.geojson"
        _write_geojson(surface, output_path)
        low_share = float(surface["low_confidence"].mean()) if len(surface) else 0.0
        print(f"{output_path.name}: {len(surface)} barangays, {low_share:.0%} low confidence")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Metro Cebu barangay-level price surfaces.")
    parser.add_argument("--boundary-zip", type=Path, default=DEFAULT_BOUNDARY_ZIP)
    args = parser.parse_args()
    build(args.boundary_zip)


if __name__ == "__main__":
    main()
