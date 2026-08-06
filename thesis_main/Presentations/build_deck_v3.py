"""Build defense_deck_v3.html — SUBSTANTIVE deck, v3 (consolidated to ~39 slides).
Cool/neutral palette. Story-paced intro. Ideas merged: 1-2 slides per subsection.
Run:  python3 build_deck_v3.py  ->  defense_deck_v3.html
"""
import html, os

DG, EDA, DECK = "../Manuscript/diagrams/", "../EDA/plots/", "assets/deck/"
def esc(s): return html.escape(str(s))

SECTION = ""
SLIDES = []
def sec(name):
    global SECTION; SECTION = name
def add(title="", body="", dark=False, divider_num="", divider_sub=""):
    SLIDES.append(dict(section=SECTION, title=title, body=body, dark=dark,
                       dnum=divider_num, dsub=divider_sub))

# ---------- body-fragment helpers ----------
def bullets(items, cls="blist"):
    out = []
    for it in items:
        if isinstance(it, tuple):
            head, subs = it
            sub = "".join(f"<li>{s}</li>" for s in subs)
            out.append(f"<li>{head}<ul class='sub'>{sub}</ul></li>")
        else:
            out.append(f"<li>{it}</li>")
    return f"<ul class='{cls}'>" + "".join(out) + "</ul>"
def lead(t): return f"<p class='lead'>{t}</p>"
def claim(t): return f"<div class='claim'>{t}</div>"  # centered, narrow main-claim statement
def takeaway(t): return f"<div class='takeaway'><span>Takeaway</span>{t}</div>"
def stat_line(stat, label, c=""):
    cc = f"<span class='c'> {c}</span>" if c else ""
    return f"<div class='statrow'><div class='bigstat'>{stat}</div><div class='statlab'>{label}{cc}</div></div>"
def fig_analysis(img, points, takeaway_text="", wide=False):
    pts = bullets(points)
    tk = takeaway(takeaway_text) if takeaway_text else ""
    fcls = "fa-fig wide" if wide else "fa-fig"
    return (f"<div class='fa'><div class='{fcls}'><img src='{img}'></div>"
            f"<div class='fa-txt'>{pts}{tk}</div></div>")
def fig_full(img, caption="", takeaway_text=""):
    cap = f"<div class='figcap'>{caption}</div>" if caption else ""
    tk = takeaway(takeaway_text) if takeaway_text else ""
    return f"<div class='fig-full'><img src='{img}'>{cap}{tk}</div>"
def fig_only(img):
    return f"<div class='fig-full big'><img src='{img}'></div>"
def table(headers, rows, first_left=True, note=""):
    th = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = ""
    for r in rows:
        tds = "".join(f"<td class='{'tl' if (j==0 and first_left) else 'tc'}'>{c}</td>" for j, c in enumerate(r))
        body += f"<tr>{tds}</tr>"
    nt = f"<div class='tnote'>{note}</div>" if note else ""
    return f"<table class='dt'><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>{nt}"
def two_col(left, right):
    return f"<div class='twocol'><div>{left}</div><div>{right}</div></div>"
def feat_cols(groups):
    """groups: list of (heading, [items]) -> multi-column feature listing."""
    cols = ""
    for h, items in groups:
        li = "".join(f"<li>{i}</li>" for i in items)
        cols += f"<div class='fcol'><div class='fh'>{h}</div><ul class='flist'>{li}</ul></div>"
    return f"<div class='featgrid'>{cols}</div>"

# ============================================================ DECK CONTENT
sec("Title")
add()  # custom title render

# ----------------------------------------------------------- CH1
sec("1 · Introduction")
add(divider_num="01", title="Introduction", divider_sub="The valuation problem in Metro Cebu")
add("Where this study is set",
    fig_analysis(DG+"lgu_boundaries.png",
      ["Metro Cebu is the country's second-largest urban region; this study focuses on its central core of <b>six LGUs</b> &mdash; Cebu City, Mandaue, Lapu-Lapu, Talisay, Minglanilla, Consolacion.",
       "A <b>fast-growing economy</b>: 7.3% growth in 2024, among the fastest outside Metro Manila <span class='c'>(PSA Cebu, 2025)</span>.",
       "And a <b>fast-rising housing market</b>: 11.5% residential price growth in 2025, the highest rate outside the NCR <span class='c'>(BSP, 2025)</span>.",
       "Major infrastructure (CBRT, Cebu&ndash;Cordova Expressway, SRP) is redrawing which barangays count as accessible."], wide=True) +
    takeaway("Prices are moving faster than the references people use to interpret them."))
