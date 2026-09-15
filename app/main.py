import logging
import uuid
from fastapi import FastAPI, Request, status, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from app.core.database import async_engine, get_db
from app.models.models import ConfiguracaoImportacaoHorarios, HorarioAulaExtrator
from app.services.extrator_horarios import obter_dfs_consolidados
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
    painel_router,
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
app.include_router(painel_router)


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


@app.post("/escolas/{escola_id}/importar-horarios")
def importar_horarios(escola_id: uuid.UUID, db: Session = Depends(get_db)):
    config = db.query(ConfiguracaoImportacaoHorarios).filter(ConfiguracaoImportacaoHorarios.escola_id == escola_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuração de importação não encontrada para esta escola.")
    
    if not config.ativo:
        raise HTTPException(status_code=400, detail="A importação de horários está desativada para esta escola.")

    if config.tipo_importacao != "PDF":
        raise HTTPException(status_code=501, detail="No momento, apenas o tipo 'PDF' é suportado automaticamente.")
        
    if not config.fonte_dados:
        raise HTTPException(status_code=400, detail="A fonte de dados (URL do PDF) não está configurada.")

    try:
        # Extrair dados usando o serviço
        dfs = obter_dfs_consolidados(config.fonte_dados)
        
        # Limpar os horários antigos desta escola
        db.query(HorarioAulaExtrator).filter(HorarioAulaExtrator.escola_id == escola_id).delete()
        
        # Inserir novos horários
        dias_banco = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex']
        aulas_inseridas = 0
        
        for turma_id, df in dfs.items():
            colunas_dias = [col for col in df.columns if col in dias_banco]
            if not colunas_dias:
                continue
                
            horario_col = 'Horário' if 'Horário' in df.columns else df.columns[0]
            
            subject_row = None
            for index, row in df.iterrows():
                if index % 2 == 0:
                    subject_row = row
                else:
                    teacher_row = row
                    horario_val = str(subject_row[horario_col]).strip()
                    if horario_val == 'None' or not horario_val:
                        continue
                        
                    for dia in dias_banco:
                        if dia in subject_row and dia in teacher_row:
                            disciplina = str(subject_row[dia]).strip()
                            professor = str(teacher_row[dia]).strip()
                            
                            if disciplina and disciplina != 'None' and professor and professor != 'None':
                                nova_aula = HorarioAulaExtrator(
                                    escola_id=escola_id,
                                    dia_semana=dia,
                                    horario=horario_val,
                                    turma=turma_id,
                                    disciplina=disciplina,
                                    professor=professor
                                )
                                db.add(nova_aula)
                                aulas_inseridas += 1
                                
        db.commit()
        return {"status": "sucesso", "mensagem": f"{aulas_inseridas} aulas importadas e salvas com sucesso."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao processar a importação: {str(e)}")
