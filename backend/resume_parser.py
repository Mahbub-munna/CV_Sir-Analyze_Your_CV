import os
import pdfplumber
import docx

def extract_text(relative_path):
    base_dir = os.path.dirname(__file__)  # backend folder

    full_path = os.path.abspath(
        os.path.join(base_dir, relative_path)
    )

    text = ""

    try:
        # -----------------------------
        # PDF Extraction
        # -----------------------------
        if full_path.lower().endswith(".pdf"):
            with pdfplumber.open(full_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"

        # -----------------------------
        # DOCX Extraction
        # -----------------------------
        elif full_path.lower().endswith(".docx"):
            document = docx.Document(full_path)
            for para in document.paragraphs:
                if para.text:
                    text += para.text + "\n"

    except Exception as e:
        print("Error extracting text:", e)

    return text