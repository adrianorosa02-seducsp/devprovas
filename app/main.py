from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from starlette.middleware.sessions import SessionMiddleware
from app.core.database import engine
from app.routers import (
    acervo_router,
    aprendizagem_router,
    auth_router,
    disciplinas_router,
    escolas_router,
    materiais_router,
    professores_router,
    provas_router,
    questoes_router,
    respostas_router,
    turmas_router,
    usuarios_router,
)
from app.admin import create_admin

app = FastAPI(title="DevProvas API", version="0.1.0")

# --- CONFIGURAÇÃO DE CORS ---
origins = [
    "https://lab.inetz.com.br",
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ----------------------------

# Session middleware para SQLAdmin auth
app.add_middleware(
    SessionMiddleware,
    secret_key="dev-secret-change-in-production",
    session_cookie="devprovas_admin_session",
    max_age=3600,
)

# Inicializa SQLAdmin
admin = create_admin(app, engine)

app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(professores_router)
app.include_router(provas_router)
app.include_router(questoes_router)
app.include_router(respostas_router)
app.include_router(turmas_router)
app.include_router(escolas_router)
app.include_router(disciplinas_router)
app.include_router(materiais_router)
app.include_router(acervo_router)
app.include_router(aprendizagem_router)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except OperationalError:
        return {"status": "unhealthy", "database": "disconnected"}
