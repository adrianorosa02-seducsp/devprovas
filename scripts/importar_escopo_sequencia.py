from io import BytesIO

import pdfplumber
import pandas as pd
import re
import requests
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.models.models import EscopoSequencia


PDF_URL = "https://drive.google.com/uc?export=download&id=1AfZ2UMTkuvpbG6ie3T_cIiu9iOknpnVx"


# ============================================================
# Localizar páginas
# ============================================================

def localizar_paginas(pdf, texto):

    paginas = []

    for numero, page in enumerate(pdf.pages, start=1):

        conteudo = page.extract_text()

        if conteudo and texto.lower() in conteudo.lower():
            paginas.append(numero)

    return paginas


# ============================================================
# Determina etapa/ano pelo prefixo
# ============================================================

def obter_contexto(prefixo):

    ano = int(prefixo[2:4])

    etapa = "EFAI" if ano <= 5 else "EFAF"

    return etapa, ano


# ============================================================
# Extração de Escopo-Sequência (integrado de modelo_extracao_escopo.py)
# ============================================================

def extrair_AE(page, numero_pagina):
    area_AE = page.crop((106.30, 63.78, 651.97, 120.47))
    texto_AE = area_AE.extract_text()

    area_HP = page.crop((651.97, 70.87, 765.35, 120.47))
    texto_HP = area_HP.extract_text()

    match = re.search(r'EF\d{2}[A-Z]{2}', texto_HP)
    prefixo_AE = match.group() if match else None

    id_AE = prefixo_AE + texto_AE[:4] if prefixo_AE and texto_AE else None
    AE_descritor = texto_AE.split("-", 1)[1].strip() if texto_AE and "-" in texto_AE else None

    return {
        "id_AE": id_AE,
        "prefixo_AE": prefixo_AE,
        "texto_AE": texto_AE,
        "AE_descritor": AE_descritor,
        "texto_HP": texto_HP,
        "numero_pagina_hp": numero_pagina
    }


def _processar_tabela_escopo_pagina(page, numero_pagina, current_ae_prefix):
    tabelas = page.extract_tables()

    if not tabelas:
        return None

    all_dfs_on_page = []
    for tabela in tabelas:
        df = pd.DataFrame(tabela)
        df['pagina_pdf'] = numero_pagina
        df['prefixo_AE'] = current_ae_prefix
        all_dfs_on_page.append(df)

    if all_dfs_on_page:
        return pd.concat(all_dfs_on_page, ignore_index=True)
    else:
        return None


def extrair_escopo_sequencia(pdf):
    # 1. Localizar páginas com "Habilidade priorizada"
    paginas_hp = localizar_paginas(pdf, "Habilidade priorizada")

    if not paginas_hp:
        print("Nenhuma página com 'Habilidade priorizada' encontrada.")
        return pd.DataFrame()
    
    ae_data_dict = {}
    for numero_pagina_hp in paginas_hp:
        page_obj = pdf.pages[numero_pagina_hp - 1]
        ae_data = extrair_AE(page_obj, numero_pagina_hp)
        if ae_data['prefixo_AE'] is not None:
            ae_data_dict[numero_pagina_hp] = ae_data
    print(f"AEs extraídas de {len(ae_data_dict)} páginas com Habilidade Priorizada.")

    # Mapear páginas de AE para seus prefixos
    ae_page_to_prefix = {
        data['numero_pagina_hp']: data['prefixo_AE']
        for page_num, data in ae_data_dict.items()
    }
    print("Dicionário de páginas AE para prefixos criado:")
    print(ae_page_to_prefix)

    # 2. Localizar a página de início do Escopo-Sequência
    paginas_com_prefixo_ae_valido = sorted(ae_page_to_prefix.keys())
    if len(paginas_com_prefixo_ae_valido) == 0:
        raise Exception("Nenhuma AE válida encontrada para determinar o início do escopo.")
    ultima_pagina_ae = paginas_com_prefixo_ae_valido[-1]
    inicio = ultima_pagina_ae + 2
    print(f"Última página AE com prefixo válido: {ultima_pagina_ae}. Início do Escopo-Sequência: {inicio}")

    # 3. Localizar páginas que contêm "Escopo-Sequência"
    paginas_escopo_encontradas = localizar_paginas(pdf, "Escopo-Sequência")

    # Filtra as páginas de Escopo-Sequência a partir do 'inicio'
    paginas_escopo_filtradas = [p for p in paginas_escopo_encontradas if p >= inicio]
    print(f"Páginas de 'Escopo-Sequência' a partir da página {inicio} até o final: {paginas_escopo_filtradas}")
    print(f"Total de páginas de 'Escopo-Sequência' filtradas: {len(paginas_escopo_filtradas)}")

    # 4. Processar as tabelas de Escopo-Sequência
    all_escopo_dfs = []
    current_ae_prefix = None
    sorted_ae_pages = sorted(ae_page_to_prefix.keys())

    for numero_pagina_escopo in paginas_escopo_filtradas:
        relevant_ae_pages = [p for p in sorted_ae_pages if p <= numero_pagina_escopo]

        if relevant_ae_pages:
            closest_ae_page = max(relevant_ae_pages)
            current_ae_prefix = ae_page_to_prefix[closest_ae_page]
        else:
            current_ae_prefix = None

        escopo_page = pdf.pages[numero_pagina_escopo - 1]
        df_page = _processar_tabela_escopo_pagina(escopo_page, numero_pagina_escopo, current_ae_prefix)
        if df_page is not None:
            all_escopo_dfs.append(df_page)

    if all_escopo_dfs:
        final_escopo_df_raw = pd.concat(all_escopo_dfs, ignore_index=True)
        print(f"Total de {len(all_escopo_dfs)} DataFrames de Escopo-Sequência concatenados.")

        # Processamento adicional: renomear colunas e remover cabeçalhos
        if 5 in final_escopo_df_raw.columns:
            final_escopo_df_raw = final_escopo_df_raw.drop(columns=[5])

        new_column_names = [
            'Aula',
            'Conteúdo',
            'Objetivos de aprendizagem',
            'Habilidades',
            'Aprendizagem Essencial'
        ]

        current_content_columns = [col for col in range(len(new_column_names)) if col in final_escopo_df_raw.columns]
        rename_dict = {old_col: new_col for old_col, new_col in zip(current_content_columns, new_column_names)}
        final_escopo_df_processed = final_escopo_df_raw.rename(columns=rename_dict)

        for col in new_column_names:
            if col not in final_escopo_df_processed.columns:
                final_escopo_df_processed[col] = None

        final_columns_order = new_column_names + ['pagina_pdf', 'prefixo_AE']
        final_escopo_df_processed = final_escopo_df_processed[final_columns_order]

        # Remove header rows (where 'Aula' column contains the literal string 'Aula')
        final_escopo_df_processed = final_escopo_df_processed[
            final_escopo_df_processed['Aula'].astype(str).str.lower() != 'aula'
        ]

        print("Primeiras 5 linhas do DataFrame processado (final_escopo_df):")
        print(final_escopo_df_processed.head())
        return final_escopo_df_processed
    else:
        print("Nenhum DataFrame de Escopo-Sequência foi extraído das páginas filtradas.")
        return pd.DataFrame()


