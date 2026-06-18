"""
generate_manuscript_maps.py
===========================
Clean cartographic maps for the manuscript (no road-network basemap):
  1. study_area_clean.png      -- 6 LGU polygons + 8 polycentric CBD nodes (labeled)
  2. lgu_boundaries.png        -- 6 LGUs with boundary lines + names (scope map)
  3. properties_by_stratum.png -- property points colored by stratum + legend

Projected to UTM 51N (EPSG:32651) for correct aspect and a metric scale bar.
Read-only on data; writes PNGs to Manuscript/diagrams/.
"""
from pathlib import Path
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

THESIS = Path(__file__).resolve().parent.parent
LGU_GEOJSON = THESIS / "QGIS" / "data" / "lgu_boundaries.geojson"
CBD_CSV = THESIS / "Data" / "processed" / "cbd_nodes.csv"
ABT_CSV = THESIS / "Data" / "processed" / "abt_clean.csv"
OUT = THESIS / "Manuscript" / "diagrams"
OUT.mkdir(parents=True, exist_ok=True)
UTM = 32651  # WGS84 / UTM zone 51N (Cebu)

AIRPORT = ("airport", "Mactan-Cebu Intl. Airport", 10.30719, 123.97899)
STRATUM = {
    "Condominium": "Condominium", "Apartment": "Condominium",
    "Single Detached": "House", "House and Lot": "House", "Townhouse": "House",
    "Vacant Lot": "Vacant Lot",
}
STRAT_COLOR = {"Condominium": "#1f77b4", "House": "#2ca02c", "Vacant Lot": "#d9911f"}


def scale_bar(ax, length_m=5000, label="5 km", corner="left"):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    if corner == "left":
        x = x0 + (x1 - x0) * 0.06
    else:
        x = x1 - (x1 - x0) * 0.06 - length_m
    y = y0 + (y1 - y0) * 0.05
    ax.plot([x, x + length_m], [y, y], color="black", lw=2.5, solid_capstyle="butt")
    ax.text(x + length_m / 2, y + (y1 - y0) * 0.012, label, ha="center", va="bottom", fontsize=8)


def load_lgu():
    g = gpd.read_file(LGU_GEOJSON).to_crs(epsg=UTM)
    g["lgu"] = g["lgu"].str.strip()
    return g


def nodes_gdf():
    df = pd.read_csv(CBD_CSV)[["label", "centroid_lat", "centroid_lon"]]
    df.columns = ["label", "lat", "lon"]
    df["short"] = ["Cebu Business Park", "Mandaue CBD", "Mactan CBD", "SRP",
                   "Talisay Tabunok", "Consolacion", "Naga City (anchor)"]
    ap = pd.DataFrame([{"label": AIRPORT[1], "lat": AIRPORT[2], "lon": AIRPORT[3], "short": "Airport"}])
    df = pd.concat([df, ap], ignore_index=True)
    g = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs=4326).to_crs(epsg=UTM)
    return g


def base(ax, lgu, fill="#eef0f2", edge="#5a5a5a", label_lgu=True):
    lgu.plot(ax=ax, color=fill, edgecolor=edge, linewidth=1.0)
    if label_lgu:
        for _, r in lgu.iterrows():
            c = r.geometry.representative_point()
            ax.annotate(r["lgu"], (c.x, c.y), ha="center", va="center",
                        fontsize=8.5, color="#222", fontweight="medium")
    ax.set_axis_off()
    ax.set_aspect("equal")


def map_study_area():
    lgu, nodes = load_lgu(), nodes_gdf()
    fig, ax = plt.subplots(figsize=(8.2, 8.2))
    base(ax, lgu)
    nodes.plot(ax=ax, marker="*", color="#c0392b", markersize=210,
               edgecolor="white", linewidth=0.6, zorder=5)
    # per-node label placement to avoid collisions: (dx, dy, ha, va)
    place = {
        "Cebu Business Park": (-8, 6, "right", "bottom"),
        "Mandaue CBD": (9, 2, "left", "center"),
        "Mactan CBD": (7, 9, "left", "bottom"),
        "SRP": (8, 0, "left", "center"),
        "Talisay Tabunok": (8, -2, "left", "top"),
        "Consolacion": (8, 4, "left", "bottom"),
        "Naga City (anchor)": (0, 10, "center", "bottom"),
        "Airport": (8, -10, "left", "top"),
    }
    for _, r in nodes.iterrows():
        dx, dy, ha, va = place.get(r["short"], (6, 6, "left", "bottom"))
        ax.annotate(r["short"], (r.geometry.x, r.geometry.y),
                    xytext=(dx, dy), textcoords="offset points", ha=ha, va=va,
                    fontsize=7.8, fontweight="bold", color="#7b241c", zorder=6)
    scale_bar(ax, corner="right")
    ax.legend(handles=[Line2D([0], [0], marker="*", color="w", markerfacecolor="#c0392b",
                              markersize=15, label="Polycentric CBD node")],
              loc="upper right", frameon=True, fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "study_area_clean.png", dpi=220, bbox_inches="tight")
    plt.close(fig)
    print("wrote study_area_clean.png")


