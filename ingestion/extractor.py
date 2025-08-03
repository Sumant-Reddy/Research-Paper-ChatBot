import pdfplumber
import os

def extract_text_from_pdf(pdf_path):
    text = ""
    method = "pdfplumber"
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        if text.strip():
            return text, method
    except Exception as e:
        print("pdfplumber failed:", e)
    # Fallback to PyMuPDF
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        method = "pymupdf"
        if text.strip():
            return text, method
    except Exception as e:
        print("PyMuPDF also failed:", e)
    return text, method

def extract_math_images(pdf_path):
    # MathPix stub — you'd need a separate PDF-to-image and HTTP call
    return []  # Replace with real image OCR results if needed

def parse_pdf_to_json(pdf_path):
    raw_text, method = extract_text_from_pdf(pdf_path)
    return {
        "title": os.path.basename(pdf_path),
        "sections": split_by_headings(raw_text),
        "extraction_method": method
    }

def split_by_headings(text):
    import re
    pattern = r"(?<=\n)([A-Z][A-Z\s\d:]{3,})\n"
    sections = re.split(pattern, text)
    results = []
    for i in range(1, len(sections), 2):
        results.append({
            "section_title": sections[i].strip(),
            "content": sections[i+1].strip()
        })
    return results
