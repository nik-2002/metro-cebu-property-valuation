import pypdf
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

pdf_path = "/Users/nicoestreba/Library/CloudStorage/GoogleDrive-nico.estreba@gmail.com/My Drive/UA&P/UA&P Classes/Data Science/15 Research Methods/DS_Thesis/Presentation/Ash Grey and Black Modern Professional Brand Research Presentation.pdf"

try:
    reader = pypdf.PdfReader(pdf_path)
    text = ""
    # Read all pages
    for i in range(len(reader.pages)):
        text += f"--- PAGE {i+1} ---\n"
        text += reader.pages[i].extract_text() + "\n"
    print(text)
except Exception as e:
    print(f"Error: {e}")
