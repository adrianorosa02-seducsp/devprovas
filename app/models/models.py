import uuid
from datetime import date, datetime

from sqlalchemy import Column, String, Text, Boolean, Integer, Date, DateTime, ForeignKey, DECIMAL, CHAR, UniqueConstraint
#from sqlalchemy.dialects.postgresql import UUID, VECTOR
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector  # Note que o nome costuma ser Vector (com 'v' maiúsculo apenas no início)
from sqlalchemy.orm import relationship
from app.core.database import Base


class Escola(Base):
    __tablename__ = "escolas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(255), nullable=False)
    endereco = Column(Text)
    telefone = Column(String(20))
    email = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    usuarios = relationship("Usuario", back_populates="escola")
    turmas = relationship("Turma", back_populates="escola")
    disciplinas = relationship("Disciplina", back_populates="escola")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    tipo = Column(String(20), nullable=False)
    escola_id = Column(UUID(as_uuid=True), ForeignKey("escolas.id", ondelete="SET NULL"))
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    escola = relationship("Escola", back_populates="usuarios")
    turmas = relationship("Turma", back_populates="professor", foreign_keys="Turma.professor_id")
    provas = relationship("Prova", back_populates="professor")
    respostas = relationship("Resposta", back_populates="aluno")
    matriculas = relationship("Matricula", back_populates="aluno")


class Turma(Base):
    __tablename__ = "turmas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(100), nullable=False)
    serie = Column(String(50))
    turno = Column(String(20))
    escola_id = Column(UUID(as_uuid=True), ForeignKey("escolas.id", ondelete="CASCADE"))
    professor_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"))
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    escola = relationship("Escola", back_populates="turmas")
    professor = relationship("Usuario", back_populates="turmas", foreign_keys=[professor_id])
    matriculas = relationship("Matricula", back_populates="turma")
    provas_turmas = relationship("ProvaTurma", back_populates="turma")


class Disciplina(Base):
    __tablename__ = "disciplinas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(100), nullable=False)
    codigo = Column(String(20), unique=True)
    escola_id = Column(UUID(as_uuid=True), ForeignKey("escolas.id", ondelete="CASCADE"))
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    escola = relationship("Escola", back_populates="disciplinas")
    provas = relationship("Prova", back_populates="disciplina")


class Matricula(Base):
    __tablename__ = "matriculas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    aluno_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"))
    turma_id = Column(UUID(as_uuid=True), ForeignKey("turmas.id", ondelete="CASCADE"))
    data_matricula = Column(Date, default=date.today)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("aluno_id", "turma_id"),)

    aluno = relationship("Usuario", back_populates="matriculas")
    turma = relationship("Turma", back_populates="matriculas")


class Prova(Base):
    __tablename__ = "provas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text)
    disciplina_id = Column(UUID(as_uuid=True), ForeignKey("disciplinas.id", ondelete="SET NULL"))
    professor_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"))
    data_aplicacao = Column(Date)
    duracao_minutos = Column(Integer)
    peso = Column(DECIMAL(5, 2), default=1.0)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    disciplina = relationship("Disciplina", back_populates="provas")
    professor = relationship("Usuario", back_populates="provas")
    questoes = relationship("Questao", back_populates="prova", order_by="Questao.ordem")
    provas_turmas = relationship("ProvaTurma", back_populates="prova")


class ProvaTurma(Base):
    __tablename__ = "provas_turmas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prova_id = Column(UUID(as_uuid=True), ForeignKey("provas.id", ondelete="CASCADE"))
    turma_id = Column(UUID(as_uuid=True), ForeignKey("turmas.id", ondelete="CASCADE"))
    data_agendada = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("prova_id", "turma_id"),)

    prova = relationship("Prova", back_populates="provas_turmas")
    turma = relationship("Turma", back_populates="provas_turmas")


class Questao(Base):
    __tablename__ = "questoes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prova_id = Column(UUID(as_uuid=True), ForeignKey("provas.id", ondelete="CASCADE"))
    enunciado = Column(Text, nullable=False)
    tipo = Column(String(20), nullable=False)
    pontos = Column(DECIMAL(5, 2), default=1.0)
    ordem = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    prova = relationship("Prova", back_populates="questoes")
    alternativas = relationship("Alternativa", back_populates="questao", order_by="Alternativa.letra")
    respostas = relationship("Resposta", back_populates="questao")


class Alternativa(Base):
    __tablename__ = "alternativas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    questao_id = Column(UUID(as_uuid=True), ForeignKey("questoes.id", ondelete="CASCADE"))
    texto = Column(Text, nullable=False)
    correta = Column(Boolean, default=False)
    letra = Column(CHAR(1), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    questao = relationship("Questao", back_populates="alternativas")
    respostas = relationship("Resposta", back_populates="alternativa")


class Resposta(Base):
    __tablename__ = "respostas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    questao_id = Column(UUID(as_uuid=True), ForeignKey("questoes.id", ondelete="CASCADE"))
    aluno_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"))
    alternativa_id = Column(UUID(as_uuid=True), ForeignKey("alternativas.id", ondelete="SET NULL"))
    texto_dissertativo = Column(Text)
    nota = Column(DECIMAL(5, 2))
    corrigida = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    questao = relationship("Questao", back_populates="respostas")
    aluno = relationship("Usuario", back_populates="respostas")
    alternativa = relationship("Alternativa", back_populates="respostas")


class AulaConteudo(Base):
    __tablename__ = "aulas_conteudo"

    id = Column(Integer, primary_key=True)
    id_aula = Column(String(50), unique=True, nullable=False)
    componente = Column(Text, nullable=False)
    titulo = Column(Text)
    competencia = Column(Text)
    tem_roteiro = Column(Boolean, default=False, nullable=False)
    conteudo_bruto = Column(Text, nullable=False)
    embedding = Column(VECTOR(1536))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
