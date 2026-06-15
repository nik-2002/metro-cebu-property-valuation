import html
import json
from pathlib import Path

import folium
import streamlit as st
from branca.element import MacroElement, Template
from streamlit_folium import st_folium

from lib.config import PROPERTY_TYPES
from lib.features import (
    build_feature_vector,
    estimate_bir_rr,
    get_last_mcrai_fallback,
)
from lib.location import city_from_point
from lib.navbar import render_navbar
from lib.predict import predict
from lib.shap_explain import explain, shap_is_available, top_drivers
from lib.style import inject_dashboard_css

st.set_page_config(
    page_title="Property Predictor — Metro Cebu Estimator",
    page_icon="🏡",
    layout="wide",
)
render_navbar(active="Property Predictor")
inject_dashboard_css()

APP_DATA = Path(__file__).resolve().parents[1] / "data"
MAP_CENTER = [10.32, 123.90]
MAP_BOUNDS = [[10.17, 123.70], [10.52, 124.21]]
MAP_MIN_ZOOM = 10
MAP_MAX_ZOOM = 16
MAP_HEIGHT = 600


class _ModifierWheelZoom(MacroElement):
    _template = Template(
        """
        {% macro script(this, kwargs) %}
        (function() {
            var map = {{ this._parent.get_name() }};
            var container = map.getContainer();
            if (!container || container.dataset.modifierWheelZoom === "1") {
                return;
            }
            container.dataset.modifierWheelZoom = "1";
            if (map.scrollWheelZoom) {
                map.scrollWheelZoom.enable();
            }
            container.addEventListener("wheel", function(event) {
                if (!event.ctrlKey && !event.metaKey) {
                    event.stopImmediatePropagation();
                }
            }, { capture: true, passive: true });
        })();
        {% endmacro %}
        """
    )


@st.cache_data
def load_lgu_geojson() -> dict:
    path = APP_DATA / "lgu_boundaries.geojson"
    return json.loads(path.read_text()) if path.exists() else {"type": "FeatureCollection", "features": []}


def _parse_optional_number(raw_value: str):
    raw_value = (raw_value or "").strip()
    if not raw_value:
        return None
    return float(raw_value)


def _sync_predict_pin_from_map() -> None:
    map_state = st.session_state.get("predict_map")
    if not isinstance(map_state, dict):
        return
    clicked = map_state.get("last_clicked")
    if not clicked:
        return

    new_pin = {"lat": round(clicked["lat"], 6), "lon": round(clicked["lng"], 6)}
    if new_pin != st.session_state.get("predict_pin"):
        st.session_state["predict_pin"] = new_pin
        st.session_state.pop("predict_bir_estimate", None)


# ── Resolve the dropped pin → derived city + auto BIR ────────────────────────
pin = st.session_state.get("predict_pin")
derived_city = city_from_point(pin["lat"], pin["lon"]) if pin else None
pin_key = f"{pin['lat']:.6f},{pin['lon']:.6f}" if (pin and derived_city) else None
cached_bir = st.session_state.get("predict_bir_estimate")
bir_estimate = (
    float(cached_bir["value"])
    if cached_bir and cached_bir.get("pin_key") == pin_key
    else None
)

# ── Three-panel layout: inputs · map · results ───────────────────────────────
rail, mapcol, panel = st.columns([1.15, 2.9, 1.6], gap="small")

