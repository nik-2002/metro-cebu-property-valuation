"""EDA script for Metro Cebu residential valuation ABT."""

from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

warnings.filterwarnings("ignore")

SCRIPT_PATH = Path(__file__).resolve()
THESIS_DIR = next(parent for parent in SCRIPT_PATH.parents if (parent / "Data" / "processed").exists())
ABT_PATH = THESIS_DIR / "Data" / "processed" / "abt_clean.csv"
EDA_DIR = THESIS_DIR / "EDA"

CBD_DIST_COLS = [
    "dist_cebu_business_park_m",
    "dist_mandaue_cbd_m",
    "dist_mactan_cbd_m",
    "dist_srp_m",
    "dist_talisay_tabunok_m",
    "dist_consolacion_m",
    "dist_naga_city_m",
    "dist_airport_m",
]
CBD_LABELS = {
    "dist_cebu_business_park_m": "Cebu Business\nPark",
    "dist_mandaue_cbd_m": "Mandaue CBD",
    "dist_mactan_cbd_m": "Mactan CBD",
    "dist_srp_m": "SRP",
    "dist_talisay_tabunok_m": "Talisay\nTabunok",
    "dist_consolacion_m": "Consolacion",
    "dist_naga_city_m": "Naga City",
    "dist_airport_m": "Airport",
}
MCRAI_COLS = [
    "mcrai_education",
    "mcrai_finance",
    "mcrai_grocery",
    "mcrai_health",
    "mcrai_security",
    "mcrai_transport",
    "mcrai_tourism",
    "mcrai_recreation",
    "mcrai_retail_density",
    "mcrai_composite",
]
TARGET_EXCLUDE_COLS = {
    "property_id",
    "price_php",
    "price_per_sqm",
    "log_price",
    "valuation_gap",
    "price_outlier_flag",
    "area_sqm",
    "bir_zonal_rr_log",
}


def save(fig: plt.Figure, name: str) -> None:
    out = EDA_DIR / name
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out}")


def staggered_horizontal_labels(labels: list[str]) -> list[str]:
    return [f"{label}\n" if index % 2 == 0 else f"\n{label}" for index, label in enumerate(labels)]


def three_level_horizontal_labels(labels: list[str]) -> list[str]:
    levels = (
        lambda label: f"{label}\n\n",
        lambda label: f"\n{label}\n",
        lambda label: f"\n\n{label}",
    )
    return [levels[index % len(levels)](label) for index, label in enumerate(labels)]


def add_three_level_column_labels(ax: plt.Axes, labels: list[str]) -> None:
    x_positions = ax.get_xticks()
    y_levels = [-0.032, -0.082, -0.132]
    line_bottoms = [-0.026, -0.076, -0.126]

    ax.set_xticklabels([])
    ax.tick_params(axis="x", length=0)

    transform = ax.get_xaxis_transform()
    for index, (x_position, label) in enumerate(zip(x_positions, labels)):
        level = index % len(y_levels)
        label_y = y_levels[level]
        line_bottom = line_bottoms[level]
        ax.plot(
            [x_position, x_position],
            [-0.004, line_bottom],
            color="#777777",
            linewidth=0.8,
            transform=transform,
            clip_on=False,
        )
        ax.text(
            x_position,
            label_y,
            label,
            transform=transform,
            ha="center",
            va="top",
            fontsize=8.5,
            linespacing=0.95,
            clip_on=False,
        )


def wrapped_distance_labels(labels: list[str]) -> list[str]:
    wrapped: list[str] = []
    for label in labels:
        parts = label.split("_")
        if len(parts) > 2:
            wrapped.append("_".join(parts[:2]) + "\n" + "_".join(parts[2:]))
        else:
            wrapped.append(label)
    return wrapped



def sep(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)



