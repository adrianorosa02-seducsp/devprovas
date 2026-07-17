from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import AcervoDigital, AprendizagemEssencial
from app.schemas.aprendizagem import (
    AprendizagemEssencialCreate,
    AprendizagemEssencialListResponse,
    AprendizagemEssencialRead,
    AprendizagemEssencialUpdate,
)

router = APIRouter(prefix="/aprendizagens-essenciais", tags=["Aprendizagens Essenciais"])


@router.post("", response_model=AprendizagemEssencialRead, status_code=status.HTTP_201_CREATED)
def create_aprendizagem(
    acervo_id: UUID,
    aprendizagem: AprendizagemEssencialCreate,
    db: Session = Depends(get_db),
):
    # Verify acervo exists
    acervo = db.query(AcervoDigital).filter(AcervoDigital.id == acervo_id).first()
    if not acervo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acervo não encontrado")
    
    # Check unique constraint
    existing = db.query(AprendizagemEssencial).filter(
        AprendizagemEssencial.acervo_id == acervo_id,
        AprendizagemEssencial.ae_codigo == aprendizagem.ae_codigo,
        AprendizagemEssencial.ano == aprendizagem.ano
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"AE {aprendizagem.ae_codigo} para ano {aprendizagem.ano} já existe neste acervo"
        )
    
    db_aprendizagem = AprendizagemEssencial(
        acervo_id=acervo_id,
        **aprendizagem.model_dump()
    )
    db.add(db_aprendizagem)
    db.commit()
    db.refresh(db_aprendizagem)
    return db_aprendizagem


@router.get("", response_model=AprendizagemEssencialListResponse)
def list_aprendizagens(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por página"),
    acervo_id: Optional[UUID] = Query(None, description="Filtrar por acervo"),
    codigo_material: Optional[str] = Query(None, description="Filtrar por código do material (ex: EFAIMAT)"),
    ano: Optional[int] = Query(None, ge=1, le=5, description="Filtrar por ano (1-5)"),
    ae_codigo: Optional[str] = Query(None, description="Filtrar por código da AE (ex: AE1)"),
    db: Session = Depends(get_db),
):
    query = db.query(AprendizagemEssencial)
    
    if acervo_id:
        query = query.filter(AprendizagemEssencial.acervo_id == acervo_id)
    if codigo_material:
        query = query.filter(AprendizagemEssencial.codigo_material.ilike(f"%{codigo_material}%"))
    if ano:
        query = query.filter(AprendizagemEssencial.ano == ano)
    if ae_codigo:
        query = query.filter(AprendizagemEssencial.ae_codigo.ilike(f"%{ae_codigo}%"))
    
    total = query.count()
    items = query.order_by(
        AprendizagemEssencial.codigo_material,
        AprendizagemEssencial.ano,
        AprendizagemEssencial.ae_codigo
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    return AprendizagemEssencialListResponse(
        items=items, total=total, page=page, page_size=page_size
    )


@router.get("/{aprendizagem_id}", response_model=AprendizagemEssencialRead)
def get_aprendizagem(aprendizagem_id: UUID, db: Session = Depends(get_db)):
    aprendizagem = db.query(AprendizagemEssencial).filter(
        AprendizagemEssencial.id == aprendizagem_id
    ).first()
    if not aprendizagem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aprendizagem não encontrada")
    return aprendizagem


@router.patch("/{aprendizagem_id}", response_model=AprendizagemEssencialRead)
def update_aprendizagem(
    aprendizagem_id: UUID,
    aprendizagem_update: AprendizagemEssencialUpdate,
    db: Session = Depends(get_db),
):
    aprendizagem = db.query(AprendizagemEssencial).filter(
        AprendizagemEssencial.id == aprendizagem_id
    ).first()
    if not aprendizagem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aprendizagem não encontrada")
    
    # Check unique constraint if updating key fields
    if aprendizagem_update.ae_codigo or aprendizagem_update.ano:
        new_ae = aprendizagem_update.ae_codigo or aprendizagem.ae_codigo
        new_ano = aprendizagem_update.ano or aprendizagem.ano
        existing = db.query(AprendizagemEssencial).filter(
            AprendizagemEssencial.acervo_id == aprendizagem.acervo_id,
            AprendizagemEssencial.ae_codigo == new_ae,
            AprendizagemEssencial.ano == new_ano,
            AprendizagemEssencial.id != aprendizagem_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"AE {new_ae} para ano {new_ano} já existe neste acervo"
            )
    
    update_data = aprendizagem_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(aprendizagem, field, value)
    
    db.commit()
    db.refresh(aprendizagem)
    return aprendizagem


@router.delete("/{aprendizagem_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_aprendizagem(aprendizagem_id: UUID, db: Session = Depends(get_db)):
    aprendizagem = db.query(AprendizagemEssencial).filter(
        AprendizagemEssencial.id == aprendizagem_id
    ).first()
    if not aprendizagem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aprendizagem não encontrada")
    db.delete(aprendizagem)
    db.commit()
    return None


@router.get("/estatisticas/resumo")
def get_estatisticas(db: Session = Depends(get_db)):
    """Retorna estatísticas resumidas das aprendizagens essenciais."""
    total = db.query(func.count(AprendizagemEssencial.id)).scalar()
    
    por_material = db.query(
        AprendizagemEssencial.codigo_material,
        func.count(AprendizagemEssencial.id)
    ).group_by(AprendizagemEssencial.codigo_material).all()
    
    por_ano = db.query(
        AprendizagemEssencial.ano,
        func.count(AprendizagemEssencial.id)
    ).group_by(AprendizagemEssencial.ano).order_by(AprendizagemEssencial.ano).all()
    
    por_acervo = db.query(
        AcervoDigital.titulo,
        func.count(AprendizagemEssencial.id)
    ).join(AprendizagemEssencial).group_by(AcervoDigital.titulo).all()
    
    return {
        "total": total,
        "por_material": [{"material": m, "count": c} for m, c in por_material],
        "por_ano": [{"ano": a, "count": c} for a, c in por_ano],
        "por_acervo": [{"acervo": a, "count": c} for a, c in por_acervo],
    }