#!/usr/bin/env python3
"""
Extract raw text from EFAIMAT PDF and save to file for manual inspection.
"""

import pdfplumber
import requests
from io import BytesIO


def download_pdf(google_drive_id: str) -> bytes:
    url = f"https://drive.google.com/uc?export=download&id={google_drive_id}"
    response = requests.get(url, stream=True)
    response.raise_for_status()
    return response.content


def main():
    ARQUIVO_ID = "1AfZ2UMTkuvpbG6ie3T_cIiu9iOknpnVx"
    
    print("Baixando PDF...")
    pdf_bytes = download_pdf(ARQUIVO_ID)
    print(f"PDF baixado: {len(pdf_bytes)} bytes")
    
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        print(f"Total de páginas: {len(pdf.pages)}")
        
        # Save full text
        with open('/tmp/efaimat_raw_text.txt', 'w', encoding='utf-8') as f:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text(x_tolerance=1, y_tolerance=1)
                if text:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"PÁGINA {page_num}\n")
                    f.write(f"{'='*80}\n")
                    f.write(text)
                    f.write("\n")
        
        print("Texto salvo em /tmp/efaimat_raw_text.txt")
        
        # Also save layout-preserved text
        with open('/tmp/efaimat_layout_text.txt', 'w', encoding='utf-8') as f:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text(layout=True, x_tolerance=1, y_tolerance=1)
                if text:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"PÁGINA {page_num} (LAYOUT)\n")
                    f.write(f"{'='*80}\n")
                    f.write(text)
                    f.write("\n")
        
        print("Texto com layout salvo em /tmp/efaimat_layout_text.txt")
        
        # Save tables
        with open('/tmp/efaimat_tables.txt', 'w', encoding='utf-8') as f:
            for page_num, page in enumerate(pdf.pages, 1):
                tables = page.extract_tables()
                if tables:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"PÁGINA {page_num} - TABELAS\n")
                    f.write(f"{'='*80}\n")
                    for i, table in enumerate(tables):
                        f.write(f"\n--- Tabela {i} ---\n")
                        for row in table:
                            f.write(" | ".join([str(c) if c else "" for c in row]) + "\n")
        
        print("Tabelas salvas em /tmp/efaimat_tables.txt")


if __name__ == "__main__":
    main()