def section1(df: pd.DataFrame) -> None:
    sep("SECTION 1 - Outlier and null triage")

    null_pps = df[df["price_per_sqm"].isna()]
    print(f"\nprice_per_sqm nulls: {len(null_pps)} rows")
    print(null_pps[["property_id", "city", "property_type", "market_segment", "area_sqm"]].to_string(index=False))

    low_pps = df[df["price_per_sqm"].notna() & (df["price_per_sqm"] < 100)]
    print(f"\nprice_per_sqm < 100: {len(low_pps)} rows")
    print(low_pps[["property_id", "city", "property_type", "price_php", "area_sqm", "price_per_sqm"]].to_string(index=False))

    null_lag = df[df["spatial_lag_price"].isna()]
    print(f"\nspatial_lag_price nulls: {len(null_lag)} rows")
    print(null_lag[["property_id", "city", "market_segment"]].to_string(index=False))

    missing_pct = df.isna().mean().mul(100).sort_values(ascending=False)
    missing_pct = missing_pct[missing_pct > 0].head(15).sort_values()
    if not missing_pct.empty:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.barh(missing_pct.index, missing_pct.values, color="#7a5195")
        ax.set_xlabel("Missing values (%)")
        ax.set_title("Top columns by missingness")
        save(fig, "missingness_top15.png")

    print("\nTop missingness rates (%):")
    print(df.isna().mean().mul(100).sort_values(ascending=False).head(10).round(2).to_string())
    print("\nSECTION 1 DONE - no rows dropped.")



def section2(df: pd.DataFrame) -> None:
    sep("SECTION 2 - Target variable distributions")

    valid_pps = df["price_per_sqm"].dropna()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(valid_pps, bins=60, density=True, color="steelblue", alpha=0.7, label="histogram")
    kde = stats.gaussian_kde(valid_pps)
    xmin, xmax = valid_pps.min(), valid_pps.quantile(0.995)
    xs = np.linspace(xmin, xmax, 400)
    ax.plot(xs, kde(xs), color="darkblue", lw=2, label="KDE")
    ax.set_xlim(xmin, xmax)
    ax.set_xlabel("price_per_sqm (PHP)")
    ax.set_ylabel("Density")
    ax.set_title("Distribution of price_per_sqm")
    ax.legend()
    save(fig, "price_per_sqm_hist.png")

    valid_lp = df["log_price"].dropna()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(valid_lp, bins=50, density=True, color="seagreen", alpha=0.7, label="histogram")
    kde2 = stats.gaussian_kde(valid_lp)
    xs2 = np.linspace(valid_lp.min(), valid_lp.max(), 400)
    ax.plot(xs2, kde2(xs2), color="darkgreen", lw=2, label="KDE")
    ax.set_xlabel("log_price")
    ax.set_ylabel("Density")
    ax.set_title("Distribution of log_price")
    ax.legend()
    save(fig, "log_price_hist.png")

    order_seg = df.groupby("market_segment")["price_per_sqm"].median().sort_values().index.tolist()
    fig, ax = plt.subplots(figsize=(9, 5))
    sub_seg = df.dropna(subset=["price_per_sqm"])
    sns.boxplot(
        data=sub_seg,
        x="market_segment",
        y="price_per_sqm",
        order=order_seg,
        showfliers=False,
        ax=ax,
    )
    ax.set_title("price_per_sqm by market_segment (outliers hidden)")
    ax.set_xlabel("market_segment")
    ax.set_ylabel("price_per_sqm (PHP)")
    save(fig, "price_by_segment.png")

    order_pt = df.groupby("property_type")["price_per_sqm"].median().sort_values().index.tolist()
    fig, ax = plt.subplots(figsize=(10, 5))
    sub_pt = df.dropna(subset=["price_per_sqm"])
    sns.boxplot(
        data=sub_pt,
        x="property_type",
        y="price_per_sqm",
        order=order_pt,
        showfliers=False,
        ax=ax,
    )
    ax.set_title("price_per_sqm by property_type (outliers hidden)")
    ax.set_xlabel("property_type")
    ax.set_ylabel("price_per_sqm (PHP)")
    plt.xticks(rotation=30, ha="right")
    save(fig, "price_by_property_type.png")

    print(f"\nprice_per_sqm - skewness: {valid_pps.skew():.4f}  kurtosis: {valid_pps.kurtosis():.4f}")
    print(f"log_price     - skewness: {valid_lp.skew():.4f}  kurtosis: {valid_lp.kurtosis():.4f}")
    print("\nSECTION 2 DONE.")



