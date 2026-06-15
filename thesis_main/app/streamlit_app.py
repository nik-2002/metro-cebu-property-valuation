import streamlit as st

from lib.navbar import render_navbar
from lib.predict import load_manifest

st.set_page_config(
    page_title="Metro Cebu Residential Price Estimator",
    page_icon="🏠",
    layout="wide",
)
render_navbar(active="Home")

st.title("Metro Cebu Residential Price Estimator")
st.subheader("A decision support tool for open-market residential valuation")
st.write(
    "This app packages the thesis's **stratified** valuation models into a practical "
    "per-sqm estimator for Metro Cebu. A property is routed to the model for its market "
    "stratum — Condominium, Houses, or Vacant Lot — and the feature vector is reconstructed "
    "from user inputs, CBD distances, and nearest-neighbour local accessibility features (MCRAI, "
    "road-network distance, spatial lag)."
)
st.write(
    "Navigate using the top bar: **Price Surface** shows the predicted open-market price-per-sqm "
    "across Metro Cebu by property archetype; **Property Predictor** generates a single-property "
    "estimate with a SHAP explanation of what drove the prediction."
)
# Headline metrics read live from the deployment manifest (MdAPE is the plain-language
# headline per the thesis convention; MAPE shown as support). Dynamic so the home page
# never drifts from the deployed models.
_strata = load_manifest()["strata"]
_mdape = " · ".join(
    f"{_strata[k]['metrics_group_cv']['MdAPE']:.0f}% {label}"
    for k, label in (("condo", "Condominium"), ("houses", "Houses"), ("lot", "Vacant Lot"))
)
st.caption(
    "Models: best-per-stratum Random Forest on log(price per sqm), evaluated leak-free "
    "(GroupKFold by location). Headline typical error (MdAPE) — "
    f"{_mdape}. See the Property Predictor for the full metric panel."
)
