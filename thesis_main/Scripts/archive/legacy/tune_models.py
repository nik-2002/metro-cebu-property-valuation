from pathlib import Path
import pickle
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, RepeatedKFold, train_test_split


THESIS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = THESIS_DIR.parent
ABT_PATH = THESIS_DIR / "Data" / "processed" / "abt_clean.csv"
MODELS_DIR = THESIS_DIR / "Models"
EDA_DIR = ROOT_DIR / "EDA"
CONFIG_PATH = THESIS_DIR / "app" / "lib" / "config.py"
STREAMLIT_APP_PATH = THESIS_DIR / "app" / "streamlit_app.py"

IMPLAUSIBLE_IDS = [468, 714, 769]
EXCLUDE_COLS = {
    "price_per_sqm", "log_price", "price_php", "valuation_gap",
    "price_outlier_flag", "price_type", "spatial_lag_price",
    "property_id", "property_name", "address", "geocode_source",
    "barangay_geocoded", "source", "floor_area_imputed",
    "mcrai_composite",
    "market_segment",
}
CAT_COLS = ["city", "property_type"]
OLS_EXTRA_DROPS = [
    "dist_talisay_tabunok_m", "is_mactan_island", "bir_zonal_rr_log",
    "is_vacant_lot", "latitude", "longitude",
    "lot_area_sqm", "floor_area_sqm", "area_sqm", "log_lot_area_sqm",
]
LOG_AREA_COLS = ["log_floor_area_sqm"]

RF_CONFIRMATION_GRID = {
    "n_estimators": [200, 300, 400],
    "max_features": [0.8, 0.9, 1.0],
    "max_depth": [None, 20],
    "min_samples_leaf": [1, 2],
    "min_samples_split": [2, 4],
}
XGB_PARAM_DIST = {
    "n_estimators": [200, 300, 400, 500],
    "learning_rate": [0.03, 0.05, 0.07, 0.10],
    "max_depth": [4, 5, 6, 7, 8],
    "subsample": [0.7, 0.8, 0.9, 1.0],
    "colsample_bytree": [0.7, 0.8, 0.9, 1.0],
    "min_child_weight": [1, 3, 5],
}
CV = RepeatedKFold(n_splits=5, n_repeats=3, random_state=42)
SCORING = {
    "rmse": "neg_root_mean_squared_error",
    "mae": "neg_mean_absolute_error",
    "r2": "r2",
}

MODEL_ARTIFACTS = {
    "RF baseline": {
        "path": MODELS_DIR / "rf_model.pkl",
        "label": "Random Forest",
        "config_filename": "rf_model.pkl",
    },
    "RF tuned": {
        "path": MODELS_DIR / "rf_tuned.pkl",
        "label": "Random Forest (Tuned)",
        "config_filename": "rf_tuned.pkl",
    },
    "XGB baseline": {
        "path": MODELS_DIR / "xgb_model.pkl",
        "label": "XGBoost",
        "config_filename": "xgb_model.pkl",
    },
    "XGB tuned": {
        "path": MODELS_DIR / "xgb_tuned.pkl",
        "label": "XGBoost (Tuned)",
        "config_filename": "xgb_tuned.pkl",
    },
}
STEP0_LABELS = {
    "RF baseline": "RF baseline",
    "RF tuned": "RF tuned (stale)",
    "XGB baseline": "XGB baseline",
    "XGB tuned": "XGB tuned (stale)",
}


def evaluate(y_true_log, y_pred_log, model_name: str) -> dict:
    y_true = np.exp(y_true_log)
    y_pred = np.exp(y_pred_log)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    print(f"\n{model_name} — Test-set metrics (total PHP price, back-transformed):")
    print(f"  MAPE : {mape:.2f}%")
    print(f"  MAE  : {mae:,.2f}")
    print(f"  RMSE : {rmse:,.2f}")
    print(f"  R2   : {r2:.4f}")
    return {
        "Model": model_name,
        "MAPE": float(mape),
        "MAE": float(mae),
        "RMSE": float(rmse),
        "R2": float(r2),
    }


def metrics_to_table_row(metrics: dict) -> dict:
    return {
        "Model": metrics["Model"],
        "R2": metrics["R2"],
        "MAPE": metrics["MAPE"],
        "MAE (PHP M)": metrics["MAE"] / 1_000_000,
        "RMSE (PHP M)": metrics["RMSE"] / 1_000_000,
    }


