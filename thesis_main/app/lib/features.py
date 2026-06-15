import numpy as np
import pandas as pd
import streamlit as st

from lib.config import ABT_PATH, METRO_CEBU_CITIES, PROPERTY_TYPES, STRATUM_MAP
from lib.mcrai_lookup import get_mcrai_lookup
from lib.predict import get_model


# Training medians for optional physical fields (bedrooms/bathrooms).
_LAST_FALLBACK = False


@st.cache_data
def get_training_medians() -> pd.Series:
    """Load training medians lazily instead of at module import time."""
    return pd.read_csv(ABT_PATH).median(numeric_only=True)


def get_last_mcrai_fallback() -> bool:
    return _LAST_FALLBACK


def estimate_bir_rr(lat: float, lon: float) -> float:
    """Auto-estimate the BIR residential zonal value (PHP/sqm) for a dropped pin.

    Uses the same nearest-neighbour ABT lookup that supplies the MCRAI/road features,
    so the value reflects the official barangay-level figures carried by the closest
    training properties. Beyond 5 km the lookup returns the training median.
    """
    local = get_mcrai_lookup().query(float(lat), float(lon))
    return float(local["bir_zonal_rr_median"])


def get_stratum(property_type: str) -> str:
    return STRATUM_MAP[property_type]


def _optional_float(value):
    if value in (None, ""):
        return None
    return float(value)


def build_feature_vector(inputs: dict):
    """Return (feature_df, stratum_key) for the routed stratum model."""
    global _LAST_FALLBACK

    city = inputs["city"]
    property_type = inputs["property_type"]
    lat = float(inputs["lat"])
    lon = float(inputs["lon"])
    area_sqm = float(inputs["area_sqm"])
    bedrooms = _optional_float(inputs.get("bedrooms"))
    bathrooms = _optional_float(inputs.get("bathrooms"))
    bir_zonal_rr_median = float(inputs["bir_zonal_rr_median"])

    if city not in METRO_CEBU_CITIES:
        raise ValueError(f"Unsupported city: {city}")
    if property_type not in PROPERTY_TYPES:
        raise ValueError(f"Unsupported property type: {property_type}")
    if area_sqm <= 0:
        raise ValueError("area_sqm must be positive.")
    if bir_zonal_rr_median <= 0:
        raise ValueError("bir_zonal_rr_median must be positive.")

    stratum_key = get_stratum(property_type)
    train_medians = get_training_medians()

    bedrooms_imputed = int(bedrooms is None)
    bathrooms_imputed = int(bathrooms is None)
    bedrooms_value = float(train_medians["bedrooms"]) if bedrooms is None else float(bedrooms)
    bathrooms_value = float(train_medians["bathrooms"]) if bathrooms is None else float(bathrooms)

    lookup = get_mcrai_lookup()
    # local_features now carries the 8 network CBD distances too (Decision 7), looked up
    # from nearest training neighbours instead of recomputed as haversine — so a Mactan
    # pin inherits the bridge-inflated network distance the model was trained on.
    local_features = lookup.query(lat, lon)  # 9 MCRAI + 8 CBD dist + 2 road + spatial_lag + 2 bir
    _LAST_FALLBACK = lookup.fallback

    feature_values = {
        "area_sqm": area_sqm,
        "bedrooms": bedrooms_value,
        "bathrooms": bathrooms_value,
        "bedrooms_imputed": bedrooms_imputed,
        "bathrooms_imputed": bathrooms_imputed,
        **local_features,
        "bir_zonal_rr_median": bir_zonal_rr_median,
        "bir_zonal_rr_log": float(np.log(bir_zonal_rr_median)),
        # City dummies (Cebu City reference)
        "city_Consolacion": int(city == "Consolacion"),
        "city_Lapu-Lapu City": int(city == "Lapu-Lapu City"),
        "city_Mandaue City": int(city == "Mandaue City"),
        "city_Minglanilla": int(city == "Minglanilla"),
        "city_Talisay City": int(city == "Talisay City"),
        # Property-type dummies (Apartment reference; used by the Houses stratum)
        "property_type_House and Lot": int(property_type == "House and Lot"),
        "property_type_Single Detached": int(property_type == "Single Detached"),
        "property_type_Townhouse": int(property_type == "Townhouse"),
    }

    model = get_model(stratum_key)
    model_features = list(model.feature_names_in_)
    missing_columns = [c for c in model_features if c not in feature_values]
    if missing_columns:
        raise KeyError(f"Feature builder missing columns for {stratum_key}: {missing_columns}")

    feature_df = pd.DataFrame([feature_values]).reindex(columns=model_features)
    if feature_df.isna().any().any():
        null_columns = feature_df.columns[feature_df.isna().any()].tolist()
        raise ValueError(f"Feature vector contains nulls after assembly: {null_columns}")
    return feature_df, stratum_key


def build_feature_vector_from_listing(row: pd.Series, stratum_key: str) -> pd.DataFrame:
    """Reconstruct the model feature vector for an existing ABT listing.

    The listing already carries the location-derived features (distances, MCRAI,
    spatial lag), so those are read straight from the row rather than recomputed.
    Only the one-hot city/property-type dummies are rebuilt from the row's
    categorical columns. Any feature still missing falls back to the training
    median so the vector is always complete.
    """
    model = get_model(stratum_key)
    model_features = list(model.feature_names_in_)
    city = row.get("city")
    property_type = row.get("property_type")
    train_medians = get_training_medians()

    values: dict = {}
    for feature in model_features:
        if feature.startswith("city_"):
            values[feature] = int(city == feature[len("city_"):])
        elif feature.startswith("property_type_"):
            values[feature] = int(property_type == feature[len("property_type_"):])
        elif feature in row.index and pd.notna(row[feature]):
            values[feature] = float(row[feature])
        elif feature in train_medians.index:
            values[feature] = float(train_medians[feature])
        else:
            values[feature] = 0.0

    return pd.DataFrame([values]).reindex(columns=model_features)
