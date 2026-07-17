#!/usr/bin/env python3
"""
Extract Aprendizagens Essenciais (AEs) from EFAIMAT PDF and save to database.

Tables:
- acervo_digital: Generic document metadata (one entry per PDF)
- aprendizagens_essenciais: Structured AE data (one entry per AE)
"""

import re
import pdfplumber
import requests
from io import BytesIO
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import AcervoDigital, AprendizagemEssencial
from sqlalchemy import delete
import uuid
from datetime import datetime


def download_pdf(google_drive_id: str) -> bytes:
    """Download PDF from Google Drive using export link."""
    url = f"https://drive.google.com/uc?export=download&id={google_drive_id}"
    response = requests.get(url, stream=True)
    response.raise_for_status()
    return response.content


# Page ranges for each year (1-indexed page numbers)
YEAR_PAGE_RANGES = [
    (1, 15, 0),   # Pages 1-15: cover, intro, TOC
    (16, 28, 1),  # Pages 16-28: Year 1 (AE1-AE13)
    (30, 42, 2),  # Pages 30-42: Year 2 (AE1-AE13)
    (44, 56, 3),  # Pages 44-56: Year 3 (AE1-AE13)
    (58, 68, 4),  # Pages 58-68: Year 4 (AE1-AE11)
    (70, 77, 5),  # Pages 70-77: Year 5 (AE1-AE8)
]

PAGE_TO_YEAR = {}
for start, end, year in YEAR_PAGE_RANGES[1:]:
    for p in range(start, end + 1):
        PAGE_TO_YEAR[p] = year


def get_year_for_page(page_num: int) -> int | None:
    return PAGE_TO_YEAR.get(page_num)


def extract_para_desenvolver_from_tables(page) -> dict:
    """Extract 'Para desenvolver a aprendizagem' data from tables."""
    result = {
        'blocos_tematicos': [],
        'materiais_digitais': [],
        'livros_estudante': []
    }
    
    tables = page.extract_tables()
    if not tables:
        return result
    
    for table in tables:
        if not table or len(table) < 1:
            continue
        
        headers = [str(h).strip() if h else '' for h in table[0]]
        if 'Bloco temático' in ' '.join(headers) and 'Materiais Digitais' in ' '.join(headers):
            for row in table[1:]:
                if not row or len(row) < 3:
                    continue
                
                bloco = (row[0] or '').strip()
                material = (row[1] or '').strip()
                livro = (row[2] or '').strip()
                
                if bloco:
                    result['blocos_tematicos'].append({'titulo': bloco})
                if material:
                    result['materiais_digitais'].append({'descricao': material})
                if livro:
                    result['livros_estudante'].append({'descricao': livro})
            break
    
    return result


def extract_habilidade_priorizada(section: str) -> str | None:
    """
    Extract the skill code (EFxxxxx or EIxxxxx) from the Habilidade priorizada section.
    The pattern is: "Habilidade priorizada:" followed by title line, then skill code line.
    """
    # Pattern 1: "Habilidade priorizada:\n<Title>\n<CODE>."
    match = re.search(r'Habilidade priorizada:\s*\n\s*[^\n]+\n\s*([A-Z]{2}\d{2}[A-Z]{2}\d{2}\*?)\.', section)
    if match:
        return match.group(1)
    
    # Pattern 2: "Habilidade priorizada:\n<Title with code>"
    match = re.search(r'Habilidade priorizada:\s*\n\s*[^\n]*\b([A-Z]{2}\d{2}[A-Z]{2}\d{2}\*?)\b', section)
    if match:
        return match.group(1)
    
    # Pattern 3: Any skill code in the section (fallback)
    match = re.search(r'\b([A-Z]{2}\d{2}[A-Z]{2}\d{2}\*?)\b', section)
    if match:
        # Verify it's not a navigation code like AE1 AE2
        code = match.group(1)
        if not code.startswith('AE'):
            return code
    
    return None


def parse_habilidades_relacionadas(section: str) -> list[str]:
    """
    Parse Habilidades Relacionadas section - keep only skill codes.
    """
    # Find the section
    match = re.search(
        r'Habilidades Relacionadas\s*(.*?)(?:\n\s*Conhecimentos Prévios|\n\s*Para desenvolver|\n\s*De Olho|\n\s*AE\d+\s+AE\d+|\Z)',
        section, re.DOTALL
    )
    if not match:
        return []
    
    content = match.group(1).strip()
    if not content:
        return []
    
    # Extract all skill codes
    codes = re.findall(r'\b([A-Z]{2}\d{2}[A-Z]{2}\d{2}\*?)\b', content)
    
    # Check for "Não há" or "Em andamento"
    if 'não há' in content.lower() or 'nao ha' in content.lower() or 'em andamento' in content.lower():
        if not codes:
            return ['Não há.']
    
    # Deduplicate preserving order
    seen = set()
    unique = []
    for c in codes:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    
    return unique


def parse_conhecimentos_previos(section: str) -> list[str]:
    """Parse Conhecimentos Prévios section - keep only skill codes."""
    match = re.search(
        r'Conhecimentos Prévios\s*(.*?)(?:\n\s*AE\d+\s+AE\d+|\n\s*Para desenvolver|\n\s*De Olho|\Z)',
        section, re.DOTALL
    )
    if not match:
        return []
    
    content = match.group(1).strip()
    if not content:
        return []
    
    # Extract all skill codes (EFxxxxx, EIxxxxx)
    codes = re.findall(r'\b([A-Z]{2}\d{2}[A-Z]{2}\d{2}\*?)\b', content)
    
    # Also check for "Não há" or "Em andamento"
    if 'não há' in content.lower() or 'nao ha' in content.lower() or 'em andamento' in content.lower():
        if not codes:
            return ['Não há.']
    
    # Deduplicate preserving order
    seen = set()
    unique = []
    for c in codes:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    
    return unique


