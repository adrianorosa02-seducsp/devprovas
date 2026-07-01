from typing import List

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Prova, Questao
from app.routers.common import apply_updates, get_model_or_404
from app.schemas.academico import QuestaoCreate, QuestaoRead, QuestaoUpdate

router = APIRouter(prefix="/questoes", tags=["questoes"])


def _validate_prova(db: Session, prova_id: UUID) -> None:
    get_model_or_404(db, Prova, prova_id)


@router.post("/", response_model=QuestaoRead, status_code=status.HTTP_201_CREATED)
def create_questao(payload: QuestaoCreate, db: Session = Depends(get_db)) -> Questao:
    _validate_prova(db, payload.prova_id)
    questao = Questao(**payload.dict())
    db.add(questao)
    db.commit()
    db.refresh(questao)
    return questao


@router.get("/", response_model=List[QuestaoRead])
def list_questoes(db: Session = Depends(get_db)) -> List[Questao]:
    return db.scalars(select(Questao)).all()


@router.get("/{questao_id}", response_model=QuestaoRead)
def get_questao(questao_id: UUID, db: Session = Depends(get_db)) -> Questao:
    return get_model_or_404(db, Questao, questao_id)


@router.put("/{questao_id}", response_model=QuestaoRead)
def update_questao(
    questao_id: UUID, payload: QuestaoUpdate, db: Session = Depends(get_db)
) -> Questao:
    questao = get_model_or_404(db, Questao, questao_id)
    if payload.prova_id is not None:
        _validate_prova(db, payload.prova_id)
    apply_updates(questao, payload)
    db.commit()
    db.refresh(questao)
    return questao


@router.delete("/{questao_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_questao(questao_id: UUID, db: Session = Depends(get_db)) -> None:
    questao = get_model_or_404(db, Questao, questao_id)
    db.delete(questao)
    db.commit()