add("How a price is decided &mdash; four partial references",
    lead("A family buying, or an owner selling, asks the same question: what is this property worth? There is no single public source &mdash; price is pieced together from several partial references, each built to answer a <b>different</b> question.") +
    table(["Reference", "Built for", "What it misses"],
      [["Broker &amp; agent opinion", "Local market knowledge", "Not standardized or reproducible across people"],
       ["Bank appraisals", "Lending &amp; collateral risk", "Conservative; not the seller's market question"],
       ["BIR zonal values", "Taxation &amp; assessment", "Not live prices; often not updated <span class='c'>(BIR, n.d.; Otsuka et al., 2023)</span>"],
       ["Online listings", "Current, property-level", "Asking prices &mdash; full of seller strategy and noise"]],
      note="They serve different purposes, follow different assumptions, and update at different speeds &mdash; so they cannot be compared."))
add("The problem",
    claim("Metro Cebu lacks a transparent, property-level, spatially detailed reference for interpreting residential price evidence.") +
    takeaway("This study builds that missing reference layer &mdash; a decision-support tool, not a replacement for professional appraisal <span class='c'>(IVSC, 2025)</span>."))
add("Research questions and scope",
    bullets(["<b>RQ1</b> &mdash; What value drivers significantly influence residential prices in Metro Cebu?",
       "<b>RQ2</b> &mdash; Among Hedonic Regression, Random Forest, and XGBoost, which is most suitable for deployment &mdash; balancing accuracy, small-sample robustness, and interpretability?",
       "<b>RQ3</b> &mdash; Do geospatial features improve accuracy over a structural-only model, and how does that differ across property types?",
       "<b>RQ4</b> &mdash; How large is the valuation gap between model estimates and BIR zonal values across Metro Cebu?"]) +
    "<div class='subh'>Scope</div>" + bullets([
       "Six LGUs and eight polycentric CBD nodes; the <b>open-market</b> segment only for the deployed model.",
       "A prototype web application for triangulation; a cross-sectional snapshot, late 2025."]))

# ----------------------------------------------------------- CH2
sec("2 · Review of Related Literature")
add(divider_num="02", title="Review of Related Literature", divider_sub="What is known, and the gap")
add("The obstacle, and two modeling traditions",
    lead("International work consistently finds the primary obstacle to valuation in developing markets is <b>data scarcity &mdash; not valuer misconduct</b>.") +
    two_col(
      "<div class='subh'>The evidence</div>" + bullets([
        "<b>Kenya</b> &mdash; a census of 427 Nairobi valuers ranked &ldquo;limited information&rdquo; the top problem <span class='c'>(Cheloti, 2021)</span>.",
        "<b>Nigeria</b> &mdash; <b>92.7%</b> of 300 valuers cited insufficient market evidence <span class='c'>(Ajibola, 2010)</span>.",
        "The fix is not better judgment but a better, shared evidence base."]),
      "<div class='subh'>Two modeling traditions</div>" + bullets([
        "<b>Hedonic regression</b> &mdash; interpretable, one coefficient per attribute <span class='c'>(Rosen, 1974)</span>.",
        "<b>Machine learning</b> &mdash; non-linear, interacting effects <span class='c'>(Breiman, 2001)</span>; tree ensembles win on tabular data <span class='c'>(Grinsztajn et al., 2022)</span>.",
        "Regional precedent in Surabaya <span class='c'>(Tanamal et al., 2023)</span>, with small-sample caution."])))
add("Location dominates &mdash; and why we model types separately",
    bullets(["<b>Location is the dominant driver.</b> Agosto (2020), the only Cebu-specific study, finds transport accessibility the primary driver of land value; accessibility is formalized through gravity indexing <span class='c'>(Hansen, 1959)</span>, since raw distances alone are too fragmented <span class='c'>(Rey-Blanco, 2024)</span>.",
       "<b>Separate models per property type</b> are grounded in evidence: modeling submarkets separately lifted R&sup2; from <b>0.637 to 0.782</b> <span class='c'>(Dr&ouml;es et al., 2019)</span>; segmenting before fitting improved fit ~<b>7%</b> and cut error &gt;<b>10%</b> <span class='c'>(Usman et al., 2020)</span>.",
       "Different property types are priced by different logic, so one pooled equation fits all of them worse."]) +
    takeaway("The gap: no published, reproducible, property-level model for Metro Cebu integrates open-market listings, geospatial accessibility, and explainable ML. This study builds it."))

# ----------------------------------------------------------- CH3
sec("3 · Methodology")
add(divider_num="03", title="Methodology", divider_sub="Data, geospatial features, modeling design")
add("The data pipeline",
    lead("Sources: <b>Lamudi, FilipinoHomes, DotProperty</b> (open-market listings); <b>BIR zonal values</b> (benchmark); <b>Google Maps &amp; OpenStreetMap</b> (POIs, geocoding); the <b>osmnx</b> road network (node distances). Target: price per square meter.") +
    fig_full(DECK+"pipeline_flow.png"))
