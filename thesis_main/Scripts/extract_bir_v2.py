"""
extract_bir_exact.py  (v2)
--------------------------
Extracts BIR zonal values from 7 pre-isolated xlsx files into one CSV.

Formats handled:
  A -- 4-col, single-cell marker: "CITY/MUNICIPALITY : NAME" in col 0
  B -- 4-col, split marker: "City/Municipality" col 0 | ": NAME" col 1
  C -- 7/10-col wide: "City/Municipality" col 0 | ":" col 1 | name col 2
       also handles "Barangay" (not "Zone/Barangay") as barangay marker (RDO81)

Column positions auto-detected from the header row containing 'CLASSIFICATION'.

Run from workspace root:
  python3 thesis_main/Scripts/extract_bir_v2.py
"""

import re
import sys
from pathlib import Path

import pandas as pd
import openpyxl

FILES = [
    ("RDO No. 80 Sheet 11.xlsx", " Sheet 11 (DO 23-2022)", 80),
    ("RDO No. 80 Sheet 10.xlsx", "Sheet 10 (DO 20-2020",   80),
    ("RDO No. 80 Sheet 9.xlsx",  "Sheet 9 (DO 90-2019)",   80),
    ("RDO No. 81 Sheet 6.xlsx",  "Sheet 6 (DO 054-2023)",  81),
    ("RDO No. 82 Sheet 6.xlsx",  "Sheet 6 (DO 86-2023)",   82),
    ("RDO No. 83 Sheet 7.xlsx",  "Sheet 7 (032-20)",       83),
    ("RDO No. 83 Sheet 8.xlsx",  "RDO No. 83 Sheet 8",     83),
]

VALID_CLS = re.compile(
    r"^(RR|CR|RC|CC|CL|GL|GP|I|X|APD|PS|A\d+)[\s*]*$",
    re.IGNORECASE,
)


def cv(cell) -> str:
    if cell is None:
        return ""
    s = str(cell).strip()
    return "" if s.lower() == "none" else s


def is_city_marker(row) -> bool:
    return any(re.search(r"city[\s/]*municipality", cv(c), re.IGNORECASE) for c in row)


def is_barangay_marker(row) -> bool:
    # RDO 81 uses "Barangay" alone (no "Zone/" prefix)
    if row and re.fullmatch(r"barangay", cv(row[0]), re.IGNORECASE):
        return True
    joined = " ".join(cv(c) for c in row).upper()
    return bool(re.search(r"ZONE[\s/]*BARANGAY", joined))


def extract_name_from_row(row, marker_col: int) -> str:
    cell_text = cv(row[marker_col])
    if ":" in cell_text:
        name = cell_text.split(":", 1)[1].strip()
        if name:
            return name
    for c in range(marker_col + 1, len(row)):
        val = cv(row[c])
        if val == ":":
            continue
        if val.startswith(":"):
            val = val[1:].strip()
        if val and not re.search(
            r"city[\s/]*municipality|zone[\s/]*barangay|^barangay$|effectivity|d\.?o\.?\s*no",
            val,
            re.IGNORECASE,
        ):
            return val
    return ""


def detect_col_positions(rows):
    """Return (street_col, vicinity_col, classification_col, value_col).

    The true header row has 'CLASSIFICATION' as the primary label in that cell
    (not 'CODE ... CLASSIFICATION' legend rows).  We require:
      - CLASSIF appears at idx > 0
      - The cell does NOT start with 'CODE'
      - The row also contains 'STREET' or 'SUBDIVISION' somewhere (sanity check)
    Falls back to (0, 1, 2, 3).
    """
    for row in rows:
        row_upper = [cv(c).upper() for c in row]
        has_street = any("STREET" in v or "SUBDIV" in v for v in row_upper)
        for idx, val in enumerate(row_upper):
            if "CLASSIF" in val and idx > 0 and not val.startswith("CODE"):
                if has_street:
                    c_col = idx
                    z_col = idx + 1
                    v_col = next(
                        (i for i, v in enumerate(row_upper) if "VICIN" in v),
                        c_col - 1,
                    )
                    if v_col < 0:
                        v_col = 1
                    return 0, v_col, c_col, z_col
    return 0, 1, 2, 3


