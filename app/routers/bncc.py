from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import BnccCompetencia, BnccConteudo, BnccEtapa
from app.routers.common import get_model_or_404
from app.schemas.bncc import (
    BnccCompetenciaRead,
    BnccConteudoRead,
    BnccEtapaRead,
)

router = APIRouter(prefix="/bncc", tags=["bncc"])


@router.get("/etapas", response_model=List[BnccEtapaRead])
def list_etapas(db: Session = Depends(get_db)) -> List[BnccEtapa]:
    stmt = select(BnccEtapa).order_by(BnccEtapa.ordenacao, BnccEtapa.nome)
    return db.scalars(stmt).all()


@router.get("/etapas/{etapa_id}", response_model=BnccEtapaRead)
def get_etapa(etapa_id: UUID, db: Session = Depends(get_db)) -> BnccEtapa:
    return get_model_or_404(db, BnccEtapa, etapa_id)


@router.get("/conteudos", response_model=List[BnccConteudoRead])
def list_conteudos(
    etapa_id: Optional[UUID] = None,
    tipo: Optional[str] = None,
    codigo: Optional[str] = None,
    db: Session = Depends(get_db),
) -> List[BnccConteudo]:
    stmt = select(BnccConteudo)
    if etapa_id:
        stmt = stmt.where(BnccConteudo.etapa_id == etapa_id)
    if tipo:
        stmt = stmt.where(BnccConteudo.tipo.ilike(f"%{tipo}%"))
    if codigo:
        stmt = stmt.where(BnccConteudo.codigo.ilike(f"%{codigo}%"))
    stmt = stmt.order_by(BnccConteudo.etapa_id, BnccConteudo.ordem, BnccConteudo.titulo)
    return db.scalars(stmt).all()


@router.get("/conteudos/{conteudo_id}", response_model=BnccConteudoRead)
def get_conteudo(conteudo_id: UUID, db: Session = Depends(get_db)) -> BnccConteudo:
    return get_model_or_404(db, BnccConteudo, conteudo_id)


@router.get("/competencias", response_model=List[BnccCompetenciaRead])
def list_competencias(
    etapa_id: Optional[UUID] = None,
    conteudo_id: Optional[UUID] = None,
    tipo: Optional[str] = None,
    codigo: Optional[str] = None,
    db: Session = Depends(get_db),
) -> List[BnccCompetencia]:
    stmt = select(BnccCompetencia)
    if etapa_id:
        stmt = stmt.where(BnccCompetencia.etapa_id == etapa_id)
    if conteudo_id:
        stmt = stmt.where(BnccCompetencia.conteudo_id == conteudo_id)
    if tipo:
        stmt = stmt.where(BnccCompetencia.tipo.ilike(f"%{tipo}%"))
    if codigo:
        stmt = stmt.where(BnccCompetencia.codigo.ilike(f"%{codigo}%"))
    stmt = stmt.order_by(BnccCompetencia.etapa_id, BnccCompetencia.ordem, BnccCompetencia.codigo, BnccCompetencia.nome)
    return db.scalars(stmt).all()


@router.get("/competencias/{competencia_id}", response_model=BnccCompetenciaRead)
def get_competencia(competencia_id: UUID, db: Session = Depends(get_db)) -> BnccCompetencia:
    return get_model_or_404(db, BnccCompetencia, competencia_id)
