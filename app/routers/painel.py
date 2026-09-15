from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.models import FonteGrade, HorarioAula, ImportacaoGrade, MensagemPainel, PainelConfiguracao, Plataforma, Sala
from app.routers.common import apply_updates, get_model_or_404
from app.schemas.painel import FonteGradeCreate, FonteGradeRead, HorarioAulaCreate, HorarioAulaRead, ImportacaoGradeCreate, ImportacaoGradeRead, MensagemPainelCreate, MensagemPainelRead, PainelConfiguracaoCreate, PainelConfiguracaoRead, PainelConfiguracaoUpdate, PainelDashboardRead, PlataformaCreate, PlataformaRead, SalaCreate, SalaRead
from app.services.grade_importer import GradeImportError, baixar_e_analisar_pdf

router = APIRouter(prefix="/painel", tags=["painel"])


def criar(db: Session, model, payload):
    item = model(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def validar_configuracao(db: Session, configuracao_id: UUID):
    return get_model_or_404(db, PainelConfiguracao, configuracao_id)


@router.post("/configuracoes", response_model=PainelConfiguracaoRead, status_code=201)
def criar_configuracao(payload: PainelConfiguracaoCreate, db: Session = Depends(get_db)):
    return criar(db, PainelConfiguracao, payload)


@router.get("/configuracoes", response_model=List[PainelConfiguracaoRead])
def listar_configuracoes(db: Session = Depends(get_db)):
    return db.scalars(select(PainelConfiguracao)).all()


@router.put("/configuracoes/{configuracao_id}", response_model=PainelConfiguracaoRead)
def atualizar_configuracao(configuracao_id: UUID, payload: PainelConfiguracaoUpdate, db: Session = Depends(get_db)):
    item = get_model_or_404(db, PainelConfiguracao, configuracao_id)
    apply_updates(item, payload)
    db.commit()
    db.refresh(item)
    return item


@router.post("/fontes", response_model=FonteGradeRead, status_code=201)
def criar_fonte(payload: FonteGradeCreate, db: Session = Depends(get_db)):
    validar_configuracao(db, payload.configuracao_id)
    return criar(db, FonteGrade, payload)


@router.get("/fontes", response_model=List[FonteGradeRead])
def listar_fontes(configuracao_id: UUID, db: Session = Depends(get_db)):
    return db.scalars(select(FonteGrade).where(FonteGrade.configuracao_id == configuracao_id)).all()


@router.post("/salas", response_model=SalaRead, status_code=201)
def criar_sala(payload: SalaCreate, db: Session = Depends(get_db)):
    return criar(db, Sala, payload)


@router.get("/salas", response_model=List[SalaRead])
def listar_salas(escola_id: UUID, db: Session = Depends(get_db)):
    return db.scalars(select(Sala).where(Sala.escola_id == escola_id, Sala.ativo.is_(True))).all()


@router.post("/plataformas", response_model=PlataformaRead, status_code=201)
def criar_plataforma(payload: PlataformaCreate, db: Session = Depends(get_db)):
    validar_configuracao(db, payload.configuracao_id)
    return criar(db, Plataforma, payload)


@router.get("/plataformas", response_model=List[PlataformaRead])
def listar_plataformas(configuracao_id: UUID, db: Session = Depends(get_db)):
    return db.scalars(select(Plataforma).where(Plataforma.configuracao_id == configuracao_id, Plataforma.ativo.is_(True)).order_by(Plataforma.ordem)).all()


@router.post("/mensagens", response_model=MensagemPainelRead, status_code=201)
def criar_mensagem(payload: MensagemPainelCreate, db: Session = Depends(get_db)):
    validar_configuracao(db, payload.configuracao_id)
    return criar(db, MensagemPainel, payload)


@router.get("/mensagens", response_model=List[MensagemPainelRead])
def listar_mensagens(configuracao_id: UUID, db: Session = Depends(get_db)):
    agora = datetime.utcnow()
    return db.scalars(select(MensagemPainel).where(MensagemPainel.configuracao_id == configuracao_id, MensagemPainel.ativo.is_(True), (MensagemPainel.inicia_em.is_(None) | (MensagemPainel.inicia_em <= agora)), (MensagemPainel.termina_em.is_(None) | (MensagemPainel.termina_em >= agora))).order_by(MensagemPainel.prioridade.desc())).all()


@router.post("/horarios", response_model=HorarioAulaRead, status_code=201)
def criar_horario(payload: HorarioAulaCreate, db: Session = Depends(get_db)):
    validar_configuracao(db, payload.configuracao_id)
    return criar(db, HorarioAula, payload)


@router.get("/horarios", response_model=List[HorarioAulaRead])
def listar_horarios(configuracao_id: UUID, dia_semana: int, db: Session = Depends(get_db)):
    return db.scalars(select(HorarioAula).where(HorarioAula.configuracao_id == configuracao_id, HorarioAula.dia_semana == dia_semana, HorarioAula.ativo.is_(True)).order_by(HorarioAula.turma_id, HorarioAula.hora_inicio)).all()


@router.post("/importacoes", response_model=ImportacaoGradeRead, status_code=201)
def importar_grade(payload: ImportacaoGradeCreate, db: Session = Depends(get_db)):
    configuracao = validar_configuracao(db, payload.configuracao_id)
    fonte = get_model_or_404(db, FonteGrade, payload.fonte_id)
    if fonte.configuracao_id != configuracao.id:
        raise HTTPException(status_code=400, detail="A fonte não pertence à configuração informada.")
    item = ImportacaoGrade(configuracao_id=configuracao.id, fonte_id=fonte.id, url_origem=str(fonte.url_google_drive), status="processando", iniciado_em=datetime.utcnow())
    db.add(item)
    db.commit()
    try:
        item.hash_arquivo, item.detalhes = baixar_e_analisar_pdf(item.url_origem)
        item.status = "concluida"
    except GradeImportError as exc:
        item.status = "erro"
        item.erro = str(exc)
    item.concluido_em = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return item


@router.get("/importacoes", response_model=List[ImportacaoGradeRead])
def listar_importacoes(configuracao_id: UUID, db: Session = Depends(get_db)):
    return db.scalars(select(ImportacaoGrade).where(ImportacaoGrade.configuracao_id == configuracao_id).order_by(ImportacaoGrade.created_at.desc())).all()


@router.get("/dashboard", response_model=PainelDashboardRead)
def dashboard(configuracao_id: UUID, db: Session = Depends(get_db)):
    agora = datetime.now()
    horarios = db.scalars(select(HorarioAula).options(joinedload(HorarioAula.turma), joinedload(HorarioAula.sala), joinedload(HorarioAula.disciplina), joinedload(HorarioAula.professor)).where(HorarioAula.configuracao_id == configuracao_id, HorarioAula.dia_semana == agora.isoweekday(), HorarioAula.ativo.is_(True)).order_by(HorarioAula.turma_id, HorarioAula.hora_inicio)).unique().all()
    grupos = {}
    for horario in horarios:
        inicio = datetime.combine(agora.date(), datetime.strptime(horario.hora_inicio, "%H:%M").time())
        fim = datetime.combine(agora.date(), datetime.strptime(horario.hora_fim, "%H:%M").time())
        estado = "em_andamento" if inicio <= agora < fim else "concluida" if agora >= fim else "proxima" if (inicio - agora).total_seconds() <= 900 else "futura"
        professor = horario.professor.usuario.nome if horario.professor and horario.professor.usuario else None
        grupos.setdefault(horario.turma_id, {"turma_id": horario.turma_id, "turma_nome": horario.turma.nome, "turno": horario.turno, "horarios": []})["horarios"].append({"id": horario.id, "turma_id": horario.turma_id, "turma_nome": horario.turma.nome, "sala_nome": horario.sala.nome if horario.sala else None, "disciplina_nome": horario.disciplina.nome if horario.disciplina else None, "disciplina_codigo": horario.disciplina.codigo if horario.disciplina else horario.disciplina_codigo_original, "professor_nome": professor, "turno": horario.turno, "hora_inicio": horario.hora_inicio, "hora_fim": horario.hora_fim, "status": estado})
    return {"data": agora.date().isoformat(), "dia_semana": agora.isoweekday(), "turno": None, "atualizado_em": agora, "turmas": list(grupos.values())}
