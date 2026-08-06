"""Build the full defense deck as a single self-contained HTML file from the storyboard.
Design language matches defense_mockup.html (warm off-white, deep-green accent, low density).
Run:  python3 build_deck.py   ->  defense_deck.html
"""
import html, os

DG   = "../Manuscript/diagrams/"
EDA  = "../EDA/plots/"
DECK = "assets/deck/"

# ---- slide builders -------------------------------------------------------
def esc(s): return html.escape(str(s))
def cite(c): return f'<div class="cite">{esc(c)}</div>' if c else ""

def title():
    return ('<div class="slide title-slide">'
            '<div class="kicker">UA&amp;P · BS Data Science · June 2026</div>'
            '<h1>Predicting Open-Market<br>Residential Property Values<br>in Metro Cebu</h1>'
            '<div class="rule"></div>'
            '<div class="lead muted">Using Machine Learning and Geospatial Features</div>'
            '<div class="meta">Chris Dominic Estreba<br>BS Data Science Capstone</div></div>')

def divider(num, name):
    return (f'<div class="slide divider"><div class="num">{esc(num)}</div>'
            f'<h2>{esc(name)}</h2></div>')

def picture(head, sub="", q="", c="", photo=""):
    body = f'<h2>{esc(head)}</h2>'
    if sub: body += f'<div class="sub">{esc(sub)}</div>'
    if q:   body += f'<div class="q">{esc(q)}</div>'
    return (f'<div class="slide pic-slide"><div class="pic-frame">[ photo: {esc(photo)} ]</div>'
            f'<div class="pic-copy">{body}</div>{cite(c)}</div>')

def statement(text, sub="", kicker="", c="", stat="", align="center"):
    cen = "center" if align == "center" else ""
    slidecls = "center-slide" if align == "center" else "left-statement"
    inner = ""
    if kicker: inner += f'<div class="kicker">{esc(kicker)}</div>'
    if stat:   inner += f'<div class="big-stat {cen}">{esc(stat)}</div>'
    inner += f'<h2 class="{cen}">{esc(text)}</h2>'
    if sub:    inner += f'<div class="sub {cen}">{esc(sub)}</div>'
    return f'<div class="slide {slidecls}">{inner}{cite(c)}</div>'

def two_beat(first, second, c=""):
    """Two statements on one slide; the second animates in on click (PowerPoint)."""
    return (f'<div class="slide center-slide two-beat">'
            f'<h2 class="center beat1">{esc(first)}</h2>'
            f'<h2 class="center beat2 accent">{esc(second)}</h2>'
            f'<div class="reveal-hint">▶ second line animates in on click</div>{cite(c)}</div>')

def qa(question, answer, sub="", c=""):
    """Side-by-side: question on the left, answer on the right. For 'Why X?' slides."""
    s = f'<div class="qa-sub">{esc(sub)}</div>' if sub else ""
    return (f'<div class="slide qa-slide"><div class="qa-q">{esc(question)}</div>'
            f'<div class="qa-a"><h2>{esc(answer)}</h2>{s}</div>{cite(c)}</div>')

def points(kicker, items, c=""):
    lis = "".join(f"<li>{i}</li>" for i in items)   # items may carry <strong>
    return (f'<div class="slide"><div class="kicker">{esc(kicker)}</div>'
            f'<ul class="points">{lis}</ul>{cite(c)}</div>')

def plot(kicker, img, caption="", c="", contain=True):
    cls = "contain" if contain else ""
    cap = f'<div class="caption">{caption}</div>' if caption else ""
    return (f'<div class="slide plot-slide"><div class="kicker">{esc(kicker)}</div>'
            f'<div class="plot-wrap"><img class="{cls}" src="{img}"></div>{cap}{cite(c)}</div>')

def insight(kicker, img, bullets, c=""):
    """plot left + takeaway bullets right. Bullets are the point, grounded in the manuscript."""
    lis = "".join(f"<li>{b}</li>" for b in bullets)
    return (f'<div class="slide insight-slide"><div class="kicker">{esc(kicker)}</div>'
            f'<div class="insight-row"><div class="insight-plot"><img src="{img}"></div>'
            f'<ul class="insight-points">{lis}</ul></div>{cite(c)}</div>')