def extract_ae_data(text: str, page_num: int, page_obj) -> list[dict]:
    """Extract AE information from page text."""
    aes = []
    
    # Get "Para desenvolver" data from tables
    dev_data = extract_para_desenvolver_from_tables(page_obj)
    
    # Split by AE entries
    ae_splits = re.split(r'(?=EFAI\s+AE\d+\s*[-–])', text)
    
    for section in ae_splits:
        if not section.strip() or 'EFAI' not in section:
            continue
        
        # Extract AE number and title
        ae_match = re.search(r'AE(\d+)\s*[-–]\s*([^\n]+)', section)
        if not ae_match:
            continue
        
        ae_num = int(ae_match.group(1))
        ae_title = ae_match.group(2).strip()
        
        # Habilidade priorizada
        habilidade = extract_habilidade_priorizada(section)
        
        # Habilidades Relacionadas
        hab_rel = parse_habilidades_relacionadas(section)
        
        # Conhecimentos Prévios
        cp = parse_conhecimentos_previos(section)
        
        aes.append({
            'ae_numero': ae_num,
            'titulo': ae_title,
            'habilidade_priorizada': habilidade,
            'habilidades_relacionadas': hab_rel,
            'conhecimentos_previos': cp,
            'blocos_tematicos': dev_data['blocos_tematicos'],
            'materiais_digitais': dev_data['materiais_digitais'],
            'livros_estudante': dev_data['livros_estudante'],
            'page': page_num
        })
    
    return aes


def parse_pdf(pdf_bytes: bytes) -> list[dict]:
    """Parse the entire PDF and extract all AEs with their years."""
    all_aes = []
    
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text(x_tolerance=1, y_tolerance=1)
            if not text:
                continue
            
            if 'Habilidade priorizada' not in text:
                continue
            
            year = get_year_for_page(page_num)
            if not year:
                continue
            
            aes = extract_ae_data(text, page_num, page)
            for ae in aes:
                ae['ano'] = year
                all_aes.append(ae)
    
    return all_aes


def save_to_database(aes: list[dict], arquivo_id: str, titulo_doc: str):
    """Save extracted data to both acervo_digital and aprendizagens_essenciais."""
    db = SessionLocal()
    try:
        # 1. Create or update AcervoDigital (generic document entry)
        acervo = db.query(AcervoDigital).filter(AcervoDigital.arquivo_id == arquivo_id).first()
        if not acervo:
            acervo = AcervoDigital(
                arquivo_id=arquivo_id,
                titulo=titulo_doc,
                descricao=f"Guia do Currículo Priorizado - {titulo_doc}",
                tipo_arquivo="PDF",
                link_google_drive=f"https://drive.google.com/file/d/{arquivo_id}/view",
                link_download_python=f"https://drive.google.com/uc?export=download&id={arquivo_id}"
            )
            db.add(acervo)
            db.flush()
        
        acervo_id = acervo.id
        
        # 2. Clear existing AEs for this acervo
        db.query(AprendizagemEssencial).filter(
            AprendizagemEssencial.acervo_id == acervo_id
        ).delete(synchronize_session=False)
        
        # 3. Insert new AEs
        saved_count = 0
        for ae in aes:
            db_ae = AprendizagemEssencial(
                acervo_id=acervo_id,
                ae_codigo=f"AE{ae['ae_numero']}",
                ano=ae['ano'],
                codigo_material="EFAIMAT",
                descricao=ae['titulo'],
                habilidade_priorizada=ae['habilidade_priorizada'],
                habilidades_relacionadas=ae['habilidades_relacionadas'],
                conhecimentos_previos=ae['conhecimentos_previos'],
                blocos_tematicos=ae['blocos_tematicos'],
                materiais_digitais=ae['materiais_digitais'],
                livros_estudante=ae['livros_estudante'],
                pagina_pdf=ae['page']
            )
            db.add(db_ae)
            saved_count += 1
        
        db.commit()
        print(f"Salvos: 1 acervo + {saved_count} AEs")
        
    except Exception as e:
        db.rollback()
        print(f"Erro ao salvar: {e}")
        raise
    finally:
        db.close()


def main():
    ARQUIVO_ID = "1AfZ2UMTkuvpbG6ie3T_cIiu9iOknpnVx"
    TITULO_DOC = "GUIA DO CURRÍCULO PRIORIZADO - Anos Iniciais - Matemática"
    
    print("Baixando PDF do Google Drive...")
    pdf_bytes = download_pdf(ARQUIVO_ID)
    print(f"PDF baixado: {len(pdf_bytes)} bytes")
    
    print("Extraindo AEs do PDF...")
    aes = parse_pdf(pdf_bytes)
    print(f"Encontrados {len(aes)} AEs")
    
    # Group by year for summary
    by_year = {}
    for ae in aes:
        year = ae.get('ano', 0)
        if year not in by_year:
            by_year[year] = []
        by_year[year].append(ae)
    
    for year in sorted(by_year.keys()):
        print(f"  {year}º Ano: {len(by_year[year])} AEs")
        for ae in by_year[year]:
            hp = ae['habilidade_priorizada'] or 'N/A'
            print(f"    AE{ae['ae_numero']}: {ae['titulo'][:60]}... | HP: {hp}")
            if ae['habilidades_relacionadas']:
                print(f"      HR: {ae['habilidades_relacionadas']}")
            if ae['conhecimentos_previos']:
                print(f"      CP: {ae['conhecimentos_previos']}")
    
    print("Salvando no banco de dados...")
    save_to_database(aes, ARQUIVO_ID, TITULO_DOC)
    print("Concluído!")


if __name__ == "__main__":
    main()