add("Geospatial features &mdash; distance, neighborhood, and the target",
    fig_analysis(DG+"study_area_clean.png",
      ["Shortest-path <b>road-network distance</b> (not straight-line) to <b>eight</b> economic nodes &mdash; Cebu Business Park, Mandaue, Mactan, SRP, Talisay Tabunok, Consolacion, Naga, and the airport &mdash; grounded in polycentric urban economics <span class='c'>(Giuliano &amp; Small, 1991; JICA, 2015)</span>.",
       "A <b>neighborhood price lag</b>: the average price of nearby same-type listings within 500 m <span class='c'>(Tobler, 1970)</span>.",
       "The model predicts the <b>log of price per square meter</b>; predictions are converted back for the price surface.",
       "Road distance captures real travel cost &mdash; including the Mactan bridge crossing."]))
add("MCRAI &mdash; measuring access to amenities",
    two_col(
      "<div class='subh'>The idea, in plain terms</div>" + bullets([
        "For each property, count the nearby amenities in a category (schools, groceries, hospitals, &hellip;).",
        "Closer amenities count more &mdash; the score fades with the <b>square</b> of road distance.",
        "Each category has its own reach, because a hospital serves a wider area than a corner store."]) +
      "<div class='formula'>MCRAI<sub>ic</sub> = &Sigma;<sub>j&isin;c</sub> 1 / max(d<sub>ij</sub>, 0.5)<sup>2</sup></div>"
      + "<p class='note-inline'>Distances in km, floored at 0.5 km. <span class='c'>(Hansen, 1959)</span></p>",
      fig_full(DECK+"mcrai_catchment.png")))
add("MCRAI &mdash; categories, reach, and how the weights were chosen",
    two_col(
      table(["Category", "Reach (km)"],
        [["Education", "2.5"], ["Grocery", "2.0"], ["Health", "2.0"], ["Hospitals", "5.0"],
         ["Recreation", "1.5"], ["Security", "2.0"], ["Tourism", "3.0"], ["Retail density", "1.0"]],
        note="Each reach is set to the category's catchment, refined for Metro Cebu. Transport is measured separately as road distance to the eight nodes."),
      "<div class='subh'>Weights from the market, in two stages</div>" + bullets([
        "<b>Stage 1</b> &mdash; fit a hedonic regression; each category's coefficient is its <b>implicit price</b> (sign = premium or penalty; significance = reliable) <span class='c'>(Rosen, 1974)</span>.",
        "<b>Stage 2</b> &mdash; keep the positive, significant categories and normalize their coefficients to sum to one.",
        "Result: <b>education 0.447, grocery 0.345, recreation 0.222</b>; the others stay as standalone features, not in the composite."])) +
    takeaway("The regression discovers the weights &mdash; we do not impose them."))

# ----------------------------------------------------------- CH4
sec("4 · Data Understanding")
add(divider_num="04", title="Data Understanding", divider_sub="Collection and exploratory analysis")
add("From collection to a clean ABT",
    fig_analysis(DECK+"funnel_collection.png",
      ["<b>16,561</b> listings scraped across three portals; <b>3,616</b> survived to the analytics base table.",
       "Filters: geocoding, the six-LGU and residential constraints, a price-per-sqm sanity band, distressed-listing removal, and de-duplication.",
       "<b>OnePropertee was excluded entirely</b> &mdash; bad geocoding and mis-extracted prices would have contaminated the model."],
      "A conservative funnel: roughly one in five raw listings is kept."))
add("What the data shows",
    fig_analysis(EDA+"02_geographic/price_by_lgu_faceted.png",
      ["Price per sqm is <b>right-skewed</b> (a few premium units) &mdash; which is why it is modeled in log.",
       "Sharp geographic spread: <b>Cebu City ~&#8369;113,600/sqm</b>, Mandaue ~&#8369;96,100, Lapu-Lapu ~&#8369;92,100; a lower band ~&#8369;47,100&ndash;56,800 for Talisay, Minglanilla, Consolacion.",
       "Some southern CBD distances move together &mdash; an early <b>collinearity warning</b> for the linear baseline (handled with VIF).",
       "MCRAI coverage checked before modeling: education and grocery near-complete, security sparsest &mdash; zero rates flag thin catchments, not data failure."]))

# ----------------------------------------------------------- CH5
sec("5 · Data Preparation")
add(divider_num="05", title="Data Preparation", divider_sub="Cleaning, and preparing data for the models")
add("Cleaning, and a data-integrity finding",
    bullets(["Imputed values were <b>flagged</b>, never silently filled; structurally-absent fields (beds/baths for vacant lots) were left <b>unimputed</b>, not faked.",
       "Hard duplicates were dropped and a price-per-square-meter sanity band applied; the modeling subset is <b>3,372</b> of the 3,616 assembled rows.",
       "Early models were dominated by one suspicious SHAP feature &mdash; the target had quietly come to mean <b>two different things</b> across scrape batches."]) +
    takeaway("Tracing and fixing that &mdash; redefining the target to log price per square meter &mdash; is exactly why the final metrics are dependable."))
