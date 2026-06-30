"""
render_listings_map.py
======================
Renders a presentation-quality static map of the open-market residential
listings across Metro Cebu, colored by deployed stratum (Condominium / Houses /
Vacant Lot), over labeled LGU boundaries. This is the print-ready replacement
for the low-opacity, unlabeled in-app Leaflet capture.

Reads the static data the web app uses (public/data/), reprojects to UTM 51N
(EPSG:32651) for correct aspect and a metric scale bar, and writes a high-DPI PNG.
"""

import os
import json
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrow
import matplotlib.patheffects as pe

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "public", "data")
OUT = os.path.join(HERE, "..", "..", "EDA", "plots", "webapp_market_map_render.png")

UTM = 32651  # WGS84 / UTM zone 51N — Metro Cebu

STRATA = [
    ("Condominium", "#1f6fb2"),
    ("Houses",      "#e07b39"),
    ("Vacant Lot",  "#3a9a5c"),
]


def load():
    listings = json.load(open(os.path.join(DATA, "listings.json")))
    df = pd.DataFrame(listings)
    gdf = gpd.GeoDataFrame(
        df, geometry=[Point(xy) for xy in zip(df.longitude, df.latitude)],
        crs="EPSG:4326").to_crs(epsg=UTM)
    lgu = gpd.read_file(os.path.join(DATA, "lgu_boundaries.geojson")).to_crs(epsg=UTM)
    return gdf, lgu


def scalebar(ax, length_km=5):
    """Simple metric scale bar at lower-left, in projected meters."""
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    L = length_km * 1000
    bx = x0 + (x1 - x0) * 0.04
    by = y0 + (y1 - y0) * 0.05
    ax.plot([bx, bx + L], [by, by], color="0.15", lw=3, solid_capstyle="butt", zorder=6)
    ax.text(bx + L / 2, by + (y1 - y0) * 0.012, f"{length_km} km",
            ha="center", va="bottom", fontsize=9, color="0.15", zorder=6)


def north_arrow(ax):
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    nx = x1 - (x1 - x0) * 0.05
    ny = y0 + (y1 - y0) * 0.10
    dy = (y1 - y0) * 0.06
    ax.add_patch(FancyArrow(nx, ny, 0, dy, width=0, head_width=(x1 - x0) * 0.012,
                            head_length=dy * 0.45, color="0.15", zorder=6))
    ax.text(nx, ny + dy * 1.15, "N", ha="center", va="bottom",
            fontsize=11, fontweight="bold", color="0.15", zorder=6)


def main():
    gdf, lgu = load()

    # size the figure to the data aspect so the map fills the frame
    xmin, ymin, xmax, ymax = lgu.total_bounds
    aspect = (xmax - xmin) / (ymax - ymin)
    W = 12.0
    fig, ax = plt.subplots(figsize=(W, W / aspect + 1.0))

    # LGU fill + edges
    lgu.plot(ax=ax, facecolor="#eef1f4", edgecolor="#9aa6b2", linewidth=0.9, zorder=1)

    # listings by stratum
    for name, color in STRATA:
        sub = gdf[gdf["stratum"] == name]
        ax.scatter(sub.geometry.x, sub.geometry.y, s=14, c=color, alpha=0.85,
                   edgecolors="white", linewidths=0.25, zorder=3, label=f"{name} (n={len(sub):,})")

    # LGU name labels at interior points, with white halo
    for _, row in lgu.iterrows():
        pt = row.geometry.representative_point()
        ax.text(pt.x, pt.y, row["lgu"], ha="center", va="center",
                fontsize=11, fontweight="bold", color="#2b3640", zorder=5,
                path_effects=[pe.withStroke(linewidth=3, foreground="white")])

    ax.set_aspect("equal")
    ax.set_axis_off()
    scalebar(ax, length_km=5)
    north_arrow(ax)

    leg = ax.legend(title="Property stratum", loc="upper right", frameon=True,
                    fontsize=10, title_fontsize=11, markerscale=1.6,
                    framealpha=0.95, edgecolor="#9aa6b2")
    leg.get_frame().set_linewidth(0.8)

    ax.set_title(
        f"{len(gdf):,} listings from three online portals, by deployed property stratum",
        fontsize=11, color="0.35", pad=8)
    fig.suptitle("Open-Market Residential Listings Across Metro Cebu",
                 fontsize=16, fontweight="bold", y=0.965)

    fig.tight_layout(rect=[0, 0, 1, 0.97])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"Saved -> {os.path.abspath(OUT)}  ({len(gdf):,} listings, {len(lgu)} LGUs)")


if __name__ == "__main__":
    main()
