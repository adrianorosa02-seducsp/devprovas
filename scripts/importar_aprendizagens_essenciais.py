from io import BytesIO

import pdfplumber
import pandas as pd
import re
import requests
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.models.models import AprendizagemEssencial, EscopoSequencia
from app.extractors.identificacao_extractor import IdentificacaoExtractor


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
# Determina etapa/ano pelo prefixo ou habilidade priorizada
# ============================================================

def obter_contexto(prefixo, habilidade_priorizada=None):
    """
    Extrai etapa e ano do prefixo (ex: EF01MA) ou da habilidade priorizada (ex: EF01MA14).
    A habilidade priorizada é mais precisa pois contém o ano da habilidade específica.
    """
    # Prioriza habilidade_priorizada se disponível (ex: EF01MA14 -> ano=1)
    if habilidade_priorizada:
        match = re.search(r'EF(\d{2})[A-Z]{2}', habilidade_priorizada)
        if match:
            ano = int(match.group(1))
            etapa = "EFAI" if ano <= 5 else "EFAF"
            return etapa, ano

    # Fallback para prefixo (ex: EF01MA -> ano=1)
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
    """
    Extrai TODAS as páginas de Escopo-Sequência do PDF (1º ao 5º ano).
    Cada página tem cabeçalho tipo: "Escopo-Sequência 2º Ano 3º Bimestre"
    """
    
    # 1. Localizar TODAS as páginas com "Escopo-Sequência"
    paginas_escopo = localizar_paginas(pdf, "Escopo-Sequência")
    
    if not paginas_escopo:
        print("Nenhuma página com 'Escopo-Sequência' encontrada.")
        return pd.DataFrame()
    
    print(f"Total de páginas de Escopo-Sequência encontradas: {len(paginas_escopo)}")
    
    # 2. Extrair prefixo AE de cada página "Habilidade priorizada" (para mapear ano->prefixo)
    paginas_hp = localizar_paginas(pdf, "Habilidade priorizada")
    ae_page_to_prefix = {}
    for p in paginas_hp:
        page_obj = pdf.pages[p - 1]
        ae_data = extrair_AE(page_obj, p)
        if ae_data['prefixo_AE']:
            ae_page_to_prefix[p] = ae_data['prefixo_AE']
    
    print(f"Prefixos AE encontrados: {dict(ae_page_to_prefix)}")
    
    # 3. Processar cada página de escopo
    all_escopo_dfs = []
    
    for numero_pagina in paginas_escopo:
        page = pdf.pages[numero_pagina - 1]
        text = page.extract_text() or ""
        first_line = text.split('\n')[0].strip()
        
        # Extrair ano e bimestre do cabeçalho: "Escopo-Sequência 2º Ano 3º Bimestre"
        import re
        match_ano = re.search(r'(\d+)º\s*Ano', first_line)
        match_bim = re.search(r'(\d+)[º°]?\s*Bimestre', first_line)
        
        if not match_ano or not match_bim:
            print(f"  ⚠ Página {numero_pagina}: não encontrou ano/bimestre no cabeçalho: '{first_line}'")
            continue
            
        ano = int(match_ano.group(1))
        bimestre = int(match_bim.group(1))
        
        # Determinar prefixo AE baseado no ano
        # 1º ano -> EF01MA, 2º ano -> EF02MA, etc.
        prefixo_ae = f"EF{ano:02d}MA"
        
        print(f"  Página {numero_pagina}: {prefixo_ae} | Ano={ano} | Bimestre={bimestre}")
        
        df_page = _processar_tabela_escopo_pagina(page, numero_pagina, prefixo_ae)
        if df_page is not None:
            df_page['bimestre'] = bimestre
            df_page['ano'] = ano  # adicionar ano para debug
            all_escopo_dfs.append(df_page)
    
    if all_escopo_dfs:
        final_escopo_df_raw = pd.concat(all_escopo_dfs, ignore_index=True)
        print(f"\nTotal de {len(all_escopo_dfs)} DataFrames concatenados.")
        
        # Processamento adicional
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

        final_columns_order = new_column_names + ['pagina_pdf', 'prefixo_AE', 'bimestre', 'ano']
        final_escopo_df_processed = final_escopo_df_processed[final_columns_order]

        # Remove header rows
        final_escopo_df_processed = final_escopo_df_processed[
            final_escopo_df_processed['Aula'].astype(str).str.lower() != 'aula'
        ]

        print("Primeiras 5 linhas:")
        print(final_escopo_df_processed.head())
        return final_escopo_df_processed
    else:
        print("Nenhum DataFrame extraído.")
        return pd.DataFrame()


