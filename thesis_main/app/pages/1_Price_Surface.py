from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

from lib.navbar import render_navbar

st.set_page_config(
    page_title="Price Surface — Metro Cebu Estimator",
    page_icon="🗺️",
    layout="wide",
)
render_navbar(active="Price Surface")

APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"
FILE_MAP = {
    "Single Detached (150 sqm lot)": "grid_sdh.parquet",
    "Condominium (60 sqm lot)": "grid_condo.parquet",
    "Vacant Lot (200 sqm lot)": "grid_vacant.parquet",
}

LOW_COLOR  = np.array([68,   1,  84], dtype=float)   # viridis purple
MID_COLOR  = np.array([33, 145, 140], dtype=float)   # viridis teal
HIGH_COLOR = np.array([253, 231,  37], dtype=float)  # viridis yellow
GREY_COLOR = [120, 120, 120, 255]                    # low-confidence (extrapolated)


@st.cache_data
def load_lgu_mask() -> object:
    """Return a single Shapely geometry covering all 6 Metro Cebu LGUs."""
    gdf = gpd.read_file(str(DATA_DIR / "lgu_boundaries.geojson"))
    return gdf.union_all()


def _ramp_color(value: float) -> list:
    if value <= 0.5:
        rgb = LOW_COLOR + (MID_COLOR - LOW_COLOR) * (value / 0.5)
    else:
        rgb = MID_COLOR + (HIGH_COLOR - MID_COLOR) * ((value - 0.5) / 0.5)
    return [int(rgb[0]), int(rgb[1]), int(rgb[2]), 255]


@st.cache_data
def load_surface(path_str: str) -> pd.DataFrame:
    df = pd.read_parquet(path_str)

    # ── Clip to LGU boundaries ──────────────────────────────────────────────
    mask = load_lgu_mask()
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["lon"], df["lat"]),
        crs="EPSG:4326",
    )
    df = gdf[gdf.within(mask)].drop(columns="geometry").copy()

    # Older parquets may predate the confidence columns; treat them as confident.
    if "low_confidence" not in df.columns:
        df["low_confidence"] = False
    if "dist_to_listing_m" not in df.columns:
        df["dist_to_listing_m"] = 0.0

    # ── Viridis ramp, scaled on CONFIDENT cells only ────────────────────────
    # Low-confidence cells lean on fallback medians; including them would distort
    # the colour scale, so the ramp is fit to the grounded cells and the rest are
    # painted a flat grey.
    confident = df[~df["low_confidence"]]
    price_basis = confident["price_per_sqm"] if len(confident) else df["price_per_sqm"]
    min_price, max_price = float(price_basis.min()), float(price_basis.max())
    span = max_price - min_price

    def _color(row):
        if row["low_confidence"]:
            return GREY_COLOR
        norm = 0.0 if span == 0 else (row["price_per_sqm"] - min_price) / span
        return _ramp_color(float(np.clip(norm, 0.0, 1.0)))

    df["color"] = df.apply(_color, axis=1)
    df["price_label"] = df["price_per_sqm"].map(lambda v: f"PHP {v:,.0f}")
    df["confidence_label"] = np.where(
        df["low_confidence"],
        df["dist_to_listing_m"].map(lambda d: f"Low confidence · {d/1000:.1f} km from nearest listing"),
        "Grounded in nearby listings",
    )
    return df


st.title("Metro Cebu Price Surface")
st.write(
    "Predicted open-market residential price per sqm across Metro Cebu. "
    "Select a property archetype to update the surface."
)

col_a, col_b = st.columns([3, 2])
with col_a:
    archetype = st.radio(
        "Property archetype",
        list(FILE_MAP.keys()),
        horizontal=True,
    )
with col_b:
    hide_low_conf = st.toggle(
        "Hide low-confidence areas",
        value=False,
        help="Cells more than 5 km from any real listing are extrapolations. "
             "Shown in grey by default; toggle on to drop them entirely.",
    )

surface_df = load_surface(str(DATA_DIR / FILE_MAP[archetype]))

low_share = float(surface_df["low_confidence"].mean())
if low_share > 0:
    st.caption(
        f"⚠️ {low_share:.0%} of this surface is **low confidence** — grey cells sit "
        f"more than 5 km from any {archetype.split(' (')[0].lower()} listing, so their "
        f"price is extrapolated, not grounded in nearby sales (mostly upland barangays)."
    )

if hide_low_conf:
    surface_df = surface_df[~surface_df["low_confidence"]].copy()

surface_records = surface_df.to_dict("records")

layers = [
    pdk.Layer(
        "ScatterplotLayer",
        data=surface_records,
        get_position="[lon, lat]",
        get_fill_color="color",
        get_radius=300,
        pickable=True,
    )
]

tooltip = {
    "html": "<b>{city}</b><br/>{price_label}<br/><i>{confidence_label}</i>",
    "style": {"color": "white"},
}

last_point = st.session_state.get("last_point")
if last_point is not None:
    last_point_records = [
        {
            "lon": float(last_point["lon"]),
            "lat": float(last_point["lat"]),
            "label": "Your property",
            "city": last_point.get("city", ""),
            "price_label": last_point.get("price_label", ""),
        }
    ]
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=last_point_records,
            get_position="[lon, lat]",
            get_fill_color=[220, 38, 38, 255],
            get_radius=400,
            pickable=True,
        )
    )
    tooltip = {
        "html": "<b>{label}</b><br/>{city}<br/>{price_label}",
        "style": {"color": "white"},
    }

view_state = pdk.ViewState(latitude=10.32, longitude=123.90, zoom=11, pitch=0)

deck = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    map_provider="carto",
    map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    tooltip=tooltip,
)

st.pydeck_chart(deck, width="stretch")
st.caption(
    "Grid spacing: ~330m. Each point is a predicted price for the selected archetype at that location, "
    "clipped to the six Metro Cebu LGUs. **Grey cells are low confidence** — more than 5 km from any "
    "real listing, so their price is extrapolated. Coloured (viridis) cells are grounded in nearby sales. "
    "Actual prices vary by specific property characteristics."
)
