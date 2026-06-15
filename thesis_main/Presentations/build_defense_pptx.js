// Thesis Defense — Metro Cebu Property Valuation (May 9, 2026)
// 30 slides | 30 min presentation | NAVY + AMBER design system
//
// Run with:  NODE_PATH=$(npm root -g) node build_defense_pptx.js

const PptxGenJS = require("pptxgenjs");
const path = require("path");

const pres = new PptxGenJS();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pres.title = "Defense - Metro Cebu Property Valuation";
pres.author = "Nico Estreba";
pres.subject = "UA&P Data Science Thesis Defense";

// ============================================================
// DESIGN SYSTEM
// ============================================================
const C = {
  NAVY: "1B2A4A",
  NAVY_DARK: "121C33",
  AMBER: "D4A843",
  AMBER_SOFT: "F5E6B8",
  SLATE: "EEF1F6",
  SLATE_DARK: "C9D1DD",
  INK: "2C3E50",
  MUTED: "7A8699",
  WHITE: "FFFFFF",
  RED_SOFT: "C0392B",
  GREEN_SOFT: "27AE60",
};

const FONT_HEAD = "Calibri";
const FONT_BODY = "Calibri";

const W = 13.33;
const H = 7.5;

// ============================================================
// SLIDE BUILDERS
// ============================================================

// Standard content slide: white bg, navy header (no underline), content area
function contentSlide(titleText, opts = {}) {
  const slide = pres.addSlide();
  slide.background = { color: C.WHITE };
  // Section indicator in top-right corner
  if (opts.sectionLabel) {
    slide.addShape("rect", { x: W - 2.6, y: 0.32, w: 2.3, h: 0.32, fill: { color: C.SLATE }, line: { color: C.SLATE } });
    slide.addText(opts.sectionLabel, {
      x: W - 2.6, y: 0.32, w: 2.3, h: 0.32,
      fontSize: 10, fontFace: FONT_HEAD, color: C.NAVY, bold: true,
      align: "center", valign: "middle", charSpacing: 2,
    });
  }
  // Title — bold navy, NO underline
  slide.addText(titleText, {
    x: 0.6, y: 0.45, w: W - 1.2, h: 0.85,
    fontSize: 30, bold: true, fontFace: FONT_HEAD, color: C.NAVY,
    align: "left", valign: "middle",
  });
  // Amber accent dot (visual motif, top-left)
  slide.addShape("ellipse", {
    x: 0.6, y: 0.40, w: 0.18, h: 0.18,
    fill: { color: C.AMBER }, line: { color: C.AMBER },
  });
  // Re-position title to leave space for the dot
  return slide;
}

// Section divider: navy left third, slate right
function sectionDivider(num, title, kicker) {
  const s = pres.addSlide();
  s.background = { color: C.SLATE };
  s.addShape("rect", { x: 0, y: 0, w: W * 0.34, h: H, fill: { color: C.NAVY }, line: { color: C.NAVY } });
  s.addText(num, {
    x: 0.6, y: H - 1.4, w: 3.0, h: 0.7,
    fontSize: 110, bold: true, fontFace: FONT_HEAD, color: C.AMBER,
    align: "left", valign: "bottom",
  });
  s.addText(kicker, {
    x: W * 0.34 + 0.8, y: 2.6, w: W * 0.62, h: 0.4,
    fontSize: 13, bold: true, fontFace: FONT_HEAD, color: C.AMBER,
    align: "left", charSpacing: 3,
  });
  s.addText(title, {
    x: W * 0.34 + 0.8, y: 3.0, w: W * 0.62, h: 1.8,
    fontSize: 44, bold: true, fontFace: FONT_HEAD, color: C.NAVY,
    align: "left", valign: "top",
  });
  return s;
}

// Big stat callout box (used inside slides for key numbers)
function statCallout(slide, x, y, w, h, value, label) {
  slide.addShape("rect", { x, y, w, h, fill: { color: C.NAVY }, line: { color: C.NAVY } });
  slide.addText(value, {
    x, y: y + 0.1, w, h: h * 0.65,
    fontSize: 60, bold: true, fontFace: FONT_HEAD, color: C.AMBER,
    align: "center", valign: "middle",
  });
  slide.addText(label, {
    x: x + 0.2, y: y + h * 0.65, w: w - 0.4, h: h * 0.3,
    fontSize: 12, fontFace: FONT_HEAD, color: C.WHITE,
    align: "center", valign: "top",
  });
}

// Card (used in stakeholder grids and feature blocks)
function card(slide, x, y, w, h, header, body, opts = {}) {
  const fillColor = opts.dark ? C.NAVY : C.WHITE;
  const borderColor = opts.dark ? C.NAVY : C.SLATE_DARK;
  const headerColor = opts.dark ? C.AMBER : C.NAVY;
  const bodyColor = opts.dark ? C.WHITE : C.INK;
  slide.addShape("roundRect", {
    x, y, w, h,
    fill: { color: fillColor }, line: { color: borderColor, width: 1 },
    rectRadius: 0.08,
  });
  // Optional accent strip
  if (opts.accentStrip) {
    slide.addShape("rect", {
      x, y, w: 0.12, h,
      fill: { color: C.AMBER }, line: { color: C.AMBER },
    });
  }
  if (opts.icon) {
    slide.addShape("ellipse", {
      x: x + 0.3, y: y + 0.3, w: 0.5, h: 0.5,
      fill: { color: C.AMBER }, line: { color: C.AMBER },
    });
    slide.addText(opts.icon, {
      x: x + 0.3, y: y + 0.3, w: 0.5, h: 0.5,
      fontSize: 16, bold: true, fontFace: FONT_HEAD, color: C.NAVY,
      align: "center", valign: "middle",
    });
  }
  slide.addText(header, {
    x: x + (opts.icon ? 0.95 : 0.3), y: y + 0.3, w: w - (opts.icon ? 1.2 : 0.6), h: 0.5,
    fontSize: 16, bold: true, fontFace: FONT_HEAD, color: headerColor,
    align: "left", valign: "middle",
  });
  slide.addText(body, {
    x: x + 0.3, y: y + 0.95, w: w - 0.6, h: h - 1.1,
    fontSize: 13, fontFace: FONT_BODY, color: bodyColor,
    align: "left", valign: "top", paraSpaceAfter: 4,
  });
}

// Pipeline step box (for flow diagrams)
function pipelineStep(slide, x, y, w, h, num, title, desc) {
  slide.addShape("roundRect", {
    x, y, w, h,
    fill: { color: C.WHITE }, line: { color: C.NAVY, width: 1.5 },
    rectRadius: 0.08,
  });
  // Numbered amber circle
  slide.addShape("ellipse", {
    x: x + w / 2 - 0.3, y: y - 0.3, w: 0.6, h: 0.6,
    fill: { color: C.AMBER }, line: { color: C.AMBER },
  });
  slide.addText(num, {
    x: x + w / 2 - 0.3, y: y - 0.3, w: 0.6, h: 0.6,
    fontSize: 18, bold: true, fontFace: FONT_HEAD, color: C.NAVY,
    align: "center", valign: "middle",
  });
  slide.addText(title, {
    x: x + 0.15, y: y + 0.5, w: w - 0.3, h: 0.5,
    fontSize: 15, bold: true, fontFace: FONT_HEAD, color: C.NAVY,
    align: "center", valign: "middle",
  });
  if (desc) {
    slide.addText(desc, {
      x: x + 0.15, y: y + 1.0, w: w - 0.3, h: h - 1.1,
      fontSize: 11, fontFace: FONT_BODY, color: C.MUTED,
      align: "center", valign: "top",
    });
  }
}

// Arrow between pipeline boxes (unused — inline arrows used instead)


function bullets(items, opts = {}) {
  return items.map((t) => ({
    text: t,
    options: { bullet: { code: "25CF" }, paraSpaceAfter: opts.spacing || 8, color: opts.color || C.INK, fontSize: opts.fontSize || 16 },
  }));
}

// ============================================================
// SLIDE 1 — Title (Full-bleed navy)
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.NAVY };
  // Amber accent bar
  s.addShape("rect", {
    x: 0.6, y: 1.8, w: 0.8, h: 0.06,
    fill: { color: C.AMBER }, line: { color: C.AMBER },
  });
  s.addText("UA&P  ·  DATA SCIENCE THESIS  ·  MAY 2026", {
    x: 0.6, y: 1.0, w: 12.0, h: 0.5,
    fontSize: 13, bold: true, fontFace: FONT_HEAD, color: C.AMBER,
    align: "left", charSpacing: 4,
  });
  s.addText("Predicting Open-Market Residential\nProperty Prices in Metro Cebu", {
    x: 0.6, y: 2.2, w: 12.0, h: 2.4,
    fontSize: 46, bold: true, fontFace: FONT_HEAD, color: C.WHITE,
    align: "left", valign: "top",
  });
  s.addText("Using Machine Learning and Geospatial Features", {
    x: 0.6, y: 4.8, w: 12.0, h: 0.7,
    fontSize: 22, fontFace: FONT_HEAD, color: C.AMBER_SOFT,
    align: "left", italic: true,
  });
  s.addShape("rect", {
    x: 0.6, y: 6.5, w: 12.0, h: 0.02,
    fill: { color: C.AMBER }, line: { color: C.AMBER },
  });
  s.addText("Nico Estreba", {
    x: 0.6, y: 6.65, w: 6.0, h: 0.4,
    fontSize: 14, bold: true, fontFace: FONT_HEAD, color: C.WHITE,
    align: "left",
  });
  s.addText("BSDS Capstone  ·  Defense Date: May 9, 2026", {
    x: 6.6, y: 6.65, w: 6.0, h: 0.4,
    fontSize: 12, fontFace: FONT_HEAD, color: C.SLATE_DARK,
    align: "right",
  });
  s.addNotes("Title slide — establish, breathe, then move on.");
}

// ============================================================
// SLIDE 2 — Agenda (6-step flow)
// ============================================================
{
  const s = contentSlide("Agenda", { sectionLabel: "ROADMAP" });
  s.addNotes(
    "I'll spend the first ten minutes on the problem and approach, fifteen on the data and modeling, and the last five on results and the deployed tool.",
  );
  const steps = [
    { num: "1", t: "The Problem", d: "Why valuation in Metro Cebu is fragmented" },
    { num: "2", t: "The Approach", d: "IVS-grounded scope, geospatial features, ML" },
    { num: "3", t: "The Data", d: "Multi-source collection, open-market training" },
    { num: "4", t: "The Models", d: "OLS → RF → XGBoost → SHAP" },
    { num: "5", t: "The Results", d: "Performance, importance, valuation gap" },
    { num: "6", t: "The Tool", d: "Streamlit web app + use cases" },
  ];
  // 3 across × 2 down grid
  const cardW = 3.9, cardH = 2.5, gapX = 0.25, gapY = 0.35;
  const startX = (W - (cardW * 3 + gapX * 2)) / 2;
  const startY = 1.7;
  steps.forEach((step, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = startX + col * (cardW + gapX);
    const y = startY + row * (cardH + gapY);
    card(s, x, y, cardW, cardH, step.t, step.d, { icon: step.num });
  });
}

// ============================================================
// SLIDE 3 — Philippine Real Estate Market (with stat callout)
// ============================================================
{
  const s = contentSlide("The Philippine Real Estate Market", { sectionLabel: "THE PROBLEM" });
  s.addNotes(
    "The Philippine residential property market is one of the most active in Southeast Asia, but the activity is uneven. Metro Cebu stands out — recording 11.5% residential price growth in 2025, the highest of any metropolitan area outside Metro Manila. This is not speculative. It is driven by real urbanization: rising incomes, migration into the urban core, and a wave of infrastructure investment — the Cebu Bus Rapid Transit, the Metro Cebu Expressway, continued buildout at South Road Properties — that is actively redrawing which barangays are accessible and which are not.",
  );
  // Stat callout left
  statCallout(s, 0.6, 1.7, 4.5, 3.0, "11.5%", "METRO CEBU 2025 PRICE GROWTH\nHighest outside NCR (BSP, 2025)");
  // Body right
  s.addText(
    [
      { text: "Metro Cebu stands out in an active national market.", options: { bold: true, fontSize: 18, color: C.NAVY, paraSpaceAfter: 14 } },
      { text: "Active infrastructure pipeline:", options: { bold: true, fontSize: 14, color: C.NAVY, paraSpaceAfter: 6 } },
      { text: "Cebu Bus Rapid Transit (CBRT)", options: { bullet: { code: "25CF" }, fontSize: 14, color: C.INK, paraSpaceAfter: 4 } },
      { text: "Metro Cebu Expressway", options: { bullet: { code: "25CF" }, fontSize: 14, color: C.INK, paraSpaceAfter: 4 } },
      { text: "South Road Properties buildout", options: { bullet: { code: "25CF" }, fontSize: 14, color: C.INK, paraSpaceAfter: 14 } },
      { text: "Six core LGUs:", options: { bold: true, fontSize: 14, color: C.NAVY, paraSpaceAfter: 6 } },
      { text: "Cebu City · Mandaue · Lapu-Lapu · Talisay · Minglanilla · Consolacion", options: { fontSize: 14, color: C.INK, italic: true } },
    ],
    { x: 5.5, y: 1.8, w: 7.3, h: 5.0, fontFace: FONT_BODY, valign: "top" },
  );
}