def section3(df: pd.DataFrame) -> None:
    sep("SECTION 3 - Geographic spread")
    total = len(df)
    city_counts = df["city"].value_counts()
    print("\nRows by city:")
    for city, n in city_counts.items():
        print(f"  {city:<22}  {n:>4}  ({n / total * 100:.1f}%)")

    city_segment = pd.crosstab(df["city"], df["market_segment"])
    city_property = pd.crosstab(df["city"], df["property_type"])

    print("\nCrosstab city x market_segment:")
    print(city_segment.to_string())

    print("\nCrosstab city x property_type:")
    print(city_property.to_string())

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(city_segment, annot=True, fmt="d", cmap="Blues", linewidths=0.5, ax=ax)
    ax.set_title("ABT rows by city and market segment")
    ax.set_xlabel("market_segment")
    ax.set_ylabel("city")
    save(fig, "city_segment_heatmap.png")

    open_market = df[(df["market_segment"] == "open_market") & df["price_per_sqm"].notna()].copy()
    city_order = open_market.groupby("city")["price_per_sqm"].median().sort_values().index.tolist()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(
        data=open_market,
        x="city",
        y="price_per_sqm",
        order=city_order,
        showfliers=False,
        ax=ax,
    )
    ax.set_title("open_market price_per_sqm by city (outliers hidden)")
    ax.set_xlabel("city")
    ax.set_ylabel("price_per_sqm (PHP)")
    plt.xticks(rotation=25, ha="right")
    save(fig, "price_by_city_open_market.png")

    print("\nSECTION 3 DONE.")



def section4(df: pd.DataFrame) -> None:
    sep("SECTION 4 - CBD distance correlations")

    cbd_df = df[CBD_DIST_COLS].dropna()
    corr = cbd_df.corr(method="pearson")
    plot_corr = corr.rename(index=CBD_LABELS, columns=CBD_LABELS)

    fig, ax = plt.subplots(figsize=(18, 8.2))
    mask = np.triu(np.ones_like(plot_corr, dtype=bool))
    sns.heatmap(
        plot_corr,
        mask=mask,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        ax=ax,
        linewidths=0.5,
        square=True,
    )
    ax.set_title("Pearson correlations - CBD distance columns")
    add_three_level_column_labels(ax, list(plot_corr.columns))
    ax.set_yticklabels(list(plot_corr.index), rotation=0, fontsize=10)
    save(fig, "cbd_distance_corr.png")

    print("\nPairs with |r| > 0.85:")
    found = False
    for i in range(len(CBD_DIST_COLS)):
        for j in range(i + 1, len(CBD_DIST_COLS)):
            col_i = CBD_DIST_COLS[i]
            col_j = CBD_DIST_COLS[j]
            r = corr.loc[col_i, col_j]
            if abs(r) > 0.85:
                print(f"  {col_i}  x  {col_j}  r={r:.3f}")
                found = True
    if not found:
        print("  None.")

    print("\nSECTION 4 DONE.")



