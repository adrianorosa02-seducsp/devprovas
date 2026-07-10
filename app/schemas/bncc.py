from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel


class BnccEtapaRead(BaseModel):
    id: UUID
    nome: str
    nivel: str
    descricao: Optional[str]
    fonte: Optional[str]
    ordenacao: Optional[int]
    dados: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class BnccConteudoRead(BaseModel):
    id: UUID
    etapa_id: UUID
    parent_id: Optional[UUID]
    tipo: str
    titulo: str
    codigo: Optional[str]
    descricao: Optional[str]
    ordem: Optional[int]
    dados: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class BnccCompetenciaRead(BaseModel):
    id: UUID
    etapa_id: UUID
    conteudo_id: Optional[UUID]
    tipo: str
    codigo: Optional[str]
    nome: Optional[str]
    descricao: Optional[str]
    ordem: Optional[int]
    dados: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
