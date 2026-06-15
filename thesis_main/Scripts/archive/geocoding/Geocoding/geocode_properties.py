import os
import time
import glob
import pandas as pd
import googlemaps
from dotenv import load_dotenv

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "Data")
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__)) # Save to Scripts/Geocoding

# Load the .env file from the thesis_main directory
load_dotenv(os.path.join(BASE_DIR, ".env"))

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# Replace this with your actual Google Maps API Key or set the GOOGLE_MAPS_API_KEY environment variable.
API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "YOUR_API_KEY_HERE")

# Files
PROCESSED_CEBU = os.path.join(DATA_DIR, "processed_properties_cebu.csv")
BDO_EXCEL = glob.glob(os.path.join(DATA_DIR, "BDO_Data", "BDO-Properties-*.xlsx"))
WEB_SCRAPED = glob.glob(os.path.join(DATA_DIR, "web_scraping", "*.csv"))

# Checkpoint frequency (save every N records)
CHECKPOINT_EVERY = 50

# ==============================================================================
# INIT GOOGLE MAPS
# ==============================================================================
if API_KEY == "YOUR_API_KEY_HERE" or not API_KEY:
    print("ERROR: Please set a valid Google Maps API Key.")
    exit(1)

gmaps = googlemaps.Client(key=API_KEY)

def geocode_address(address):
    """Hits the Google Maps Geocoding API."""
    try:
        # Request geocoding
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            formatted_address = geocode_result[0]['formatted_address']
            return location['lat'], location['lng'], formatted_address
        return None, None, None
    except Exception as e:
        print(f"  [!] Error geocoding '{address}': {e}")
        return None, None, None

def process_dataframe(df, address_col, output_filename, context="Cebu, Philippines"):
    """Iterates through DataFrame, geocodes addresses, and saves checkpoints."""
    print(f"\n--- Processing {output_filename} ({len(df)} rows) ---")
    
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # Load checkpoint if exists
    if os.path.exists(output_path):
        print(f"Found existing output file. Resuming from {output_path}...")
        df_existing = pd.read_csv(output_path)
        # Update our dataframe with previously processed results
        df = df.set_index(df.columns[0]).combine_first(df_existing.set_index(df_existing.columns[0])).reset_index()
    else:
        df['latitude'] = pd.NA
        df['longitude'] = pd.NA
        df['gmaps_formatted_address'] = pd.NA

    # Find rows that need geocoding
    unprocessed = df[df['latitude'].isna() | (df['latitude'] == '')]
    print(f"{len(unprocessed)} rows need geocoding.")

    count = 0
    for idx, row in unprocessed.iterrows():
        raw_address = str(row[address_col])
        if pd.isna(row[address_col]) or raw_address.strip() == "":
            continue
            
        # Append context for better accuracy
        full_address = raw_address
        # Only append specific context words if they are missing
        for word in context.split(", "):
            if word not in full_address:
                full_address += f", {word}"

        print(f"[{count+1}/{len(unprocessed)}] Geocoding: {full_address[:50]}...", end=" ")
        
        lat, lng, formatted_addr = geocode_address(full_address)
        
        if lat and lng:
            df.at[idx, 'latitude'] = lat
            df.at[idx, 'longitude'] = lng
            df.at[idx, 'gmaps_formatted_address'] = formatted_addr
            print(f"OK ({lat}, {lng})")
        else:
            print("FAILED")
            
        count += 1
        
        # Checkpoint saving
        if count % CHECKPOINT_EVERY == 0:
            df.to_csv(output_path, index=False)
            print(f"  -> Checkpoint saved to {output_path}")
            
    # Final save
    df.to_csv(output_path, index=False)
    print(f"Completed mapping. Final results saved to {output_path}")

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
if __name__ == "__main__":
    print("Starting Geocoding Pipeline using Google Maps API")
    print("Output directory:", OUTPUT_DIR)
    
    # 1. Process processed_properties_cebu.csv
    if os.path.exists(PROCESSED_CEBU):
        df_cebu = pd.read_csv(PROCESSED_CEBU)
        if 'Address' in df_cebu.columns:
            process_dataframe(df_cebu, 'Address', 'geocoded_processed_properties_cebu.csv')
    
    # 2. Process BDO Data
    if BDO_EXCEL:
        print(f"\nReading BDO data from {BDO_EXCEL[0]}")
        # Need header=3 based on previous inspection
        df_bdo = pd.read_excel(BDO_EXCEL[0], header=3) 
        # Filter for Cebu
        df_bdo_cebu = df_bdo[df_bdo['Property Address'].str.contains('Cebu', case=False, na=False)].copy()
        if not df_bdo_cebu.empty:
            process_dataframe(df_bdo_cebu, 'Property Address', 'geocoded_bdo_properties_cebu.csv')
            
    # 3. Process Web Scraped Data
    for file_path in WEB_SCRAPED:
        df_ws = pd.read_csv(file_path)
        filename = os.path.basename(file_path)
        
        # Determine address column
        cols = df_ws.columns.tolist()
        loc_col = None
        for col in ['Location', 'Address', 'Property Address', 'address', 'location']:
            if col in cols:
                loc_col = col
                break
                
        if loc_col and not df_ws.empty:
            process_dataframe(df_ws, loc_col, f"geocoded_{filename}", context="Philippines")
        else:
            print(f"\nSkipping {filename}: No recognizable location column found or file is empty.")

    print("\nAll tasks finished.")
