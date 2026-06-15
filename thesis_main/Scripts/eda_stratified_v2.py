"""Full pre-modeling EDA and diagnostics for the stratified Metro Cebu ABTs."""

from __future__ import annotations

from pathlib import Path
from textwrap import fill

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from matplotlib.lines import Line2D
from scipy import stats
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import OLSInfluence, variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson


STRATA = {
    "Condo": "abt_condo.csv",
    "Houses": "abt_houses.csv",
    "Lot": "abt_lot.csv",
}

# OLS feature spec — Decision 32 trim:
#   - Top 2 CBD distances per stratum (by |Spearman rho| with price_per_sqm)
#   - mcrai_composite dropped (perfect linear combination of education + grocery + recreation)
#   - bir_zonal_rr_median dropped (log-log spec keeps only the log)
FEATURE_COLS = {
    "Condo": [
        "area_sqm",
        "bedrooms",
        "bathrooms",
        "bedrooms_imputed",
        "bathrooms_imputed",
        "dist_cebu_business_park_m",
        "dist_talisay_tabunok_m",
        "dist_to_trunk_road_m",
        "dist_to_primary_road_m",
        "mcrai_education",
        "mcrai_grocery",
        "mcrai_health",
        "mcrai_hospitals",
        "mcrai_recreation",
        "mcrai_security",
        "mcrai_tourism",
        "mcrai_retail_density",
        "bir_zonal_rr_log",
        "bir_zonal_cr_median",
        "is_mactan_island",
        "spatial_lag_price",
    ],
    "Houses": [
        "area_sqm",
        "bedrooms",
        "bathrooms",
        "bedrooms_imputed",
        "bathrooms_imputed",
        "dist_cebu_business_park_m",
        "dist_mandaue_cbd_m",
        "dist_to_trunk_road_m",
        "dist_to_primary_road_m",
        "mcrai_education",
        "mcrai_grocery",
        "mcrai_health",
        "mcrai_hospitals",
        "mcrai_recreation",
        "mcrai_security",
        "mcrai_tourism",
        "mcrai_retail_density",
        "bir_zonal_rr_log",
        "bir_zonal_cr_median",
        "is_mactan_island",
        "spatial_lag_price",
    ],
    "Lot": [
        "area_sqm",
        "dist_cebu_business_park_m",
        "dist_mandaue_cbd_m",
        "dist_to_trunk_road_m",
        "dist_to_primary_road_m",
        "mcrai_education",
        "mcrai_grocery",
        "mcrai_health",
        "mcrai_hospitals",
        "mcrai_recreation",
        "mcrai_security",
        "mcrai_tourism",
        "mcrai_retail_density",
        "bir_zonal_rr_log",
        "bir_zonal_cr_median",
        "is_mactan_island",
        "spatial_lag_price",
    ],
}

# Tree-model spec — retains full feature set (VIF irrelevant for tree models).
# Defined here for reference; not used in this EDA script.
FEATURE_COLS_TREE = {
    "Condo": [
        "area_sqm",
        "bedrooms",
        "bathrooms",
        "bedrooms_imputed",
        "bathrooms_imputed",
        "dist_cebu_business_park_m",
        "dist_mandaue_cbd_m",
        "dist_mactan_cbd_m",
        "dist_srp_m",
        "dist_talisay_tabunok_m",
        "dist_consolacion_m",
        "dist_naga_city_m",
        "dist_airport_m",
        "dist_to_trunk_road_m",
        "dist_to_primary_road_m",
        "mcrai_education",
        "mcrai_grocery",
        "mcrai_health",
        "mcrai_hospitals",
        "mcrai_recreation",
        "mcrai_security",
        "mcrai_tourism",
        "mcrai_retail_density",
        "mcrai_composite",
        "bir_zonal_rr_median",
        "bir_zonal_rr_log",
        "bir_zonal_cr_median",
        "is_mactan_island",
        "spatial_lag_price",
    ],
    "Houses": [
        "area_sqm",
        "bedrooms",
        "bathrooms",
        "bedrooms_imputed",
        "bathrooms_imputed",
        "dist_cebu_business_park_m",
        "dist_mandaue_cbd_m",
        "dist_mactan_cbd_m",
        "dist_srp_m",
        "dist_talisay_tabunok_m",
        "dist_consolacion_m",
        "dist_naga_city_m",
        "dist_airport_m",
        "dist_to_trunk_road_m",
        "dist_to_primary_road_m",
        "mcrai_education",
        "mcrai_grocery",
        "mcrai_health",
        "mcrai_hospitals",
        "mcrai_recreation",
        "mcrai_security",
        "mcrai_tourism",
        "mcrai_retail_density",
        "mcrai_composite",
        "bir_zonal_rr_median",
        "bir_zonal_rr_log",
        "bir_zonal_cr_median",
        "is_mactan_island",
        "spatial_lag_price",
    ],
    "Lot": [
        "area_sqm",
        "dist_cebu_business_park_m",
        "dist_mandaue_cbd_m",
        "dist_mactan_cbd_m",
        "dist_srp_m",
        "dist_talisay_tabunok_m",
        "dist_consolacion_m",
        "dist_naga_city_m",
        "dist_airport_m",
        "dist_to_trunk_road_m",
        "dist_to_primary_road_m",
        "mcrai_education",
        "mcrai_grocery",
        "mcrai_health",
        "mcrai_hospitals",
        "mcrai_recreation",
        "mcrai_security",
        "mcrai_tourism",
        "mcrai_retail_density",
        "mcrai_composite",
        "bir_zonal_rr_median",
        "bir_zonal_rr_log",
        "bir_zonal_cr_median",
        "is_mactan_island",
        "spatial_lag_price",
    ],
}

