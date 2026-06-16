---
title: Metro Cebu Residential Valuation
emoji: 🏙️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Metro Cebu Residential Valuation

A Vite + TypeScript + Leaflet frontend with a FastAPI inference backend
(stratified Random Forest per-sqm models, GroupKFold-evaluated). It provides:

- **Market Map** — scraped listings (open-market ABT) with filters, POIs, and per-LGU stats.
- **Price Surface** — barangay-level predicted price choropleth per archetype, with
  hover/click amenity (MCRAI) and accessibility breakdowns.
- **Property Predictor** — drop a pin to get a predicted price/sqm with a model
  uncertainty range, SHAP price drivers, and the actual ABT listings within 1 km.

The whole app runs as one container: FastAPI serves `/api/*` (inference) and the
built static frontend at `/`, so there is no CORS or separate host to manage.

> Research prototype for a Metro Cebu real-estate valuation thesis. Not IAAO-compliant;
> decision-support estimates only.