// ============================================================
// SLIDE 4 — Three Imperfect Valuation Systems
// ============================================================
{
  const s = contentSlide("Three Imperfect Valuation Systems", { sectionLabel: "THE PROBLEM" });
  s.addNotes(
    "Despite this activity, Metro Cebu does not have a reliable, consistent way to value residential property. Three systems exist, and each has a different weakness.\n\nBIR zonal values are administratively set and chronically outdated — only 60% of LGUs have updated theirs nationally (Otsuka et al., 2023). Bank appraisals are designed for lending risk, not market value. Online listings reflect seller strategy: asking prices, not transaction prices, mixed without adjustment.\n\nNone of these, on their own, gives buyers, sellers, banks, or LGUs a defensible estimate of what a property is worth on the open market.",
  );
  const cols = [
    {
      title: "BIR Zonal Values",
      tag: "ADMINISTRATIVE",
      rows: [
        "Administratively set",
        "Only 60% of LGUs updated nationally",
        "Lags infrastructure changes",
      ],
    },
    {
      title: "Bank Appraisals",
      tag: "LENDING-RISK",
      rows: [
        "Designed for lending risk",
        "Conservative by design",
        "Underestimates open market",
      ],
    },
    {
      title: "Online Listings",
      tag: "SELLER-STRATEGY",
      rows: [
        "Asking prices, not transactions",
        "Unstandardized property mix",
        "Seller-strategy noise",
      ],
    },
  ];
  const cardW = 3.9, cardH = 4.4, gapX = 0.2;
  const startX = (W - (cardW * 3 + gapX * 2)) / 2;
  const startY = 1.7;
  cols.forEach((col, i) => {
    const x = startX + i * (cardW + gapX);
    const y = startY;
    // Header band
    s.addShape("rect", { x, y, w: cardW, h: 1.0, fill: { color: C.NAVY }, line: { color: C.NAVY } });
    s.addText(col.tag, {
      x, y: y + 0.1, w: cardW, h: 0.3,
      fontSize: 10, bold: true, fontFace: FONT_HEAD, color: C.AMBER,
      align: "center", charSpacing: 3,
    });
    s.addText(col.title, {
      x, y: y + 0.4, w: cardW, h: 0.55,
      fontSize: 18, bold: true, fontFace: FONT_HEAD, color: C.WHITE,
      align: "center", valign: "middle",
    });
    // Body
    s.addShape("rect", {
      x, y: y + 1.0, w: cardW, h: cardH - 1.0,
      fill: { color: C.WHITE }, line: { color: C.SLATE_DARK, width: 1 },
    });
    s.addText(
      col.rows.map((t) => ({
        text: t,
        options: { bullet: { code: "25CF" }, fontSize: 14, color: C.INK, paraSpaceAfter: 12 },
      })),
      { x: x + 0.3, y: y + 1.2, w: cardW - 0.6, h: cardH - 1.4, fontFace: FONT_BODY, valign: "top" },
    );
  });
  // Footer line
  s.addText("Each is broken differently. None gives a defensible open-market estimate.", {
    x: 0.6, y: 6.4, w: W - 1.2, h: 0.5,
    fontSize: 14, italic: true, fontFace: FONT_BODY, color: C.MUTED,
    align: "center",
  });
}

// ============================================================
// SLIDE 5 — Who Pays the Cost? (2x2 stakeholder grid)
// ============================================================
{
  const s = contentSlide("Who Pays the Cost?", { sectionLabel: "THE PROBLEM" });
  s.addNotes(
    "The cost of this gap falls on everyone in a transaction. Buyers lack reference points and may overpay. Sellers may underprice or hold at unrealistic asking. Banks face collateral risk when appraisal and market diverge. And LGUs leave revenue on the table — when zonal values lag market prices by 30 to 50 percent, real property tax assessments are systematically undervalued.\n\nThe problem is not a lack of data. It is a lack of integration.",
  );
  const stakeholders = [
    { icon: "B", h: "Buyers", b: "No reliable reference for negotiation. Risk of overpaying or walking from fair-value properties." },
    { icon: "S", h: "Sellers", b: "No market anchor for pricing. Hold at unrealistic asking, or underprice in confusion." },
    { icon: "$", h: "Banks", b: "Collateral risk when appraisal and market diverge significantly." },
    { icon: "L", h: "LGUs", b: "Undervalued tax base when zonal rates lag 30–50% behind market prices." },
  ];
  const cardW = 5.8, cardH = 2.3, gapX = 0.4, gapY = 0.4;
  const startX = (W - (cardW * 2 + gapX)) / 2;
  const startY = 1.7;
  stakeholders.forEach((sh, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = startX + col * (cardW + gapX);
    const y = startY + row * (cardH + gapY);
    card(s, x, y, cardW, cardH, sh.h, sh.b, { icon: sh.icon, accentStrip: true });
  });
  s.addText("The problem is not a lack of data. It is a lack of integration.", {
    x: 0.6, y: 6.6, w: W - 1.2, h: 0.4,
    fontSize: 15, italic: true, bold: true, fontFace: FONT_BODY, color: C.NAVY,
    align: "center",
  });
}

// ============================================================
// SLIDE 6 — Why Metro Cebu, and Why Now
// ============================================================
{
  const s = contentSlide("Why Metro Cebu, and Why Now", { sectionLabel: "THE PROBLEM" });
  s.addNotes(
    "This study focuses on Metro Cebu — specifically the six core LGUs that form its urban conurbation — for three converging reasons.\n\nFirst, prices are moving faster than any benchmark can track. Second, infrastructure is actively restructuring accessibility — the Cebu Bus Rapid Transit and expressway systems are not hypothetical, they are reshaping which barangays sit fifteen minutes from the CBD and which sit forty-five. Third, the data now exists to study this at scale: Lamudi listings, OpenStreetMap road networks, and geocoding APIs make a property-level dataset feasible without sealed deed records.\n\nI should also briefly acknowledge that this research is informed by firsthand exposure to Metro Cebu's residential market through a family business — that context sharpened my awareness of where the valuation problem is felt most. The methodology, however, is designed to be reproducible and objective.",
  );
  // Three reason cards
  const reasons = [
    { num: "I", h: "Prices outpace benchmarks", b: "11.5% growth vs. stagnant zonal values—the gap widens with every transaction." },
    { num: "II", h: "Infrastructure rewriting access", b: "CBRT, Metro Cebu Expressway, SRP are reshaping which barangays sit 15 minutes from the CBD." },
    { num: "III", h: "Property-level data feasible", b: "Lamudi listings, OpenStreetMap routing, and geocoding APIs replace sealed deed records." },
  ];
  const cardW = 4.0, cardH = 3.5, gapX = 0.25;
  const startX = (W - (cardW * 3 + gapX * 2)) / 2;
  reasons.forEach((r, i) => {
    const x = startX + i * (cardW + gapX);
    card(s, x, 1.7, cardW, cardH, r.h, r.b, { icon: r.num });
  });
  // Personal-note footnote
  s.addText(
    "Note: This research is also informed by firsthand exposure to Metro Cebu's residential market through a family business. The methodology is designed to be reproducible and objective.",
    {
      x: 0.6, y: 5.7, w: W - 1.2, h: 1.2,
      fontSize: 12, italic: true, fontFace: FONT_BODY, color: C.MUTED,
      align: "center", valign: "top",
    },
  );
}

// ============================================================
// SLIDE 7 — Research Gap → What We Built (3-step flow)
// ============================================================
{
  const s = contentSlide("Research Gap → What We Built", { sectionLabel: "THE APPROACH" });
  s.addNotes(
    "The research gap is concrete. There is no published, reproducible, property-level valuation model for Metro Cebu that integrates open-market listing data, geospatial accessibility, and machine learning explainability.\n\nThis thesis builds one. We trained a model on open-market listings — the only arm's-length signal available without sealed deed records — and engineered geospatial features grounded in urban-economics literature. We deployed the result as a transparent, explainable web tool. Not to replace appraisers. To give them, and everyone else in a transaction, a defensible reference point.",
  );
  const steps = [
    { t: "GAP", h: "What's Missing", d: "No published, reproducible, property-level valuation model for Metro Cebu integrating listing data + geospatial accessibility + ML explainability." },
    { t: "APPROACH", h: "What We Did", d: "Trained on open-market listings (IVS 2025 arm's-length). Engineered geospatial features from urban-economics literature." },
    { t: "DELIVERABLE", h: "What Practitioners Get", d: "Streamlit web app + QGIS spatial layer. Transparent, explainable, locally calibrated price estimates with SHAP." },
  ];
  const cardW = 3.9, cardH = 4.0, gapX = 0.4;
  const startX = (W - (cardW * 3 + gapX * 2)) / 2;
  const startY = 2.0;
  steps.forEach((st, i) => {
    const x = startX + i * (cardW + gapX);
    // Tag
    s.addShape("rect", { x: x + cardW / 2 - 1.0, y: startY - 0.3, w: 2.0, h: 0.36, fill: { color: C.AMBER }, line: { color: C.AMBER } });
    s.addText(st.t, {
      x: x + cardW / 2 - 1.0, y: startY - 0.3, w: 2.0, h: 0.36,
      fontSize: 10, bold: true, fontFace: FONT_HEAD, color: C.NAVY,
      align: "center", valign: "middle", charSpacing: 3,
    });
    s.addShape("roundRect", {
      x, y: startY, w: cardW, h: cardH,
      fill: { color: C.WHITE }, line: { color: C.NAVY, width: 1.5 },
      rectRadius: 0.08,
    });
    s.addText(st.h, {
      x: x + 0.3, y: startY + 0.5, w: cardW - 0.6, h: 0.6,
      fontSize: 20, bold: true, fontFace: FONT_HEAD, color: C.NAVY,
      align: "left", valign: "middle",
    });
    s.addText(st.d, {
      x: x + 0.3, y: startY + 1.3, w: cardW - 0.6, h: cardH - 1.5,
      fontSize: 13, fontFace: FONT_BODY, color: C.INK,
      align: "left", valign: "top",
    });
    // Arrow between cards
    if (i < steps.length - 1) {
      const ax = x + cardW + 0.05;
      const ay = startY + cardH / 2 - 0.15;
      s.addShape("rightTriangle", {
        x: ax + 0.13, y: ay - 0.05, w: 0.18, h: 0.32,
        fill: { color: C.AMBER }, line: { color: C.AMBER },
        flipH: false,
      });
      s.addShape("rect", { x: ax, y: ay + 0.08, w: 0.2, h: 0.08, fill: { color: C.AMBER }, line: { color: C.AMBER } });
    }
  });
}

// ============================================================
// SECTION DIVIDER 1 → Research Design
// ============================================================
sectionDivider("01", "Research Design", "PART ONE").addNotes("Section transition: from problem framing to research design.");

// ============================================================
// SLIDE 8 — Research Questions
// ============================================================
{
  const s = contentSlide("Research Questions", { sectionLabel: "RESEARCH DESIGN" });
  s.addNotes(
    "Four research questions. RQ1 on value drivers, RQ2 on model comparison, RQ3 on whether geospatial features earn their place, RQ4 on the size of the valuation gap.",
  );
  const rqs = [
    { n: "RQ 1", t: "What value drivers significantly influence residential prices in Metro Cebu?" },
    { n: "RQ 2", t: "Which model — OLS, Random Forest, or XGBoost — yields the lowest error?" },
    { n: "RQ 3", t: "Do geospatial features improve performance over structural-only models?" },
    { n: "RQ 4", t: "How large is the valuation gap between model predictions and BIR zonal values?" },
  ];
  rqs.forEach((rq, i) => {
    const y = 1.7 + i * 1.25;
    s.addShape("rect", { x: 0.6, y, w: 1.4, h: 0.9, fill: { color: C.NAVY }, line: { color: C.NAVY } });
    s.addText(rq.n, {
      x: 0.6, y, w: 1.4, h: 0.9,
      fontSize: 18, bold: true, fontFace: FONT_HEAD, color: C.AMBER,
      align: "center", valign: "middle", charSpacing: 1,
    });
    s.addShape("rect", { x: 2.0, y, w: W - 2.6, h: 0.9, fill: { color: C.SLATE }, line: { color: C.SLATE } });
    s.addText(rq.t, {
      x: 2.3, y, w: W - 3.0, h: 0.9,
      fontSize: 16, fontFace: FONT_BODY, color: C.INK,
      align: "left", valign: "middle",
    });
  });
}