TARGET = "price_per_sqm"
LOG_TARGET = "log_price"

SCRIPT_DIR = Path(__file__).resolve().parent
THESIS_DIR = SCRIPT_DIR.parent
DATA_DIR = THESIS_DIR / "Data" / "processed"
PLOTS_DIR = THESIS_DIR / "EDA" / "plots"
TABLES_DIR = THESIS_DIR / "EDA" / "tables"

SECTION_DIRS = {
    "01_target": PLOTS_DIR / "01_target",
    "02_geographic": PLOTS_DIR / "02_geographic",
    "03_features": PLOTS_DIR / "03_features",
    "04_correlation": PLOTS_DIR / "04_correlation",
    "05_multicollinearity": PLOTS_DIR / "05_multicollinearity",
    "06_ols_residuals": PLOTS_DIR / "06_ols_residuals",
    "07_outliers": PLOTS_DIR / "07_outliers",
    "08_mcrai": PLOTS_DIR / "08_mcrai",
}

VIF_EXCLUDE = {"bedrooms_imputed", "bathrooms_imputed", "is_mactan_island"}
MCRAI_COLS = [
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
LGU_ORDER = [
    "Cebu City",
    "Mandaue City",
    "Lapu-Lapu City",
    "Talisay City",
    "Minglanilla",
    "Consolacion",
]
PALETTE = {"Condo": "#4c78a8", "Houses": "#f58518", "Lot": "#54a24b"}
WRITTEN_FILES: list[Path] = []


def ensure_directories() -> None:
    for path in SECTION_DIRS.values():
        path.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)


def configure_plotting() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    sns.set_theme(style="whitegrid")
    plt.rcParams["figure.dpi"] = 150


def section_header(title: str) -> None:
    print(f"\n{'=' * 88}")
    print(title)
    print(f"{'=' * 88}")


def save_figure(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=150, format="png")
    plt.close(fig)
    WRITTEN_FILES.append(path)
    print(f"Saved -> {path}")


def save_table(frame: pd.DataFrame, path: Path, *, json_path: Path | None = None) -> None:
    frame.to_csv(path, index=False)
    WRITTEN_FILES.append(path)
    print(f"Saved -> {path}")
    if json_path is not None:
        frame.to_json(json_path, orient="records", indent=2)
        WRITTEN_FILES.append(json_path)
        print(f"Saved -> {json_path}")


def print_written_files() -> None:
    section_header("FILES WRITTEN")
    for path in WRITTEN_FILES:
        print(path)


def set_diagnostic_title(ax: plt.Axes, title: str, subtitle: str) -> None:
    ax.set_title(f"{title}\n{fill(subtitle, width=110)}", pad=12, fontsize=12)


def load_strata() -> dict[str, pd.DataFrame]:
    strata_frames: dict[str, pd.DataFrame] = {}
    for stratum, filename in STRATA.items():
        path = DATA_DIR / filename
        df = pd.read_csv(path)
        strata_frames[stratum] = df.copy()
        print(f"Loaded {stratum:<6} -> {path} ({len(df):,} rows x {df.shape[1]} cols)")
    return strata_frames


