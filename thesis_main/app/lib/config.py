from pathlib import Path


THESIS_DIR = Path(__file__).resolve().parents[2]

# abt_clean.csv is used only as the spatial pool for nearest-neighbour lookup of
# local features (MCRAI, road distances, spatial lag, BIR commercial). The log_price
# column in this file is NOT used here, so its known issue is irrelevant to the app.
ABT_PATH = THESIS_DIR / "Data" / "processed" / "abt_clean.csv"
AB_PATH = ABT_PATH

# Stratified deployment (Decision 34): one best-per-stratum tree model each.
STRAT_DIR = THESIS_DIR / "Models" / "stratified"
MANIFEST_PATH = STRAT_DIR / "deployment_manifest.json"
STRATUM_MODEL_FILES = {
    "condo":  STRAT_DIR / "condo_model.pkl",
    "houses": STRAT_DIR / "houses_model.pkl",
    "lot":    STRAT_DIR / "lot_model.pkl",
}
MODEL_LABEL = "Stratified Random Forest (per-sqm)"

# property_type -> stratum key
STRATUM_MAP = {
    "Condominium":     "condo",
    "Vacant Lot":      "lot",
    "Single Detached": "houses",
    "House and Lot":   "houses",
    "Townhouse":       "houses",
    "Apartment":       "houses",
}
STRATUM_LABELS = {"condo": "Condominium", "houses": "Houses", "lot": "Vacant Lot"}

# The eight CBD/subcenter anchors — keys match the model feature names.
CBD_COORDS = {
    "dist_airport_m": (10.30719, 123.97899),
    "dist_cebu_business_park_m": (10.317868, 123.904254),
    "dist_mandaue_cbd_m": (10.341511, 123.920887),
    "dist_mactan_cbd_m": (10.313654, 123.951363),
    "dist_srp_m": (10.271864, 123.858887),
    "dist_talisay_tabunok_m": (10.244388, 123.838787),
    "dist_consolacion_m": (10.376512, 123.963788),
    "dist_naga_city_m": (10.207879, 123.758231),
}

# Cebu City is the reference category (no dummy column).
METRO_CEBU_CITIES = [
    "Cebu City",
    "Consolacion",
    "Lapu-Lapu City",
    "Mandaue City",
    "Minglanilla",
    "Talisay City",
]

PROPERTY_TYPES = [
    "Condominium",
    "House and Lot",
    "Single Detached",
    "Townhouse",
    "Vacant Lot",
]

# City-level median BIR zonal RR values (PHP/sqm).
BIR_ZONAL_RR_DEFAULTS = {
    "Cebu City":       29500.0,
    "Consolacion":      2400.0,
    "Lapu-Lapu City":   6500.0,
    "Mandaue City":    12040.0,
    "Minglanilla":      7000.0,
    "Talisay City":     9500.0,
}

# MCRAI categories used by the models (Decision 28/29: finance + transport retired,
# hospitals added; composite retained for the tree models).
MCRAI_CATS = [
    "mcrai_education",
    "mcrai_grocery",
    "mcrai_health",
    "mcrai_hospitals",
    "mcrai_recreation",
    "mcrai_security",
    "mcrai_tourism",
    "mcrai_retail_density",
    "mcrai_composite",
]

# Network CBD distances are precomputed per training row (osmnx Dijkstra, Decision 7).
# They are looked up from the nearest training neighbours rather than recomputed, so a
# dropped pin inherits the trained network distance — including Mactan bridge friction —
# without loading the osmnx graph at runtime. Replaces the old haversine_to_cbds path,
# which fed straight-line distances into features the model learned as network distances.
CBD_DIST_COLS = list(CBD_COORDS.keys())

# All location-derived features supplied by nearest-neighbour lookup from the ABT pool.
# bir_zonal_rr_median is included so the predictor can auto-estimate it from the dropped
# pin; build_feature_vector still overrides it with the user's value (estimate or override).
LOCAL_LOOKUP_COLS = MCRAI_CATS + CBD_DIST_COLS + [
    "dist_to_trunk_road_m",
    "dist_to_primary_road_m",
    "spatial_lag_price",
    "bir_zonal_cr_median",
    "bir_zonal_rr_median",
]