// ============================================================
// SLIDE 9 — Conceptual Framework
// ============================================================
{
  const s = contentSlide("Conceptual Framework", { sectionLabel: "RESEARCH DESIGN" });
  s.addNotes(
    "Two-layer framework: predictive model produces price estimates; prescriptive layer uses the valuation gap to produce decision-support outputs. Anchored in IVS 2025 Market Value definition.",
  );
  // Two layered cards
  const layers = [
    { tag: "LAYER 1 · PREDICTIVE", h: "Price Estimation", d: "Tree-based ML model trained on open-market listings → estimates price per sqm at the parcel level.", color: C.NAVY },
    { tag: "LAYER 2 · PRESCRIPTIVE", h: "Decision Support", d: "Valuation gap (model − BIR zonal) drives recommendations for banks, LGUs, urban planners, and practitioners.", color: C.AMBER },
  ];
  layers.forEach((l, i) => {
    const y = 1.7 + i * 1.85;
    s.addShape("roundRect", {
      x: 0.6, y, w: 12.1, h: 1.6,
      fill: { color: i === 0 ? C.NAVY : C.WHITE },
      line: { color: i === 0 ? C.NAVY : C.AMBER, width: 2 },
      rectRadius: 0.1,
    });
    s.addText(l.tag, {
      x: 0.9, y: y + 0.2, w: 11.5, h: 0.3,
      fontSize: 11, bold: true, fontFace: FONT_HEAD,
      color: i === 0 ? C.AMBER : C.AMBER,
      charSpacing: 3,
    });
    s.addText(l.h, {
      x: 0.9, y: y + 0.5, w: 11.5, h: 0.5,
      fontSize: 22, bold: true, fontFace: FONT_HEAD,
      color: i === 0 ? C.WHITE : C.NAVY,
    });
    s.addText(l.d, {
      x: 0.9, y: y + 1.0, w: 11.5, h: 0.55,
      fontSize: 14, fontFace: FONT_BODY,
      color: i === 0 ? C.SLATE_DARK : C.INK,
    });
  });
  // IVS anchor footer
  s.addShape("rect", { x: 0.6, y: 5.6, w: 12.1, h: 1.4, fill: { color: C.SLATE }, line: { color: C.SLATE } });
  s.addText("ANCHOR", {
    x: 0.9, y: 5.7, w: 11.5, h: 0.3,
    fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 3,
  });
  s.addText(
    'IVS 2025 Market Value definition  ·  arm\'s-length transaction between willing buyer and willing seller  ·  Output: Streamlit web app + QGIS spatial layer for practitioner use.',
    {
      x: 0.9, y: 6.0, w: 11.5, h: 0.9,
      fontSize: 14, fontFace: FONT_BODY, color: C.NAVY, italic: true,
    },
  );
}

// ============================================================
// SLIDE 10 — Scope and Study Area
// ============================================================
{
  const s = contentSlide("Scope and Study Area", { sectionLabel: "RESEARCH DESIGN" });
  s.addNotes(
    "Six LGUs in the training scope. Eight CBD nodes anchor the geospatial features. Naga City is included as a CBD anchor only — outside our LGU training area, but it functions as an employment anchor and disamenity proxy. Lapu-Lapu City is split between mainland and Mactan Island via the is_mactan_island flag.",
  );
  // Map placeholder, left
  s.addShape("roundRect", {
    x: 0.6, y: 1.7, w: 6.5, h: 5.2,
    fill: { color: C.SLATE }, line: { color: C.SLATE_DARK, width: 1 },
    rectRadius: 0.08,
  });
  s.addText("[ DIAGRAM TO ADD ]", {
    x: 0.6, y: 2.0, w: 6.5, h: 0.4,
    fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 3,
    align: "center",
  });
  s.addText("Metro Cebu Study Area Map", {
    x: 0.6, y: 2.4, w: 6.5, h: 0.5,
    fontSize: 18, bold: true, fontFace: FONT_HEAD, color: C.NAVY,
    align: "center",
  });
  s.addText(
    "Source: thesis_main/Manuscript figure (Chapter 1)\n6 LGU boundaries + 8 CBD node markers\n• highlight Naga City as 'anchor only'\n• use color to distinguish Mactan Island",
    {
      x: 0.9, y: 3.1, w: 5.9, h: 3.5,
      fontSize: 12, italic: true, fontFace: FONT_BODY, color: C.MUTED,
      align: "center", valign: "top",
    },
  );
  // Body, right
  s.addText("6 LGUs (training scope)", {
    x: 7.4, y: 1.7, w: 5.4, h: 0.4,
    fontSize: 14, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 2,
  });
  s.addText("Cebu City  ·  Mandaue  ·  Lapu-Lapu  ·  Talisay  ·  Minglanilla  ·  Consolacion", {
    x: 7.4, y: 2.05, w: 5.4, h: 0.7,
    fontSize: 14, fontFace: FONT_BODY, color: C.INK, paraSpaceAfter: 6,
  });
  s.addText("8 CBD Nodes (geospatial features)", {
    x: 7.4, y: 2.85, w: 5.4, h: 0.4,
    fontSize: 14, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 2,
  });
  s.addText(
    "Cebu Business Park · Mandaue CBD · Mactan CBD · South Road Properties · Talisay Tabunok · Consolacion · Naga City (anchor only) · Mactan-Cebu International Airport",
    {
      x: 7.4, y: 3.2, w: 5.4, h: 1.6,
      fontSize: 13, fontFace: FONT_BODY, color: C.INK,
    },
  );
  s.addText(
    [
      { text: "Naga City: anchor only — excluded from training (n≈4 listings)", options: { bullet: { code: "25CF" }, fontSize: 12, color: C.MUTED, paraSpaceAfter: 4 } },
      { text: "Lapu-Lapu split: mainland vs. Mactan (is_mactan_island flag)", options: { bullet: { code: "25CF" }, fontSize: 12, color: C.MUTED, paraSpaceAfter: 4 } },
    ],
    { x: 7.4, y: 5.1, w: 5.4, h: 1.5, fontFace: FONT_BODY },
  );
}

// ============================================================
// SECTION DIVIDER 2 → Data
// ============================================================
sectionDivider("02", "The Data", "PART TWO");

// ============================================================
// SLIDE 11 — Data Collection: What Was Gathered
// ============================================================
{
  const s = contentSlide("Data Collection: What Was Gathered", { sectionLabel: "THE DATA" });
  s.addNotes(
    "We collected four data sources. Only one of them — open-market listings — was used to train the model. The other tiers were collected for context, validation, and future research.",
  );
  const sources = [
    { src: "Lamudi open-market listings", rows: "1,619", role: "Training data", isTraining: true },
    { src: "Bank ROPA (BDO, BPI, Metrobank, Landbank, BoC, China Bank)", rows: "320", role: "Context only — excluded from training", isTraining: false },
    { src: "Floor prices (BDO, Pag-IBIG distressed)", rows: "108", role: "Context only — excluded from training", isTraining: false },
    { src: "BIR zonal values (per barangay)", rows: "All rows", role: "Benchmark for valuation gap (not a feature)", isTraining: false },
  ];
  // Header bar
  const headerY = 1.7;
  s.addShape("rect", { x: 0.6, y: headerY, w: 12.1, h: 0.5, fill: { color: C.NAVY }, line: { color: C.NAVY } });
  s.addText("SOURCE", { x: 0.85, y: headerY, w: 5.5, h: 0.5, fontSize: 12, bold: true, fontFace: FONT_HEAD, color: C.AMBER, valign: "middle", charSpacing: 2 });
  s.addText("ROWS", { x: 6.4, y: headerY, w: 1.8, h: 0.5, fontSize: 12, bold: true, fontFace: FONT_HEAD, color: C.AMBER, valign: "middle", align: "center", charSpacing: 2 });
  s.addText("ROLE", { x: 8.3, y: headerY, w: 4.3, h: 0.5, fontSize: 12, bold: true, fontFace: FONT_HEAD, color: C.AMBER, valign: "middle", charSpacing: 2 });
  // Data rows
  sources.forEach((src, i) => {
    const y = headerY + 0.6 + i * 1.1;
    const fill = src.isTraining ? C.AMBER_SOFT : C.WHITE;
    const accent = src.isTraining ? C.AMBER : C.SLATE_DARK;
    s.addShape("rect", { x: 0.6, y, w: 12.1, h: 1.0, fill: { color: fill }, line: { color: accent } });
    if (src.isTraining) {
      s.addShape("rect", { x: 0.6, y, w: 0.12, h: 1.0, fill: { color: C.AMBER }, line: { color: C.AMBER } });
    }
    s.addText(src.src, {
      x: 0.85, y, w: 5.5, h: 1.0,
      fontSize: 13, bold: src.isTraining, fontFace: FONT_BODY, color: C.NAVY,
      valign: "middle",
    });
    s.addText(src.rows, {
      x: 6.4, y, w: 1.8, h: 1.0,
      fontSize: 18, bold: true, fontFace: FONT_HEAD, color: C.NAVY,
      align: "center", valign: "middle",
    });
    s.addText(src.role, {
      x: 8.3, y, w: 4.3, h: 1.0,
      fontSize: 12, fontFace: FONT_BODY, color: src.isTraining ? C.NAVY : C.MUTED,
      bold: src.isTraining, valign: "middle",
    });
  });
  s.addText("Only the open-market tier feeds training. The rest provide context, benchmark, and future cross-validation.", {
    x: 0.6, y: 6.7, w: 12.1, h: 0.4,
    fontSize: 13, italic: true, fontFace: FONT_BODY, color: C.MUTED, align: "center",
  });
}

// ============================================================
// SLIDE 12 — Why Training Uses Open-Market Only (Script B)
// ============================================================
{
  const s = contentSlide("Why Training Uses Open-Market Only", { sectionLabel: "THE DATA" });
  s.addNotes(
    "[Slide line]\nWe trained only on open-market listings — Lamudi data — even though we collected bank ROPA and floor-price records as well. This is grounded in the IVS 2025 Market Value definition, which requires arm's-length transactions between willing parties.\n\n[If pressed: 'Why not pool the data for more rows?']\nIVS 104 explicitly distinguishes Market Value from Liquidation Value. Bank ROPA is liquidation — sales under compulsion, with documented discounts of 28 to 34 percent in the Philippine and Southeast Asian literature, including Calinao et al. 2022 and Wong et al. 2014. Pooling these into a single training set would systematically bias the open-market coefficients downward. The empirical hedonic literature backs this up — Droes, Hoesli and Bourassa 2019 showed stratified models improved R² from 0.637 to 0.782 versus pooled; Usman et al. 2020 showed similar gains in Malaysia. Stratification is the correct choice both definitionally and empirically.\n\n[Pivot]\nThe bank and floor-price data still serve the thesis — they're useful for cross-validation in future work and they're documented in the canonical ABT — but they don't belong in the training target.",
  );
  // Big quote/anchor on left
  s.addShape("rect", { x: 0.6, y: 1.7, w: 0.12, h: 5.2, fill: { color: C.AMBER }, line: { color: C.AMBER } });
  s.addText("IVS 2025 ANCHOR", {
    x: 0.95, y: 1.7, w: 5.5, h: 0.4,
    fontSize: 12, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 3,
  });
  s.addText(
    '"Market Value is the price expected in an arm\'s-length transaction between a willing buyer and willing seller, neither under compulsion."',
    {
      x: 0.95, y: 2.1, w: 5.5, h: 2.0,
      fontSize: 16, italic: true, fontFace: FONT_BODY, color: C.NAVY,
    },
  );
  s.addText("— International Valuation Standards (IVS 2025)", {
    x: 0.95, y: 4.1, w: 5.5, h: 0.4,
    fontSize: 11, fontFace: FONT_BODY, color: C.MUTED,
  });
  s.addText("Empirical support:", {
    x: 0.95, y: 4.7, w: 5.5, h: 0.3,
    fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 2,
  });
  s.addText(
    [
      { text: "Droes, Hoesli & Bourassa (2019): stratified R² 0.637 → 0.782 vs. pooled", options: { bullet: { code: "25CF" }, fontSize: 12, color: C.INK, paraSpaceAfter: 4 } },
      { text: "Usman et al. (2020): +7% fit, −10% error in Malaysia", options: { bullet: { code: "25CF" }, fontSize: 12, color: C.INK, paraSpaceAfter: 4 } },
      { text: "Calinao (2022): Philippine foreclosure discount 28–30%", options: { bullet: { code: "25CF" }, fontSize: 12, color: C.INK } },
    ],
    { x: 1.1, y: 5.0, w: 5.5, h: 1.6, fontFace: FONT_BODY },
  );
  // Right-side reasoning
  const reasons = [
    { tag: "OPEN-MARKET", h: "Arm's-length signal", color: C.AMBER, text: "The only data type that meets the IVS Market Value definition." },
    { tag: "BANK ROPA", h: "Liquidation Value", color: C.MUTED, text: "Sales under compulsion. Different basis of value entirely." },
    { tag: "FLOOR PRICE", h: "Administrative", color: C.MUTED, text: "Lender risk floor. Not market behavior." },
    { tag: "BIR ZONAL", h: "Benchmark only", color: C.MUTED, text: "Comparison reference for valuation gap. Not a model feature." },
  ];
  reasons.forEach((r, i) => {
    const y = 1.7 + i * 1.3;
    s.addShape("roundRect", {
      x: 7.0, y, w: 5.7, h: 1.15,
      fill: { color: i === 0 ? C.AMBER_SOFT : C.WHITE },
      line: { color: r.color, width: 1.5 },
      rectRadius: 0.06,
    });
    s.addText(r.tag, {
      x: 7.2, y: y + 0.1, w: 5.3, h: 0.3,
      fontSize: 10, bold: true, fontFace: FONT_HEAD, color: r.color, charSpacing: 3,
    });
    s.addText(r.h, {
      x: 7.2, y: y + 0.4, w: 5.3, h: 0.4,
      fontSize: 16, bold: true, fontFace: FONT_HEAD, color: C.NAVY,
    });
    s.addText(r.text, {
      x: 7.2, y: y + 0.78, w: 5.3, h: 0.3,
      fontSize: 11, fontFace: FONT_BODY, color: C.INK,
    });
  });
}

