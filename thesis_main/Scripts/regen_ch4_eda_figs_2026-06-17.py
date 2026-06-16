"""
regen_ch4_eda_figs_2026-06-17.py
================================
Regenerate the three Chapter 4 EDA figures from the CURRENT frozen open-market ABT
(abt_clean.csv, 3,616 rows) so the figures match the refreshed Chapter 4 tables. The
old top-level EDA/*.png price figures came from the legacy run_eda.py on the
pre-expansion 2,047-row ABT and were stale (e.g. open-market median ~111k vs current ~82k).

Overwrites (same paths the manuscript references):
    EDA/price_by_city_open_market.png
    EDA/price_by_property_type.png
    EDA/missingness_top15.png

price_by_segment.png is NOT regenerated here: the bank_ropa/floor_price tiers are not in
the processed open-market ABT, and Chapter 4 no longer relies on that figure.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ABT = os.path.join(BASE, "Data", "processed", "abt_clean.csv")
EDA = os.path.join(BASE, "EDA")

d = pd.read_csv(ABT)

# ---- 1. price_per_sqm by city (boxplot, outliers hidden, sorted by median) ----
order = d.groupby("city")["price_per_sqm"].median().sort_values().index.tolist()
data = [d.loc[d.city == c, "price_per_sqm"].dropna().values for c in order]
fig, ax = plt.subplots(figsize=(11, 6))
ax.boxplot(data, labels=order, showfliers=False, vert=True)
ax.set_title("open_market price_per_sqm by city (outliers hidden)")
ax.set_ylabel("price_per_sqm (PHP)")
ax.set_xlabel("city")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
fig.savefig(os.path.join(EDA, "price_by_city_open_market.png"), dpi=150)
plt.close(fig)

# ---- 2. price_per_sqm by property type (boxplot, outliers hidden, sorted by median) ----
torder = d.groupby("property_type")["price_per_sqm"].median().sort_values().index.tolist()
tdata = [d.loc[d.property_type == t, "price_per_sqm"].dropna().values for t in torder]
fig, ax = plt.subplots(figsize=(11, 6))
ax.boxplot(tdata, labels=torder, showfliers=False, vert=True)
ax.set_title("open_market price_per_sqm by property type (outliers hidden)")
ax.set_ylabel("price_per_sqm (PHP)")
ax.set_xlabel("property_type")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
fig.savefig(os.path.join(EDA, "price_by_property_type.png"), dpi=150)
plt.close(fig)

# ---- 3. top-15 missingness ----
miss = (d.isna().mean() * 100).sort_values(ascending=False)
miss = miss[miss > 0].head(15)
fig, ax = plt.subplots(figsize=(11, 6))
ax.barh(miss.index[::-1], miss.values[::-1])
ax.set_title("Top-15 fields by missingness rate (open-market ABT)")
ax.set_xlabel("missing (%)")
plt.tight_layout()
fig.savefig(os.path.join(EDA, "missingness_top15.png"), dpi=150)
plt.close(fig)

print("Regenerated: price_by_city_open_market.png, price_by_property_type.png, missingness_top15.png")
print("city order (low->high median):", order)
print("type order (low->high median):", torder)