add("Preparing the data for modeling",
    fig_analysis(DECK+"feature_selection.png",
      ["<b>Split</b> by property type into three datasets; <b>encode</b> cities as indicators; <b>assemble</b> structural, distance, MCRAI, benchmark, and spatial-lag features.",
       "Every candidate passes four screens: <b>variance inflation</b> (drop duplicates), <b>OLS significance</b> (keep what moves price), <b>leave-one-block ablation</b>, and <b>MCRAI zero rates</b>.",
       "The result is three tailored feature sets: <b>21 / 24 / 22</b>."], wide=True))

# ----------------------------------------------------------- CH6
sec("6 · Modeling")
add(divider_num="06", title="Modeling", divider_sub="Stratified models, selection, tuning")
add("One model cannot price three markets",
    stat_line("5.8&times;", "The condominium median price per square meter runs about 5.8 times the vacant-lot median.") +
    bullets([
      "Built area and land-only follow fundamentally different price logic; a single pooled model averages them into one blurred equation that fits none well.",
      "So the study fits <b>three separate models</b>, one per property type &mdash; backed by Dr&ouml;es et al. (2019) and Usman et al. (2020)."]) +
    takeaway("Stratifying is itself an evidence-based finding, not a convenience."))
add("The three feature sets",
    two_col(
      "<div class='subh'>Shared core (all three strata)</div>" + bullets([
        "Eight road-network <b>CBD distances</b>.",
        "<b>BIR zonal benchmark</b> + 500 m <b>spatial lag</b>.",
        "<b>City indicators</b> (Cebu City = reference)."]),
      "<div class='subh'>Per-stratum differences</div>" + bullets([
        "<b>Condos &amp; houses</b>: structural attributes (area, beds, baths + flags) and the single MCRAI <b>composite</b>.",
        "<b>Houses</b> add property-type indicators (single-detached, house-and-lot, townhouse).",
        "<b>Vacant lots</b>: land area only (no beds/baths) + <b>six individual MCRAI</b> categories."])) +
    takeaway("Collinearity shaped the OLS baseline (composite and redundant terms trimmed); the deployed trees tolerate it. The strata differ mainly by what each property type has. Final counts: 21 / 24 / 22."))
add("Models, selection, and tuning",
    two_col(
      "<div class='subh'>The lineup</div>" + bullets([
        "<b>OLS hedonic</b> &mdash; interpretable baseline, HC3 robust errors <span class='c'>(Rosen, 1974)</span>.",
        "<b>Random Forest</b> &mdash; non-linear, robust on small samples <span class='c'>(Breiman, 2001)</span>.",
        "<b>XGBoost</b> &mdash; gradient boosting <span class='c'>(Chen &amp; Guestrin, 2016)</span>; <b>SHAP</b> explains every prediction <span class='c'>(Lundberg &amp; Lee, 2017)</span>."]),
      "<div class='subh'>Why these, and tuning</div>" + bullets([
        "Set aside: SVR (hard to tune, weak interpretability), LASSO/Ridge (subsumed by OLS), deep nets (need &gt;10,000 samples).",
        "Deployed Random Forest <b>tuned per stratum</b> (300 trees; max-features 0.7 / 1.0 / 1.0; min-leaf 1 / 2 / 1).",
        "Comparators run at standard settings, so the head-to-head stays fair."])))

# ----------------------------------------------------------- CH7
sec("7 · Evaluation")
add(divider_num="07", title="Evaluation", divider_sub="Accuracy, model comparison, ablation")
add("Headline accuracy &mdash; all three models",
    lead("Estimated under a strict, <b>leak-free protocol</b>: GroupKFold(5) by coordinate cluster &mdash; the same location never appears in both train and test folds, so the model cannot memorize a neighborhood.") +
    two_col(
      "<div class='subh'>MdAPE &mdash; typical error (lower better)</div>" +
      table(["Type", "OLS", "RF &dagger;", "XGB"],
        [["Condo", "24.5%", "19.3%", "19.8%"],
         ["Houses", "25.1%", "22.7%", "23.6%"],
         ["Lot", "44.8%", "38.4%", "40.2%"]]),
      "<div class='subh'>PE20 &mdash; share within 20% (higher better)</div>" +
      table(["Type", "OLS", "RF &dagger;", "XGB"],
        [["Condo", "40%", "51%", "50%"],
         ["Houses", "41%", "44%", "43%"],
         ["Lot", "22%", "26%", "27%"]])) +
    takeaway("&dagger; Deployed. Both tree models beat OLS in every stratum; Random Forest is best-or-tied and deployed. Condos and houses estimate well; vacant lots remain weakest. (The study does not claim IAAO assessment-grade compliance.)"))
