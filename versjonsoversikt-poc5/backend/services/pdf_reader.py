from pypdf import PdfReader

#henter informasjon fra PDF og gjør det om til tekst
def read_pdf(path: str) -> str:
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text