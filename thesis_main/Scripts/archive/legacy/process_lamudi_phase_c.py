from __future__ import annotations

from pathlib import Path
import re

import pandas as pd

LAMUDI_PATH = Path("thesis_main/Data/webscraping-lamudi/lamudi_cebu_full.csv")
ABT_PATH = Path("thesis_main/Data/processed/abt_clean.csv")
OUTPUT_PATH = Path("thesis_main/Data/raw/phase_c_lamudi.csv")

CITY_MAP = {
    "Cebu": "Cebu City",
    "Cebu City": "Cebu City",
    "Lapu-Lapu": "Lapu-Lapu City",
    "Lapu-Lapu City": "Lapu-Lapu City",
    "Mandaue": "Mandaue City",
    "Mandaue City": "Mandaue City",
    "Talisay": "Talisay City",
    "Talisay City": "Talisay City",
    "Minglanilla": "Minglanilla",
    "Consolacion": "Consolacion",
    "Naga": "Naga City",
    "Naga City": "Naga City",
}

TYPE_RULES = [
    (r"\bcondo(?:minium)?\b|\bapartment\b|\bpenthouse\b|\bstudio\b", "Condominium"),
    (r"\bsingle[-\s]?detached\b|\bdetached\s+house\b", "Single Detached"),
    (r"\btownhouse\b|\bduplex\b|\browhouse\b|\bsingle[-\s]?attached\b", "Townhouse"),
    (r"\bvacant\s+lot\b|\blot\s+only\b|\bresidential\s+lot\b|\bland\s+for\s+sale\b", "Vacant Lot"),
    (r"\bhouse\s*(?:and|&)\s*lot\b|\bvilla\b|\bhouse\b", "House and Lot"),
    (r"\bresidential\b", "Residential"),
]

EXCLUDED_TITLE_PATTERN = re.compile(
    r"commercial|office|warehouse|farm|industrial|beach house",
    flags=re.IGNORECASE,
)

OUTPUT_COLUMNS = [
    "source",
    "property_name",
    "address",
    "city",
    "property_type",
    "lot_area_sqm",
    "floor_area_sqm",
    "bedrooms",
    "bathrooms",
    "price_php",
    "latitude",
    "longitude",
    "listing_url",
    "market_segment",
]


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def combo_key(left: object, right: object) -> tuple[str, str]:
    return (normalize_text(left).casefold(), normalize_text(right).casefold())


def parse_price(value: object) -> float | None:
    if pd.isna(value):
        return None
    cleaned = re.sub(r"[^0-9.]", "", str(value))
    if not cleaned:
        return None
    try:
        parsed = float(cleaned)
    except ValueError:
        return None
    if parsed <= 0:
        return None
    return parsed


def infer_property_type(title: object) -> str | None:
    title_text = normalize_text(title)
    if not title_text:
        return None
    if EXCLUDED_TITLE_PATTERN.search(title_text):
        return None
    for pattern, label in TYPE_RULES:
        if re.search(pattern, title_text, flags=re.IGNORECASE):
            return label
    return None


def main() -> None:
    lamudi = pd.read_csv(LAMUDI_PATH, encoding="utf-8")

    lamudi = lamudi.dropna(subset=["price", "latitude", "longitude"]).copy()
    lamudi["latitude"] = pd.to_numeric(lamudi["latitude"], errors="coerce")
    lamudi["longitude"] = pd.to_numeric(lamudi["longitude"], errors="coerce")
    lamudi = lamudi.dropna(subset=["latitude", "longitude"]).copy()
    lamudi["price_php"] = lamudi["price"].map(parse_price)
    lamudi = lamudi[lamudi["price_php"].notna()].copy()
    print(f"Rows after price/latlon filter: {len(lamudi)}")

    before_price_bounds = len(lamudi)
    lamudi = lamudi[lamudi["price_php"].between(500_000, 500_000_000, inclusive="both")].copy()
    print(f"Rows dropped by price bounds filter: {before_price_bounds - len(lamudi)}")

    lamudi["city"] = lamudi["city"].map(CITY_MAP)
    lamudi = lamudi[lamudi["city"].notna()].copy()
    print(f"Rows after city filter: {len(lamudi)}")

    lamudi["property_type"] = lamudi["title"].map(infer_property_type)
    lamudi = lamudi[lamudi["property_type"].notna()].copy()
    print(f"Rows after property type filter: {len(lamudi)}")

    lamudi["rounded_lat"] = lamudi["latitude"].round(4)
    lamudi["rounded_lon"] = lamudi["longitude"].round(4)
    before_spatial_cap = len(lamudi)
    lamudi = (
        lamudi.sort_values(["rounded_lat", "rounded_lon", "price_php"], kind="stable")
        .groupby(["rounded_lat", "rounded_lon"], sort=False, group_keys=False)
        .head(3)
        .copy()
    )
    spatial_dropped = before_spatial_cap - len(lamudi)
    print(f"Rows after spatial cap (dropped {spatial_dropped}): {len(lamudi)}")

    abt = pd.read_csv(ABT_PATH, usecols=["property_name", "address"])
    existing_keys = {
        combo_key(row.property_name, row.address)
        for row in abt.itertuples(index=False)
    }

    lamudi = lamudi[
        ~lamudi.apply(
            lambda row: combo_key(row["title"], row["street_address"]) in existing_keys,
            axis=1,
        )
    ].copy()

    lamudi = lamudi.drop_duplicates(
        subset=["street_address", "price_php", "property_type"],
        keep="first",
    ).copy()
    print(f"Rows after ABT dedup: {len(lamudi)}")

    lamudi["source"] = "Lamudi"
    lamudi["property_name"] = lamudi["title"]
    lamudi["address"] = lamudi["street_address"]
    lamudi["lot_area_sqm"] = pd.NA
    lamudi["floor_area_sqm"] = pd.to_numeric(lamudi["floor_area_sqm"], errors="coerce")
    lamudi["bedrooms"] = pd.to_numeric(lamudi["bedrooms"], errors="coerce")
    lamudi["bathrooms"] = pd.to_numeric(lamudi["bathrooms"], errors="coerce")
    lamudi["listing_url"] = lamudi["url"]
    lamudi["market_segment"] = "open_market"

    output = lamudi[
        [
            "source",
            "property_name",
            "address",
            "city",
            "property_type",
            "lot_area_sqm",
            "floor_area_sqm",
            "bedrooms",
            "bathrooms",
            "price_php",
            "latitude",
            "longitude",
            "listing_url",
            "market_segment",
        ]
    ].copy()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_PATH, index=False)

    print(f"Final rows written: {len(output)}")
    print(f"Rows per city: {output['city'].value_counts().sort_index().to_dict()}")
    print(f"Rows per property_type: {output['property_type'].value_counts().sort_index().to_dict()}")


if __name__ == "__main__":
    main()
