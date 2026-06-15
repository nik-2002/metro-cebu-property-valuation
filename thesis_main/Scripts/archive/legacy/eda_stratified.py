"""Stratified EDA for the Metro Cebu residential valuation ABT."""

from __future__ import annotations

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
THESIS_DIR = os.path.dirname(SCRIPT_DIR)           # thesis_main/
ROOT_DIR = os.path.dirname(THESIS_DIR)             # workspace root (16 Thesis/)

ABT_PATH = os.path.join(THESIS_DIR, "Data", "processed", "abt_clean.csv")
EDA_DIR = os.path.join(ROOT_DIR, "EDA")

os.makedirs(EDA_DIR, exist_ok=True)


STRATUM_ORDER = ["Condominium", "Vacant Lot", "Houses"]
NULL_CHECK_COLS = ["lot_area_sqm", "floor_area_sqm", "bedrooms", "bathrooms"]
CORR_EXCLUDE_COLS = {
    "price_php",
    "log_price",
    "valuation_gap",
    "spatial_lag_price",
    "property_id",
    "price_outlier_flag",
    "bedrooms_imputed",
    "bathrooms_imputed",
    "floor_area_imputed",
    "price_per_sqm",
}


def assign_stratum(property_type: str) -> str:
    if property_type == "Condominium":
        return "Condominium"
    if property_type == "Vacant Lot":
        return "Vacant Lot"
    return "Houses"


def load_modeling_ready_abt() -> pd.DataFrame:
    df = pd.read_csv(ABT_PATH)
    df = df[df["market_segment"] == "open_market"].copy()
    df = df[~df["property_id"].isin([468, 714, 769])].copy()
    df = df[df["price_per_sqm"].notna()].copy()
    df = df[df["spatial_lag_price"].notna()].copy()
    df["stratum"] = df["property_type"].apply(assign_stratum)
    df["stratum"] = pd.Categorical(df["stratum"], categories=STRATUM_ORDER, ordered=True)
    return df


def save_csv(df: pd.DataFrame, name: str) -> str:
    out_path = os.path.join(EDA_DIR, name)
    df.to_csv(out_path, index=False)
    print(f"Saved -> {out_path}")
    return out_path


def format_currency(value: float) -> str:
    return f"PHP {value:,.0f}"


def build_stratum_counts(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for stratum in STRATUM_ORDER:
        subset = df[df["stratum"] == stratum].copy()
        city_counts = subset["city"].value_counts().sort_index()
        rows.append(
            {
                "stratum": stratum,
                "total_rows": int(len(subset)),
                "rows_with_price": int(subset["price_per_sqm"].notna().sum()),
                "cities_covered": json.dumps(sorted(subset["city"].dropna().unique().tolist()), ensure_ascii=False),
                "lgu_breakdown": json.dumps({city: int(count) for city, count in city_counts.items()}, ensure_ascii=False),
            }
        )

    counts_df = pd.DataFrame(rows)
    print("\n=== STRATUM COUNTS ===")
    print(counts_df.to_string(index=False))

    city_stratum = pd.crosstab(df["city"], df["stratum"])
    city_stratum = city_stratum.reindex(columns=STRATUM_ORDER, fill_value=0)
    print("\n=== CITY × STRATUM CROSSTAB ===")
    print(city_stratum.to_string())

    return counts_df


def build_stratum_price_stats(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for stratum in STRATUM_ORDER:
        subset = df[df["stratum"] == stratum]["price_per_sqm"].dropna()
        if subset.empty:
            rows.append(
                {
                    "stratum": stratum,
                    "count": 0,
                    "min": np.nan,
                    "p5": np.nan,
                    "p25": np.nan,
                    "median": np.nan,
                    "mean": np.nan,
                    "p75": np.nan,
                    "p95": np.nan,
                    "max": np.nan,
                    "std": np.nan,
                    "cv": np.nan,
                }
            )
            continue

        mean = float(subset.mean())
        std = float(subset.std(ddof=1))
        rows.append(
            {
                "stratum": stratum,
                "count": int(subset.shape[0]),
                "min": float(subset.min()),
                "p5": float(subset.quantile(0.05)),
                "p25": float(subset.quantile(0.25)),
                "median": float(subset.median()),
                "mean": mean,
                "p75": float(subset.quantile(0.75)),
                "p95": float(subset.quantile(0.95)),
                "max": float(subset.max()),
                "std": std,
                "cv": float(std / mean) if mean else np.nan,
            }
        )

    stats_df = pd.DataFrame(rows)
    print("\n=== STRATUM PRICE STATS ===")
    print(stats_df.to_string(index=False, float_format=lambda x: f"{x:,.2f}" if pd.notna(x) else "nan"))
    return stats_df


def plot_price_distributions(df: pd.DataFrame) -> str:
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5), sharey=True)

    for ax, stratum in zip(axes, STRATUM_ORDER):
        subset = df[df["stratum"] == stratum]["price_per_sqm"].dropna()
        if subset.empty:
            ax.set_visible(False)
            continue

        ax.hist(subset, bins=50, color="#4c78a8", alpha=0.8, edgecolor="white", linewidth=0.5)
        ax.set_xscale("log")
        ax.grid(True, axis="y", linestyle=":", linewidth=0.7, alpha=0.5)

        p25 = float(subset.quantile(0.25))
        median = float(subset.median())
        p75 = float(subset.quantile(0.75))
        y_top = ax.get_ylim()[1]
        marker_specs = [
            (p25, "P25", "#2ca02c"),
            (median, "Median", "#d62728"),
            (p75, "P75", "#9467bd"),
        ]
        for value, label, color in marker_specs:
            ax.axvline(value, color=color, linestyle="--", linewidth=1.8)
            ax.text(
                value,
                y_top * 0.95,
                f"{label}\n{value:,.0f}",
                rotation=90,
                va="top",
                ha="center",
                fontsize=8,
                color=color,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.75, "pad": 1.5},
            )

        ax.set_title(f"{stratum} (n={len(subset):,}, median={format_currency(median)}/sqm)")
        ax.set_xlabel("price_per_sqm (PHP/sqm, log scale)")
        ax.set_ylabel("Count")

    fig.suptitle("Stratum Price Distributions", fontsize=14, y=1.02)
    fig.tight_layout()
    out_path = os.path.join(EDA_DIR, "stratum_price_distributions.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved -> {out_path}")
    return out_path


