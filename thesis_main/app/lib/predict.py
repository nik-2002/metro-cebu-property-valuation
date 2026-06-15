import json
import pickle

import numpy as np
import pandas as pd
import streamlit as st

from lib.config import MANIFEST_PATH, MODEL_LABEL, STRATUM_LABELS, STRATUM_MODEL_FILES


@st.cache_resource
def load_models() -> dict:
    """Load the three best-per-stratum models once."""
    models = {}
    for key, path in STRATUM_MODEL_FILES.items():
        with open(path, "rb") as fh:
            models[key] = pickle.load(fh)
    return models


@st.cache_resource
def load_manifest() -> dict:
    with open(MANIFEST_PATH) as fh:
        return json.load(fh)


def get_model(stratum_key: str):
    return load_models()[stratum_key]


def predict(feature_df: pd.DataFrame, stratum_key: str) -> dict:
    """Predict for one property. The target is log(price_per_sqm); total = per-sqm * area."""
    model = get_model(stratum_key)
    manifest = load_manifest()

    log_pred = float(model.predict(feature_df)[0])
    price_per_sqm = float(np.exp(log_pred))
    area_sqm = float(feature_df["area_sqm"].iloc[0])
    price_php = price_per_sqm * area_sqm

    # Uncertainty band from the spread across RF trees (log per-sqm scale).
    if hasattr(model, "estimators_"):
        rng = np.random.default_rng(42)
        sample_size = min(100, len(model.estimators_))
        sampled_indices = rng.choice(len(model.estimators_), size=sample_size, replace=False)
        feature_array = feature_df.to_numpy()  # trees were fit without feature names
        tree_preds = np.array(
            [float(model.estimators_[idx].predict(feature_array)[0]) for idx in sampled_indices]
        )
        std_log = float(tree_preds.std(ddof=1)) if sample_size > 1 else 0.0
        ci_low_per_sqm = float(np.exp(log_pred - 1.96 * std_log))
        ci_high_per_sqm = float(np.exp(log_pred + 1.96 * std_log))
        ci_available = True
    else:
        ci_low_per_sqm = ci_high_per_sqm = price_per_sqm
        ci_available = False

    family = manifest["strata"][stratum_key]["deployed_family"]
    # Decision 42: GroupKFold(5) leak-free metrics live under "metrics_group_cv".
    # Fall back to the legacy "deployed_metrics" key only if an older manifest is loaded.
    stratum_manifest = manifest["strata"][stratum_key]
    metrics = stratum_manifest.get("metrics_group_cv") or stratum_manifest.get("deployed_metrics") or {}

    return {
        "price_php": price_php,
        "price_per_sqm": price_per_sqm,
        "log_pred": log_pred,
        "ci_low_per_sqm": ci_low_per_sqm,
        "ci_high_per_sqm": ci_high_per_sqm,
        "ci_available": ci_available,
        "stratum_key": stratum_key,
        "stratum_label": STRATUM_LABELS[stratum_key],
        "model_family": family,
        "model_label": f"{MODEL_LABEL} — {STRATUM_LABELS[stratum_key]} ({family})",
        # Backward-compatible headline field (UI still reads test_mape).
        "test_mape": metrics.get("MAPE"),
        # Decision 42 GroupKFold metrics. MdAPE/PE20 are the headline operational
        # metrics; COD/PRD/PE10 are IAAO-context diagnostics (not IAAO-compliant).
        "mdape": metrics.get("MdAPE"),
        "mape": metrics.get("MAPE"),
        "cod": metrics.get("COD"),
        "prd": metrics.get("PRD"),
        "pe10": metrics.get("PE10"),
        "pe20": metrics.get("PE20"),
        "median_ratio": metrics.get("median_ratio"),
        # Full metric block for any consumer that needs the raw values.
        "metrics": metrics,
    }