def table(kicker, headers, rows):
    th = "".join(f"<th>{esc(h)}</th>" for h in headers)
    tr = "".join("<tr>" + "".join(f'<td class="{ "num" if j else "" }">{esc(c)}</td>'
                 for j, c in enumerate(r)) + "</tr>" for r in rows)
    return (f'<div class="slide"><div class="kicker">{esc(kicker)}</div>'
            f'<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>')

def formula(kicker, name, tex, sub, c=""):
    return (f'<div class="slide center-slide"><div class="kicker">{esc(kicker)}</div>'
            f'<h2 class="center">{esc(name)}</h2>'
            f'<div class="formula">{tex}</div>'
            f'<div class="sub center">{esc(sub)}</div>{cite(c)}</div>')

def flow(kicker, stages):
    pills = '<span class="arrow">→</span>'.join(f'<span class="pill">{esc(s)}</span>' for s in stages)
    return (f'<div class="slide center-slide"><div class="kicker">{esc(kicker)}</div>'
            f'<div class="flow">{pills}</div></div>')

def claim_support(claim, bullets, kicker="", c="", stat="", sub=""):
    """Big claim + 2-3 supporting bullets, so a claim slide gives narrative flow."""
    inner = ""
    if kicker: inner += f'<div class="kicker">{esc(kicker)}</div>'
    if stat:   inner += f'<div class="big-stat">{esc(stat)}</div>'
    inner += f'<h2>{esc(claim)}</h2>'
    if sub:    inner += f'<div class="sub">{esc(sub)}</div>'
    lis = "".join(f"<li>{b}</li>" for b in bullets)
    inner += f'<ul class="support">{lis}</ul>'
    return f'<div class="slide claim-support">{inner}{cite(c)}</div>'

def split(kicker, img1, img2, cap1="", cap2="", c=""):
    """Two visuals side by side (e.g., map + distribution)."""
    def col(img, cap):
        ca = f'<div class="caption">{cap}</div>' if cap else ""
        return f'<div class="split-col"><div class="split-img"><img src="{img}"></div>{ca}</div>'
    return (f'<div class="slide split-slide"><div class="kicker">{esc(kicker)}</div>'
            f'<div class="split-row">{col(img1,cap1)}{col(img2,cap2)}</div>{cite(c)}</div>')

def feature_matrix(kicker, headers, rows, c=""):
    """rows: (group, condo, houses, lot). Shows which features each stratum uses."""
    th = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = ""
    for r in rows:
        body += "<tr><td class='grp'>" + r[0] + "</td>" + "".join(f"<td class='mk'>{x}</td>" for x in r[1:]) + "</tr>"
    return (f'<div class="slide matrix-slide"><div class="kicker">{esc(kicker)}</div>'
            f'<table class="matrix"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>{cite(c)}</div>')

def close(lead, accent):
    return (f'<div class="slide center-slide"><div class="lead center">{esc(lead)}</div>'
            f'<h2 class="center accent">{esc(accent)}</h2></div>')

def references(items):
    lis = "".join(f"<li>{esc(i)}</li>" for i in items)
    return (f'<div class="slide refs-slide"><div class="kicker">References</div>'
            f'<ol class="refs">{lis}</ol></div>')

def thankyou():
    return ('<div class="slide divider"><h2>Thank you</h2>'
            '<div class="num" style="margin-top:18px">Chris Dominic Estreba · Questions welcome</div></div>')

# ---- the deck -------------------------------------------------------------
S = []
# SECTION 1 — THE PROPERTY
S += [title()]
S += [picture("Everyone needs a place to live.", photo="a Cebu family / a home")]
S += [picture("A home is the biggest purchase most families ever make.", photo="Cebu homes / skyline")]
S += [picture("You find one. ₱6.5M.", q="Is that fair?", photo="a property listing")]
S += [picture("Ask a broker — you get a number.", photo="a real-estate broker")]
S += [picture("Ask an appraiser — you get a different one.", photo="an appraiser at work")]
S += [statement("None of them agree. And none of them says why.")]
S += [picture("Now you're the seller. What is it worth?", photo="a 'For Sale' sign")]
S += [picture("Too high, it sits for months. Too low, you leave money behind.", photo="an empty house / keys")]
S += [picture("Everyone guesses — from a different corner.", photo="one house, five question marks (buyer · seller · broker · bank · LGU)")]
S += [picture("BIR zonal values — built for taxation, not live market prices. And not always updated.", c="BIR, n.d.; Otsuka et al., 2023", photo="a tax / zonal schedule")]
S += [picture("Bank appraisals — tied to lending and collateral risk. A different question than market value.", photo="a bank facade")]
S += [picture("Online listings — asking prices, not verified sales. Full of seller strategy and noise.", photo="a property listings website")]
S += [two_beat("Each one is useful. But they answer different questions — and they don't line up.",
               "The references exist. Nothing connects them.")]
