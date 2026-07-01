from typing import List

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Disciplina
from app.routers.common import apply_updates, get_model_or_404
from app.schemas.academico import DisciplinaCreate, DisciplinaRead, DisciplinaUpdate

router = APIRouter(prefix="/disciplinas", tags=["disciplinas"])


@router.post("/", response_model=DisciplinaRead, status_code=status.HTTP_201_CREATED)
def create_disciplina(payload: DisciplinaCreate, db: Session = Depends(get_db)) -> Disciplina:
    disciplina = Disciplina(**payload.dict())
    db.add(disciplina)
    db.commit()
    db.refresh(disciplina)
    return disciplina


@router.get("/", response_model=List[DisciplinaRead])
def list_disciplinas(db: Session = Depends(get_db)) -> List[Disciplina]:
    return db.scalars(select(Disciplina)).all()


@router.get("/{disciplina_id}", response_model=DisciplinaRead)
def get_disciplina(disciplina_id: UUID, db: Session = Depends(get_db)) -> Disciplina:
    return get_model_or_404(db, Disciplina, disciplina_id)


@router.put("/{disciplina_id}", response_model=DisciplinaRead)
def update_disciplina(
    disciplina_id: UUID, payload: DisciplinaUpdate, db: Session = Depends(get_db)
) -> Disciplina:
    disciplina = get_model_or_404(db, Disciplina, disciplina_id)
    apply_updates(disciplina, payload)
    db.commit()
    db.refresh(disciplina)
    return disciplina


@router.delete("/{disciplina_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_disciplina(disciplina_id: UUID, db: Session = Depends(get_db)) -> None:
    disciplina = get_model_or_404(db, Disciplina, disciplina_id)
    db.delete(disciplina)
    db.commit()