# ============================================================
# Persistência Escopo-Sequência
# ============================================================

def importar_escopo_sequencia(db, df_escopo, ano_referencia=2025):
    if df_escopo.empty:
        print("DataFrame de Escopo-Sequência vazio. Nada a importar.")
        return 0, 0

    inseridos = 0
    atualizados = 0

    import json
    def to_json_array(val):
        if not val:
            return None
        if isinstance(val, list):
            return val
        if isinstance(val, str):
            parts = [p.strip() for p in val.replace('\n', ';').split(';') if p.strip()]
            return parts if len(parts) > 1 else val
        return val

    for _, row in df_escopo.iterrows():
        prefixo_ae = row.get('prefixo_AE')
        if not prefixo_ae:
            print(f"  ⚠ Pulando linha sem prefixo_AE: {row.to_dict()}")
            continue

        aula_val = str(row.get('Aula', '')).strip() if row.get('Aula') else None
        if not aula_val:
            print(f"  ⚠ Pulando linha sem Aula válida: {row.to_dict()}")
            continue

        etapa, ano = obter_contexto(prefixo_ae)
        id_ae = prefixo_ae + aula_val[:4]
        id_aula = prefixo_ae + aula_val

        escopo = (
            db.query(EscopoSequencia)
            .filter(
                EscopoSequencia.ano_referencia == ano_referencia,
                EscopoSequencia.id_aula == id_aula,
                EscopoSequencia.aula == aula_val
            )
            .first()
        )

        habilidades_raw = row.get('Habilidades')
        aprendizagem_raw = row.get('Aprendizagem Essencial')
        
        dados = {
            "ano_referencia": ano_referencia,
            "etapa": etapa,
            "componente": "Matemática",
            "ano": ano,
            "id_ae": id_ae,
            "prefixo_ae": prefixo_ae,
            "id_aula": id_aula,
            "aula": aula_val,
            "conteudo": row.get('Conteúdo'),
            "objetivos_aprendizagem": row.get('Objetivos de aprendizagem'),
            "habilidades": to_json_array(habilidades_raw),
            "aprendizagem_essencial": to_json_array(aprendizagem_raw),
            "pagina_pdf": int(row.get('pagina_pdf', 0))
        }

        if escopo is None:
            escopo = EscopoSequencia(**dados)
            db.add(escopo)
            inseridos += 1
            print(f"   ✔ Inserido Escopo id_aula={id_aula} Aula={aula_val} Pág={dados['pagina_pdf']}")
        else:
            for key, value in dados.items():
                setattr(escopo, key, value)
            atualizados += 1
            print(f"   ↺ Atualizado Escopo id_aula={id_aula} Aula={aula_val} Pág={dados['pagina_pdf']}")

    return inseridos, atualizados


# ============================================================
# Main - APENAS Escopo-Sequência
# ============================================================

def main():

    print("\n======================================")
    print("IMPORTAÇÃO ESCOPO-SEQUÊNCIA (standalone)")
    print("======================================\n")

    print("Abrindo PDF...")

    pdf = pdfplumber.open(
        BytesIO(requests.get(PDF_URL).content)
    )

    db = SessionLocal()

    try:
        df_escopo = extrair_escopo_sequencia(pdf)
        
        if not df_escopo.empty:
            print(f"\nImportando {len(df_escopo)} registros de Escopo-Sequência...")
            esc_inseridos, esc_atualizados = importar_escopo_sequencia(db, df_escopo, 2025)
            db.commit()
            print("\n======================================")
            print("IMPORTAÇÃO ESCOPO-SEQUÊNCIA FINALIZADA")
            print("======================================")
            print(f"Inseridos : {esc_inseridos}")
            print(f"Atualizados : {esc_atualizados}")
        else:
            print("Nenhum dado de Escopo-Sequência extraído.")

    except SQLAlchemyError:

        db.rollback()
        raise

    finally:

        db.close()


if __name__ == "__main__":
    main()