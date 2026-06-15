# Lamudi Playwright Subproject

Isolated browser-automation for scraping Lamudi (`lamudi.com.ph`) and for interactive
navigation/screenshots. Everything Playwright-related lives here so it stays separate from the
rest of the thesis pipeline.

## Why this exists

The legacy scrapers in `../Data/webscraping-lamudi/` fetch with `requests` (+ `curl` fallback).
Neither runs JavaScript, so they cannot pass Lamudi's **DataDome-class WAF**. Observed behavior:
the first ~2–3 requests in a burst succeed, then every page returns the `window.gokuProps`
challenge wall. The IP is **not** banned — it is a rate/behavior-based JS challenge that only a
real browser can solve.

A persistent Playwright Chromium context solves the challenge once, holds the DataDome cookie,
and (run **sequentially**, slowly, **headed**) keeps fetching past page 3.

## Anti-WAF rules (do not regress these)

- **One persistent browser context** for a whole run — never a fresh context per page.
- **Sequential only** — no threads/concurrency. Concurrency is what trips the burst WAF.
- **Headed by default** (`--headless` is opt-in). Headless is easier for DataDome to fingerprint.
- **Human pacing**: 4–8s between navigations.
- **Warm up** on `https://www.lamudi.com.ph/` first so the challenge resolves before scraping.

## Layout

```
browser.py            LamudiBrowser: launch, persistent context + stealth, warm_up(),
                      fetch(url) -> html (challenge-aware retry), screenshot(url, path)
parse.py              JSON-LD / area / type / lot parsing (ported from legacy scrape_properties.py)
scrape_index.py       Index discovery -> writes property_links.txt
scrape_properties.py  Sequential detail scraper -> data/lamudi_scraped.csv
data/                 Staging output. NOT the canonical CSV.
screenshots/          Debug + on-request screenshots.
```

## Running (in your own terminal — residential connection)

```bash
PY="../../.venv/bin/python"   # the "16 Thesis/.venv" interpreter
"$PY" -m playwright install chromium      # one-time browser binary

# Validation run (small) then scale up:
"$PY" scrape_index.py --max-pages 5
"$PY" scrape_properties.py
```

## Output and merge

`scrape_properties.py` writes to `data/lamudi_scraped.csv` (15-column schema matching the
canonical file). It does **not** touch `../Data/webscraping-lamudi/lamudi_cebu_full.csv`. A
separate merge step appends only new-URL rows to the canonical CSV and then re-runs the
enrichment chain (`compute_road_distances` -> `compute_hansen_scores` ->
`prepare_stratified_abt` -> `run_models_stratified`). See Decision 35e.
