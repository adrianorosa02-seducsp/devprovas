from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from app.core.database import engine
from app.routers import (
    aulas_router,
    auth_router,
    bncc_router,
    disciplinas_router,
    escolas_router,
    professores_router,
    provas_router,
    questoes_router,
    respostas_router,
    turmas_router,
    usuarios_router,
)

app = FastAPI(title="DevProvas API", version="0.1.0")
app.include_router(aulas_router)
app.include_router(auth_router)
app.include_router(bncc_router)
app.include_router(usuarios_router)
app.include_router(professores_router)
app.include_router(disciplinas_router)
app.include_router(escolas_router)
app.include_router(turmas_router)
app.include_router(provas_router)
app.include_router(questoes_router)
app.include_router(respostas_router)


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
