"""
generate_abt_snapshot_image.py
==============================
Render a spreadsheet-style snapshot image of the assembled ABT (abt_clean.csv):
a representative slice of key columns over the first rows, so the appendix can
show what the raw analytics base table looks like. The ABT has 51 columns, so
this is an illustrative slice, not the full width.
Writes Manuscript/diagrams/abt_snapshot.png
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

THESIS = Path(__file__).resolve().parent.parent
ABT = THESIS / "Data" / "processed" / "abt_clean.csv"
OUT = THESIS / "Manuscript" / "diagrams" / "abt_snapshot.png"

COLS = ["property_id", "source", "city", "property_type", "area_sqm",
        "bedrooms", "bathrooms", "price_php", "price_per_sqm",
        "bir_zonal_rr_median", "mcrai_composite", "spatial_lag_price"]
HEADERS = ["id", "source", "city", "type", "area_sqm", "beds", "baths",
           "price_php", "price/sqm", "bir_zonal", "mcrai_comp", "spatial_lag"]
NROWS = 9

df = pd.read_csv(ABT, usecols=lambda c: c in COLS)[COLS].head(NROWS).copy()


def fmt(col, v):
    if pd.isna(v):
        return ""
    if col in ("price_php", "price_per_sqm", "bir_zonal_rr_median", "spatial_lag_price"):
        return f"{v:,.0f}"
    if col in ("area_sqm", "mcrai_composite"):
        return f"{v:,.1f}"
    if col in ("bedrooms", "bathrooms", "property_id"):
        return f"{int(v)}" if pd.notna(v) else ""
    s = str(v)
    return s[:18] + "…" if len(s) > 19 else s


cells = [[fmt(c, df.iloc[r][c]) for c in COLS] for r in range(len(df))]

fig, ax = plt.subplots(figsize=(13.5, 3.4))
ax.axis("off")
tbl = ax.table(cellText=cells, colLabels=HEADERS, loc="center", cellLoc="center")
tbl.auto_set_font_size(False)
tbl.set_fontsize(8.5)
tbl.scale(1, 1.5)
# header styling + zebra rows
for (r, c), cell in tbl.get_celld().items():
    cell.set_edgecolor("#cfcfcf")
    if r == 0:
        cell.set_facecolor("#34557a"); cell.set_text_props(color="white", fontweight="bold")
    elif r % 2 == 0:
        cell.set_facecolor("#f2f5f8")
tbl.auto_set_column_width(col=list(range(len(COLS))))
fig.tight_layout()
fig.savefig(OUT, dpi=200, bbox_inches="tight")
print("wrote", OUT, "| shape shown:", df.shape, "of 51 cols")
