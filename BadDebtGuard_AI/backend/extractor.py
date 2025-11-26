import pdfplumber
from docx import Document
import mimetypes
import os

def extract_text(file_path):
    extension = os.path.splitext(file_path)[1].lower()
    mime_type, _ = mimetypes.guess_type(file_path)

    # PDF
    if extension == ".pdf":
        try:
            with pdfplumber.open(file_path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as e:
            return f"Error reading PDF: {e}"

    # DOCX
    if extension == ".docx":
        try:
            doc = Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception as e:
            return f"Error reading DOCX: {e}"

    # TXT
    if extension == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except:
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    return f.read()
            except Exception as e:
                return f"Error reading TXT: {e}"

    return f"Unsupported file type: {extension}. Supported formats: .pdf, .docx, .txt"