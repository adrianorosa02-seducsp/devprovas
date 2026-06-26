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

## Conteúdos vetoriais

O backend agora mantém os textos de cada aula na tabela `aulas_conteudo` e gera embeddings usando o modelo `text-embedding-3-small`. Cada registro insere ou atualiza:

| Coluna          | Origem no JSON           |
|----------------|--------------------------|
| `id_aula`      | `id_aula`                |
| `componente`   | `componente`             |
| `titulo`       | `metadata.titulo`        |
| `competencia`  | `metadata.competencia`   |
| `tem_roteiro`  | `metadata.tem_roteiro`   |
| `conteudo_bruto` | `conteudo_vetor`        |
| `embedding`    | vetor retornado pela OpenAI |


Antes de chamar o endpoint, exporte a variável de ambiente `OPENAI_API_KEY` (e `OPENAI_EMBEDDING_MODEL` caso precise outro modelo). O serviço disponível no `POST /aulas/conteudos` espera um array como este:

```json
[
  {
    "id_aula": "SISANO1C2B2S10A1",
    "componente": "Redes...",
    "conteudo_vetor": "AULA: ...",
    "metadata": {
      "titulo": "Aula 1: Formato do Quadro Ethernet",
      "competencia": "Utilizar...",
      "tem_roteiro": true
    }
  }
]
```

O endpoint gera o embedding automaticamente e grava o vetor na tabela `aulas_conteudo`, que utiliza a extensão `vector`. Basta enviar o JSON acima que a API cuida do restante.

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
## A FAZER
```
Próximos passos:

  1. Garanta que .env continue expondo OPENAI_API_KEY (e eventual DEVPROVAS_BASE_URL
     personalizado).
  2. Execute python scripts/test_ingest.py no mesmo terminal onde o backend está ativo; ele
     reportará o status e a resposta do servidor.
```