# SECTION 2 — THE MARKET
S += [divider("02", "The Market")]
S += [claim_support("Cebu's economy grew in 2024.", [
    "Among the fastest-growing provinces in the country.",
    "Driven by IT-BPM and call-center expansion.",
    "And a strong post-pandemic rebound in tourism."], stat="7.3%", c="PSA Cebu, 2025")]
S += [claim_support("And home prices followed in 2025.", [
    "Metro Cebu's growth — the highest rate outside Metro Manila.",
    "From the BSP residential property price index (RREPI).",
    "Prices moving faster than benchmarks and incomes can adjust."], stat="11.5%", c="BSP, 2025")]
S += [picture("New infrastructure keeps redrawing what counts as ‘near’.", photo="CBRT / Cebu–Cordova Expressway / SRP")]
# SECTION 3 — THE QUESTION
S += [divider("03", "The Question")]
S += [statement("No defensible, market-facing price reference for Metro Cebu homes.", kicker="The business problem")]
S += [claim_support("Turn a property — and where it sits — into a defensible price per square meter.", [
    "Property-level data at scale, drawn from online listings.",
    "Location turned into measurable features — distances, accessibility, neighborhood price.",
    "A model that generalizes honestly, and explains its reasoning."], kicker="The data problem")]
S += [points("Objectives", ["<strong>Predictive</strong> — estimate open-market price per square meter across Metro Cebu.",
                            "<strong>Prescriptive</strong> — show where those estimates diverge from official benchmarks."])]
S += [points("Research Questions", ["<strong>1</strong> &nbsp; What value drivers influence price?",
                                    "<strong>2</strong> &nbsp; Which model deploys best?",
                                    "<strong>3</strong> &nbsp; Do geospatial features help?",
                                    "<strong>4</strong> &nbsp; How large is the BIR gap?"])]
S += [statement("A stratified, explainable ML model — delivered as a prototype for triangulation.", kicker="The solution")]
S += [flow("Roadmap — CRISP-DM", ["Business", "Data", "Prep", "Modeling", "Evaluation", "Deployment"])]
# SECTION 4 — THE FIELD
S += [divider("04", "The Field")]
S += [points("Two traditions", ["<strong>Hedonic regression</strong> — interpretable, classic.",
                                "<strong>Machine learning</strong> — flexible, higher accuracy."], c="Rosen, 1974; Breiman, 2001")]
S += [points("What drives price in the literature", ["Structural", "Economic / benchmark", "Geospatial / accessibility", "Amenity / point-of-interest"])]
S += [points("International evidence", ["Tree models tend to outperform linear models on tabular property data.",
                                       "But small samples demand caution."], c="Grinsztajn et al., 2022; Tanamal et al., 2023")]
S += [points("Philippine &amp; Cebu evidence", ["ML work is mostly Manila / Pangasinan-centric.",
                                                "<strong>Agosto (2020)</strong> is the only Cebu study — transport accessibility is the primary driver."],
             c="Viray, 2023; Ramolete et al., 2023; Agosto, 2020")]
S += [statement("Nothing property-level, geospatial, and explainable — for Metro Cebu.", kicker="The gap")]
S += [claim_support("This study builds exactly that.", [
    "Property-level — every listing geocoded across the six LGUs.",
    "Open-market — aligned to the IVS Market Value basis.",
    "Geospatial and explainable — with SHAP behind every prediction."], kicker="Our bridge")]
S += [qa("Why open-market listings?", "The closest available proxy to IVS Market Value.",
         sub="Arm's-length asking evidence — the basis a willing buyer and seller actually meet on.", c="IVSC, 2025")]
S += [qa("Why geospatial features?", "Location is price — so we construct the location signal, not ingest it.")]
# SECTION 5 — THE DATA
S += [divider("05", "The Data")]
S += [insight("Collection funnel", DECK+"funnel_collection.png", [
    "16,561 listings scraped — only <strong>3,616</strong> survived.",
    "Geocoding, the six-LGU and residential filters, a price-per-sqm sanity band, and de-duplication did the cutting.",
    "OnePropertee was dropped entirely — city-centroid geocoding and mis-extracted prices."])]