// ============================================================
// SLIDE 13 — From Collection to Modeling-Ready ABT (funnel)
// ============================================================
{
  const s = contentSlide("From Collection to Modeling-Ready ABT", { sectionLabel: "THE DATA" });
  s.addNotes(
    "Started from a canonical 2,047-row Analytics Base Table covering all market tiers. Filtered to open_market only (1,619 rows). Dropped rows with null price_per_sqm and rows without spatial-lag neighbors, leaving 1,491 modeling-ready rows. 80/20 train-test split, random_state=42.",
  );
  // Funnel: 4 horizontal stages, each narrower
  const stages = [
    { rows: "2,047", label: "Canonical ABT", desc: "All market tiers · 50+ columns", w: 11.0, color: C.NAVY },
    { rows: "1,619", label: "Open-market filter", desc: "market_segment == 'open_market'", w: 9.0, color: C.NAVY },
    { rows: "1,491", label: "Modeling-ready", desc: "Drop nulls + require spatial-lag neighbors", w: 7.0, color: C.AMBER },
    { rows: "1,192 / 299", label: "Train / Test split", desc: "80/20, random_state=42", w: 5.0, color: C.AMBER },
  ];
  const startY = 1.7;
  stages.forEach((st, i) => {
    const y = startY + i * 1.15;
    const x = (W - st.w) / 2;
    s.addShape("roundRect", {
      x, y, w: st.w, h: 0.95,
      fill: { color: st.color }, line: { color: st.color },
      rectRadius: 0.08,
    });
    s.addText(st.rows, {
      x, y, w: 2.5, h: 0.95,
      fontSize: 26, bold: true, fontFace: FONT_HEAD,
      color: i < 2 ? C.AMBER : C.NAVY,
      align: "center", valign: "middle",
    });
    s.addText(st.label, {
      x: x + 2.5, y: y + 0.1, w: st.w - 2.7, h: 0.4,
      fontSize: 16, bold: true, fontFace: FONT_HEAD,
      color: i < 2 ? C.WHITE : C.NAVY,
      valign: "middle",
    });
    s.addText(st.desc, {
      x: x + 2.5, y: y + 0.5, w: st.w - 2.7, h: 0.4,
      fontSize: 12, fontFace: FONT_BODY,
      color: i < 2 ? C.SLATE_DARK : C.NAVY,
      valign: "middle",
    });
    if (i < stages.length - 1) {
      const ax = W / 2 - 0.15;
      const ay = y + 0.95;
      s.addShape("rightTriangle", {
        x: ax, y: ay, w: 0.3, h: 0.18,
        fill: { color: C.MUTED }, line: { color: C.MUTED },
        rotate: 90,
      });
    }
  });
}

// ============================================================
// SLIDE 14 — Geospatial Features Overview (4 blocks)
// ============================================================
{
  const s = contentSlide("Geospatial Features Overview", { sectionLabel: "THE DATA" });
  s.addNotes("Four feature blocks: CBD network distances, MCRAI accessibility index, spatial lag, and structural attributes.");
  const blocks = [
    { num: "1", h: "CBD Distances", d: "8 nodes · osmnx Dijkstra routing.\nGiuliano & Small (1991), JICA 2050." },
    { num: "2", h: "MCRAI", d: "9 amenity categories · Hansen gravity\nwith category-specific radii." },
    { num: "3", h: "Spatial Lag", d: "Neighbor-mean price within 1 km.\nTobler's First Law of Geography." },
    { num: "4", h: "Structural", d: "Property type, area, bedrooms, baths,\nbarangay, is_mactan_island flag." },
  ];
  const cardW = 2.95, cardH = 4.0, gapX = 0.2;
  const startX = (W - (cardW * 4 + gapX * 3)) / 2;
  blocks.forEach((b, i) => {
    const x = startX + i * (cardW + gapX);
    card(s, x, 1.8, cardW, cardH, b.h, b.d, { icon: b.num });
  });
  s.addText("Each block is engineered, not ingested raw. The contribution is in the construction.", {
    x: 0.6, y: 6.3, w: W - 1.2, h: 0.5,
    fontSize: 14, italic: true, fontFace: FONT_BODY, color: C.MUTED, align: "center",
  });
}

// ============================================================
// SECTION DIVIDER 3 → Methodology
// ============================================================
sectionDivider("03", "Methodology", "PART THREE");

// ============================================================
// SLIDE 15 — CBD Network Distances (Scripts C + F)
// ============================================================
{
  const s = contentSlide("CBD Network Distances", { sectionLabel: "METHODOLOGY" });
  s.addNotes(
    "[Slide line — Script C]\nWe identified eight urban nodes as distance features. The selection follows two anchors: Giuliano and Small's 1991 employment-density criteria for polycentric subcenter identification, and the JICA Mega Cebu Roadmap 2050, which is the official regional plan and explicitly names each of these as a distinct urban cluster.\n\n[If pressed: 'Why these eight specifically? Why drop IT Park?']\nWe started with eleven candidates. IT Park was dropped because its distance correlates 0.99 with Cebu Business Park — it's an extension of the same employment center, not an independent peak. Minglanilla Lipata correlated 0.997 with another node. Minglanilla Poblacion fails the Giuliano-Small employment threshold. The eight that remained pass McMillen's 2001 nonparametric distance-decay test. The Airport is included separately because Heikkila et al. 1989 established that aerotropolis effects generate independent distance-to-value gradients.\n\n[Pivot — Naga City]\nNaga City sits outside our six-LGU training area but functions as a CBD node because it pulls labor from Talisay and Minglanilla. The single distance variable captures the net effect.\n\n— — —\n\n[Script F — osmnx vs Haversine]\nAll distance features are computed through the OSM road network using osmnx Dijkstra routing, with Haversine as a fallback only.\n\n[If pressed: 'Why not Haversine?']\nMactan Island. We have 312 properties in Lapu-Lapu City separated from the mainland by water. Haversine — straight-line — gives them an artificially short distance to Cebu Business Park because it ignores the bridge crossing. Modern hedonic literature is consistent: network distance is theoretically and empirically superior.",
  );
  // Left: 21.4% callout
  statCallout(s, 0.6, 1.7, 4.5, 2.6, "21.4%", "OF TOTAL SHAP WEIGHT\nLargest geospatial signal block");
  // Right: methodology bullets
  s.addText("Selection criteria", {
    x: 5.5, y: 1.7, w: 7.3, h: 0.4,
    fontSize: 13, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 2,
  });
  s.addText(
    [
      { text: "Giuliano & Small (1991): employment-density polycentric subcenter criteria", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.INK, paraSpaceAfter: 6 } },
      { text: "JICA Mega Cebu Roadmap 2050: official designation as distinct urban clusters", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.INK, paraSpaceAfter: 6 } },
      { text: "McMillen (2001) nonparametric distance-decay test: independent peaks", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.INK, paraSpaceAfter: 6 } },
    ],
    { x: 5.7, y: 2.05, w: 7.1, h: 1.7, fontFace: FONT_BODY, valign: "top" },
  );
  s.addText("Routing: osmnx Dijkstra (network), Haversine fallback only", {
    x: 5.5, y: 4.0, w: 7.3, h: 0.4,
    fontSize: 13, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 2,
  });
  s.addText(
    "Mactan Island has 312 properties separated from the mainland by water. Haversine is physically wrong — it ignores the bridge crossing. Network distance captures real travel cost and the western mountain detours.",
    {
      x: 5.7, y: 4.4, w: 7.1, h: 1.5,
      fontSize: 13, fontFace: FONT_BODY, color: C.INK, italic: true,
    },
  );
  // 8 nodes pill list
  s.addShape("rect", { x: 0.6, y: 5.8, w: 12.1, h: 1.1, fill: { color: C.SLATE }, line: { color: C.SLATE } });
  s.addText("8 NODES", {
    x: 0.85, y: 5.85, w: 1.5, h: 0.3,
    fontSize: 10, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 3,
  });
  s.addText(
    "Cebu Business Park · Mandaue CBD · Mactan CBD · South Road Properties · Talisay Tabunok · Consolacion · Naga City (anchor only) · Mactan-Cebu International Airport",
    {
      x: 0.85, y: 6.15, w: 11.6, h: 0.7,
      fontSize: 12, fontFace: FONT_BODY, color: C.NAVY,
    },
  );
}

// ============================================================
// SLIDE 16 — MCRAI Introduction (Script A: OHANA comparison)
// ============================================================
{
  const s = contentSlide("MCRAI: Built From OHANA, Rebuilt For Valuation", { sectionLabel: "METHODOLOGY" });
  s.addNotes(
    "[Slide line — Script A]\nMCRAI — the Metro Cebu Residential Accessibility Index — is a custom Hansen gravity-based accessibility framework. The methodological lineage traces back to Project OHANA, a nationwide equity-mapping framework. We kept the Hansen structure. We rebuilt almost everything else, because OHANA's design serves a different objective.\n\n[If pressed: 'Why didn't you just use OHANA?']\nOHANA was built to identify where public services *should* be located for social equity — that's normative economics. Property valuation has to measure what buyers *actually* pay — that's positive economics, revealed preferences. Beyond that, OHANA has four implementation choices that don't transfer to a hedonic model: 1km×1km grid centroids (MAUP), Euclidean distance (impossible across Mactan), equal weights across categories (violates utility theory), and fixed β=2.0 decay. We rebuilt all four. What we kept from OHANA is the conceptual architecture — Hansen gravity scoring across multiple POI categories. What we rebuilt is the entire computation.\n\n[Pivot]\nSo MCRAI is a Cebu-specific, residential-specific, revealed-preference accessibility index that draws on OHANA's framework but is calibrated to the valuation problem this thesis is solving.",
  );
  // Top label
  s.addText(
    "Methodological lineage from Project OHANA — Hansen gravity structure kept, every implementation detail rebuilt for residential valuation.",
    {
      x: 0.6, y: 1.65, w: W - 1.2, h: 0.6,
      fontSize: 14, italic: true, fontFace: FONT_BODY, color: C.MUTED,
    },
  );
  // Two-column comparison: OHANA (left) vs MCRAI (right)
  const colW = 6.0, colY = 2.4, colH = 4.5;
  // OHANA left
  s.addShape("roundRect", {
    x: 0.6, y: colY, w: colW, h: colH,
    fill: { color: C.SLATE }, line: { color: C.SLATE_DARK, width: 1 },
    rectRadius: 0.08,
  });
  s.addShape("rect", { x: 0.6, y: colY, w: colW, h: 0.6, fill: { color: C.MUTED }, line: { color: C.MUTED } });
  s.addText("PROJECT OHANA  ·  inherited", {
    x: 0.6, y: colY, w: colW, h: 0.6,
    fontSize: 13, bold: true, fontFace: FONT_HEAD, color: C.WHITE,
    align: "center", valign: "middle", charSpacing: 3,
  });
  const ohana = [
    "Normative — where services should be (equity)",
    "1km × 1km grid centroids",
    "Euclidean (straight-line) distance",
    "Equal weights across all categories",
    "Fixed β = 2.0 decay parameter",
  ];
  s.addText(
    ohana.map((t) => ({ text: t, options: { bullet: { code: "25CB" }, fontSize: 13, color: C.MUTED, paraSpaceAfter: 8 } })),
    { x: 0.85, y: colY + 0.85, w: colW - 0.4, h: colH - 1.0, fontFace: FONT_BODY, valign: "top" },
  );
  // Arrow
  s.addShape("rightTriangle", {
    x: 6.7 - 0.18, y: colY + colH / 2 - 0.18, w: 0.36, h: 0.36,
    fill: { color: C.AMBER }, line: { color: C.AMBER },
  });
  // MCRAI right
  s.addShape("roundRect", {
    x: W - 0.6 - colW, y: colY, w: colW, h: colH,
    fill: { color: C.WHITE }, line: { color: C.AMBER, width: 2 },
    rectRadius: 0.08,
  });
  s.addShape("rect", { x: W - 0.6 - colW, y: colY, w: colW, h: 0.6, fill: { color: C.NAVY }, line: { color: C.NAVY } });
  s.addText("MCRAI  ·  rebuilt", {
    x: W - 0.6 - colW, y: colY, w: colW, h: 0.6,
    fontSize: 13, bold: true, fontFace: FONT_HEAD, color: C.AMBER,
    align: "center", valign: "middle", charSpacing: 3,
  });
  const mcrai = [
    "Positive — what buyers pay (revealed preference)",
    "Parcel-level computation (avoids MAUP)",
    "osmnx network distance (handles Mactan)",
    "OLS-derived empirical weights (Decision 20)",
    "Category-specific radii (0.8 – 3.0 km)",
  ];
  s.addText(
    mcrai.map((t) => ({ text: t, options: { bullet: { code: "25CF" }, fontSize: 13, color: C.NAVY, paraSpaceAfter: 8, bold: false } })),
    { x: W - 0.6 - colW + 0.25, y: colY + 0.85, w: colW - 0.4, h: colH - 1.0, fontFace: FONT_BODY, valign: "top" },
  );
  s.addText("Literature anchor: Tiebout (1956) · Bayer & McMillan (2012) · Yang et al. (2016) · Hansen (1959)", {
    x: 0.6, y: 7.05, w: W - 1.2, h: 0.4,
    fontSize: 11, fontFace: FONT_BODY, color: C.MUTED, align: "center", italic: true,
  });
}

