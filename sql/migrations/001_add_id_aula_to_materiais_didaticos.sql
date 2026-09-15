-- Adicionar coluna id_aula na tabela materiais_didaticos (se não existir)
ALTER TABLE materiais_didaticos 
ADD COLUMN IF NOT EXISTS id_aula VARCHAR(50);

-- Adicionar índice se não existir
CREATE INDEX IF NOT EXISTS idx_materiais_id_aula ON materiais_didaticos(id_aula);