S += [plot("Study area", DG+"lgu_boundaries.png", "The six LGUs in scope.")]
S += [split("Where the listings sit", DG+"properties_by_stratum.png", DECK+"listings_by_lgu.png",
            cap1="Across the six LGUs.", cap2="Concentrated in Cebu City and the island; thin in the south.")]
S += [plot("One row of the data", DECK+"abt_snapshot_wide.png", "18 of 51 columns — structural, location, distances, MCRAI, benchmarks.")]
S += [plot("Engineered location — CBD distance", DG+"study_area_clean.png",
           "Shortest-path road distance to 8 polycentric nodes.", c="Giuliano &amp; Small, 1991; McMillen, 2003; JICA, 2015; Boeing, 2017")]
S += [formula("MCRAI — what it is", "Metro Cebu Residential Accessibility Index (MCRAI)",
              "MCRAI<sub>ic</sub> = &Sigma;<sub>j&isin;c</sub> 1 / max(d<sub>ij</sub>, 0.5)<sup>&beta;</sup> &nbsp;&nbsp; (&beta; = 2)",
              "Nearer amenities count more — accessibility decays with the square of road-distance.", c="Hansen, 1959")]
S += [plot("MCRAI — how it's built", DG+"amenities_map.png",
           "Eight amenity categories, each with its own radius. The composite keeps only positive-signal categories.")]
S += [insight("MCRAI — how one property scores", DECK+"mcrai_catchment.png", [
    "Each category has its own catchment radius (1–5 km).",
    "Nearer amenities count more — inverse-square decay (β = 2).",
    "Transport enters separately, as road-network distance."], c="Hansen, 1959")]
S += [plot("Engineered location — spatial lag", EDA+"09_data_integrity/Master_geocoding_clusters.png",
           "Mean price of nearby same-type listings within 500 m.", c="Tobler, 1970")]
S += [insight("Price per square meter is skewed", EDA+"01_target/all_strata_price_boxplot.png", [
    "Price per square meter is right-skewed — a few premium units stretch the tail.",
    "Modeled in <strong>log</strong>: it tames the skew but keeps a per-unit meaning.",
    "Predictions are back-transformed for the price surface."])]
S += [insight("Price varies across the map", EDA+"02_geographic/price_by_lgu_faceted.png", [
    "Premium signal sits in the core and island: Cebu City ~₱113,600/sqm, Mandaue ~₱96,100, Lapu-Lapu ~₱92,100.",
    "Talisay, Minglanilla, Consolacion form a lower band (~₱47–57k).",
    "Location can't be assumed uniform — it has to be modeled."])]
S += [insight("Do we trust the features?", EDA+"04_correlation/Houses_feature_correlation_heatmap.png", [
    "Several CBD-distance features move together — the southern corridor is geographically nested.",
    "A flag for the linear baseline, not the trees: OLS trimmed the collinear terms (confirmed with VIF).",
    "Random Forest tolerates correlated predictors, so the meaningful nodes stayed."])]
# SECTION 6 — GROUNDWORK
S += [divider("06", "Groundwork")]
S += [insight("The finding that changed everything", EDA+"01_target/all_strata_price_boxplot.png", [
    "The condo median runs ≈ <strong>5.8×</strong> the vacant-lot median.",
    "Built area vs land-only are different price logics.",
    "A single pooled model would blur them — so we stratify by type."])]
S += [claim_support("Cleaning kept every decision visible.", [
    "Imputed values were flagged, never silently filled.",
    "Structurally-absent fields (beds/baths for lots) left blank, not faked.",
    "Hard duplicates dropped; a price-per-sqm sanity band applied."], kicker="Cleaning, honestly")]
S += [claim_support("One feature was quietly hijacking the target.", [
    "A scale-selector feature dominated the SHAP rankings.",
    "The target had come to mean two different things across scrape batches.",
    "Tracing and fixing it is why the final metrics can be trusted."], kicker="A data-integrity story")]
# SECTION 7 — THE BUILD
S += [divider("07", "The Build")]
S += [statement("A single model would treat condos, houses, and lots as one market — and they differ 5.8×.", kicker="One model isn't enough")]
S += [points("So we built three", ["<strong>Condominium</strong> — 1,300", "<strong>Houses</strong> — 1,223", "<strong>Vacant Lot</strong> — 849"],
             c="Dröes et al., 2019; Usman et al., 2020")]