// ============================================================
// SLIDE 17 — MCRAI Categories (Script D: spatial sorting)
// ============================================================
{
  const s = contentSlide("MCRAI Categories: Which Enter the Composite", { sectionLabel: "METHODOLOGY" });
  s.addNotes(
    "[Slide line — Script D]\nThree of the nine MCRAI categories returned negative OLS coefficients in the Stage 1 hedonic regression: security, tourism, and retail density. We excluded these from the composite index. They remain as individual features for the tree models.\n\n[If pressed: 'Doesn't a negative coefficient mean those amenities are bad?']\nIt's not a disamenity argument — it's a spatial sorting argument. Tiebout (1956) established that households self-select into neighborhoods based on tax-and-service bundles. Bayer and McMillan (2012) extended this empirically: public good provision, including security infrastructure, clusters where lower-income populations sort, NOT where high property values are located. Police substations are deployed where they're needed most — which tends to be lower-priced barangays. Dronyk-Trosper (2017) documents this across three million Florida home sales. For retail density, Yang, Song & Choi (2016) in Seoul show an inverted-U: commercial density raises values up to a point, then depresses them through noise and traffic.\n\n[Pivot]\nBy restricting the composite to education, grocery, recreation, and transport — the four positive-coefficient categories — we get a clean revealed-preference measure of amenities homebuyers actually pay for.",
  );
  // Categories table (left, redesigned)
  const tableX = 0.6, tableY = 1.7, rowH = 0.42;
  // Header
  s.addShape("rect", { x: tableX, y: tableY, w: 7.5, h: rowH, fill: { color: C.NAVY }, line: { color: C.NAVY } });
  s.addText("CATEGORY", { x: tableX + 0.2, y: tableY, w: 4.0, h: rowH, fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, valign: "middle", charSpacing: 2 });
  s.addText("RADIUS", { x: tableX + 4.2, y: tableY, w: 1.5, h: rowH, fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, valign: "middle", charSpacing: 2, align: "center" });
  s.addText("COMPOSITE", { x: tableX + 5.7, y: tableY, w: 1.8, h: rowH, fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, valign: "middle", charSpacing: 2, align: "center" });
  const cats = [
    { c: "Education", r: "0.8 km", in: true },
    { c: "Grocery", r: "2.0 km", in: true },
    { c: "Recreation", r: "1.5 km", in: true },
    { c: "Transport (OSM corridors)", r: "3.0 km", in: true },
    { c: "Health", r: "2.0 km", in: false },
    { c: "Finance", r: "1.5 km", in: false },
    { c: "Security", r: "2.0 km", in: false },
    { c: "Tourism", r: "3.0 km", in: false },
    { c: "Retail Density", r: "1.0 km", in: false },
  ];
  cats.forEach((cat, i) => {
    const y = tableY + (i + 1) * rowH;
    const fill = cat.in ? C.AMBER_SOFT : (i % 2 === 0 ? C.WHITE : C.SLATE);
    s.addShape("rect", { x: tableX, y, w: 7.5, h: rowH, fill: { color: fill }, line: { color: C.SLATE_DARK } });
    if (cat.in) {
      s.addShape("rect", { x: tableX, y, w: 0.08, h: rowH, fill: { color: C.AMBER }, line: { color: C.AMBER } });
    }
    s.addText(cat.c, { x: tableX + 0.2, y, w: 4.0, h: rowH, fontSize: 12, bold: cat.in, fontFace: FONT_BODY, color: C.NAVY, valign: "middle" });
    s.addText(cat.r, { x: tableX + 4.2, y, w: 1.5, h: rowH, fontSize: 12, fontFace: FONT_BODY, color: C.INK, valign: "middle", align: "center" });
    s.addText(cat.in ? "✓  YES" : "—  no", { x: tableX + 5.7, y, w: 1.8, h: rowH, fontSize: 12, bold: cat.in, fontFace: FONT_HEAD, color: cat.in ? C.NAVY : C.MUTED, valign: "middle", align: "center" });
  });
  // Right-side explanation
  s.addShape("rect", { x: 8.4, y: 1.7, w: 0.12, h: 5.2, fill: { color: C.AMBER }, line: { color: C.AMBER } });
  s.addText("DECISION 20", {
    x: 8.7, y: 1.7, w: 4.4, h: 0.35,
    fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 3,
  });
  s.addText("Composite restricted to positive-OLS categories", {
    x: 8.7, y: 2.05, w: 4.4, h: 0.6,
    fontSize: 16, bold: true, fontFace: FONT_HEAD, color: C.NAVY,
  });
  s.addText(
    "Excluded categories had negative OLS coefficients — interpreted as spatial sorting / threshold disamenity, not amenity value.",
    {
      x: 8.7, y: 2.75, w: 4.4, h: 1.5,
      fontSize: 12, fontFace: FONT_BODY, color: C.INK, italic: true,
    },
  );
  s.addText("Why negative ≠ bad", {
    x: 8.7, y: 4.3, w: 4.4, h: 0.4,
    fontSize: 13, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 2,
  });
  s.addText(
    "Tiebout (1956) — household sorting by service bundles produces income-stratified equilibria.\n\nBayer & McMillan (2012) — public-good provision clusters with lower-income populations.\n\nYang et al. (2016) — inverted-U for commercial density.",
    {
      x: 8.7, y: 4.7, w: 4.4, h: 2.2,
      fontSize: 11, fontFace: FONT_BODY, color: C.INK,
    },
  );
}

// ============================================================
// SLIDE 18 — Modeling Pipeline (4-step flow + Script G)
// ============================================================
{
  const s = contentSlide("Modeling Pipeline", { sectionLabel: "METHODOLOGY" });
  s.addNotes(
    "[Slide line — Script G]\nWe log-transformed total price for OLS estimation. For Random Forest and XGBoost, we keep raw values — trees handle nonlinearity through splits.\n\n[If pressed: 'Why the asymmetric treatment?']\nThree reasons. First, hedonic theory: Rosen 1974, Can 1992, Sirmans et al. 2005 — log-linear specifications are standard in real estate hedonic regression. Second, the data: there are a small number of large-development listings — one of them is 150,000 square meters — which under linear OLS amplify into multi-billion-peso predictions, a 400x distortion. Third, the result: without log transformation, OLS produced an R² of negative 45 on the test set. With log transformation, OLS reached 0.394. RF and XGBoost don't need this because their splits are scale-invariant on the input side.\n\n[Pivot]\nOLS is still the weakest of the three models — it's the linear baseline. After log transformation it produces interpretable elasticities, which is what we use it for.",
  );
  // 4-step pipeline
  const steps = [
    { num: "1", t: "OLS Hedonic", d: "Log-linear baseline\n(Rosen 1974)" },
    { num: "2", t: "Random Forest", d: "Non-linear, robust\n(deployed)" },
    { num: "3", t: "XGBoost", d: "Gradient boosting\non tabular data" },
    { num: "4", t: "SHAP", d: "Feature-level\nexplainability" },
  ];
  const stepW = 2.6, stepH = 2.0, gapX = 0.55;
  const startX = (W - (stepW * 4 + gapX * 3)) / 2;
  const startY = 2.0;
  steps.forEach((st, i) => {
    const x = startX + i * (stepW + gapX);
    pipelineStep(s, x, startY, stepW, stepH, st.num, st.t, st.d);
    if (i < steps.length - 1) {
      const ax = x + stepW + 0.05;
      const ay = startY + stepH / 2;
      s.addShape("rightTriangle", {
        x: ax + 0.30, y: ay - 0.15, w: 0.2, h: 0.32,
        fill: { color: C.AMBER }, line: { color: C.AMBER },
      });
      s.addShape("rect", {
        x: ax, y: ay - 0.05, w: 0.35, h: 0.1,
        fill: { color: C.AMBER }, line: { color: C.AMBER },
      });
    }
  });
  // Bottom bar with key choices
  s.addShape("rect", { x: 0.6, y: 5.0, w: 12.1, h: 1.95, fill: { color: C.SLATE }, line: { color: C.SLATE } });
  s.addText("KEY MODELING CHOICES", {
    x: 0.85, y: 5.1, w: 11.6, h: 0.3,
    fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 3,
  });
  s.addText(
    [
      { text: "Target: log(total price) — right-skewed; back-transformed for the price surface.", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.NAVY, paraSpaceAfter: 4 } },
      { text: "OLS uses log-log specification (Rosen 1974, Can 1992, Sirmans 2005); RF/XGB use raw features.", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.NAVY, paraSpaceAfter: 4 } },
      { text: "Without log transform, OLS hit R² = −45 (worse than mean). With log, OLS → 0.394.", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.NAVY, paraSpaceAfter: 4 } },
      { text: "Evaluation: R², MAPE, MAE, RMSE.", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.NAVY, paraSpaceAfter: 4 } },
    ],
    { x: 0.95, y: 5.4, w: 11.5, h: 1.5, fontFace: FONT_BODY, valign: "top" },
  );
}

// ============================================================
// SECTION DIVIDER 4 → Results
// ============================================================
sectionDivider("04", "Results", "PART FOUR");

