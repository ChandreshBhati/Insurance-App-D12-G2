import sys
from pypdf import PdfReader

def extract_text(pdf_path, output_file):
    output_file.write(f"--- Extracting from {pdf_path} ---\n")
    try:
        reader = PdfReader(pdf_path)
        text = ""
        # read first 10 pages
        for i, page in enumerate(reader.pages[:10]):
            text += f"\n--- Page {i+1} ---\n"
            text += page.extract_text()
        output_file.write(text[:3000]) # Print first 3000 chars
        output_file.write(f"\n--- End of {pdf_path} (Truncated) ---\n\n")
    except Exception as e:
        output_file.write(f"Error reading {pdf_path}: {e}\n")

with open("pdf_out.txt", "w", encoding="utf-8") as f:
    extract_text("IRDA (Licensing of Bancassurance Entities) Regulations, 2012.pdf", f)
    extract_text("Consumer Affairs Booklet 2019-2020.pdf", f)
