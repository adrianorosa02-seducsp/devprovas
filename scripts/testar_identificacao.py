from io import BytesIO

import requests
import pdfplumber

from app.extractors.identificacao_extractor import IdentificacaoExtractor


url = "https://drive.google.com/uc?export=download&id=1AfZ2UMTkuvpbG6ie3T_cIiu9iOknpnVx"

dados = BytesIO(requests.get(url).content)

pdf = pdfplumber.open(dados)

# Página 16 (índice 15)
page = pdf.pages[15]

extractor = IdentificacaoExtractor()

resultado = extractor.extrair(page)

print(resultado)