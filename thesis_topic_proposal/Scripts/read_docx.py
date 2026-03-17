
import zipfile
import xml.etree.ElementTree as ET
import sys
import io

# set stdout to handle utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def read_docx(path):
    try:
        with zipfile.ZipFile(path) as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            
            # wrapper to capture namespaces
            namespaces = dict([node for _, node in ET.iterparse(docx.open('word/document.xml'), events=['start-ns'])])
            
            text_parts = []
            for elem in tree.iter():
                # checking for text tag
                if elem.tag.endswith('}t'):
                    if elem.text:
                        text_parts.append(elem.text)
                # checking for paragraph break or break tag
                elif elem.tag.endswith('}p') or elem.tag.endswith('}br'):
                    text_parts.append('\n')
                # checking for tab
                elif elem.tag.endswith('}tab'):
                    text_parts.append('\t')
                    
            return "".join(text_parts)
    except Exception as e:
        return f"Error reading file: {e}"

if __name__ == "__main__":
    file_path = r'e:/My Drive/UA&P/UA&P Classes/Data Science/15 Research Methods/DS_Thesis/Main/Thesis_chapter1.docx'
    print(read_docx(file_path))
