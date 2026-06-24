# DevProvas

Sistema de gerenciamento de provas educacionais.

## Stack

- **Backend:** FastAPI
- **Banco:** PostgreSQL
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic

## Pré-requisitos

- Python 3.12+
- Poetry
- PostgreSQL

## Setup

```bash
# Instalar dependências
poetry install

# Ativar ambiente virtual
poetry shell

# Configurar variáveis de ambiente (opcional)
# Copie e edite o arquivo .env
```

## Banco de Dados

### Criar as tabelas manualmente via SQL

```bash
psql -U postgres -d devprovas -f sql/schema.sql
```

### Ou usar o script Python

```bash
python app/create_tables.py
```

### Ou usar Alembic

```bash
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

## Executar

```bash
uvicorn app.main:app --reload
```

Acesse http://localhost:8000/docs para a documentação interativa.

## Estrutura do Projeto

```
app/
├── core/
│   └── database.py        # Configuração do SQLAlchemy
├── models/
│   ├── __init__.py
│   └── models.py          # Modelos ORM
├── create_tables.py       # Script para criar tabelas
└── main.py               # Aplicação FastAPI
sql/
└── schema.sql            # Schema SQL puro
alembic/                   # Migrations
├── versions/
├── env.py
└── script.py.mako
alembic.ini
```
