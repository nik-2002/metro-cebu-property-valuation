"""
flag_ropa_outliers.py

Fills price_outlier_flag for bank ROPA rows using the same rule as build_abt.py:
flag = True if price_php < 1st percentile OR > 99th percentile of the full ABT.

Operates on abt_clean.csv in-place.
"""

from pathlib import Path
import pandas as pd

ABT_PATH = Path("thesis_main/Data/processed/abt_clean.csv")

BANK_ROPA_SOURCES = {"BPI", "Metrobank", "Bank of Commerce", "China Bank Savings", "Landbank"}


def main():
    abt = pd.read_csv(ABT_PATH)
    print(f"Input:  {len(abt):,} rows × {abt.shape[1]} columns")

    # Current state
    null_count = abt["price_outlier_flag"].isna().sum()
    print(f"Rows with null price_outlier_flag: {null_count}")

    # Compute p01/p99 from the full ABT (same method as build_abt.py)
    p01 = abt["price_php"].quantile(0.01)
    p99 = abt["price_php"].quantile(0.99)
    print(f"\nPrice thresholds (1st–99th pct of full ABT):")
    print(f"  p01 = PHP {p01:,.0f}")
    print(f"  p99 = PHP {p99:,.0f}")

    # Fill nulls for bank ROPA rows
    ropa_mask = abt["source"].isin(BANK_ROPA_SOURCES) & abt["price_outlier_flag"].isna()
    abt.loc[ropa_mask, "price_outlier_flag"] = ~abt.loc[ropa_mask, "price_php"].between(p01, p99)

    # Convert to bool (pandas may store as object after fillna)
    abt["price_outlier_flag"] = abt["price_outlier_flag"].astype(bool)

    # Report
    still_null = abt["price_outlier_flag"].isna().sum()
    flagged_ropa = abt.loc[abt["source"].isin(BANK_ROPA_SOURCES), "price_outlier_flag"].sum()
    print(f"\nRows still null after fill: {still_null}")
    print(f"Bank ROPA rows flagged as outliers: {flagged_ropa}")
    print(f"\nOverall price_outlier_flag summary:")
    print(abt.groupby("source")["price_outlier_flag"].agg(["sum", "count"]).rename(
        columns={"sum": "flagged", "count": "total"}
    ).to_string())

    abt.to_csv(ABT_PATH, index=False)
    print(f"\nSaved: {ABT_PATH}")


if __name__ == "__main__":
    main()