def combined_frame(strata_frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    combined = pd.concat(
        [frame.assign(_stratum_name=stratum) for stratum, frame in strata_frames.items()],
        ignore_index=True,
    )
    combined["_stratum_name"] = pd.Categorical(
        combined["_stratum_name"],
        categories=list(STRATA.keys()),
        ordered=True,
    )
    return combined


def format_float_table(frame: pd.DataFrame, digits: int = 4) -> str:
    return frame.to_string(
        index=False,
        float_format=lambda value: f"{value:,.{digits}f}" if pd.notna(value) else "nan",
    )


def prepare_ols_subset(df: pd.DataFrame, stratum: str) -> pd.DataFrame:
    required_cols = FEATURE_COLS[stratum] + [LOG_TARGET]
    return df.dropna(subset=required_cols).copy()


def compute_spearman_table(df: pd.DataFrame, stratum: str) -> pd.DataFrame:
    rows = []
    for feature in FEATURE_COLS[stratum]:
        pair = df[[feature, TARGET]].dropna()
        if len(pair) < 3 or pair[feature].nunique() < 2:
            rho = np.nan
            p_value = np.nan
        else:
            rho, p_value = stats.spearmanr(pair[feature], pair[TARGET], nan_policy="omit")
        rows.append(
            {
                "feature": feature,
                "spearman_rho": rho,
                "p_value": p_value,
                "abs_rho": abs(rho) if pd.notna(rho) else np.nan,
            }
        )

    return (
        pd.DataFrame(rows)
        .sort_values(by=["abs_rho", "feature"], ascending=[False, True], na_position="last")
        .reset_index(drop=True)
    )


def compute_vif_table(df: pd.DataFrame, stratum: str) -> pd.DataFrame:
    vif_features = [feature for feature in FEATURE_COLS[stratum] if feature not in VIF_EXCLUDE]
    design = df[vif_features].astype(float)
    design = sm.add_constant(design, has_constant="add")

    rows = []
    for index, feature in enumerate(design.columns):
        if feature == "const":
            continue
        value = variance_inflation_factor(design.values, index)
        rows.append({"feature": feature, "vif": float(value)})

    return pd.DataFrame(rows).sort_values(by="vif", ascending=False).reset_index(drop=True)


def fit_ols(df: pd.DataFrame, stratum: str):
    x = df[FEATURE_COLS[stratum]].astype(float)
    y = df[LOG_TARGET].astype(float)
    x = sm.add_constant(x, has_constant="add")
    model = sm.OLS(y, x)
    results = model.fit(cov_type="HC3")
    return model, results


def section1_target_distribution(strata_frames: dict[str, pd.DataFrame]) -> None:
    section_header("SECTION 1 - TARGET DISTRIBUTION")
    for stratum, df in strata_frames.items():
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))

        sns.histplot(df[TARGET].dropna(), kde=True, ax=axes[0], color=PALETTE[stratum])
        axes[0].set_title(f"{stratum} - price_per_sqm distribution")
        axes[0].set_xlabel("price_per_sqm (PHP/sqm)")
        axes[0].set_ylabel("Count")

        sns.histplot(df[LOG_TARGET].dropna(), kde=True, ax=axes[1], color=PALETTE[stratum])
        axes[1].set_title(f"{stratum} - log_price distribution")
        axes[1].set_xlabel("log_price from price_per_sqm (PHP/sqm)")
        axes[1].set_ylabel("Count")

        save_figure(fig, SECTION_DIRS["01_target"] / f"{stratum}_price_distribution.png")

        q25 = df[TARGET].quantile(0.25)
        q75 = df[TARGET].quantile(0.75)
        shapiro_stat, shapiro_p = stats.shapiro(df[LOG_TARGET].dropna())
        normality = "appears approximately normal" if shapiro_p >= 0.05 else "does not appear normal"
        summary = pd.DataFrame(
            [
                {
                    "stratum": stratum,
                    "n": len(df),
                    "mean": df[TARGET].mean(),
                    "median": df[TARGET].median(),
                    "std": df[TARGET].std(ddof=1),
                    "skewness": df[TARGET].skew(),
                    "kurtosis": df[TARGET].kurtosis(),
                    "min": df[TARGET].min(),
                    "max": df[TARGET].max(),
                    "iqr": q75 - q25,
                    "log_price_shapiro_stat": shapiro_stat,
                    "log_price_shapiro_p": shapiro_p,
                    "log_price_normality": normality,
                }
            ]
        )
        save_table(
            summary,
            TABLES_DIR / f"eda_01_target_summary_{stratum.lower()}.csv",
            json_path=TABLES_DIR / f"eda_01_target_summary_{stratum.lower()}.json",
        )

        print(f"\n[{stratum}] price_per_sqm summary")
        print(f"n: {len(df):,}")
        print(f"mean: {df[TARGET].mean():,.4f}")
        print(f"median: {df[TARGET].median():,.4f}")
        print(f"std: {df[TARGET].std(ddof=1):,.4f}")
        print(f"skewness: {df[TARGET].skew():,.4f}")
        print(f"kurtosis: {df[TARGET].kurtosis():,.4f}")
        print(f"min: {df[TARGET].min():,.4f}")
        print(f"max: {df[TARGET].max():,.4f}")
        print(f"IQR: {(q75 - q25):,.4f}")
        print(
            f"Shapiro-Wilk on log_price: statistic={shapiro_stat:,.4f}, "
            f"p-value={shapiro_p:,.6f} -> {normality} at alpha=0.05"
        )

    combined = combined_frame(strata_frames)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(
        data=combined,
        x="_stratum_name",
        y=TARGET,
        order=list(STRATA.keys()),
        palette=PALETTE,
        ax=ax,
        showfliers=False,
    )
    ax.set_yscale("log")
    ax.set_title("All Strata - price_per_sqm boxplot")
    ax.set_xlabel("Stratum")
    ax.set_ylabel("price_per_sqm (PHP/sqm, log scale)")
    save_figure(fig, SECTION_DIRS["01_target"] / "all_strata_price_boxplot.png")


def section2_geographic_spread(strata_frames: dict[str, pd.DataFrame]) -> None:
    section_header("SECTION 2 - GEOGRAPHIC SPREAD")
    combined = combined_frame(strata_frames)

    count_table = pd.crosstab(combined["city"], combined["_stratum_name"]).reindex(LGU_ORDER, fill_value=0)
    count_table = count_table.reindex(columns=list(STRATA.keys()), fill_value=0)
    save_table(count_table.reset_index(), TABLES_DIR / "eda_02_lgu_stratum_counts.csv")
    print("\nRow count by city x stratum")
    print(count_table.to_string())

    median_table = (
        combined.pivot_table(index="city", columns="_stratum_name", values=TARGET, aggfunc="median")
        .reindex(LGU_ORDER)
        .reindex(columns=list(STRATA.keys()))
    )
    save_table(median_table.reset_index(), TABLES_DIR / "eda_02_lgu_stratum_median_price_per_sqm.csv")
    print("\nMedian price_per_sqm by city x stratum")
    print(format_float_table(median_table.reset_index(), digits=2))

    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
    for ax, stratum in zip(axes, STRATA.keys()):
        subset = strata_frames[stratum].copy()
        city_order = [city for city in LGU_ORDER if city in subset["city"].unique()]
        sns.boxplot(
            data=subset,
            x="city",
            y=TARGET,
            order=city_order,
            color=PALETTE[stratum],
            showfliers=False,
            ax=ax,
        )
        ax.set_yscale("log")
        ax.set_title(f"{stratum} - price_per_sqm by city")
        ax.set_xlabel("City")
        ax.set_ylabel("price_per_sqm (PHP/sqm, log scale)")
        ax.tick_params(axis="x", rotation=35)
    save_figure(fig, SECTION_DIRS["02_geographic"] / "price_by_lgu_faceted.png")

    thin = count_table.stack().reset_index(name="rows")
    thin.columns = ["city", "stratum", "rows"]
    thin = thin[thin["rows"] < 20]
    save_table(thin, TABLES_DIR / "eda_02_thin_lgu_cells.csv")
    if thin.empty:
        print("\nNo LGU thin-stratum risk flags (<20 rows).")
    else:
        print("\nThin-stratum risk flags (<20 rows)")
        print(thin.to_string(index=False))


