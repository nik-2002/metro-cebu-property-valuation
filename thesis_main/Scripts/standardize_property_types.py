"""
standardize_property_types.py

Applies a unified residential property-type taxonomy to abt_clean.csv.
Non-residential rows (Commercial, Industrial) are dropped.
Writes abt_clean.csv in-place (overwrites).

Taxonomy
--------
Condominium      <- Residential - Condominium Unit, Condominium
House and Lot    <- Residential - House and Lot
Townhouse        <- Residential - Townhouse, Townhouse, Townhouse (End/Firewall),
                    Single Attached, Row House
Single Detached  <- Single Detached
Vacant Lot       <- Residential - Vacant Lot, Lot Only
Apartment        <- Apartment
Residential      <- Residential (unspecified label from Lamudi; kept as own category)

Dropped
-------
Commercial - Condominium Unit, Commercial - with Improvements, Industrial - Vacant Lot
"""

from pathlib import Path
import pandas as pd

ABT_PATH = Path(
    "thesis_main/Data/processed/abt_clean.csv"
)

# Labels to drop outright (non-residential)
DROP_TYPES = {
    "Commercial - Condominium Unit",
    "Commercial - with Improvements",
    "Industrial - Vacant Lot",
}

# Map from raw label → canonical label
TAXONOMY = {
    # Condominium
    "Residential - Condominium Unit": "Condominium",
    "Condominium": "Condominium",
    # House and Lot
    "Residential - House and Lot": "House and Lot",
    # Townhouse / attached variants
    "Residential - Townhouse": "Townhouse",
    "Townhouse": "Townhouse",
    "Townhouse (End/Firewall)": "Townhouse",
    "Single Attached": "Townhouse",
    "Row House": "Townhouse",
    # Single detached
    "Single Detached": "Single Detached",
    # Vacant lot
    "Residential - Vacant Lot": "Vacant Lot",
    "Lot Only": "Vacant Lot",
    # Apartment
    "Apartment": "Apartment",
    # Unspecified residential (Lamudi label)
    "Residential": "Residential",
}


def main():
    abt = pd.read_csv(ABT_PATH)
    print(f"Input:  {len(abt):,} rows × {abt.shape[1]} columns")

    # 1. Drop non-residential rows
    mask_drop = abt["property_type"].isin(DROP_TYPES)
    if mask_drop.any():
        dropped = abt.loc[mask_drop, "property_type"].value_counts()
        print(f"\nDropping {mask_drop.sum()} non-residential rows:")
        for pt, n in dropped.items():
            print(f"  {pt}: {n}")
        abt = abt[~mask_drop].copy()
    else:
        print("\nNo non-residential rows found.")

    # 2. Remap labels
    unmapped = abt.loc[~abt["property_type"].isin(TAXONOMY), "property_type"].unique()
    if len(unmapped):
        raise ValueError(f"Unmapped property_type values: {list(unmapped)}")

    abt["property_type"] = abt["property_type"].map(TAXONOMY)

    # 3. Report
    print(f"\nProperty type breakdown after standardization:")
    print(abt["property_type"].value_counts().to_string())

    print(f"\nOutput: {len(abt):,} rows × {abt.shape[1]} columns")

    # 4. Overwrite abt_clean.csv
    abt.to_csv(ABT_PATH, index=False)
    print(f"Saved:  {ABT_PATH}")


if __name__ == "__main__":
    main()
