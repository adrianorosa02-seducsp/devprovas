#!/usr/bin/env python
"""Teste simples de conexão com a API SED."""

import requests
import os

# Token pode vir de variável de ambiente ou ser colado aqui
TOKEN = os.getenv("SED_TOKEN") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJMT0dJTiI6InJnMjAwOTU0MjM0c3AiLCJOSUNLTkFNRSI6IkFEUklBTk9KVVNUSU4yMDA5NTQyIiwiQ0RfVVNVQVJJTyI6IjEwMDAwMDA5Njk2ODAwIiwidW5pcXVlX25hbWUiOiJQRVJGSVMiLCJQRVJGSVMiOiJbe1wiQ0RfUEVSRklMXCI6XCI0XCIsXCJOTV9QRVJGSUxcIjpcIlByb2Zlc3NvclwiLFwiTlJfQ09NUE9SVEFNRU5UT1wiOlwiNFwiLFwiQ09NUE9SVEFNRU5UT1wiOlwiUHJvZmVzc29yXCJ9LHtcIkNEX1BFUkZJTFwiOlwiMTY1MVwiLFwiTk1fUEVSRklMXCI6XCJQcm9mZXNzb3IgLSAgQXVsYSBFdmVudHVhbFwiLFwiTlJfQ09NUE9SVEFNRU5UT1wiOlwiNFwiLFwiQ09NUE9SVEFNRU5UT1wiOlwiUHJvZmVzc29yXCJ9LHtcIkNEX1BFUkZJTFwiOlwiMTY3NFwiLFwiTk1fUEVSRklMXCI6XCJQQUVFVC0gUHJvZmVzc29yIGRlIEFwb2lvIGFvIEVuc2lubyBUw6ljbmljbyBcIixcIk5SX0NPTVBPUlRBTUVOVE9cIjpcIjNcIixcIkNPTVBPUlRBTUVOVE9cIjpcIkVzY29sYVwifV0iLCJOQU1FIjoiQURSSUFOTyBKVVNUSU5PIFJPU0EiLCJNRVRPRE9MT0dJTiI6IkdPVkJSIiwiQ1BGIjoiMTEwNTczODE4MzciLCJFTUFJTCI6ImFkcmlhbm9AaWRlYWwudHVyLmJyIiwibmJmIjoxNzgzNjM2ODUzLCJleHAiOjE3ODM3MjMyNTMsImlhdCI6MTc4MzYzNjg1M30.ByJFGdY8W0qRbHtwwJ88BWEwxQQk5OhkjWCDkCvP5T8"

URL = "https://sedintegracoes.educacao.sp.gov.br/apirepocmsp/api/materiais-digitais/materiaisdigitais"

params = {
    "Ano": "2026",
    "Bimestre": "3",
    "Componente": "13",
    "Serie": "1",
    "TipoEnsino": "1"
}

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print(f"Testando API: {URL}")
print(f"Token: {TOKEN[:20]}..." if TOKEN != "COLE_SEU_TOKEN_AQUI" else "Token: NÃO DEFINIDO")
print("-" * 50)

try:
    response = requests.get(URL, params=params, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Tamanho resposta: {len(response.text)} chars")
    print("-" * 50)
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"JSON válido - {len(data) if isinstance(data, list) else 'objeto'} itens")
            if isinstance(data, list) and data:
                print(f"Primeiro item: {data[0]}")
        except Exception as e:
            print(f"Erro ao parsear JSON: {e}")
            print(f"Resposta bruta: {response.text[:500]}")
    elif response.status_code == 403:
        print("403 Forbidden - Verificar se token expirou ou IP bloqueado")
        print(f"Resposta: {response.text[:500]}")
    elif response.status_code == 401:
        print("401 Unauthorized - Token inválido/expirado")
    else:
        print(f"Resposta: {response.text[:500]}")

except requests.exceptions.Timeout:
    print("Timeout - API não respondeu em 30s")
except requests.exceptions.ConnectionError as e:
    print(f"Erro de conexão: {e}")
except Exception as e:
    print(f"Erro inesperado: {e}")