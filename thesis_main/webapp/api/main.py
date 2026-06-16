"""FastAPI inference backend for the Metro Cebu valuation webapp.

The Streamlit Property Predictor page and this API share the exact same model
code under ``thesis_main/app/lib`` — the same pickles, ABT nearest-neighbour
lookup, feature builder, RandomForest inference, and SHAP explainer. Setting
``WEBAPP_API=1`` before importing ``lib`` swaps Streamlit's cache decorators for
plain ``functools`` memoization (see ``app/lib/_cache.py``), so this process
runs without a Streamlit runtime while ``streamlit run`` keeps working.

Endpoints:
  GET  /api/health                 readiness probe
  GET  /api/resolve?lat=&lon=       point-in-polygon city + auto BIR estimate
  POST /api/predict                 full feature build + prediction + drivers

The heavy artifacts (models, BallTree over the ABT, SHAP explainer) load lazily
on first request and stay warm for the life of the process.
"""

from __future__ import annotations

import os

# Must be set before `lib` is imported so the cache shim avoids Streamlit.
os.environ.setdefault("WEBAPP_API", "1")

import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# thesis_main/webapp/api -> thesis_main/app
APP_DIR = Path(__file__).resolve().parents[2] / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from lib.config import PROPERTY_TYPES  # noqa: E402
from lib.features import (  # noqa: E402
    build_feature_vector,
    estimate_bir_rr,
    get_last_mcrai_fallback,
)
from lib.location import city_from_point  # noqa: E402
from lib.predict import predict  # noqa: E402
from lib.shap_explain import explain, shap_is_available, top_drivers  # noqa: E402

app = FastAPI(title="Metro Cebu Valuation API", version="0.1.0")

# Permissive CORS for local dev (Vite proxies /api, so same-origin in practice).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictRequest(BaseModel):
    lat: float
    lon: float
    property_type: str
    area_sqm: float
    bedrooms: Optional[float] = None
    bathrooms: Optional[float] = None
    bir_override: Optional[float] = None


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "shap_available": shap_is_available()}


@app.get("/api/resolve")
def resolve(lat: float = Query(...), lon: float = Query(...)) -> dict:
    """Resolve the LGU for a dropped pin and auto-estimate the BIR zonal value.

    Mirrors the Streamlit page's pin-drop behaviour: city comes from
    point-in-polygon, and the BIR residential value is read from the nearest
    training neighbours. Outside the six LGUs both are null.
    """
    city = city_from_point(lat, lon)
    if city is None:
        return {"city": None, "inside_metro": False, "bir_estimate": None}
    return {
        "city": city,
        "inside_metro": True,
        "bir_estimate": float(estimate_bir_rr(lat, lon)),
    }


@app.post("/api/predict")
def do_predict(req: PredictRequest) -> dict:
    city = city_from_point(req.lat, req.lon)
    if city is None:
        raise HTTPException(
            status_code=422,
            detail="Pin is outside the six Metro Cebu LGUs.",
        )
    if req.property_type not in PROPERTY_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported property type: {req.property_type}",
        )
    if req.area_sqm <= 0:
        raise HTTPException(status_code=422, detail="area_sqm must be positive.")

    if req.bir_override is not None and req.bir_override > 0:
        bir = float(req.bir_override)
    else:
        bir = float(estimate_bir_rr(req.lat, req.lon))

    try:
        feature_df, stratum_key = build_feature_vector(
            {
                "city": city,
                "property_type": req.property_type,
                "lat": req.lat,
                "lon": req.lon,
                "area_sqm": req.area_sqm,
                "bedrooms": req.bedrooms,
                "bathrooms": req.bathrooms,
                "bir_zonal_rr_median": bir,
            }
        )
        # Read the fallback flag right after the feature build that set it.
        mcrai_fallback = get_last_mcrai_fallback()
        result = predict(feature_df, stratum_key)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    drivers: list[dict] = []
    driver_error: Optional[str] = None
    if shap_is_available():
        try:
            drivers = top_drivers(explain(feature_df, stratum_key), n=5)
        except (ImportError, ValueError, RuntimeError) as exc:
            driver_error = str(exc)
    else:
        driver_error = "SHAP is unavailable in this environment."

    return {
        "city": city,
        "bir_used": bir,
        "stratum_label": result["stratum_label"],
        "model_family": result["model_family"],
        "price_per_sqm": result["price_per_sqm"],
        "price_php": result["price_php"],
        "ci_available": result["ci_available"],
        "ci_low_per_sqm": result["ci_low_per_sqm"],
        "ci_high_per_sqm": result["ci_high_per_sqm"],
        "mdape": result["mdape"],
        "mape": result["mape"],
        "pe20": result["pe20"],
        "mcrai_fallback": mcrai_fallback,
        "drivers": drivers,
        "driver_error": driver_error,
    }


# Serve the built Vite frontend from the same origin when it is present, so a single
# deployment (e.g. Hugging Face Spaces) hosts both the static site and the API with no
# CORS. Mounted last so the /api routes above always take precedence. Skipped in local
# dev where Vite serves the frontend (though dist/ may also exist after a build).
_DIST = Path(__file__).resolve().parents[1] / "dist"
if _DIST.is_dir():
    app.mount("/", StaticFiles(directory=str(_DIST), html=True), name="frontend")
