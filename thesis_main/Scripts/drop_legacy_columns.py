"""
drop_legacy_columns.py

- Drops fully-null legacy columns: dist_cbd_m, bir_zonal_value, valuation_gap
- Regenerates valuation_gap = price_per_sqm - bir_zonal_rr_median
  (positive = above BIR benchmark, negative = below)
- Operates on abt_clean.csv in-place.
"""

from pathlib import Path
import pandas as pd

ABT_PATH = Path("thesis_main/Data/processed/abt_clean.csv")

DROP_COLS = ["dist_cbd_m", "bir_zonal_value", "valuation_gap"]


def main():
    abt = pd.read_csv(ABT_PATH)
    print(f"Input:  {len(abt):,} rows × {abt.shape[1]} columns")

    # 1. Drop legacy columns
    existing = [c for c in DROP_COLS if c in abt.columns]
    abt.drop(columns=existing, inplace=True)
    print(f"Dropped: {existing}")

    # 2. Regenerate valuation_gap from bir_zonal_rr_median
    #    valuation_gap = price_per_sqm - bir_zonal_rr_median
    #    positive  → property priced above BIR residential benchmark
    #    negative  → property priced below BIR residential benchmark
    abt["valuation_gap"] = abt["price_per_sqm"] - abt["bir_zonal_rr_median"]

    null_gap = abt["valuation_gap"].isna().sum()
    print(f"\nvaluation_gap regenerated from bir_zonal_rr_median")
    print(f"  Nulls: {null_gap}")
    print(f"  Mean gap: PHP {abt['valuation_gap'].mean():,.0f} / sqm")
    print(f"  Median gap: PHP {abt['valuation_gap'].median():,.0f} / sqm")

    print(f"\nOutput: {len(abt):,} rows × {abt.shape[1]} columns")

    abt.to_csv(ABT_PATH, index=False)
    print(f"Saved:  {ABT_PATH}")


if __name__ == "__main__":
    main()