def print_table(title: str, rows: list[dict]) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)
    df = pd.DataFrame(rows)
    df_print = df.copy()
    df_print["R2"] = df_print["R2"].map(lambda value: f"{value:.4f}")
    df_print["MAPE"] = df_print["MAPE"].map(lambda value: f"{value:.2f}%")
    df_print["MAE (PHP M)"] = df_print["MAE (PHP M)"].map(lambda value: f"{value:.2f}")
    df_print["RMSE (PHP M)"] = df_print["RMSE (PHP M)"].map(lambda value: f"{value:.2f}")
    print(df_print.to_string(index=False))


def prepare_model_data() -> dict:
    print("=" * 70)
    print("STEP A — Pre-modeling data prep")
    print("=" * 70)

    df = pd.read_csv(ABT_PATH)
    df = df[df["market_segment"] == "open_market"].copy()
    print(f"Filtered to open_market: {len(df)} rows")
    print(f"Loaded ABT: {len(df):,} rows")

    df = df[~df["property_id"].isin(IMPLAUSIBLE_IDS)].copy()
    print(f"After dropping implausible property_ids {IMPLAUSIBLE_IDS}: {len(df):,} rows")

    df = df[df["price_per_sqm"].notna()].copy()
    print(f"After dropping null price_per_sqm: {len(df):,} rows")

    df = df[df["spatial_lag_price"].notna()].copy()
    print(f"After dropping null spatial_lag_price: {len(df):,} rows")
    print(f"\nFinal modeling-ready dataset: {len(df):,} rows")

    print("\n" + "=" * 70)
    print("STEP B — Feature matrix definition")
    print("=" * 70)

    df_encoded = pd.get_dummies(df, columns=CAT_COLS, drop_first=True, dtype=int)
    feature_cols = [c for c in df_encoded.columns if c not in EXCLUDE_COLS and c != "log_price"]

    all_null_cols = [c for c in feature_cols if df_encoded[c].isna().all()]
    imputable_cols = [
        c for c in feature_cols
        if df_encoded[c].isnull().any() and not df_encoded[c].isna().all()
    ]

    if all_null_cols:
        print(f"All-null columns (filling with 0): {all_null_cols}")
        df_encoded[all_null_cols] = df_encoded[all_null_cols].fillna(0)

    if imputable_cols:
        print(f"Columns with remaining nulls (imputing with median): {imputable_cols}")
        imputer = SimpleImputer(strategy="median")
        df_encoded[imputable_cols] = imputer.fit_transform(df_encoded[imputable_cols])

    for col in ["lot_area_sqm", "floor_area_sqm", "area_sqm"]:
        df_encoded[f"log_{col}"] = np.log1p(df_encoded[col])

    x_full = df_encoded[feature_cols].copy().reset_index(drop=True)
    x_ols_base = x_full.drop(columns=OLS_EXTRA_DROPS, errors="ignore").copy().reset_index(drop=True)
    log_area_df = df_encoded[LOG_AREA_COLS].reset_index(drop=True)
    x_ols = pd.concat([x_ols_base, log_area_df], axis=1)
    y = df_encoded["log_price"].reset_index(drop=True)
    market_seg_col = df["market_segment"].reset_index(drop=True)

    print(f"\nX_full shape: {x_full.shape}")
    print(f"X_ols shape: {x_ols.shape}")

    print("\n" + "=" * 70)
    print("STEP C — Train / test split (80/20, stratify=market_segment)")
    print("=" * 70)

    (
        x_full_train,
        x_full_test,
        x_ols_train,
        x_ols_test,
        y_train,
        y_test,
        seg_train,
        seg_test,
    ) = train_test_split(
        x_full,
        x_ols,
        y,
        market_seg_col,
        test_size=0.2,
        random_state=42,
        stratify=market_seg_col,
    )

    print(f"Train size: {len(x_full_train):,} rows")
    print(f"Test  size: {len(x_full_test):,} rows")
    print("\nmarket_segment distribution — TRAIN:")
    print(seg_train.value_counts().to_string())
    print("\nmarket_segment distribution — TEST:")
    print(seg_test.value_counts().to_string())

    return {
        "X_full_train": x_full_train,
        "X_full_test": x_full_test,
        "X_ols_train": x_ols_train,
        "X_ols_test": x_ols_test,
        "y_train": y_train,
        "y_test": y_test,
    }