S += [feature_matrix("Features per stratum", ["Feature group", "Condo", "Houses", "Lot"], [
    ("Structural — area", "✓", "✓", "✓"),
    ("Bedrooms / bathrooms", "✓", "✓", "—"),
    ("CBD distances (8 nodes)", "✓", "✓", "✓"),
    ("MCRAI composite", "✓", "✓", "—"),
    ("MCRAI individual categories", "—", "—", "✓ (6)"),
    ("BIR zonal + spatial lag", "✓", "✓", "✓"),
    ("Property-type dummies", "—", "✓", "—"),
    ("Total features", "21", "24", "22"),
])]
S += [points("The model lineup", [
    "<strong>OLS</strong> — interpretable hedonic baseline.",
    "<strong>Random Forest &amp; XGBoost</strong> — capture non-linear, interacting effects.",
    "<strong>SHAP</strong> — explains every prediction, feature by feature."],
    c="Rosen, 1974; Breiman, 2001; Chen &amp; Guestrin, 2016; Lundberg &amp; Lee, 2017")]
S += [claim_support("GroupKFold by location — the honest test.", [
    "Listings are grouped by coordinate cluster.",
    "The same spot never appears in both train and test.",
    "Stricter than a random 80/20 split — it blocks neighborhood memorization."], kicker="Honest evaluation")]
S += [points("Random Forest deployed (RQ2)", [
    "Tree models beat OLS in every stratum.",
    "RF edged XGBoost (19.3 vs 19.8 / 22.7 vs 23.6 / 38.4 vs 40.2 MdAPE).",
    "Deployed for robustness on small samples and simplicity."])]
# SECTION 8 — THE APPRAISAL
S += [divider("08", "The Appraisal")]
S += [table("Headline accuracy", ["Property type", "Typical error (MdAPE)", "Within 20% (PE20)"],
            [["Condominium", "19.3%", "51%"], ["Houses", "22.7%", "44%"], ["Vacant Lot", "38.4%", "26%"]])]
S += [points("What that means", [
    "<strong>MdAPE</strong> — half of estimates fall within this error.",
    "<strong>PE20</strong> — the share landing within 20% (the practical hit-rate).",
    "Reported with MAPE, COD, PRD — but not claiming IAAO compliance."])]
S += [insight("Do geospatial features help? (RQ3)", DECK+"ablation_tiers.png", [
    "Geospatial features improve <strong>every</strong> stratum over structural-only.",
    "Biggest lift where benchmarks are weakest: vacant lots (+13 pts) and condos (+5.7).",
    "For houses, city + BIR zonal already capture most of the location signal."])]
S += [insight("What drives price — condominiums (RQ1)", EDA+"10_stratified_models/shap_condo_rf_bar.png", [
    "Neighborhood price level (spatial lag) leads — condos track their block.",
    "Weight spreads across several nodes — Consolacion, airport, Mactan, CBP.",
    "The signature of a multi-node, polycentric market."])]
S += [insight("What drives price — houses (RQ1)", EDA+"10_stratified_models/shap_houses_rf_bar.png", [
    "Distance to <strong>Cebu Business Park</strong> is the single strongest driver.",
    "Classic bid-rent: detached-house value falls with distance from the core.",
    "Amenities enter only as the bundled MCRAI composite."])]
S += [insight("What drives price — vacant lots (RQ1)", EDA+"10_stratified_models/shap_lot_rf_bar.png", [
    "Distance to Cebu Business Park leads — the steepest bid-rent gradient of the three.",
    "Individual amenities are the second-largest driver — bare land responds to specific nearby access.",
    "Still the weakest stratum: unrecorded parcel attributes (frontage, zoning) cap accuracy."])]
S += [insight("The valuation gap (RQ4)", DECK+"valuation_gap_lots.png", [
    "Market prices run ~<strong>3×</strong> the BIR zonal benchmark for vacant lots.",
    "Systematic, not noise — listings beat BIR in nearly every LGU.",
    "A signal that benchmarks are stale — not a correction factor to apply."])]
S += [points("Is it good enough?", ["A triangulation reference, not a replacement.",
                                    "Strongest for condos and houses; indicative for lots.",
                                    "It complements professional judgment — never replaces it."])]
