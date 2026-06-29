import io
import PyPDF2
from docx import Document
import pandas as pd

def extract_text(file_obj, filename: str) -> str:
    """Extracts text from an uploaded file based on its extension."""
    ext = filename.split('.')[-1].lower()
    text = ""
    
    try:
        if ext == 'txt':
            text = file_obj.read().decode('utf-8')
        elif ext == 'pdf':
            reader = PyPDF2.PdfReader(file_obj)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        elif ext == 'docx':
            doc = Document(file_obj)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif ext == 'xlsx':
            # Read all sheets, combine them into a string representation
            xls = pd.ExcelFile(file_obj)
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                text += f"--- Sheet: {sheet_name} ---\n"
                text += df.to_string(index=False) + "\n\n"
        else:
            text = f"Unsupported file type: {ext}"
    except Exception as e:
        text = f"Error extracting text from {filename}: {str(e)}"
        
    return text.strip()