def section5(df: pd.DataFrame) -> None:
    sep("SECTION 5 - MCRAI distributions and correlations")

    print(f"\n{'Column':<26}  {'zeros':>6}  {'zero%':>6}  {'mean':>10}  {'median':>10}  {'std':>10}")
    for col in MCRAI_COLS:
        s = df[col].dropna()
        n_zero = int((s == 0).sum())
        pct_zero = n_zero / len(s) * 100 if len(s) > 0 else 0.0
        print(f"  {col:<24}  {n_zero:>6}  {pct_zero:>5.1f}%  {s.mean():>10.4f}  {s.median():>10.4f}  {s.std():>10.4f}")

    print("\nmcrai_retail_density zero rate by city:")
    for city, group in df.groupby("city"):
        s = group["mcrai_retail_density"].dropna()
        n_zero = int((s == 0).sum())
        pct = n_zero / len(s) * 100 if len(s) > 0 else 0.0
        print(f"  {city:<22}  {n_zero:>4} / {len(s):>4}  ({pct:.1f}%)")

    valid_mc = df["mcrai_composite"].dropna()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(valid_mc, bins=50, color="mediumpurple", alpha=0.8, edgecolor="white")
    ax.set_xlabel("mcrai_composite")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of mcrai_composite")
    save(fig, "mcrai_composite_hist.png")

    mcrai_df = df[MCRAI_COLS].dropna()
    mcrai_corr = mcrai_df.corr(method="spearman")
    fig, ax = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(mcrai_corr, dtype=bool))
    sns.heatmap(
        mcrai_corr,
        mask=mask,
        annot=True,
        fmt=".2f",
        cmap="vlag",
        center=0,
        ax=ax,
        linewidths=0.5,
        square=True,
    )
    ax.set_title("Spearman correlations - MCRAI components")
    plt.xticks(rotation=30, ha="right")
    save(fig, "mcrai_corr_matrix.png")

    print("\nSECTION 5 DONE.")



def section6(df: pd.DataFrame) -> None:
    sep("SECTION 6 - Feature correlations with target")

    open_market = df[(df["market_segment"] == "open_market") & df["price_per_sqm"].notna()].copy()
    numeric = open_market.select_dtypes(include="number").drop(columns=TARGET_EXCLUDE_COLS, errors="ignore")
    corr_with_target = numeric.corrwith(open_market["price_per_sqm"], method="spearman").dropna()
    corr_with_target = corr_with_target.sort_values(key=np.abs, ascending=False)

    print("\nTop 15 Spearman correlations with price_per_sqm in open_market (by |r|):")
    print(corr_with_target.head(15).round(4).to_string())

    print("\nBottom 15 Spearman correlations with price_per_sqm in open_market (by |r|):")
    print(corr_with_target.tail(15).round(4).to_string())

    top_features = corr_with_target.head(15).sort_values()
    fig, ax = plt.subplots(figsize=(9, 6))
    colors = np.where(top_features.values >= 0, "#2c7fb8", "#d95f0e")
    ax.barh(top_features.index, top_features.values, color=colors)
    ax.axvline(0, color="black", linewidth=1)
    ax.set_xlabel("Spearman correlation with price_per_sqm")
    ax.set_title("Strongest numeric feature correlations - open_market subset")
    save(fig, "target_corr_open_market.png")

    heatmap_features = corr_with_target.head(12).index.tolist()
    heatmap_df = open_market[["price_per_sqm", *heatmap_features]].corr(method="spearman")
    fig, ax = plt.subplots(figsize=(11, 9))
    sns.heatmap(
        heatmap_df,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        linewidths=0.5,
        square=True,
        ax=ax,
    )
    ax.set_title("Spearman correlations - top open_market numeric features")
    plt.xticks(rotation=30, ha="right")
    save(fig, "open_market_top_feature_corr.png")

    print("\nSECTION 6 DONE.")



def section7(df: pd.DataFrame) -> None:
    sep("SECTION 7 - Imputation flag check")

    for flag in ["bedrooms_imputed", "bathrooms_imputed", "floor_area_imputed"]:
        print(f"\n{flag} value counts:")
        print(df[flag].value_counts().to_string())

        grouped = df.groupby(flag)["price_per_sqm"].mean()
        print(f"  mean price_per_sqm by {flag}:")
        for val, mean_pps in grouped.items():
            print(f"    {flag}={val}: {mean_pps:,.2f}")

    print("\nSECTION 7 DONE.")



def main() -> None:
    EDA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"EDA output directory: {EDA_DIR.resolve()}")

    df = pd.read_csv(ABT_PATH)
    print(f"Loaded ABT: {df.shape[0]} rows x {df.shape[1]} columns")

    section1(df)
    section2(df)
    section3(df)
    section4(df)
    section5(df)
    section6(df)
    section7(df)

    print("\nAll EDA sections complete.")


if __name__ == "__main__":
    main()