// ============================================================
// SLIDE 19 — Model Comparison (Script E)
// ============================================================
{
  const s = contentSlide("Model Comparison Results", { sectionLabel: "RESULTS" });
  s.addNotes(
    "[Slide line — Script E]\nRandom Forest baseline outperformed both tuned RF and tuned XGBoost on the held-out test set. We ran a baseline-centered confirmation grid search after the initial result. The baseline still wins.\n\n[If pressed: 'Tuning is supposed to improve performance. Why didn't it here?']\nSample size. With 1,212 training rows and five-fold CV, fold variance dominates signal variance — the search finds parameters that look CV-optimal because they fit the fold structure, not because they generalize. Even with the baseline parameters explicitly inside the search space, the tuned best fell short of the deployed baseline by about 7.9 million pesos in RMSE and 0.13 in R². The conclusion is that the binding constraint is data volume, not configuration.\n\n[Pivot]\nThis is informative for future work — it tells us where the next round of investment should go: more transaction data, not more hyperparameters.",
  );
  // Stat callout: R² 0.807
  statCallout(s, 0.6, 1.7, 4.5, 2.6, "0.807", "RANDOM FOREST R²\nDeployed model · held-out test set");
  // Comparison table
  const tableX = 5.4, tableY = 1.7, tableW = 7.4;
  const colWs = [2.4, 1.0, 1.2, 1.4, 1.4];
  const headerH = 0.5, rowH = 0.65;
  // Header
  s.addShape("rect", { x: tableX, y: tableY, w: tableW, h: headerH, fill: { color: C.NAVY }, line: { color: C.NAVY } });
  ["Model", "R²", "MAPE", "MAE", "RMSE"].forEach((h, i) => {
    const cx = tableX + colWs.slice(0, i).reduce((a, b) => a + b, 0);
    s.addText(h, {
      x: cx + 0.1, y: tableY, w: colWs[i] - 0.2, h: headerH,
      fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER,
      align: i === 0 ? "left" : "center", valign: "middle", charSpacing: 2,
    });
  });
  const rows = [
    { m: "OLS Hedonic", r2: "0.083", mape: "201.6%", mae: "9.82M", rmse: "59.82M", winner: false },
    { m: "Random Forest (deployed)", r2: "0.807", mape: "59.28%", mae: "4.95M", rmse: "27.45M", winner: true },
    { m: "XGBoost (tuned)", r2: "0.557", mape: "58.93%", mae: "6.06M", rmse: "41.58M", winner: false },
  ];
  rows.forEach((row, i) => {
    const y = tableY + headerH + i * rowH;
    const fill = row.winner ? C.AMBER_SOFT : (i % 2 === 0 ? C.WHITE : C.SLATE);
    s.addShape("rect", { x: tableX, y, w: tableW, h: rowH, fill: { color: fill }, line: { color: C.SLATE_DARK } });
    if (row.winner) {
      s.addShape("rect", { x: tableX, y, w: 0.1, h: rowH, fill: { color: C.AMBER }, line: { color: C.AMBER } });
    }
    [row.m, row.r2, row.mape, row.mae, row.rmse].forEach((cell, j) => {
      const cx = tableX + colWs.slice(0, j).reduce((a, b) => a + b, 0);
      s.addText(cell, {
        x: cx + 0.1, y, w: colWs[j] - 0.2, h: rowH,
        fontSize: row.winner ? 13 : 12, bold: row.winner, fontFace: FONT_BODY, color: C.NAVY,
        align: j === 0 ? "left" : "center", valign: "middle",
      });
    });
  });
  // Footer interpretation
  s.addShape("rect", { x: 0.6, y: 4.7, w: 12.1, h: 2.2, fill: { color: C.SLATE }, line: { color: C.SLATE } });
  s.addText("WHY BASELINE BEATS TUNED", {
    x: 0.85, y: 4.85, w: 11.6, h: 0.3,
    fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 3,
  });
  s.addText(
    [
      { text: "Sample size (1,212 train rows) is the binding constraint, not configuration.", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.NAVY, paraSpaceAfter: 4 } },
      { text: "5-fold CV on small N: fold variance dominates signal variance. Tuned parameters overfit to fold structure.", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.NAVY, paraSpaceAfter: 4 } },
      { text: "Decision 25 confirmation: even with baseline params explicitly in search space, tuning did not win.", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.NAVY, paraSpaceAfter: 4 } },
    ],
    { x: 0.95, y: 5.15, w: 11.5, h: 1.7, fontFace: FONT_BODY, valign: "top" },
  );
}

// ============================================================
// SLIDE 20 — RF Actual vs. Predicted (PLACEHOLDER)
// ============================================================
{
  const s = contentSlide("Random Forest: Actual vs. Predicted", { sectionLabel: "RESULTS" });
  s.addNotes(
    "Insert the RF actual-vs-predicted scatter from EDA/. Cluster tightness clearest below PHP 10M; dispersion increases above PHP 20M where listing data thins out.",
  );
  // Visual placeholder
  s.addShape("roundRect", {
    x: 0.6, y: 1.7, w: 8.0, h: 5.2,
    fill: { color: C.SLATE }, line: { color: C.SLATE_DARK, width: 1 },
    rectRadius: 0.08,
  });
  s.addText("[ DIAGRAM TO ADD ]", {
    x: 0.6, y: 2.0, w: 8.0, h: 0.4,
    fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 3,
    align: "center",
  });
  s.addText("RF Actual vs. Predicted Scatter", {
    x: 0.6, y: 2.4, w: 8.0, h: 0.5,
    fontSize: 18, bold: true, fontFace: FONT_HEAD, color: C.NAVY,
    align: "center",
  });
  s.addText(
    "Source: thesis_main/EDA/ (existing manuscript Chapter 7 figure)\n\nx-axis: actual price (PHP) · y-axis: predicted price (PHP)\nDiagonal reference line · 299 held-out test points",
    {
      x: 1.0, y: 3.2, w: 7.2, h: 3.5,
      fontSize: 12, italic: true, fontFace: FONT_BODY, color: C.MUTED,
      align: "center", valign: "top",
    },
  );
  // Right interpretation
  s.addShape("rect", { x: 8.9, y: 1.7, w: 0.12, h: 5.2, fill: { color: C.AMBER }, line: { color: C.AMBER } });
  s.addText("INTERPRETATION", {
    x: 9.2, y: 1.7, w: 3.6, h: 0.35,
    fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 3,
  });
  s.addText(
    [
      { text: "Tightest cluster below PHP 10M — where the listing data is densest.", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.INK, paraSpaceAfter: 10 } },
      { text: "Higher dispersion above PHP 20M — luxury tier where listings thin out.", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.INK, paraSpaceAfter: 10 } },
      { text: "299 held-out test properties.", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.INK, paraSpaceAfter: 10 } },
      { text: "Random_state = 42 for reproducibility.", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.INK, paraSpaceAfter: 10 } },
    ],
    { x: 9.2, y: 2.1, w: 3.6, h: 4.8, fontFace: FONT_BODY, valign: "top" },
  );
}

// ============================================================
// SLIDE 21 — SHAP Top 10 Features
// ============================================================
{
  const s = contentSlide("SHAP Top 10 Features (Random Forest)", { sectionLabel: "RESULTS" });
  s.addNotes(
    "Top 10 SHAP features in order from the Chapter 7 RF table. Property type and structural attributes dominate; CBD distances enter at #4 (Consolacion) and #10 (Cebu Business Park).",
  );
  const features = [
    { rank: "1", name: "property_type_Single Detached", cat: "STRUCTURAL", w: 100 },
    { rank: "2", name: "property_type_Condominium", cat: "STRUCTURAL", w: 86 },
    { rank: "3", name: "bedrooms", cat: "STRUCTURAL", w: 72 },
    { rank: "4", name: "dist_consolacion_m", cat: "CBD DISTANCE", w: 65, highlight: true },
    { rank: "5", name: "city_Mandaue City", cat: "STRUCTURAL", w: 58 },
    { rank: "6", name: "is_vacant_lot", cat: "STRUCTURAL", w: 52 },
    { rank: "7", name: "property_type_Vacant Lot", cat: "STRUCTURAL", w: 47 },
    { rank: "8", name: "area_sqm", cat: "STRUCTURAL", w: 44 },
    { rank: "9", name: "floor_area_sqm", cat: "STRUCTURAL", w: 41 },
    { rank: "10", name: "dist_cebu_business_park_m", cat: "CBD DISTANCE", w: 37, highlight: true },
  ];
  const startY = 1.7, rowH = 0.48;
  features.forEach((f, i) => {
    const y = startY + i * rowH;
    // Rank
    s.addText(f.rank, {
      x: 0.6, y, w: 0.6, h: rowH,
      fontSize: 14, bold: true, fontFace: FONT_HEAD, color: C.MUTED,
      align: "center", valign: "middle",
    });
    // Bar
    const barW = f.w * 0.07;
    s.addShape("rect", { x: 1.3, y: y + 0.08, w: 7.0, h: rowH - 0.16, fill: { color: C.SLATE }, line: { color: C.SLATE } });
    s.addShape("rect", { x: 1.3, y: y + 0.08, w: barW, h: rowH - 0.16, fill: { color: f.highlight ? C.AMBER : C.NAVY }, line: { color: f.highlight ? C.AMBER : C.NAVY } });
    s.addText(f.name, {
      x: 1.45, y, w: 6.7, h: rowH,
      fontSize: 12, bold: f.highlight, fontFace: FONT_BODY, color: f.highlight ? C.NAVY : C.WHITE,
      valign: "middle",
    });
    // Category tag
    s.addShape("rect", { x: 8.5, y: y + 0.08, w: 1.8, h: rowH - 0.16, fill: { color: f.highlight ? C.AMBER : C.SLATE }, line: { color: f.highlight ? C.AMBER : C.SLATE } });
    s.addText(f.cat, {
      x: 8.5, y: y + 0.08, w: 1.8, h: rowH - 0.16,
      fontSize: 9, bold: true, fontFace: FONT_HEAD, color: f.highlight ? C.NAVY : C.MUTED,
      align: "center", valign: "middle", charSpacing: 1,
    });
  });
  // Legend right
  s.addShape("rect", { x: 10.5, y: 1.7, w: 2.3, h: 4.8, fill: { color: C.SLATE }, line: { color: C.SLATE } });
  s.addText("LEGEND", {
    x: 10.65, y: 1.85, w: 2.0, h: 0.3,
    fontSize: 10, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 3,
  });
  s.addShape("rect", { x: 10.7, y: 2.3, w: 0.4, h: 0.25, fill: { color: C.NAVY }, line: { color: C.NAVY } });
  s.addText("Structural", { x: 11.2, y: 2.25, w: 1.5, h: 0.3, fontSize: 11, fontFace: FONT_BODY, color: C.NAVY, valign: "middle" });
  s.addShape("rect", { x: 10.7, y: 2.7, w: 0.4, h: 0.25, fill: { color: C.AMBER }, line: { color: C.AMBER } });
  s.addText("CBD distance", { x: 11.2, y: 2.65, w: 1.5, h: 0.3, fontSize: 11, fontFace: FONT_BODY, color: C.NAVY, valign: "middle" });
  s.addText(
    "CBD distances enter at #4 (Consolacion) and #10 (CBP). Spatial signal is real but lives in CBD distances, not MCRAI.",
    { x: 10.65, y: 3.4, w: 2.0, h: 3.0, fontSize: 11, italic: true, fontFace: FONT_BODY, color: C.MUTED, valign: "top" },
  );
}

// ============================================================
// SLIDE 22 — SHAP Block Analysis (visual bars)
// ============================================================
{
  const s = contentSlide("SHAP Importance — by Block", { sectionLabel: "RESULTS" });
  s.addNotes(
    "MCRAI's individual signal is muted because the CBD distance block absorbs the spatial accessibility variation it also measures. This is expected collinearity, not a failure of the index. The geospatial signal is real — it lives mostly in the CBD distances.",
  );
  const blocks = [
    { name: "Structural + property type", pct: 75.6, color: C.NAVY },
    { name: "CBD distance block (8 nodes combined)", pct: 21.4, color: C.AMBER },
    { name: "MCRAI 9 categories combined", pct: 3.0, color: C.MUTED },
  ];
  const startY = 1.9, blockH = 1.3, gap = 0.3;
  blocks.forEach((b, i) => {
    const y = startY + i * (blockH + gap);
    // Bar background
    s.addShape("rect", { x: 0.6, y: y + 0.5, w: 11.0, h: 0.4, fill: { color: C.SLATE }, line: { color: C.SLATE } });
    // Bar fill
    const fillW = (b.pct / 100) * 11.0;
    s.addShape("rect", { x: 0.6, y: y + 0.5, w: fillW, h: 0.4, fill: { color: b.color }, line: { color: b.color } });
    // Label
    s.addText(b.name, {
      x: 0.6, y, w: 8.0, h: 0.5,
      fontSize: 16, bold: true, fontFace: FONT_HEAD, color: C.NAVY,
    });
    // Percentage
    s.addText(`${b.pct}%`, {
      x: W - 2.7, y, w: 2.0, h: 0.5,
      fontSize: 28, bold: true, fontFace: FONT_HEAD, color: b.color,
      align: "right",
    });
  });
  // Bottom interpretation
  s.addShape("rect", { x: 0.6, y: 6.1, w: 12.1, h: 0.85, fill: { color: C.AMBER_SOFT }, line: { color: C.AMBER } });
  s.addShape("rect", { x: 0.6, y: 6.1, w: 0.12, h: 0.85, fill: { color: C.AMBER }, line: { color: C.AMBER } });
  s.addText(
    "MCRAI's individual signal is muted because the CBD distance block absorbs the same spatial accessibility variation. Expected collinearity, not failure — the geospatial signal lives in CBD distances.",
    {
      x: 0.95, y: 6.1, w: 11.6, h: 0.85,
      fontSize: 13, italic: true, fontFace: FONT_BODY, color: C.NAVY, valign: "middle",
    },
  );
}

