import requests
from sqlalchemy.orm import Session
from app.models import MaterialDidatico
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJMT0dJTiI6InJnMjAwOTU0MjM0c3AiLCJOSUNLTkFNRSI6IkFEUklBTk9KVVNUSU4yMDA5NTQyIiwiQ0RfVVNVQVJJTyI6IjEwMDAwMDA5Njk2ODAwIiwidW5pcXVlX25hbWUiOiJQRVJGSVMiLCJQRVJGSVMiOiJbe1wiQ0RfUEVSRklMXCI6XCI0XCIsXCJOTV9QRVJGSUxcIjpcIlByb2Zlc3NvclwiLFwiTlJfQ09NUE9SVEFNRU5UT1wiOlwiNFwiLFwiQ09NUE9SVEFNRU5UT1wiOlwiUHJvZmVzc29yXCJ9LHtcIkNEX1BFUkZJTFwiOlwiMTY1MVwiLFwiTk1fUEVSRklMXCI6XCJQcm9mZXNzb3IgLSAgQXVsYSBFdmVudHVhbFwiLFwiTlJfQ09NUE9SVEFNRU5UT1wiOlwiNFwiLFwiQ09NUE9SVEFNRU5UT1wiOlwiUHJvZmVzc29yXCJ9LHtcIkNEX1BFUkZJTFwiOlwiMTY3NFwiLFwiTk1fUEVSRklMXCI6XCJQQUVFVC0gUHJvZmVzc29yIGRlIEFwb2lvIGFvIEVuc2lubyBUw6ljbmljbyBcIixcIk5SX0NPTVBPUlRBTUVOVE9cIjpcIjNcIixcIkNPTVBPUlRBTUVOVE9cIjpcIkVzY29sYVwifV0iLCJOQU1FIjoiQURSSUFOTyBKVVNUSU5PIFJPU0EiLCJNRVRPRE9MT0dJTiI6IkdPVkJSIiwiQ1BGIjoiMTEwNTczODE4MzciLCJFTUFJTCI6ImFkcmlhbm9AaWRlYWwudHVyLmJyIiwibmJmIjoxNzgzNjIyMTI3LCJleHAiOjE3ODM3MDg1MjcsImlhdCI6MTc4MzYyMjEyN30.pNuSWwTUPhG0cyCtEbYKFcjAnR1FS6qNywSMUZUk9zE"
def carregar_dados_sed_teste(db: Session, token: str):
    url = "https://sedintegracoes.educacao.sp.gov.br/apirepocmsp/api/materiais-digitais/materiaisdigitais"
    
    # Parâmetros que você identificou no seu payload
    params = {
        "Ano": "2026",
        "Bimestre": "3",
        "Componente": "13",
        "Serie": "1",
        "TipoEnsino": "1"
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        materiais = response.json()
        print(f"Carga OK. Recebidos {len(materiais)} itens.")
        
        for item in materiais:
            # Lógica de gravação conforme definimos (usando o contexto do params)
            novo_mat = MaterialDidatico(
                ano_referencia=int(params["Ano"]),
                bimestre=int(params["Bimestre"]),
                serie=params["Serie"],
                componente=params["Componente"],
                cod_cronograma=item['codCronogramaAula'],
                id_cronograma=item['idCronogramaAula'],
                titulo=item['titulo'],
                ordenacao=item['ordenacao'],
                arquivos=item.get('arquivos', [])
            )
            db.add(novo_mat)
        
        db.commit()
        print("Dados gravados no PostgreSQL com sucesso.")
    else:
        print(f"Erro: {response.status_code} - {response.text}")