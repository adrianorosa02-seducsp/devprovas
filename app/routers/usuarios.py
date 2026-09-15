from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password
from app.models.models import Usuario
from app.routers.common import apply_updates, get_model_or_404
from app.schemas.academico import UsuarioCreate, UsuarioRead, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post("/", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def create_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)) -> Usuario:
    # Compatibilidade segura para Pydantic v1 e v2
    dump_method = getattr(payload, "model_dump", None) or payload.dict
    usuario_data = dump_method(exclude={"senha"})
    
    usuario = Usuario(**usuario_data, senha_hash=hash_password(payload.senha))
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.get("/", response_model=List[UsuarioRead])
def list_usuarios(db: Session = Depends(get_db)) -> List[Usuario]:
    return db.scalars(select(Usuario)).all()


@router.get("/{usuario_id}", response_model=UsuarioRead)
def get_usuario(usuario_id: UUID, db: Session = Depends(get_db)) -> Usuario:
    return get_model_or_404(db, Usuario, usuario_id)


@router.put("/{usuario_id}", response_model=UsuarioRead)
def update_usuario(
    usuario_id: UUID, payload: UsuarioUpdate, db: Session = Depends(get_db)
) -> Usuario:
    usuario = get_model_or_404(db, Usuario, usuario_id)
    update_data = payload.dict(exclude_unset=True)
    senha = update_data.pop("senha", None)
    if senha:
        usuario.senha_hash = hash_password(senha)
    if update_data:
        apply_updates(usuario, UsuarioUpdate(**update_data))
    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario(usuario_id: UUID, db: Session = Depends(get_db)) -> None:
    usuario = get_model_or_404(db, Usuario, usuario_id)
    db.delete(usuario)
    db.commit()
