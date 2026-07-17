from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AprendizagemEssencialBase(BaseModel):
    ae_codigo: str = Field(..., max_length=20, description="Código da AE (ex: AE1, AE2)")
    ano: int = Field(..., ge=1, le=5, description="Ano (1-5)")
    codigo_material: str = Field(..., max_length=50, description="Código do material (ex: EFAIMAT)")
    descricao: str = Field(..., description="Descrição da Aprendizagem Essencial")
    habilidade_priorizada: Optional[str] = Field(None, description="Habilidade priorizada (ex: EF01MA14)")
    habilidades_relacionadas: list[str] = Field(default_factory=list, description="Lista de habilidades relacionadas")
    conhecimentos_previos: list[str] = Field(default_factory=list, description="Lista de conhecimentos prévios")
    blocos_tematicos: list[dict[str, Any]] = Field(default_factory=list, description="Blocos temáticos estruturados")
    materiais_digitais: list[dict[str, Any]] = Field(default_factory=list, description="Materiais digitais estruturados")
    livros_estudante: list[dict[str, Any]] = Field(default_factory=list, description="Livros do estudante estruturados")
    pagina_pdf: Optional[int] = Field(None, description="Página do PDF de origem")


class AprendizagemEssencialCreate(AprendizagemEssencialBase):
    pass


class AprendizagemEssencialUpdate(BaseModel):
    ae_codigo: Optional[str] = Field(None, max_length=20)
    ano: Optional[int] = Field(None, ge=1, le=5)
    codigo_material: Optional[str] = Field(None, max_length=50)
    descricao: Optional[str] = None
    habilidade_priorizada: Optional[str] = None
    habilidades_relacionadas: Optional[list[str]] = None
    conhecimentos_previos: Optional[list[str]] = None
    blocos_tematicos: Optional[list[dict[str, Any]]] = None
    materiais_digitais: Optional[list[dict[str, Any]]] = None
    livros_estudante: Optional[list[dict[str, Any]]] = None
    pagina_pdf: Optional[int] = None


class AprendizagemEssencialRead(AprendizagemEssencialBase):
    id: UUID
    acervo_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AprendizagemEssencialListResponse(BaseModel):
    items: list[AprendizagemEssencialRead]
    total: int
    page: int
    page_size: int