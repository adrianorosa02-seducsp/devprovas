from app.extractors.identificacao_extractor import IdentificacaoExtractor

extractor = IdentificacaoExtractor()

dados = extractor.extrair(page)

print(dados)