def compute_spearman_correlations(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    outputs: dict[str, pd.DataFrame] = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    feature_cols = [c for c in numeric_cols if c not in CORR_EXCLUDE_COLS]

    for stratum in STRATUM_ORDER:
        subset = df[df["stratum"] == stratum].copy()
        corr_rows = []
        for col in feature_cols:
            pair = subset[["price_per_sqm", col]].dropna()
            if pair.shape[0] < 3 or pair[col].nunique() < 2:
                continue
            corr = pair["price_per_sqm"].corr(pair[col], method="spearman")
            if pd.notna(corr):
                corr_rows.append({"feature": col, "spearman_r": float(corr), "abs_r": abs(float(corr))})

        corr_df = pd.DataFrame(corr_rows).sort_values("abs_r", ascending=False).head(15).reset_index(drop=True)
        outputs[stratum] = corr_df
    return outputs


def plot_stratum_correlations(df: pd.DataFrame) -> str:
    corr_map = compute_spearman_correlations(df)
    fig, axes = plt.subplots(1, 3, figsize=(20, 9), sharex=True)

    for ax, stratum in zip(axes, STRATUM_ORDER):
        corr_df = corr_map[stratum]
        if corr_df.empty:
            ax.set_visible(False)
            continue

        corr_df = corr_df.sort_values("spearman_r")
        colors = ["#d95f02" if value > 0 else "#1f77b4" for value in corr_df["spearman_r"]]
        ax.barh(corr_df["feature"], corr_df["spearman_r"], color=colors, alpha=0.9)
        ax.axvline(0, color="black", linewidth=1)
        ax.set_title(f"{stratum} (top 15 |rho|)")
        ax.set_xlabel("Spearman rho with price_per_sqm")
        ax.grid(True, axis="x", linestyle=":", linewidth=0.7, alpha=0.5)

        x_limit = max(0.1, float(corr_df["spearman_r"].abs().max()) * 1.2)
        ax.set_xlim(-x_limit, x_limit)

    fig.suptitle("Stratum-Specific Spearman Correlations with price_per_sqm", fontsize=14, y=0.995)
    fig.tight_layout()
    out_path = os.path.join(EDA_DIR, "stratum_correlations.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved -> {out_path}")
    return out_path


def print_structural_nulls(df: pd.DataFrame) -> None:
    rows = []
    for stratum in STRATUM_ORDER:
        subset = df[df["stratum"] == stratum]
        for col in NULL_CHECK_COLS:
            null_count = int(subset[col].isna().sum())
            rows.append(
                {
                    "stratum": stratum,
                    "column": col,
                    "null_count": null_count,
                    "null_pct": (null_count / len(subset) * 100) if len(subset) else np.nan,
                }
            )

    null_df = pd.DataFrame(rows)
    print("\n=== STRUCTURAL NULL ANALYSIS ===")
    print(null_df.to_string(index=False, float_format=lambda x: f"{x:.1f}" if pd.notna(x) else "nan"))


def main() -> None:
    df = load_modeling_ready_abt()

    print("\n=== EDA STRATIFIED — START ===")
    print(f"ABT path: {ABT_PATH}")
    print(f"EDA output dir: {EDA_DIR}")
    print(f"Total modeling-ready rows: {len(df):,}")

    counts_df = build_stratum_counts(df)
    save_csv(counts_df, "stratum_counts.csv")

    stats_df = build_stratum_price_stats(df)
    save_csv(stats_df, "stratum_price_stats.csv")

    plot_price_distributions(df)
    plot_stratum_correlations(df)
    print_structural_nulls(df)

    print("\n=== EDA STRATIFIED — SUMMARY ===")
    print(f"Total modeling-ready rows: {len(df):,}")
    for stratum in STRATUM_ORDER:
        subset = df[df["stratum"] == stratum]["price_per_sqm"].dropna()
        median = float(subset.median()) if not subset.empty else np.nan
        print(f"Stratum: {stratum} — {len(subset):,} rows, median {format_currency(median)}/sqm")
    print("=== FILES SAVED ===")
    print(os.path.join(EDA_DIR, "stratum_counts.csv"))
    print(os.path.join(EDA_DIR, "stratum_price_stats.csv"))
    print(os.path.join(EDA_DIR, "stratum_price_distributions.png"))
    print(os.path.join(EDA_DIR, "stratum_correlations.png"))


if __name__ == "__main__":
    main()