def map_lgu_boundaries():
    lgu = load_lgu()
    palette = ["#a6cee3", "#b2df8a", "#fdbf6f", "#cab2d6", "#fb9a99", "#ffff99"]
    fig, ax = plt.subplots(figsize=(8.2, 8.2))
    lgu = lgu.sort_values("lgu").reset_index(drop=True)
    lgu.plot(ax=ax, color=[palette[i % len(palette)] for i in range(len(lgu))],
             edgecolor="#333", linewidth=1.3)
    for _, r in lgu.iterrows():
        c = r.geometry.representative_point()
        ax.annotate(r["lgu"], (c.x, c.y), ha="center", va="center", fontsize=9.5, fontweight="medium")
    ax.set_axis_off(); ax.set_aspect("equal")
    scale_bar(ax)
    fig.tight_layout()
    fig.savefig(OUT / "lgu_boundaries.png", dpi=220, bbox_inches="tight")
    plt.close(fig)
    print("wrote lgu_boundaries.png")


def map_properties():
    lgu = load_lgu()
    df = pd.read_csv(ABT_CSV)
    df = df.dropna(subset=["latitude", "longitude"]).copy()
    df["stratum"] = df["property_type"].map(STRATUM)
    df = df.dropna(subset=["stratum"])
    g = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude),
                         crs=4326).to_crs(epsg=UTM)
    fig, ax = plt.subplots(figsize=(8.2, 8.2))
    base(ax, lgu, fill="#f5f6f7", label_lgu=True)
    for strat, color in STRAT_COLOR.items():
        sub = g[g["stratum"] == strat]
        sub.plot(ax=ax, color=color, markersize=7, alpha=0.55, linewidth=0, zorder=4)
    handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markersize=9,
                      label=f"{s} (n={int((g['stratum'] == s).sum())})")
               for s, c in STRAT_COLOR.items()]
    ax.legend(handles=handles, loc="upper right", frameon=True, fontsize=9, title="Listing type")
    scale_bar(ax)
    fig.tight_layout()
    fig.savefig(OUT / "properties_by_stratum.png", dpi=220, bbox_inches="tight")
    plt.close(fig)
    print("wrote properties_by_stratum.png")


def map_amenities():
    lgu = load_lgu()
    cats = {"education": "Education", "grocery": "Grocery", "health": "Health",
            "hospitals": "Hospitals", "recreation": "Recreation",
            "retail_density": "Retail density", "security": "Security", "tourism": "Tourism"}
    colors = {"education": "#1f77b4", "grocery": "#ff7f0e", "health": "#2ca02c",
              "hospitals": "#d62728", "recreation": "#9467bd", "retail_density": "#8c564b",
              "security": "#e377c2", "tourism": "#17becf"}
    poi = THESIS / "QGIS" / "data" / "mcrai_pois"
    layers = {c: gpd.read_file(poi / f"mcrai_{c}_pois.geojson").to_crs(epsg=UTM) for c in cats}
    fig, ax = plt.subplots(figsize=(8.4, 8.4))
    base(ax, lgu, fill="#f7f8f9", label_lgu=False)
    for c in sorted(cats, key=lambda k: -len(layers[k])):  # densest first
        layers[c].plot(ax=ax, color=colors[c], markersize=4, alpha=0.5, linewidth=0, zorder=4)
    handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=colors[c], markersize=8,
                      label=f"{cats[c]} (n={len(layers[c])})") for c in cats]
    ax.legend(handles=handles, loc="upper right", frameon=True, fontsize=8,
              title="MCRAI amenity category")
    scale_bar(ax)
    fig.tight_layout()
    fig.savefig(OUT / "amenities_map.png", dpi=220, bbox_inches="tight")
    plt.close(fig)
    print("wrote amenities_map.png")


if __name__ == "__main__":
    # map_study_area() retired: study-area map is node-free (lgu_boundaries.png).
    map_lgu_boundaries()
    map_properties()
    map_amenities()
    print("done ->", OUT)
