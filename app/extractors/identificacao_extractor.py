import re


class IdentificacaoExtractor:

    """
    Responsável pela identificação da Aprendizagem Essencial (AE).

    Extrai:

        • id_ae
        • prefixo
        • codigo_ae
        • descricao
        • habilidade_priorizada
        • habilidades_relacionadas
        • conhecimentos_previos
        • prova_paulista
        • saresp
        • desenvolvimento_aprendizagem
    """

    def extrair(self, page):

        # =====================================================
        # ÁREA DA AE
        # =====================================================

        area_ae = page.crop((
            106.30,
            63.78,
            651.97,
            120.47
        ))

        texto_ae = area_ae.extract_text() or ""

        # =====================================================
        # ÁREA DA HABILIDADE PRIORIZADA
        # =====================================================

        area_hp = page.crop((
            651.97,
            70.87,
            765.35,
            120.47
        ))

        texto_hp = area_hp.extract_text() or ""

        # =====================================================
        # PREFIXO
        # =====================================================

        match = re.search(r'EF\d{2}[A-Z]{2}', texto_hp)

        if not match:
            raise Exception(
                "Não foi possível localizar o prefixo da habilidade."
            )

        prefixo = match.group()

        # =====================================================
        # HABILIDADE PRIORIZADA
        # =====================================================

        match = re.search(r'EF\d{2}[A-Z]{2}\d{2}', texto_hp)

        if not match:
            raise Exception(
                "Não foi possível localizar a habilidade priorizada."
            )

        habilidade_priorizada = match.group()

        # =====================================================
        # CÓDIGO AE
        # =====================================================

        match = re.search(r'AE\d+', texto_ae)

        if not match:
            raise Exception(
                "Não foi possível localizar o código AE."
            )

        codigo_ae = match.group()

        # =====================================================
        # ID DA AE
        # =====================================================

        id_ae = prefixo + codigo_ae

        # =====================================================
        # DESCRIÇÃO
        # =====================================================

        partes = texto_ae.split("-", 1)

        descricao = ""

        if len(partes) > 1:
            descricao = partes[1].strip()

        # =====================================================
        # ÁREA DE HABILIDADES RELACIONADAS E CONHECIMENTOS PRÉVIOS
        # =====================================================

        area_hr = page.crop((
            63.78,
            134.65,
            226.77,
            255.12
        ))

        texto_hr = area_hr.extract_text() or ""

        habilidades_relacionadas = self._extrair_habilidades_relacionadas(texto_hr)
        conhecimentos_previos = self._extrair_conhecimentos_previos(texto_hr)

        # =====================================================
        # ÁREA DE OLHO (PROVA PAULISTA / SARESP)
        # =====================================================

        area_deolho = page.crop((
            226.78,
            134.65,
            765.35,
            269.29
        ))

        texto_deolho = area_deolho.extract_text() or ""

        prova_paulista, saresp, tem_prova_paulista, tem_saresp = self._extrair_de_olho(texto_deolho)

        # =====================================================
        # TABELAS (DESENVOLVIMENTO APRENDIZAGEM + PROVA PAULISTA/SARESP)
        # =====================================================

        tabelas = page.extract_tables()

        ano = int(prefixo[2:4])

        desenvolvimento_aprendizagem, prova_paulista_tabela, saresp_tabela = self._extrair_tabelas(
            tabelas, tem_prova_paulista, tem_saresp, ano
        )

        prova_paulista.extend(prova_paulista_tabela)
        saresp.extend(saresp_tabela)

        return {

            "id_ae": id_ae,

            "prefixo": prefixo,

            "codigo_ae": codigo_ae,

            "descricao": descricao,

            "habilidade_priorizada": habilidade_priorizada,

            "habilidades_relacionadas": habilidades_relacionadas,

            "conhecimentos_previos": conhecimentos_previos,

            "prova_paulista": prova_paulista,

            "saresp": saresp,

            "desenvolvimento_aprendizagem": desenvolvimento_aprendizagem

        }

    def _extrair_habilidades_relacionadas(self, texto):
        """Extrai códigos de habilidades relacionadas do texto."""
        if not texto:
            return []

        match = re.search(r'Habilidades Relacionadas\n(.*?)(?:\nConhecimentos Prévios|\Z)', texto, re.DOTALL)
        if not match:
            return []

        conteudo = match.group(1).strip()
        if "Não há" in conteudo:
            return []

        codigos = re.findall(r'EF\d{2}[A-Z]{2}\d{2}', conteudo)
        return [{"codigo": c} for c in codigos]

    def _extrair_conhecimentos_previos(self, texto):
        """Extrai códigos de conhecimentos prévios do texto."""
        if not texto:
            return []

        match = re.search(r'Conhecimentos Prévios\n(.*)', texto, re.DOTALL)
        if not match:
            return []

        conteudo = match.group(1).strip()
        if "Não há" in conteudo:
            return []

        codigos = re.findall(r'EI\d{2}[A-Z]{2}\d{2}|EF\d{2}[A-Z]{2}\d{2}', conteudo)
        return [{"codigo": c} for c in codigos]

    def _extrair_de_olho(self, texto):
        """Extrai itens de Prova Paulista e SARESP da seção 'De Olho'."""
        prova_paulista = []
        saresp = []
        tem_prova_paulista = False
        tem_saresp = False

        if not texto:
            return prova_paulista, saresp, tem_prova_paulista, tem_saresp

        if "De Olho na Prova Paulista" in texto:
            tem_prova_paulista = True
            match = re.search(r'De Olho na Prova Paulista\n(.*)', texto, re.DOTALL)
            if match:
                itens = match.group(1).strip().split('\n• ')
                for item in itens:
                    item = item.strip()
                    if item and not item.startswith("De Olho"):
                        prova_paulista.append(item)

        if "De Olho no SARESP" in texto:
            tem_saresp = True
            match = re.search(r'De Olho no SARESP\n(.*)', texto, re.DOTALL)
            if match:
                itens = match.group(1).strip().split('\n• ')
                for item in itens:
                    item = item.strip()
                    if item and not item.startswith("De Olho"):
                        if item != "Em andamento.":
                            saresp.append(item)

        return prova_paulista, saresp, tem_prova_paulista, tem_saresp

    def _extrair_tabelas(self, tabelas, tem_prova_paulista, tem_saresp, ano):
        """Extrai dados das tabelas da página."""
        desenvolvimento = []
        pp_tabela = []
        sp_tabela = []

        if not tabelas:
            return desenvolvimento, pp_tabela, sp_tabela

        # Default: anos 1-3 vão para Prova Paulista, 4-5 dependem do "De Olho"
        if not tem_prova_paulista and not tem_saresp:
            if ano <= 3:
                tem_prova_paulista = True
            else:
                tem_prova_paulista = True
                tem_saresp = True

        for tabela in tabelas:
            if not tabela or len(tabela) < 2:
                continue

            headers = tabela[0]
            if not headers or len(headers) < 3:
                continue

            bloco_idx = None
            materiais_idx = None
            livro_idx = None

            for i, h in enumerate(headers):
                if h and "Bloco" in str(h):
                    bloco_idx = i
                elif h and "Materiais" in str(h):
                    materiais_idx = i
                elif h and "Livro" in str(h):
                    livro_idx = i

            if bloco_idx is None or materiais_idx is None or livro_idx is None:
                continue

            for row in tabela[1:]:
                if not row or len(row) <= max(bloco_idx, materiais_idx, livro_idx):
                    continue

                bloco = str(row[bloco_idx] or "").strip()
                materiais = str(row[materiais_idx] or "").strip()
                livro = str(row[livro_idx] or "").strip()

                if bloco:
                    desenvolvimento.append({
                        "bloco_tematico": bloco,
                        "livro_estudante": livro if livro else None
                    })

                if materiais:
                    items = re.findall(r'(\d+º bim\.\s*:\s*[\d,\s\.]+)', materiais)
                    for item in items:
                        item = item.strip()
                        if tem_prova_paulista and not tem_saresp:
                            pp_tabela.append(item)
                        elif tem_saresp and not tem_prova_paulista:
                            sp_tabela.append(item)
                        else:
                            pp_tabela.append(item)
                            sp_tabela.append(item)

        return desenvolvimento, pp_tabela, sp_tabela