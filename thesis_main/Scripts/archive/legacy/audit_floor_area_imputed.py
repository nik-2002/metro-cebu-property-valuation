from pathlib import Path

import pandas as pd
from scipy.stats import pointbiserialr


ABT_PATH = Path(__file__).resolve().parents[1] / "Data" / "processed" / "abt_clean.csv"


def print_crosstab(df: pd.DataFrame, column: str) -> None:
    counts = pd.crosstab(df["floor_area_imputed"], df[column], dropna=False)
    row_percentages = counts.div(counts.sum(axis=1), axis=0).fillna(0).mul(100).round(1)

    print(f"\nCROSSTAB: floor_area_imputed x {column} (counts)")
    print(counts.to_string())
    print(f"\nCROSSTAB: floor_area_imputed x {column} (row %)")
    print(row_percentages.to_string())


def print_open_market_summary(df: pd.DataFrame) -> None:
    open_market = df[df["market_segment"] == "open_market"].copy()
    grouped = (
        open_market.groupby("floor_area_imputed")
        .agg(
            count=("floor_area_imputed", "size"),
            mean=("price_per_sqm", "mean"),
            median=("price_per_sqm", "median"),
        )
        .reindex([0, 1])
    )

    print("\nOPEN MARKET ONLY: price_per_sqm by floor_area_imputed")
    print(grouped.to_string(float_format=lambda value: f"{value:,.2f}"))


def print_point_biserial(df: pd.DataFrame) -> None:
    valid = df[["floor_area_imputed", "price_per_sqm"]].dropna().copy()
    valid["floor_area_imputed"] = valid["floor_area_imputed"].astype(int)

    print("\nPOINT-BISERIAL CORRELATION: floor_area_imputed vs price_per_sqm")
    if valid["floor_area_imputed"].nunique() < 2:
        print("Not computed: floor_area_imputed has fewer than 2 groups.")
        return

    correlation, p_value = pointbiserialr(valid["floor_area_imputed"], valid["price_per_sqm"])
    print(f"r = {correlation:.4f}")
    print(f"p-value = {p_value:.4g}")


def print_recommendation(df: pd.DataFrame) -> None:
    imputed_market_counts = df.loc[df["floor_area_imputed"] == 1, "market_segment"].value_counts()

    if imputed_market_counts.empty:
        recommendation = "KEEP flag"
    else:
        dominant_share = imputed_market_counts.max() / imputed_market_counts.sum()
        recommendation = "DROP flag" if dominant_share >= 0.60 else "KEEP flag"

    print(f"\nRECOMMENDATION: {recommendation}")


def main() -> None:
    df = pd.read_csv(ABT_PATH)
    df["floor_area_imputed"] = df["floor_area_imputed"].astype(int)

    total_rows = len(df)
    imputed_rows = int((df["floor_area_imputed"] == 1).sum())

    print(f"TOTAL ROWS: {total_rows:,}")
    print(f"ROWS WHERE floor_area_imputed == 1: {imputed_rows:,}")

    print_crosstab(df, "market_segment")
    print_crosstab(df, "property_type")
    print_open_market_summary(df)
    print_point_biserial(df)
    print_recommendation(df)


if __name__ == "__main__":
    main()