# ============================================================
# Persistência Escopo-Sequência
# ============================================================

def importar_escopo_sequencia(db, df_escopo, ano_referencia=2026):
    if df_escopo.empty:
        print("DataFrame de Escopo-Sequência vazio. Nada a importar.")
        return 0, 0

    inseridos = 0
    atualizados = 0

    for _, row in df_escopo.iterrows():
        prefixo_ae = row.get('prefixo_AE')
        if not prefixo_ae:
            print(f"  ⚠ Pulando linha sem prefixo_AE: {row.to_dict()}")
            continue

        aula_val = str(row.get('Aula', '')).strip() if row.get('Aula') else None
        if not aula_val:
            print(f"  ⚠ Pulando linha sem Aula válida: {row.to_dict()}")
            continue

        etapa, ano = obter_contexto(prefixo_ae, row.get('Habilidades'))
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

        # Converter para JSONB se necessário (habilidades e aprendizagem_essencial podem vir como texto estruturado)
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

        habilidades_raw = row.get('Habilidades')
        aprendizagem_raw = row.get('Aprendizagem Essencial')
        
        dados = {
            "ano_referencia": ano_referencia,
            "etapa": etapa,
            "componente": "Matemática",
            "ano": ano,
            "bimestre": row.get('bimestre'),
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
# Main
# ============================================================

def main():

    print("\nAbrindo PDF...")

    pdf = pdfplumber.open(
        BytesIO(requests.get(PDF_URL).content)
    )

    paginas = localizar_paginas(
        pdf,
        "Habilidade priorizada:"
    )

    print(f"{len(paginas)} páginas encontradas.\n")

    extractor = IdentificacaoExtractor()

    db = SessionLocal()

    inseridos = 0
    atualizados = 0

    try:

        for numero in paginas:

            print(f"Processando página {numero}...")

            page = pdf.pages[numero - 1]

            dados = extractor.extrair(page)

            etapa, ano = obter_contexto(
                dados["prefixo"],
                dados.get("habilidade_priorizada")
            )

            ae = (
                db.query(AprendizagemEssencial)
                .filter(
                    AprendizagemEssencial.id_ae == dados["id_ae"]
                )
                .first()
            )

            if ae is None:

                ae = AprendizagemEssencial(
                    ano_referencia=2026,
                    etapa=etapa,
                    componente="Matemática",
                    ano=ano,

                    id_ae=dados["id_ae"],
                    prefixo=dados["prefixo"],
                    codigo_ae=dados["codigo_ae"],
                    descricao=dados["descricao"],
                    habilidade_priorizada=dados["habilidade_priorizada"],

                    habilidades_relacionadas=dados["habilidades_relacionadas"],
                    conhecimentos_previos=dados["conhecimentos_previos"],
                    prova_paulista=dados["prova_paulista"],
                    saresp=dados["saresp"],
                    desenvolvimento_aprendizagem=dados["desenvolvimento_aprendizagem"]
                )

                db.add(ae)

                inseridos += 1

                print(f"   ✔ Inserido {ae.id_ae}")

            else:

                ae.ano_referencia = 2026
                ae.etapa = etapa
                ae.componente = "Matemática"
                ae.ano = ano

                ae.prefixo = dados["prefixo"]
                ae.codigo_ae = dados["codigo_ae"]
                ae.descricao = dados["descricao"]
                ae.habilidade_priorizada = dados["habilidade_priorizada"]

                ae.habilidades_relacionadas = dados["habilidades_relacionadas"]
                ae.conhecimentos_previos = dados["conhecimentos_previos"]
                ae.prova_paulista = dados["prova_paulista"]
                ae.saresp = dados["saresp"]
                ae.desenvolvimento_aprendizagem = dados["desenvolvimento_aprendizagem"]

                atualizados += 1

                print(f"   ↺ Atualizado {ae.id_ae}")

        db.commit()

        print("\n======================================")
        print("IMPORTAÇÃO APRENDIZAGENS ESSENCIAIS FINALIZADA")
        print("======================================")
        print(f"Inseridos : {inseridos}")
        print(f"Atualizados : {atualizados}")

        # ============================================================
        # Extração e Importação do Escopo-Sequência
        # ============================================================
        print("\n======================================")
        print("EXTRAINDO ESCOPO-SEQUÊNCIA")
        print("======================================\n")

        df_escopo = extrair_escopo_sequencia(pdf)
        
        if not df_escopo.empty:
            print(f"\nImportando {len(df_escopo)} registros de Escopo-Sequência...")
            esc_inseridos, esc_atualizados = importar_escopo_sequencia(db, df_escopo, 2026)
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