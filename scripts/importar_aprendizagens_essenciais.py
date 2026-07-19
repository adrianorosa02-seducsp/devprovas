from io import BytesIO

import pdfplumber
import requests
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.models.models import AprendizagemEssencial
from app.extractors.identificacao_extractor import IdentificacaoExtractor


PDF_URL = "https://drive.google.com/uc?export=download&id=1AfZ2UMTkuvpbG6ie3T_cIiu9iOknpnVx"


# ============================================================
# Localizar páginas
# ================================poetry run python -m scripts.importar_aprendizagens_essenciais============================

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
                dados["prefixo"]
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
                    ano_referencia=2025,
                    etapa=etapa,
                    componente="Matemática",
                    ano=ano,

                    id_ae=dados["id_ae"],
                    prefixo=dados["prefixo"],
                    codigo_ae=dados["codigo_ae"],
                    descricao=dados["descricao"],
                    habilidade_priorizada=dados["habilidade_priorizada"],

                    habilidades_relacionadas=[],
                    conhecimentos_previos=[],
                    prova_paulista=[],
                    saresp=[],
                    desenvolvimento_aprendizagem=[]
                )

                db.add(ae)

                inseridos += 1

                print(f"   ✔ Inserido {ae.id_ae}")

            else:

                ae.ano_referencia = 2025
                ae.etapa = etapa
                ae.componente = "Matemática"
                ae.ano = ano

                ae.prefixo = dados["prefixo"]
                ae.codigo_ae = dados["codigo_ae"]
                ae.descricao = dados["descricao"]
                ae.habilidade_priorizada = dados["habilidade_priorizada"]

                atualizados += 1

                print(f"   ↺ Atualizado {ae.id_ae}")

        db.commit()

        print("\n======================================")
        print("IMPORTAÇÃO FINALIZADA")
        print("======================================")
        print(f"Inseridos : {inseridos}")
        print(f"Atualizados : {atualizados}")

    except SQLAlchemyError:

        db.rollback()
        raise

    finally:

        db.close()


if __name__ == "__main__":
    main()