def section3_feature_distributions(strata_frames: dict[str, pd.DataFrame]) -> None:
    section_header("SECTION 3 - PHYSICAL FEATURE DISTRIBUTIONS")
    for stratum, df in strata_frames.items():
        summary = pd.DataFrame(
            {
                "feature": FEATURE_COLS[stratum],
                "mean": [df[col].mean() for col in FEATURE_COLS[stratum]],
                "median": [df[col].median() for col in FEATURE_COLS[stratum]],
                "std": [df[col].std(ddof=1) for col in FEATURE_COLS[stratum]],
                "min": [df[col].min() for col in FEATURE_COLS[stratum]],
                "max": [df[col].max() for col in FEATURE_COLS[stratum]],
                "pct_null": [df[col].isna().mean() * 100 for col in FEATURE_COLS[stratum]],
            }
        )
        save_table(summary, TABLES_DIR / f"eda_03_feature_summary_{stratum.lower()}.csv")
        print(f"\n[{stratum}] feature summary")
        print(format_float_table(summary, digits=4))

        fig, ax = plt.subplots(figsize=(12, 6))
        sns.histplot(df["area_sqm"].dropna(), kde=True, ax=ax, color=PALETTE[stratum])
        ax.set_title(f"{stratum} - area_sqm distribution")
        ax.set_xlabel("area_sqm")
        ax.set_ylabel("Count")
        save_figure(fig, SECTION_DIRS["03_features"] / f"{stratum}_area_distribution.png")

        if stratum in {"Condo", "Houses"}:
            fig, ax = plt.subplots(figsize=(12, 6))
            bedroom_counts = df["bedrooms"].dropna().round().astype(int)
            sns.countplot(x=bedroom_counts, ax=ax, color=PALETTE[stratum])
            ax.set_title(f"{stratum} - bedrooms distribution")
            ax.set_xlabel("bedrooms")
            ax.set_ylabel("Count")
            save_figure(fig, SECTION_DIRS["03_features"] / f"{stratum}_bedrooms_distribution.png")

            fig, ax = plt.subplots(figsize=(12, 6))
            bathroom_counts = df["bathrooms"].dropna().round().astype(int)
            sns.countplot(x=bathroom_counts, ax=ax, color=PALETTE[stratum])
            ax.set_title(f"{stratum} - bathrooms distribution")
            ax.set_xlabel("bathrooms")
            ax.set_ylabel("Count")
            save_figure(fig, SECTION_DIRS["03_features"] / f"{stratum}_bathrooms_distribution.png")


