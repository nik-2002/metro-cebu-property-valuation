
import os
import sys
import io
import pypdf

# set stdout to handle utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def extract_text_from_pdf(pdf_path, max_pages=3):
    text = ""
    try:
        reader = pypdf.PdfReader(pdf_path)
        # Read up to max_pages to get abstract/intro/conclusion
        for i in range(min(max_pages, len(reader.pages))):
            text += reader.pages[i].extract_text() + "\n"
            
        # Also try to read the last page for conclusion if it exists and wasn't read
        if len(reader.pages) > max_pages:
             text += "\n--- LAST PAGE ---\n"
             text += reader.pages[-1].extract_text()
             
        return text
    except Exception as e:
        return f"Error reading {pdf_path}: {e}"

folder = r'e:/My Drive/UA&P/UA&P Classes/Data Science/15 Research Methods/DS_Thesis/Research Papers & References'
files = [
    "2012.09115v1.pdf", 
    "MacroeconomicDeterminantsResearch.pdf",
    "pids-dps2004-49.pdf"
]

for f in files:
    path = os.path.join(folder, f)
    if os.path.exists(path):
        print(f"--- START {f} ---")
        print(extract_text_from_pdf(path))
        print(f"--- END {f} ---")
    else:
        print(f"File not found: {f}")
