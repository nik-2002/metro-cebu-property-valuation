from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

from lib.config import ABT_PATH, CBD_COORDS, METRO_CEBU_CITIES
from lib.features import build_feature_vector_from_listing, get_stratum
from lib.navbar import render_navbar
from lib.shap_explain import explain, prettify, shap_is_available, top_drivers

st.set_page_config(page_title="Market Map — Metro Cebu Estimator", page_icon="🗺️", layout="wide")
render_navbar(active="Market Map")

PROCESSED_DIR = ABT_PATH.parent
APP_DATA = Path(__file__).resolve().parents[1] / "data"
MCRAI_POI_DIR = ABT_PATH.parents[2] / "QGIS" / "data" / "mcrai_pois"

STRATA_FILES = {
    "Condominium": "abt_condo.csv",
    "Houses": "abt_houses.csv",
    "Vacant Lot": "abt_lot.csv",
}
STRATUM_COLOR = {
    "Condominium": [37, 99, 235],    # blue
    "Houses": [22, 163, 74],         # green
    "Vacant Lot": [217, 119, 6],     # gold
}
POI_CATEGORIES = {
    "Grocery": ("mcrai_grocery_pois.geojson", [217, 119, 6, 255]),
    "Retail": ("mcrai_retail_density_pois.geojson", [219, 39, 119, 255]),
    "Health": ("mcrai_health_pois.geojson", [2, 132, 199, 255]),
    "Hospitals": ("mcrai_hospitals_pois.geojson", [220, 38, 38, 255]),
    "Education": ("mcrai_education_pois.geojson", [79, 70, 229, 255]),
    "Security": ("mcrai_security_pois.geojson", [17, 24, 39, 255]),
    "Recreation": ("mcrai_recreation_pois.geojson", [22, 163, 74, 255]),
    "Tourism": ("mcrai_tourism_pois.geojson", [126, 34, 206, 255]),
}

# Opaque, high-contrast ramp for a light basemap: low = indigo, high = red.
PRICE_STOPS = [
    (0.00, (49, 46, 129)),
    (0.25, (34, 113, 177)),
    (0.50, (21, 156, 128)),
    (0.75, (244, 185, 66)),
    (1.00, (204, 45, 45)),
]
PRICE_GRADIENT_CSS = (
    "linear-gradient(to right, rgb(49,46,129), rgb(34,113,177), "
    "rgb(21,156,128), rgb(244,185,66), rgb(204,45,45))"
)


def _chip_color_css(label: str, color: list[int]) -> str:
    safe_label = label.replace('"', '\\"')
    r, g, b = color[:3]
    return f"""
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-baseweb="tag"][aria-label^="{safe_label},"],
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-baseweb="tag"]:has(> span[title="{safe_label}"]) {{
        background:rgb({r},{g},{b}) !important;
        border-color:rgba({r},{g},{b},0.95) !important;
        color:#FFFFFF !important;
        box-shadow:0 0 0 1px rgba(255,255,255,0.16), 0 1px 2px rgba(0,0,0,0.18) !important;
    }}
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-baseweb="tag"][aria-label^="{safe_label},"] span,
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-baseweb="tag"][aria-label^="{safe_label},"] svg,
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-baseweb="tag"]:has(> span[title="{safe_label}"]) span,
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-baseweb="tag"]:has(> span[title="{safe_label}"]) svg {{
        color:#FFFFFF !important;
        fill:#FFFFFF !important;
    }}
    """


CHIP_COLOR_CSS = "\n".join(
    [_chip_color_css(label, color) for label, color in STRATUM_COLOR.items()]
    + [_chip_color_css(label, color) for label, (_, color) in POI_CATEGORIES.items()]
)

# Columns kept for the map payload (small) + needed to rebuild a feature vector.
DISPLAY_COLS = ["latitude", "longitude", "price_per_sqm", "price_fmt", "city",
                "barangay", "property_type", "stratum", "property_id", "address"]


def price_color(t: float, alpha: int = 255) -> list:
    t = float(np.clip(t, 0.0, 1.0))
    for (t0, c0), (t1, c1) in zip(PRICE_STOPS, PRICE_STOPS[1:]):
        if t <= t1:
            f = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            return [int(c0[j] + (c1[j] - c0[j]) * f) for j in range(3)] + [alpha]
    return list(PRICE_STOPS[-1][1]) + [alpha]


