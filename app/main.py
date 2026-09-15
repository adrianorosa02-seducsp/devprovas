from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from app.core.database import engine, get_db
from app.models.models import ConfiguracaoImportacaoHorarios, HorarioAula
from app.services.extrator_horarios import obter_dfs_consolidados
import uuid

app = FastAPI(title="DevProvas API", version="0.1.0")


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
        db.query(HorarioAula).filter(HorarioAula.escola_id == escola_id).delete()
        
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
                                nova_aula = HorarioAula(
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
