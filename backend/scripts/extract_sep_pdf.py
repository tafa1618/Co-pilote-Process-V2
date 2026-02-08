import pdfplumber
import json

pdf_path = r"E:\Process Copilote\Co-pilote-Process-V2\SEP\2025 SEP Training_v1.1 - EAME Dealers Webinar.pdf"
output_path = r"C:\Users\gaye3\.gemini\antigravity\brain\0faf62a8-bcaf-48f0-9b29-b9b2aa3a0136\sep_extracted.txt"

with pdfplumber.open(pdf_path) as pdf:
    full_text = ""
    for page in pdf.pages:
        full_text += page.extract_text() + "\n\n"

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(full_text)

print(f"Extracted {len(full_text)} characters to {output_path}")
