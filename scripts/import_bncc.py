from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.models import BnccCompetencia, BnccConteudo, BnccEtapa

BNCC_DIR = BASE_DIR / "bncc"
CODE_REGEX = re.compile(r"^\(([^)]+)\)\s*(.+)", re.UNICODE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Importa os dados BNCC para o banco DevProvas.")
    parser.add_argument(
        "--no-clear",
        action="store_false",
        dest="clear",
        help="Não limpa as tabelas BNCC antes de popular (risco de duplicação).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Não realiza commit no banco após a importação (bom para testes).",
    )
    return parser.parse_args()


def load_json(filename: str) -> dict[str, Any]:
    path = BNCC_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Arquivo BNCC ausente: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def split_codigo(text: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    if not text:
        return None, None
    match = CODE_REGEX.match(text.strip())
    if not match:
        return None, text.strip()
    return match.group(1).strip(), match.group(2).strip()


def clear_bncc_tables(session: Session) -> None:
    session.execute(delete(BnccCompetencia))
    session.execute(delete(BnccConteudo))
    session.execute(delete(BnccEtapa))
    session.commit()


def ensure_etapa(
    session: Session,
    nome: str,
    nivel: str,
    descricao: Optional[str] = None,
    ordenacao: Optional[int] = None,
    dados: Optional[Dict[str, Any]] = None,
) -> BnccEtapa:
    etapa = session.scalar(select(BnccEtapa).where(BnccEtapa.nome == nome))
    if etapa:
        return etapa
    etapa = BnccEtapa(
        nome=nome,
        nivel=nivel,
        descricao=descricao,
        ordenacao=ordenacao,
        dados=dados,
    )
    session.add(etapa)
    session.flush()
    return etapa


def create_conteudo(
    session: Session,
    etapa: BnccEtapa,
    tipo: str,
    titulo: Optional[str] = None,
    descricao: Optional[str] = None,
    codigo: Optional[str] = None,
    parent: Optional[BnccConteudo] = None,
    dados: Optional[Dict[str, Any]] = None,
    ordem: Optional[int] = None,
) -> BnccConteudo:
    titulo_final = titulo or f"{tipo}"
    conteudo = BnccConteudo(
        etapa=etapa,
        tipo=tipo,
        titulo=titulo_final[:255],
        descricao=descricao,
        codigo=codigo,
        parent=parent,
        dados=dados,
        ordem=ordem,
    )
    session.add(conteudo)
    session.flush()
    return conteudo


def create_competencia(
    session: Session,
    etapa: BnccEtapa,
    tipo: str,
    descricao: str,
    nome: Optional[str] = None,
    codigo: Optional[str] = None,
    conteudo: Optional[BnccConteudo] = None,
    dados: Optional[Dict[str, Any]] = None,
    ordem: Optional[int] = None,
) -> BnccCompetencia:
    nome_final = nome or descricao or ""
    competencia = BnccCompetencia(
        etapa=etapa,
        conteudo=conteudo,
        tipo=tipo,
        descricao=descricao,
        nome=nome_final[:255],
        codigo=codigo,
        dados=dados,
        ordem=ordem,
    )
    session.add(competencia)
    return competencia


def import_general_competencias(session: Session) -> None:
    payload = load_json("geral_competencias.json")
    geral = payload.get("comp_gerais", {})
    etapa_geral = ensure_etapa(
        session,
        geral.get("nome_competencia", "Competências Gerais"),
        "geral",
        descricao="Competências Gerais da BNCC.",
        ordenacao=0,
        dados={"fonte": "geral_competencias.json", "secao": "comp_gerais"},
    )

    conteudo = create_conteudo(
        session,
        etapa_geral,
        tipo="grupo_competencias_gerais",
        titulo=geral.get("nome_competencia"),
        dados=geral,
    )
    for idx, texto in enumerate(geral.get("competencias", [])):
        codigo, descricao = split_codigo(texto)
        create_competencia(
            session,
            etapa_geral,
            tipo="competencia_geral",
            descricao=descricao or texto,
            codigo=codigo,
            conteudo=conteudo,
            ordem=idx + 1,
            dados={"raw": texto},
        )

    etapa_fundamental = ensure_etapa(
        session,
        "Ensino Fundamental",
        "fundamental",
        descricao="Competências específicas do Ensino Fundamental.",
        ordenacao=2,
        dados={"fonte": "geral_competencias.json", "secao": "comp_fundamental"},
    )
    for key, bloco in payload.get("comp_fundamental", {}).items():
        conteudo = create_conteudo(
            session,
            etapa_fundamental,
            tipo="competencia_especifica",
            titulo=bloco.get("nome_competencia"),
            dados={"bloco": key},
        )
        for idx, texto in enumerate(bloco.get("competencias", [])):
            codigo, descricao = split_codigo(texto)
            create_competencia(
                session,
                etapa_fundamental,
                tipo="competencia_especifica",
                descricao=descricao or texto,
                codigo=codigo,
                conteudo=conteudo,
                ordem=idx + 1,
                dados={"raw": texto},
            )

    etapa_medio = ensure_etapa(
        session,
        "Ensino Médio",
        "medio",
        descricao="Competências específicas do Ensino Médio.",
        ordenacao=3,
        dados={"fonte": "geral_competencias.json", "secao": "comp_medio"},
    )
    for key, bloco in payload.get("comp_medio", {}).items():
        conteudo = create_conteudo(
            session,
            etapa_medio,
            tipo="competencia_especifica",
            titulo=bloco.get("nome_competencia"),
            dados={"bloco": key},
        )
        for idx, texto in enumerate(bloco.get("competencias", [])):
            codigo, descricao = split_codigo(texto)
            create_competencia(
                session,
                etapa_medio,
                tipo="competencia_especifica",
                descricao=descricao or texto,
                codigo=codigo,
                conteudo=conteudo,
                ordem=idx + 1,
                dados={"raw": texto},
            )


def import_infantil(session: Session) -> None:
    payload = load_json("geral_educacao_infantil.json")
    etapa_info = payload["educacao_infantil"]
    etapa = ensure_etapa(
        session,
        etapa_info.get("nome_etapa", "Educação Infantil"),
        "infantil",
        descricao="Base BNCC da Educação Infantil",
        ordenacao=1,
        dados={"fonte": "geral_educacao_infantil.json"},
    )

    for idx, direito in enumerate(etapa_info.get("direitos_aprendizagem", []), start=1):
        titulo = direito.get("descricao", "").strip()
        create_conteudo(
            session,
            etapa,
            tipo="direito_aprendizagem",
            titulo=titulo[:255] or f"Direito de aprendizagem {idx}",
            descricao=titulo,
            dados=direito,
            ordem=idx,
        )

    for idx, campo in enumerate(etapa_info.get("campos_experiencia", []), start=1):
        campo_conteudo = create_conteudo(
            session,
            etapa,
            tipo="campo_experiencia",
            titulo=campo.get("nome_campo"),
            dados=campo,
            ordem=idx,
        )
        for faixa_idx, faixa in enumerate(campo.get("faixas_etarias", []), start=1):
            faixa_conteudo = create_conteudo(
                session,
                etapa,
                tipo="faixa_etaria",
                titulo=faixa.get("nome_faixa"),
                parent=campo_conteudo,
                dados=faixa,
                ordem=faixa_idx,
            )
            for obj_idx, objetivo in enumerate(faixa.get("objetivos", []), start=1):
                codigo = objetivo.get("codigo")
                descricao = objetivo.get("descricao")
                create_competencia(
                    session,
                    etapa,
                    tipo="objetivo_campo_experiencia",
                    descricao=descricao or "",
                    nome=descricao,
                    codigo=codigo,
                    conteudo=faixa_conteudo,
                    ordem=obj_idx,
                    dados=objetivo,
                )


def import_fundamental(session: Session) -> None:
    payload = load_json("geral_ensino_fundamental.json")
    etapa = ensure_etapa(
        session,
        "Ensino Fundamental",
        "fundamental",
        descricao="Base BNCC do Ensino Fundamental",
        ordenacao=2,
        dados={"fonte": "geral_ensino_fundamental.json"},
    )

    for disciplina_key, disciplina in payload.items():
        disc_conteudo = create_conteudo(
            session,
            etapa,
            tipo="disciplina",
            titulo=disciplina.get("nome_disciplina", disciplina_key),
            codigo=disciplina_key,
            dados=disciplina,
        )
        for ano_idx, ano_data in enumerate(disciplina.get("ano", []), start=1):
            nome_ano = ", ".join(nome for nome in ano_data.get("nome_ano", []))
            ano_conteudo = create_conteudo(
                session,
                etapa,
                tipo="ano",
                titulo=nome_ano or f"Ano {ano_idx}",
                parent=disc_conteudo,
                dados=ano_data,
                ordem=ano_idx,
            )
            for unidade_idx, unidade in enumerate(ano_data.get("unidades_tematicas", []), start=1):
                unidade_conteudo = create_conteudo(
                    session,
                    etapa,
                    tipo="unidade_tematica",
                    titulo=unidade.get("nome_unidade"),
                    parent=ano_conteudo,
                    dados=unidade,
                    ordem=unidade_idx,
                )
                for objeto_idx, objeto in enumerate(unidade.get("objeto_conhecimento", []), start=1):
                    objeto_conteudo = create_conteudo(
                        session,
                        etapa,
                        tipo="objeto_conhecimento",
                        titulo=objeto.get("nome_objeto"),
                        parent=unidade_conteudo,
                        dados=objeto,
                        ordem=objeto_idx,
                    )
                    for hab_idx, habilidade in enumerate(objeto.get("habilidades", []), start=1):
                        codigo, descricao = split_codigo(habilidade.get("nome_habilidade"))
                        create_competencia(
                            session,
                            etapa,
                            tipo="habilidade",
                            descricao=descricao or habilidade.get("nome_habilidade", ""),
                            nome=descricao,
                            codigo=codigo,
                            conteudo=objeto_conteudo,
                            ordem=hab_idx,
                            dados=habilidade,
                        )


def import_medio(session: Session) -> None:
    payload = load_json("geral_ensino_medio.json")
    etapa = ensure_etapa(
        session,
        "Ensino Médio",
        "medio",
        descricao="Base BNCC do Ensino Médio",
        ordenacao=3,
        dados={"fonte": "geral_ensino_medio.json"},
    )

    for disciplina_key, disciplina in payload.items():
        disc_conteudo = create_conteudo(
            session,
            etapa,
            tipo="disciplina",
            titulo=disciplina.get("nome_disciplina", disciplina_key),
            codigo=disciplina_key,
            dados=disciplina,
        )
        for ano_idx, ano_data in enumerate(disciplina.get("ano", []), start=1):
            nome_ano = ", ".join(nome for nome in ano_data.get("nome_ano", []))
            ano_conteudo = create_conteudo(
                session,
                etapa,
                tipo="ano",
                titulo=nome_ano or f"Ano {ano_idx}",
                parent=disc_conteudo,
                dados=ano_data,
                ordem=ano_idx,
            )
            for codigo_idx, item in enumerate(ano_data.get("codigo_habilidade", []), start=1):
                codigo = item.get("nome_codigo")
                habilidade_text = item.get("nome_habilidade")
                _, descricao = split_codigo(habilidade_text)
                create_competencia(
                    session,
                    etapa,
                    tipo="habilidade",
                    descricao=descricao or habilidade_text or "",
                    nome=descricao,
                    codigo=codigo,
                    conteudo=ano_conteudo,
                    ordem=codigo_idx,
                    dados=item,
                )


def main() -> int:
    if not BNCC_DIR.exists():
        print("Diretório bncc/ não encontrado. Coloque os arquivos .json na raiz do projeto.")
        return 1

    args = parse_args()
    session = SessionLocal()

    try:
        if args.clear:
            clear_bncc_tables(session)
        import_general_competencias(session)
        import_infantil(session)
        import_fundamental(session)
        import_medio(session)
        if args.dry_run:
            session.rollback()
            print("Execução em dry-run concluída. Nenhum commit foi realizado.")
        else:
            session.commit()
            print("Importação dos dados BNCC concluída com sucesso.")
        return 0
    except Exception as exc:  # pragma: no cover
        session.rollback()
        print("Falha durante a importação:", exc)
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
