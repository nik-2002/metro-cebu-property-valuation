import pypdf
import sys
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

pdf_path = "/Users/nicoestreba/Library/CloudStorage/GoogleDrive-nico.estreba@gmail.com/My Drive/UA&P/UA&P Classes/Data Science/15 Research Methods/DS_Thesis/Data/BDO_Data/VISAYAS-as-of-October-29-2025.pdf"

try:
    reader = pypdf.PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    
    # Simple count of "Cebu City"
    cebu_city_count = len(re.findall(r'Cebu City', full_text, re.IGNORECASE))
    cebu_prov_count = len(re.findall(r'Cebu', full_text, re.IGNORECASE))
    
    print(f"Total 'Cebu City' mentions: {cebu_city_count}")
    print(f"Total 'Cebu' mentions: {cebu_prov_count}")
    
    # Try to verify the "955" number or estimate total rows
    # Assuming standard BDO listing format, maybe look for dates or prices or address lines
    # This is a rough heuristic
    
except Exception as e:
    print(f"Error: {e}")