def get_model_feature_names(model) -> list[str] | None:
    feature_names = getattr(model, "feature_names_in_", None)
    if feature_names is not None:
        return [str(name) for name in feature_names]
    if hasattr(model, "get_booster"):
        try:
            booster_names = model.get_booster().feature_names
        except Exception:
            booster_names = None
        if booster_names:
            return [str(name) for name in booster_names]
    return None


def align_feature_frame(frame: pd.DataFrame, feature_names: list[str] | None) -> pd.DataFrame:
    if feature_names is None:
        return frame
    return frame.reindex(columns=feature_names, fill_value=0)


def load_model(model_path: Path):
    with model_path.open("rb") as handle:
        return pickle.load(handle)


def score_existing_artifacts(x_full_test: pd.DataFrame, y_test: pd.Series) -> dict:
    print("\n" + "=" * 70)
    print("STEP 0 — Existing artifact verification on current split")
    print("=" * 70)

    raw_metrics = {}
    table_rows = []
    for key in ["RF baseline", "RF tuned", "XGB baseline", "XGB tuned"]:
        artifact = MODEL_ARTIFACTS[key]
        model = load_model(artifact["path"])
        feature_names = get_model_feature_names(model)
        aligned_test = align_feature_frame(x_full_test, feature_names)
        preds = model.predict(aligned_test)
        metrics = evaluate(y_test, preds, STEP0_LABELS[key])
        raw_metrics[key] = metrics
        table_rows.append(metrics_to_table_row(metrics))

    print_table("STEP 0 — Existing pkl artifact comparison", table_rows)
    best_rmse_key = min(raw_metrics, key=lambda key: raw_metrics[key]["RMSE"])
    print(f"\nBest held-out RMSE among existing artifacts: {best_rmse_key}")
    return raw_metrics


def run_rf_search(x_train: pd.DataFrame, y_train: pd.Series) -> tuple[GridSearchCV, pd.DataFrame]:
    print("\n" + "=" * 70)
    print("STEP 1 — Random Forest baseline-centered confirmation search")
    print("=" * 70)

    search = GridSearchCV(
        estimator=RandomForestRegressor(random_state=42, n_jobs=1),
        param_grid=RF_CONFIRMATION_GRID,
        scoring=SCORING,
        refit="rmse",
        cv=CV,
        n_jobs=-1,
        verbose=1,
        return_train_score=True,
    )
    search.fit(x_train, y_train)
    cv_df = pd.DataFrame(search.cv_results_).copy()
    cv_df["mean_cv_rmse"] = -cv_df["mean_test_rmse"]
    cv_df["mean_cv_mae"] = -cv_df["mean_test_mae"]
    cv_df["mean_cv_r2"] = cv_df["mean_test_r2"]
    cv_df.to_csv(MODELS_DIR / "rf_cv_results.csv", index=False)
    print(f"Best RF params: {search.best_params_}")
    print(f"Best RF CV RMSE: {-search.best_score_:,.2f}")
    return search, cv_df


def run_xgb_search(x_train: pd.DataFrame, y_train: pd.Series) -> tuple[RandomizedSearchCV, pd.DataFrame]:
    print("\n" + "=" * 70)
    print("STEP 2 — XGBoost retuning")
    print("=" * 70)

    search = RandomizedSearchCV(
        estimator=xgb.XGBRegressor(
            objective="reg:squarederror",
            random_state=42,
            verbosity=0,
            n_jobs=1,
        ),
        param_distributions=XGB_PARAM_DIST,
        n_iter=40,
        scoring=SCORING,
        refit="rmse",
        cv=CV,
        random_state=42,
        n_jobs=-1,
        verbose=1,
        return_train_score=True,
    )
    search.fit(x_train, y_train)
    cv_df = pd.DataFrame(search.cv_results_).copy()
    cv_df["mean_cv_rmse"] = -cv_df["mean_test_rmse"]
    cv_df["mean_cv_mae"] = -cv_df["mean_test_mae"]
    cv_df["mean_cv_r2"] = cv_df["mean_test_r2"]
    cv_df.to_csv(MODELS_DIR / "xgb_cv_results.csv", index=False)
    print(f"Best XGBoost params: {search.best_params_}")
    print(f"Best XGBoost CV RMSE: {-search.best_score_:,.2f}")
    return search, cv_df


def save_model(model, output_path: Path) -> None:
    with output_path.open("wb") as handle:
        pickle.dump(model, handle)
    print(f"Saved -> {output_path}")


