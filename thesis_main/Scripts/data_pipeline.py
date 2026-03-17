import pandas as pd
import re
import os

# Paths
RAW_DATA_PATH = "Data/BDO_Data/BDO-Properties-as-of-11.18.25_03709b93-6342-41c1-b4f6-b2103ef49741 (1).xlsx"
PROCESSED_DATA_PATH = "Data/processed_properties_cebu.csv"

def parse_description(desc):
    """
    Parses property description to extract Bedrooms (BR) and Bathrooms (TB/T&B).
    """
    if pd.isna(desc):
        return None, None
    
    # Regex for Bedrooms
    br_match = re.search(r'(\d+)\s*(?:BR|Bedroom)', str(desc), re.IGNORECASE)
    br_count = int(br_match.group(1)) if br_match else None
    
    # Regex for Bathrooms
    tb_match = re.search(r'(\d+)\s*(?:TB|T&B|Bathroom)', str(desc), re.IGNORECASE)
    tb_count = int(tb_match.group(1)) if tb_match else None
    
    return br_count, tb_count

def main():
    print("🚀 Starting Data Pipeline...")
    
    # Load raw data (no header to handle the BDO Excel structure)
    if not os.path.exists(RAW_DATA_PATH):
        print(f"❌ File not found: {RAW_DATA_PATH}")
        return

    df = pd.read_excel(RAW_DATA_PATH, header=None)
    
    # Mapping based on inspection:
    # 0: Region, 1: City, 2: Segment, 3: Property Type, 4: Project Name, 
    # 5: Address, 6: Lot Area, 7: Floor Area, 8: Price, 9: Description
    
    columns = {
        0: 'Region',
        1: 'City',
        2: 'Segment',
        3: 'PropertyType',
        4: 'ProjectName',
        5: 'Address',
        6: 'LotArea',
        7: 'FloorArea',
        8: 'Price',
        9: 'Description'
    }
    
    df = df.rename(columns=columns)
    
    # Remove header rows if any (usually the first few rows in BDO excels)
    # We look for rows where 'Price' or 'Address' is not the string 'Price' or 'Address'
    df = df[df['Price'].apply(lambda x: isinstance(x, (int, float)))]
    
    print(f"📊 Total properties loaded: {len(df)}")
    
    # Filter for Cebu
    # BDO lists 'City' as 'Cebu City', 'Mandaue City', etc.
    # We'll filter for anything in Cebu province or specific cities
    cebu_df = df[
        df['City'].astype(str).str.contains("Cebu", case=False, na=False) |
        df['Address'].astype(str).str.contains("Cebu", case=False, na=False)
    ].copy()
    
    print(f"✅ Filtered for Cebu: {len(cebu_df)} properties found.")
    
    # Apply Parsing
    print("🔍 Parsing descriptions for BR/TB...")
    cebu_df[['Bedrooms', 'Bathrooms']] = cebu_df['Description'].apply(
        lambda x: pd.Series(parse_description(x))
    )
    
    # Basic Cleaning: Convert areas and price to numeric
    cebu_df['LotArea'] = pd.to_numeric(cebu_df['LotArea'], errors='coerce')
    cebu_df['FloorArea'] = pd.to_numeric(cebu_df['FloorArea'], errors='coerce')
    cebu_df['Price'] = pd.to_numeric(cebu_df['Price'], errors='coerce')
    
    # Save processed data
    cebu_df.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"💾 Processed data saved to: {PROCESSED_DATA_PATH}")

if __name__ == "__main__":
    main()
