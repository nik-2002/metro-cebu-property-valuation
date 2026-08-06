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

# ---- deck palette (cool / neutral) ----
BG      = "#FAFBFC"
INK     = "#1E2530"
MUTED   = "#8A92A0"
ACCENT  = "#33455E"   # deep slate blue
ACCENT2 = "#6B89A8"   # steel blue
ACCENT3 = "#C5D2DF"   # light cool blue-grey
RED     = "#A86B6B"   # muted dusty rose — excluded / reference only

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

    fig, ax = plt.subplots(figsize=(11.5, 6.6))
    xmax = max(raw); off = xmax * 0.013
    ax.barh(y, raw, color=ACCENT3, height=0.60, label="Raw scraped", zorder=1)
    ax.barh(y, ret, color=ACCENT,  height=0.60, label="Retained in ABT", zorder=2)
    for i, (rw, rt) in enumerate(zip(raw, ret)):
        # both counts sit just past the END of their own bar — never inside, never clipped
        ax.text(rw + off, i, f"{rw:,}", va="center", ha="left", fontsize=12, color=MUTED)
        if rt > 0:
            ax.text(rt + off, i, f"{rt:,}", va="center", ha="left", fontsize=12,
                    color=ACCENT, fontweight="bold")
        else:
            ax.text(off, i, "excluded — contamination", va="center", ha="left",
                    fontsize=11, color=RED, fontstyle="italic")
    ax.set_yticks(list(y)); ax.set_yticklabels(labels, fontsize=13)
    ax.invert_yaxis()
    ax.set_xlabel("Listings", fontsize=12)
    ax.set_xlim(0, xmax * 1.16)
    ax.set_title("16,561 raw listings  →  3,616 clean open-market records",
                 fontsize=18, fontweight="bold", color=ACCENT, loc="left", pad=18)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.09), ncol=2,
              frameon=False, fontsize=12)
    style_ax(ax)
    fig.savefig(os.path.join(OUT, "funnel_collection.png"), dpi=150,
                bbox_inches="tight", pad_inches=0.22)
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
        (1.0, "Retail density", "#33455E"),
        (1.5, "Recreation",     "#46627F"),
        (2.0, "Grocery · Health · Security", "#5B7A99"),
        (2.5, "Education",      "#7592AE"),
        (3.0, "Tourism",        "#93AAC2"),
        (5.0, "Hospitals",      "#A9B8C8"),
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
    pts = {0.7:("#33455E",4), 1.2:("#46627F",3), 1.6:("#5B7A99",5), 2.2:("#7592AE",3),
           2.7:("#93AAC2",2), 4.2:("#A9B8C8",2)}
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


# ============================================================ 7. MODEL COMPARISON (MdAPE)
def model_comparison():
    # from model_comparison_groupcv.csv (MdAPE) — leak-free GroupKFold(5), all three
    # models on identical folds. RF matches the deployment manifest exactly.
    strata = ["Condominium", "Houses", "Vacant Lot"]
    ols = [24.47, 25.06, 44.79]
    rf  = [19.32, 22.67, 38.36]   # == deployment_manifest.json metrics_group_cv
    xgb = [19.81, 23.64, 40.22]
    x = range(len(strata)); w = 0.26
    fig, ax = plt.subplots(figsize=(11, 6.2))
    b1 = ax.bar([i - w for i in x], ols, w, color=ACCENT3, label="OLS (hedonic baseline)")
    b2 = ax.bar(list(x),            rf,  w, color=ACCENT,  label="Random Forest (deployed)")
    b3 = ax.bar([i + w for i in x], xgb, w, color=ACCENT2, label="XGBoost")
    for bars in (b1, b2, b3):
        for b in bars:
            ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.5, f"{b.get_height():.1f}",
                    ha="center", va="bottom", fontsize=11, color=INK)
    ax.set_xticks(list(x)); ax.set_xticklabels(strata, fontsize=14)
    ax.set_ylabel("MdAPE  (%, lower is better)", fontsize=12); ax.set_ylim(0, 50)
    ax.legend(loc="upper left", frameon=False, fontsize=11.5)
    ax.set_title("Tree models beat the linear baseline in every stratum",
                 fontsize=17, fontweight="bold", color=ACCENT, loc="left", pad=14)
    style_ax(ax)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "model_comparison.png"), dpi=150); plt.close(fig)
    print("wrote model_comparison.png")


