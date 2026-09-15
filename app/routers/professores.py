from typing import List

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Professor, Usuario
from app.routers.common import apply_updates, get_model_or_404
from app.schemas.academico import ProfessorCreate, ProfessorRead, ProfessorUpdate

router = APIRouter(prefix="/professores", tags=["professores"])


@router.post("/", response_model=ProfessorRead, status_code=status.HTTP_201_CREATED)
def create_professor(payload: ProfessorCreate, db: Session = Depends(get_db)) -> Professor:
    usuario = get_model_or_404(db, Usuario, payload.usuario_id)
    if usuario.tipo != "professor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O usuário precisa ser do tipo 'professor' para ser vinculado.",
        )

    existing = db.scalar(select(Professor).where(Professor.usuario_id == usuario.id))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um perfil de professor para esse usuário.",
        )

    professor = Professor(**payload.dict())
    db.add(professor)
    db.commit()
    db.refresh(professor)
    return professor


@router.get("/", response_model=List[ProfessorRead])
def list_professores(db: Session = Depends(get_db)) -> List[Professor]:
    return db.scalars(select(Professor)).all()


@router.get("/{professor_id}", response_model=ProfessorRead)
def get_professor(professor_id: UUID, db: Session = Depends(get_db)) -> Professor:
    return get_model_or_404(db, Professor, professor_id)


@router.put("/{professor_id}", response_model=ProfessorRead)
def update_professor(
    professor_id: UUID, payload: ProfessorUpdate, db: Session = Depends(get_db)
) -> Professor:
    professor = get_model_or_404(db, Professor, professor_id)
    apply_updates(professor, payload)
    db.commit()
    db.refresh(professor)
    return professor


@router.delete("/{professor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_professor(professor_id: UUID, db: Session = Depends(get_db)) -> None:
    professor = get_model_or_404(db, Professor, professor_id)
    db.delete(professor)
    db.commit()