def _heatmap(data: pd.DataFrame, x_col: str, y_col: str, title: str, output_path: Path) -> None:
    heat_df = data.copy()
    heat_df[x_col] = heat_df[x_col].map(str)
    heat_df[y_col] = heat_df[y_col].map(str)
    pivot = heat_df.pivot_table(index=y_col, columns=x_col, values="mean_cv_rmse", aggfunc="mean")

    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(pivot.values, aspect="auto", cmap="viridis")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_xlabel(x_col.replace("param_", ""))
    ax.set_ylabel(y_col.replace("param_", ""))
    ax.set_title(title)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Mean CV RMSE (PHP)")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved plot -> {output_path}")


def _scatter(data: pd.DataFrame, color_col: str, title: str, output_path: Path) -> None:
    scatter_df = data.sort_values("mean_cv_rmse", ascending=True).reset_index(drop=True).copy()
    scatter_df["rank"] = np.arange(1, len(scatter_df) + 1)
    color_values = pd.to_numeric(scatter_df[color_col], errors="coerce")

    fig, ax = plt.subplots(figsize=(8, 5))
    scatter = ax.scatter(
        scatter_df["rank"],
        scatter_df["mean_cv_rmse"],
        c=color_values,
        cmap="viridis",
        s=40,
        alpha=0.9,
    )
    ax.set_xlabel("Iteration rank by CV RMSE")
    ax.set_ylabel("Mean CV RMSE (PHP)")
    ax.set_title(title)
    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label(color_col.replace("param_", ""))
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved plot -> {output_path}")


def make_tuning_plots(rf_cv: pd.DataFrame, xgb_cv: pd.DataFrame) -> None:
    print("\n" + "=" * 70)
    print("STEP 3 — Regression tuning diagnostics")
    print("=" * 70)

    _heatmap(
        rf_cv,
        "param_n_estimators",
        "param_max_features",
        "RF mean CV RMSE — n_estimators × max_features",
        EDA_DIR / "rf_tuning_heatmap_nest_maxfeat.png",
    )
    _heatmap(
        rf_cv,
        "param_max_depth",
        "param_min_samples_leaf",
        "RF mean CV RMSE — max_depth × min_samples_leaf",
        EDA_DIR / "rf_tuning_heatmap_depth_leaf.png",
    )
    _scatter(
        rf_cv,
        "param_n_estimators",
        "RF CV RMSE by iteration rank",
        EDA_DIR / "rf_tuning_cv_scatter.png",
    )

    _heatmap(
        xgb_cv,
        "param_n_estimators",
        "param_learning_rate",
        "XGB mean CV RMSE — n_estimators × learning_rate",
        EDA_DIR / "xgb_tuning_heatmap_nest_lr.png",
    )
    _heatmap(
        xgb_cv,
        "param_max_depth",
        "param_subsample",
        "XGB mean CV RMSE — max_depth × subsample",
        EDA_DIR / "xgb_tuning_heatmap_depth_sub.png",
    )
    _scatter(
        xgb_cv,
        "param_learning_rate",
        "XGB CV RMSE by iteration rank",
        EDA_DIR / "xgb_tuning_cv_scatter.png",
    )


def refit_ols_benchmark(x_train: pd.DataFrame, x_test: pd.DataFrame, y_train: pd.Series, y_test: pd.Series) -> dict:
    print("\n" + "=" * 70)
    print("STEP 4 — OLS benchmark refit")
    print("=" * 70)

    x_train_sm = sm.add_constant(x_train, has_constant="add")
    x_test_sm = sm.add_constant(x_test, has_constant="add")
    for column in x_train_sm.columns:
        if column not in x_test_sm.columns:
            x_test_sm[column] = 0
    x_test_sm = x_test_sm[x_train_sm.columns]

    ols_model = sm.OLS(y_train, x_train_sm).fit()
    preds = ols_model.predict(x_test_sm)
    return evaluate(y_test, preds, "OLS")


def save_final_comparison(rows: list[dict]) -> None:
    comparison_df = pd.DataFrame(rows)
    comparison_df.to_csv(MODELS_DIR / "model_comparison_final.csv", index=False)
    print(f"Saved -> {MODELS_DIR / 'model_comparison_final.csv'}")
    print_table("STEP 5 — Final model comparison", rows)