add("Which model performed best? (RQ2)",
    fig_analysis(DECK+"model_comparison.png",
      ["Under identical leak-free folds, <b>both tree models beat the OLS baseline</b> in every stratum.",
       "Random Forest and XGBoost are close; RF edges it on grouped-CV (19.3 vs 19.8 / 22.7 vs 23.6 / 38.4 vs 40.2).",
       "Because the tree models are so close, the fair reading is &ldquo;RF best-or-tied.&rdquo;",
       "<b>Random Forest was deployed</b> &mdash; robust on small samples, and simpler to maintain."]))
add("Do geospatial features earn their place? (RQ3)",
    fig_analysis(DECK+"ablation_tiers.png",
      ["A three-tier ablation under identical folds: Structural &rarr; + Administrative &rarr; + Geospatial.",
       "Geospatial features improve <b>every</b> stratum vs structural-only: condo +5.7, houses +4.2, lot +13.0 points.",
       "On top of administrative location (city + BIR zonal): condo +3.7, lot +3.8, houses &asymp; &minus;0.7.",
       "<b>They add the most where benchmarks are weakest</b> &mdash; vertical condos and bare land."]))

# ----------------------------------------------------------- CH8
sec("8 · Results & Discussion")
add(divider_num="08", title="Results and Discussion", divider_sub="Drivers and spatial structure")
add("What drives value, and the polycentric structure (RQ1)",
    bullets(["<b>Location dominates</b> in every stratum &mdash; the geospatial block carries most of the SHAP attribution.",
       "<b>Drivers differ by type</b>: condos track their neighborhood price (spatial lag); houses and lots are driven by distance to <b>Cebu Business Park</b> (classic bid-rent); bare land also responds to individual amenity access.",
       "<b>MCRAI is selective</b> &mdash; education, grocery, recreation carry positive weight; security, tourism, retail behave as diagnostics, not premiums.",
       "The model learned a <b>polycentric</b>, not monocentric, structure: CBP anchors land and housing, but condo weight spreads across the Mactan/airport corridor and the Mandaue&ndash;Consolacion nodes <span class='c'>(Giuliano &amp; Small, 1991; JICA, 2015)</span>."]) +
    takeaway("Negative MCRAI signs reflect spatial sorting &mdash; these uses cluster where congestion deters some buyers <span class='c'>(Tiebout, 1956; Bayer &amp; McMillan, 2012)</span> &mdash; not proof of harm."))
add("The valuation gap (RQ4)",
    fig_analysis(DECK+"valuation_gap_lots.png",
      ["On the clean land-to-land comparison, vacant-lot market price runs <b>~3&times; the BIR benchmark overall</b>.",
       "From <b>~2.2&times; in Cebu City to ~4.8&times; in Mandaue</b>; listings exceed the benchmark in nearly every LGU.",
       "The gap is <b>large, positive, and systematic</b> &mdash; BIR zonal values sit well below the open market.",
       "Read it as a <b>research signal that benchmarks are stale</b> &mdash; not a correction factor to apply."]))

# ----------------------------------------------------------- THE TOOL
sec("The Decision-Support Tool")
add("The decision-support tool &mdash; the applied deliverable",
    fig_analysis(DECK+"webapp_price_surface.png",
      ["<b>Market Map</b> &mdash; open-market listings with filters and market-intelligence summaries.",
       "<b>Price Surface</b> &mdash; the predicted price-per-square-meter surface, aggregated by barangay.",
       "<b>Property Predictor</b> &mdash; a property-level prediction with its SHAP breakdown; the tool always shows its reasoning.",
       "The backend runs the <b>exact deployed Random Forest models</b>."], wide=True))

# ----------------------------------------------------------- CH9
sec("9 · Conclusions")
add(divider_num="09", title="Conclusions", divider_sub="Answers, contributions, limits")
add("Answers, contributions, and limits",
    two_col(
      "<div class='subh'>Answers to the research questions</div>" + bullets([
        "<b>RQ1</b> &mdash; Location dominates; drivers differ by type (spatial lag for condos; CBP distance for houses and lots; amenities for bare land).",
        "<b>RQ2</b> &mdash; Tree models beat OLS everywhere; RF best-or-tied with XGBoost, deployed for robustness and simplicity.",
        "<b>RQ3</b> &mdash; Geospatial features materially help, most where benchmarks are weakest.",
        "<b>RQ4</b> &mdash; The BIR gap is large, positive, and systematic (~3&times; on the clean lot comparison)."]),
      "<div class='subh'>Contributions &amp; limits</div>" + bullets([
        "Per-type modeling with evidence-based feature selection; a polycentric distance set; a two-stage MCRAI; all results under leak-free grouped CV.",
        "A reproducible, explainable web prototype over the deployed models.",
        "<b>Limits</b>: an asking-price ceiling (listings, not deeds); a cross-sectional snapshot; a vacant-lot data ceiling; thin LGU&times;type cells."])))

