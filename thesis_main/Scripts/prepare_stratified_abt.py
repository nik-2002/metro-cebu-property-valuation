"""Prepare stratum-specific ABT CSVs for the Decision 31 modeling workflow."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
THESIS_DIR = SCRIPT_DIR.parent
PROCESSED_DIR = THESIS_DIR / "Data" / "processed"
ABT_PATH = PROCESSED_DIR / "abt_clean.csv"

STARTING_SHAPE = (1579, 51)

COMMON_FEATURES = [
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
]

PHYSICAL_FEATURES = {
    "Condo": ["area_sqm", "bedrooms", "bathrooms", "bedrooms_imputed", "bathrooms_imputed"],
    "Houses": ["area_sqm", "bedrooms", "bathrooms", "bedrooms_imputed", "bathrooms_imputed"],
    "Lot": ["area_sqm"],
}

KEEP_META = [
    "property_id",
    "price_type",
    "property_name",
    "address",
    "city",
    "property_type",
    "latitude",
    "longitude",
    "price_php",
    "price_per_sqm",
    "log_price",
    "valuation_gap",
]

DROP_COLUMNS = [
    "lot_area_sqm",
    "floor_area_sqm",
    "floor_area_imputed",
    "bir_zonal_rc_median",
    "source",
    "market_segment",
    "stratum",
    "is_vacant_lot",
    "barangay_geocoded",
    "price_outlier_flag",
    "geocode_source",
]

STRATUM_MAP = {
    "Condominium": "Condo",
    "Vacant Lot": "Lot",
    "Single Detached": "Houses",
    "House and Lot": "Houses",
    "Townhouse": "Houses",
    "Apartment": "Houses",
}


def write_csv_atomic(path: Path, frame: pd.DataFrame) -> None:
    temp_path = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temp_path, index=False)
    os.replace(temp_path, path)


def dedupe_preserve_order(columns: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for column in columns:
        if column in seen:
            continue
        seen.add(column)
        ordered.append(column)
    return ordered


def audit_source_frame(frame: pd.DataFrame) -> None:
    print(f"Starting shape: {frame.shape}")
    if frame.shape != STARTING_SHAPE:
        print(f"  Note: expected {STARTING_SHAPE} based on Decision 31 audit.")

    if not frame["area_sqm"].equals(frame["floor_area_sqm"]):
        raise AssertionError("area_sqm and floor_area_sqm are not identical.")

    if not frame["lot_area_sqm"].isna().all():
        raise AssertionError("lot_area_sqm is not 100% null.")

    present_drop = [c for c in DROP_COLUMNS if c in frame.columns]
    print(f"DROP_COLUMNS present in master: {len(present_drop)} of {len(DROP_COLUMNS)}: {present_drop}")
    print("Audit checks passed: area_sqm matches floor_area_sqm, lot_area_sqm is 100% null.")


def add_stratum(frame: pd.DataFrame) -> pd.DataFrame:
    stratum = frame["property_type"].map(STRATUM_MAP)
    if stratum.isna().any():
        missing_types = sorted(frame.loc[stratum.isna(), "property_type"].unique().tolist())
        raise ValueError(f"Unmapped property_type values: {missing_types}")

    result = frame.copy()
    result["stratum"] = stratum
    return result


def main() -> None:
    print(f"Loading master ABT: {ABT_PATH}")
    master = pd.read_csv(ABT_PATH)
    present_drop = [c for c in DROP_COLUMNS if c in master.columns]

    print("\nStep 1 - Load and audit")
    audit_source_frame(master)

    print("\nStep 2 - Drop retired columns from working frame")
    working = master.drop(columns=present_drop).copy()
    print(f"Dropped columns: {len(present_drop)}")
    print(f"Remaining columns: {working.shape[1]}")

    print("\nStep 3 - Row-level cleanup")
    before_area = len(working)
    working = working.loc[working["area_sqm"].notna()].copy()
    n_area_null = before_area - len(working)
    print(f"After dropping null area_sqm rows: {len(working):,}")

    before_price = len(working)
    working = working.loc[working["price_per_sqm"].notna()].copy()
    n_price_null = before_price - len(working)
    print(f"After dropping null price_per_sqm rows: {len(working):,}")

    # Decision 31: property_id 769 (PHP 5/sqm Single Detached anomaly).
    # Decision 32: property_id 843 (Condo, 3949 sqm with imputed 1bed/1bath — bulk listing miscategorized);
    #              property_id 1989 (Houses, bedrooms field=40 — scraper field-shift error).
    # 2026-06-03 audit (post log_price fix): drop impossible condos and whole-building apartments:
    #   621  (Condo, total PHP 25k -> 714/sqm, junk price field)
    #   1292 (Condo, 2898 sqm area -> 966/sqm, impossible condo area)
    #   1500, 1928, 1959 (Condominium-typed but whole apartment BUILDINGS; bedrooms = unit count,
    #                     non-comparable to single residential units — dropped per author)
    OUTLIER_IDS = [769, 843, 1989, 621, 1292, 1500, 1928, 1959]
    before_anomaly = len(working)
    working = working.loc[~working["property_id"].isin(OUTLIER_IDS)].copy()
    anomaly_drop = before_anomaly - len(working)
    print(f"After dropping outlier rows {OUTLIER_IDS}: {len(working):,}")
    print(
        "Rows dropped: "
        f"{n_area_null} for null area, "
        f"{n_price_null} for null price_per_sqm, "
        f"{anomaly_drop} for outlier IDs {OUTLIER_IDS}."
    )

    print("\nStep 3b - Drop hard duplicate listings")
    working = working.sort_values("property_id").reset_index(drop=True)
    before_dedup = len(working)
    working = working.drop_duplicates(
        subset=["latitude", "longitude", "area_sqm", "price_per_sqm"],
        keep="first",
    ).copy()
    n_deduped = before_dedup - len(working)
    print(f"Hard duplicates dropped: {n_deduped}")
    print(f"After deduplication: {len(working):,} rows")
    print(f"Decision 33 deduplication complete. Rows dropped: {n_deduped}")

    print("\nStep 3c - Recompute log_price target as log(price_per_sqm)")
    # Bug fix (2026-06-03): the Phase C merge stored log_price = log(price_per_sqm) while the
    # original build stored log(total price). The target is redefined to log(price_per_sqm) for
    # ALL rows (matches the price-per-sqm deliverable + CLAUDE.md target; avoids area-amplification;
    # see modeling_decisions.md). price_per_sqm is clean and non-null at this point.
    working["log_price"] = np.log(working["price_per_sqm"])
    print(f"  log_price recomputed from price_per_sqm for {len(working):,} rows")

    print("\nStep 3d - Repair corrupt bedroom field (property_id 2151)")
    # property_id 2151: bedrooms=378 is a scraper field-shift error; the row is otherwise valid
    # (Cebu City house, PHP 22M, 73k/sqm). Impute with the house-stratum median bedrooms and flag it.
    house_types = ["Single Detached", "House and Lot", "Townhouse", "Apartment"]
    bad_bed = working["property_id"] == 2151
    if bad_bed.any():
        med_bed = working.loc[
            working.property_type.isin(house_types) & (working.bedrooms <= 20), "bedrooms"
        ].median()
        working.loc[bad_bed, "bedrooms"] = med_bed
        working.loc[bad_bed, "bedrooms_imputed"] = 1
        print(f"  property_id 2151 bedrooms 378 -> {med_bed:.0f} (house median); bedrooms_imputed=1")

    print("\nStep 4 - Define strata")
    working = add_stratum(working)
    stratum_counts = working["stratum"].value_counts().reindex(["Condo", "Houses", "Lot"]).fillna(0).astype(int)
    for stratum, count in stratum_counts.items():
        print(f"  {stratum:<6} {count:,} rows")

    print("\nStep 5 - Define common feature set")
    print(f"COMMON_FEATURES count: {len(COMMON_FEATURES)}")

    print("\nStep 6 - Define stratum-specific physical features")
    for stratum, columns in PHYSICAL_FEATURES.items():
        print(f"  {stratum:<6} {len(columns)} physical columns")

    print("\nStep 7 - Define metadata columns to keep")
    print(f"KEEP_META count: {len(KEEP_META)}")

    print("\nStep 8 - Write stratum CSVs")
    outputs: list[tuple[str, Path, tuple[int, int]]] = []
    for stratum in ["Condo", "Houses", "Lot"]:
        stratum_frame = working.loc[working["stratum"] == stratum].copy()

        # Decision 41 - Vacant Lot residential-scope + data-quality filter.
        # The raw lot stratum spans a 241x price-per-sqm range (PHP 1.3k -> 313.5k) because it
        # mixes genuine residential lots with development/agricultural parcels and a few data
        # errors. This breaks honest evaluation (MAPE blows up on cheap denominators) and mixes
        # two valuation regimes. Filters (each independently defensible):
        #   1. area_sqm <= 2000  -> residential-lot scope. PH subdivision lots are ~100-500 sqm
        #      (estate lots to ~1.5k); above ~2000 sqm parcels are subdivision-scale raw/dev land
        #      priced on a bulk discount (median price/sqm collapses from ~51k at 600-1000 sqm to
        #      ~16.5k above 5000 sqm). Out of scope for a residential valuation model.
        #   2. area_sqm >= 80    -> drop micro-parcels (e.g., a 50 sqm "lot" at 280k/sqm) that are
        #      mislabeled units/slots, not residential land.
        #   3. price_per_sqm >= 0.5 * bir_zonal_rr_median -> data-quality. The BIR zonal value is
        #      the legal valuation floor; genuine arm's-length residential land transacts at/above
        #      it. Rows below half the zonal floor are data errors or non-arm's-length sales.
        if stratum == "Lot":
            before = len(stratum_frame)
            scope = stratum_frame["area_sqm"].between(80, 2000)
            quality = (
                stratum_frame["price_per_sqm"]
                >= 0.5 * stratum_frame["bir_zonal_rr_median"]
            )
            stratum_frame = stratum_frame.loc[scope & quality].copy()
            n_scope = int((~scope).sum())
            n_quality = int((scope & ~quality).sum())
            print(
                f"  Lot scope/quality filter: {before} -> {len(stratum_frame)} "
                f"(dropped {n_scope} out-of-scope by area, {n_quality} below 0.5x BIR zonal floor)"
            )

        ordered_columns = dedupe_preserve_order(KEEP_META + PHYSICAL_FEATURES[stratum] + COMMON_FEATURES)
        missing_columns = [column for column in ordered_columns if column not in stratum_frame.columns]
        if missing_columns:
            raise KeyError(f"Missing expected columns for {stratum}: {missing_columns}")

        output_frame = stratum_frame.loc[:, ordered_columns].copy()
        output_path = PROCESSED_DIR / f"abt_{stratum.lower()}.csv"
        write_csv_atomic(output_path, output_frame)

        print(f"  Wrote {output_path.name}: shape={output_frame.shape}")
        preview = output_frame.head(3).to_string(index=False)
        print(preview)
        outputs.append((stratum, output_path, output_frame.shape))

    print("\nStep 9 - Final summary")
    print(f"{'Stratum':<8} {'Rows':>6} {'Cols':>6}  Output")
    for stratum, output_path, shape in outputs:
        print(f"{stratum:<8} {shape[0]:>6,} {shape[1]:>6,}  {output_path}")

    print("Decision 33 cleanup complete. Modeling can proceed with the three stratum CSVs.")


if __name__ == "__main__":
    main()
