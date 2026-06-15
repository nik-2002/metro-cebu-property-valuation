"""Shared dashboard styling for the rail · map · panel pages.

The Market Map established the look (dark-blue input rail, white map + panel columns,
brand block, stat cards). The Property Predictor reuses it here so both pages stay
visually consistent. Market Map still inlines its own copy for now; this module is the
shared source going forward.
"""

import streamlit as st


_DASHBOARD_CSS = """
<style>
:root {
    --ink:#14233B;
    --muted:#6B7280;
    --line:#E6EAF0;
    --rail:#053B68;
    --rail-deep:#052F55;
    --brand:#F7C80E;
    --accent:#E23E57;
    --blue:#0B4F83;
}
.stApp { background:#F4F7FB; }
.main .block-container,
[data-testid="stMainBlockContainer"] {
    padding:3.5rem 0 0 !important;
    max-width:100% !important;
    width:100% !important;
    margin:0 !important;
}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
    gap:0 !important;
}
[data-testid="stHorizontalBlock"] { gap:0 !important; }
[data-testid="column"] {
    padding-left:0 !important;
    padding-right:0 !important;
}
[data-testid="stHorizontalBlock"] > div:nth-child(1) {
    background:linear-gradient(180deg,var(--rail) 0%,var(--rail-deep) 100%);
    min-height:calc(100vh - 3.5rem);
    padding:0.75rem 0.9rem 0.65rem;
    border-radius:0;
    box-shadow:inset -1px 0 0 rgba(255,255,255,0.08);
}
[data-testid="stHorizontalBlock"] > div:nth-child(2) {
    background:#FFFFFF;
    padding:0 0.55rem 0.55rem;
    min-height:calc(100vh - 3.5rem);
    border-left:1px solid #DDE5EE;
    border-right:1px solid #DDE5EE;
}
[data-testid="stHorizontalBlock"] > div:nth-child(3) {
    background:#FFFFFF;
    padding:0.85rem 0.75rem 0.55rem;
    min-height:calc(100vh - 3.5rem);
}
/* Guard: the rail/panel styling above must apply only to the top-level layout
   columns. Nested st.columns (e.g. bedrooms · bathrooms inside the rail) form
   their own stHorizontalBlock and would otherwise inherit the full-viewport
   min-height + rail gradient. Reset any horizontal block nested in a column. */
[data-testid="stColumn"] [data-testid="stHorizontalBlock"] > div {
    background:transparent !important;
    min-height:0 !important;
    padding:0 !important;
    border:none !important;
    box-shadow:none !important;
}
[data-testid="stHorizontalBlock"] > div:nth-child(1) label,
[data-testid="stHorizontalBlock"] > div:nth-child(1) .stMarkdown,
[data-testid="stHorizontalBlock"] > div:nth-child(1) .stCaption,
[data-testid="stHorizontalBlock"] > div:nth-child(1) p {
    color:rgba(255,255,255,0.80) !important;
}
[data-testid="stHorizontalBlock"] > div:nth-child(1) [data-baseweb="select"] > div,
[data-testid="stHorizontalBlock"] > div:nth-child(1) [data-baseweb="tag"] {
    background:rgba(255,255,255,0.12) !important;
    border-color:rgba(255,255,255,0.16) !important;
    color:#FFFFFF !important;
    border-radius:7px !important;
}
[data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="stSelectbox"],
[data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="stMultiSelect"] {
    margin-bottom:0.75rem;
}
[data-testid="stHorizontalBlock"] > div:nth-child(1) hr {
    border-color:rgba(255,255,255,0.12) !important;
    margin:1rem 0 !important;
}
.brand-block {
    display:flex;
    align-items:center;
    gap:0.75rem;
    padding-bottom:0.9rem;
    border-bottom:1px solid rgba(255,255,255,0.11);
    margin-bottom:1rem;
}
.brand-name { color:#FFFFFF; font-size:0.95rem; font-weight:800; line-height:1.05; }
.brand-sub { color:#F7C80E; font-size:0.72rem; font-weight:700; margin-top:0.1rem; }
.rail-note {
    color:rgba(255,255,255,0.54);
    font-size:0.72rem;
    line-height:1.35;
    margin:0.65rem 0 0.85rem;
}
.rail-footer {
    color:rgba(255,255,255,0.48);
    font-size:0.72rem;
    border-top:1px solid rgba(255,255,255,0.11);
    margin-top:1rem;
    padding-top:0.85rem;
}
.rail-title {
    font-size:0.69rem;
    font-weight:800;
    letter-spacing:0.08em;
    color:rgba(255,255,255,0.62);
    text-transform:uppercase;
    margin:0.7rem 0 0.3rem;
}
.rail-title.dark { color:#8A94A6; }
.rail-pill {
    display:inline-block;
    background:rgba(247,200,14,0.16);
    border:1px solid rgba(247,200,14,0.35);
    color:#FFFFFF;
    font-size:0.92rem;
    font-weight:800;
    padding:0.5rem 0.8rem;
    border-radius:8px;
}
.rail-readout {
    color:#FFFFFF;
    font-size:1.05rem;
    font-weight:800;
}
.rail-readout small { color:rgba(255,255,255,0.6); font-weight:600; font-size:0.72rem; }
.map-topbar {
    min-height:56px;
    display:grid;
    grid-template-columns:minmax(170px,0.95fr) auto minmax(160px,1fr);
    align-items:center;
    gap:1rem;
    border-bottom:1px solid var(--line);
    margin:0 -0.55rem 0.65rem;
    padding:0 1rem;
}
.map-title { color:var(--ink); font-size:1.2rem; font-weight:800; line-height:1.18; }
.region-pill {
    border-radius:999px;
    background:#EAF0F6;
    color:#2A5274;
    font-size:0.78rem;
    font-weight:800;
    padding:0.58rem 0.95rem;
    white-space:nowrap;
}
.region-pill.empty { background:#FBEAEC; color:#A23B47; }
.map-caption-row {
    display:flex;
    align-items:center;
    justify-content:space-between;
    margin-bottom:0.55rem;
}
.panel-h {
    font-size:1.02rem;
    font-weight:800;
    color:var(--ink);
    margin-bottom:0.1rem;
}
.panel-sub {
    font-size:0.74rem;
    color:#8791A0;
    margin-bottom:0.75rem;
}
.metric-grid {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:0.65rem;
    margin:0.65rem 0 1rem;
}
.stat-card {
    background:#FBFCFE;
    border:1px solid #EEF2F7;
    border-radius:8px;
    padding:0.8rem;
    min-height:82px;
    box-shadow:0 1px 4px rgba(15,23,42,0.04);
}
.stat-card.warm { background:#FFF7F0; }
.stat-card.cool { background:#F0F7FF; }
.stat-num { font-size:1.25rem; font-weight:850; color:#D43D4D; line-height:1.1; }
.stat-card.cool .stat-num { color:#2563EB; }
.stat-lbl { font-size:0.69rem; color:#6B7280; margin-top:0.25rem; }
.driver-panel {
    border-top:1px solid #E6EAF0;
    margin-top:0.9rem;
    padding-top:0.85rem;
}
.driver-row {
    margin:0.55rem 0;
}
.driver-top {
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    gap:0.6rem;
    color:#334155;
    font-size:0.72rem;
    line-height:1.2;
}
.driver-label {
    max-width:72%;
}
.driver-impact {
    flex:0 0 auto;
    font-weight:800;
}
.driver-track {
    height:5px;
    border-radius:999px;
    background:#EEF2F7;
    overflow:hidden;
    margin-top:0.25rem;
}
.driver-bar {
    height:100%;
    border-radius:999px;
}
.driver-note {
    color:#8791A0;
    font-size:0.66rem;
    line-height:1.3;
    margin-top:0.5rem;
}

/* Segmented control rendered as a chip group inside the dark input rail. */
[data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="stButtonGroup"] {
    flex-wrap:wrap;
    gap:6px;
}
[data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid^="stBaseButton-segmented_control"] {
    background:rgba(255,255,255,0.10);
    border:1px solid rgba(255,255,255,0.18);
    border-radius:8px;
    padding:0.34rem 0.7rem;
    min-height:0;
}
[data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid^="stBaseButton-segmented_control"] p {
    color:#FFFFFF !important;
    font-weight:700;
    font-size:0.82rem;
}
[data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="stBaseButton-segmented_controlActive"] {
    background:var(--brand);
    border-color:var(--brand);
}
[data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="stBaseButton-segmented_controlActive"] p {
    color:#08243F !important;
}
/* Keep text + number fields on the dark rail light and legible. */
[data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="stTextInput"] input,
[data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="stNumberInputField"] {
    background:#FFFFFF;
    color:#14233B !important;
    -webkit-text-fill-color:#14233B;
}
[data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="stTextInput"] input::placeholder {
    color:#9AA3AF !important;
    -webkit-text-fill-color:#9AA3AF;
}

@media (max-width: 1100px) {
    .map-topbar { grid-template-columns:1fr; align-items:start; padding:0.9rem 1rem; }
    [data-testid="stHorizontalBlock"] > div:nth-child(1),
    [data-testid="stHorizontalBlock"] > div:nth-child(2),
    [data-testid="stHorizontalBlock"] > div:nth-child(3) {
        min-height:auto;
    }
}
</style>
"""


def inject_dashboard_css() -> None:
    """Inject the shared rail · map · panel dashboard styling into the page."""
    st.markdown(_DASHBOARD_CSS, unsafe_allow_html=True)
