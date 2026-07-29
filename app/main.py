import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from app.core.database import async_engine
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
    mapa_gdrive_router,
)
from app.admin import create_admin

# Configuração básica de logging do Python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="DevProvas API", version="0.1.0")

# --- Inicializa Admin ---
create_admin(app, engine=async_engine)

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

# --- TRATAMENTO CUSTOMIZADO DE ERROS (LOGS DETALHADOS) ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Captura erros de validação do Pydantic ( payloads incorretos )"""
    logger.error(f"Erro de Validação Pydantic na rota {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "message": "Erro de validação nos dados enviados."},
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Captura erros relacionados ao banco de dados"""
    logger.error(f"Erro de Banco de Dados na rota {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno no banco de dados.", "error": str(exc)},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Captura qualquer outro erro 500 inesperado"""
    logger.error(f"Erro Interno Não Tratado na rota {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno inesperado no servidor.", "error": str(exc)},
    )

# --------------------------------------------------------

# Inclusão das rotas
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
app.include_router(mapa_gdrive_router)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health():
    try:
        with async_engine.sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except OperationalError:
        return {"status": "unhealthy", "database": "disconnected"}