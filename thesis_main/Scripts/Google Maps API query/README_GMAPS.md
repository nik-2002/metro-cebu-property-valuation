Google Maps fetch script
========================

This folder contains `gmaps_fetch_mahayag.py`, a small script to fetch nearby places
around "Mahayag, Zamboanga Peninsula, Philippines" using the Google Maps Web APIs.

Quick start
-----------

1. Create and export a Google Maps API key with Geocoding and Places APIs enabled:

```bash
export GOOGLE_MAPS_API_KEY=your_key_here
```

2. Install dependencies (preferably in a virtualenv):

```bash
pip install -r requirements.txt
```

3. Run the script (example):

```bash
python "Scripts/gmaps_fetch_mahayag.py" --radius 5000 --output "cache/gmaps_mahayag.json"
```

The script will save a JSON array of place objects with `epsg3857` coordinates and a `geojson` Point.
