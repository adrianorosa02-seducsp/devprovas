from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Escola
from app.routers.common import apply_updates, get_model_or_404
from app.schemas.academico import EscolaCreate, EscolaRead, EscolaUpdate

router = APIRouter(prefix="/escolas", tags=["escolas"])


@router.post("/", response_model=EscolaRead, status_code=status.HTTP_201_CREATED)
def create_escola(payload: EscolaCreate, db: Session = Depends(get_db)) -> Escola:
    escola = Escola(**payload.dict())
    db.add(escola)
    db.commit()
    db.refresh(escola)
    return escola


@router.get("/", response_model=List[EscolaRead])
def list_escolas(db: Session = Depends(get_db)) -> List[Escola]:
    return db.scalars(select(Escola)).all()


@router.get("/{escola_id}", response_model=EscolaRead)
def get_escola(escola_id: UUID, db: Session = Depends(get_db)) -> Escola:
    return get_model_or_404(db, Escola, escola_id)


@router.put("/{escola_id}", response_model=EscolaRead)
def update_escola(
    escola_id: UUID, payload: EscolaUpdate, db: Session = Depends(get_db)
) -> Escola:
    escola = get_model_or_404(db, Escola, escola_id)
    apply_updates(escola, payload)
    db.commit()
    db.refresh(escola)
    return escola


@router.delete("/{escola_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_escola(escola_id: UUID, db: Session = Depends(get_db)) -> None:
    escola = get_model_or_404(db, Escola, escola_id)
    db.delete(escola)
    db.commit()
