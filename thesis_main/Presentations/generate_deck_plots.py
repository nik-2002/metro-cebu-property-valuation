"""Generate the three deck visuals that do not exist as manuscript figures:
   1. Collection funnel (Ch4 Table: Open-Market Collection Funnel)
   2. Ablation by feature tier (Ch7 Table: tab:ablation)
   3. Valuation gap by LGU, vacant lots (Models/stratified/valuation_gap_summary.csv)

Style matches the defense deck mockup: warm off-white bg, deep-green accent, big type, minimal chartjunk.
Data for (1) and (2) is hardcoded from the verified manuscript tables; (3) is read from the CSV.
"""
import csv
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ---- deck palette ----
BG      = "#FAF8F4"
INK     = "#1A1A1A"
MUTED   = "#9A968C"
ACCENT  = "#2F5D50"   # deep green
ACCENT2 = "#7FA99B"   # mid green
ACCENT3 = "#CFE0D8"   # light green tint
RED     = "#B4543F"   # excluded / reference

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "font.family": "DejaVu Sans", "text.color": INK,
    "axes.edgecolor": "#D9D6CF", "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK, "axes.linewidth": 0.8,
})

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "assets", "deck")
os.makedirs(OUT, exist_ok=True)
ROOT = os.path.abspath(os.path.join(HERE, ".."))   # thesis_main/


def style_ax(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)


# ============================================================ 1. FUNNEL
def funnel():
    # (source, raw, retained)  — OnePropertee excluded entirely
    rows = [
        ("Lamudi (bulk)",    4477, 1578),
        ("Lamudi (browser)",  665,  270),
        ("FilipinoHomes",    3894, 1203),
        ("DotProperty",      3721,  565),
        ("OnePropertee",     3804,    0),   # excluded (contamination)
    ]
    labels = [r[0] for r in rows]
    raw    = [r[1] for r in rows]
    ret    = [r[2] for r in rows]
    y = range(len(rows))

    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.barh(y, raw, color=ACCENT3, height=0.66, label="Raw scraped")
    ax.barh(y, ret, color=ACCENT,  height=0.66, label="Retained in ABT")
    for i, (rw, rt) in enumerate(zip(raw, ret)):
        ax.text(rw + 90, i, f"{rw:,}", va="center", ha="left", fontsize=12, color=MUTED)
        if rt > 0:
            ax.text(rt - 90, i, f"{rt:,}", va="center", ha="right", fontsize=12,
                    color="white", fontweight="bold")
        else:
            ax.text(120, i, "excluded — contamination", va="center", ha="left",
                    fontsize=11, color=RED, fontstyle="italic")
    ax.set_yticks(list(y)); ax.set_yticklabels(labels, fontsize=13)
    ax.invert_yaxis()
    ax.set_xlabel("Listings", fontsize=12)
    ax.set_xlim(0, 5200)
    ax.legend(loc="lower right", frameon=False, fontsize=12)
    ax.set_title("16,561 raw listings  →  3,616 clean open-market records",
                 fontsize=18, fontweight="bold", color=ACCENT, loc="left", pad=16)
    style_ax(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "funnel_collection.png"), dpi=150)
    plt.close(fig)
    print("wrote funnel_collection.png")


# ============================================================ 2. ABLATION
def ablation():
    strata = ["Condominium", "Houses", "Vacant Lot"]
    structural = [24.9, 27.1, 51.5]
    admin      = [23.0, 22.3, 42.3]
    geo        = [19.3, 23.0, 38.6]   # + Geospatial (full set)
    x = range(len(strata)); w = 0.26
    fig, ax = plt.subplots(figsize=(11, 6.2))
    b1 = ax.bar([i - w for i in x], structural, w, color=ACCENT3, label="Structural only")
    b2 = ax.bar(list(x),            admin,      w, color=ACCENT2, label="+ Administrative")
    b3 = ax.bar([i + w for i in x], geo,        w, color=ACCENT,  label="+ Geospatial")
    for bars in (b1, b2, b3):
        for b in bars:
            ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.6,
                    f"{b.get_height():.1f}", ha="center", va="bottom",
                    fontsize=11, color=INK)
    ax.set_xticks(list(x)); ax.set_xticklabels(strata, fontsize=14)
    ax.set_ylabel("MdAPE  (%, lower is better)", fontsize=12)
    ax.set_ylim(0, 58)
    ax.legend(loc="upper left", frameon=False, fontsize=12)
    ax.set_title("Geospatial features improve every stratum",
                 fontsize=18, fontweight="bold", color=ACCENT, loc="left", pad=16)
    style_ax(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "ablation_tiers.png"), dpi=150)
    plt.close(fig)
    print("wrote ablation_tiers.png")


