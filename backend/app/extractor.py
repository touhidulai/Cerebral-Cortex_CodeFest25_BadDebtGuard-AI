import mimetypes
import os

# Note: PDF and DOCX processing requires packages that need compilation
# Install standard Python from python.org if you need these features
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

def extract_text(file_path):
    extension = os.path.splitext(file_path)[1].lower()
    mime_type, _ = mimetypes.guess_type(file_path)

    # PDF
    if extension == ".pdf":
        if not PDF_AVAILABLE:
            return "Error: PDF processing not available. Install pdfplumber with proper Python from python.org"
        try:
            with pdfplumber.open(file_path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as e:
            return f"Error reading PDF: {e}"

    # DOCX
    if extension == ".docx":
        if not DOCX_AVAILABLE:
            return "Error: DOCX processing not available. Install python-docx with proper Python from python.org"
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