from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import AcervoDigital
from app.schemas.acervo import AcervoDigitalCreate, AcervoDigitalListResponse, AcervoDigitalRead, AcervoDigitalUpdate

router = APIRouter(prefix="/acervo-digital", tags=["Acervo Digital"])


@router.post("", response_model=AcervoDigitalRead, status_code=status.HTTP_201_CREATED)
def create_acervo(acervo: AcervoDigitalCreate, db: Session = Depends(get_db)):
    existing = db.query(AcervoDigital).filter(AcervoDigital.arquivo_id == acervo.arquivo_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="arquivo_id já cadastrado")
    db_acervo = AcervoDigital(**acervo.model_dump())
    db.add(db_acervo)
    db.commit()
    db.refresh(db_acervo)
    return db_acervo


@router.get("", response_model=AcervoDigitalListResponse)
def list_acervo(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por página"),
    titulo: Optional[str] = Query(None, description="Filtrar por título (busca parcial)"),
    arquivo_id: Optional[str] = Query(None, description="Filtrar por ID do arquivo"),
    tipo_arquivo: Optional[str] = Query(None, description="Filtrar por tipo de arquivo"),
    db: Session = Depends(get_db),
):
    query = db.query(AcervoDigital)
    if titulo:
        query = query.filter(AcervoDigital.titulo.ilike(f"%{titulo}%"))
    if arquivo_id:
        query = query.filter(AcervoDigital.arquivo_id == arquivo_id)
    if tipo_arquivo:
        query = query.filter(AcervoDigital.tipo_arquivo.ilike(f"%{tipo_arquivo}%"))
    
    total = query.count()
    items = query.order_by(AcervoDigital.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return AcervoDigitalListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{acervo_id}", response_model=AcervoDigitalRead)
def get_acervo(acervo_id: UUID, db: Session = Depends(get_db)):
    acervo = db.query(AcervoDigital).filter(AcervoDigital.id == acervo_id).first()
    if not acervo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acervo não encontrado")
    return acervo


@router.patch("/{acervo_id}", response_model=AcervoDigitalRead)
def update_acervo(acervo_id: UUID, acervo_update: AcervoDigitalUpdate, db: Session = Depends(get_db)):
    acervo = db.query(AcervoDigital).filter(AcervoDigital.id == acervo_id).first()
    if not acervo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acervo não encontrado")
    
    if acervo_update.arquivo_id:
        existing = db.query(AcervoDigital).filter(
            AcervoDigital.arquivo_id == acervo_update.arquivo_id,
            AcervoDigital.id != acervo_id
        ).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="arquivo_id já cadastrado")
    
    update_data = acervo_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(acervo, field, value)
    
    db.commit()
    db.refresh(acervo)
    return acervo


@router.delete("/{acervo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_acervo(acervo_id: UUID, db: Session = Depends(get_db)):
    acervo = db.query(AcervoDigital).filter(AcervoDigital.id == acervo_id).first()
    if not acervo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acervo não encontrado")
    db.delete(acervo)
    db.commit()
    return None