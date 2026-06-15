"""
Quick consultation visuals — run this before the meeting.
Generates two figures saved to thesis_main/Scripts/output/
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

ABT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "Data", "processed", "abt_clean.csv"
)
df = pd.read_csv(ABT_PATH)

# Drop rows missing lat/lon or price_per_sqm
df = df.dropna(subset=["latitude", "longitude", "price_per_sqm"])

# ── Figure 1: Geographic scatter of all properties, colored by price/sqm ──────
fig, ax = plt.subplots(figsize=(9, 8))

p5, p95 = df["price_per_sqm"].quantile(0.05), df["price_per_sqm"].quantile(0.95)
clipped = df["price_per_sqm"].clip(p5, p95)
norm = mcolors.Normalize(vmin=p5, vmax=p95)
cmap = cm.get_cmap("RdYlGn_r")

scatter = ax.scatter(
    df["longitude"], df["latitude"],
    c=clipped, cmap=cmap, norm=norm,
    s=18, alpha=0.75, linewidths=0
)

cbar = plt.colorbar(scatter, ax=ax, fraction=0.03, pad=0.02)
cbar.set_label("Price per sqm (PHP)", fontsize=10)

city_colors = {
    "Cebu City": "#1f77b4", "Mandaue City": "#ff7f0e",
    "Lapu-Lapu City": "#2ca02c", "Talisay City": "#d62728",
    "Minglanilla": "#9467bd", "Consolacion": "#8c564b",
}
for city, color in city_colors.items():
    sub = df[df["city"] == city]
    if len(sub):
        cx, cy = sub["longitude"].mean(), sub["latitude"].mean()
        ax.annotate(city, (cx, cy), fontsize=7.5, color="white",
                    ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.2", fc=color, alpha=0.75, lw=0))

ax.set_title(
    f"Metro Cebu Residential Property Dataset  |  n = {len(df):,} records\n"
    "Color = price per sqm (PHP) — clipped to 5th–95th percentile",
    fontsize=11, pad=12
)
ax.set_xlabel("Longitude", fontsize=9)
ax.set_ylabel("Latitude", fontsize=9)
ax.tick_params(labelsize=8)
ax.set_facecolor("#1a1a2e")
fig.patch.set_facecolor("#12121f")
for spine in ax.spines.values():
    spine.set_edgecolor("#444")

plt.tight_layout()
out1 = os.path.join(OUTPUT_DIR, "fig1_property_map.png")
plt.savefig(out1, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"Saved: {out1}")


# ── Figure 2: 2-panel — price distribution + data source breakdown ─────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Panel A — price/sqm distribution by market segment
colors_seg = {"open_market": "#4CAF50", "bank_ropa": "#FF5722", "floor_price": "#2196F3"}
for seg, grp in df.groupby("market_segment"):
    axes[0].hist(
        grp["price_per_sqm"].clip(0, 200_000),
        bins=40, alpha=0.65, label=seg,
        color=colors_seg.get(seg, "gray"), edgecolor="none"
    )
axes[0].set_title("Price per sqm Distribution\nby Market Segment", fontsize=11)
axes[0].set_xlabel("Price per sqm (PHP, capped at 200k)", fontsize=9)
axes[0].set_ylabel("Count", fontsize=9)
axes[0].legend(fontsize=8)
axes[0].tick_params(labelsize=8)

# Panel B — record count by city × market_segment
city_order = ["Cebu City", "Mandaue City", "Lapu-Lapu City",
              "Talisay City", "Minglanilla", "Consolacion"]
pivot = (
    df.groupby(["city", "market_segment"])
    .size().unstack(fill_value=0)
    .reindex(city_order)
)
pivot.plot(
    kind="barh", stacked=True, ax=axes[1],
    color=[colors_seg.get(c, "gray") for c in pivot.columns],
    edgecolor="white", linewidth=0.4
)
axes[1].set_title(f"Records by City & Segment\nTotal: {len(df):,} rows", fontsize=11)
axes[1].set_xlabel("Number of Records", fontsize=9)
axes[1].set_ylabel("")
axes[1].tick_params(labelsize=8)
axes[1].legend(fontsize=8, loc="lower right")

# Annotate totals on bars
for i, city in enumerate(city_order):
    if city in pivot.index:
        total = pivot.loc[city].sum()
        axes[1].text(total + 3, i, str(total), va="center", fontsize=8)

plt.suptitle("Metro Cebu Residential Valuation — ABT Overview", fontsize=13, y=1.02)
plt.tight_layout()
out2 = os.path.join(OUTPUT_DIR, "fig2_abt_overview.png")
plt.savefig(out2, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {out2}")

print("\nDone. Open the two PNGs in thesis_main/Scripts/output/")
