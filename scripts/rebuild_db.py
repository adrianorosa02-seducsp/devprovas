#!/usr/bin/env python
"""Script para recriar todas as tabelas do banco de dados."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from app.models import Base
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
)


def rebuild_database():
    print("Deletando todas as tabelas...")
    Base.metadata.drop_all(bind=engine)
    print("Tabelas deletadas com sucesso.")

    print("Criando todas as tabelas...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")


if __name__ == "__main__":
    rebuild_database()