with rail:
    st.markdown(
        """
        <div class="brand-block">
            <div>
                <div class="brand-name">Metro Cebu</div>
                <div class="brand-sub">Valuation Intelligence</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="rail-title">Property type</div>', unsafe_allow_html=True)
    property_type = st.segmented_control(
        "Property type", PROPERTY_TYPES, default=PROPERTY_TYPES[0],
        label_visibility="collapsed",
    ) or PROPERTY_TYPES[0]
    is_lot = property_type == "Vacant Lot"

    area_label = {
        "Condominium": "Floor area (sqm)",
        "Vacant Lot": "Lot area (sqm)",
    }.get(property_type, "Total area (sqm)")
    st.markdown(f'<div class="rail-title">{area_label}</div>', unsafe_allow_html=True)
    area_sqm = st.number_input(
        area_label, min_value=0.01, value=100.0, format="%.2f", label_visibility="collapsed",
    )

    if is_lot:
        bedrooms_raw = ""
        bathrooms_raw = ""
        st.caption("Bedrooms / bathrooms do not apply to vacant lots.")
    else:
        st.markdown('<div class="rail-title">Bedrooms · Bathrooms</div>', unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        bedrooms_raw = b1.text_input("Bedrooms", placeholder="Optional", label_visibility="collapsed")
        bathrooms_raw = b2.text_input("Bathrooms", placeholder="Optional", label_visibility="collapsed")
        st.caption("Optional — left blank, the training median is used.")

    st.markdown('<div class="rail-title">City (from pin)</div>', unsafe_allow_html=True)
    if pin and derived_city:
        st.markdown(f'<div class="rail-pill">{derived_city}</div>', unsafe_allow_html=True)
    elif pin:
        st.markdown('<div class="rail-pill">Outside Metro Cebu</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="rail-pill">Drop a pin →</div>', unsafe_allow_html=True)

    st.markdown('<div class="rail-title">BIR zonal — residential</div>', unsafe_allow_html=True)
    bir_controls = st.empty()
    bir_value = None

    st.markdown(
        '<div class="rail-footer">Click the map to set the location. City and BIR zonal '
        'value follow the pin automatically.</div>',
        unsafe_allow_html=True,
    )

# ── Map column: drop-a-pin ───────────────────────────────────────────────────
with mapcol:
    city_pill = derived_city or ("Outside Metro Cebu" if pin else "No location set")
    pill_class = "region-pill" if (pin and derived_city) else "region-pill empty"
    st.markdown(
        f"""
        <div class="map-topbar">
            <div class="map-title">Property Price<br>Predictor</div>
            <div class="{pill_class}">{city_pill}</div>
            <div></div>
        </div>
        <div class="map-caption-row">
            <div>
                <div class="panel-h">Drop a pin on the property</div>
                <div class="panel-sub">Click anywhere inside the six Metro Cebu LGUs.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fmap = folium.Map(
        location=MAP_CENTER,
        zoom_start=11,
        tiles="CartoDB positron",
        min_zoom=MAP_MIN_ZOOM,
        max_zoom=MAP_MAX_ZOOM,
        min_lat=MAP_BOUNDS[0][0],
        min_lon=MAP_BOUNDS[0][1],
        max_lat=MAP_BOUNDS[1][0],
        max_lon=MAP_BOUNDS[1][1],
        max_bounds=True,
        prefer_canvas=True,
    )
    fmap.add_child(_ModifierWheelZoom())
    folium.GeoJson(
        load_lgu_geojson(),
        name="LGU boundaries",
        style_function=lambda _f: {"color": "#46505F", "weight": 1.4, "fill": False},
        highlight_function=lambda _f: {"color": "#053B68", "weight": 2.2, "fill": False},
        tooltip=folium.GeoJsonTooltip(fields=["lgu"], aliases=[""]),
    ).add_to(fmap)
    if pin:
        folium.Marker(
            [pin["lat"], pin["lon"]],
            tooltip="Selected location",
            icon=folium.Icon(color="red", icon="home", prefix="fa"),
        ).add_to(fmap)

    st_folium(
        fmap, height=MAP_HEIGHT, width=None, key="predict_map",
        returned_objects=["last_clicked"], on_change=_sync_predict_pin_from_map,
    )

    if pin and derived_city:
        st.caption(f"Pin: {pin['lat']:.5f}, {pin['lon']:.5f} · {derived_city}")
    elif pin:
        st.warning(
            "This pin is outside the six Metro Cebu LGUs. Drop it inside Cebu City, Mandaue, "
            "Lapu-Lapu, Talisay, Minglanilla, or Consolacion to get a prediction."
        )

if pin and derived_city and bir_estimate is None:
    with st.spinner("Estimating BIR zonal value from nearby training properties..."):
        bir_estimate = estimate_bir_rr(pin["lat"], pin["lon"])
    st.session_state["predict_bir_estimate"] = {"pin_key": pin_key, "value": float(bir_estimate)}

with bir_controls.container():
    if bir_estimate is not None:
        st.markdown(
            f'<div class="rail-readout">PHP {bir_estimate:,.0f}<small> /sqm · auto from location</small></div>',
            unsafe_allow_html=True,
        )
        override = st.checkbox("Override BIR value")
        if override:
            bir_value = st.number_input(
                "BIR zonal RR (PHP/sqm)", min_value=1.0, value=float(bir_estimate), format="%.2f",
            )
        else:
            bir_value = float(bir_estimate)
    elif pin and derived_city:
        st.markdown(
            '<div class="rail-readout"><small>Estimating from location...</small></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="rail-readout"><small>Set once a pin is inside Metro Cebu.</small></div>',
            unsafe_allow_html=True,
        )

# ── Panel: predict + results ─────────────────────────────────────────────────
with panel:
    st.markdown('<div class="panel-h">Estimate</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-sub">Open-market residential price per sqm.</div>', unsafe_allow_html=True)

    ready = bool(pin and derived_city and bir_value)
    predict_clicked = st.button("Predict Price", width="stretch", disabled=not ready, type="primary")
    if not ready:
        st.caption("Drop a pin inside Metro Cebu to enable prediction.")

    if predict_clicked:
        try:
            feature_df, stratum_key = build_feature_vector(
                {
                    "city": derived_city,
                    "property_type": property_type,
                    "lat": pin["lat"],
                    "lon": pin["lon"],
                    "area_sqm": area_sqm,
                    "bedrooms": _parse_optional_number(bedrooms_raw),
                    "bathrooms": _parse_optional_number(bathrooms_raw),
                    "bir_zonal_rr_median": bir_value,
                }
            )
            result = predict(feature_df, stratum_key)
            st.session_state["last_feature_df"] = feature_df
            st.session_state["last_stratum_key"] = stratum_key
            st.session_state["last_result"] = result
            st.session_state["prediction_ready"] = True
            st.session_state["last_mcrai_fallback"] = get_last_mcrai_fallback()
            st.session_state["last_drivers"] = []
            st.session_state["driver_error"] = None
            if shap_is_available():
                try:
                    raw_shap = explain(feature_df, stratum_key)
                    st.session_state["last_drivers"] = top_drivers(raw_shap, n=5)
                except (ImportError, ValueError, RuntimeError) as exc:
                    st.session_state["driver_error"] = str(exc)
            else:
                st.session_state["driver_error"] = "SHAP is unavailable in this environment."
        except (ValueError, KeyError) as exc:
            st.error(str(exc))
            st.session_state["prediction_ready"] = False

    if st.session_state.get("prediction_ready"):
        result = st.session_state["last_result"]
        # Decision 42 headline metrics: group-CV MdAPE and PE20, with MAPE as support.
        def _pct(value):
            return f"{value:.0f}%" if isinstance(value, (int, float)) else "n/a"

        st.caption(
            f"Model: **{result['stratum_label']}** stratum · {result['model_family']} "
            f"(group-CV MdAPE ≈ {_pct(result.get('mdape'))}, "
            f"MAPE ≈ {_pct(result.get('test_mape'))}, "
            f"PE20 ≈ {_pct(result.get('pe20'))})"
        )
        st.metric("Predicted price per sqm", f"PHP {result['price_per_sqm']:,.0f}")
        st.metric("Total estimated price", f"PHP {result['price_php']:,.0f}")

        if result["ci_available"]:
            st.write(
                f"Model uncertainty range: "
                f"PHP {result['ci_low_per_sqm']:,.0f} – {result['ci_high_per_sqm']:,.0f} per sqm"
            )
        st.caption("Total = price/sqm × area.")

        if st.session_state.get("last_mcrai_fallback"):
            st.warning(
                "Location is outside the Metro Cebu training area — "
                "local accessibility features approximated from city averages."
            )
        drivers = st.session_state.get("last_drivers", [])
        driver_html = ['<div class="driver-panel"><div class="rail-title dark">Price drivers</div>']
        if drivers:
            for driver in drivers:
                up = driver["shap"] >= 0
                color = "#E23E57" if up else "#2563EB"
                sign = "+" if up else "-"
                width = min(100.0, max(8.0, abs(driver["pct"])))
                driver_html.append(
                    f'<div class="driver-row">'
                    f'<div class="driver-top">'
                    f'<span class="driver-label">{html.escape(driver["label"])}</span>'
                    f'<span class="driver-impact" style="color:{color};">'
                    f'{sign}{abs(driver["pct"]):.0f}%</span>'
                    f'</div>'
                    f'<div class="driver-track"><div class="driver-bar" '
                    f'style="width:{width:.0f}%;background:{color};"></div></div>'
                    f'</div>'
                )
            driver_html.append(
                '<div class="driver-note">Approximate effect on price/sqm. '
                'Red raises the estimate, blue lowers it.</div>'
            )
        elif st.session_state.get("driver_error"):
            driver_html.append(
                f'<div class="driver-note">{html.escape(st.session_state["driver_error"])}</div>'
            )
        driver_html.append('</div>')
        st.markdown("".join(driver_html), unsafe_allow_html=True)
