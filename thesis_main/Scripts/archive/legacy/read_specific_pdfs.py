
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def extract_text(pdf_path, max_pages=1):
    text = ""
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        for i in range(min(max_pages, len(reader.pages))):
            text += reader.pages[i].extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error: {e}"

folder = r'e:/My Drive/UA&P/UA&P Classes/Data Science/15 Research Methods/DS_Thesis/Research Papers & References'
files = [
    "2405.08398v2.pdf",
    "Exploring the spatial segmentation of housing markets from online listings_14May'24.pdf"
]

for f in files:
    path = os.path.join(folder, f)
    if os.path.exists(path):
        print(f"--- START {f} ---")
        print(extract_text(path, max_pages=2))
        print(f"--- END {f} ---")
