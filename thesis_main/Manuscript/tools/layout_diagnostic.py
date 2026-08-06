#!/usr/bin/env python3
"""Layout diagnostic for the thesis manuscript.

Reports two classes of layout problems so we can work from a concrete list
instead of eyeballing the PDF:

  1. Pages with excessive trailing whitespace at the bottom of the text block
     (the tell-tale sign of a float that got bumped, leaving a gap).
  2. Overfull / underfull box warnings from the pdflatex log (text or figures
     spilling past the margins, or badly stretched lines).

Whitespace is measured against the APA text block: top margin 1in, bottom
margin 1in on letter paper (11in = 792pt tall), so the bottom edge of the text
block sits 720pt from the top. Content below that (page-number footer) is
ignored. A page whose lowest real content leaves more than THRESHOLD_IN inches
of blank space above the bottom margin is flagged.

Chapter-final and section-final pages are legitimately short; the report notes
these so they can be skipped. Usage:

    python3 tools/layout_diagnostic.py [main.pdf] [main.log]
"""
import sys
import re
from pathlib import Path

import pdfplumber

# APA text block geometry (points; 1in = 72pt).
PAGE_HEIGHT = 792.0            # letter, 11in
BOTTOM_MARGIN = 72.0          # 1in
TOP_MARGIN = 72.0             # 1in
TEXT_BOTTOM = PAGE_HEIGHT - BOTTOM_MARGIN   # 720pt from top
THRESHOLD_IN = 1.5            # flag gaps larger than this many inches


def page_content_bottom(page):
    """Lowest content edge on the page (distance from top), ignoring the
    page-number footer that sits inside the bottom margin."""
    bottoms = []
    for kind in ("chars", "images", "lines", "rects", "curves"):
        for obj in getattr(page, kind, []):
            b = obj.get("bottom")
            if b is None:
                continue
            # ignore anything sitting in the bottom margin (footer/page no.)
            if b <= TEXT_BOTTOM + 2:
                bottoms.append(b)
    return max(bottoms) if bottoms else None


def starts_new_section(page):
    """True if a page begins a new chapter/major section — its first body line
    (after the running head) is a short, un-punctuated heading. Such headings
    are \\clearpage'd, so the PREVIOUS page is legitimately short and its gap is
    a structural break, not wasted space."""
    text = page.extract_text() or ""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) < 2:
        return False
    heading = lines[1]  # lines[0] is the running head
    return len(heading) < 40 and not heading.endswith((".", ",", ";", ":"))


def scan_whitespace(pdf_path):
    """Return (actionable, structural) gap lists. A gap is 'structural' — and
    thus expected — if the page ends a chapter/section (next page starts a new
    one) or lives in the front matter. Everything else is actionable."""
    actionable, structural = [], []
    with pdfplumber.open(pdf_path) as pdf:
        pages = pdf.pages
        for i, page in enumerate(pages, start=1):
            bottom = page_content_bottom(page)
            if bottom is None:
                continue  # blank page
            gap_in = round((TEXT_BOTTOM - bottom) / 72.0, 2)
            if gap_in <= THRESHOLD_IN:
                continue
            nxt = pages[i] if i < len(pages) else None
            is_break = (nxt is not None and starts_new_section(nxt))
            (structural if is_break else actionable).append((i, gap_in))
    return actionable, structural


BOX_RE = re.compile(
    r"^(Overfull|Underfull) \\([hv])box .*?(?:\bin paragraph|\bdetected|\bhas occurred|\bwhile)",
)


def scan_log(log_path):
    """Collect Overfull/Underfull box warnings with the page they land on.
    pdflatex prints '[N]' as it ships out page N, so we track the running page
    number and attribute each warning to the most recently opened page."""
    if not Path(log_path).exists():
        return []
    text = Path(log_path).read_text(errors="replace")
    warnings = []
    page = 1
    for line in text.splitlines():
        # crude page tracking: count '[' that open a shipped page
        for _ in re.findall(r"\[\d+", line):
            page += 1
        m = re.match(r"^(Overfull|Underfull) \\([hv])box \(([\d.]+)pt", line)
        if m:
            kind, box, amt = m.group(1), m.group(2), float(m.group(3))
            warnings.append((page, kind, f"\\{box}box", amt, line.strip()[:90]))
    return warnings


def main():
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "main.pdf"
    log_path = sys.argv[2] if len(sys.argv) > 2 else "main.log"

    actionable, structural = scan_whitespace(pdf_path)
    print(f"=== ACTIONABLE gaps > {THRESHOLD_IN} in  ({len(actionable)} pages) ===")
    print("   (mid-chapter whitespace — a float or table likely got bumped)")
    for pg, gap in actionable:
        print(f"  page {pg:>3}:  {gap} in blank at bottom")
    if not actionable:
        print("  (none)")

    print(f"\n=== Structural gaps (expected — chapter/section ends, front matter): "
          f"{len(structural)} pages ===")
    print("  " + ", ".join(f"p{pg}" for pg, _ in structural) if structural else "  (none)")

    boxes = scan_log(log_path)
    overfull = [b for b in boxes if b[1] == "Overfull"]
    print(f"\n=== Overfull boxes ({len(overfull)}) — content past the margin ===")
    for pg, kind, box, amt, _ in sorted(overfull, key=lambda x: -x[3])[:40]:
        print(f"  ~page {pg:>3}:  {box} overfull by {amt:.1f}pt")
    if not overfull:
        print("  (none)")

    print(f"\nSummary: {len(actionable)} actionable gaps, "
          f"{len(structural)} structural gaps, {len(overfull)} overfull boxes")


if __name__ == "__main__":
    main()
