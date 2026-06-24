CREATE TABLE IF NOT EXISTS escolas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL,
    endereco TEXT,
    telefone VARCHAR(20),
    email VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('admin', 'professor', 'aluno')),
    escola_id UUID REFERENCES escolas(id) ON DELETE SET NULL,
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS turmas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(100) NOT NULL,
    serie VARCHAR(50),
    turno VARCHAR(20) CHECK (turno IN ('manha', 'tarde', 'noite')),
    escola_id UUID REFERENCES escolas(id) ON DELETE CASCADE,
    professor_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS disciplinas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(100) NOT NULL,
    codigo VARCHAR(20) UNIQUE,
    escola_id UUID REFERENCES escolas(id) ON DELETE CASCADE,
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS matriculas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aluno_id UUID REFERENCES usuarios(id) ON DELETE CASCADE,
    turma_id UUID REFERENCES turmas(id) ON DELETE CASCADE,
    data_matricula DATE DEFAULT CURRENT_DATE,
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(aluno_id, turma_id)
);

CREATE TABLE IF NOT EXISTS provas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT,
    disciplina_id UUID REFERENCES disciplinas(id) ON DELETE SET NULL,
    professor_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    data_aplicacao DATE,
    duracao_minutos INTEGER,
    peso DECIMAL(5,2) DEFAULT 1.0,
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS provas_turmas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prova_id UUID REFERENCES provas(id) ON DELETE CASCADE,
    turma_id UUID REFERENCES turmas(id) ON DELETE CASCADE,
    data_agendada TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(prova_id, turma_id)
);

CREATE TABLE IF NOT EXISTS questoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prova_id UUID REFERENCES provas(id) ON DELETE CASCADE,
    enunciado TEXT NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('multipla_escolha', 'dissertativa', 'verdadeiro_falso')),
    pontos DECIMAL(5,2) DEFAULT 1.0,
    ordem INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS alternativas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    questao_id UUID REFERENCES questoes(id) ON DELETE CASCADE,
    texto TEXT NOT NULL,
    correta BOOLEAN DEFAULT false,
    letra CHAR(1) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS respostas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    questao_id UUID REFERENCES questoes(id) ON DELETE CASCADE,
    aluno_id UUID REFERENCES usuarios(id) ON DELETE CASCADE,
    alternativa_id UUID REFERENCES alternativas(id) ON DELETE SET NULL,
    texto_dissertativo TEXT,
    nota DECIMAL(5,2),
    corrigida BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_tipo ON usuarios(tipo);
CREATE INDEX idx_usuarios_escola ON usuarios(escola_id);
CREATE INDEX idx_turmas_escola ON turmas(escola_id);
CREATE INDEX idx_turmas_professor ON turmas(professor_id);
CREATE INDEX idx_matriculas_aluno ON matriculas(aluno_id);
CREATE INDEX idx_matriculas_turma ON matriculas(turma_id);
CREATE INDEX idx_provas_disciplina ON provas(disciplina_id);
CREATE INDEX idx_provas_professor ON provas(professor_id);
CREATE INDEX idx_questoes_prova ON questoes(prova_id);
CREATE INDEX idx_alternativas_questao ON alternativas(questao_id);
CREATE INDEX idx_respostas_questao ON respostas(questao_id);
CREATE INDEX idx_respostas_aluno ON respostas(aluno_id);
