"""
standardize_property_types.py

Applies a unified residential property-type taxonomy to abt_clean.csv.
Non-residential rows (Commercial, Industrial, office/commercial leakage inside
Lamudi's generic Residential label) are dropped. Writes abt_clean.csv in-place.

Taxonomy
--------
Condominium      <- Residential - Condominium Unit, Condominium,
                    Residential (studio / condo-like listing title)
House and Lot    <- Residential - House and Lot
Townhouse        <- Residential - Townhouse, Townhouse, Townhouse (End/Firewall),
                    Single Attached, Row House
Single Detached  <- Single Detached, Residential (villa / house listing title)
Vacant Lot       <- Residential - Vacant Lot, Lot Only,
                    Residential (land / lot listing title)
Apartment        <- Apartment

Dropped
-------
Commercial - Condominium Unit, Commercial - with Improvements,
Industrial - Vacant Lot, Residential (office / commercial listing title)
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

# Map from raw label -> canonical label
TAXONOMY = {
    # Condominium
    "Residential - Condominium Unit": "Condominium",
    "Condominium": "Condominium",
    # House and Lot
    "Residential - House and Lot": "House and Lot",
    "House and Lot": "House and Lot",
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
    "Vacant Lot": "Vacant Lot",
    # Apartment
    "Apartment": "Apartment",
}


def infer_residential_subtype(residential_rows: pd.DataFrame) -> pd.Series:
    """Resolve Lamudi's generic Residential label into defensible subtypes."""
    text = (
        residential_rows["property_name"].fillna("")
        + " "
        + residential_rows["address"].fillna("")
    ).str.lower()

    inferred = pd.Series(pd.NA, index=residential_rows.index, dtype="object")

    office_or_commercial = text.str.contains(
        r"\boffices?\b|\bcommercial\b", regex=True, na=False
    )
    land_or_lot = text.str.contains(r"\bland\b|\blot\b", regex=True, na=False)
    condo_like = text.str.contains(
        r"\bstudio\b|\bcondo\b|\bcondominium\b", regex=True, na=False
    )
    detached_like = text.str.contains(
        r"\bvilla\b|\bvillas\b|\bhouse\b", regex=True, na=False
    )

    inferred.loc[office_or_commercial] = "__DROP__"
    inferred.loc[inferred.isna() & land_or_lot] = "Vacant Lot"
    inferred.loc[inferred.isna() & condo_like] = "Condominium"
    inferred.loc[inferred.isna() & detached_like] = "Single Detached"

    unresolved = residential_rows.loc[
        inferred.isna(), ["property_id", "property_name", "city", "address"]
    ]
    if not unresolved.empty:
        preview = unresolved.head(10).to_dict("records")
        raise ValueError(
            "Unresolved Residential rows after title-based recode. "
            f"Review examples: {preview}"
        )

    return inferred


def main():
    abt = pd.read_csv(ABT_PATH)
    print(f"Input:  {len(abt):,} rows x {abt.shape[1]} columns")

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

    mask_residential = abt["property_type"].eq("Residential")
    if mask_residential.any():
        inferred = infer_residential_subtype(abt.loc[mask_residential].copy())
        print(
            f"\nResolving {mask_residential.sum()} generic Residential rows "
            "from Lamudi listing titles:"
        )
        print(inferred.value_counts().to_string())

        keep_mask = inferred.ne("__DROP__")
        abt.loc[inferred.index[keep_mask], "property_type"] = inferred.loc[keep_mask]
        abt = abt.drop(index=inferred.index[~keep_mask]).copy()

    # 2. Remap labels
    unmapped = abt.loc[~abt["property_type"].isin(TAXONOMY), "property_type"].unique()
    if len(unmapped):
        raise ValueError(f"Unmapped property_type values: {list(unmapped)}")

    abt["property_type"] = abt["property_type"].map(TAXONOMY)

    # 3. Report
    print("\nProperty type breakdown after standardization:")
    print(abt["property_type"].value_counts().to_string())

    print(f"\nOutput: {len(abt):,} rows x {abt.shape[1]} columns")

    # 4. Overwrite abt_clean.csv
    abt.to_csv(ABT_PATH, index=False)
    print(f"Saved:  {ABT_PATH}")


if __name__ == "__main__":
    main()
