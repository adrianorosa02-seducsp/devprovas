FROM python:3.14-slim

WORKDIR /app

# instala dependências de sistema necessárias para o pandas e manipulação de imagem do pdfplumber
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# instala poetry
RUN pip install poetry

# desativa venv dentro do container
RUN poetry config virtualenvs.create false

# copia dependências primeiro (cache layer)
    COPY pyproject.toml poetry.lock* ./
    
    # copia código da aplicação (necessário para poetry instalar o pacote geduc)
    COPY app ./app
    
    # instala dependências
    RUN poetry install --no-interaction --no-ansi
    
    # cache bust para forçar rebuild da aplicação
    ARG CACHE_DATE=2026-06-29
    
    # copia restante da aplicação
    COPY . .
RUN ls -R /app
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
