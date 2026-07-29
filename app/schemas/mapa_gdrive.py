from typing import Any, Dict
from pydantic import BaseModel


class MapaGDriveSync(BaseModel):
    alias_professor: str
    estrutura: Dict[str, Any]


class MapaGDriveRead(BaseModel):
    id: str
    professor_id: str
    alias_professor: str
    estrutura: Dict[str, Any]
    ativo: bool
    model_config = {"from_attributes": True}