# ============================================================ 3. VALUATION GAP
def valuation_gap():
    csv_path = os.path.join(ROOT, "Models", "stratified", "valuation_gap_summary.csv")
    data = {}
    with open(csv_path) as fh:
        for row in csv.DictReader(fh):
            if row["stratum"] == "Vacant Lot":
                mult = 1.0 + float(row["median_listing_gap_pct"]) / 100.0
                data[row["city"]] = mult
    items = sorted(data.items(), key=lambda kv: kv[1])
    labels = [k for k, _ in items]
    vals   = [v for _, v in items]
    y = range(len(items))

    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.barh(y, vals, color=ACCENT, height=0.62)
    ax.axvline(1.0, color=RED, lw=1.6, ls="--")
    ax.text(1.04, len(items) - 0.4, "BIR zonal benchmark (1×)", color=RED,
            fontsize=11, va="center")
    for i, v in enumerate(vals):
        ax.text(v + 0.06, i, f"{v:.1f}×", va="center", ha="left",
                fontsize=13, fontweight="bold", color=ACCENT)
    ax.set_yticks(list(y)); ax.set_yticklabels(labels, fontsize=13)
    ax.set_xlabel("Market price ÷ BIR zonal value  (vacant lots)", fontsize=12)
    ax.set_xlim(0, 5.6)
    ax.set_title("Market prices run far above official benchmarks",
                 fontsize=18, fontweight="bold", color=ACCENT, loc="left", pad=16)
    style_ax(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "valuation_gap_lots.png"), dpi=150)
    plt.close(fig)
    print("wrote valuation_gap_lots.png")


# ============================================================ 4. LISTINGS BY LGU x STRATUM
def listings_by_lgu():
    # full-ABT counts by LGU x property-type group (Appendix B table, verified)
    rows = [  # city, condo, house, lot
        ("Cebu City", 669, 360, 339),
        ("Lapu-Lapu City", 444, 273, 153),
        ("Mandaue City", 241, 182, 125),
        ("Talisay City", 19, 214, 139),
        ("Consolacion", 8, 131, 103),
        ("Minglanilla", 10, 141, 65),
    ]
    rows.sort(key=lambda r: r[1] + r[2] + r[3])   # ascending total for horizontal bars
    labels = [r[0] for r in rows]
    condo = [r[1] for r in rows]; house = [r[2] for r in rows]; lot = [r[3] for r in rows]
    y = range(len(rows))
    fig, ax = plt.subplots(figsize=(9.2, 6.2))
    ax.barh(y, condo, color=ACCENT,  height=0.66, label="Condominium")
    ax.barh(y, house, left=condo, color=ACCENT2, height=0.66, label="Houses")
    ax.barh(y, lot, left=[c + h for c, h in zip(condo, house)], color=ACCENT3, height=0.66, label="Vacant Lot")
    for i, r in enumerate(rows):
        tot = r[1] + r[2] + r[3]
        ax.text(tot + 14, i, f"{tot:,}", va="center", ha="left", fontsize=12, color=MUTED)
    ax.set_yticks(list(y)); ax.set_yticklabels(labels, fontsize=13)
    ax.set_xlabel("Listings", fontsize=12); ax.set_xlim(0, 1520)
    ax.legend(loc="lower right", frameon=False, fontsize=11.5)
    ax.set_title("Listings by LGU and property type", fontsize=17, fontweight="bold", color=ACCENT, loc="left", pad=14)
    style_ax(ax)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "listings_by_lgu.png"), dpi=150); plt.close(fig)
    print("wrote listings_by_lgu.png")