// ============================================================
// SLIDE 23 — On the 59.28% MAPE (Script I)
// ============================================================
{
  const s = contentSlide("On the 59.28% MAPE", { sectionLabel: "RESULTS" });
  s.addNotes(
    "[Slide line — Script I]\nI want to address the 59 percent MAPE directly, because it looks high in absolute terms and the panel will rightly want to understand it.\n\n[If pressed: '59 percent error means the model is wrong half the time. How is this useful?']\nThree things. First, the framing: total-price MAPE compounds two error sources — area mis-specification and unit-price mis-specification — into one number. The per-square-meter MAE of about 19,743 pesos is what valuation practitioners actually compare against. Second, the data ceiling: we're trained on asking prices, not deed-of-sale records. There's no architecture that resolves a noise floor that comes from the data source itself. Third, the deliverable framing: this isn't being presented as a certified appraisal substitute. It's a first-generation, geospatially grounded decision-support tool.\n\n[Pivot]\nThe next step is access to deed-of-sale transaction data. That's the single biggest move that would lower the noise floor. Until then, this is the best evidence-based starting point for Metro Cebu open-market residential valuation that exists.",
  );
  // Two-column layout
  // Left: stat callout — 59.28% with framing
  s.addShape("rect", { x: 0.6, y: 1.7, w: 6.0, h: 5.2, fill: { color: C.NAVY }, line: { color: C.NAVY } });
  s.addText("HEADLINE METRIC", {
    x: 0.6, y: 1.9, w: 6.0, h: 0.4,
    fontSize: 12, bold: true, fontFace: FONT_HEAD, color: C.AMBER, align: "center", charSpacing: 3,
  });
  s.addText("59.28%", {
    x: 0.6, y: 2.4, w: 6.0, h: 1.6,
    fontSize: 92, bold: true, fontFace: FONT_HEAD, color: C.AMBER, align: "center", valign: "middle",
  });
  s.addText("Total-price MAPE", {
    x: 0.6, y: 4.0, w: 6.0, h: 0.4,
    fontSize: 16, fontFace: FONT_HEAD, color: C.WHITE, align: "center",
  });
  s.addText("Chapter 7 Table 1", {
    x: 0.6, y: 4.4, w: 6.0, h: 0.3,
    fontSize: 11, italic: true, fontFace: FONT_BODY, color: C.SLATE_DARK, align: "center",
  });
  s.addShape("rect", { x: 1.6, y: 5.0, w: 4.0, h: 0.02, fill: { color: C.AMBER }, line: { color: C.AMBER } });
  s.addText("Per-sqm reframing", {
    x: 0.6, y: 5.2, w: 6.0, h: 0.4,
    fontSize: 12, bold: true, fontFace: FONT_HEAD, color: C.AMBER, align: "center", charSpacing: 2,
  });
  s.addText("≈ PHP 19,743 / sqm MAE", {
    x: 0.6, y: 5.6, w: 6.0, h: 0.5,
    fontSize: 22, bold: true, fontFace: FONT_HEAD, color: C.WHITE, align: "center",
  });
  s.addText("≈ one BIR zonal tier of error", {
    x: 0.6, y: 6.15, w: 6.0, h: 0.4,
    fontSize: 13, italic: true, fontFace: FONT_BODY, color: C.SLATE_DARK, align: "center",
  });
  // Right: three reasons
  const reasons = [
    { t: "Total-price MAPE is compound", d: "It mixes area mis-specification with unit-price error. Per-sqm framing isolates what practitioners actually compare." },
    { t: "Asking-price data ceiling", d: "We're trained on listings, not deed-of-sale records. No model architecture resolves data-source noise." },
    { t: "Decision-support, not appraisal", d: "First-generation tool with feature-level SHAP. Banks, LGUs, planners need defensible references — not 3% error." },
  ];
  reasons.forEach((r, i) => {
    const y = 1.7 + i * 1.78;
    s.addShape("ellipse", {
      x: 6.95, y: y + 0.12, w: 0.55, h: 0.55,
      fill: { color: C.AMBER }, line: { color: C.AMBER },
    });
    s.addText(`${i + 1}`, {
      x: 6.95, y: y + 0.12, w: 0.55, h: 0.55,
      fontSize: 18, bold: true, fontFace: FONT_HEAD, color: C.NAVY,
      align: "center", valign: "middle",
    });
    s.addText(r.t, {
      x: 7.65, y: y + 0.1, w: 5.1, h: 0.5,
      fontSize: 16, bold: true, fontFace: FONT_HEAD, color: C.NAVY,
    });
    s.addText(r.d, {
      x: 7.65, y: y + 0.6, w: 5.1, h: 1.1,
      fontSize: 12, fontFace: FONT_BODY, color: C.INK,
    });
  });
}

// ============================================================
// SLIDE 24 — Performance Across LGUs (Script H)
// ============================================================
{
  const s = contentSlide("Performance Across LGUs", { sectionLabel: "RESULTS" });
  s.addNotes(
    "[Slide line — Script H]\nTotal-price MAPE is 59.28 percent. On a per-square-meter basis, MAE is roughly 19,000 to 20,000 pesos per square meter — about one BIR zonal tier. Across our six LGUs, performance is uneven; Lapu-Lapu, our largest sample at 108 properties, achieves 40 percent MAPE.\n\n[If pressed: 'Where in the manuscript do these numbers appear?']\nThese are in the Chapter 7 evaluation summary file — chapter7_eval_summary_2026-05-05.json — and Models/model_comparison_per_sqm.csv. They supplement the main Chapter 7 table. The model predicts log of total price following Rosen 1974 hedonic specification; per-sqm accuracy is then derived by back-transforming and dividing by floor area.\n\n[Pivot]\nWe treat Lapu-Lapu's 40 percent MAPE on 108 properties as the most credible single-LGU benchmark. Talisay and Minglanilla, both under 15 properties, are too small to be reliable.",
  );
  // Bar chart on left
  const cities = [
    { name: "Consolacion", mape: 33.3, n: 21, hl: false },
    { name: "Lapu-Lapu", mape: 40.0, n: 108, hl: true },
    { name: "Cebu City", mape: 42.2, n: 86, hl: false },
    { name: "Minglanilla", mape: 47.2, n: 12, hl: false },
    { name: "Mandaue", mape: 51.4, n: 64, hl: false },
    { name: "Talisay", mape: 65.8, n: 13, hl: false },
  ];
  const chartX = 0.6, chartY = 1.7, chartW = 8.0, chartH = 4.8;
  const maxMape = 70;
  cities.forEach((c, i) => {
    const y = chartY + 0.2 + i * 0.72;
    // Label
    s.addText(c.name, {
      x: chartX, y, w: 1.7, h: 0.5,
      fontSize: 13, bold: c.hl, fontFace: FONT_BODY, color: c.hl ? C.NAVY : C.INK,
      valign: "middle",
    });
    // n
    s.addText(`n=${c.n}`, {
      x: chartX + 1.7, y, w: 0.8, h: 0.5,
      fontSize: 11, fontFace: FONT_BODY, color: C.MUTED,
      valign: "middle",
    });
    // Bar background
    s.addShape("rect", { x: chartX + 2.6, y: y + 0.15, w: 4.5, h: 0.3, fill: { color: C.SLATE }, line: { color: C.SLATE } });
    // Bar fill
    const fillW = (c.mape / maxMape) * 4.5;
    s.addShape("rect", { x: chartX + 2.6, y: y + 0.15, w: fillW, h: 0.3, fill: { color: c.hl ? C.AMBER : C.NAVY }, line: { color: c.hl ? C.AMBER : C.NAVY } });
    // Value
    s.addText(`${c.mape}%`, {
      x: chartX + 7.2, y, w: 0.8, h: 0.5,
      fontSize: 13, bold: c.hl, fontFace: FONT_HEAD, color: c.hl ? C.NAVY : C.INK,
      valign: "middle", align: "right",
    });
  });
  s.addText("MAPE by LGU (test set)", {
    x: chartX, y: chartY - 0.05, w: chartW, h: 0.4,
    fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.MUTED, charSpacing: 2,
  });
  // Right interpretation
  s.addShape("rect", { x: 8.9, y: 1.7, w: 0.12, h: 5.2, fill: { color: C.AMBER }, line: { color: C.AMBER } });
  s.addText("MOST CREDIBLE", {
    x: 9.2, y: 1.7, w: 3.6, h: 0.35,
    fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 3,
  });
  s.addText("Lapu-Lapu", {
    x: 9.2, y: 2.1, w: 3.6, h: 0.5,
    fontSize: 22, bold: true, fontFace: FONT_HEAD, color: C.NAVY,
  });
  s.addText("40.0% MAPE on n=108 — largest sample, best-evidenced LGU benchmark.", {
    x: 9.2, y: 2.65, w: 3.6, h: 1.0,
    fontSize: 12, fontFace: FONT_BODY, color: C.INK,
  });
  s.addText("CAUTION", {
    x: 9.2, y: 4.0, w: 3.6, h: 0.35,
    fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.MUTED, charSpacing: 3,
  });
  s.addText(
    "Talisay (n=13) and Minglanilla (n=12): too small for reliable single-LGU estimates. Reported as indicative only.",
    {
      x: 9.2, y: 4.4, w: 3.6, h: 1.5,
      fontSize: 12, fontFace: FONT_BODY, color: C.INK, italic: true,
    },
  );
  s.addText("Source: chapter7_eval_summary_2026-05-05.json", {
    x: 9.2, y: 6.4, w: 3.6, h: 0.4,
    fontSize: 10, fontFace: FONT_BODY, color: C.MUTED,
  });
}

// ============================================================
// SLIDE 25 — Valuation Gap Findings (PLACEHOLDER)
// ============================================================
{
  const s = contentSlide("Valuation Gap: Model Prediction vs. BIR Zonal", { sectionLabel: "RESULTS" });
  s.addNotes(
    "RQ4 — the size of the valuation gap. BIR zonal values systematically lag model predictions in barangays where infrastructure has restructured accessibility. These barangays are candidates for zonal-value revision.",
  );
  // Map placeholder
  s.addShape("roundRect", {
    x: 0.6, y: 1.7, w: 8.0, h: 5.2,
    fill: { color: C.SLATE }, line: { color: C.SLATE_DARK, width: 1 },
    rectRadius: 0.08,
  });
  s.addText("[ DIAGRAM TO ADD ]", {
    x: 0.6, y: 2.0, w: 8.0, h: 0.4,
    fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 3, align: "center",
  });
  s.addText("Valuation Gap Map", {
    x: 0.6, y: 2.4, w: 8.0, h: 0.5,
    fontSize: 18, bold: true, fontFace: FONT_HEAD, color: C.NAVY, align: "center",
  });
  s.addText(
    "Source: build in QGIS using BIR zonal vs. RF model prediction\n\nChoropleth by barangay: (model_pred − bir_zonal_median) / bir_zonal_median\nDarker = larger upward gap (BIR underestimates market)\nNumeric callouts on top 3–5 gap barangays",
    {
      x: 1.0, y: 3.2, w: 7.2, h: 3.5,
      fontSize: 12, italic: true, fontFace: FONT_BODY, color: C.MUTED, align: "center", valign: "top",
    },
  );
  // Right interpretation
  s.addShape("rect", { x: 8.9, y: 1.7, w: 0.12, h: 5.2, fill: { color: C.AMBER }, line: { color: C.AMBER } });
  s.addText("RQ 4 ANSWER", {
    x: 9.2, y: 1.7, w: 3.6, h: 0.35,
    fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 3,
  });
  s.addText(
    [
      { text: "BIR zonal systematically below model prediction in fast-moving barangays.", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.INK, paraSpaceAfter: 14 } },
      { text: "Implication: candidates for LGU zonal-value revision.", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.INK, paraSpaceAfter: 14 } },
      { text: "Directly answers RQ4 — the size of the valuation gap.", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.INK, paraSpaceAfter: 14 } },
    ],
    { x: 9.2, y: 2.1, w: 3.6, h: 4.7, fontFace: FONT_BODY, valign: "top" },
  );
}

// ============================================================
// SECTION DIVIDER 5 → The Tool
// ============================================================
sectionDivider("05", "The Tool", "PART FIVE");

