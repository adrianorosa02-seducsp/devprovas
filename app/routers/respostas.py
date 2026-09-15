from typing import List, Optional

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Alternativa, Questao, Resposta, Usuario
from app.routers.common import apply_updates, get_model_or_404
from app.schemas.academico import RespostaCreate, RespostaRead, RespostaUpdate

router = APIRouter(prefix="/respostas", tags=["respostas"])


def _validate_aluno(db: Session, aluno_id: UUID) -> Usuario:
    aluno = get_model_or_404(db, Usuario, aluno_id)
    if aluno.tipo != "aluno":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Somente alunos podem registrar respostas.",
        )
    return aluno


def _validate_references(db: Session, payload: RespostaCreate | RespostaUpdate) -> None:
    if isinstance(payload, RespostaCreate):
        get_model_or_404(db, Questao, payload.questao_id)
        _validate_aluno(db, payload.aluno_id)
    else:
        if payload.questao_id is not None:
            get_model_or_404(db, Questao, payload.questao_id)
        if payload.aluno_id is not None:
            _validate_aluno(db, payload.aluno_id)

    if payload.alternativa_id is not None:
        get_model_or_404(db, Alternativa, payload.alternativa_id)


@router.post("/", response_model=RespostaRead, status_code=status.HTTP_201_CREATED)
def create_resposta(payload: RespostaCreate, db: Session = Depends(get_db)) -> Resposta:
    _validate_references(db, payload)
    resposta = Resposta(**payload.dict())
    db.add(resposta)
    db.commit()
    db.refresh(resposta)
    return resposta


@router.get("/", response_model=List[RespostaRead])
def list_respostas(db: Session = Depends(get_db)) -> List[Resposta]:
    return db.scalars(select(Resposta)).all()


@router.get("/{resposta_id}", response_model=RespostaRead)
def get_resposta(resposta_id: UUID, db: Session = Depends(get_db)) -> Resposta:
    return get_model_or_404(db, Resposta, resposta_id)


@router.put("/{resposta_id}", response_model=RespostaRead)
def update_resposta(
    resposta_id: UUID, payload: RespostaUpdate, db: Session = Depends(get_db)
) -> Resposta:
    resposta = get_model_or_404(db, Resposta, resposta_id)
    _validate_references(db, payload)
    apply_updates(resposta, payload)
    db.commit()
    db.refresh(resposta)
    return resposta


@router.delete("/{resposta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resposta(resposta_id: UUID, db: Session = Depends(get_db)) -> None:
    resposta = get_model_or_404(db, Resposta, resposta_id)
    db.delete(resposta)
    db.commit()
