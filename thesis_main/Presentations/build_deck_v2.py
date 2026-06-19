"""Build defense_deck_v2.html — the SUBSTANTIVE, panel-appropriate angle.
Cool/neutral palette. Story-paced intro. Full modeling detail.
Run:  python3 build_deck_v2.py  ->  defense_deck_v2.html
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

sec("Outline")
add("Outline",
    lead("The study follows the CRISP-DM arc, mapped to the thesis chapters.") +
    two_col(
      bullets(["<b>1 · Introduction</b> — the valuation problem in Metro Cebu",
        "<b>2 · Review of Related Literature</b> — what is known, and the gap",
        "<b>3 · Methodology</b> — data, geospatial features, modeling design",
        "<b>4 · Data Understanding</b> — collection and exploratory analysis",
        "<b>5 · Data Preparation</b> — cleaning, and preparing data for models"]),
      bullets(["<b>6 · Modeling</b> — stratified models, selection, tuning",
        "<b>7 · Evaluation</b> — accuracy, model comparison, ablation",
        "<b>8 · Results &amp; Discussion</b> — drivers and spatial structure",
        "<b>9 · Conclusions</b> — answers, contributions, limits",
        "<b>10 · Recommendations</b> — practice, policy, future work"])))

# ----------------------------------------------------------- CH1  (story-paced)
sec("1 · Introduction")
add(divider_num="01", title="Introduction", divider_sub="The valuation problem in Metro Cebu")

# -- context: where Cebu is --
add("Where this study is set",
    fig_analysis(DG+"lgu_boundaries.png",
      ["Metro Cebu is the country's second-largest urban region.",
       "This study focuses on its central core: <b>six local government units</b> &mdash; Cebu City, Mandaue, Lapu-Lapu, Talisay, Minglanilla, and Consolacion.",
       "Together they hold the most active transactions and the densest infrastructure."], wide=True))
add("A fast-growing economy",
    stat_line("7.3%", "Cebu economic growth in 2024 — among the fastest outside Metro Manila.", "(PSA Cebu, 2025)") +
    bullets(["Growth is led by the IT-BPM sector and call-center expansion.",
       "Tourism has rebounded strongly since the pandemic.",
       "More jobs and higher incomes mean more demand for housing."]))
add("And a fast-rising housing market",
    stat_line("11.5%", "Metro Cebu residential price growth in 2025 — the highest rate outside the National Capital Region.", "(BSP, 2025)") +
    bullets(["Major infrastructure (CBRT, Cebu&ndash;Cordova Expressway, SRP) is redrawing which barangays count as accessible.",
       "Two similar houses can now sit in very different market positions depending on access."]) +
    takeaway("Prices are moving faster than the references people use to interpret them."))

# -- how a price is decided --
add("So how is a price decided in Cebu?",
    lead("Imagine a family that finds a home, or an owner who wants to sell. Both ask the same question: what is this property actually worth?") +
    bullets(["There is no single public source that answers it.",
       "Instead, price is pieced together from several partial references.",
       "Each reference is useful &mdash; but each was built to answer a <b>different</b> question."]))
add("Four partial references",
    table(["Reference", "Built for", "What it misses"],
      [["Broker &amp; agent opinion", "Local market knowledge", "Not standardized or reproducible across people"],
       ["Bank appraisals", "Lending &amp; collateral risk", "Conservative; not the seller's market question"],
       ["BIR zonal values", "Taxation &amp; assessment", "Not live prices; often not updated <span class='c'>(BIR, n.d.; Otsuka et al., 2023)</span>"],
       ["Online listings", "Current, property-level", "Asking prices &mdash; full of seller strategy and noise"]]))
add("Useful, but they don't line up",
    lead("The references are not useless. The real problem is that they cannot be compared.") +
    bullets(["They serve different purposes, follow different assumptions, and update at different speeds.",
       "A buyer cannot tell if an asking price is fair; a seller has no anchor; banks and LGUs work from drifting benchmarks.",
       "Metro Cebu has plenty of valuation activity &mdash; but <b>no shared, spatially detailed reference layer</b>."]))

# -- the problem --
add("The problem",
    lead("Metro Cebu lacks a transparent, property-level, spatially detailed reference for interpreting residential price evidence.") +
    takeaway("This study builds that missing reference layer &mdash; a decision-support tool, not a replacement for professional appraisal <span class='c'>(IVSC, 2025)</span>."))

# -- RQs + scope --
add("Research questions",
    bullets(["<b>RQ1</b> &mdash; What value drivers significantly influence residential prices in Metro Cebu?",
       "<b>RQ2</b> &mdash; Among Hedonic Regression, Random Forest, and XGBoost, which is most suitable for deployment &mdash; balancing accuracy, small-sample robustness, and interpretability?",
       "<b>RQ3</b> &mdash; Do geospatial features improve accuracy over a structural-only model, and how does that differ across property types?",
       "<b>RQ4</b> &mdash; How large is the valuation gap between model estimates and BIR zonal values across Metro Cebu?"]))
add("Significance and scope",
    two_col(
      "<div class='subh'>Who benefits</div>" + bullets([
        "<b>Brokers &amp; appraisers</b> &mdash; an inspectable extra evidence layer.",
        "<b>Buyers, sellers, investors</b> &mdash; a transparent reference for an asking price.",
        "<b>Banks</b> &mdash; market-facing spatial evidence.",
        "<b>LGUs</b> &mdash; where benchmarks drift from the market."]),
      "<div class='subh'>Scope</div>" + bullets([
        "Six LGUs; eight polycentric CBD nodes.",
        "Open-market segment only for the deployed model.",
        "A prototype web application for triangulation.",
        "Cross-sectional snapshot, late 2025."])))

# ----------------------------------------------------------- CH2
sec("2 · Review of Related Literature")
add(divider_num="02", title="Review of Related Literature", divider_sub="What is known, and the gap")
add("Two modeling traditions",
    two_col(
      "<div class='subh'>Hedonic regression</div>" + bullets([
        "Interpretable; one explicit coefficient per attribute.",
        "The classic basis of property valuation <span class='c'>(Rosen, 1974)</span>.",
        "Struggles with non-linear effects and correlated features."]),
      "<div class='subh'>Machine learning</div>" + bullets([
        "Captures non-linear, interacting effects <span class='c'>(Breiman, 2001)</span>.",
        "Tree ensembles tend to win on tabular data <span class='c'>(Grinsztajn et al., 2022)</span>.",
        "Regional precedent in Surabaya <span class='c'>(Tanamal et al., 2023)</span>, with small-sample caution."])))
add("Location is the dominant driver",
    bullets(["Four feature families recur: <b>structural</b>, <b>economic / benchmark</b>, <b>geospatial / accessibility</b>, <b>amenity / point-of-interest</b>.",
       "<b>Agosto (2020) is the only Cebu-specific study</b> &mdash; it finds transport accessibility the primary driver of land value, followed by neighborhood quality.",
       "Accessibility is formalized through gravity indexing <span class='c'>(Hansen, 1959)</span>; raw distances alone are too fragmented to stand on their own <span class='c'>(Rey-Blanco, 2024)</span>.",
       "Philippine ML work is mostly Manila- or Pangasinan-centric <span class='c'>(Viray, 2023; Ramolete et al., 2023)</span>."]))
add("Why model property types separately?",
    lead("The decision to build separate models per property type is grounded in direct empirical evidence:") +
    bullets([
      "<b>Dr&ouml;es, Hoesli &amp; Bourassa (2019)</b> &mdash; modeling housing submarkets separately rather than pooling them lifted explanatory power substantially (R&sup2; from <b>0.637 to 0.782</b>).",
      "<b>Usman, Lizam &amp; Adekunle (2020), Malaysia</b> &mdash; segmenting the market before fitting improved model fit by about <b>7%</b> and cut prediction error by over <b>10%</b>.",
      "The intuition: different property types are priced by different logic, so one pooled equation averages those logics into a worse fit for all of them."]))
add("The research gap &mdash; and the bridge",
    two_col(
      "<div class='subh'>The gap</div>" + lead("No published, reproducible, property-level valuation model for Metro Cebu integrates open-market listings, geospatial accessibility, and explainable ML."),
      "<div class='subh'>This study</div>" + bullets([
        "Property-level &mdash; every listing geocoded across six LGUs.",
        "Open-market &mdash; aligned to the IVS Market Value basis.",
        "Geospatial &mdash; the location signal is engineered, not ingested.",
        "Explainable &mdash; SHAP behind every prediction."])))

# ----------------------------------------------------------- CH3
sec("3 · Methodology")
add(divider_num="03", title="Methodology", divider_sub="Data, geospatial features, modeling design")
add("Research design and data sources",
    lead("A quantitative, non-experimental design &mdash; predictive (estimate price) and prescriptive (surface the benchmark gap).") +
    table(["Source", "Role in the study"],
      [["Lamudi, FilipinoHomes, DotProperty", "Open-market listings &mdash; the training data"],
       ["BIR zonal values", "Administrative benchmark &mdash; the valuation-gap diagnostic"],
       ["Google Maps &amp; OpenStreetMap", "Points of interest and geocoding for MCRAI"],
       ["Road network via osmnx", "Network distances to economic nodes"]],
      note="Target variable: price per square meter. A licensed-broker check validated plausibility."))
add("The data pipeline",
    lead("Six stages turn raw listings into a model-ready analytics base table (ABT).") +
    bullets(["<b>Ingest</b> &rarr; <b>Clean</b> &rarr; <b>Geocode</b> &rarr; <b>BIR join</b> &rarr; <b>GIS features</b> &rarr; <b>ABT</b>.",
       "Spatial features &mdash; road-network distances, MCRAI accessibility, neighborhood price lag &mdash; are computed from geocoded coordinates.",
       "Collection funnel: <b>16,561 raw listings &rarr; 3,616</b> clean open-market records."]) +
    takeaway("Every spatial feature is constructed in the pipeline &mdash; the contribution is in the construction."))
add("Geospatial features &mdash; distance to economic centers",
    fig_analysis(DG+"study_area_clean.png",
      ["Shortest-path <b>road-network distance</b> (not straight-line) to <b>eight</b> economic nodes.",
       "Nodes: Cebu Business Park, Mandaue CBD, Mactan CBD, SRP, Talisay Tabunok, Consolacion, Naga City (anchor), and the airport.",
       "Grounded in polycentric urban economics <span class='c'>(Giuliano &amp; Small, 1991; McMillen, 2003; JICA, 2015)</span>.",
       "Road distance captures real travel cost &mdash; including the Mactan bridge crossing."]))
add("MCRAI &mdash; measuring access to amenities",
    two_col(
      "<div class='subh'>The idea, in plain terms</div>" + bullets([
        "For each property, count the nearby amenities in a category (schools, groceries, hospitals, &hellip;).",
        "Closer amenities count more than far ones &mdash; the score fades with the <b>square</b> of road distance.",
        "Each category has its own reach (radius), because a hospital serves a wider area than a corner store."]) +
      "<div class='formula'>MCRAI<sub>ic</sub> = &Sigma;<sub>j&isin;c</sub> 1 / max(d<sub>ij</sub>, 0.5)<sup>2</sup></div>"
      + "<p class='note-inline'>Distances in km, floored at 0.5 km. <span class='c'>(Hansen, 1959)</span></p>",
      fig_full(DECK+"mcrai_catchment.png")))
add("MCRAI &mdash; categories and reach",
    two_col(
      table(["Category", "Reach (km)"],
        [["Education", "2.5"], ["Grocery", "2.0"], ["Health", "2.0"], ["Hospitals", "5.0"],
         ["Recreation", "1.5"], ["Security", "2.0"], ["Tourism", "3.0"], ["Retail density", "1.0"]]),
      bullets([
        "Eight categories, each at its typical catchment scale.",
        "The reach values follow standard accessibility conventions &mdash; a sensible baseline.",
        "Transport access is measured <b>separately</b>, as road distance to the eight nodes.",
        "Banking proximity was dropped &mdash; no comparable study treats it as a residential amenity."])))
add("MCRAI &mdash; how the weights were chosen",
    fig_analysis(DECK+"mcrai_weighting.png",
      ["We did not assume the weights &mdash; we let the market reveal them, in two stages.",
       "<b>Stage 1:</b> fit a regression and check which categories actually raise price (the sign).",
       "<b>Stage 2:</b> for the positive ones, turn their strength into weights that sum to one.",
       "Result: <b>education 0.447, grocery 0.345, recreation 0.222</b>."], wide=True))
add("Two more design choices",
    two_col(
      "<div class='subh'>Neighborhood price (spatial lag)</div>" + bullets([
        "The average price of nearby <b>same-type</b> listings within 500 m.",
        "Captures Tobler's First Law &mdash; near things tend to be alike <span class='c'>(Tobler, 1970)</span>."]),
      "<div class='subh'>Target variable</div>" + bullets([
        "The model predicts the <b>log of price per square meter</b>.",
        "Logging tames the skew; predictions are converted back for the price surface."])))
add("Evaluation protocol &mdash; an honest test",
    lead("The headline numbers are estimated under a deliberately strict protocol.") +
    bullets(["<b>GroupKFold(5)</b>, with groups defined by <b>coordinate cluster</b>.",
       "The same location can never appear in both training and test folds.",
       "This is stricter than a random 80/20 split &mdash; it stops the model from memorizing a neighborhood and flattering itself.",
       "Every reported accuracy figure is out-of-fold."]))

# ----------------------------------------------------------- CH4
sec("4 · Data Understanding")
add(divider_num="04", title="Data Understanding", divider_sub="Collection and exploratory analysis")
add("From collection to a clean ABT",
    fig_analysis(DECK+"funnel_collection.png",
      ["<b>16,561</b> listings scraped across three portals; <b>3,616</b> survived to the ABT.",
       "Filters: geocoding, the six-LGU and residential constraints, a price-per-sqm sanity band, distressed-listing removal, and de-duplication.",
       "<b>OnePropertee was excluded entirely</b> &mdash; bad geocoding and mis-extracted prices would have contaminated the model."],
      "A conservative funnel: roughly one in five raw listings is kept."))
add("What one record looks like",
    fig_full(DECK+"abt_snapshot_wide.png",
      "A slice of the assembled ABT &mdash; 18 of 51 columns: structural attributes, coordinates, node distances, MCRAI scores, BIR benchmark, and spatial lag."))
add("Exploratory analysis &mdash; the target",
    fig_analysis(EDA+"01_target/all_strata_price_boxplot.png",
      ["Price per square meter is <b>right-skewed</b> &mdash; a few premium units stretch the upper tail.",
       "Condominiums command the highest unit prices; vacant lots the lowest (land only, no built area).",
       "This is why the target is modeled in <b>log</b> and converted back for the surface."]))
add("Price varies sharply across the map",
    fig_analysis(EDA+"02_geographic/price_by_lgu_faceted.png",
      ["The premium signal sits in the core and island: <b>Cebu City ~&#8369;113,600/sqm</b>, Mandaue ~&#8369;96,100, Lapu-Lapu ~&#8369;92,100.",
       "Talisay, Minglanilla, and Consolacion form a lower band (~&#8369;47,100&ndash;56,800).",
       "Location cannot be treated as uniform &mdash; it has to be modeled explicitly."]))
add("Can we trust the features?",
    fig_analysis(EDA+"04_correlation/Houses_feature_correlation_heatmap.png",
      ["Several southern-corridor <b>CBD distances move together</b> &mdash; an early collinearity warning.",
       "This matters for the <b>linear baseline</b>, not the trees: OLS dropped the redundant terms (confirmed with VIF).",
       "Random Forest tolerates correlated predictors, so the substantively meaningful nodes were kept."]))
add("MCRAI coverage is real, not assumed",
    two_col(
      table(["MCRAI category", "Zero rate"],
        [["Security", "26.6%"], ["Retail density", "15.8%"], ["Recreation", "12.0%"],
         ["Health", "10.0%"], ["Grocery", "4.3%"], ["Education", "0.3%"]]),
      bullets([
        "Zero rates were checked before modeling to separate true absence from data gaps.",
        "Education and grocery access are effectively complete; security is the sparsest.",
        "High zero rates flag genuinely thin amenity catchments &mdash; not a data failure."])))

# ----------------------------------------------------------- CH5
sec("5 · Data Preparation")
add(divider_num="05", title="Data Preparation", divider_sub="Cleaning, and preparing data for the models")
add("Cleaning kept every decision visible",
    bullets(["Imputed values were <b>flagged</b>, never silently filled &mdash; imputation stays auditable.",
       "Structurally-absent fields (bedrooms/bathrooms for vacant lots) were left <b>unimputed</b>, not faked.",
       "Hard duplicates were dropped and a price-per-square-meter sanity band applied.",
       "The modeling subset is <b>3,372</b> of the 3,616 assembled rows, after model-requirement filters."]) +
    takeaway("The aim was a clean, honest table &mdash; usable rows without inventing evidence."))
add("A data-integrity story",
    lead("One finding shaped how much the rest of the results can be trusted.") +
    bullets(["Early models were dominated by a single suspicious feature in the SHAP rankings.",
       "The cause: the target had quietly come to mean <b>two different things</b> across scrape batches &mdash; the feature was acting as a scale-selector.",
       "Tracing and fixing it (redefining the target to log price per square meter) is exactly why the final metrics are dependable."]))
add("Preparing the data for modeling",
    lead("Three steps turn the clean ABT into model-ready inputs.") +
    bullets([
      "<b>Split by property type</b> &mdash; condominiums, houses, and vacant lots become three separate datasets.",
      "<b>Encode and assemble</b> &mdash; cities become indicator columns; structural, distance, MCRAI, benchmark, and spatial-lag features are joined per row.",
      "<b>Select features per stratum</b> &mdash; each dataset keeps only the features that earn their place (next slide)."]))
add("How the three feature sets were chosen",
    fig_analysis(DECK+"feature_selection.png",
      ["Every candidate feature passed through four screens:",
       "<b>Variance inflation</b> &mdash; drop features that duplicate others.",
       "<b>OLS significance</b> &mdash; keep features that actually move price.",
       "<b>Leave-one-block ablation</b> + <b>MCRAI zero rates</b> &mdash; drop blocks that add nothing and empty categories.",
       "The result is three tailored feature sets: <b>21 / 24 / 22</b>."], wide=True))

# ----------------------------------------------------------- CH6
sec("6 · Modeling")
add(divider_num="06", title="Modeling", divider_sub="Stratified models, selection, tuning")
add("One model cannot price three markets",
    fig_analysis(EDA+"01_target/all_strata_price_boxplot.png",
      ["The condominium median runs <b>about 5.8&times;</b> the vacant-lot median.",
       "Built area and land-only follow fundamentally different price logic.",
       "A single pooled model averages these into one blurred equation.",
       "So the study fits <b>three separate models</b> &mdash; backed by Dr&ouml;es et al. (2019) and Usman et al. (2020)."],
      "Stratifying is itself an evidence-based finding, not a convenience."))
# -- full feature lists, one slide per stratum --
add("Features used &mdash; Condominium (21)",
    feat_cols([
      ("Structural", ["area_sqm", "bedrooms", "bathrooms", "bedrooms_imputed", "bathrooms_imputed"]),
      ("CBD distances (8)", ["Cebu Business Park", "Mandaue CBD", "Mactan CBD", "SRP", "Talisay Tabunok", "Consolacion", "Naga City", "Airport"]),
      ("Accessibility &amp; benchmark", ["mcrai_composite", "bir_zonal_rr_median", "spatial_lag_price"]),
      ("City indicators (5)", ["Consolacion", "Lapu-Lapu City", "Mandaue City", "Minglanilla", "Talisay City"]),
    ]) + "<div class='tnote'>Reference city = Cebu City (all city indicators zero). Beds/baths kept with imputation flags.</div>")
add("Features used &mdash; Houses (24)",
    feat_cols([
      ("Structural", ["area_sqm", "bedrooms", "bathrooms", "bedrooms_imputed", "bathrooms_imputed"]),
      ("CBD distances (8)", ["Cebu Business Park", "Mandaue CBD", "Mactan CBD", "SRP", "Talisay Tabunok", "Consolacion", "Naga City", "Airport"]),
      ("Accessibility &amp; benchmark", ["mcrai_composite", "bir_zonal_rr_median", "spatial_lag_price"]),
      ("City indicators (5)", ["Consolacion", "Lapu-Lapu City", "Mandaue City", "Minglanilla", "Talisay City"]),
      ("Property-type (3)", ["House and Lot", "Single Detached", "Townhouse"]),
    ]) + "<div class='tnote'>Houses span sub-types, so property-type indicators are retained. Reference city = Cebu City.</div>")
add("Features used &mdash; Vacant Lot (22)",
    feat_cols([
      ("Structural", ["area_sqm"]),
      ("CBD distances (8)", ["Cebu Business Park", "Mandaue CBD", "Mactan CBD", "SRP", "Talisay Tabunok", "Consolacion", "Naga City", "Airport"]),
      ("MCRAI individual (6)", ["education", "grocery", "health", "hospitals", "recreation", "tourism"]),
      ("Benchmark", ["bir_zonal_rr_median", "spatial_lag_price"]),
      ("City indicators (5)", ["Consolacion", "Lapu-Lapu City", "Mandaue City", "Minglanilla", "Talisay City"]),
    ]) + "<div class='tnote'>Lots have no beds/baths and use individual MCRAI categories (not the composite), since bare land responds to specific nearby access.</div>")
add("The model lineup",
    two_col(
      bullets(["<b>OLS hedonic</b> &mdash; interpretable baseline (HC3 robust errors) <span class='c'>(Rosen, 1974)</span>.",
        "<b>Random Forest</b> &mdash; non-linear, robust on small samples <span class='c'>(Breiman, 2001)</span>.",
        "<b>XGBoost</b> &mdash; gradient boosting on tabular data <span class='c'>(Chen &amp; Guestrin, 2016)</span>."]),
      bullets(["<b>SHAP</b> explains every prediction, feature by feature <span class='c'>(Lundberg &amp; Lee, 2017)</span>.",
        "OLS doubles as the diagnostic that screens MCRAI category signs.",
        "All three fit per stratum on the log price-per-sqm target."])))
add("Hyperparameters and tuning",
    lead("Each Random Forest was tuned per stratum, with the winner chosen by grouped-CV median error (MdAPE).") +
    table(["Stratum", "Trees", "Max features", "Min leaf", "Max depth"],
      [["Condominium", "300", "0.7", "1", "none"],
       ["Houses", "300", "1.0", "2", "none"],
       ["Vacant Lot", "300", "1.0", "1", "none"]],
      note="Selection basis: lowest GroupKFold MdAPE among the random-forest grid (random_state = 42)."))

# ----------------------------------------------------------- CH7
sec("7 · Evaluation")
add(divider_num="07", title="Evaluation", divider_sub="Accuracy, model comparison, ablation")
add("Headline accuracy",
    table(["Property type", "MdAPE (typical error)", "PE20 (within 20%)"],
      [["Condominium", "19.3%", "51%"],
       ["Houses", "22.7%", "44%"],
       ["Vacant Lot", "38.4%", "26%"]],
      note="Deployed Random Forest, leak-free GroupKFold. Supporting diagnostics: MAPE, COD, PRD. The study does not claim IAAO assessment-grade compliance.") +
    takeaway("Condominiums and houses estimate well; vacant lots remain the weakest stratum."))
add("Reading the metrics",
    bullets(["<b>MdAPE</b> &mdash; the median absolute percentage error; half of estimates fall within this band. Robust to a few extreme listings.",
       "<b>PE20</b> &mdash; the share of estimates within 20% of the listing; the practical hit-rate.",
       "<b>MAPE, COD, PRD</b> &mdash; supporting diagnostics, reported for comparability.",
       "Peer benchmark: comparable small-sample studies report MAPE near 48&ndash;53% <span class='c'>(Nyanda, 2024)</span> &mdash; the present errors are competitive."]))
add("Which model performed best? (RQ2)",
    fig_analysis(DECK+"model_comparison.png",
      ["Under identical leak-free folds, <b>both tree models beat the OLS baseline</b> in every stratum.",
       "Random Forest and XGBoost are close; RF edges it on the deployed grouped-CV (19.3 vs 19.8 / 22.7 vs 23.6 / 38.4 vs 40.2).",
       "Because the tree models are so close, the honest reading is &ldquo;RF best-or-tied.&rdquo;",
       "<b>Random Forest was deployed</b> &mdash; robust on small samples, and simpler to maintain."]))
add("Do geospatial features earn their place? (RQ3)",
    fig_analysis(DECK+"ablation_tiers.png",
      ["A three-tier ablation under identical folds: Structural &rarr; + Administrative &rarr; + Geospatial.",
       "Geospatial features improve <b>every</b> stratum vs structural-only: condo +5.7, houses +4.2, lot +13.0 points.",
       "On top of administrative location (city + BIR zonal): condo +3.7, lot +3.8, but houses &asymp; &minus;0.7.",
       "<b>They add the most where benchmarks are weakest</b> &mdash; vertical condos and bare land."]))

# ----------------------------------------------------------- CH8
sec("8 · Results & Discussion")
add(divider_num="08", title="Results and Discussion", divider_sub="Drivers and spatial structure")
add("Three findings stand out",
    bullets(["<b>Location dominates</b> value formation in every stratum &mdash; the geospatial block carries most of the SHAP attribution.",
       "<b>Drivers differ by property type</b> &mdash; which is exactly why the three strata are modeled separately.",
       "<b>MCRAI is selective</b> &mdash; education, grocery, and recreation carry positive weight; security, tourism, and retail behave as diagnostic categories, not premiums."]))
add("Drivers &mdash; condominiums",
    fig_analysis(EDA+"10_stratified_models/shap_condo_rf_bar.png",
      ["<b>Neighborhood price level (spatial lag) leads</b> &mdash; condos track their immediate block.",
       "Locational weight then spreads across several nodes: Consolacion, the airport, Mactan CBD, and CBP.",
       "The signature of a market responding to <b>several active centers</b> at once."]))
add("Drivers &mdash; houses",
    fig_analysis(EDA+"10_stratified_models/shap_houses_rf_bar.png",
      ["<b>Distance to Cebu Business Park is the single strongest driver.</b>",
       "Classic bid-rent: detached-house value falls with distance from the principal center.",
       "Amenities enter only as the bundled MCRAI composite."]))
add("Drivers &mdash; vacant lots",
    fig_analysis(EDA+"10_stratified_models/shap_lot_rf_bar.png",
      ["Distance to CBP leads &mdash; the <b>steepest bid-rent gradient</b> of the three strata.",
       "Individual amenity categories are the second-largest driver: bare land responds to specific nearby access.",
       "Still the weakest stratum &mdash; unrecorded parcel attributes (frontage, zoning, slope, titling) cap accuracy."],
      "A data ceiling, reported transparently &mdash; not a modeling failure."))
add("A polycentric price surface",
    lead("The SHAP results are the clearest evidence that the model learned a polycentric, not monocentric, structure.") +
    bullets(["CBP still anchors land and detached housing &mdash; the historic core matters most there.",
       "But it does not stand alone: condominium weight spreads across the Mactan/airport corridor and the northern Mandaue&ndash;Consolacion nodes.",
       "The reading is a <b>corridor of linked centers</b>, consistent with the JICA roadmap and polycentric theory <span class='c'>(Giuliano &amp; Small, 1991; McMillen, 2003; JICA, 2015)</span>."]))
add("The Mactan submarket, and spatial sorting",
    two_col(
      "<div class='subh'>Mactan</div>" + bullets([
        "The Mactan signal comes through the <b>condominium</b> stratum, via airport and Mactan-CBD distance.",
        "Better read as a <b>submarket bundle</b> (airport access, bridge connectivity, tourism-adjacent demand) than a raw island premium."]),
      "<div class='subh'>MCRAI negative signs</div>" + bullets([
        "Negative coefficients on security, tourism, and retail density are <b>not</b> proof of harm.",
        "They reflect <b>spatial sorting</b> &mdash; these uses cluster where congestion or commercial intensity deters some buyers <span class='c'>(Tiebout, 1956; Bayer &amp; McMillan, 2012; Yang et al., 2016)</span>."])))
add("The valuation gap (RQ4)",
    fig_analysis(DECK+"valuation_gap_lots.png",
      ["On the clean land-to-land comparison, vacant-lot market price runs <b>~3&times; the BIR benchmark overall</b>.",
       "From <b>~2.2&times; in Cebu City to ~4.8&times; in Mandaue</b>; listings exceed the benchmark in nearly every LGU.",
       "The gap is <b>large, positive, and systematic</b> &mdash; BIR zonal values sit well below the open market.",
       "Read it as a <b>research signal that benchmarks are stale</b> &mdash; not a correction factor to apply."]))
add("Is the model good enough?",
    lead("A measured answer, consistent with the manuscript.") +
    bullets(["As a <b>triangulation reference</b>, yes &mdash; but held-out error stays substantial even in the best strata.",
       "Strongest for condominiums and houses; only indicative for vacant lots and thin LGU&times;type cells.",
       "It complements professional appraisal judgment; it does not replace it."]))

# ----------------------------------------------------------- THE TOOL
sec("The Decision-Support Tool")
add(divider_num="&#9656;", title="The Decision-Support Tool", divider_sub="The applied deliverable")
add("Market Map", fig_full(DECK+"webapp_market_map.png",
    "Open-market listings with filters and market-intelligence summaries. The backend runs the exact deployed models."))
add("Price Surface", fig_full(DECK+"webapp_price_surface.png",
    "The predicted price-per-square-meter surface, aggregated by barangay."))
add("Property Predictor", fig_full(DECK+"webapp_predictor.png",
    "A property-level prediction with its SHAP contribution breakdown &mdash; the tool always shows its reasoning."))

# ----------------------------------------------------------- CH9
sec("9 · Conclusions")
add(divider_num="09", title="Conclusions", divider_sub="Answers, contributions, limits")
add("Answers to the research questions",
    bullets(["<b>RQ1</b> &mdash; Location dominates; drivers differ by type (spatial lag for condos; CBP distance for houses and lots; amenities for bare land).",
       "<b>RQ2</b> &mdash; Tree models beat OLS everywhere; Random Forest best-or-tied with XGBoost, deployed for robustness and simplicity.",
       "<b>RQ3</b> &mdash; Geospatial features materially help, most where administrative benchmarks are weakest.",
       "<b>RQ4</b> &mdash; The BIR gap is large, positive, and systematic (~3&times; on the clean lot comparison)."]))
add("Contributions",
    two_col(
      "<div class='subh'>Methodological</div>" + bullets([
        "Per-type modeling with evidence-based feature selection.",
        "A polycentric distance set, not a single-CBD measure.",
        "A two-stage MCRAI (OLS signs screen categories; positive-only composite).",
        "All headline results under leak-free grouped CV."]),
      "<div class='subh'>Practical</div>" + bullets([
        "A reproducible, explainable web prototype.",
        "TypeScript + Leaflet front end over a Python service running the deployed models.",
        "A market-facing price surface with the valuation-gap diagnostic."])))
add("Limitations",
    bullets(["<b>Asking-price ceiling</b> &mdash; trained on listings, not verified deed-of-sale transactions.",
       "<b>Cross-sectional snapshot</b> &mdash; late 2025; no cyclical or temporal modeling.",
       "<b>Vacant-lot data ceiling</b> &mdash; parcel attributes that drive land value are not recorded in listings.",
       "<b>Thin cells</b> &mdash; some LGU&times;type combinations are too sparse for reliable single-cell estimates."]))

# ----------------------------------------------------------- CH10
sec("10 · Recommendations")
add(divider_num="10", title="Recommendations", divider_sub="Practice, policy, future work")
add("For practice and policy",
    two_col(
      "<div class='subh'>Practice</div>" + bullets([
        "Read the surface as a triangulation tool, alongside zonal values and comparables &mdash; not a final appraisal.",
        "Weight polycentric distance and property type ahead of the amenity composite.",
        "Treat the valuation gap as a research signal; validate against transactions before any operational use."]),
      "<div class='subh'>Policy</div>" + bullets([
        "Keep recognizing secondary and corridor subcenters (Mactan, Consolacion, Naga), not just CBP.",
        "Use MCRAI as an adaptable template, not a finished index."])))
add("For future research",
    bullets(["Put MCRAI on an empirical footing &mdash; estimate the decay rate, radii, and weights from data rather than fixing them.",
       "Test spatial heterogeneity directly with Geographically Weighted Regression (GWR / MGWR).",
       "Enrich inputs &mdash; parcel attributes (frontage, corner-lot), a time dimension, and macro indicators <span class='c'>(Udomsap &amp; Abid, 2020)</span>.",
       "Triangulate against complementary reference prices instead of a single market-facing target."]))
add("Closing",
    lead("This thesis should be read as a demonstrated, reproducible workflow more than a finished product.") +
    bullets(["A custom MCRAI design, a polycentric distance set, and a Random Forest + SHAP pipeline that can be rebuilt, checked, and adapted for other Philippine secondary cities.",
       "What it finishes is a <b>defensible template for local valuation analytics</b> &mdash; a clearer starting point for the family deciding what a home is worth, not the last word."]))

# ----------------------------------------------------------- REFS + THANKS
sec("References")
REFS = [
 "Agosto, A. (2020). Determinants of Land Values in Cebu City, Philippines.",
 "Bangko Sentral ng Pilipinas. (2025). Residential Real Estate Price Index (RREPI): Q2 2025 Report.",
 "Bayer, P., &amp; McMillan, R. (2012). Tiebout sorting and neighborhood stratification.",
 "Boeing, G. (2017). OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks.",
 "Breiman, L. (2001). Random forests.",
 "Bureau of Internal Revenue. (n.d.). Zonal Values Resources and Schedules.",
 "Chen, T., &amp; Guestrin, C. (2016). XGBoost: A scalable tree boosting system. ACM SIGKDD.",
 "Dr&ouml;es, M. I., Hoesli, M., &amp; Bourassa, S. C. (2019). Heterogeneous households and market segmentation in a hedonic framework. ERES.",
 "Giuliano, G., &amp; Small, K. A. (1991). Subcenters in the Los Angeles region.",
 "Grinsztajn, L., Oyallon, E., &amp; Varoquaux, G. (2022). Why do tree-based models still outperform deep learning on typical tabular data? NeurIPS 35.",
 "Hansen, W. G. (1959). How accessibility shapes land use.",
 "International Valuation Standards Council. (2025). International Valuation Standards (IVS) 2025.",
 "Japan International Cooperation Agency &amp; MCDCB. (2015). The Roadmap Study for Sustainable Urban Development in Metro Cebu.",
 "Lundberg, S. M., &amp; Lee, S.-I. (2017). A unified approach to interpreting model predictions. NeurIPS 30.",
 "McMillen, D. P. (2003). The return of centralization to Chicago.",
 "Otsuka, K., Manasan, R. G., &amp; Piza, S. (2023). Local government unit income and real property tax collection in the Philippines. PIDS.",
 "Philippine Statistics Authority &ndash; Central Visayas. (2025). Cebu's economy grows by 7.3 percent in 2024.",
 "Ramolete, G. I. L., Bramaskara, B., Reyes, D. A., &amp; Heinrich, A. (2023). Utilization of machine learning and government-based indicators for property value prediction in the Philippines. The Philippine Statistician.",
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
           '<title>Defense Deck — Substantive</title><style>', CSS, '</style></head><body>',
           f'<div class="topbar"><span>Defense Deck · substantive angle · {n} slides</span>'
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
                       f'<div class="body">{s["body"]}</div>'
                       '<div class="foot"><span>Predicting Open-Market Residential Property Values in Metro Cebu</span>'
                       '<span>C. D. Estreba</span></div></div>')
        out.append('</div>')
    out.append('</div></body></html>')
    return "".join(out)

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "defense_deck_v2.html"), "w") as f:
    f.write(render())
print(f"wrote defense_deck_v2.html  ({len(SLIDES)} slides)")