# ----------------------------------------------------------- CH10
sec("10 · Recommendations")
add(divider_num="10", title="Recommendations", divider_sub="Practice, policy, future work")
add("Recommendations",
    two_col(
      "<div class='subh'>Practice &amp; policy</div>" + bullets([
        "Read the surface as a <b>triangulation tool</b>, alongside zonal values and comparables &mdash; not a final appraisal.",
        "Weight polycentric distance and property type ahead of the amenity composite.",
        "Keep recognizing secondary and corridor subcenters (Mactan, Consolacion, Naga), not just CBP.",
        "Treat the valuation gap as a research signal; validate against transactions before operational use."]),
      "<div class='subh'>Future research</div>" + bullets([
        "Put MCRAI on an empirical footing &mdash; estimate the decay rate, radii, and weights from data.",
        "Test spatial heterogeneity directly with Geographically Weighted Regression (GWR / MGWR).",
        "Enrich inputs &mdash; parcel attributes (frontage, corner-lot), a time dimension, macro indicators <span class='c'>(Udomsap &amp; Abid, 2020)</span>.",
        "Triangulate against complementary reference prices, not a single target."])))
add("Closing",
    claim("A defensible, reproducible template for local valuation analytics &mdash; a clearer starting point for deciding what a home is worth, not the last word.") +
    takeaway("The contribution is a demonstrated workflow &mdash; a custom MCRAI, a polycentric distance set, and a Random Forest + SHAP pipeline that can be rebuilt, checked, and adapted for other Philippine secondary cities."))

# ----------------------------------------------------------- REFS + THANKS
sec("References")
REFS = [
 "Agosto, A. (2020). Determinants of Land Values in Cebu City, Philippines.",
 "Ajibola, M. O. (2010). Valuation inaccuracy: An examination of causes in Lagos Metropolis.",
 "Bangko Sentral ng Pilipinas. (2025). Residential Real Estate Price Index (RREPI): Q2 2025 Report.",
 "Bayer, P., &amp; McMillan, R. (2012). Tiebout sorting and neighborhood stratification.",
 "Breiman, L. (2001). Random forests.",
 "Bureau of Internal Revenue. (n.d.). Zonal Values Resources and Schedules.",
 "Chen, T., &amp; Guestrin, C. (2016). XGBoost: A scalable tree boosting system. ACM SIGKDD.",
 "Cheloti, I. (2021). Valuation problems in Kenya: A census of Nairobi valuers.",
 "Dr&ouml;es, M. I., Hoesli, M., &amp; Bourassa, S. C. (2019). Heterogeneous households and market segmentation in a hedonic framework. ERES.",
 "Giuliano, G., &amp; Small, K. A. (1991). Subcenters in the Los Angeles region.",
 "Grinsztajn, L., Oyallon, E., &amp; Varoquaux, G. (2022). Why do tree-based models still outperform deep learning on typical tabular data? NeurIPS 35.",
 "Hansen, W. G. (1959). How accessibility shapes land use.",
 "International Valuation Standards Council. (2025). International Valuation Standards (IVS) 2025.",
 "Japan International Cooperation Agency &amp; MCDCB. (2015). The Roadmap Study for Sustainable Urban Development in Metro Cebu.",
 "Lundberg, S. M., &amp; Lee, S.-I. (2017). A unified approach to interpreting model predictions. NeurIPS 30.",
 "McMillen, D. P. (2003). The return of centralization to Chicago.",
 "Nyanda, F. (2024). House price prediction with machine learning on small samples.",
 "Otsuka, K., Manasan, R. G., &amp; Piza, S. (2023). Local government unit income and real property tax collection in the Philippines. PIDS.",
 "Philippine Statistics Authority &ndash; Central Visayas. (2025). Cebu's economy grows by 7.3 percent in 2024.",
 "Ramolete, G. I. L., Bramaskara, B., Reyes, D. A., &amp; Heinrich, A. (2023). Utilization of machine learning and government-based indicators for property value prediction in the Philippines. The Philippine Statistician.",
 "Rey-Blanco, D. (2024). Improving hedonic housing models with accessibility indicators.",
 "Rosen, S. (1974). Hedonic prices and implicit markets.",
 "Tanamal, R., Minoque, N., Wiradinata, T., Soekamto, Y., &amp; Ratih, T. (2023). House price prediction model using Random Forest in Surabaya City. TEM Journal.",
 "Tiebout, C. M. (1956). A pure theory of local expenditures.",
 "Tobler, W. R. (1970). A computer movie simulating urban growth in the Detroit region.",
 "Udomsap, A., &amp; Abid, M. (2020). Macroeconomic determinants of housing prices.",
 "Usman, H., Lizam, M., &amp; Adekunle, M. U. (2020). A priori spatial segmentation of commercial property market using hedonic price modelling.",
 "Viray, F. S. (2023). Residential property price forecasting model for Central Pangasinan, Philippines.",
 "Yang, H., Song, J., &amp; Choi, M. (2016). Measuring the externality effects of commercial land use on residential land value: Seoul.",
]
half = (len(REFS)+1)//2
add("References",
    f"<div class='refcols'><ol class='refs'>" + "".join(f"<li>{r}</li>" for r in REFS[:half]) +
    "</ol><ol class='refs' start='"+str(half+1)+"'>" + "".join(f"<li>{r}</li>" for r in REFS[half:]) + "</ol></div>")
