import uuid
from datetime import date, datetime

from sqlalchemy import Column, String, Text, Boolean, Integer, Date, DateTime, ForeignKey, DECIMAL, CHAR, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
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
    professores = relationship("Professor", back_populates="escola")


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
    professor_profile = relationship("Professor", back_populates="usuario", uselist=False)
    respostas = relationship("Resposta", back_populates="aluno")
    matriculas = relationship("Matricula", back_populates="aluno")


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


class Professor(Base):
    __tablename__ = "professores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, unique=True)
    escola_id = Column(UUID(as_uuid=True), ForeignKey("escolas.id", ondelete="CASCADE"))
    formacao = Column(Text)
    especialidade = Column(Text)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="professor_profile")
    escola = relationship("Escola", back_populates="professores")
    turmas = relationship("Turma", back_populates="professor")
    provas = relationship("Prova", back_populates="professor")


class Turma(Base):
    __tablename__ = "turmas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(100), nullable=False)
    serie = Column(String(50))
    turno = Column(String(20))
    escola_id = Column(UUID(as_uuid=True), ForeignKey("escolas.id", ondelete="CASCADE"))
    professor_id = Column(UUID(as_uuid=True), ForeignKey("professores.id", ondelete="SET NULL"))
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    escola = relationship("Escola", back_populates="turmas")
    professor = relationship("Professor", back_populates="turmas")
    matriculas = relationship("Matricula", back_populates="turma")
    provas_turmas = relationship("ProvaTurma", back_populates="turma")


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
    professor_id = Column(UUID(as_uuid=True), ForeignKey("professores.id", ondelete="SET NULL"))
    data_aplicacao = Column(Date)
    duracao_minutos = Column(Integer)
    peso = Column(DECIMAL(5, 2), default=1.0)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    disciplina = relationship("Disciplina", back_populates="provas")
    professor = relationship("Professor", back_populates="provas")
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


class MaterialDidatico(Base):
    __tablename__ = "materiais_didaticos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    ano_referencia = Column(Integer, nullable=False)
    bimestre = Column(Integer, nullable=False)
    serie = Column(String(10), nullable=False)
    componente = Column(String(50), nullable=False)
    
    cod_cronograma = Column(Integer, nullable=False)
    id_cronograma = Column(Integer, nullable=False)
    titulo = Column(String(255))
    referencia_id = Column(Integer)
    tipo = Column(String(100))
    ordenacao = Column(Integer)
    semana = Column(Integer)
    aulas_com_tarefa = Column(Boolean)
    link_url_youtube = Column(Text, nullable=True)
    exibir_municipio = Column(Boolean)
    
    arquivos = Column(JSONB) 
    
    array_links_youtube = Column(Text)


class AcervoDigital(Base):
    __tablename__ = "acervo_digital"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    arquivo_id = Column(String(255), unique=True, nullable=False, index=True)
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text)
    tipo_arquivo = Column(String(100))
    link_google_drive = Column(Text)
    link_download_python = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class AprendizagemEssencial(Base):
    __tablename__ = "aprendizagens_essenciais"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    acervo_id = Column(UUID(as_uuid=True), ForeignKey("acervo_digital.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Identificação
    ae_codigo = Column(String(20), nullable=False)  # AE1, AE2, etc.
    ano = Column(Integer, nullable=False, index=True)  # 1-5
    codigo_material = Column(String(50), nullable=False, index=True)  # EFAIMAT, EFAFMAT, etc.
    
    # Conteúdo principal
    descricao = Column(Text, nullable=False)
    habilidade_priorizada = Column(Text)
    habilidades_relacionadas = Column(JSONB)  # array de strings
    conhecimentos_previos = Column(JSONB)  # array de strings
    
    # Para desenvolver (tabela estruturada)
    blocos_tematicos = Column(JSONB)  # array de objetos
    materiais_digitais = Column(JSONB)  # array de objetos
    livros_estudante = Column(JSONB)  # array de objetos
    
    # Metadados
    pagina_pdf = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    acervo = relationship("AcervoDigital", backref="aprendizagens_essenciais")
    
    __table_args__ = (
        UniqueConstraint("acervo_id", "ae_codigo", "ano", name="uq_acervo_ae_ano"),
    )