from hashlib import sha256
from hashlib import sha256
from io import BytesIO
from urllib.parse import parse_qs, urlparse

import pdfplumber
import requests


class GradeImportError(RuntimeError):
    pass


def normalizar_url_google_drive(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc not in {"drive.google.com", "www.drive.google.com"}:
        return url

    file_id = None
    path_parts = parsed.path.strip("/").split("/")
    if "d" in path_parts:
        index = path_parts.index("d")
        if index + 1 < len(path_parts):
            file_id = path_parts[index + 1]
    if not file_id:
        file_id = parse_qs(parsed.query).get("id", [None])[0]
    if not file_id:
        raise GradeImportError("Não foi possível identificar o arquivo no link do Google Drive.")
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def baixar_e_analisar_pdf(url: str) -> tuple[str, dict]:
    url = normalizar_url_google_drive(url)
    try:
        resposta = requests.get(url, timeout=60)
        resposta.raise_for_status()
    except requests.RequestException as exc:
        raise GradeImportError(f"Não foi possível baixar o PDF: {exc}") from exc

    if not resposta.content.startswith(b"%PDF"):
        raise GradeImportError("A URL não retornou um arquivo PDF válido.")

    hash_arquivo = sha256(resposta.content).hexdigest()
    try:
        with pdfplumber.open(BytesIO(resposta.content)) as pdf:
            paginas = []
            for numero, pagina in enumerate(pdf.pages, start=1):
                texto = pagina.extract_text() or ""
                paginas.append({"pagina": numero, "caracteres": len(texto)})
    except Exception as exc:
        raise GradeImportError(f"Não foi possível ler o PDF: {exc}") from exc

    return hash_arquivo, {
        "paginas": len(paginas),
        "paginas_textuais": sum(1 for pagina in paginas if pagina["caracteres"] > 0),
        "detalhes_paginas": paginas,
    }
