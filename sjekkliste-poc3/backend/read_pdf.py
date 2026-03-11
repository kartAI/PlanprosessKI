from pypdf import PdfReader

# Hent informasjon fra pdf og gjør den til tekst
def read_pdf(path: str) -> str:
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text