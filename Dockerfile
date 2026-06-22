FROM python:3.14-slim

WORKDIR /app

# instala poetry
RUN pip install poetry

# desativa venv dentro do container
RUN poetry config virtualenvs.create false

# copia dependências primeiro (cache layer)
COPY pyproject.toml poetry.lock* ./

# instala dependências
RUN poetry install --no-interaction --no-ansi

# copia aplicação
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
