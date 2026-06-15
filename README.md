# Metro Cebu Residential Valuation Thesis

This repository contains the code, manuscript materials, and supporting analysis for a data science thesis on residential property valuation in Metro Cebu, Philippines.

The project builds a predictive and prescriptive decision support workflow for open-market residential valuation, using geospatial features, market-segmented property data, accessibility measures, and tree-based modeling.

## Project Structure

- `thesis_main/Scripts/` - data preparation, feature engineering, EDA, and modeling scripts.
- `thesis_main/app/` - Streamlit app for market maps, price surfaces, and property prediction.
- `thesis_main/Data/` - raw, processed, and geospatial datasets used during thesis development.
- `thesis_main/Models/` - local trained model outputs and model comparison summaries.
- `thesis_main/Manuscript/` - LaTeX thesis manuscript files and supporting diagrams.
- `thesis_main/Literature/` - literature notes, source reviews, and research synthesis.
- `thesis_main/reference/` - decision logs, project snapshots, and methodology references.
- `thesis_main/Presentations/` - defense, colloquium, and methodology presentation materials.

## Environment Setup

Create a local Python environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Some scripts use a Google Maps API key for geocoding and POI collection. Keep credentials in a local `.env` file:

```bash
GOOGLE_MAPS_API_KEY=your_key_here
```

Do not commit `.env`.

## Streamlit App

From the repository root:

```bash
source .venv/bin/activate
streamlit run thesis_main/app/streamlit_app.py
```

## GitHub Notes

This project includes data files, local model outputs, generated LaTeX artifacts, and geospatial outputs. The `.gitignore` is set up to keep future virtual environments, caches, secrets, generated LaTeX files, and local binary model artifacts out of Git.

Before making the GitHub repository public, review whether the datasets and scraped property listings can be shared. A private GitHub repository is the safer default for thesis work involving collected listings or API-derived data.

