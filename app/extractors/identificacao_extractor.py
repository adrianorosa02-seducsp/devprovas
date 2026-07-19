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

        return {

            "id_ae": id_ae,

            "prefixo": prefixo,

            "codigo_ae": codigo_ae,

            "descricao": descricao,

            "habilidade_priorizada": habilidade_priorizada

        }