sec("Thank you")
add(title="Thank you", divider_sub="Chris Dominic Estreba &nbsp;·&nbsp; BS Data Science, UA&amp;P", dark=True)

# ============================================================ RENDER
CSS = """
:root{--bg:#FAFBFC;--ink:#1E2530;--muted:#6E7686;--accent:#33455E;--accent2:#5B7A99;
      --soft:#EAEEF3;--line:#DEE3EA;--rule:#33455E;}
*{box-sizing:border-box;margin:0;padding:0}
body{background:#DDE1E7;font-family:'Helvetica Neue','Segoe UI',Arial,sans-serif;color:var(--ink);
     padding:40px 0 90px;-webkit-font-smoothing:antialiased}
.topbar{position:fixed;top:0;left:0;right:0;background:var(--accent);color:#fff;font-size:12.5px;
        letter-spacing:.05em;padding:7px 18px;z-index:60;display:flex;justify-content:space-between}
.deck{display:flex;flex-direction:column;align-items:center;gap:30px;margin-top:34px}
.slidewrap{position:relative}
.snum{position:absolute;top:-22px;left:2px;font-size:11px;color:#90939b}
.slide{width:1280px;height:720px;background:var(--bg);border-radius:5px;
       box-shadow:0 8px 32px rgba(30,37,48,.18);overflow:hidden;display:flex;flex-direction:column}
.hdr{display:flex;justify-content:space-between;align-items:baseline;padding:30px 56px 0}
.hdr .sec{font-size:15px;font-weight:700;letter-spacing:.13em;text-transform:uppercase;color:var(--accent)}
.hdr .pg{font-size:14px;color:var(--muted);font-variant-numeric:tabular-nums}
.hrule{height:2px;background:var(--rule);margin:9px 56px 0;opacity:.9}
.title{font-size:31px;font-weight:700;letter-spacing:-.2px;color:var(--ink);padding:20px 56px 0;line-height:1.12}
.body{flex:1;padding:18px 56px 26px;min-height:0;display:flex;flex-direction:column;justify-content:center}
.foot{display:flex;justify-content:space-between;font-size:11px;color:#9aa0ab;padding:0 56px 16px}
.lead{font-size:21px;line-height:1.4;color:#2a3340;margin-bottom:14px;font-weight:500}
.claim{max-width:64%;margin:0 auto 6px;text-align:center;font-size:30px;line-height:1.45;color:var(--ink);font-weight:500}
.subh{font-size:14px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--accent2);margin:0 0 8px}
ul.blist{list-style:none;margin:2px 0}
ul.blist>li{position:relative;padding-left:26px;margin-bottom:13px;font-size:19px;line-height:1.38;color:#262d38}
ul.blist>li::before{content:"";position:absolute;left:0;top:9px;width:11px;height:11px;background:var(--accent);border-radius:2px}
ul.sub{list-style:none;margin:7px 0 0}
ul.sub>li{position:relative;padding-left:20px;margin:5px 0;font-size:15.5px;color:var(--muted);line-height:1.34}
ul.sub>li::before{content:"";position:absolute;left:0;top:8px;width:6px;height:6px;border:1.5px solid var(--accent2);border-radius:50%}
.c{color:var(--muted);font-style:italic;font-size:.92em}
b{color:var(--ink)}
.twocol{display:flex;gap:46px}.twocol>div{flex:1}
.note-inline{font-size:14px;color:var(--muted);margin-top:8px}
.takeaway{margin-top:16px;background:var(--soft);border-left:4px solid var(--accent);border-radius:4px;
          padding:12px 18px;font-size:18px;line-height:1.35;color:#23303f}
.takeaway span{display:inline-block;font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
               color:var(--accent);margin-right:10px}
.statrow{display:flex;align-items:baseline;gap:22px;margin-bottom:18px}
.bigstat{font-size:78px;font-weight:800;color:var(--accent);line-height:1}
.statlab{font-size:21px;color:#2a3340;line-height:1.3;font-weight:500}
.fa{display:flex;gap:36px;align-items:center;height:100%}
.fa-fig{flex:1.18;display:flex;align-items:center;justify-content:center;height:100%;min-height:0}
.fa-fig.wide{flex:1.5}
.fa-fig img{max-width:100%;max-height:440px;object-fit:contain;border:1px solid var(--line);border-radius:4px;background:#fff}
.fa-txt{flex:1;display:flex;flex-direction:column;justify-content:center}
.fa-txt ul.blist>li{font-size:17.5px;margin-bottom:11px}
.fig-full{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:12px}
.fig-full img{max-width:100%;max-height:470px;object-fit:contain;border:1px solid var(--line);border-radius:4px;background:#fff}
.fig-full.big img{max-height:540px}
.figcap{font-size:17px;color:var(--muted);text-align:center;max-width:92%}
table.dt{width:100%;border-collapse:collapse;font-size:18px;margin:4px 0}
table.dt th{background:var(--accent);color:#fff;text-align:left;padding:11px 14px;font-size:15px;font-weight:700}
table.dt td{padding:10px 14px;border-bottom:1px solid var(--line)}
table.dt td.tc{text-align:center;font-variant-numeric:tabular-nums}
table.dt tbody tr:nth-child(even){background:#F1F4F8}
.tnote{font-size:14px;color:var(--muted);margin-top:10px;line-height:1.4;font-style:italic}
.formula{margin-top:14px;background:var(--soft);border-radius:6px;padding:16px;text-align:center;
         font-size:22px;font-family:'Cambria','Georgia',serif;color:var(--ink)}
.featgrid{display:flex;gap:30px;margin-top:6px}
.fcol{flex:1}
.fh{font-size:13px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--accent2);
    margin-bottom:9px;padding-bottom:5px;border-bottom:2px solid var(--soft)}
ul.flist{list-style:none}
ul.flist>li{font-size:15.5px;line-height:1.3;margin-bottom:7px;color:#2a3340;padding-left:14px;position:relative}
ul.flist>li::before{content:"·";position:absolute;left:2px;color:var(--accent2);font-weight:700}
.divider{background:var(--accent);color:#fff;height:720px;display:flex;flex-direction:column;
         justify-content:center;padding:0 90px}
.divider .dn{font-size:120px;font-weight:800;line-height:.9;opacity:.24}
.divider h2{font-size:54px;font-weight:700;margin-top:6px}
.divider .ds{font-size:22px;color:#C5D2DF;margin-top:14px;font-weight:400}
.title-slide{background:var(--bg);height:720px;display:flex;flex-direction:column;justify-content:center;padding:0 90px}
.title-slide .ey{font-size:16px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--accent)}
.title-slide h1{font-size:46px;font-weight:700;line-height:1.1;letter-spacing:-.5px;margin:22px 0;max-width:90%}
.title-slide .tr{width:70px;height:5px;background:var(--accent);margin:6px 0 24px}
.title-slide .pm{font-size:20px;color:var(--muted);line-height:1.7}
.refcols{display:flex;gap:40px}
ol.refs{flex:1;font-size:12.5px;line-height:1.42;color:#33384200;padding-left:22px;color:#363c47}
ol.refs li{margin-bottom:8px}
"""

