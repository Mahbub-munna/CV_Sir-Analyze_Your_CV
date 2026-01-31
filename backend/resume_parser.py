import os
import pdfplumber
import docx

def extract_text(relative_path):
    base_dir = os.path.dirname(__file__)  # backend folder
    full_path = os.path.abspath(
        os.path.join(base_dir, relative_path)
    )

    text = ""

    if full_path.endswith(".pdf"):
        with pdfplumber.open(full_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

    elif full_path.endswith(".docx"):
        doc = docx.Document(full_path)
        for para in doc.paragraphs:
            text += para.text + "\n"

    return text
