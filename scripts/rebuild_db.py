#!/usr/bin/env python
"""Script para recriar todas as tabelas do banco de dados."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from app.models import Base
from sqlalchemy import text
from app.models.models import (
    Escola,
    Usuario,
    Professor,
    Disciplina,
    Turma,
    Matricula,
    Prova,
    ProvaTurma,
    Questao,
    Alternativa,
    Resposta,
    MaterialDidatico,
    AprendizagemEssencial,
    EscopoSequencia,
)


def rebuild_database():
    print("Deletando views dependentes...")
    with engine.connect() as conn:
        for schema in ['devprovas', 'public']:
            conn.execute(text(f"DROP VIEW IF EXISTS {schema}.v_materiais_completo CASCADE"))
            conn.execute(text(f"DROP VIEW IF EXISTS {schema}.v_materiais_escopo_sequencia CASCADE"))
            conn.execute(text(f"DROP VIEW IF EXISTS {schema}.v_materiais_aprendizagens_essenciais CASCADE"))
        conn.commit()
    print("Views deletadas.")

    print("Deletando todas as tabelas...")
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA devprovas CASCADE"))
        conn.execute(text("CREATE SCHEMA devprovas"))
        conn.commit()
    print("Schema recriado.")

    print("Criando todas as tabelas...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")


if __name__ == "__main__":
    rebuild_database()