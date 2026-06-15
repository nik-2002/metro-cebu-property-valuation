import copy
import importlib.util

import numpy as np
import pandas as pd
import streamlit as st

from lib.predict import get_model


def _load_shap():
    import shap

    return shap


# Human-readable labels for the model feature columns, used on the SHAP
# waterfall so the explanation reads for a valuation practitioner rather than
# exposing raw column names.
FEATURE_LABELS = {
    # Physical
    "area_sqm": "Floor / lot area (sqm)",
    "bedrooms": "Bedrooms",
    "bathrooms": "Bathrooms",
    "bedrooms_imputed": "Bedrooms estimated (no input)",
    "bathrooms_imputed": "Bathrooms estimated (no input)",
    # CBD / node distances (metres)
    "dist_airport_m": "Distance to Mactan Airport (m)",
    "dist_cebu_business_park_m": "Distance to Cebu Business Park (m)",
    "dist_mandaue_cbd_m": "Distance to Mandaue CBD (m)",
    "dist_mactan_cbd_m": "Distance to Mactan CBD (m)",
    "dist_srp_m": "Distance to SRP (m)",
    "dist_talisay_tabunok_m": "Distance to Talisay–Tabunok (m)",
    "dist_consolacion_m": "Distance to Consolacion CBD (m)",
    "dist_naga_city_m": "Distance to Naga City node (m)",
    # Local accessibility (MCRAI) and neighbourhood
    "mcrai_education": "Education access (MCRAI)",
    "mcrai_grocery": "Grocery access (MCRAI)",
    "mcrai_health": "Health access (MCRAI)",
    "mcrai_hospitals": "Hospital access (MCRAI)",
    "mcrai_recreation": "Recreation access (MCRAI)",
    "mcrai_security": "Security access (MCRAI)",
    "mcrai_tourism": "Tourism access (MCRAI)",
    "mcrai_retail_density": "Retail density (MCRAI)",
    "mcrai_composite": "Overall accessibility (MCRAI)",
    "dist_to_trunk_road_m": "Distance to trunk road (m)",
    "dist_to_primary_road_m": "Distance to primary road (m)",
    "spatial_lag_price": "Neighbourhood price level",
    "bir_zonal_cr_median": "BIR zonal value — commercial",
    # BIR residential
    "bir_zonal_rr_median": "BIR zonal value — residential",
    "bir_zonal_rr_log": "BIR zonal value — residential (log)",
    # City dummies (Cebu City is the reference level)
    "city_Consolacion": "City: Consolacion",
    "city_Lapu-Lapu City": "City: Lapu-Lapu",
    "city_Mandaue City": "City: Mandaue",
    "city_Minglanilla": "City: Minglanilla",
    "city_Talisay City": "City: Talisay",
    # Property-type dummies (Apartment is the reference level)
    "property_type_House and Lot": "Type: House and Lot",
    "property_type_Single Detached": "Type: Single Detached",
    "property_type_Townhouse": "Type: Townhouse",
}


def shap_is_available() -> bool:
    return importlib.util.find_spec("shap") is not None


@st.cache_resource
def load_shap_explainer(stratum_key: str):
    if not shap_is_available():
        raise ImportError("SHAP is not installed in the active environment.")
    shap = _load_shap()
    return shap.TreeExplainer(get_model(stratum_key))


def explain(feature_df: pd.DataFrame, stratum_key: str):
    explainer = load_shap_explainer(stratum_key)
    shap_values = explainer(feature_df)
    return shap_values[0]


def _round_display_value(name: str, value: float) -> float:
    """Round a feature's raw value to a sensible precision for the y-axis label."""
    v = float(value)
    if name.startswith("mcrai_"):
        return round(v, 1)
    if name.endswith("_log"):
        return round(v, 2)
    return float(round(v))


def prettify(shap_values):
    """Return a copy of a single-row SHAP Explanation with readable feature
    names and rounded data values, for display on the waterfall."""
    raw_names = list(shap_values.feature_names)
    pretty = copy.deepcopy(shap_values)
    pretty.feature_names = [FEATURE_LABELS.get(n, n) for n in raw_names]
    pretty.data = np.array(
        [_round_display_value(n, v) for n, v in zip(raw_names, shap_values.data)]
    )
    return pretty


def top_drivers(shap_values, n: int = 6):
    """Return the n largest-magnitude feature contributions for a single-row
    SHAP Explanation (raw, un-prettified). Each driver carries a readable label,
    the raw log-scale contribution, and an approximate % effect on price/sqm
    (exp(shap) − 1), since the model target is log(price/sqm)."""
    raw_names = list(shap_values.feature_names)
    values = np.asarray(shap_values.values, dtype=float)
    order = np.argsort(np.abs(values))[::-1][:n]
    drivers = []
    for i in order:
        sv = float(values[i])
        drivers.append(
            {
                "label": FEATURE_LABELS.get(raw_names[i], raw_names[i]),
                "shap": sv,
                "pct": (float(np.exp(sv)) - 1.0) * 100.0,
            }
        )
    return drivers
