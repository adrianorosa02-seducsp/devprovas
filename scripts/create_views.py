#!/usr/bin/env python
"""Script para criar as views."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from sqlalchemy import text

VIEWS = [
    "sql/views/v_materiais_completo.sql",
    "sql/views/v_materiais_escopo_sequencia.sql",
    "sql/views/v_materiais_aprendizagens_essenciais.sql",
]

def create_views():
    with engine.connect() as conn:
        for view_file in VIEWS:
            print(f"Criando view: {view_file}")
            with open(view_file, 'r') as f:
                sql = f.read()
            conn.execute(text(sql))
            conn.commit()
        print("Todas as views criadas com sucesso!")

if __name__ == "__main__":
    create_views()