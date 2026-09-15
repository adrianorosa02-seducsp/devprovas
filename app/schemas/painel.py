from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class PainelConfiguracaoCreate(BaseModel):
    escola_id: UUID
    nome: str = Field(..., max_length=255)
    intervalo_sincronizacao_minutos: int = Field(default=15, ge=1, le=1440)
    ativo: bool = True


class PainelConfiguracaoUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=255)
    intervalo_sincronizacao_minutos: Optional[int] = Field(None, ge=1, le=1440)
    ativo: Optional[bool] = None


class PainelConfiguracaoRead(PainelConfiguracaoCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FonteGradeCreate(BaseModel):
    configuracao_id: UUID
    nome: str = Field(..., max_length=255)
    turno: Optional[str] = Field(None, max_length=20)
    url_google_drive: HttpUrl
    ativo: bool = True


class FonteGradeRead(FonteGradeCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SalaCreate(BaseModel):
    escola_id: UUID
    nome: str = Field(..., max_length=100)
    codigo: Optional[str] = Field(None, max_length=50)
    ativo: bool = True


class SalaRead(SalaCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlataformaCreate(BaseModel):
    configuracao_id: UUID
    ordem: int = Field(..., ge=1, le=3)
    nome: str = Field(..., max_length=100)
    tipo: str = Field(default="link", max_length=30)
    url: Optional[HttpUrl] = None
    conteudo: Optional[str] = None
    ativo: bool = True


class PlataformaRead(PlataformaCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MensagemPainelCreate(BaseModel):
    configuracao_id: UUID
    titulo: str = Field(..., max_length=255)
    conteudo: str
    prioridade: int = 0
    inicia_em: Optional[datetime] = None
    termina_em: Optional[datetime] = None
    ativo: bool = True


class MensagemPainelRead(MensagemPainelCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HorarioAulaCreate(BaseModel):
    configuracao_id: UUID
    turma_id: UUID
    disciplina_id: Optional[UUID] = None
    professor_id: Optional[UUID] = None
    sala_id: Optional[UUID] = None
    dia_semana: int = Field(..., ge=1, le=7)
    turno: str = Field(..., max_length=20)
    hora_inicio: str = Field(..., pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    hora_fim: str = Field(..., pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    disciplina_codigo_original: Optional[str] = Field(None, max_length=20)
    ativo: bool = True


class HorarioAulaRead(HorarioAulaCreate):
    id: UUID
    importacao_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ImportacaoGradeCreate(BaseModel):
    configuracao_id: UUID
    fonte_id: UUID


class ImportacaoGradeRead(BaseModel):
    id: UUID
    configuracao_id: UUID
    fonte_id: Optional[UUID] = None
    url_origem: str
    status: str
    hash_arquivo: Optional[str] = None
    detalhes: Optional[dict] = None
    erro: Optional[str] = None
    iniciado_em: Optional[datetime] = None
    concluido_em: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PainelHorarioRead(BaseModel):
    id: UUID
    turma_id: UUID
    turma_nome: str
    sala_nome: Optional[str] = None
    disciplina_nome: Optional[str] = None
    disciplina_codigo: Optional[str] = None
    professor_nome: Optional[str] = None
    turno: str
    hora_inicio: str
    hora_fim: str
    status: str


class PainelTurmaRead(BaseModel):
    turma_id: UUID
    turma_nome: str
    turno: Optional[str] = None
    horarios: list[PainelHorarioRead]


class PainelDashboardRead(BaseModel):
    data: str
    dia_semana: int
    turno: Optional[str] = None
    atualizado_em: datetime
    turmas: list[PainelTurmaRead]
