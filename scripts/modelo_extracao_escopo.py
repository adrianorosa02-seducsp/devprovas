import pandas as pd
import re

def extrair_dados_pdf(pdf):
    # Helper function: Localiza páginas que contêm um texto específico.
    def localizar_paginas(pdf, texto_procurado):
        paginas = []
        for numero_pagina, page in enumerate(pdf.pages, start=1):
            texto = page.extract_text()
            if texto and texto_procurado.lower() in texto.lower():
                paginas.append(numero_pagina)
        return paginas

    # Helper function: Extrai os detalhes da Habilidade Priorizada (AE) de uma página.
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

    # Helper function: Processa as tabelas de uma única página de Escopo-Sequência,
    # adicionando `pagina_pdf` e o `prefixo_AE` correspondente.
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

    # ============================================================ #
    # Main Processing Logic                                        #
    # ============================================================ #

    # 1. Localizar páginas com "Habilidade priorizada"
    paginas_hp = localizar_paginas(pdf, "Habilidade priorizada")

    if not paginas_hp:
        print("Nenhuma página com 'Habilidade priorizada' encontrada.")
        ae_data_dict = {}
    else:
        ae_data_dict = {}
        for numero_pagina_hp in paginas_hp:
            page_obj = pdf.pages[numero_pagina_hp - 1]
            ae_data = extrair_AE(page_obj, numero_pagina_hp)
            if ae_data['prefixo_AE'] is not None:
                ae_data_dict[numero_pagina_hp] = ae_data
        print(f"AEs extraídas de {len(ae_data_dict)} páginas com Habilidade Priorizada.")

    # Mapear páginas de AE para seus prefixos para uso posterior
    ae_page_to_prefix = {
        data['numero_pagina_hp']: data['prefixo_AE']
        for page_num, data in ae_data_dict.items()
    }
    print("Dicionário de páginas AE para prefixos criado:")
    print(ae_page_to_prefix)

    # 2. Localizar a página de início do Escopo-Sequência
    # Usar as páginas que tiveram prefixo_AE extraído com sucesso para determinar 'inicio'
    paginas_com_prefixo_ae_valido = sorted(ae_page_to_prefix.keys())
    if len(paginas_com_prefixo_ae_valido) == 0:
        raise Exception("Nenhuma AE válida encontrada para determinar o início do escopo.")
    ultima_pagina_ae = paginas_com_prefixo_ae_valido[-1]
    inicio = ultima_pagina_ae + 2 # Presume-se que o escopo começa 2 páginas após a última AE
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
        # Encontrar a AE mais recente (maior número de página) que seja menor ou igual à página atual de escopo
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
        # Drop the extra column '5' as the target DataFrame has 5 content columns
        if 5 in final_escopo_df_raw.columns:
            final_escopo_df_raw = final_escopo_df_raw.drop(columns=[5])

        # Define the new column names for the content columns
        new_column_names = [
            'Aula',
            'Conteúdo',
            'Objetivos de aprendizagem',
            'Habilidades',
            'Aprendizagem Essencial'
        ]

        # Rename the first 5 numerical columns if they exist
        current_content_columns = [col for col in range(len(new_column_names)) if col in final_escopo_df_raw.columns]
        rename_dict = {old_col: new_col for old_col, new_col in zip(current_content_columns, new_column_names)}
        final_escopo_df_processed = final_escopo_df_raw.rename(columns=rename_dict)

        # Ensure all target columns are present, fill missing with None/NaN if necessary
        for col in new_column_names:
            if col not in final_escopo_df_processed.columns:
                final_escopo_df_processed[col] = None

        # Reorder columns to the desired sequence
        final_columns_order = new_column_names + ['pagina_pdf', 'prefixo_AE']
        final_escopo_df_processed = final_escopo_df_processed[final_columns_order]

        # Remove header rows (where 'Aula' column contains the literal string 'Aula')
        final_escopo_df_processed = final_escopo_df_processed[
            final_escopo_df_processed['Aula'].astype(str).str.lower() != 'aula'
        ]

        print("Primeiras 5 linhas do DataFrame processado (final_escopo_df):")
        display(final_escopo_df_processed.head())
        return final_escopo_df_processed
    else:
        print("Nenhum DataFrame de Escopo-Sequência foi extraído das páginas filtradas.")
        return pd.DataFrame()

# Exemplo de uso da função consolidada:
final_escopo_df = extrair_dados_pdf(pdf)