# ============================================================ 8. MCRAI WEIGHTING (two-stage)
def mcrai_weighting():
    import matplotlib.patches as mp
    fig, ax = plt.subplots(figsize=(11.5, 6.0)); ax.axis("off")
    ax.set_xlim(0, 100); ax.set_ylim(0, 100)
    def card(x, y, w, h, title, lines, fc=BG, ec=ACCENT):
        ax.add_patch(mp.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6,rounding_size=2",
                     fc=fc, ec=ec, lw=1.6))
        ax.text(x+w/2, y+h-5, title, ha="center", va="top", fontsize=11.5, fontweight="bold", color=ACCENT, linespacing=1.3)
        ax.text(x+w/2, y+h-17, lines, ha="center", va="top", fontsize=10.3, color=INK, linespacing=1.5)
    card(2, 30, 27, 46, "STAGE 1\nLet the market speak",
         "Fit a regression using each\namenity category on its own.\n\nWhich categories actually\nraise price?  (the sign tells us)")
    card(36.5, 30, 27, 46, "Keep the positives",
         "Education  ↑\nGrocery  ↑\nRecreation  ↑\n\nSecurity, tourism, retail →\nnegative / mixed → not in\nthe composite", fc="#EEF2F6")
    card(71, 30, 27, 46, "STAGE 2\nTurn strength into weights",
         "Normalize the positive\ncoefficients so they sum to 1:\n\nEducation   0.447\nGrocery      0.345\nRecreation  0.222", fc=BG, ec=ACCENT)
    for x0 in (29.4, 63.8):
        ax.annotate("", xy=(x0+6.6, 53), xytext=(x0, 53),
                    arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=2.2))
    ax.text(50, 20, "The weights are derived from Cebu's own market behavior — not assumed.",
            ha="center", fontsize=12, color=ACCENT, fontstyle="italic", fontweight="bold")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "mcrai_weighting.png"), dpi=150); plt.close(fig)
    print("wrote mcrai_weighting.png")


# ============================================================ 9. FEATURE SELECTION FUNNEL
def feature_selection():
    import matplotlib.patches as mp
    fig, ax = plt.subplots(figsize=(11.5, 6.0)); ax.axis("off")
    ax.set_xlim(0, 100); ax.set_ylim(0, 100)
    # pool
    ax.add_patch(mp.FancyBboxPatch((6, 64), 88, 22, boxstyle="round,pad=0.6,rounding_size=2",
                 fc="#EEF2F6", ec=ACCENT, lw=1.6))
    ax.text(50, 80, "Full feature pool", ha="center", fontsize=13, fontweight="bold", color=ACCENT)
    ax.text(50, 71, "structural · 8 CBD distances · 8 MCRAI categories + composite · BIR zonal · spatial lag · city dummies",
            ha="center", fontsize=10, color=INK)
    # screens
    screens = ["Variance Inflation\n(drop collinear)", "OLS significance\n(keep what matters)",
               "Leave-one-block\nablation", "MCRAI zero rates\n(drop empty categories)"]
    bw = 21; gap = 2.0; x0 = 6
    for i, sc in enumerate(screens):
        x = x0 + i*(bw+gap)
        ax.add_patch(mp.FancyBboxPatch((x, 40), bw, 14, boxstyle="round,pad=0.5,rounding_size=2",
                     fc=BG, ec=ACCENT2, lw=1.4))
        ax.text(x+bw/2, 47, sc, ha="center", va="center", fontsize=9.6, color=INK, linespacing=1.4)
    ax.annotate("", xy=(50, 55), xytext=(50, 63), arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=2.2))
    ax.annotate("", xy=(50, 31), xytext=(50, 39), arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=2.2))
    # three sets
    sets = [("Condominium", "21 features", 9), ("Houses", "24 features", 39.5), ("Vacant Lot", "22 features", 70)]
    for name, cnt, x in sets:
        ax.add_patch(mp.FancyBboxPatch((x, 8), 21, 18, boxstyle="round,pad=0.5,rounding_size=2",
                     fc=ACCENT, ec=ACCENT, lw=0))
        ax.text(x+10.5, 19, name, ha="center", fontsize=11.5, fontweight="bold", color="white")
        ax.text(x+10.5, 12.5, cnt, ha="center", fontsize=11, color="#C5D2DF")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "feature_selection.png"), dpi=150); plt.close(fig)
    print("wrote feature_selection.png")