# SECTION 9 — THE WALKTHROUGH
S += [divider("09", "The Walkthrough")]
S += [plot("Market Map", DECK+"webapp_market_map.png", "Open-market listings with filters.", contain=True)]
S += [plot("Price Surface", DECK+"webapp_price_surface.png", "Predicted ₱/sqm by barangay.", contain=True)]
S += [plot("Property Predictor", DECK+"webapp_predictor.png", "A live estimate — and its SHAP reasoning.", contain=True)]
# SECTION 10 — THE CLOSE
S += [divider("10", "The Close")]
S += [points("Answers to the four questions", ["<strong>RQ1</strong> — Location dominates; drivers differ by type.",
                                               "<strong>RQ2</strong> — Random Forest deployed.",
                                               "<strong>RQ3</strong> — Geospatial helps, most where benchmarks are weak.",
                                               "<strong>RQ4</strong> — The BIR gap is large and systematic."])]
S += [points("Contribution", ["<strong>Methodological</strong> — per-type modeling, polycentric distances, the two-stage MCRAI, leak-free CV.",
                              "<strong>Practical</strong> — a reproducible, explainable web prototype."])]
S += [points("Limitations", ["Asking-price ceiling (not deed-of-sale).", "Cross-sectional snapshot.", "Vacant-lot data ceiling."])]
S += [points("Recommendations — practice &amp; policy", ["Use as triangulation, not a final number.",
                                                        "Recognize secondary subcenters; MCRAI as a template, not a finished index."])]
S += [points("Recommendations — future research", ["Estimate MCRAI parameters from data.",
                                                   "Enrich parcel attributes; add a time dimension."], c="Udomsap &amp; Abid, 2020")]
S += [close("A clearer starting point for the family deciding what a home is worth —", "not the last word on it.")]
S += [references([
    "Agosto, A. (2020). Determinants of Land Values in Cebu City, Philippines.",
    "Bangko Sentral ng Pilipinas. (2025). Residential Real Estate Price Index (RREPI): Q2 2025 Report.",
    "Boeing, G. (2017). OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks.",
    "Breiman, L. (2001). Random forests.",
    "Bureau of Internal Revenue. (n.d.). Zonal Values Resources and Schedules.",
    "Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. ACM SIGKDD.",
    "Dröes, M. I., Hoesli, M., & Bourassa, S. C. (2019). Heterogeneous households and market segmentation in a hedonic framework. ERES.",
    "Giuliano, G., & Small, K. A. (1991). Subcenters in the Los Angeles region.",
    "Grinsztajn, L., Oyallon, E., & Varoquaux, G. (2022). Why do tree-based models still outperform deep learning on typical tabular data? NeurIPS 35.",
    "Hansen, W. G. (1959). How accessibility shapes land use.",
    "International Valuation Standards Council. (2025). International Valuation Standards (IVS) 2025.",
    "Japan International Cooperation Agency & MCDCB. (2015). The Roadmap Study for Sustainable Urban Development in Metro Cebu.",
    "Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. NeurIPS 30.",
    "McMillen, D. P. (2003). The return of centralization to Chicago.",
    "Otsuka, K., Manasan, R. G., & Piza, S. (2023). Local government unit income and real property tax collection in the Philippines. PIDS.",
    "Philippine Statistics Authority – Central Visayas. (2025). Cebu's economy grows by 7.3 percent in 2024.",
    "Ramolete, G. I. L., Bramaskara, B., Reyes, D. A., & Heinrich, A. (2023). Utilization of machine learning and government-based indicators for property value prediction in the Philippines. The Philippine Statistician.",
    "Rosen, S. (1974). Hedonic prices and implicit markets.",
    "Tanamal, R., Minoque, N., Wiradinata, T., Soekamto, Y., & Ratih, T. (2023). House price prediction model using Random Forest in Surabaya City. TEM Journal.",
    "Tobler, W. R. (1970). A computer movie simulating urban growth in the Detroit region.",
    "Udomsap, A., & Abid, M. (2020). Macroeconomic determinants of housing prices.",
    "Usman, H., Lizam, M., & Adekunle, M. U. (2020). A priori spatial segmentation of commercial property market using hedonic price modelling.",
    "Viray, F. S. (2023). Residential property price forecasting model for Central Pangasinan, Philippines.",
])]
S += [thankyou()]