def section4_correlation_analysis(strata_frames: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    section_header("SECTION 4 - CORRELATION ANALYSIS")
    spearman_tables: dict[str, pd.DataFrame] = {}

    for stratum, df in strata_frames.items():
        spearman_table = compute_spearman_table(df, stratum)
        spearman_tables[stratum] = spearman_table
        save_table(
            spearman_table,
            TABLES_DIR / f"eda_04_spearman_vs_price_{stratum.lower()}.csv",
            json_path=TABLES_DIR / f"eda_04_spearman_vs_price_{stratum.lower()}.json",
        )

        print(f"\n[{stratum}] Spearman rho vs price_per_sqm")
        print(format_float_table(spearman_table, digits=4))

        plot_table = spearman_table.dropna(subset=["spearman_rho"]).sort_values("spearman_rho")
        fig, ax = plt.subplots(figsize=(12, 10))
        colors = ["#2ca02c" if value >= 0 else "#d62728" for value in plot_table["spearman_rho"]]
        ax.barh(plot_table["feature"], plot_table["spearman_rho"], color=colors)
        ax.axvline(0, color="black", linewidth=1)
        ax.set_title(f"{stratum} - Spearman rho vs price_per_sqm")
        ax.set_xlabel("Spearman rho")
        ax.set_ylabel("Feature")
        save_figure(fig, SECTION_DIRS["04_correlation"] / f"{stratum}_spearman_vs_price.png")

        heatmap_df = df[FEATURE_COLS[stratum]].corr(method="spearman")
        save_table(
            heatmap_df.reset_index().rename(columns={"index": "feature"}),
            TABLES_DIR / f"eda_04_spearman_feature_matrix_{stratum.lower()}.csv",
        )
        fig, ax = plt.subplots(figsize=(16, 14))
        sns.heatmap(
            heatmap_df,
            cmap="coolwarm",
            center=0,
            annot=True,
            fmt=".2f",
            linewidths=0.4,
            cbar_kws={"label": "Spearman rho"},
            ax=ax,
        )
        ax.set_title(f"{stratum} - feature Spearman correlation heatmap")
        save_figure(fig, SECTION_DIRS["04_correlation"] / f"{stratum}_feature_correlation_heatmap.png")

    return spearman_tables


def section5_multicollinearity(strata_frames: dict[str, pd.DataFrame]) -> tuple[dict[str, pd.DataFrame], dict[str, list[str]]]:
    section_header("SECTION 5 - MULTICOLLINEARITY (VIF)")
    vif_tables: dict[str, pd.DataFrame] = {}
    vif_flags: dict[str, list[str]] = {}

    for stratum, df in strata_frames.items():
        ols_ready = prepare_ols_subset(df, stratum)
        vif_table = compute_vif_table(ols_ready, stratum)
        vif_tables[stratum] = vif_table
        vif_flags[stratum] = vif_table.loc[vif_table["vif"] > 5, "feature"].tolist()
        save_table(
            vif_table,
            TABLES_DIR / f"eda_05_vif_{stratum.lower()}.csv",
            json_path=TABLES_DIR / f"eda_05_vif_{stratum.lower()}.json",
        )

        print(f"\n[{stratum}] VIF table")
        print(format_float_table(vif_table, digits=4))

        moderate = vif_table[vif_table["vif"] > 5]
        severe = vif_table[vif_table["vif"] > 10]
        if not moderate.empty:
            print(f"Warning: {stratum} features with VIF > 5")
            print(format_float_table(moderate, digits=4))
        if not severe.empty:
            print(f"Critical warning: {stratum} features with VIF > 10")
            print(format_float_table(severe, digits=4))

        fig, ax = plt.subplots(figsize=(12, 8))
        plot_table = vif_table.sort_values("vif")
        ax.barh(plot_table["feature"], plot_table["vif"], color=PALETTE[stratum])
        ax.axvline(5, color="red", linestyle="--", linewidth=1.2)
        ax.axvline(10, color="red", linestyle=":", linewidth=1.2)
        ax.set_title(f"{stratum} - Variance Inflation Factors")
        ax.set_xlabel("VIF")
        ax.set_ylabel("Feature")
        ax.legend(
            handles=[
                Line2D([0], [0], color="red", linestyle="--", linewidth=1.2, label="VIF = 5: moderate collinearity flag"),
                Line2D([0], [0], color="red", linestyle=":", linewidth=1.2, label="VIF = 10: severe collinearity flag"),
            ],
            title="Reference lines",
            loc="lower right",
            frameon=True,
        )
        save_figure(fig, SECTION_DIRS["05_multicollinearity"] / f"{stratum}_vif.png")

    return vif_tables, vif_flags


def section6_ols_and_residuals(
    strata_frames: dict[str, pd.DataFrame],
) -> tuple[dict[str, dict[str, object]], dict[str, pd.DataFrame]]:
    section_header("Section 6 - OLS Baseline + Residual Diagnostics (HC3 robust SE)")
    diagnostics: dict[str, dict[str, object]] = {}
    ols_ready_frames: dict[str, pd.DataFrame] = {}
    diagnostic_rows: list[pd.DataFrame] = []

    for stratum, df in strata_frames.items():
        ols_ready = prepare_ols_subset(df, stratum)
        ols_ready_frames[stratum] = ols_ready
        model, results = fit_ols(ols_ready, stratum)
        influence = OLSInfluence(results)

        residuals = results.resid
        fitted = results.fittedvalues
        standardized = influence.resid_studentized_internal
        sqrt_abs_standardized = np.sqrt(np.abs(standardized))

        print(f"\n[{stratum}] OLS summary")
        print(results.summary())
        conf_int = results.conf_int()
        coef_table = pd.DataFrame(
            {
                "term": results.params.index,
                "coef": results.params.values,
                "robust_se_hc3": results.bse.values,
                "z_value": results.tvalues.values,
                "p_value": results.pvalues.values,
                "ci_lower": conf_int[0].values,
                "ci_upper": conf_int[1].values,
            }
        )
        save_table(
            coef_table,
            TABLES_DIR / f"eda_06_ols_coefficients_{stratum.lower()}.csv",
            json_path=TABLES_DIR / f"eda_06_ols_coefficients_{stratum.lower()}.json",
        )

        fig, ax = plt.subplots(figsize=(12, 6))
        sns.scatterplot(x=fitted, y=residuals, ax=ax, color=PALETTE[stratum], s=40, alpha=0.7)
        sns.regplot(
            x=fitted,
            y=residuals,
            lowess=True,
            scatter=False,
            line_kws={"color": "black", "linewidth": 1.5},
            ax=ax,
        )
        ax.axhline(0, color="red", linestyle="--", linewidth=1.2)
        set_diagnostic_title(
            ax,
            f"{stratum} - residuals vs fitted",
            "Ideal: random scatter around zero. Curved trend = model misspecification; funnel shape = heteroscedasticity.",
        )
        ax.set_xlabel("Fitted Values (OLS-predicted log_price)")
        ax.set_ylabel("Residuals (observed − predicted log_price)")
        ax.legend(
            handles=[
                Line2D([0], [0], color="black", linewidth=1.5, label="LOWESS trend"),
                Line2D([0], [0], color="red", linestyle="--", linewidth=1.2, label="Zero residual line"),
            ],
            loc="upper right",
        )
        save_figure(fig, SECTION_DIRS["06_ols_residuals"] / f"{stratum}_residuals_vs_fitted.png")

        fig, ax = plt.subplots(figsize=(12, 6))
        (theoretical_quantiles, sample_quantiles), qq_fit = stats.probplot(residuals, dist="norm")
        slope, intercept, _ = qq_fit
        ax.scatter(theoretical_quantiles, sample_quantiles, color=PALETTE[stratum], s=25, alpha=0.8)
        ax.plot(
            theoretical_quantiles,
            slope * theoretical_quantiles + intercept,
            color="red",
            linestyle="--",
            linewidth=1.2,
            label="y=x reference (perfect normality)",
        )
        set_diagnostic_title(
            ax,
            f"{stratum} - residual Q-Q plot",
            "Points on the line = residuals are normally distributed. Curved tails = non-normal (heavy/light tails).",
        )
        ax.set_xlabel("Theoretical Quantiles (standard normal distribution)")
        ax.set_ylabel("Sample Quantiles (OLS residuals)")
        ax.legend(
            handles=[
                Line2D(
                    [0],
                    [0],
                    color="red",
                    linestyle="--",
                    linewidth=1.2,
                    label="y=x reference (perfect normality)",
                )
            ],
            loc="lower right",
        )
        save_figure(fig, SECTION_DIRS["06_ols_residuals"] / f"{stratum}_qq_plot.png")

        fig, ax = plt.subplots(figsize=(12, 6))
        sns.scatterplot(x=fitted, y=sqrt_abs_standardized, ax=ax, color=PALETTE[stratum], s=40, alpha=0.7)
        sns.regplot(
            x=fitted,
            y=sqrt_abs_standardized,
            lowess=True,
            scatter=False,
            line_kws={"color": "black", "linewidth": 1.5},
            ax=ax,
        )
        set_diagnostic_title(
            ax,
            f"{stratum} - scale-location",
            "Horizontal trend = homoscedastic (constant residual variance). Upward slope = heteroscedasticity.",
        )
        ax.set_xlabel("Fitted Values (OLS-predicted log_price)")
        ax.set_ylabel("√|Standardized Residuals|")
        ax.legend(
            handles=[Line2D([0], [0], color="black", linewidth=1.5, label="LOWESS trend")],
            loc="upper right",
        )
        save_figure(fig, SECTION_DIRS["06_ols_residuals"] / f"{stratum}_scale_location.png")

        bp_lm, bp_lm_p, bp_f, bp_f_p = het_breuschpagan(residuals, model.exog)
        jb_stat, jb_p = stats.jarque_bera(residuals)
        dw_stat = durbin_watson(residuals)

        bp_interpretation = "heteroscedastic" if bp_lm_p < 0.05 else "no strong heteroscedasticity signal"
        jb_interpretation = "non-normal residuals" if jb_p < 0.05 else "residuals approximately normal"
        if dw_stat < 1.5:
            dw_interpretation = "possible positive autocorrelation"
        elif dw_stat > 2.5:
            dw_interpretation = "possible negative autocorrelation"
        else:
            dw_interpretation = "near 2, no strong autocorrelation signal"

        print(
            f"Breusch-Pagan: LM={bp_lm:,.4f}, p-value={bp_lm_p:,.6f}, "
            f"F={bp_f:,.4f}, F p-value={bp_f_p:,.6f} -> {bp_interpretation}"
        )
        print(
            f"Jarque-Bera: statistic={jb_stat:,.4f}, p-value={jb_p:,.6f} -> {jb_interpretation}"
        )
        print(f"Durbin-Watson: {dw_stat:,.4f} -> {dw_interpretation}")
        diagnostic_table = pd.DataFrame(
            [
                {
                    "stratum": stratum,
                    "n_ols": len(ols_ready),
                    "ols_feature_count": len(FEATURE_COLS[stratum]),
                    "r_squared": results.rsquared,
                    "adj_r_squared": results.rsquared_adj,
                    "aic": results.aic,
                    "bic": results.bic,
                    "breusch_pagan_lm": bp_lm,
                    "breusch_pagan_lm_p_value": bp_lm_p,
                    "breusch_pagan_f": bp_f,
                    "breusch_pagan_f_p_value": bp_f_p,
                    "breusch_pagan_interpretation": bp_interpretation,
                    "jarque_bera_stat": jb_stat,
                    "jarque_bera_p_value": jb_p,
                    "jarque_bera_interpretation": jb_interpretation,
                    "durbin_watson": dw_stat,
                    "durbin_watson_interpretation": dw_interpretation,
                    "covariance_type": "HC3",
                }
            ]
        )
        diagnostic_rows.append(diagnostic_table)
        save_table(
            diagnostic_table,
            TABLES_DIR / f"eda_06_ols_residual_diagnostics_{stratum.lower()}.csv",
            json_path=TABLES_DIR / f"eda_06_ols_residual_diagnostics_{stratum.lower()}.json",
        )

        diagnostics[stratum] = {
            "model": model,
            "results": results,
            "influence": influence,
            "bp_lm": bp_lm,
            "bp_p": bp_lm_p,
            "jb_stat": jb_stat,
            "jb_p": jb_p,
            "dw": dw_stat,
            "bp_interpretation": bp_interpretation,
            "jb_interpretation": jb_interpretation,
            "dw_interpretation": dw_interpretation,
            "n_ols": len(ols_ready),
        }

    if diagnostic_rows:
        save_table(
            pd.concat(diagnostic_rows, ignore_index=True),
            TABLES_DIR / "eda_06_ols_residual_diagnostics_all_strata.csv",
            json_path=TABLES_DIR / "eda_06_ols_residual_diagnostics_all_strata.json",
        )

    return diagnostics, ols_ready_frames


def section7_outlier_influence(
    diagnostics: dict[str, dict[str, object]],
    ols_ready_frames: dict[str, pd.DataFrame],
) -> dict[str, int]:
    section_header("SECTION 7 - OUTLIER INFLUENCE (COOK'S DISTANCE)")
    influence_counts: dict[str, int] = {}

    for stratum, diagnostic in diagnostics.items():
        influence: OLSInfluence = diagnostic["influence"]
        ols_ready = ols_ready_frames[stratum].copy().reset_index(drop=True)
        cooks_d, _ = influence.cooks_distance
        cooks_d_values = np.asarray(cooks_d)
        threshold = 4 / len(ols_ready)

        ols_ready["cooks_d"] = cooks_d_values
        high_influence = ols_ready[ols_ready["cooks_d"] > threshold].sort_values("cooks_d", ascending=False)
        influence_counts[stratum] = int(len(high_influence))

        fig, ax = plt.subplots(figsize=(12, 6))
        markerline, stemlines, baseline = ax.stem(np.arange(len(cooks_d_values)), cooks_d_values, basefmt=" ")
        plt.setp(stemlines, color=PALETTE[stratum], linewidth=1.0)
        plt.setp(markerline, color=PALETTE[stratum], markersize=3)
        ax.axhline(
            threshold,
            color="red",
            linestyle="--",
            linewidth=1.2,
        )
        flagged = np.where(cooks_d_values > threshold)[0]
        if len(flagged) > 0:
            ax.scatter(flagged, cooks_d_values[flagged], color="red", s=25, zorder=3)
        ax.set_title(f"{stratum} - Cook's distance")
        ax.text(
            0.5,
            1.01,
            "Points above the red threshold disproportionately influence the OLS fit and warrant inspection.",
            transform=ax.transAxes,
            ha="center",
            va="bottom",
            fontsize=10,
        )
        ax.set_xlabel("Observation index")
        ax.set_ylabel("Cook's Distance")
        ax.legend(
            handles=[
                Line2D(
                    [0],
                    [0],
                    color=PALETTE[stratum],
                    marker="o",
                    linestyle="-",
                    linewidth=1.0,
                    markersize=4,
                    label="Cook's D per observation",
                ),
                Line2D(
                    [0],
                    [0],
                    color="red",
                    linestyle="--",
                    linewidth=1.2,
                    label=f"4/n threshold ({threshold:.4f}) — high-influence cutoff",
                ),
            ],
            loc="upper right",
        )
        save_figure(fig, SECTION_DIRS["07_outliers"] / f"{stratum}_cooks_distance.png")

        print(f"\n[{stratum}] Cook's distance threshold: {threshold:,.6f}")
        print(f"High-influence observations (Cook's D > 4/n): {len(high_influence):,}")
        top10 = high_influence[["property_id", "city", TARGET, "cooks_d"]].head(10)
        top_n = high_influence[["property_id", "city", TARGET, "cooks_d"]].head(25).copy()
        top_n.insert(0, "stratum", stratum)
        save_table(
            top_n,
            TABLES_DIR / f"eda_07_cooks_distance_top25_{stratum.lower()}.csv",
            json_path=TABLES_DIR / f"eda_07_cooks_distance_top25_{stratum.lower()}.json",
        )
        if top10.empty:
            print("No high-influence rows above threshold.")
        else:
            print(top10.to_string(index=False, float_format=lambda value: f"{value:,.6f}"))

    return influence_counts


def section8_mcrai(strata_frames: dict[str, pd.DataFrame]) -> None:
    section_header("SECTION 8 - MCRAI ZERO-RATE AND DISTRIBUTION")

    zero_rate = pd.DataFrame(
        {
            stratum: [(df[col] == 0).mean() * 100 for col in MCRAI_COLS]
            for stratum, df in strata_frames.items()
        },
        index=MCRAI_COLS,
    )
    zero_rate.index.name = "mcrai_category"
    save_table(
        zero_rate.reset_index(),
        TABLES_DIR / "eda_08_mcrai_zero_rate_by_category_stratum.csv",
        json_path=TABLES_DIR / "eda_08_mcrai_zero_rate_by_category_stratum.json",
    )
    print("\nMCRAI zero rate (%) by category and stratum")
    print(format_float_table(zero_rate.reset_index(), digits=2))

    for stratum, df in strata_frames.items():
        zero_rate_lgu = df.groupby("city")[MCRAI_COLS].apply(lambda frame: (frame == 0).mean() * 100)
        zero_rate_lgu = zero_rate_lgu.reindex([city for city in LGU_ORDER if city in zero_rate_lgu.index])
        save_table(
            zero_rate_lgu.reset_index(),
            TABLES_DIR / f"eda_08_mcrai_zero_rate_by_lgu_{stratum.lower()}.csv",
        )

        fig, axes = plt.subplots(3, 3, figsize=(16, 12))
        for ax, column in zip(axes.flatten(), MCRAI_COLS):
            sns.histplot(df[column].dropna(), kde=True, ax=ax, color=PALETTE[stratum])
            ax.set_title(f"{stratum} - {column}")
            ax.set_xlabel(column)
            ax.set_ylabel("Count")
        save_figure(fig, SECTION_DIRS["08_mcrai"] / f"{stratum}_mcrai_distributions.png")

    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
    for ax, stratum in zip(axes, STRATA.keys()):
        df = strata_frames[stratum]
        sns.regplot(
            data=df,
            x="mcrai_composite",
            y=TARGET,
            scatter_kws={"alpha": 0.55, "s": 28, "color": PALETTE[stratum]},
            line_kws={"color": "black", "linewidth": 1.4},
            ax=ax,
        )
        ax.set_title(f"{stratum} - mcrai_composite vs price_per_sqm")
        ax.set_xlabel("mcrai_composite")
        ax.set_ylabel("price_per_sqm (PHP/sqm)")
        ax.legend(
            handles=[
                Line2D([0], [0], color="black", linewidth=1.4, label="Linear regression fit"),
            ],
            loc="upper right",
        )
    save_figure(fig, SECTION_DIRS["08_mcrai"] / "composite_vs_price_all_strata.png")


def print_final_summary(
    diagnostics: dict[str, dict[str, object]],
    vif_flags: dict[str, list[str]],
    influence_counts: dict[str, int],
    spearman_tables: dict[str, pd.DataFrame],
) -> None:
    section_header("FINAL SUMMARY")
    for stratum in STRATA.keys():
        bp_result = "Yes" if diagnostics[stratum]["bp_p"] < 0.05 else "No"
        jb_result = "Yes" if diagnostics[stratum]["jb_p"] >= 0.05 else "No"
        top3 = spearman_tables[stratum].dropna(subset=["abs_rho"]).head(3)
        top3_text = ", ".join(
            f"{row.feature} ({row.spearman_rho:,.3f})" for row in top3.itertuples(index=False)
        )
        vif_text = ", ".join(vif_flags[stratum]) if vif_flags[stratum] else "None"

        print(f"\n[{stratum}]")
        print(f"n rows used in OLS: {diagnostics[stratum]['n_ols']:,}")
        print(f"OLS feature count: {len(FEATURE_COLS[stratum]):,}")
        print(f"Heteroscedastic? {bp_result} ({diagnostics[stratum]['bp_interpretation']})")
        print(f"Normality of residuals? {jb_result} ({diagnostics[stratum]['jb_interpretation']})")
        print(f"Features with VIF > 5: {vif_text}")
        print(f"High-influence observations count: {influence_counts[stratum]:,}")
        print(f"Top 3 features by |Spearman rho|: {top3_text}")


def write_defense_table() -> None:
    defense_rows = [
        {
            "issue": "skewed prices",
            "implication": "Some listings are much more expensive than the typical row, so raw prices are not well behaved.",
            "workflow_response": "Model log(price_per_sqm) instead of raw total price, then back-transform for reporting and app output.",
            "defense_wording": "The target was log-transformed because listing prices are strongly skewed; this keeps the modeling scale more stable while preserving peso-per-sqm reporting.",
        },
        {
            "issue": "heteroscedasticity",
            "implication": "OLS errors get wider or narrower across price levels, so ordinary OLS standard errors are unreliable.",
            "workflow_response": "Use HC3 robust standard errors in OLS diagnostics and do not use OLS as the deployed valuation model.",
            "defense_wording": "Heteroscedasticity was detected and accounted for in the diagnostic OLS layer using HC3 robust standard errors; it is not presented as fixed.",
        },
        {
            "issue": "residual non-normality",
            "implication": "OLS residuals are not perfectly normal, which is common in listing data.",
            "workflow_response": "Keep OLS as a transparent diagnostic baseline and rely on tree models for deployment.",
            "defense_wording": "Residual non-normality limits coefficient-level OLS inference, so OLS is used only for diagnostics, not as the final valuation engine.",
        },
        {
            "issue": "collinearity/VIF",
            "implication": "Some location and amenity variables overlap strongly, making OLS coefficients unstable.",
            "workflow_response": "Use a trimmed OLS diagnostic specification and keep the full feature set in Random Forest, where correlated predictors are less destabilizing.",
            "defense_wording": "Collinearity is reported transparently; it is handled as an OLS interpretation limitation rather than hidden or claimed away.",
        },
        {
            "issue": "MCRAI-CBD overlap",
            "implication": "Amenity access and CBD proximity measure related spatial effects.",
            "workflow_response": "Interpret MCRAI as a local accessibility block, not as the dominant standalone price driver.",
            "defense_wording": "MCRAI is treated as one accessibility signal among several correlated spatial variables, so the thesis avoids overclaiming it as the main driver.",
        },
        {
            "issue": "duplicate listings",
            "implication": "Same or near-same listings can inflate support for a location or price point.",
            "workflow_response": "Drop hard duplicates in the stratified ABT workflow using identical coordinates, area, and price per sqm.",
            "defense_wording": "Duplicate risk is checked explicitly, and the modeling workflow removes hard duplicates before final training.",
        },
        {
            "issue": "shared coordinates/geocoding clusters",
            "implication": "Multiple listings may share the same pin or a fallback centroid, making random splits leak location information.",
            "workflow_response": "Evaluate with GroupKFold by coordinate cluster so shared-coordinate rows stay in the same fold.",
            "defense_wording": "Shared coordinates are handled through coordinate-group cross-validation, reducing the risk that the model is tested on locations it effectively saw in training.",
        },
        {
            "issue": "vacant-lot instability",
            "implication": "Land prices depend on missing parcel-specific details such as frontage, zoning, title, slope, and flood risk.",
            "workflow_response": "Apply the residential-lot scope filter and report Vacant Lot as the weakest stratum.",
            "defense_wording": "The weaker Vacant Lot results are framed as a data ceiling from missing parcel attributes, not simply as a modeling failure.",
        },
        {
            "issue": "thin LGU cells",
            "implication": "Some city-by-stratum combinations have few listings, so their boxplots and medians are less stable.",
            "workflow_response": "Stratify by property type and interpret small LGU cells cautiously with sample-size tables.",
            "defense_wording": "Thin LGU cells are reported with counts, and the thesis avoids overreading local patterns where support is small.",
        },
    ]
    save_table(pd.DataFrame(defense_rows), TABLES_DIR / "eda_defense_table.csv")


def main() -> None:
    ensure_directories()
    configure_plotting()
    strata_frames = load_strata()

    section1_target_distribution(strata_frames)
    section2_geographic_spread(strata_frames)
    section3_feature_distributions(strata_frames)
    spearman_tables = section4_correlation_analysis(strata_frames)
    _, vif_flags = section5_multicollinearity(strata_frames)
    diagnostics, ols_ready_frames = section6_ols_and_residuals(strata_frames)
    influence_counts = section7_outlier_influence(diagnostics, ols_ready_frames)
    section8_mcrai(strata_frames)
    print_final_summary(diagnostics, vif_flags, influence_counts, spearman_tables)
    write_defense_table()
    print_written_files()


if __name__ == "__main__":
    main()
