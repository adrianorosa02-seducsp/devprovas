-- Recriar materiais_didaticos com id_aula no início
CREATE TABLE materiais_didaticos_new (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_aula VARCHAR(50) NOT NULL,
    ano_referencia INTEGER NOT NULL,
    bimestre INTEGER,
    serie VARCHAR(50),
    componente VARCHAR(100),
    cod_cronograma VARCHAR(50),
    id_cronograma UUID,
    titulo VARCHAR(255) NOT NULL,
    tipo VARCHAR(50),
    ordenacao INTEGER,
    semana INTEGER,
    aulas_com_tarefa INTEGER,
    arquivos JSONB,
    link_url_youtube TEXT,
    array_links_youtube TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Copiar dados (id_aula será preenchido na importação)
INSERT INTO materiais_didaticos_new (id, ano_referencia, bimestre, serie, componente, cod_cronograma, id_cronograma, titulo, tipo, ordenacao, semana, aulas_com_tarefa, arquivos, link_url_youtube, array_links_youtube, created_at, updated_at)
SELECT id, ano_referencia, bimestre, serie, componente, cod_cronograma, id_cronograma, titulo, tipo, ordenacao, semana, aulas_com_tarefa, arquivos, link_url_youtube, array_links_youtube, created_at, updated_at
FROM materiais_didaticos;

-- Trocar tabelas
DROP TABLE materiais_didaticos;
ALTER TABLE materiais_didaticos_new RENAME TO materiais_didaticos;

-- Recriar índice
CREATE INDEX idx_materiais_id_aula ON materiais_didaticos(id_aula);
CREATE INDEX idx_materiais_ano_referencia ON materiais_didaticos(ano_referencia);