# ---- assemble -------------------------------------------------------------
CSS = """
:root{--bg:#FAF8F4;--ink:#1A1A1A;--muted:#6B6B66;--accent:#2F5D50;--accent-soft:#E7EEEA;--line:#D9D6CF;}
*{box-sizing:border-box;margin:0;padding:0}
body{background:#E9E6E0;font-family:'Helvetica Neue',Arial,sans-serif;color:var(--ink);padding:42px 0 90px;-webkit-font-smoothing:antialiased}
.bar{position:fixed;top:0;left:0;right:0;background:#2F5D50;color:#fff;font-size:13px;letter-spacing:.04em;padding:7px 16px;z-index:50;display:flex;justify-content:space-between}
.bar a{color:#CFE0D8;text-decoration:none;margin-left:14px}
.deck{display:flex;flex-direction:column;align-items:center;gap:34px;margin-top:30px}
.slide{position:relative;width:1280px;height:720px;background:var(--bg);border-radius:6px;box-shadow:0 10px 38px rgba(0,0,0,.16);overflow:hidden;display:flex;flex-direction:column;justify-content:center;padding:88px 104px}
.snum{position:absolute;top:-24px;left:3px;font-size:12px;color:#8a8a8a}
.muted{color:var(--muted)}.accent{color:var(--accent)}.center{text-align:center}
.kicker{font-size:21px;letter-spacing:.2em;text-transform:uppercase;color:var(--accent);margin-bottom:26px;font-weight:700}
h1{font-size:60px;line-height:1.1;font-weight:700;letter-spacing:-.5px}
h2{font-size:50px;line-height:1.16;font-weight:700;letter-spacing:-.3px}
.lead{font-size:32px;line-height:1.3;font-weight:400}
.sub{font-size:25px;color:var(--muted);margin-top:22px}
.q{font-size:32px;color:var(--accent);font-weight:700;margin-top:22px}
.cite{position:absolute;right:40px;bottom:30px;font-size:15px;color:var(--muted);font-style:italic}
.center-slide{align-items:center;text-align:center}
.center-slide .kicker{text-align:center}
.left-statement h2{max-width:88%}
.qa-slide{flex-direction:row;align-items:center;gap:56px}
.qa-q{flex:0.82;font-size:38px;font-weight:700;color:var(--accent);line-height:1.16;border-right:3px solid var(--accent);padding-right:48px}
.qa-a{flex:1.1}
.qa-a h2{font-size:42px}
.qa-sub{font-size:23px;color:var(--muted);margin-top:22px;line-height:1.4}
.two-beat .beat1{font-size:42px;margin-bottom:40px}
.two-beat .beat2{font-size:50px}
.reveal-hint{position:absolute;bottom:24px;left:0;right:0;text-align:center;font-size:13px;color:var(--muted);font-style:italic;opacity:.7}
.claim-support h2{font-size:44px;max-width:94%;line-height:1.14}
.claim-support .big-stat{font-size:86px;margin-bottom:6px}
.claim-support .sub{margin-top:14px}
.claim-support .support{list-style:none;margin-top:30px}
.claim-support .support li{font-size:25px;line-height:1.4;padding-left:30px;position:relative;margin-bottom:18px;color:#33332f}
.claim-support .support li:last-child{margin-bottom:0}
.claim-support .support li::before{content:"";position:absolute;left:0;top:11px;width:11px;height:11px;background:var(--accent);border-radius:3px}
.split-slide{padding:56px 78px 50px}.split-slide .kicker{margin-bottom:12px}
.split-row{flex:1;display:flex;gap:46px;align-items:center;min-height:0;margin-top:6px}
.split-col{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;min-height:0}
.split-img{flex:1;display:flex;align-items:center;justify-content:center;min-height:0;width:100%}
.split-img img{max-width:100%;max-height:452px;object-fit:contain;border-radius:4px}
.matrix-slide .kicker{margin-bottom:18px}
.matrix{width:100%;border-collapse:collapse;font-size:22px;margin-top:6px}
.matrix th,.matrix td{padding:15px 14px;border-bottom:1px solid var(--line);text-align:center}
.matrix thead th{font-size:18px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);border-bottom:2px solid var(--accent)}
.matrix th:first-child,.matrix td.grp{text-align:left;font-weight:600}
.matrix td.mk{color:var(--accent);font-weight:700;font-size:20px}
.matrix tbody tr:last-child td{border-bottom:none}
.title-slide{justify-content:center}.title-slide .meta{margin-top:50px;font-size:22px;color:var(--muted);line-height:1.7}
.rule{width:64px;height:5px;background:var(--accent);margin:30px 0}
.divider{background:var(--accent);color:#fff;justify-content:center;align-items:center;text-align:center}
.divider .num{font-size:24px;letter-spacing:.3em;opacity:.72;margin-bottom:16px}
.divider h2{font-size:80px;color:#fff}
.pic-slide{flex-direction:row;align-items:center;gap:64px}
.pic-frame{flex:1.12;height:100%;max-height:540px;background:repeating-linear-gradient(45deg,#ECE9E2,#ECE9E2 14px,#E5E1D9 14px,#E5E1D9 28px);border:2px dashed #BDB9AF;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#9a968c;font-size:17px;text-align:center;padding:20px}
.pic-copy{flex:1;display:flex;flex-direction:column;justify-content:center}
.points{list-style:none;margin-top:30px}
.points li{font-size:29px;line-height:1.45;padding-left:34px;position:relative;margin-bottom:22px}
.points li::before{content:"";position:absolute;left:0;top:13px;width:13px;height:13px;background:var(--accent);border-radius:3px}
.insight-slide{padding:58px 84px 52px}.insight-slide .kicker{margin-bottom:12px}
.insight-row{flex:1;display:flex;align-items:center;gap:50px;min-height:0;margin-top:6px}
.insight-plot{flex:1.22;display:flex;align-items:center;justify-content:center;height:100%;min-height:0}
.insight-plot img{max-width:100%;max-height:486px;object-fit:contain;border-radius:4px}
.insight-points{flex:1;list-style:none}
.insight-points li{font-size:24px;line-height:1.4;padding-left:30px;position:relative;margin-bottom:26px}
.insight-points li:last-child{margin-bottom:0}
.insight-points li::before{content:"";position:absolute;left:0;top:10px;width:12px;height:12px;background:var(--accent);border-radius:3px}
.plot-slide{padding:62px 84px 54px}.plot-slide .kicker{margin-bottom:14px}
.plot-wrap{flex:1;display:flex;align-items:center;justify-content:center;min-height:0;margin-top:4px}
.plot-wrap img{max-width:100%;max-height:452px;object-fit:contain;border-radius:4px}
.caption{font-size:23px;color:var(--ink);margin-top:14px}
table{width:100%;border-collapse:collapse;margin-top:34px;font-size:30px}
th,td{text-align:left;padding:20px 16px;border-bottom:1px solid var(--line)}
thead th{font-size:19px;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);border-bottom:2px solid var(--accent)}
td.num{font-variant-numeric:tabular-nums;font-weight:700;color:var(--accent)}
tbody tr:last-child td{border-bottom:none}
.big-stat{font-size:128px;font-weight:700;color:var(--accent);line-height:1;margin-bottom:14px}
.formula{font-size:34px;color:var(--ink);background:var(--accent-soft);padding:26px 34px;border-radius:8px;margin:26px 0;font-family:'Cambria','Georgia',serif}
.flow{display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:10px;margin-top:18px}
.pill{background:var(--accent-soft);color:var(--accent);font-size:25px;font-weight:700;padding:14px 24px;border-radius:30px}
.arrow{color:var(--muted);font-size:26px;margin:0 4px}
.refs-slide{padding:64px 90px}.refs{margin-top:18px;columns:2;column-gap:48px;font-size:15.5px;line-height:1.5;color:#33332f}
.refs li{margin-bottom:11px;break-inside:avoid;padding-left:4px}
"""

def page():
    out = ['<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">',
           '<title>Defense Deck</title><style>', CSS, '</style></head><body>',
           f'<div class="bar"><span>Defense Deck — {len(S)} slides · ~30 min</span>'
           '<span>Predicting Open-Market Residential Property Values in Metro Cebu</span></div>',
           '<div class="deck">']
    for i, s in enumerate(S, 1):
        out.append(f'<div style="position:relative"><span class="snum">{i}</span>{s}</div>')
    out.append('</div></body></html>')
    return "".join(out)

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "defense_deck.html"), "w") as f:
    f.write(page())
print(f"wrote defense_deck.html  ({len(S)} slides)")