# ============================================================ 5. MCRAI CATCHMENT (schematic)
def mcrai_catchment():
    import matplotlib.patches as mp
    # (radius_km, label, color)
    rings = [
        (1.0, "Retail density", "#B4543F"),
        (1.5, "Recreation",     "#C9962F"),
        (2.0, "Grocery · Health · Security", "#2F5D50"),
        (2.5, "Education",      "#3E7CB1"),
        (3.0, "Tourism",        "#7A6FAF"),
        (5.0, "Hospitals",      "#6B6B66"),
    ]
    fig, ax = plt.subplots(figsize=(10.6, 7.0))
    ax.set_aspect("equal")
    for r, label, col in rings:
        ax.add_patch(plt.Circle((0, 0), r, fill=False, ls="--", lw=1.4, ec=col, alpha=.85))
        ax.text(0, r, f"  {label}  ·  {r:g} km", ha="center", va="bottom", fontsize=10.5,
                color=col, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.18", fc=BG, ec="none", alpha=.9))
    # amenity dots within each ring
    import math
    pts = {0.7:("#B4543F",4), 1.2:("#C9962F",3), 1.6:("#2F5D50",5), 2.2:("#3E7CB1",3),
           2.7:("#7A6FAF",2), 4.2:("#6B6B66",2)}
    ang0 = 0.6
    for k,(rr,(col,n)) in enumerate(pts.items()):
        for j in range(n):
            a = ang0 + (k*1.3) + j*(2*math.pi/ (n+1))
            ax.plot(rr*math.cos(a), rr*math.sin(a), "o", ms=7, color=col, alpha=.9)
    # the property at center
    ax.plot(0, 0, marker="*", ms=26, color=ACCENT, zorder=5)
    ax.text(0, -0.35, "Property", ha="center", va="top", fontsize=12, fontweight="bold", color=ACCENT)
    # CBD node + road-distance link (modeled separately)
    ax.annotate("", xy=(4.3, -3.2), xytext=(0, 0),
                arrowprops=dict(arrowstyle="->", color=INK, lw=1.6, ls=(0,(4,3))))
    ax.plot(4.3, -3.2, "s", ms=12, color=INK)
    ax.text(4.45, -3.2, " CBD node\n (road-network distance —\n a separate feature)", va="center", fontsize=10, color=INK)
    ax.text(-5.4, 5.0, "Each category counts nearby amenities,\nweighted by 1 / distance²  (β = 2).",
            fontsize=11.5, color=INK, va="top")
    ax.text(-5.4, -4.4, "Composite = 0.447·Education + 0.345·Grocery + 0.222·Recreation",
            fontsize=10.5, color=ACCENT, va="top", fontstyle="italic")
    ax.set_xlim(-5.6, 6.6); ax.set_ylim(-5.0, 5.8); ax.axis("off")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "mcrai_catchment.png"), dpi=150); plt.close(fig)
    print("wrote mcrai_catchment.png")


# ============================================================ 6. WIDE ABT SNAPSHOT
def abt_snapshot_wide():
    import pandas as pd
    abt = os.path.join(ROOT, "Data", "processed", "abt_clean.csv")
    cols = ["property_id","source","city","property_type","area_sqm","bedrooms","bathrooms",
            "latitude","longitude","price_php","price_per_sqm","dist_cebu_business_park_m",
            "dist_mandaue_cbd_m","mcrai_education","mcrai_grocery","mcrai_composite",
            "bir_zonal_rr_median","spatial_lag_price"]
    hdr = ["id","source","city","type","area","beds","baths","lat","lon","price_php",
           "price/sqm","d_CBP","d_Mandaue","mcrai_edu","mcrai_groc","mcrai_comp","bir_zonal","sp_lag"]
    df = pd.read_csv(abt, usecols=lambda c: c in cols)[cols].head(8).copy()
    def fmt(c, v):
        if pd.isna(v): return ""
        if c in ("price_php","price_per_sqm","bir_zonal_rr_median","spatial_lag_price",
                 "dist_cebu_business_park_m","dist_mandaue_cbd_m"): return f"{v:,.0f}"
        if c in ("area_sqm","mcrai_education","mcrai_grocery","mcrai_composite"): return f"{v:,.1f}"
        if c in ("latitude","longitude"): return f"{v:.3f}"
        if c in ("bedrooms","bathrooms","property_id"): return f"{int(v)}"
        s = str(v); return s[:13]+"…" if len(s) > 14 else s
    cells = [[fmt(c, df.iloc[r][c]) for c in cols] for r in range(len(df))]
    fig, ax = plt.subplots(figsize=(15.5, 3.6)); ax.axis("off")
    t = ax.table(cellText=cells, colLabels=hdr, loc="center", cellLoc="center")
    t.auto_set_font_size(False); t.set_fontsize(8); t.scale(1, 1.5)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor("#D9D6CF")
        if r == 0: cell.set_facecolor(ACCENT); cell.set_text_props(color="white", fontweight="bold")
        elif r % 2 == 0: cell.set_facecolor("#EEF3F0")
    t.auto_set_column_width(col=list(range(len(cols))))
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "abt_snapshot_wide.png"), dpi=170, bbox_inches="tight"); plt.close(fig)
    print("wrote abt_snapshot_wide.png  (18 of 51 cols)")


if __name__ == "__main__":
    funnel()
    ablation()
    valuation_gap()
    listings_by_lgu()
    mcrai_catchment()
    abt_snapshot_wide()
    print("OUT:", OUT)
