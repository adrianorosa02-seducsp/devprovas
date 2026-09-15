from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import uuid4

from app.core.database import get_db
from app.models.models import MapaGDrive, Professor, Usuario
from app.schemas.mapa_gdrive import MapaGDriveSync, MapaGDriveRead

router = APIRouter(prefix="/mapa-gdrive", tags=["mapa-gdrive"])


@router.post("/sync", response_model=MapaGDriveRead)
def sync_mapa(payload: MapaGDriveSync, db: Session = Depends(get_db)):
    # Tenta localizar professor pelo alias (usuário.nome == alias) ou retorna 404
    usuario = db.scalar(select(Usuario).where(Usuario.nome == payload.alias_professor))
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario (alias) não encontrado")

    professor = db.scalar(select(Professor).where(Professor.usuario_id == usuario.id))
    if not professor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil de professor não encontrado para o alias fornecido")

    # Busca registro existente por professor_id
    existente = db.scalar(select(MapaGDrive).where(MapaGDrive.professor_id == professor.id))
    if existente:
        existente.estrutura = payload.estrutura
        existente.alias_professor = payload.alias_professor
        existente.ativo = True
        db.add(existente)
        db.commit()
        db.refresh(existente)
        return existente

    # Caso não exista, cria novo
    novo = MapaGDrive(
        id=uuid4(),
        professor_id=professor.id,
        alias_professor=payload.alias_professor,
        estrutura=payload.estrutura,
        ativo=True,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo
