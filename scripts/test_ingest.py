"""Script simples para testar o endpoint de ingestão de conteúdos."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib import error, request

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
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(url, data=body, headers=headers, method="POST")

    try:
        with request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            status = resp.status
    except error.HTTPError as exc:
        status = exc.code
        content = exc.read().decode("utf-8", errors="replace")
    except error.URLError as exc:
        print("Falha ao conectar:", exc.reason)
        return 1

    print("Status:", status)
    try:
        decoded = json.loads(content)
        print("Resposta:", json.dumps(decoded, ensure_ascii=False, indent=2))
    except ValueError:
        print("Resposta não serializável como JSON:", content)

    return 0 if status < 400 else 1


if __name__ == "__main__":
    raise SystemExit(main())
