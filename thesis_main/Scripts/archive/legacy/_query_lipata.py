import os, googlemaps
from dotenv import load_dotenv
load_dotenv("thesis_main/.env")
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

queries = [
    "Lipata Minglanilla Cebu",
    "San Nicolas de Tolentino Parish Lipata Minglanilla",
    "Lipata Barangay Hall Minglanilla",
    "Gaisano Grand Mall Minglanilla",
    "Minglanilla Town Plaza",
    "Minglanilla poblacion Cebu",
]
for q in queries:
    results = gmaps.places(query=q, location=(10.183, 123.820), radius=5000)
    r = results.get("results", [])
    if r:
        loc = r[0]["geometry"]["location"]
        print(f"{q}")
        print(f"  -> {r[0]['name']}  ({loc['lat']}, {loc['lng']})")
        print(f"     {r[0].get('formatted_address', '')}")
    else:
        print(f"{q} -> NO RESULTS")