// ============================================================
// SLIDE 26 — Streamlit App: Property Predictor (PLACEHOLDER)
// ============================================================
{
  const s = contentSlide("Streamlit App  ·  Property Predictor", { sectionLabel: "THE TOOL" });
  s.addNotes(
    "Walk the panel through the predictor: user enters property attributes, app returns price_per_sqm, total price, and a SHAP waterfall that shows feature-level contributions to that specific prediction.",
  );
  // Screenshot placeholder
  s.addShape("roundRect", {
    x: 0.6, y: 1.7, w: 8.0, h: 5.2,
    fill: { color: C.SLATE }, line: { color: C.SLATE_DARK, width: 1 },
    rectRadius: 0.08,
  });
  s.addText("[ SCREENSHOT TO ADD ]", {
    x: 0.6, y: 2.0, w: 8.0, h: 0.4,
    fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 3, align: "center",
  });
  s.addText("Streamlit Predictor Page", {
    x: 0.6, y: 2.4, w: 8.0, h: 0.5,
    fontSize: 18, bold: true, fontFace: FONT_HEAD, color: C.NAVY, align: "center",
  });
  s.addText(
    "Source: thesis_main/app/streamlit_app.py\n\nCapture: input form (property type, area, bedrooms,\nbathrooms, city/barangay) + output (price_per_sqm,\ntotal price, SHAP waterfall)",
    {
      x: 1.0, y: 3.2, w: 7.2, h: 3.5,
      fontSize: 12, italic: true, fontFace: FONT_BODY, color: C.MUTED, align: "center", valign: "top",
    },
  );
  // Right details
  s.addText("INPUTS", {
    x: 9.2, y: 1.7, w: 3.6, h: 0.35,
    fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 3,
  });
  s.addText(
    "Property type · Area · Bedrooms · Bathrooms · City / barangay",
    {
      x: 9.2, y: 2.05, w: 3.6, h: 0.7,
      fontSize: 13, fontFace: FONT_BODY, color: C.INK,
    },
  );
  s.addText("OUTPUTS", {
    x: 9.2, y: 2.95, w: 3.6, h: 0.35,
    fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 3,
  });
  s.addText("price_per_sqm · total price · SHAP waterfall (15 bars)", {
    x: 9.2, y: 3.3, w: 3.6, h: 0.7,
    fontSize: 13, fontFace: FONT_BODY, color: C.INK,
  });
  s.addText("DEMO", {
    x: 9.2, y: 4.2, w: 3.6, h: 0.35,
    fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 3,
  });
  s.addShape("roundRect", {
    x: 9.2, y: 4.55, w: 3.6, h: 1.6,
    fill: { color: C.NAVY }, line: { color: C.NAVY },
    rectRadius: 0.06,
  });
  s.addText("Single Detached\n4 br / 2 ba\nCebu City", {
    x: 9.2, y: 4.6, w: 3.6, h: 0.7,
    fontSize: 11, fontFace: FONT_BODY, color: C.SLATE_DARK, align: "center",
  });
  s.addText("PHP 176,661 / sqm\nPHP 17.67 M total", {
    x: 9.2, y: 5.3, w: 3.6, h: 0.85,
    fontSize: 13, bold: true, fontFace: FONT_HEAD, color: C.AMBER, align: "center",
  });
}

// ============================================================
// SLIDE 27 — Streamlit App: Price Surface (PLACEHOLDER)
// ============================================================
{
  const s = contentSlide("Streamlit App  ·  Price Surface", { sectionLabel: "THE TOOL" });
  s.addNotes(
    "The price surface page renders the predicted open-market price across Metro Cebu as a continuous spatial layer. Practitioners can scan relative price levels.",
  );
  // Screenshot placeholder
  s.addShape("roundRect", {
    x: 0.6, y: 1.7, w: 8.0, h: 5.2,
    fill: { color: C.SLATE }, line: { color: C.SLATE_DARK, width: 1 },
    rectRadius: 0.08,
  });
  s.addText("[ SCREENSHOT TO ADD ]", {
    x: 0.6, y: 2.0, w: 8.0, h: 0.4,
    fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 3, align: "center",
  });
  s.addText("Streamlit Price Surface Map", {
    x: 0.6, y: 2.4, w: 8.0, h: 0.5,
    fontSize: 18, bold: true, fontFace: FONT_HEAD, color: C.NAVY, align: "center",
  });
  s.addText(
    "Source: thesis_main/app/streamlit_app.py · Price Surface page\n\nCapture: hex/point layer over Metro Cebu basemap\ncolored by RF predicted price_per_sqm",
    {
      x: 1.0, y: 3.2, w: 7.2, h: 3.5,
      fontSize: 12, italic: true, fontFace: FONT_BODY, color: C.MUTED, align: "center", valign: "top",
    },
  );
  // Right details
  s.addShape("rect", { x: 8.9, y: 1.7, w: 0.12, h: 5.2, fill: { color: C.AMBER }, line: { color: C.AMBER } });
  s.addText("WHAT IT SHOWS", {
    x: 9.2, y: 1.7, w: 3.6, h: 0.35,
    fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 3,
  });
  s.addText(
    [
      { text: "Predicted open-market price across Metro Cebu (open_market scope)", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.INK, paraSpaceAfter: 12 } },
      { text: "Hex / point layer over basemap", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.INK, paraSpaceAfter: 12 } },
      { text: "Spatial scan of relative price levels — including barangays without current listings", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.INK, paraSpaceAfter: 12 } },
      { text: "Backed by deployed Random Forest model (rf_model.pkl)", options: { bullet: { code: "25CF" }, fontSize: 13, color: C.INK, paraSpaceAfter: 12 } },
    ],
    { x: 9.2, y: 2.1, w: 3.6, h: 4.8, fontFace: FONT_BODY, valign: "top" },
  );
}

// ============================================================
// SLIDE 28 — How Practitioners Would Use This
// ============================================================
{
  const s = contentSlide("How Practitioners Would Use This", { sectionLabel: "THE TOOL" });
  s.addNotes(
    "Four user groups. Decision-support layer, not appraisal substitute. The transparency from SHAP at the prediction level is the differentiator over generic listing-aggregator estimates.",
  );
  const users = [
    { num: "$", h: "Banks", d: "First-pass collateral benchmark before full appraisal engagement." },
    { num: "L", h: "LGUs", d: "Barangay-level evidence base for zonal-value revision." },
    { num: "B/S", h: "Buyers / Sellers", d: "Transparent reference price with feature-level explanation (SHAP)." },
    { num: "U", h: "Urban Planners", d: "Accessibility-premium mapping — which infrastructure moves prices, where." },
  ];
  const cardW = 5.85, cardH = 2.3, gapX = 0.35, gapY = 0.4;
  const startX = (W - (cardW * 2 + gapX)) / 2;
  const startY = 1.7;
  users.forEach((u, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = startX + col * (cardW + gapX);
    const y = startY + row * (cardH + gapY);
    card(s, x, y, cardW, cardH, u.h, u.d, { icon: u.num, accentStrip: true });
  });
  s.addText("Decision-support layer  ·  not an appraisal substitute  ·  SHAP transparency at every prediction.", {
    x: 0.6, y: 6.6, w: W - 1.2, h: 0.4,
    fontSize: 14, italic: true, bold: true, fontFace: FONT_BODY, color: C.NAVY, align: "center",
  });
}

// ============================================================
// SECTION DIVIDER 6 → Conclusion
// ============================================================
sectionDivider("06", "Conclusion", "PART SIX");

// ============================================================
// SLIDE 29 — Limitations and Future Work
// ============================================================
{
  const s = contentSlide("Limitations & Future Work", { sectionLabel: "CONCLUSION" });
  s.addNotes(
    "Five limitations, paired with concrete paths forward. Be honest. The single biggest improvement vector is access to deed-of-sale transaction data.",
  );
  const items = [
    { lim: "Asking-price data, not deed-of-sale", path: "Future: Registry of Deeds, BIR eFPS transaction records" },
    { lim: "Cross-sectional snapshot (late 2025)", path: "Quarterly listing snapshots, time-series extension" },
    { lim: "Vacant lots: 76.9% MAPE", path: "Separate land valuation model" },
    { lim: "MCRAI marginal (3% SHAP weight)", path: "Stronger signal expected with transaction-grade data" },
    { lim: "1,200 training rows = binding constraint", path: "Cross-validation with bank ROPA + Naga City scrape" },
  ];
  // Header
  const tableY = 1.7, headerH = 0.45, rowH = 0.85;
  s.addShape("rect", { x: 0.6, y: tableY, w: 5.95, h: headerH, fill: { color: C.NAVY }, line: { color: C.NAVY } });
  s.addText("LIMITATION", {
    x: 0.85, y: tableY, w: 5.7, h: headerH,
    fontSize: 12, bold: true, fontFace: FONT_HEAD, color: C.AMBER, valign: "middle", charSpacing: 3,
  });
  s.addShape("rect", { x: 6.7, y: tableY, w: 6.0, h: headerH, fill: { color: C.AMBER }, line: { color: C.AMBER } });
  s.addText("PATH FORWARD", {
    x: 6.95, y: tableY, w: 5.75, h: headerH,
    fontSize: 12, bold: true, fontFace: FONT_HEAD, color: C.NAVY, valign: "middle", charSpacing: 3,
  });
  items.forEach((it, i) => {
    const y = tableY + headerH + 0.1 + i * (rowH + 0.08);
    s.addShape("roundRect", {
      x: 0.6, y, w: 5.95, h: rowH,
      fill: { color: C.SLATE }, line: { color: C.SLATE },
      rectRadius: 0.04,
    });
    s.addText(it.lim, {
      x: 0.85, y, w: 5.7, h: rowH,
      fontSize: 13, fontFace: FONT_BODY, color: C.NAVY, valign: "middle",
    });
    s.addShape("rightTriangle", {
      x: 6.27, y: y + rowH / 2 - 0.13, w: 0.2, h: 0.26,
      fill: { color: C.AMBER }, line: { color: C.AMBER },
    });
    s.addShape("roundRect", {
      x: 6.7, y, w: 6.0, h: rowH,
      fill: { color: C.WHITE }, line: { color: C.AMBER, width: 1 },
      rectRadius: 0.04,
    });
    s.addText(it.path, {
      x: 6.95, y, w: 5.75, h: rowH,
      fontSize: 13, bold: true, fontFace: FONT_BODY, color: C.NAVY, valign: "middle",
    });
  });
}

// ============================================================
// SLIDE 30 — Conclusion + Thank You
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.NAVY };
  s.addShape("rect", { x: 0.6, y: 0.6, w: 0.8, h: 0.06, fill: { color: C.AMBER }, line: { color: C.AMBER } });
  s.addText("CONCLUSION", {
    x: 0.6, y: 0.75, w: 12.0, h: 0.5,
    fontSize: 13, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 4,
  });
  s.addText(
    "Metro Cebu's property market is moving faster than any existing benchmark can track.\n\nThis thesis delivers a geospatially grounded, machine-learning-powered decision-support tool — transparent, reproducible, and locally calibrated.",
    {
      x: 0.6, y: 1.3, w: 12.0, h: 2.7,
      fontSize: 26, bold: true, fontFace: FONT_HEAD, color: C.WHITE, align: "left", valign: "top",
    },
  );
  s.addText("KEY CONTRIBUTIONS", {
    x: 0.6, y: 4.2, w: 12.0, h: 0.4,
    fontSize: 11, bold: true, fontFace: FONT_HEAD, color: C.AMBER, charSpacing: 3,
  });
  const kc = [
    "First property-level ML valuation grounded in Metro Cebu's open market",
    "Custom MCRAI accessibility framework — derived from but rebuilt beyond Project OHANA",
    "Deployed Streamlit tool with feature-level SHAP at the prediction level",
    "Methodologically aligned with IVS 2025 Market Value definition",
  ];
  s.addText(
    kc.map((t) => ({ text: t, options: { bullet: { code: "25CF" }, fontSize: 13, color: C.SLATE_DARK, paraSpaceAfter: 5 } })),
    { x: 0.85, y: 4.6, w: 12.0, h: 1.6, fontFace: FONT_BODY, valign: "top" },
  );
  s.addShape("rect", { x: 0.6, y: 6.5, w: 12.1, h: 0.02, fill: { color: C.AMBER }, line: { color: C.AMBER } });
  s.addText("Thank you. I welcome your questions.", {
    x: 0.6, y: 6.65, w: 8.0, h: 0.7,
    fontSize: 22, bold: true, italic: true, fontFace: FONT_HEAD, color: C.AMBER,
    valign: "middle",
  });
  s.addText("Nico Estreba  ·  May 9, 2026", {
    x: 8.7, y: 6.65, w: 4.0, h: 0.7,
    fontSize: 12, fontFace: FONT_BODY, color: C.SLATE_DARK,
    align: "right", valign: "middle",
  });
  s.addNotes(
    "Closing line:\n\nMetro Cebu's property market is moving faster than any existing benchmark can track. This thesis delivers a geospatially grounded, machine-learning-powered decision-support tool — transparent, reproducible, and locally calibrated. It does not replace appraisal judgment. It gives practitioners a defensible starting point.\n\nThank you. I welcome your questions.",
  );
}

// ============================================================
// Save
// ============================================================
const outPath = path.join(__dirname, "defense_2026-05-09.pptx");
pres.writeFile({ fileName: outPath }).then((f) => {
  console.log("Wrote:", f);
});
