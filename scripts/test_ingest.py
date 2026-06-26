"""Script simples para testar o endpoint de ingestão de conteúdos."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = lambda *args, **kwargs: None  # type: ignore


def load_settings() -> dict[str, str]:
    root = Path(__file__).resolve().parent.parent
    load_dotenv(dotenv_path=root / ".env", override=False)

    return {
        "base_url": os.getenv("DEVPROVAS_BASE_URL", "http://localhost:8000"),
        "endpoint": os.getenv("DEVPROVAS_INGEST_ENDPOINT", "/aulas/conteudos"),
    }


def build_payload() -> list[dict]:
    return [
        {
            "id_aula": "TESTE-01",
            "componente": "Infraestrutura",
            "conteudo_vetor": "A aula explica como as camadas OSI e TCP/IP operam",
            "metadata": {
                "titulo": "Camadas de rede",
                "competencia": "Compreender protocolos de comunicação",
                "tem_roteiro": True,
            },
        },
        {
            "id_aula": "TESTE-02",
            "componente": "Segurança",
            "conteudo_vetor": "Vulnerações frequentes envolvem engenharia social e falta de patch",
            "metadata": {
                "titulo": "Principais riscos",
                "competencia": "Aplicar controles básicos de segurança",
                "tem_roteiro": False,
            },
        },
    ]


def main() -> int:
    settings = load_settings()
    payload = build_payload()

    url = f"{settings['base_url'].rstrip('/')}{settings['endpoint']}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    print(f"Enviando {len(payload)} aulas para {url}")
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    print("Status:", response.status_code)
    try:
        print("Resposta:", json.dumps(response.json(), ensure_ascii=False, indent=2))
    except ValueError:  # pragma: no cover
        print("Resposta não serializável como JSON:", response.text)

    return 0 if response.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