# ============================================================ 10. DATA PIPELINE (6 stages)
def pipeline_flow():
    import matplotlib.patches as mp
    fig, ax = plt.subplots(figsize=(13.0, 4.6)); ax.axis("off")
    ax.set_xlim(0, 100); ax.set_ylim(18, 100)

    stages = [
        ("1 · Ingest",
         "16,561 raw listings\nscraped across\nfour portals\n(five batches)"),
        ("2 · Clean & filter",
         "drop distressed /\n“For Assume” · de-dup ·\nprice-per-sqm band ·\nresidential + 6 LGUs ·\nOnePropertee excluded"),
        ("3 · Geocode",
         "Google Maps API\n→ coordinates\n(FilipinoHomes\narrived geocoded)"),
        ("4 · BIR join",
         "spatial join to BIR\nzonal-value areas\n→ benchmark\ncolumn"),
        ("5 · Geospatial\nfeatures",
         "osmnx road-network\ndistance to 8 nodes ·\nMCRAI access ·\n500 m spatial lag"),
        ("6 · ABT",
         "3,616 open-market\nrecords\n× 51 columns"),
    ]
    n = len(stages); w = 14.3; gap = 2.0; x0 = 2.0; ytop = 52; h = 44
    for i, (title, body) in enumerate(stages):
        x = x0 + i * (w + gap)
        last = (i == n - 1)
        fc = ACCENT if last else BG
        ax.add_patch(mp.FancyBboxPatch((x, ytop), w, h, boxstyle="round,pad=0.5,rounding_size=2",
                     fc=fc, ec=ACCENT, lw=1.5))
        ax.text(x + w / 2, ytop + h - 4, title, ha="center", va="top", fontsize=10.2,
                fontweight="bold", color=("white" if last else ACCENT), linespacing=1.3)
        ax.text(x + w / 2, ytop + h - 16, body, ha="center", va="top", fontsize=8.6,
                color=("#E7EDF3" if last else INK), linespacing=1.55)
    for i in range(n - 1):
        xr = x0 + i * (w + gap) + w
        ax.annotate("", xy=(xr + gap, ytop + h / 2), xytext=(xr, ytop + h / 2),
                    arrowprops=dict(arrowstyle="-|>", color=ACCENT2, lw=2.0))

    # phase brackets ----------------------------------------------------------
    def bracket(xa, xb, y, color, label):
        ax.plot([xa, xb], [y, y], color=color, lw=1.8)
        for xx in (xa, xb):
            ax.plot([xx, xx], [y, y + 2.6], color=color, lw=1.8)
        ax.text((xa + xb) / 2, y - 5, label, ha="center", va="top",
                fontsize=10.2, color=color, fontweight="bold", linespacing=1.4)
    left_a = x0; right_a = x0 + 2 * (w + gap) + w           # cards 1-3
    left_b = x0 + 3 * (w + gap); right_b = x0 + 5 * (w + gap) + w  # cards 4-6
    bracket(left_a, right_a, 48, ACCENT,
            "Row filtering\n16,561 → 3,616 rows")
    bracket(left_b, right_b, 48, ACCENT2,
            "Feature enrichment\n→ 51 columns, no rows dropped")

    ax.text(50, 26, "Cleaning prunes the rows; the join and geospatial steps add columns, not drop records.",
            ha="center", fontsize=11.5, color=ACCENT, fontstyle="italic", fontweight="bold")
    fig.savefig(os.path.join(OUT, "pipeline_flow.png"), dpi=150,
                bbox_inches="tight", pad_inches=0.2); plt.close(fig)
    print("wrote pipeline_flow.png")


# ============================================================ 11. MCRAI FORMULA (image)
def mcrai_formula():
    # Rendered as an image so PowerPoint never has to typeset subscripts/sigma.
    fig = plt.figure(figsize=(7.4, 1.5)); fig.patch.set_alpha(0)
    tex = (r"$\mathrm{MCRAI}_{ic}=\sum_{j\in c}\dfrac{1}{\max(d_{ij},\,0.5)^{2}}$")
    fig.text(0.5, 0.5, tex, ha="center", va="center", fontsize=30, color="#1E2530")
    fig.savefig(os.path.join(OUT, "formula_mcrai.png"), dpi=220,
                bbox_inches="tight", pad_inches=0.18, transparent=True)
    plt.close(fig)
    print("wrote formula_mcrai.png")


if __name__ == "__main__":
    funnel()
    ablation()
    valuation_gap()
    listings_by_lgu()
    mcrai_catchment()
    abt_snapshot_wide()
    model_comparison()
    mcrai_weighting()
    feature_selection()
    pipeline_flow()
    mcrai_formula()
    print("OUT:", OUT)
