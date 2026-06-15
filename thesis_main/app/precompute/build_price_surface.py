"""Precompute the per-sqm price surface grids for each property archetype.

Uses the stratified models (Decision 34): predictions are log(price_per_sqm),
back-transformed to price_per_sqm. One batched model.predict per archetype.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

# Allow running outside a Streamlit runtime: stub the cache decorators.
if "streamlit" not in sys.modules:
    st_stub = types.ModuleType("streamlit")
    st_stub.cache_resource = lambda f=None, **k: (f if f else (lambda g: g))
    st_stub.cache_data = lambda f=None, **k: (f if f else (lambda g: g))
    sys.modules["streamlit"] = st_stub

from lib.config import ABT_PATH, BIR_ZONAL_RR_DEFAULTS, STRATUM_MAP  # noqa: E402
from lib.features import build_feature_vector  # noqa: E402
from lib.predict import get_model  # noqa: E402

LAT_MIN, LAT_MAX = 10.20, 10.45
LON_MIN, LON_MAX = 123.75, 124.07
STEP = 0.003
DATA_DIR = APP_DIR / "data"
BOUNDARY_PATH = DATA_DIR / "lgu_boundaries.geojson"

EARTH_RADIUS_M = 6_371_000.0
# Beyond this distance from the nearest same-stratum listing, the feature lookup
# falls back toward global medians (mcrai_lookup.FALLBACK_DISTANCE_M), so the
# prediction is an extrapolation rather than grounded in nearby sales.
CONFIDENCE_RADIUS_M = 5_000.0

ARCHETYPES = {
    "sdh":    {"property_type": "Single Detached", "area_sqm": 150.0, "output": DATA_DIR / "grid_sdh.parquet"},
    "condo":  {"property_type": "Condominium",     "area_sqm": 60.0,  "output": DATA_DIR / "grid_condo.parquet"},
    "vacant": {"property_type": "Vacant Lot",      "area_sqm": 200.0, "output": DATA_DIR / "grid_vacant.parquet"},
}

def generate_grid():
    """Regular lat/lon lattice clipped to the six LGU polygons.

    The full rectangle spills ~50% of its cells into the Camotes Sea, the Mactan
    Channel, and out-of-scope uplands. We keep only points that fall *within* a
    real LGU boundary and label each surviving cell with the LGU it sits in — a
    point-in-polygon test, not a nearest-centroid guess, so border cells get the
    correct city dummy and BIR default. Mactan stays (inside the Lapu-Lapu polygon).
    """
    lats = np.arange(LAT_MIN, LAT_MAX + STEP / 2, STEP)
    lons = np.arange(LON_MIN, LON_MAX + STEP / 2, STEP)
    grid = pd.MultiIndex.from_product([lats, lons], names=["lat", "lon"]).to_frame(index=False)

    lgus = gpd.read_file(BOUNDARY_PATH)[["lgu", "geometry"]]
    pts = gpd.GeoDataFrame(
        grid, geometry=gpd.points_from_xy(grid["lon"], grid["lat"]), crs="EPSG:4326"
    )
    joined = gpd.sjoin(pts, lgus, how="inner", predicate="within")
    # A cell on a shared border can match two polygons; keep the first match.
    joined = joined.drop_duplicates(subset=["lat", "lon"])
    out = (
        joined[["lat", "lon", "lgu"]]
        .rename(columns={"lgu": "city"})
        .sort_values(["lat", "lon"])
        .reset_index(drop=True)
    )
    return out


def stratum_listing_tree(stratum_key):
    """BallTree over the coordinates of training listings in this stratum.

    Used to measure how far each grid cell sits from the nearest real sale of the
    same property family — the basis for the per-cell confidence flag.
    """
    types_in = [t for t, s in STRATUM_MAP.items() if s == stratum_key]
    abt = pd.read_csv(ABT_PATH, usecols=["latitude", "longitude", "property_type"])
    sub = abt[abt["property_type"].isin(types_in)].dropna(subset=["latitude", "longitude"])
    coords_rad = np.radians(sub[["latitude", "longitude"]].to_numpy())
    return BallTree(coords_rad, metric="haversine")


def attach_confidence(out, stratum_key):
    """Add dist_to_listing_m and low_confidence to a built surface."""
    tree = stratum_listing_tree(stratum_key)
    dist_rad, _ = tree.query(np.radians(out[["lat", "lon"]].to_numpy()), k=1)
    out["dist_to_listing_m"] = (dist_rad[:, 0] * EARTH_RADIUS_M).astype(float)
    out["low_confidence"] = out["dist_to_listing_m"] > CONFIDENCE_RADIUS_M
    return out


def build_surface(key, grid_df):
    cfg = ARCHETYPES[key]
    print(f"\n[{key}] building {len(grid_df):,} feature rows...")
    rows, feats, stratum_key = [], [], None
    for i, r in enumerate(grid_df.itertuples(index=False), 1):
        lat, lon, city = float(r.lat), float(r.lon), r.city
        fdf, stratum_key = build_feature_vector({
            "city": city, "property_type": cfg["property_type"],
            "lat": lat, "lon": lon, "area_sqm": cfg["area_sqm"],
            "bedrooms": None, "bathrooms": None,
            "bir_zonal_rr_median": BIR_ZONAL_RR_DEFAULTS[city],
        })
        feats.append(fdf)
        rows.append({"lat": lat, "lon": lon, "city": city})
        if i % 1000 == 0:
            print(f"[{key}] {i:,}/{len(grid_df):,}")

    X = pd.concat(feats, ignore_index=True)
    model = get_model(stratum_key)
    price_per_sqm = np.exp(model.predict(X))
    out = pd.DataFrame(rows)
    out["price_per_sqm"] = price_per_sqm.astype(float)
    out = attach_confidence(out, stratum_key)
    return out


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    grid_df = generate_grid()
    print(f"Grid: {len(grid_df):,} points")
    for key in ARCHETYPES:
        surface = build_surface(key, grid_df)
        surface.to_parquet(ARCHETYPES[key]["output"], index=False)
        low_pct = 100.0 * surface["low_confidence"].mean()
        print(f"[{key}] price_per_sqm min={surface.price_per_sqm.min():,.0f} "
              f"max={surface.price_per_sqm.max():,.0f} mean={surface.price_per_sqm.mean():,.0f}")
        print(f"[{key}] low_confidence cells (>5km from a listing): {low_pct:.1f}%")
        print(f"[{key}] wrote {ARCHETYPES[key]['output']}")


if __name__ == "__main__":
    main()
