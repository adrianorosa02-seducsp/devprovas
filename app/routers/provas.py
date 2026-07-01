from typing import List, Optional

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Disciplina, Professor, Prova
from app.routers.common import apply_updates, get_model_or_404
from app.schemas.academico import ProvaCreate, ProvaRead, ProvaUpdate

router = APIRouter(prefix="/provas", tags=["provas"])


def _validate_professor(db: Session, professor_id: Optional[UUID]) -> None:
    if professor_id is not None:
        get_model_or_404(db, Professor, professor_id)


def _validate_disciplina(db: Session, disciplina_id: Optional[UUID]) -> None:
    if disciplina_id is not None:
        get_model_or_404(db, Disciplina, disciplina_id)


@router.post("/", response_model=ProvaRead, status_code=status.HTTP_201_CREATED)
def create_prova(payload: ProvaCreate, db: Session = Depends(get_db)) -> Prova:
    _validate_professor(db, payload.professor_id)
    _validate_disciplina(db, payload.disciplina_id)
    prova = Prova(**payload.dict())
    db.add(prova)
    db.commit()
    db.refresh(prova)
    return prova


@router.get("/", response_model=List[ProvaRead])
def list_provas(db: Session = Depends(get_db)) -> List[Prova]:
    return db.scalars(select(Prova)).all()


@router.get("/{prova_id}", response_model=ProvaRead)
def get_prova(prova_id: UUID, db: Session = Depends(get_db)) -> Prova:
    return get_model_or_404(db, Prova, prova_id)


@router.put("/{prova_id}", response_model=ProvaRead)
def update_prova(
    prova_id: UUID, payload: ProvaUpdate, db: Session = Depends(get_db)
) -> Prova:
    prova = get_model_or_404(db, Prova, prova_id)
    _validate_professor(db, payload.professor_id)
    _validate_disciplina(db, payload.disciplina_id)
    apply_updates(prova, payload)
    db.commit()
    db.refresh(prova)
    return prova


@router.delete("/{prova_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prova(prova_id: UUID, db: Session = Depends(get_db)) -> None:
    prova = get_model_or_404(db, Prova, prova_id)
    db.delete(prova)
    db.commit()
