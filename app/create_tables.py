import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from app.core.database import engine, Base
from app.models.models import *


def create_tables():
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS devprovas;"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")


if __name__ == "__main__":
    create_tables()
