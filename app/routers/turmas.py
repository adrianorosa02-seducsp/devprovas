from typing import List

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Professor, Turma
from app.routers.common import apply_updates, get_model_or_404
from app.schemas.academico import TurmaCreate, TurmaRead, TurmaUpdate

router = APIRouter(prefix="/turmas", tags=["turmas"])


def _validate_professor(db: Session, professor_id: UUID | None) -> None:
    if professor_id is None:
        return
    get_model_or_404(db, Professor, professor_id)


@router.post("/", response_model=TurmaRead, status_code=status.HTTP_201_CREATED)
def create_turma(payload: TurmaCreate, db: Session = Depends(get_db)) -> Turma:
    _validate_professor(db, payload.professor_id)
    turma = Turma(**payload.dict())
    db.add(turma)
    db.commit()
    db.refresh(turma)
    return turma


@router.get("/", response_model=List[TurmaRead])
def list_turmas(db: Session = Depends(get_db)) -> List[Turma]:
    return db.scalars(select(Turma)).all()


@router.get("/{turma_id}", response_model=TurmaRead)
def get_turma(turma_id: UUID, db: Session = Depends(get_db)) -> Turma:
    return get_model_or_404(db, Turma, turma_id)


@router.put("/{turma_id}", response_model=TurmaRead)
def update_turma(turma_id: UUID, payload: TurmaUpdate, db: Session = Depends(get_db)) -> Turma:
    turma = get_model_or_404(db, Turma, turma_id)
    _validate_professor(db, payload.professor_id)
    apply_updates(turma, payload)
    db.commit()
    db.refresh(turma)
    return turma


@router.delete("/{turma_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_turma(turma_id: UUID, db: Session = Depends(get_db)) -> None:
    turma = get_model_or_404(db, Turma, turma_id)
    db.delete(turma)
    db.commit()
