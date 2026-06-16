# Metro Cebu Valuation Webapp Prototype

This is a separate JavaScript/TypeScript proof of concept for replacing the Streamlit UI in phases.

The current prototype rebuilds the Market Map and Price Surface with static HTML controls and TypeScript state handling. It uses exported JSON/GeoJSON from the existing thesis CSV and GeoJSON files, so the current Streamlit app remains untouched.

## Run

**Quickest:** double-click `run.command` (or `./run.command` in a terminal). It
starts the FastAPI backend and the Vite frontend together, opens the browser, and
stops both on Ctrl+C. Reuses an already-running backend on port 8000 if present.
Pass `--export` to force a fresh data export first.

Manual, if you prefer two terminals —

Static frontend (Market Map + Price Surface):

```bash
npm install
npm run export:data
npm run dev
```

Property Predictor — also start the Python inference backend (separate terminal):

```bash
pip install -r api/requirements.txt   # into the same env that trained the models
npm run api                            # uvicorn on 127.0.0.1:8000
```

Then open the local Vite URL printed by the dev server. Vite proxies `/api` to
the backend, so the Predictor page works with no extra config.

## Architecture

- **Frontend (this folder):** Vite + TypeScript + Leaflet. All three views — Market
  Map, Price Surface, Predictor — render client-side. Map interaction never hits Python.
- **Backend (`api/`):** FastAPI service that imports the thesis model code from
  `../app/lib` **unchanged** (same pickles, ABT nearest-neighbour lookup, feature
  builder, RandomForest inference, SHAP). It sets `WEBAPP_API=1` so the shared
  `lib._cache` shim swaps Streamlit's cache decorators for `functools` — that is the
  only change to `lib`, and `streamlit run` still works exactly as before.

Endpoints: `GET /api/health`, `GET /api/resolve?lat&lon` (city + auto BIR estimate on
pin drop), `POST /api/predict` (full prediction + price drivers).

## Scope

- Included: Market Map, Price Surface, and a live Property Predictor (pin-drop →
  predicted price/sqm, total, uncertainty range, and SHAP price drivers when SHAP is
  installed in the backend env).
- The Predictor needs the backend running. Without `shap` installed, predictions still
  return; the drivers panel shows a "SHAP unavailable" note (matching the Streamlit app).

The Streamlit app remains the source of truth and is untouched by this prototype.
