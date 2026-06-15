"""
tune_models_stratified.py
=========================
Per-stratum hyperparameter tuning + k-fold cross-validation reporting
for the residential property valuation thesis (Cebu market).

This script performs GridSearchCV for RandomForest and RandomizedSearchCV for XGBoost,
compares them with their baseline counterparts on held-out test data and via 5x3 RepeatedKFold
cross-validation, and deploys the config with the lowest k-fold MAPE mean.
"""

import os
import sys
import json
import pickle
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, RepeatedKFold, train_test_split
from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score

# Ensure we can import run_models_stratified from the same folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

from run_models_stratified import (
    build_features, evaluate, run_shap,
    STRATA, CBD_TOP2, ALL_CBD, TARGET,
    PROCESSED_DIR, MODELS_DIR, SHAP_DIR,
    RANDOM_STATE, TEST_SIZE,
)

# Reuse the tuning grids from tune_models.py verbatim
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


def main() -> None:
    print("=" * 80)
    print("STRATIFIED HYPERPARAMETER TUNING & K-FOLD CV REPORTING")
    print("=" * 80)

    # 1. Back up existing manifest
    manifest_path = os.path.join(MODELS_DIR, "deployment_manifest.json")
    if os.path.exists(manifest_path):
        backup_path = os.path.join(MODELS_DIR, "deployment_manifest.backup_pre_tuning.json")
        try:
            with open(manifest_path, "r") as fh:
                manifest_data = json.load(fh)
            with open(backup_path, "w") as fh:
                json.dump(manifest_data, fh, indent=2)
            print(f"Backed up deployment_manifest.json to {backup_path}")
        except Exception as e:
            print(f"Warning: Could not backup manifest: {e}")
            manifest_data = {}
    else:
        manifest_data = {}

    if "strata" not in manifest_data:
        manifest_data["strata"] = {}

    kfold_cv_rows = []
    summary_print_rows = []

    # Loop over STRATA: condo, houses, lot
    for stratum_key, cfg in STRATA.items():
        print("\n" + "=" * 78)
        print(f"STRATUM: {cfg['label']} ({cfg['csv']})")
        print("=" * 78)

        # 1. Load the stratum CSV
        csv_path = os.path.join(PROCESSED_DIR, cfg["csv"])
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df):,} rows")

        # Get features
        X_full, _, y, area = build_features(df, stratum_key)
        print(f"X_full features: {X_full.shape[1]}")

        # 2. Make the same held-out split as the baseline
        idx = np.arange(len(y))
        X_full_tr, X_full_te, y_tr, y_te, idx_tr, idx_te = train_test_split(
            X_full, y, idx, test_size=TEST_SIZE, random_state=RANDOM_STATE
        )
        area_te = area.to_numpy()[idx_te]
        print(f"Train split: {len(y_tr):,} | Test split: {len(y_te):,}")

        # Define CV
        cv = RepeatedKFold(n_splits=5, n_repeats=3, random_state=42)

        # 3. Tuning (train split only)
        # RF Tuning
        print(f"\n[RF Tuning] GridSearchCV on {len(y_tr)} rows...")
        rf_grid = GridSearchCV(
            estimator=RandomForestRegressor(random_state=42, n_jobs=1),
            param_grid=RF_CONFIRMATION_GRID,
            scoring="neg_root_mean_squared_error",
            cv=cv,
            refit=True,
            n_jobs=-1
        )
        rf_grid.fit(X_full_tr, y_tr)
        
        rf_cv_results_path = os.path.join(MODELS_DIR, f"rf_cv_results_{stratum_key}.csv")
        pd.DataFrame(rf_grid.cv_results_).to_csv(rf_cv_results_path, index=False)
        rf_best_params = rf_grid.best_params_
        rf_best_score = rf_grid.best_score_
        print(f"RF Best Params: {rf_best_params}")
        print(f"RF Best CV RMSE: {-rf_best_score:.6f}")

        # XGB Tuning
        print(f"\n[XGB Tuning] RandomizedSearchCV on {len(y_tr)} rows...")
        xgb_random = RandomizedSearchCV(
            estimator=xgb.XGBRegressor(
                objective="reg:squarederror",
                random_state=42,
                verbosity=0,
                n_jobs=1
            ),
            param_distributions=XGB_PARAM_DIST,
            n_iter=40,
            scoring="neg_root_mean_squared_error",
            cv=cv,
            refit=True,
            random_state=42,
            n_jobs=-1
        )
        xgb_random.fit(X_full_tr, y_tr)

        xgb_cv_results_path = os.path.join(MODELS_DIR, f"xgb_cv_results_{stratum_key}.csv")
        pd.DataFrame(xgb_random.cv_results_).to_csv(xgb_cv_results_path, index=False)
        xgb_best_params = xgb_random.best_params_
        xgb_best_score = xgb_random.best_score_
        print(f"XGB Best Params: {xgb_best_params}")
        print(f"XGB Best CV RMSE: {-xgb_best_score:.6f}")

        # 4. Define four candidate configs
        configs = {
            "RF baseline": RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1),
            "RF tuned": RandomForestRegressor(**rf_best_params, random_state=42, n_jobs=-1),
            "XGB baseline": xgb.XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=6, random_state=42, verbosity=0),
            "XGB tuned": xgb.XGBRegressor(**xgb_best_params, objective="reg:squarederror", random_state=42, verbosity=0)
        }

        # 5. HELD-OUT evaluation
        print("\n[Held-Out Test Set Performance]")
        heldout_results = {}
        for name, clf in configs.items():
            clf.fit(X_full_tr, y_tr)
            pred_te = clf.predict(X_full_te)
            heldout_results[name] = evaluate(y_te, pred_te, name, area_te)

        # 6. K-FOLD honest reporting (on full stratum data)
        print("\n[K-Fold Cross-Validation Performance (RepeatedKFold 5x3)]")
        kfold_metrics = {}
        for name, clf in configs.items():
            fold_mapes = []
            fold_mdapes = []
            fold_r2sqms = []

            for fold_idx, (train_idx, val_idx) in enumerate(cv.split(X_full)):
                X_tr_f, X_val_f = X_full.iloc[train_idx], X_full.iloc[val_idx]
                y_tr_f, y_val_f = y.iloc[train_idx], y.iloc[val_idx]
                area_val = area.iloc[val_idx].to_numpy()

                model_fold = clone(clf)
                model_fold.fit(X_tr_f, y_tr_f)
                pred_val_log = model_fold.predict(X_val_f)

                # Back-transform to price per sqm
                val_true_psqm = np.exp(y_val_f.to_numpy())
                val_pred_psqm = np.exp(pred_val_log)

                # Compute fold metrics
                ape = np.abs((val_true_psqm - val_pred_psqm) / val_true_psqm)
                mape = np.mean(ape) * 100
                mdape = np.median(ape) * 100
                r2_sqm = r2_score(val_true_psqm, val_pred_psqm)

                fold_mapes.append(mape)
                fold_mdapes.append(mdape)
                fold_r2sqms.append(r2_sqm)

            kfold_metrics[name] = {
                "kfold_MAPE_mean": float(np.mean(fold_mapes)),
                "kfold_MAPE_std": float(np.std(fold_mapes)),
                "kfold_MdAPE_mean": float(np.mean(fold_mdapes)),
                "kfold_MdAPE_std": float(np.std(fold_mdapes)),
                "kfold_R2sqm_mean": float(np.mean(fold_r2sqms)),
                "kfold_R2sqm_std": float(np.std(fold_r2sqms)),
            }
            print(f"  {name:<14} MAPE={kfold_metrics[name]['kfold_MAPE_mean']:6.2f}% ±{kfold_metrics[name]['kfold_MAPE_std']:5.2f}%  "
                  f"MdAPE={kfold_metrics[name]['kfold_MdAPE_mean']:6.2f}% ±{kfold_metrics[name]['kfold_MdAPE_std']:5.2f}%  "
                  f"R2(psqm)={kfold_metrics[name]['kfold_R2sqm_mean']:7.4f} ±{kfold_metrics[name]['kfold_R2sqm_std']:6.4f}")

        # 7. SELECTION (Decision 40c)
        chosen_name = min(configs.keys(), key=lambda name: kfold_metrics[name]["kfold_MAPE_mean"])
        print(f"\n>> Chosen deployed config: {chosen_name}")
        print(f"   K-Fold Mean MAPE: {kfold_metrics[chosen_name]['kfold_MAPE_mean']:.2f}% ± {kfold_metrics[chosen_name]['kfold_MAPE_std']:.2f}%")
        print(f"   Held-out MAPE:    {heldout_results[chosen_name]['MAPE']:.2f}%")

        # 8. DEPLOY (Decision 40d)
        deployed_model = clone(configs[chosen_name])
        deployed_model.fit(X_full, y)

        # Overwrite pkl
        model_pkl_path = os.path.join(MODELS_DIR, f"{stratum_key}_model.pkl")
        with open(model_pkl_path, "wb") as fh:
            pickle.dump(deployed_model, fh)
        print(f"Refit deployed model saved -> {model_pkl_path}")

        # Save tuned references (fit on train split)
        rf_tuned_path = os.path.join(MODELS_DIR, f"{stratum_key}_rf_tuned.pkl")
        with open(rf_tuned_path, "wb") as fh:
            pickle.dump(rf_grid.best_estimator_, fh)
        print(f"Saved tuned RF reference -> {rf_tuned_path}")

        xgb_tuned_path = os.path.join(MODELS_DIR, f"{stratum_key}_xgb_tuned.pkl")
        with open(xgb_tuned_path, "wb") as fh:
            pickle.dump(xgb_random.best_estimator_, fh)
        print(f"Saved tuned XGB reference -> {xgb_tuned_path}")

        # Regenerate SHAP on the refit deployed model
        family_short = "rf" if chosen_name.startswith("RF") else "xgb"
        print(f"Regenerating SHAP summary plot for {chosen_name}...")
        run_shap(deployed_model, X_full_te, stratum_key, family_short)

        # Write tuning_results_{stratum}.json
        tuning_results = {
            "rf_best_params": rf_best_params,
            "xgb_best_params": xgb_best_params,
            "rf_best_cv_rmse": float(-rf_best_score),
            "xgb_best_cv_rmse": float(-xgb_best_score),
            "chosen_deployed_config": chosen_name
        }
        tuning_results_path = os.path.join(MODELS_DIR, f"tuning_results_{stratum_key}.json")
        with open(tuning_results_path, "w") as fh:
            json.dump(tuning_results, fh, indent=2)
        print(f"Saved tuning results -> {tuning_results_path}")

        # Collect for CSV
        for name in configs.keys():
            kfold_cv_rows.append({
                "Stratum": cfg["label"],
                "Config": name,
                "heldout_MAPE": heldout_results[name]["MAPE"],
                "heldout_MdAPE": heldout_results[name]["MdAPE"],
                "heldout_R2_sqm": heldout_results[name]["R2_sqm"],
                "kfold_MAPE_mean": kfold_metrics[name]["kfold_MAPE_mean"],
                "kfold_MAPE_std": kfold_metrics[name]["kfold_MAPE_std"],
                "kfold_MdAPE_mean": kfold_metrics[name]["kfold_MdAPE_mean"],
                "kfold_MdAPE_std": kfold_metrics[name]["kfold_MdAPE_std"],
                "kfold_R2sqm_mean": kfold_metrics[name]["kfold_R2sqm_mean"],
                "kfold_R2sqm_std": kfold_metrics[name]["kfold_R2sqm_std"],
                "deployed": (name == chosen_name)
            })

        summary_print_rows.append({
            "Stratum": cfg["label"],
            "Deployed Config": chosen_name,
            "K-Fold Mean MAPE": f"{kfold_metrics[chosen_name]['kfold_MAPE_mean']:.2f}% ± {kfold_metrics[chosen_name]['kfold_MAPE_std']:.2f}%",
            "K-Fold Mean MdAPE": f"{kfold_metrics[chosen_name]['kfold_MdAPE_mean']:.2f}% ± {kfold_metrics[chosen_name]['kfold_MdAPE_std']:.2f}%",
            "Held-out MAPE": f"{heldout_results[chosen_name]['MAPE']:.2f}%",
            "Held-out MdAPE": f"{heldout_results[chosen_name]['MdAPE']:.2f}%"
        })

        # Update manifest dict for this stratum
        if stratum_key not in manifest_data["strata"]:
            manifest_data["strata"][stratum_key] = {}
        
        stratum_manifest = manifest_data["strata"][stratum_key]
        stratum_manifest["deployed_config"] = chosen_name
        stratum_manifest["best_params"] = rf_best_params if chosen_name.startswith("RF") else xgb_best_params
        stratum_manifest["kfold_metrics"] = kfold_metrics[chosen_name]
        stratum_manifest["selection_basis"] = "lowest k-fold mean MAPE (RepeatedKFold 5x3) among {RF,XGB}x{baseline,tuned}"
        
        # Sync the standard deployment manifest keys to match new deployment
        stratum_manifest["label"] = cfg["label"]
        stratum_manifest["n_rows"] = len(df)
        stratum_manifest["n_test"] = len(y_te)
        stratum_manifest["deployed_family"] = "Random Forest" if chosen_name.startswith("RF") else "XGBoost"
        stratum_manifest["deployed_metrics"] = {
            "MAPE": heldout_results[chosen_name]["MAPE"],
            "MdAPE": heldout_results[chosen_name]["MdAPE"],
            "R2_sqm": heldout_results[chosen_name]["R2_sqm"],
            "MAE_sqm": heldout_results[chosen_name]["MAE_sqm"],
            "R2_total": heldout_results[chosen_name]["R2_total"],
            "MAE_total": heldout_results[chosen_name]["MAE_total"]
        }
        stratum_manifest["model_file"] = f"{stratum_key}_model.pkl"
        stratum_manifest["n_features"] = len(X_full.columns)
        stratum_manifest["features"] = list(X_full.columns)

    # Write kfold_cv_stratified.csv
    kfold_csv_path = os.path.join(MODELS_DIR, "kfold_cv_stratified.csv")
    pd.DataFrame(kfold_cv_rows).to_csv(kfold_csv_path, index=False)
    print(f"\nSaved cross-stratum CV comparison to {kfold_csv_path}")

    # Write deployment_manifest.json
    with open(manifest_path, "w") as fh:
        json.dump(manifest_data, fh, indent=2)
    print(f"Updated deployment manifest -> {manifest_path}")

    # Print final summary table
    print("\n" + "=" * 80)
    print("FINAL SUMMARY TABLE")
    print("=" * 80)
    summary_df = pd.DataFrame(summary_print_rows)
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
