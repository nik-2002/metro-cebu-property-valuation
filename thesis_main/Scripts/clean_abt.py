"""
clean_abt.py
------------
Applies scope and column cleanup to the raw analytics base table.

Steps:
  1. Filter rows to the 6 in-scope Metro Cebu LGUs.
  2. Drop dist_cbrt_nearest_m (CBRT route not yet active; removed from feature set).
  3. Write cleaned ABT to Data/processed/abt_clean.csv.
"""

from pathlib import Path
import pandas as pd

INPUT_PATH  = Path("thesis_main/Data/processed/analytics_base_table.csv")
OUTPUT_PATH = Path("thesis_main/Data/processed/abt_clean.csv")

IN_SCOPE_LGUS = {
    "Cebu City",
    "Mandaue City",
    "Lapu-Lapu City",
    "Talisay City",
    "Consolacion",
    "Minglanilla",
}

DROP_COLUMNS = [
    "dist_cbrt_nearest_m",
]


def main():
    abt = pd.read_csv(INPUT_PATH)
    print(f"Input:  {len(abt):,} rows × {len(abt.columns)} columns")

    # --- 1. Geographic scope filter ---
    out_of_scope = ~abt["city"].isin(IN_SCOPE_LGUS)
    dropped_cities = abt.loc[out_of_scope, "city"].value_counts()
    if dropped_cities.empty:
        print("Geographic filter: no out-of-scope rows found.")
    else:
        print(f"\nDropping {out_of_scope.sum()} out-of-scope rows:")
        for city, n in dropped_cities.items():
            print(f"  {city}: {n}")

    abt = abt[~out_of_scope].copy()

    # --- 2. Drop retired columns ---
    existing_drops = [c for c in DROP_COLUMNS if c in abt.columns]
    if existing_drops:
        abt.drop(columns=existing_drops, inplace=True)
        print(f"\nDropped columns: {existing_drops}")
    else:
        print("\nNo columns to drop (already absent).")

    # --- 3. Write output ---
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    abt.to_csv(OUTPUT_PATH, index=False)
    print(f"\nOutput: {len(abt):,} rows × {len(abt.columns)} columns")
    print(f"Saved:  {OUTPUT_PATH}")

    print("\nCity breakdown:")
    print(abt["city"].value_counts().to_string())


if __name__ == "__main__":
    main()
