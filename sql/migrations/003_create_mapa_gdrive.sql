-- Migration SQL to create mapa_gdrive table

CREATE TABLE IF NOT EXISTS mapa_gdrive (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  professor_id UUID NOT NULL REFERENCES professores(id) ON DELETE CASCADE,
  alias_professor VARCHAR(255) NOT NULL,
  estrutura JSONB NOT NULL,
  ativo BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_mapa_gdrive_alias ON mapa_gdrive(alias_professor);
CREATE INDEX IF NOT EXISTS idx_mapa_gdrive_professor ON mapa_gdrive(professor_id);
