from __future__ import annotations

from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field


class MaterialArquivo(BaseModel):
    idCronograma: int
    idArquivo: int
    nomeArquivo: str
    linkDownload: str
    baixou: bool
    utilizou: bool
    avaliou: bool
    ativo: bool
    dtArquivo: datetime
    tipoArquivo: int


class MaterialDidaticoBase(BaseModel):
    ano_referencia: int
    bimestre: int = Field(ge=1, le=4)
    serie: str
    componente: str
    cod_cronograma: int
    id_cronograma: int
    titulo: Optional[str] = None
    referencia_id: Optional[int] = None
    tipo: Optional[str] = None
    ordenacao: Optional[int] = None
    semana: Optional[int] = None
    aulas_com_tarefa: Optional[bool] = None
    link_url_youtube: Optional[str] = None
    exibir_municipio: Optional[bool] = None
    arquivos: list[MaterialArquivo] = Field(default_factory=list)
    array_links_youtube: Optional[str] = None


class MaterialDidaticoCreate(MaterialDidaticoBase):
    pass


class MaterialDidaticoUpdate(BaseModel):
    titulo: Optional[str] = None
    referencia_id: Optional[int] = None
    tipo: Optional[str] = None
    ordenacao: Optional[int] = None
    semana: Optional[int] = None
    aulas_com_tarefa: Optional[bool] = None
    link_url_youtube: Optional[str] = None
    exibir_municipio: Optional[bool] = None
    arquivos: Optional[list[MaterialArquivo]] = None
    array_links_youtube: Optional[str] = None


class MaterialDidaticoRead(MaterialDidaticoBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class MaterialDidaticoFilters(BaseModel):
    ano_referencia: Optional[int] = None
    bimestre: Optional[int] = Field(None, ge=1, le=4)
    serie: Optional[str] = None
    componente: Optional[str] = None
    tipo: Optional[str] = None
    semana: Optional[int] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=500)