def render():
    n = len(SLIDES)
    out = ['<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">',
           '<title>Defense Deck — v3</title><style>', CSS, '</style></head><body>',
           f'<div class="topbar"><span>Defense Deck · v3 (consolidated) · {n} slides</span>'
           '<span>Predicting Open-Market Residential Property Values in Metro Cebu</span></div>',
           '<div class="deck">']
    for i, s in enumerate(SLIDES, 1):
        out.append(f'<div class="slidewrap"><span class="snum">{i} / {n}</span>')
        if i == 1:
            out.append('<div class="slide"><div class="title-slide">'
                       '<div class="ey">University of Asia and the Pacific · BS Data Science · June 2026</div>'
                       '<h1>Predicting Open-Market Residential Property Values in Metro Cebu</h1>'
                       '<div class="tr"></div>'
                       '<div class="pm">Using Machine Learning and Geospatial Features<br><br>'
                       'Chris Dominic Estreba &nbsp;·&nbsp; BS Data Science Capstone</div></div></div>')
        elif s["dnum"]:
            out.append(f'<div class="slide"><div class="divider"><div class="dn">{s["dnum"]}</div>'
                       f'<h2>{s["title"]}</h2><div class="ds">{s["dsub"]}</div></div></div>')
        elif s["dark"]:
            out.append(f'<div class="slide"><div class="divider" style="align-items:center;text-align:center">'
                       f'<h2 style="font-size:64px">{s["title"]}</h2><div class="ds">{s["dsub"]}</div></div></div>')
        else:
            out.append('<div class="slide">'
                       f'<div class="hdr"><span class="sec">{s["section"]}</span><span class="pg">{i} / {n}</span></div>'
                       '<div class="hrule"></div>'
                       f'<div class="title">{s["title"]}</div>'
                       f'<div class="body">{s["body"]}</div></div>')
        out.append('</div>')
    out.append('</div></body></html>')
    return "".join(out)

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "defense_deck_v3.html"), "w") as f:
    f.write(render())
print(f"wrote defense_deck_v3.html  ({len(SLIDES)} slides)")
