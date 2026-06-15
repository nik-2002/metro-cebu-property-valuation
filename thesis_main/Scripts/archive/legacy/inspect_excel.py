import pandas as pd
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

excel_path = "/Users/nicoestreba/Library/CloudStorage/GoogleDrive-nico.estreba@gmail.com/My Drive/UA&P/UA&P Classes/Data Science/15 Research Methods/DS_Thesis/Data/BDO_Data/BDO-Properties-as-of-11.18.25_03709b93-6342-41c1-b4f6-b2103ef49741 (1).xlsx"

try:
    # Read Excel - no header to see raw grid
    df = pd.read_excel(excel_path, header=None)
    
    print("First 5 rows raw:")
    print(df.head(5).to_string())
    
    
    total_rows = len(df)
    print(f"Total Rows in File: {total_rows}")

    # Column 1 = City (based on row 3 output: 3 Region City ...)
    city_col_idx = 1
    # Column 5 = Address
    address_col_idx = 5
    
    # Filter by City Column
    cebu_city_col = df[df[city_col_idx].astype(str).str.contains("Cebu City", case=False, na=False)]
    
    # Filter by Address Column
    cebu_addr_col = df[df[address_col_idx].astype(str).str.contains("Cebu City", case=False, na=False)]
    
    cebu_prov_col = df[df[address_col_idx].astype(str).str.contains("Cebu", case=False, na=False)]

    print(f"Total Properties in 'Cebu City' (by City Col): {len(cebu_city_col)}")
    print(f"Total Properties in 'Cebu City' (by Address Col): {len(cebu_addr_col)}")
    print(f"Total Properties in 'Cebu' (Province, by Address): {len(cebu_prov_col)}")
    
    print("\nSample Cebu City (City Col):")
    print(df.loc[cebu_city_col.index, address_col_idx].head(5).to_string(index=False))



except Exception as e:
    print(f"Error: {e}")