# ── Dashboard styling ───────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    :root {
        --ink:#14233B;
        --muted:#6B7280;
        --line:#E6EAF0;
        --rail:#053B68;
        --rail-deep:#052F55;
        --brand:#F7C80E;
        --accent:#E23E57;
        --blue:#0B4F83;
    }
    .stApp { background:#F4F7FB; }
    .main .block-container,
    [data-testid="stMainBlockContainer"] {
        padding:3.56rem 0 0.1rem !important;
        max-width:100% !important;
        width:100% !important;
        margin:0 !important;
    }
    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
        gap:0 !important;
    }
    [data-testid="stHorizontalBlock"] { gap:0 !important; }
    [data-testid="column"] { padding-left:0 !important; padding-right:0 !important; }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) {
        background:linear-gradient(180deg,var(--rail) 0%,var(--rail-deep) 100%);
        min-height:calc(100vh - 3.56rem);
        padding:0.55rem 0.8rem 0.45rem;
        border-radius:0;
        box-shadow:inset -1px 0 0 rgba(255,255,255,0.08);
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(2) {
        background:#FFFFFF;
        padding:0 0.25rem 0.25rem;
        min-height:calc(100vh - 3.56rem);
        border-left:1px solid #DDE5EE;
        border-right:1px solid #DDE5EE;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(3) {
        background:#FFFFFF;
        padding:0.55rem 0.45rem 0.25rem;
        min-height:calc(100vh - 3.56rem);
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) label,
    [data-testid="stHorizontalBlock"] > div:nth-child(1) .stMarkdown,
    [data-testid="stHorizontalBlock"] > div:nth-child(1) .stCaption,
    [data-testid="stHorizontalBlock"] > div:nth-child(1) p {
        color:rgba(255,255,255,0.80) !important;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-baseweb="select"] > div,
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-baseweb="tag"] {
        background:#1B5A8B !important;
        border-color:#4C8EBA !important;
        color:#FFFFFF !important;
        border-radius:7px !important;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-baseweb="select"] > div {
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.10), 0 1px 0 rgba(0,0,0,0.16);
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-baseweb="select"] input,
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-baseweb="select"] div,
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-baseweb="select"] span {
        color:#FFFFFF !important;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-baseweb="select"] svg {
        fill:#DDEEFF !important;
        color:#DDEEFF !important;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-baseweb="tag"] {
        background:#F7C80E !important;
        border-color:#FFE066 !important;
        color:#083154 !important;
        font-size:0.68rem !important;
        font-weight:750 !important;
        line-height:1.05 !important;
        min-height:22px !important;
        padding:2px 6px !important;
        margin:2px 2px !important;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-baseweb="tag"] span,
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-baseweb="tag"] svg {
        color:#083154 !important;
        fill:#083154 !important;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-baseweb="tag"] svg {
        width:12px !important;
        height:12px !important;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="stSelectbox"],
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="stMultiSelect"] {
        margin-bottom:0.75rem;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) hr {
        border-color:rgba(255,255,255,0.12) !important;
        margin:1rem 0 !important;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="stToggle"] {
        background:#0D4876;
        border:1px solid #286C9D;
        border-radius:8px;
        padding:0.45rem 0.55rem;
        margin-bottom:0.45rem;
        box-shadow:inset 0 1px 0 rgba(255,255,255,0.08);
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="stToggle"] p {
        color:#EAF6FF !important;
        font-weight:650 !important;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) button[aria-label^="Help for"] {
        background:transparent !important;
        border:none !important;
        color:#8CCBFF !important;
        box-shadow:none !important;
        padding:0 !important;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) button[aria-label^="Help for"] svg {
        color:#8CCBFF !important;
        fill:#8CCBFF !important;
        width:15px !important;
        height:15px !important;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) button[aria-label^="Help for"]:hover {
        background:transparent !important;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) button[aria-label^="Help for"]:hover svg {
        color:#F7C80E !important;
        fill:#F7C80E !important;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [role="switch"] {
        background:#8FB2D0 !important;
        border-color:#DCEEFF !important;
        box-shadow:inset 0 0 0 1px rgba(5,59,104,0.12);
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [role="switch"] > div {
        background:#FFFFFF !important;
        box-shadow:0 1px 3px rgba(0,0,0,0.22);
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [role="switch"][aria-checked="true"] {
        background:#F7C80E !important;
        border-color:#FFE58F !important;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(1) [role="switch"][aria-checked="true"] > div {
        background:#FFFFFF !important;
    }
    .rail-note {
        color:rgba(255,255,255,0.54);
        font-size:0.72rem;
        line-height:1.35;
        margin:0.65rem 0 0.85rem;
    }
    .rail-footer {
        color:rgba(255,255,255,0.48);
        font-size:0.72rem;
        border-top:1px solid rgba(255,255,255,0.11);
        margin-top:1rem;
        padding-top:0.85rem;
    }
    .rail-title {
        font-size:0.69rem;
        font-weight:800;
        letter-spacing:0.08em;
        color:rgba(255,255,255,0.62);
        text-transform:uppercase;
        margin:0.7rem 0 0.3rem;
    }
    .rail-title.dark { color:#8A94A6; }
    .map-topbar {
        min-height:66px;
        display:flex;
        align-items:center;
        border-bottom:1px solid var(--line);
        margin:0 -1.05rem 0.85rem 0;
        padding:0 1.35rem;
    }
    .map-title { color:var(--ink); font-size:1.2rem; font-weight:800; line-height:1.18; }
    .soft-btn {
        border-radius:7px;
        background:#EEF2F7;
        color:#29445E;
        padding:0.55rem 0.8rem;
        font-size:0.78rem;
        font-weight:800;
        white-space:nowrap;
    }
    .map-frame {
        border:1px solid #DCE4ED;
        border-radius:0;
        overflow:hidden;
        background:#FFFFFF;
        box-shadow:0 1px 2px rgba(15,23,42,0.04);
    }
    .map-caption-row {
        position:sticky;
        top:3.56rem;
        z-index:5;
        display:flex;
        align-items:flex-start;
        justify-content:space-between;
        gap:1rem;
        background:#FFFFFF;
        border-bottom:1px solid transparent;
        margin:0 -0.25rem 0.55rem;
        padding:0 0.25rem 0.15rem;
    }
    .map-caption-main { min-width:0; }
    .panel-h {
        font-size:1.02rem;
        font-weight:800;
        color:var(--ink);
        margin-bottom:0.1rem;
    }
    .panel-sub {
        font-size:0.74rem;
        color:#8791A0;
        margin-bottom:0.75rem;
    }
    .panel-head-flex {
        display:flex;
        align-items:flex-start;
        justify-content:space-between;
        gap:0.75rem;
    }
    .metric-grid {
        display:grid;
        grid-template-columns:1fr 1fr;
        gap:0.65rem;
        margin:0.65rem 0 1rem;
    }
    .stat-card {
        background:#FBFCFE;
        border:1px solid #EEF2F7;
        border-radius:8px;
        padding:0.8rem;
        min-height:82px;
        box-shadow:0 1px 4px rgba(15,23,42,0.04);
    }
    .stat-card.warm { background:#FFF7F0; }
    .stat-card.cool { background:#F0F7FF; }
    .stat-num { font-size:1.25rem; font-weight:850; color:#D43D4D; line-height:1.1; }
    .stat-card.cool .stat-num { color:#2563EB; }
    .stat-lbl { font-size:0.69rem; color:#6B7280; margin-top:0.25rem; }
    .composition-card,
    .ranking-card,
    .driver-card {
        border-top:1px solid #EEF2F7;
        padding-top:0.85rem;
        margin-top:0.85rem;
    }
    .rank-row { display:flex; align-items:center; justify-content:space-between;
                font-size:0.78rem; padding:4px 0 2px; gap:0.6rem; }
    .rank-row span:first-child { color:#334155; font-weight:700; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .rank-bar-track { height:5px; border-radius:99px; background:#EEF2F7; overflow:hidden; margin-bottom:0.42rem; }
    .rank-bar { height:5px; border-radius:99px; background:#E23E57; }
    .sel-card {
        background:#FFF7ED;
        border:1px solid #FED7AA;
        border-radius:8px;
        padding:0.85rem;
        margin-bottom:0.75rem;
    }
    .sel-addr { font-size:0.78rem; color:#445065; line-height:1.3; }
    .sel-price { font-size:1.25rem; font-weight:850; color:#172033; }
    .drv-row { font-size:0.8rem; margin:5px 0; }
    .drv-top { display:flex; justify-content:space-between; }
    .legend-dot {
        display:inline-block;
        width:11px;
        height:11px;
        border-radius:999px;
        margin-right:7px;
        border:2px solid #FFFFFF;
        box-shadow:0 0 0 1px rgba(15,23,42,0.18);
        vertical-align:-1px;
    }
    .map-legend {
        display:flex;
        flex-wrap:wrap;
        gap:0.85rem 1.25rem;
        align-items:flex-start;
        padding:0.72rem 0 0;
        margin-top:0.2rem;
        border-top:1px solid #E6EAF0;
    }
    .map-legend.map-legend-top {
        flex:0 0 auto;
        padding:0;
        margin:0;
        border-top:0;
        justify-content:flex-end;
    }
    .map-legend-top .map-legend-group {
        justify-content:flex-end;
    }
    .map-legend-top .map-legend-title {
        text-align:right;
    }
    .map-legend-group {
        display:flex;
        flex-wrap:wrap;
        align-items:center;
        gap:0.45rem 0.8rem;
    }
    .map-legend-title {
        width:100%;
        color:#8A94A6;
        font-size:0.68rem;
        font-weight:850;
        letter-spacing:0.08em;
        text-transform:uppercase;
    }
    .map-legend-item {
        color:#334155;
        font-size:0.75rem;
        font-weight:650;
        white-space:nowrap;
    }
    .price-ramp {
        width:220px;
        height:11px;
        border-radius:999px;
        box-shadow:0 0 0 1px rgba(15,23,42,0.12);
    }
    .price-ramp-labels {
        display:flex;
        justify-content:space-between;
        color:#64748B;
        font-size:0.68rem;
        width:220px;
        margin-top:0.2rem;
    }
    @media (max-width: 1100px) {
        .map-topbar { align-items:start; padding:0.9rem 1rem; }
        [data-testid="stHorizontalBlock"] > div:nth-child(1),
        [data-testid="stHorizontalBlock"] > div:nth-child(2),
        [data-testid="stHorizontalBlock"] > div:nth-child(3) {
            min-height:auto;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(f"<style>{CHIP_COLOR_CSS}</style>", unsafe_allow_html=True)


@st.cache_data
def load_listings() -> pd.DataFrame:
    frames = []
    for label, fname in STRATA_FILES.items():
        df = pd.read_csv(PROCESSED_DIR / fname)
        df = df.dropna(subset=["latitude", "longitude", "price_per_sqm"]).copy()
        df["stratum"] = label
        frames.append(df)
    listings_df = pd.concat(frames, ignore_index=True)
    if ABT_PATH.exists():
        barangay = pd.read_csv(ABT_PATH, usecols=["property_id", "barangay_geocoded"])
        barangay = barangay.dropna(subset=["barangay_geocoded"]).drop_duplicates("property_id")
        barangay = barangay.rename(columns={"barangay_geocoded": "barangay"})
        listings_df = listings_df.merge(barangay, on="property_id", how="left")
    else:
        listings_df["barangay"] = np.nan
    return listings_df


@st.cache_data
def load_lgu_geojson() -> dict:
    path = APP_DATA / "lgu_boundaries.geojson"
    return json.loads(path.read_text()) if path.exists() else {"type": "FeatureCollection", "features": []}


@st.cache_data
def load_pois() -> pd.DataFrame:
    records = []
    for label, (fname, color) in POI_CATEGORIES.items():
        path = MCRAI_POI_DIR / fname
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        for feature in data.get("features", []):
            geom = feature.get("geometry") or {}
            coords = geom.get("coordinates") or []
            if geom.get("type") != "Point" or len(coords) < 2:
                continue
            props = feature.get("properties") or {}
            records.append({
                "longitude": float(coords[0]),
                "latitude": float(coords[1]),
                "category": label,
                "amenity_type": props.get("amenity_type", "POI"),
                "amenity": props.get("amenity", label),
                "color": color,
            })
    return pd.DataFrame(records)


def _selected_pid_from_event(event) -> int | None:
    try:
        objs = event.selection["objects"].get("listings", [])
    except Exception:
        return None
    if objs:
        try:
            return int(objs[0]["property_id"])
        except (KeyError, TypeError, ValueError):
            return None
    return None


listings = load_listings()
pois = load_pois()

# ── Three-panel layout: controls · map · insights ───────────────────────────
rail, mapcol, panel = st.columns([1.15, 2.9, 1.6], gap="medium")

with rail:
    st.markdown('<div class="rail-title">Target LGU</div>', unsafe_allow_html=True)
    lgu = st.selectbox("Target LGU", ["All LGUs", *METRO_CEBU_CITIES], label_visibility="collapsed")

    lgu_scope = listings if lgu == "All LGUs" else listings[listings["city"] == lgu]
    barangays = sorted(b for b in lgu_scope["barangay"].dropna().unique() if str(b).strip())
    st.markdown('<div class="rail-title">Barangay</div>', unsafe_allow_html=True)
    barangay_sel = st.selectbox("Barangay", ["All barangays", *barangays], label_visibility="collapsed")
    st.markdown(
        '<div class="rail-note">Filter by LGU, barangay, and residential stratum before reading the market pattern.</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="rail-title">Market stratum</div>', unsafe_allow_html=True)
    strata_sel = st.multiselect(
        "Stratum", list(STRATA_FILES.keys()), default=list(STRATA_FILES.keys()),
        label_visibility="collapsed",
    )

    st.markdown('<div class="rail-title">Map layers</div>', unsafe_allow_html=True)
    heatmap = st.toggle("Price heatmap", value=False,
                        help="Colour listings by price/sqm (cool → warm) instead of by stratum.")
    show_cbd = st.toggle("CBD nodes", value=False)
    show_lgu = st.toggle("LGU boundaries", value=True)
    show_pois = st.toggle("MCRAI POIs", value=True)

    st.markdown('<div class="rail-title">POI categories</div>', unsafe_allow_html=True)
    poi_sel = st.multiselect(
        "POI categories",
        list(POI_CATEGORIES.keys()),
        default=["Grocery", "Retail"],
        label_visibility="collapsed",
        disabled=not show_pois,
    )

    st.markdown('<div class="rail-footer">Places Insights - PH - Jun 2026</div>', unsafe_allow_html=True)

# ── Filter ──────────────────────────────────────────────────────────────────
view = listings[listings["stratum"].isin(strata_sel)].copy()
if lgu != "All LGUs":
    view = view[view["city"] == lgu].copy()
if barangay_sel != "All barangays":
    view = view[view["barangay"] == barangay_sel].copy()

poi_view = pois[pois["category"].isin(poi_sel)].copy() if show_pois and poi_sel else pd.DataFrame()

# Per-point colour (stratum or price ramp) on the filtered view.
if heatmap and len(view):
    lo = float(view["price_per_sqm"].quantile(0.05))
    hi = float(view["price_per_sqm"].quantile(0.95))
    span = (hi - lo) or 1.0
    view["color"] = [price_color((p - lo) / span) for p in view["price_per_sqm"]]
else:
    view["color"] = view["stratum"].map(STRATUM_COLOR)

view["price_fmt"] = view["price_per_sqm"].map(lambda v: f"{v:,.0f}").astype(str)
view["tooltip_title"] = view["stratum"].astype(str) + " · " + view["city"].astype(str)
barangay_tip = pd.Series("", index=view.index, dtype="object")
if "barangay" in view:
    barangay_tip = view["barangay"].fillna("").astype(str).map(lambda v: f"<br/>{v}" if v else "")
view["tooltip_body"] = (
    "PHP " + view["price_fmt"].astype(str) + "/sqm"
    + barangay_tip
    + "<br/><span style='font-size:11px'>" + view["address"].fillna("").astype(str) + "</span>"
)
map_records = view[DISPLAY_COLS + ["color", "tooltip_title", "tooltip_body"]].to_dict("records")
poi_records = []
if len(poi_view):
    poi_view["tooltip_title"] = poi_view["category"] + " POI"
    poi_view["tooltip_body"] = (
        poi_view["amenity"].fillna(poi_view["category"]).astype(str)
        + "<br/><span style='font-size:11px'>"
        + poi_view["amenity_type"].fillna("POI").astype(str)
        + "</span>"
    )
    poi_records = poi_view.to_dict("records")
selected_pid = st.session_state.get("mkt_sel_pid")

with mapcol:
    title = "Listing price intensity (₱/sqm)" if heatmap else "Listing distribution by stratum"
    top_legend = ""
    if heatmap:
        top_legend = (
            f'<div class="map-legend map-legend-top"><div class="map-legend-group">'
            f'<div class="map-legend-title">Price heatmap</div>'
            f'<div><div class="price-ramp" style="background:{PRICE_GRADIENT_CSS};"></div>'
            '<div class="price-ramp-labels"><span>Lower PHP/sqm</span><span>Higher PHP/sqm</span></div>'
            '</div></div></div>'
        )
    else:
        top_legend_parts = ['<div class="map-legend map-legend-top"><div class="map-legend-group"><div class="map-legend-title">Listings</div>']
        for label in [s for s in STRATA_FILES if s in strata_sel]:
            c = STRATUM_COLOR[label]
            top_legend_parts.append(
                f'<span class="map-legend-item"><span class="legend-dot" '
                f'style="background:rgb({c[0]},{c[1]},{c[2]});"></span>{label}</span>'
            )
        top_legend_parts.append('</div></div>')
        top_legend = "".join(top_legend_parts)
    st.markdown(
        f"""
        <div class="map-topbar">
            <div class="map-title">Residential<br>Market Map</div>
        </div>
        <div class="map-caption-row">
            <div class="map-caption-main">
                <div class="panel-h">{title}</div>
                <div class="panel-sub">{len(view):,} listings · {len(poi_records):,} visible POIs</div>
            </div>
            {top_legend}
        </div>
        """,
        unsafe_allow_html=True,
    )

    layers = []
    if show_lgu:
        layers.append(pdk.Layer(
            "GeoJsonLayer", data=load_lgu_geojson(), stroked=True, filled=False,
            get_line_color=[70, 80, 95], line_width_min_pixels=1.4, pickable=False,
        ))
    if poi_records:
        layers.append(pdk.Layer(
            "ScatterplotLayer", id="pois", data=poi_records,
            get_position="[longitude, latitude]", get_fill_color="color",
            stroked=True, get_line_color=[255, 255, 255, 230], line_width_min_pixels=0.5,
            get_radius=6, radius_units="pixels", radius_min_pixels=4, radius_max_pixels=10,
            pickable=True, auto_highlight=True, opacity=1.0,
        ))
    layers.append(pdk.Layer(
        "ScatterplotLayer", id="listings", data=map_records,
        get_position="[longitude, latitude]", get_fill_color="color",
        stroked=True, get_line_color=[255, 255, 255], line_width_min_pixels=1,
        get_radius=6, radius_units="pixels", radius_min_pixels=3, radius_max_pixels=11,
        pickable=True, auto_highlight=True, opacity=1.0,
    ))
    if show_cbd:
        cbd_pts = [{"lon": lon, "lat": lat, "name": k.replace("dist_", "").replace("_m", "")}
                   for k, (lat, lon) in CBD_COORDS.items()]
        layers.append(pdk.Layer(
            "ScatterplotLayer", data=cbd_pts, get_position="[lon, lat]",
            get_fill_color=[17, 24, 39], get_radius=7, radius_units="pixels", pickable=False,
        ))
    # Highlight ring on the currently selected property — white halo + dark ring
    # so it stays visible inside dense clusters and on any basemap.
    if selected_pid is not None:
        sel_rows = view[view["property_id"] == selected_pid]
        if len(sel_rows):
            sr = sel_rows.iloc[0]
            sel_data = [{"longitude": float(sr["longitude"]), "latitude": float(sr["latitude"])}]
            layers.append(pdk.Layer(
                "ScatterplotLayer", data=sel_data, get_position="[longitude, latitude]",
                stroked=True, filled=False, get_line_color=[255, 255, 255],
                line_width_min_pixels=6, get_radius=15, radius_units="pixels",
            ))
            layers.append(pdk.Layer(
                "ScatterplotLayer", data=sel_data, get_position="[longitude, latitude]",
                stroked=True, filled=False, get_line_color=[17, 24, 39],
                line_width_min_pixels=3, get_radius=15, radius_units="pixels",
            ))

    deck = pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(latitude=10.32, longitude=123.90, zoom=10.5),
        map_provider="carto",
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        tooltip={"html": "<b>{tooltip_title}</b><br/>{tooltip_body}",
                 "style": {"color": "white"}},
    )
    event = st.pydeck_chart(
        deck, width="stretch", height=700,
        on_select="rerun", selection_mode="single-object", key="market_map",
    )
    legend_html = ['<div class="map-legend">']
    legend_has_items = False
    if show_pois and poi_sel:
        legend_has_items = True
        legend_html.append('<div class="map-legend-group"><div class="map-legend-title">POI overlay</div>')
        for label in poi_sel:
            c = POI_CATEGORIES[label][1]
            legend_html.append(
                f'<span class="map-legend-item"><span class="legend-dot" '
                f'style="background:rgba({c[0]},{c[1]},{c[2]},{c[3] / 255:.2f});"></span>{label}</span>'
            )
        legend_html.append('</div>')
    if show_cbd:
        legend_has_items = True
        legend_html.append(
            '<div class="map-legend-group"><div class="map-legend-title">Reference</div>'
            '<span class="map-legend-item"><span class="legend-dot" style="background:#111827;"></span>CBD node</span></div>'
        )
    legend_html.append('</div>')
    if legend_has_items:
        st.markdown("".join(legend_html), unsafe_allow_html=True)

# Sync selection: capture this run's click and redraw if it changed.
new_pid = _selected_pid_from_event(event)
if new_pid != st.session_state.get("mkt_sel_pid"):
    st.session_state["mkt_sel_pid"] = new_pid
    st.rerun()

with panel:
    # ── Selected property + SHAP drivers ─────────────────────────────────────
    if selected_pid is not None:
        match = listings[listings["property_id"] == selected_pid]
        if len(match):
            row = match.iloc[0]
            st.markdown('<div class="panel-h">Selected property</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="sel-card">'
                f'<div class="sel-price">₱{row["price_per_sqm"]:,.0f}<span style="font-size:0.8rem;'
                f'color:#6B7280;font-weight:500;"> /sqm listed</span></div>'
                f'<div class="sel-addr">{row["stratum"]} · {row["property_type"]}'
                f'{"<br/>" + str(row["barangay"]) if pd.notna(row.get("barangay")) else ""}'
                f'<br/>{row["address"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            if shap_is_available():
                stratum_key = get_stratum(row["property_type"])
                feature_df = build_feature_vector_from_listing(row, stratum_key)
                raw_shap = explain(feature_df, stratum_key)
                st.markdown('<div class="rail-title dark">Top price drivers</div>', unsafe_allow_html=True)
                for d in top_drivers(raw_shap, n=6):
                    up = d["shap"] >= 0
                    color = "#d7191c" if up else "#2c7bb6"
                    arrow = "▲" if up else "▼"
                    sign = "+" if up else "−"
                    width = min(100.0, abs(d["pct"]))
                    st.markdown(
                        f'<div class="drv-row"><div class="drv-top"><span>{d["label"]}</span>'
                        f'<span style="color:{color};font-weight:600;">{arrow} {sign}{abs(d["pct"]):.0f}%</span>'
                        f'</div><div style="height:5px;border-radius:3px;background:{color};'
                        f'width:{width:.0f}%;opacity:0.8;"></div></div>',
                        unsafe_allow_html=True,
                    )
                st.caption("Approx. % effect on the model's price/sqm estimate. Red raises, blue lowers.")
            else:
                st.warning("SHAP is not installed, so the driver breakdown is unavailable.")

    # ── Market intelligence ──────────────────────────────────────────────────
    med = view["price_per_sqm"].median() if len(view) else 0
    avg = view["price_per_sqm"].mean() if len(view) else 0
    active_city = lgu if lgu != "All LGUs" else "Metro Cebu"
    st.markdown(
        f"""
        <div class="panel-head-flex">
            <div>
                <div class="panel-h">Market Intelligence</div>
                <div class="panel-sub">{active_city} - Places Insights</div>
            </div>
        </div>
        <div class="metric-grid">
            <div class="stat-card cool">
                <div class="stat-num">{len(view):,}</div>
                <div class="stat-lbl">Mapped listings</div>
            </div>
            <div class="stat-card warm">
                <div class="stat-num">₱{med:,.0f}</div>
                <div class="stat-lbl">Median / sqm</div>
            </div>
            <div class="stat-card">
                <div class="stat-num" style="color:#C8860A;">₱{avg:,.0f}</div>
                <div class="stat-lbl">Average / sqm</div>
            </div>
            <div class="stat-card">
                <div class="stat-num" style="color:#4F46E5;">{len(strata_sel)}</div>
                <div class="stat-lbl">Active strata</div>
            </div>
            <div class="stat-card">
                <div class="stat-num" style="color:#059669;">{len(poi_records):,}</div>
                <div class="stat-lbl">Visible POIs</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="composition-card"><div class="rail-title dark">Stratum composition</div>', unsafe_allow_html=True)
    if len(view):
        comp = view["stratum"].value_counts(normalize=True)
        bar = "".join(
            f'<span style="display:inline-block;height:12px;width:{p*100:.1f}%;'
            f'background:rgb({STRATUM_COLOR[s][0]},{STRATUM_COLOR[s][1]},{STRATUM_COLOR[s][2]});"></span>'
            for s, p in comp.items()
        )
        st.markdown(f'<div style="border-radius:6px;overflow:hidden;">{bar}</div>', unsafe_allow_html=True)
        for s, p in comp.items():
            st.markdown(f'<div style="font-size:0.78rem;color:#6B7280;">{s}: {p*100:.0f}%</div>',
                        unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="ranking-card"><div class="rail-title dark">Median PHP/sqm by LGU</div>', unsafe_allow_html=True)
    by_lgu = (listings[listings["stratum"].isin(strata_sel)]
              .groupby("city")["price_per_sqm"].median().sort_values(ascending=False))
    top = float(by_lgu.max()) if len(by_lgu) else 1.0
    for i, (city, val) in enumerate(by_lgu.items(), 1):
        width = val / top * 100
        st.markdown(
            f'<div class="rank-row"><span>{i}. {city}</span>'
            f'<span style="font-weight:600;">₱{val:,.0f}</span></div>'
            f'<div class="rank-bar-track"><div class="rank-bar" style="width:{width:.0f}%;"></div></div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

# ── Full SHAP breakdown for the selected property (below the map) ─────────────
if selected_pid is not None and shap_is_available():
    match = listings[listings["property_id"] == selected_pid]
    if len(match):
        row = match.iloc[0]
        with st.expander("Full SHAP breakdown for the selected property"):
            stratum_key = get_stratum(row["property_type"])
            feature_df = build_feature_vector_from_listing(row, stratum_key)
            shap_values = prettify(explain(feature_df, stratum_key))
            plt.rcParams.update({
                "figure.facecolor": "#FFFFFF", "axes.facecolor": "#FFFFFF",
                "savefig.facecolor": "#FFFFFF", "text.color": "#1F2937",
                "axes.labelcolor": "#1F2937", "axes.edgecolor": "#E5E7EB",
                "xtick.color": "#6B7280", "ytick.color": "#6B7280",
            })
            import shap  # noqa: F401
            shap.plots.waterfall(shap_values, max_display=15, show=False)
            st.pyplot(plt.gcf(), width="stretch")
            plt.close("all")
            st.caption(
                "Contributions in log(price/sqm) units. Red bars raise the model's estimate, "
                "blue bars lower it. The number beside each label is this property's value for that feature."
            )
