import pypdf
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

pdf_path = "/Users/nicoestreba/Library/CloudStorage/GoogleDrive-nico.estreba@gmail.com/My Drive/UA&P/UA&P Classes/Data Science/15 Research Methods/DS_Thesis/Data/BDO_Data/VISAYAS-as-of-October-29-2025.pdf"

try:
    reader = pypdf.PdfReader(pdf_path)
    # Print first 2 pages to see structure
    for i in range(min(2, len(reader.pages))):
        print(f"--- PAGE {i+1} ---")
        print(reader.pages[i].extract_text())
except Exception as e:
    print(f"Error: {e}")
