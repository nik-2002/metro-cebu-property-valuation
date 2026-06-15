from __future__ import annotations

import copy
import json
from pathlib import Path

import numpy as np
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
SURFACE_MAP = {
    "Single Detached": {
        "file": "barangay_surface_sdh.geojson",
        "subtitle": "150 sqm lot archetype",
    },
    "Condominium": {
        "file": "barangay_surface_condo.geojson",
        "subtitle": "60 sqm unit archetype",
    },
    "Vacant Lot": {
        "file": "barangay_surface_vacant.geojson",
        "subtitle": "200 sqm lot archetype",
    },
}

PALETTE = [
    [239, 243, 255, 225],
    [198, 219, 239, 225],
    [158, 202, 225, 225],
    [107, 174, 214, 225],
    [33, 113, 181, 225],
]
LOW_CONF_COLOR = [148, 163, 184, 155]
OUTLINE_COLOR = [255, 255, 255, 210]
LGU_OUTLINE_COLOR = [30, 41, 59, 190]


st.markdown(
    """
    <style>
    .surface-page {
        max-width: 1420px;
        margin: 0 auto;
        padding: 2.25rem 3.2rem 1.8rem;
    }
    .surface-kicker {
        color:#8A94A6;
        font-size:0.72rem;
        font-weight:800;
        letter-spacing:0.12em;
        text-transform:uppercase;
        margin-bottom:0.2rem;
    }
    .surface-title {
        color:#14233B;
        font-size:2.15rem;
        line-height:1.08;
        font-weight:850;
        margin:0 0 0.35rem;
    }
    .surface-sub {
        color:#4B5563;
        max-width:900px;
        font-size:0.95rem;
        margin-bottom:1.2rem;
    }
    .surface-toolbar {
        display:flex;
        align-items:flex-end;
        justify-content:space-between;
        gap:1rem;
        border-top:1px solid #E6EAF0;
        border-bottom:1px solid #E6EAF0;
        padding:0.9rem 0 0.75rem;
        margin-bottom:0.85rem;
    }
    .surface-statline {
        color:#64748B;
        font-size:0.78rem;
        line-height:1.35;
    }
    .legend-row {
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:0.85rem;
        margin:0.3rem 0 0.75rem;
    }
    .legend-items {
        display:flex;
        align-items:center;
        gap:0.4rem;
        flex-wrap:wrap;
    }
    .legend-swatch {
        display:inline-flex;
        align-items:center;
        gap:0.35rem;
        color:#475569;
        font-size:0.72rem;
        white-space:nowrap;
    }
    .legend-chip {
        width:20px;
        height:10px;
        border-radius:2px;
        border:1px solid rgba(15,23,42,0.12);
        display:inline-block;
    }
    .surface-note {
        color:#64748B;
        font-size:0.75rem;
        line-height:1.45;
        margin-top:0.65rem;
    }
    [data-testid="stMainBlockContainer"] {
        padding-top:3.7rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_lgu_boundaries() -> dict:
    return json.loads((DATA_DIR / "lgu_boundaries.geojson").read_text())


@st.cache_data
def load_surface(filename: str) -> dict:
    return json.loads((DATA_DIR / filename).read_text())


def _peso(value: float) -> str:
    return f"PHP {value:,.0f}"


def _class_breaks(features: list[dict]) -> np.ndarray:
    prices = [
        float(feature["properties"]["price_per_sqm"])
        for feature in features
        if not feature["properties"].get("low_confidence")
    ]
    if not prices:
        prices = [float(feature["properties"]["price_per_sqm"]) for feature in features]
    return np.quantile(np.array(prices, dtype=float), [0, 0.2, 0.4, 0.6, 0.8, 1.0])


def _class_index(value: float, breaks: np.ndarray) -> int:
    return int(np.clip(np.searchsorted(breaks[1:], value, side="right"), 0, len(PALETTE) - 1))


def _decorate_surface(surface: dict, hide_low_confidence: bool) -> tuple[dict, dict]:
    decorated = copy.deepcopy(surface)
    all_features = decorated.get("features", [])
    breaks = _class_breaks(all_features)

    features = []
    low_count = 0
    for feature in all_features:
        props = feature["properties"]
        price = float(props["price_per_sqm"])
        low_conf = bool(props.get("low_confidence"))
        if low_conf:
            low_count += 1
            if hide_low_confidence:
                continue
            fill = LOW_CONF_COLOR
            class_label = "Low confidence"
        else:
            idx = _class_index(price, breaks)
            fill = PALETTE[idx]
            class_label = f"{_peso(breaks[idx])}–{_peso(breaks[idx + 1])}"

        props["fill_color"] = fill
        props["line_color"] = OUTLINE_COLOR
        props["class_label"] = class_label
        props["tooltip_html"] = (
            f"<b>{props['barangay']}</b><br/>"
            f"{props['lgu']}<br/>"
            f"<b>{props['price_label']}</b><br/>"
            f"{props['confidence_label']}<br/>"
            f"{int(props['point_count'])} grid cells aggregated"
        )
        features.append(feature)

    decorated["features"] = features
    prices = [float(f["properties"]["price_per_sqm"]) for f in all_features]
    meta = {
        "barangay_count": len(all_features),
        "visible_count": len(features),
        "low_count": low_count,
        "low_share": low_count / max(len(all_features), 1),
        "median_price": float(np.median(prices)) if prices else 0.0,
        "breaks": breaks,
    }
    return decorated, meta


def _legend_html(breaks: np.ndarray, show_low_confidence: bool) -> str:
    items = []
    for idx, color in enumerate(PALETTE):
        label = f"{_peso(breaks[idx])}–{_peso(breaks[idx + 1])}"
        rgba = f"rgba({color[0]},{color[1]},{color[2]},{color[3] / 255:.2f})"
        items.append(
            f'<span class="legend-swatch"><span class="legend-chip" '
            f'style="background:{rgba};"></span>{label}</span>'
        )
    if show_low_confidence:
        color = LOW_CONF_COLOR
        rgba = f"rgba({color[0]},{color[1]},{color[2]},{color[3] / 255:.2f})"
        items.append(
            f'<span class="legend-swatch"><span class="legend-chip" '
            f'style="background:{rgba};"></span>Low confidence</span>'
        )
    return '<div class="legend-items">' + "".join(items) + "</div>"


st.markdown('<div class="surface-page">', unsafe_allow_html=True)
st.markdown('<div class="surface-kicker">Barangay valuation surface</div>', unsafe_allow_html=True)
st.markdown('<h1 class="surface-title">Metro Cebu Price Surface</h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="surface-sub">Median predicted open-market residential price per sqm, '
    'aggregated to barangay polygons from the model grid. Barangay boundaries use the '
    'Philippines COD-AB Admin 4 layer sourced from NAMRIA/PSA/OCHA via HDX.</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="surface-toolbar">', unsafe_allow_html=True)
col_a, col_b = st.columns([3.2, 1.6])
with col_a:
    archetype = st.radio(
        "Property archetype",
        list(SURFACE_MAP.keys()),
        horizontal=True,
    )
with col_b:
    hide_low_conf = st.toggle(
        "Hide low-confidence barangays",
        value=False,
        help="Low-confidence barangays are dominated by grid cells more than 5 km from a real listing.",
    )
st.markdown("</div>", unsafe_allow_html=True)

surface, meta = _decorate_surface(
    load_surface(SURFACE_MAP[archetype]["file"]),
    hide_low_conf,
)

st.markdown(
    f'<div class="surface-statline">{SURFACE_MAP[archetype]["subtitle"]} · '
    f'{meta["visible_count"]:,} of {meta["barangay_count"]:,} barangays visible · '
    f'median {_peso(meta["median_price"])} /sqm · '
    f'{meta["low_share"]:.0%} low confidence</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="legend-row">'
    + _legend_html(meta["breaks"], not hide_low_conf)
    + "</div>",
    unsafe_allow_html=True,
)

layers = [
    pdk.Layer(
        "GeoJsonLayer",
        data=surface,
        id="barangay-price-surface",
        pickable=True,
        stroked=True,
        filled=True,
        auto_highlight=True,
        get_fill_color="properties.fill_color",
        get_line_color="properties.line_color",
        line_width_min_pixels=1,
    ),
    pdk.Layer(
        "GeoJsonLayer",
        data=load_lgu_boundaries(),
        id="lgu-outline",
        pickable=False,
        stroked=True,
        filled=False,
        get_line_color=LGU_OUTLINE_COLOR,
        line_width_min_pixels=2,
    ),
]

last_point = st.session_state.get("last_point")
if last_point is not None:
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=[{
                "lon": float(last_point["lon"]),
                "lat": float(last_point["lat"]),
                "label": "Your property",
                "city": last_point.get("city", ""),
                "price_label": last_point.get("price_label", ""),
            }],
            get_position="[lon, lat]",
            get_fill_color=[220, 38, 38, 255],
            get_radius=220,
            pickable=True,
        )
    )

deck = pdk.Deck(
    layers=layers,
    initial_view_state=pdk.ViewState(latitude=10.32, longitude=123.90, zoom=10.5, pitch=0),
    map_provider="carto",
    map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    tooltip={
        "html": "{tooltip_html}",
        "style": {
            "backgroundColor": "#14233B",
            "color": "white",
            "fontSize": "12px",
            "padding": "8px",
        },
    },
    height=620,
)

st.pydeck_chart(deck, width="stretch")
st.markdown(
    '<div class="surface-note">Each barangay value is the median of model grid predictions '
    'inside that barangay. Low-confidence barangays are dominated by extrapolated grid cells, '
    'so they should be read as directional estimates rather than local market evidence. '
    'Actual prices vary by property characteristics and exact site conditions.</div>',
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)
