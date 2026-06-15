from __future__ import annotations

import streamlit as st

_PAGES = [
    ("Home", "/"),
    ("Market Map", "/Market_Map"),
    ("Price Surface", "/Price_Surface"),
    ("Property Predictor", "/Property_Predictor"),
]

_CSS = """
<style>
/* ── Hide Streamlit chrome ── */
header[data-testid="stHeader"]   { display: none !important; }
[data-testid="stToolbar"]         { display: none !important; }
[data-testid="stSidebar"]         { display: none !important; }
[data-testid="stSidebarNav"]      { display: none !important; }
[data-testid="collapsedControl"]  { display: none !important; }

/* ── Top navigation bar ── */
.mcr-nav {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 56px;
    background: #ffffff;
    border-bottom: 1px solid #E5E7EB;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    display: flex;
    align-items: center;
    padding: 0 2rem;
    gap: 2rem;
    z-index: 9999;
}
.mcr-nav .brand {
    font-size: 0.9rem;
    font-weight: 700;
    color: #111827;
    letter-spacing: -0.01em;
    margin-right: 0.5rem;
    white-space: nowrap;
}
.mcr-nav a {
    font-size: 0.875rem;
    font-weight: 500;
    color: #6B7280;
    text-decoration: none;
    padding: 4px 0;
    border-bottom: 2px solid transparent;
    white-space: nowrap;
}
.mcr-nav a:hover { color: #111827; }
.mcr-nav a.active {
    color: #C8860A;
    border-bottom: 2px solid #C8860A;
}

/* ── Push page content below navbar ── */
.main .block-container {
    padding-top: 4.5rem !important;
}
</style>
"""


def render_navbar(active: str = "") -> None:
    links = ""
    for label, href in _PAGES:
        cls = "active" if label.lower() == active.lower() else ""
        links += f'<a href="{href}" class="{cls}" target="_self">{label}</a>\n'

    # NOTE: no leading whitespace on the <nav> tag — 4+ spaces would make
    # Streamlit's Markdown parser treat the block as a code fence.
    html = (
        _CSS
        + '\n<nav class="mcr-nav">\n'
        + '<span class="brand">Metro Cebu Estimator</span>\n'
        + links
        + "\n</nav>\n"
    )
    st.markdown(html, unsafe_allow_html=True)
