from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, condecimal

TipoUsuario = Literal["admin", "professor", "aluno"]
TipoQuestao = Literal["multipla_escolha", "dissertativa", "verdadeiro_falso"]
Turno = Literal["manha", "tarde", "noite"]

DecimalField = condecimal(max_digits=5, decimal_places=2)


class UsuarioBase(BaseModel):
    nome: str = Field(..., max_length=255)
    email: EmailStr
    tipo: TipoUsuario
    escola_id: Optional[UUID] = None
    ativo: bool = True


class UsuarioCreate(UsuarioBase):
    senha_hash: str = Field(..., min_length=8)


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    senha_hash: Optional[str] = Field(None, min_length=8)
    tipo: Optional[TipoUsuario] = None
    escola_id: Optional[UUID] = None
    ativo: Optional[bool] = None


class UsuarioRead(UsuarioBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ProfessorBase(BaseModel):
    usuario_id: UUID
    escola_id: Optional[UUID] = None
    formacao: Optional[str] = None
    especialidade: Optional[str] = None
    ativo: bool = True


class ProfessorCreate(ProfessorBase):
    pass


class ProfessorUpdate(BaseModel):
    escola_id: Optional[UUID] = None
    formacao: Optional[str] = None
    especialidade: Optional[str] = None
    ativo: Optional[bool] = None


class ProfessorRead(ProfessorBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class DisciplinaBase(BaseModel):
    nome: str = Field(..., max_length=100)
    codigo: Optional[str] = Field(None, max_length=20)
    escola_id: Optional[UUID] = None
    ativo: bool = True


class DisciplinaCreate(DisciplinaBase):
    pass


class DisciplinaUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=100)
    codigo: Optional[str] = Field(None, max_length=20)
    escola_id: Optional[UUID] = None
    ativo: Optional[bool] = None


class DisciplinaRead(DisciplinaBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TurmaBase(BaseModel):
    nome: str = Field(..., max_length=100)
    serie: Optional[str] = None
    turno: Optional[Turno] = None
    escola_id: Optional[UUID] = None
    professor_id: Optional[UUID] = None
    ativo: bool = True


class TurmaCreate(TurmaBase):
    pass


class TurmaUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=100)
    serie: Optional[str] = None
    turno: Optional[Turno] = None
    escola_id: Optional[UUID] = None
    professor_id: Optional[UUID] = None
    ativo: Optional[bool] = None


class TurmaRead(TurmaBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ProvaBase(BaseModel):
    titulo: str = Field(..., max_length=255)
    descricao: Optional[str] = None
    disciplina_id: Optional[UUID] = None
    professor_id: Optional[UUID] = None
    data_aplicacao: Optional[date] = None
    duracao_minutos: Optional[int] = None
    peso: DecimalField = Field(default=1)
    ativo: bool = True


class ProvaCreate(ProvaBase):
    pass


class ProvaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, max_length=255)
    descricao: Optional[str] = None
    disciplina_id: Optional[UUID] = None
    professor_id: Optional[UUID] = None
    data_aplicacao: Optional[date] = None
    duracao_minutos: Optional[int] = None
    peso: Optional[DecimalField] = None
    ativo: Optional[bool] = None


class ProvaRead(ProvaBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class QuestaoBase(BaseModel):
    prova_id: UUID
    enunciado: str
    tipo: TipoQuestao
    pontos: DecimalField = Field(default=1)
    ordem: int


class QuestaoCreate(QuestaoBase):
    pass


class QuestaoUpdate(BaseModel):
    prova_id: Optional[UUID] = None
    enunciado: Optional[str] = None
    tipo: Optional[TipoQuestao] = None
    pontos: Optional[DecimalField] = None
    ordem: Optional[int] = None


class QuestaoRead(QuestaoBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class RespostaBase(BaseModel):
    questao_id: UUID
    aluno_id: UUID
    alternativa_id: Optional[UUID] = None
    texto_dissertativo: Optional[str] = None
    nota: Optional[DecimalField] = None
    corrigida: bool = False


class RespostaCreate(RespostaBase):
    pass


class RespostaUpdate(BaseModel):
    questao_id: Optional[UUID] = None
    aluno_id: Optional[UUID] = None
    alternativa_id: Optional[UUID] = None
    texto_dissertativo: Optional[str] = None
    nota: Optional[DecimalField] = None
    corrigida: Optional[bool] = None


class RespostaRead(RespostaBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class EscolaBase(BaseModel):
    nome: str = Field(..., max_length=255)
    endereco: Optional[str] = None
    telefone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None


class EscolaCreate(EscolaBase):
    pass


class EscolaUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=255)
    endereco: Optional[str] = None
    telefone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None


class EscolaRead(EscolaBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
