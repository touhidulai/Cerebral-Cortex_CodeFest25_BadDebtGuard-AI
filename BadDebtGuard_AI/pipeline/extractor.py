import pdfplumber
from docx import Document
import pytesseract
from PIL import Image
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
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()

    # Images (OCR)
    if extension in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
        try:
            img = Image.open(file_path)
            return pytesseract.image_to_string(img)
        except Exception as e:
            return f"OCR error: {e}"

    return f"Unsupported file type: {extension}"