def clean_cls(raw: str) -> str:
    return re.sub(r"[\s*]+$", "", raw.strip())


def parse_value(raw) -> float:
    s = cv(raw)
    if not s or re.fullmatch(r"\*+", s):
        return float("nan")
    try:
        return float(s)
    except ValueError:
        return float("nan")


def is_separator(row) -> bool:
    vals = [cv(c) for c in row if cv(c)]
    return not vals or all(re.fullmatch(r"[-\u2013\u2014]+", v) for v in vals)


def parse_sheet(filepath: str, sheet_name: str, rdo: int) -> list:
    wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
    ws = wb[sheet_name]
    rows = [tuple(r) for r in ws.iter_rows(values_only=True)]
    wb.close()

    s_col, v_col, c_col, z_col = detect_col_positions(rows)

    current_city = ""
    current_brgy = ""
    last_street = ""
    records = []

    for row in rows:
        if is_separator(row):
            continue

        if is_city_marker(row):
            for idx, cell in enumerate(row):
                if re.search(r"city[\s/]*municipality", cv(cell), re.IGNORECASE):
                    name = extract_name_from_row(row, idx)
                    if name:
                        current_city = name
                    current_brgy = last_street = ""
                    break
            continue

        if is_barangay_marker(row):
            for idx, cell in enumerate(row):
                cv_cell = cv(cell)
                is_brgy_cell = (
                    re.fullmatch(r"barangay", cv_cell, re.IGNORECASE)
                    or "BARANGAY" in cv_cell.upper()
                )
                if is_brgy_cell:
                    name = extract_name_from_row(row, idx)
                    if name:
                        current_brgy = name
                    last_street = ""
                    break
            continue

        if not current_brgy:
            continue
        if c_col >= len(row):
            continue

        cls = clean_cls(cv(row[c_col]))
        if not VALID_CLS.match(cls):
            continue

        street = cv(row[s_col]) if s_col < len(row) else ""
        vicinity = cv(row[v_col]) if v_col < len(row) else ""
        zval = parse_value(row[z_col] if z_col < len(row) else None)

        if not street:
            street = last_street
        else:
            last_street = street

        records.append(
            {
                "rdo": rdo,
                "city_municipality": current_city,
                "barangay": current_brgy,
                "street_subdivision": street,
                "vicinity": vicinity,
                "classification": cls,
                "zonal_value": zval,
            }
        )

    return records


def main():
    workspace = Path.cwd()
    bir_dir = workspace / "thesis_main" / "Data" / "BIR Zonal Values" / "exact-RDO-files"
    out_path = (
        workspace / "thesis_main" / "Data" / "BIR Zonal Values" / "bir_zonal_extracted_all.csv"
    )

    if not bir_dir.exists():
        print(f"ERROR: directory not found: {bir_dir}")
        sys.exit(1)

    all_records = []
    for fname, sheet, rdo in FILES:
        fpath = bir_dir / fname
        print(f"Processing: {fname}  (sheet: {sheet!r})")
        records = parse_sheet(str(fpath), sheet, rdo)
        cities = len({r["city_municipality"] for r in records})
        brgys = len({r["barangay"] for r in records})
        print(f"  -> {len(records):>6} rows | {cities} cities | {brgys} barangays")
        all_records.extend(records)

    df = pd.DataFrame(
        all_records,
        columns=[
            "rdo",
            "city_municipality",
            "barangay",
            "street_subdivision",
            "vicinity",
            "classification",
            "zonal_value",
        ],
    )
    df.to_csv(out_path, index=False)

    print(f"\n{'='*60}")
    print(f"Total rows:       {len(df)}")
    print(f"Unique cities:    {df['city_municipality'].nunique()}")
    print(f"Unique barangays: {df['barangay'].nunique()}")
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    main()
