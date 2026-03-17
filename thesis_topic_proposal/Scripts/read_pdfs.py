
import os
import sys
import io

# set stdout to handle utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def extract_text(pdf_path, max_pages=3):
    text = ""
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        for i in range(min(max_pages, len(reader.pages))):
            text += reader.pages[i].extract_text() + "\n"
        return text
    except ImportError:
        pass

    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(pdf_path)
        for i in range(min(max_pages, len(reader.pages))):
            text += reader.pages[i].extract_text() + "\n"
        return text
    except ImportError:
        return "MISSING_LIB"
    except Exception as e:
        return f"Error: {e}"

folder = r'e:/My Drive/UA&P/UA&P Classes/Data Science/15 Research Methods/DS_Thesis/Research Papers & References'
files = [
    "2012.09115v1.pdf",
    "2405.08398v2.pdf",
    "Determinants_of_Land_Values_in_Cebu_City.pdf",
    "DomingoFulleros-REPI-Philippine-Model-bispap'05.pdf",
    "Exploring the spatial segmentation of housing markets from online listings_14May'24.pdf",
    "MacroeconomicDeterminantsResearch.pdf",
    "pids-dps2004-49.pdf",
    "tps_2023_72_1_1.pdf"
]

results = {}
lib_missing = False

for f in files:
    path = os.path.join(folder, f)
    if os.path.exists(path):
        content = extract_text(path)
        if content == "MISSING_LIB":
            lib_missing = True
            break
        results[f] = content
    else:
        results[f] = "File not found"

if lib_missing:
    print("LIBRARY_MISSING: Please install pypdf or PyPDF2")
else:
    for f, content in results.items():
        print(f"--- START {f} ---")
        print(content[:2000]) # First 2000 chars
        print(f"--- END {f} ---")
