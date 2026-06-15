"""Cleanup the final ABT and restrict it to open_market rows only."""

import os

import pandas as pd


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
THESIS_DIR = os.path.dirname(SCRIPT_DIR)
ABT_PATH = os.path.join(THESIS_DIR, "Data", "processed", "abt_clean.csv")


def main() -> None:
    df = pd.read_csv(ABT_PATH)
    print(f"Loaded ABT: {len(df):,} rows x {df.shape[1]} columns")

    # Fix 1 - Drop non-open_market rows
    before = len(df)
    df = df[df["market_segment"] == "open_market"].copy()
    print(
        f"Fix 1 - Dropped non-open_market rows: {before - len(df)} rows removed "
        f"({len(df)} remaining)"
    )

    # Fix 2 - Drop property ID 1967 (implausible price)
    before = len(df)
    df = df[df["property_id"] != 1967].copy()
    print(
        "Fix 2 - Dropped property_id 1967 (PHP 14.3M/sqm data error): "
        f"{before - len(df)} rows removed"
    )

    # Fix 3 - Drop commercial lot contamination
    before = len(df)
    comm_mask = (
        (df["property_type"] == "Vacant Lot")
        & (df["property_name"].str.contains("commercial", case=False, na=False))
    )
    dropped_ids = df.loc[comm_mask, "property_id"].tolist()
    df = df[~comm_mask].copy()
    print(f"Fix 3 - Dropped commercial lot contamination: {before - len(df)} rows removed")
    print(f"  Dropped property_ids: {dropped_ids}")

    # Fix 4 - Reclassify misclassified penthouse units
    mask = df["property_id"].isin([707, 386]) & (df["property_type"] != "Condominium")
    changed = int(mask.sum())
    df.loc[mask, "property_type"] = "Condominium"
    print(
        "Fix 4 - Reclassified property_ids [707, 386] from Single Detached -> Condominium: "
        f"{changed} rows changed"
    )

    print("\n=== FINAL ABT STATE ===")
    print(f"Total rows: {len(df)}")
    print(f"Columns: {df.shape[1]}")
    print("\nProperty type breakdown:")
    print(df["property_type"].value_counts())
    print("\nAll market_segment values (should be only open_market):")
    print(df["market_segment"].value_counts())
    print("\nCity breakdown:")
    print(df["city"].value_counts())

    df.to_csv(ABT_PATH, index=False)
    print(f"\nSaved to {ABT_PATH}")


if __name__ == "__main__":
    main()