def select_deployment_model(candidate_metrics: dict[str, dict]) -> tuple[str, dict, str]:
    best_r2 = max(metrics["R2"] for metrics in candidate_metrics.values())
    eligible = {
        key: metrics
        for key, metrics in candidate_metrics.items()
        if metrics["R2"] >= best_r2 - 0.02
    }
    selected_key = min(
        eligible,
        key=lambda key: (
            eligible[key]["RMSE"],
            eligible[key]["MAPE"],
            eligible[key]["MAE"],
        ),
    )
    selected_metrics = eligible[selected_key]
    reason = (
        f"Selected {selected_key} because it had the lowest held-out RMSE among models "
        f"within 0.02 R² of the best competitor."
    )
    return selected_key, selected_metrics, reason


def update_streamlit_app(winner_key: str) -> Path:
    artifact = MODEL_ARTIFACTS[winner_key]
    config_text = CONFIG_PATH.read_text()
    config_text, count_path = re.subn(
        r'^MODEL_PATH = .*$',
        f'MODEL_PATH = THESIS_DIR / "Models" / "{artifact["config_filename"]}"',
        config_text,
        flags=re.MULTILINE,
    )
    config_text, count_label = re.subn(
        r'^MODEL_LABEL = .*$',
        f'MODEL_LABEL = "{artifact["label"]}"',
        config_text,
        flags=re.MULTILINE,
    )
    if count_path != 1 or count_label != 1:
        raise RuntimeError("Could not update MODEL_PATH / MODEL_LABEL in config.py")
    CONFIG_PATH.write_text(config_text)

    streamlit_text = STREAMLIT_APP_PATH.read_text()
    if "Random Forest model" not in streamlit_text and "XGBoost model" not in streamlit_text:
        raise RuntimeError("Could not find the homepage model description in streamlit_app.py")
    streamlit_text = streamlit_text.replace("Random Forest model", f'{artifact["label"]} model', 1)
    streamlit_text = streamlit_text.replace("XGBoost model", f'{artifact["label"]} model', 1)
    STREAMLIT_APP_PATH.write_text(streamlit_text)
    return artifact["path"]


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    EDA_DIR.mkdir(parents=True, exist_ok=True)

    data = prepare_model_data()
    step0_metrics = score_existing_artifacts(data["X_full_test"], data["y_test"])

    rf_search, rf_cv = run_rf_search(data["X_full_train"], data["y_train"])
    rf_metrics = evaluate(data["y_test"], rf_search.best_estimator_.predict(data["X_full_test"]), "RF tuned")
    save_model(rf_search.best_estimator_, MODELS_DIR / "rf_tuned.pkl")

    xgb_search, xgb_cv = run_xgb_search(data["X_full_train"], data["y_train"])
    xgb_metrics = evaluate(data["y_test"], xgb_search.best_estimator_.predict(data["X_full_test"]), "XGB tuned")
    save_model(xgb_search.best_estimator_, MODELS_DIR / "xgb_tuned.pkl")

    make_tuning_plots(rf_cv, xgb_cv)

    ols_metrics = refit_ols_benchmark(
        data["X_ols_train"],
        data["X_ols_test"],
        data["y_train"],
        data["y_test"],
    )

    final_rows = [
        metrics_to_table_row(ols_metrics),
        metrics_to_table_row({**step0_metrics["RF baseline"], "Model": "RF baseline"}),
        metrics_to_table_row({**rf_metrics, "Model": "RF tuned"}),
        metrics_to_table_row({**step0_metrics["XGB baseline"], "Model": "XGB baseline"}),
        metrics_to_table_row({**xgb_metrics, "Model": "XGB tuned"}),
    ]
    save_final_comparison(final_rows)

    candidate_metrics = {
        "RF baseline": {**step0_metrics["RF baseline"], "Model": "RF baseline"},
        "RF tuned": {**rf_metrics, "Model": "RF tuned"},
        "XGB baseline": {**step0_metrics["XGB baseline"], "Model": "XGB baseline"},
        "XGB tuned": {**xgb_metrics, "Model": "XGB tuned"},
    }
    winner_key, winner_metrics, reason = select_deployment_model(candidate_metrics)
    winner_path = update_streamlit_app(winner_key)

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(reason)
    print(f"Selected deployment model: {winner_key}")
    print(f"Held-out RMSE: {winner_metrics['RMSE'] / 1_000_000:.2f} PHP M")
    print(f"Held-out R2: {winner_metrics['R2']:.4f}")
    print(f"Held-out MAPE: {winner_metrics['MAPE']:.2f}%")
    print(f"config.py now points to: {winner_path}")


if __name__ == "__main__":
    main()
