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

## Autenticação

- `POST /auth/login` recebe um JSON com `email` e `senha` (pelo menos 8 caracteres) e responde com `access_token`, `refresh_token`, `token_type` e `expires_in`.
- `POST /auth/refresh` recebe `{ "refresh_token": "..." }` e retorna um novo par de tokens quando o refresh ainda estiver válido.
- O backend armazena somente `senha_hash` criptografado com bcrypt e emite JWTs assinados com o segredo definido em `JWT_SECRET_KEY`. Configure também `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` (padrão 60) e `JWT_REFRESH_TOKEN_EXPIRE_HOURS` (padrão 168) conforme sua estratégia de expiração.

Um frontend independente pode chamar `POST /auth/login` logo após ser implantado, guardar o `access_token` no armazenamento seguro e usar o header `Authorization: Bearer <token>` em todas as requisições subsequentes.

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
- Adicionei um roteador de autenticação que valida credenciais, emite JWTs de acesso/refresh e expõe os
    esquemas de login/refresh para que o frontend possa obter tokens de forma independente (app/routers/
    auth.py:46, app/routers/auth.py:64, app/schemas/auth.py:6).
  - Inseri utilitários de segurança reutilizáveis para hash bcrypt e criação/validação de JWTs (com o modelo de
    payload e expirações configuráveis), permitindo que o roteador de auth e as mutações de usuário compartilhem
    a mesma lógica (app/core/security.py:1).
  - Atualizei os schemas e CRUD de usuários para aceitar senha em texto puro, persistir como senha_hash e
    rehashear nas atualizações, garantindo que senhas nunca sejam armazenadas em texto plano (app/schemas/
    academico.py:24, app/routers/usuarios.py:17).
  - Incluí passlib[bcrypt] e python-jose[cryptography] nas dependências e documentei os novos endpoints de auth,
    além das variáveis de ambiente JWT_*, para que o frontend saiba como se autenticar (pyproject.toml:18-19,
    requirements.txt:18-19, readme.md:52).

  Próximos passos:

  1. Injete JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES e JWT_REFRESH_TOKEN_EXPIRE_HOURS via
     secrets ou variáveis do Swarm para que os tokens sejam assinados por uma chave segura.
  2. Teste os novos endpoints (por exemplo POST /auth/login) com o stack/front-end em execução para confirmar
     que os tokens funcionam nas rotas protegidas.

      Detalhamento

  - 1. Fornecer as variáveis JWT para o Swarm
      - app/core/security.py lê JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES e
        JWT_REFRESH_TOKEN_EXPIRE_HOURS. Esses valores precisam existir no ambiente onde a imagem irá rodar, e o
        jeito mais direto é declarar o environment/secrets no stack do Swarm que o deploy.yml copia.
      - Edite infra/labprovas.yaml (ou outro compose usado no deploy) para injetar essas variáveis no serviço
        apps_geduc. Exemplo:

        services:
          apps_geduc:
            image: ${DEPLOY_IMAGE}
            environment:
              - JWT_SECRET_KEY=${JWT_SECRET_KEY}
              - JWT_ALGORITHM=HS256
              - JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
              - JWT_REFRESH_TOKEN_EXPIRE_HOURS=168
        ou, preferível, use secrets do Docker Swarm (secrets: + docker secret create jwt_secret ...) e
        referencie-os no environment (ex.: JWT_SECRET_KEY_FILE=/run/secrets/jwt_secret). Ajuste os scripts/
        compose para apontar para o valor correto.
      - Garanta que os valores reais sejam fornecidos como secrets no Swarm host (via docker secret create ou
        variáveis protegidas) e, se usar GitHub vars/secrets para o deploy (ex.: vars.JWT_SECRET_KEY), atualize
        o arquivo infra/labprovas.yaml copiado para o host com placeholders substituídos antes do docker stack
        deploy.
  - 2. Testar os endpoints para dar autonomia ao frontend
      - Depois de subir a nova imagem, use algo como curl ou um cliente REST para chamar POST /auth/login com um
        usuário existente (o payload deve ser { "email": "...", "senha": "..." }). O retorno contém
        access_token, refresh_token, token_type e expires_in.
      - O frontend pode guardar o access_token em storage seguro (e o refresh_token em httpOnly cookie, se
        desejar) e incluir Authorization: Bearer <token> nas chamadas seguintes, validando o fluxo de
        autorização que você já preparou.
      - Para renovar o acesso sem obrigar logout, chame POST /auth/refresh com { "refresh_token": "..." } e
        confirme que o novo par de JWTs é emitido.

  Sobre o workflow .github/workflows/deploy.yml

  - Não é preciso alterar o workflow para suportar o JWT, desde que o infra/labprovas.yaml já inclua as
    variáveis/secretos necessários e o job de deploy copie esse arquivo atualizado para o host. O workflow só
    faz build/push e atualiza o serviço, então quem consome as variáveis são o stack e o próprio ambiente do
    Swarm.
  - Se você preferir manter os valores fora do compose (o que é recomendado), adicione secrets/vars no host e
    use docker service update --env-add ... ou .env/configs no infra/labprovas.yaml em vez de expor dados no
    repositório; o workflow não muda, apenas o conteúdo do YAML que ele copia.
  - Caso o deploy precise substituir placeholders com os valores reais antes de transferir o arquivo, você pode
    incorporar esse step antes do appleboy/scp-action (ex.: gerar um arquivo temporário com envsubst). Mas isso
    também não obriga nenhuma modificação no resto do deploy.yml se o arquivo já estiver preparado.


No infra/labprovas.yaml ajuste o serviço apps_geduc para expor a variável JWT_SECRET_KEY (de preferência via
    secret). Por exemplo:

  services:
    apps_geduc:
      image: ${DEPLOY_IMAGE}
      environment:
        - JWT_SECRET_KEY_FILE=/run/secrets/jwt_secret
      secrets:
        - jwt_secret

  secrets:
    jwt_secret:
      external: true

  - Crie o docker secret no host (docker secret create jwt_secret <arquivo-com-chave>) e garanta que o deploy
    copie o stack atualizado do infra/ para o nó; assim o FastAPI lê JWT_SECRET_KEY do arquivo referenciado em
    JWT_SECRET_KEY_FILE.
  - Não é necessário mexer no workflow: ele já copia infra/labprovas.yaml e atualiza o serviço, então basta
    garantir que o stack final inclua o secret/variável acima antes de rodar o deploy.